#!/usr/bin/env python3
"""
WLAN Device Hunter — find & fingerprint IoT/spy-like devices on your LAN

Features:
  - ARP sweep to find live hosts
  - mDNS/zeroconf service discovery
  - SSDP/UPnP discovery (M-SEARCH)
  - Light port scan on common IoT/camera ports
  - OUI vendor lookup (built-in shortlist + optional IEEE oui.txt)
  - Heuristic risk scoring & CSV/JSON report

Author: ChatGPT (assistant)
License: MIT
"""

import argparse
import csv
import ipaddress
import json
import os
import re
import socket
import struct
import sys
import threading
import time
from datetime import datetime
from collections import defaultdict

# Optional deps: we'll import lazily and handle absence gracefully
try:
    import netifaces
except Exception:
    netifaces = None

# scapy may require admin/sudo for ARP scan
try:
    from scapy.all import ARP, Ether, srp, conf as scapy_conf
except Exception:
    ARP = Ether = srp = scapy_conf = None

# Zeroconf for mDNS
try:
    from zeroconf import ServiceBrowser, Zeroconf
except Exception:
    ServiceBrowser = Zeroconf = None

###############################################################################
# OUI vendor shortlist (common IoT/spy gear vendors)
###############################################################################

OUI_SHORTLIST = {
    "24:0A:C4": "Espressif Inc. (ESP32/ESP8266)",
    "7C:DF:A1": "Espressif Inc. (ESP32/ESP8266)",
    "BC:DD:C2": "Espressif Inc. (ESP32/ESP8266)",
    "84:F3:EB": "Espressif Inc. (ESP)",
    "D8:F1:5B": "Tuya Smart Inc.",
    "84:0D:8E": "Tuya Smart Inc.",
    "50:02:91": "Shenzhen Bilian Electronic",
    "28:6C:07": "Shenzhen Skyworth",
    "18:FE:34": "Espressif Inc.",
    "54:EF:44": "Shenzhen Mercury/TP-Link",
    "B4:4B:D6": "Hikvision (Cameras)",
    "00:23:63": "Hikvision (Cameras)",
    "44:64:5D": "Dahua (Cameras)",
    "68:AB:1E": "Dahua (Cameras)",
    "3C:2E:FF": "Realtek Semiconductor",
    "9C:65:F9": "Realtek Semiconductor",
    "C8:2B:96": "Xiaomi Communications",
    "8C:4B:14": "Sonoff / ITEAD",
    "60:01:94": "Wyze Labs (Cameras)",
    "74:AC:B9": "Arlo / Netgear",
    "00:22:93": "Axis Communications (Cameras)",
    "00:40:8C": "Axis Communications (Cameras)",
    "00:1D:67": "Cisco",
}

def normalize_mac(mac: str) -> str:
    mac = mac.upper().replace('-', ':')
    if len(mac.split(':')[0]) == 1:
        # handle single-digit nibbles
        mac = ':'.join(x.zfill(2) for x in mac.split(':'))
    return mac

def lookup_vendor(mac: str, oui_map=None):
    if not mac:
        return None, None
    mac = normalize_mac(mac)
    prefix = ':'.join(mac.split(':')[:3])
    if prefix in OUI_SHORTLIST:
        return OUI_SHORTLIST[prefix], "shortlist"
    if oui_map:
        if prefix in oui_map:
            return oui_map[prefix], "ieee"
    return None, None

def load_oui_file(path: str):
    """
    Parses IEEE OUI file (text variants). Accepts lines like:
    'FC-EC-DA   (hex)        Amazon Technologies Inc.'
    or 'FCECDA     Amazon Technologies Inc'
    """
    if not path or not os.path.exists(path):
        return {}
    pat = re.compile(r'^([0-9A-Fa-f]{2})[-: ]?([0-9A-Fa-f]{2})[-: ]?([0-9A-Fa-f]{2}).*?\s{2,}(.+)$')
    mapping = {}
    with open(path, 'r', errors='ignore') as f:
        for line in f:
            line = line.strip()
            m = pat.match(line)
            if m:
                pfx = f"{m.group(1)}:{m.group(2)}:{m.group(3)}".upper()
                vendor = m.group(4).strip()
                mapping[pfx] = vendor
    return mapping

###############################################################################
# Network utilities
###############################################################################

def local_ipv4_cidrs():
    """Return list of candidate IPv4 CIDRs for scanning (exclude loopbacks/vpn where possible)."""
    cidrs = set()
    # Prefer netifaces; fallback to environment
    if netifaces:
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface).get(netifaces.AF_INET, [])
            for a in addrs:
                ip = a.get('addr')
                netmask = a.get('netmask')
                if not ip or not netmask:
                    continue
                if ip.startswith('127.'):
                    continue
                try:
                    network = ipaddress.IPv4Network((ip, netmask), strict=False)
                    # Skip link-local or very small subnets /32
                    if network.is_link_local or network.prefixlen > 30:
                        continue
                    cidrs.add(str(network))
                except Exception:
                    continue
    # Fallback: try common private ranges
    if not cidrs:
        cidrs = {"192.168.0.0/24", "192.168.1.0/24", "10.0.0.0/24"}
    return sorted(cidrs)

def arp_sweep(cidr: str, timeout=2, verbose=False):
    """ARP sweep using scapy (needs admin). Returns list of (ip, mac)."""
    results = []
    if ARP is None or Ether is None or srp is None:
        if verbose:
            print("[!] scapy not available; skipping ARP sweep")
        return results
    try:
        scapy_conf.verb = 0
        pkt = Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=cidr)
        answered, _ = srp(pkt, timeout=timeout, retry=1)
        for _, rcv in answered:
            ip = rcv.psrc
            mac = rcv.hwsrc
            results.append((ip, mac))
    except PermissionError:
        if verbose:
            print("[!] Permission denied: run as Administrator/sudo for ARP scan")
    except Exception as e:
        if verbose:
            print(f"[!] ARP sweep error: {e}")
    return results

def tcp_port_is_open(ip, port, timeout=0.5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((ip, port))
        s.close()
        return True
    except Exception:
        return False

def light_port_scan(ip, ports):
    open_ports = []
    for p in ports:
        if tcp_port_is_open(ip, p):
            open_ports.append(p)
    return open_ports

def ssdp_discover(timeout=2.5, mx=2, st="ssdp:all"):
    """
    SSDP discovery. Returns list of dicts with fields: ip, server, st, usn, location
    """
    group = ("239.255.255.250", 1900)
    msg = "\r\n".join([
        'M-SEARCH * HTTP/1.1',
        f'HOST: {group[0]}:{group[1]}',
        'MAN: "ssdp:discover"',
        f'MX: {mx}',
        f'ST: {st}', '', '']).encode('utf-8')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    sock.settimeout(timeout)
    responses = []
    try:
        for _ in range(3):
            sock.sendto(msg, group)
        start = time.time()
        while time.time() - start < timeout:
            try:
                data, addr = sock.recvfrom(65507)
                text = data.decode(errors='ignore')
                headers = parse_ssdp_response(text)
                info = {
                    "ip": addr[0],
                    "server": headers.get("server"),
                    "st": headers.get("st"),
                    "usn": headers.get("usn"),
                    "location": headers.get("location"),
                }
                responses.append(info)
            except socket.timeout:
                break
    finally:
        sock.close()
    return responses

def parse_ssdp_response(resp: str):
    headers = {}
    for line in resp.splitlines()[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip().lower()] = v.strip()
    return headers

class _MDNSListener:
    def __init__(self):
        self.records = []
    def add_service(self, zc, stype, name):
        try:
            info = zc.get_service_info(stype, name, 2000)
            if info:
                addrs = []
                for addr in info.addresses:
                    try:
                        addrs.append(socket.inet_ntoa(addr))
                    except Exception:
                        pass
                self.records.append({
                    "type": stype, "name": name,
                    "addresses": addrs, "port": info.port,
                    "properties": {k.decode(): v.decode(errors='ignore') if isinstance(v, bytes) else v
                                   for k, v in info.properties.items()}
                })
        except Exception:
            pass

def mdns_browse(services=None, duration=5):
    """
    Browse mDNS services for `duration` seconds.
    """
    if Zeroconf is None:
        return []
    if services is None:
        services = [
            "_http._tcp.local.",
            "_rtsp._tcp.local.",
            "_ipp._tcp.local.",
            "_airplay._tcp.local.",
            "_raop._tcp.local.",
            "_hap._tcp.local.",
            "_googlecast._tcp.local.",
            "_ssh._tcp.local.",
        ]
    zc = Zeroconf()
    listener = _MDNSListener()
    browsers = [ServiceBrowser(zc, s, listener) for s in services]
    time.sleep(duration)
    try:
        zc.close()
    except Exception:
        pass
    return listener.records

###############################################################################
# Heuristics
###############################################################################

SUSPICIOUS_PORTS = [23, 22, 80, 443, 554, 8000, 8001, 8080, 8443, 8554, 5000, 5353, 1900]
CAMERA_HINTS = ["ipcam", "ip camera", "hikvision", "dahua", "rtsp", "isapi", "onvif", "go2rtc", "wyze", "arlo", "axis"]
IOT_HINTS = ["tuya", "espressif", "esp32", "esp8266", "smart plug", "smartcam", "iot"]

def score_device(features):
    """
    Compute a risk score 0-100 based on ports, vendor, service strings.
    """
    score = 0
    vendor = (features.get("vendor") or "").lower()
    server = (features.get("server") or "").lower()
    mdns_names = " ".join(features.get("mdns_names", [])).lower()
    open_ports = features.get("open_ports", [])

    # Vendors known for IoT/cameras
    if any(x in vendor for x in ["hikvision", "dahua", "axis", "tuya", "espressif", "wyze", "arlo", "xiaomi", "sonoff", "itead", "realtek"]):
        score += 30

    # Ports commonly used by cameras
    if 554 in open_ports or 8554 in open_ports:
        score += 40
    if 80 in open_ports or 8000 in open_ports or 8080 in open_ports or 8443 in open_ports:
        score += 10
    if 1900 in open_ports or 5353 in open_ports:
        score += 5

    # Strings that hint at cameras
    hay = f"{server} {mdns_names}"
    if any(h in hay for h in CAMERA_HINTS):
        score += 25

    # mDNS service types (AirPlay/RAOP usually fine; RTSP suspicious in office)
    if features.get("mdns_rtsp"):
        score += 20

    return min(score, 100)

###############################################################################
# Main discovery workflow
###############################################################################

def discover(subnets, oui_file=None, quick=False, verbose=False):
    oui_map = load_oui_file(oui_file) if oui_file else {}

    # Step 1: ARP sweep all subnets
    arp_hosts = {}
    for cidr in subnets:
        if verbose:
            print(f"[*] ARP sweep {cidr} ...")
        for ip, mac in arp_sweep(cidr, timeout=2, verbose=verbose):
            arp_hosts[ip] = mac

    # Step 2: SSDP discovery
    if verbose:
        print("[*] SSDP discovery ...")
    ssdp = ssdp_discover(timeout=2.5 if quick else 5)
    ssdp_by_ip = defaultdict(list)
    for r in ssdp:
        ssdp_by_ip[r["ip"]].append(r)

    # Step 3: mDNS browse
    mdns_records = []
    if not quick:
        if verbose:
            print("[*] mDNS browse ...")
        mdns_records = mdns_browse(duration=5)
    mdns_by_ip = defaultdict(list)
    for rec in mdns_records:
        for ip in rec.get("addresses", []):
            mdns_by_ip[ip].append(rec)

    # Union of IPs
    ips = set(arp_hosts.keys()) | set(ssdp_by_ip.keys()) | set(mdns_by_ip.keys())

    # Step 4: port scan (light)
    results = []
    for ip in sorted(ips, key=lambda x: tuple(map(int, x.split('.')))):
        mac = arp_hosts.get(ip)
        vendor, vendor_src = lookup_vendor(mac, oui_map)
        open_ports = light_port_scan(ip, SUSPICIOUS_PORTS) if not quick else []
        server = None
        ssdp_entries = ssdp_by_ip.get(ip, [])
        if ssdp_entries:
            # use the first non-empty server header
            for e in ssdp_entries:
                if e.get("server"):
                    server = e["server"]
                    break

        mdns_names = []
        mdns_rtsp = False
        for rec in mdns_by_ip.get(ip, []):
            mdns_names.append(rec.get("name", ""))
            if rec.get("type") == "_rtsp._tcp.local.":
                mdns_rtsp = True

        features = {
            "ip": ip,
            "mac": mac,
            "vendor": vendor or "",
            "vendor_source": vendor_src or "",
            "open_ports": open_ports,
            "server": server or "",
            "ssdp_count": len(ssdp_entries),
            "mdns_names": mdns_names,
            "mdns_rtsp": mdns_rtsp,
        }
        score = score_device(features)
        features["risk_score"] = score
        results.append(features)

    return results

def save_reports(results, outfile_base):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    json_path = f"{outfile_base}_{ts}.json"
    csv_path = f"{outfile_base}_{ts}.csv"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    headers = ["ip","mac","vendor","vendor_source","open_ports","server","ssdp_count","mdns_names","mdns_rtsp","risk_score"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=headers)
        w.writeheader()
        for r in results:
            row = r.copy()
            row["open_ports"] = ",".join(map(str, row.get("open_ports", [])))
            row["mdns_names"] = "|".join(row.get("mdns_names", []))
            w.writerow(row)

    return json_path, csv_path

def main():
    parser = argparse.ArgumentParser(description="Discover and flag potential IoT/spy devices on LAN/WLAN.")
    parser.add_argument("--subnet", action="append", help="CIDR to scan (e.g., 192.168.1.0/24). Can be repeated.")
    parser.add_argument("--quick", action="store_true", help="Skip mDNS and port scan for faster results.")
    parser.add_argument("--outfile", default="wlan_device_hunter_report", help="Base filename (no extension).")
    parser.add_argument("--oui-file", help="Path to IEEE OUI text for vendor lookup.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    args = parser.parse_args()

    subnets = args.subnet if args.subnet else local_ipv4_cidrs()
    if args.verbose:
        print(f"[*] Target subnets: {', '.join(subnets)}")

    results = discover(subnets, oui_file=args.oui_file, quick=args.quick, verbose=args.verbose)
    json_path, csv_path = save_reports(results, args.outfile)

    print(f"[+] Done. Results:\n  JSON: {json_path}\n  CSV:  {csv_path}")
    print("[i] Tip: Review high risk_score entries first (>=60).")

if __name__ == "__main__":
    main()
