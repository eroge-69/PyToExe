
#!/usr/bin/env python3
"""
RedTiger-Lite — An ethical, educational recon & diagnostics toolkit
------------------------------------------------------------------
A single-file Python utility inspired by "Red Tiger" menus, focused on
non-destructive, consent-based checks only. No doxxing, password cracking,
phishing, or intrusive exploitation. Think of it as a Swiss‑army knife for
basic web/network hygiene.

Usage:
  $ python redtiger_lite.py           # interactive menu
  $ python redtiger_lite.py --help     # CLI help & one-shot commands

Requirements (optional, auto‑detected):
  requests, beautifulsoup4, dnspython, python-whois, Pillow

All features degrade gracefully if an optional dependency is missing.
"""

from __future__ import annotations
import argparse
import datetime as _dt
import json
import os
import platform
import re
import socket
import ssl
import subprocess
import sys
import textwrap
import threading
import time
from contextlib import closing
from dataclasses import dataclass
from typing import List, Optional, Tuple

# ------- Optional deps (graceful fallbacks) ---------------------------------
try:
    import requests  # type: ignore
except Exception:  # pragma: no cover
    requests = None  # type: ignore

try:
    from bs4 import BeautifulSoup  # type: ignore
except Exception:  # pragma: no cover
    BeautifulSoup = None  # type: ignore

try:
    import dns.resolver  # type: ignore
except Exception:  # pragma: no cover
    dns = None  # type: ignore

try:
    import whois as _whois  # type: ignore
except Exception:  # pragma: no cover
    _whois = None  # type: ignore

try:
    from PIL import Image, ExifTags  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore
    ExifTags = None  # type: ignore

# ------- Banner --------------------------------------------------------------
BANNER = r"""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣠⣤⣤⣤⡴⣶⣶⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣴⣶⣿⣿⣿⣿⣿⣿⣷⣿⣶⣿⣧⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣤⣄⣀⣀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣾⣿⣿⣿⠿⠿⠛⠛⠛⠋⠉⠉⠉⠛⠛⠛⠛⠿⠟⠛⠛⠛⠛⠛⠛⠛⠛⠛⣻⣿⣿⠋⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣠⣴⣿⣿⣿⠟⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣟⡁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⣠⣾⣿⣿⠟⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠴⠿⠿⠿⣿⣿⣷⣦⡀⠀⠀⠀⠀
⠀⠀⠀⢰⣿⣿⡿⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣠⣄⣀⣀⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣶⣄⠀⠀
⠀⠀⠀⢸⣿⣿⣿⣦⣤⣤⣀⣀⣀⣀⣠⣤⠴⠖⠋⢉⣽⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠧⡀
⠀⠀⢠⣿⠟⠉⠁⠈⠉⠉⠙⠛⠛⠿⠿⣿⣿⣿⣿⣿⣿⠿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈
⠀⢠⣿⡁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠽⠟⠛⠉⠀⢀⣀⣤⣴⣶⣶⣶⣶⣶⣶⣤⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⣿⣿⣿⣷⣶⣦⣤⣤⣤⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠈⠉⠛⠿⣿⣿⣿⣶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⣿⠘⢿⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠈⣿⣴⣿⣿⣄⠀⠀⠀⠀⠀⣀⣠⣴⠶⣿⣿⠋⠉⠉⠉⠙⢻⣿⡆⠀⠀⠀⠀⠀⠀⣀⣴⣶⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢹⣿⡍⠛⠻⢷⣶⣶⣶⠟⢿⣿⠗⠀⠹⠃⡀⠀⠀⠀⠀⠀⣿⡇⠀⠀⠀⢀⣴⣿⣿⣿⣿⠿⠿⠛⠛⠛⠛⠛⠂⠀⠀⠀⠀⠀⠀⠀
⠀⠀⢻⡇⠀⠀⠀⢻⣿⣿⠀⠈⠛⠀⠀⠀⢹⠇⠀⠀⠀⠀⢶⣿⠇⠀⢀⣴⣿⣿⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠁⠀⠀⠀⠀⠹⡇⠀⠀⠀⠀⠀⣀⡾⠀⠀⠀⠀⠀⢸⡿⠀⣠⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠀⣦⠀⠀⢠⣿⢳⠀⠀⠀⠙⣿⣿⠁⢰⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⣿⣷⡾⠿⠃⢸⣷⣀⠀⢀⣾⠃⢀⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⠻⠷⢾⣿⣿⣷⡿⠁⠀⢸⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⢿⣷⣄⠀⠀⠉⠛⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⣦⣄⡀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣿⣶⣶⣾⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠛⠛⠿⠧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀

RedTiger-Lite (Ethical Edition)
"""

MENU = {
    1: "Website Security Headers Check",
    2: "Website Info (title, server, tech hints)",
    3: "URL Scanner (redirects, status, final URL)",
    4: "IP Tools (whois, reverse DNS)",
    5: "Port Scan (top ports, TCP connect)",
    6: "Ping Host",
    7: "DNS Lookup (A/AAAA/MX/NS)",
    8: "robots.txt fetch",
    9: "SSL Certificate info",
    10: "Image EXIF reader (local file)",
}

TOP_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 123, 135, 139, 143, 161, 389, 443, 445,
    465, 587, 993, 995, 1433, 1521, 2049, 2375, 27017, 3306, 3389, 5432,
    5900, 6379, 8080, 8443, 9200,
]

# ----------------------------- Helpers --------------------------------------

def require(pkg_name: str, obj, purpose: str) -> None:
    if obj is None:
        raise SystemExit(
            f"Optional dependency '{pkg_name}' is missing.\n"
            f"Install it with: pip install {pkg_name}\n"
            f"Required for: {purpose}"
        )


def pretty_json(data) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


# ----------------------------- Features -------------------------------------

def check_security_headers(url: str) -> dict:
    require("requests", requests, "HTTP requests")
    resp = requests.get(url, timeout=12, allow_redirects=True)
    headers = {k.lower(): v for k, v in resp.headers.items()}
    expected = [
        "strict-transport-security",
        "content-security-policy",
        "x-content-type-options",
        "x-frame-options",
        "referrer-policy",
        "permissions-policy",
    ]
    missing = [h for h in expected if h not in headers]
    return {
        "url": resp.url,
        "status": resp.status_code,
        "present": {h: headers.get(h) for h in expected if h in headers},
        "missing": missing,
    }


def website_info(url: str) -> dict:
    require("requests", requests, "HTTP requests")
    resp = requests.get(url, timeout=12, allow_redirects=True)
    info = {
        "requested_url": url,
        "final_url": resp.url,
        "status": resp.status_code,
        "server": resp.headers.get("Server"),
        "powered_by": resp.headers.get("X-Powered-By"),
        "content_type": resp.headers.get("Content-Type"),
    }
    if BeautifulSoup is not None:
        try:
            soup = BeautifulSoup(resp.text, "html.parser")
            title = soup.title.string.strip() if soup.title else None
        except Exception:
            title = None
        info["title"] = title
    return info


def url_scanner(url: str) -> dict:
    require("requests", requests, "HTTP requests")
    session = requests.Session()
    history = []
    resp = session.get(url, timeout=12, allow_redirects=True)
    for r in resp.history:
        history.append({"status": r.status_code, "url": r.url})
    history.append({"status": resp.status_code, "url": resp.url})
    return {"chain": history}


def ip_tools(target: str) -> dict:
    result = {"input": target}
    # Resolve host -> IP or accept IP
    try:
        ip = socket.gethostbyname(target)
        result["ip"] = ip
    except socket.gaierror:
        result["ip"] = None
    # Reverse DNS
    try:
        if result["ip"]:
            host, _, _ = socket.gethostbyaddr(result["ip"])
            result["reverse_dns"] = host
    except Exception:
        result["reverse_dns"] = None
    # WHOIS (if module available)
    if _whois is not None:
        try:
            w = _whois.whois(target)
            # Convert some fields to str for JSON safety
            result["whois"] = {k: (str(v) if not isinstance(v, (str, int, float)) else v)
                                 for k, v in w.items()}
        except Exception:
            result["whois"] = "whois lookup failed (maybe rate-limited)"
    else:
        result["whois"] = "python-whois not installed"
    return result


def tcp_connect(host: str, port: int, timeout: float = 1.0) -> bool:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.settimeout(timeout)
        try:
            return s.connect_ex((host, port)) == 0
        except Exception:
            return False


def port_scan(host: str, ports: List[int] = TOP_PORTS, workers: int = 100) -> dict:
    # Resolve first to avoid repeated DNS
    try:
        target_ip = socket.gethostbyname(host)
    except socket.gaierror as e:
        return {"error": f"cannot resolve host: {e}"}

    open_ports: List[int] = []
    lock = threading.Lock()

    def worker(p_list: List[int]):
        for p in p_list:
            if tcp_connect(target_ip, p):
                with lock:
                    open_ports.append(p)

    # Simple chunked threads
    chunks = [ports[i:i+int(max(1, len(ports)/workers))] for i in range(0, len(ports), int(max(1, len(ports)/workers)))]
    threads = [threading.Thread(target=worker, args=(chunk,), daemon=True) for chunk in chunks]
    for t in threads: t.start()
    for t in threads: t.join()

    return {"host": host, "ip": target_ip, "open_ports": sorted(open_ports)}


def ping_host(host: str, count: int = 4) -> dict:
    """Cross‑platform ping via system binary (no raw sockets/root needed)."""
    flag = "-n" if platform.system().lower().startswith("win") else "-c"
    try:
        out = subprocess.check_output(["ping", flag, str(count), host], stderr=subprocess.STDOUT, timeout=20)
        return {"ok": True, "output": out.decode(errors="ignore")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def dns_lookup(name: str) -> dict:
    result = {"query": name}
    if dns is None:
        result["note"] = "dnspython not installed; using socket only for A lookup"
        try:
            result["A"] = [socket.gethostbyname(name)]
        except Exception:
            result["A"] = []
        return result

    answers = {}
    for rtype in ["A", "AAAA", "MX", "NS"]:
        try:
            res = dns.resolver.resolve(name, rtype)
            answers[rtype] = [str(r.to_text()) for r in res]
        except Exception:
            answers[rtype] = []
    result.update(answers)
    return result


def fetch_robots(url: str) -> dict:
    require("requests", requests, "HTTP requests")
    # Normalize base
    if not re.match(r"^https?://", url):
        url = "http://" + url
    base = url.rstrip("/")
    target = base + "/robots.txt"
    r = requests.get(target, timeout=12)
    return {"url": target, "status": r.status_code, "content": r.text[:10000]}


def ssl_cert_info(host: str, port: int = 443) -> dict:
    ctx = ssl.create_default_context()
    with closing(socket.create_connection((host, port), timeout=10)) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as ssock:
            cert = ssock.getpeercert()
    # Parse dates
    not_before = cert.get("notBefore")
    not_after = cert.get("notAfter")
    def parse_dt(s: Optional[str]):
        if not s: return None
        try:
            return _dt.datetime.strptime(s, "%b %d %H:%M:%S %Y %Z").isoformat()
        except Exception:
            return s
    return {
        "subject": dict(x for x in cert.get("subject", [])),
        "issuer": dict(x for x in cert.get("issuer", [])),
        "not_before": parse_dt(not_before),
        "not_after": parse_dt(not_after),
        "serialNumber": cert.get("serialNumber"),
        "version": cert.get("version"),
    }


def image_exif(path: str) -> dict:
    require("Pillow", Image, "reading EXIF")
    try:
        img = Image.open(path)
        exif = getattr(img, "_getexif", lambda: None)()
        if not exif:
            return {"file": path, "exif": {}, "note": "No EXIF tags present."}
        # Convert EXIF tag ids to names
        tagmap = {ExifTags.TAGS.get(k, str(k)): v for k, v in exif.items()}
        # Scrub potentially sensitive GPS coordinates by default
        if "GPSInfo" in tagmap:
            tagmap["GPSInfo"] = "(hidden — contains precise location)"
        return {"file": path, "exif": tagmap}
    except FileNotFoundError:
        return {"error": f"file not found: {path}"}


# ----------------------------- CLI / Menu -----------------------------------

def run_interactive():
    print(BANNER)
    print("Ethical use only: run these checks on systems you own or have explicit permission to test.\n")
    while True:
        print("Main Menu")
        for k in sorted(MENU):
            print(f" [{k:02d}] {MENU[k]}")
        print(" [00] Exit\n")
        choice = input("Select option: ").strip()
        if not choice.isdigit():
            print("Please enter a number.\n"); continue
        n = int(choice)
        if n == 0:
            print("Goodbye!"); return

        try:
            if n == 1:
                url = input("URL (https://...): ").strip()
                print(pretty_json(check_security_headers(url)))
            elif n == 2:
                url = input("URL (https://...): ").strip()
                print(pretty_json(website_info(url)))
            elif n == 3:
                url = input("URL (https://...): ").strip()
                print(pretty_json(url_scanner(url)))
            elif n == 4:
                target = input("Domain or IP: ").strip()
                print(pretty_json(ip_tools(target)))
            elif n == 5:
                host = input("Host or IP: ").strip()
                print(pretty_json(port_scan(host)))
            elif n == 6:
                host = input("Host or IP: ").strip()
                print(pretty_json(ping_host(host)))
            elif n == 7:
                name = input("Domain: ").strip()
                print(pretty_json(dns_lookup(name)))
            elif n == 8:
                url = input("Site base (https://example.com): ").strip()
                print(pretty_json(fetch_robots(url)))
            elif n == 9:
                host = input("Host (domain): ").strip()
                print(pretty_json(ssl_cert_info(host)))
            elif n == 10:
                path = input("Local image path: ").strip()
                print(pretty_json(image_exif(path)))
            else:
                print("Unknown option.\n")
        except SystemExit as se:
            print(str(se) + "\n")
        except Exception as e:
            print(f"Error: {e}\n")


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="RedTiger-Lite (ethical recon toolkit)")
    sub = p.add_subparsers(dest="cmd")

    s1 = sub.add_parser("headers", help="Check common security headers")
    s1.add_argument("url")

    s2 = sub.add_parser("info", help="Basic website info")
    s2.add_argument("url")

    s3 = sub.add_parser("scanurl", help="URL scanner (redirect chain)")
    s3.add_argument("url")

    s4 = sub.add_parser("ip", help="IP tools (reverse DNS, whois)")
    s4.add_argument("target")

    s5 = sub.add_parser("ports", help="Port scan common ports")
    s5.add_argument("host")

    s6 = sub.add_parser("ping", help="Ping host")
    s6.add_argument("host")
    s6.add_argument("--count", type=int, default=4)

    s7 = sub.add_parser("dns", help="DNS lookup A/AAAA/MX/NS")
    s7.add_argument("name")

    s8 = sub.add_parser("robots", help="Fetch robots.txt")
    s8.add_argument("url")

    s9 = sub.add_parser("ssl", help="Fetch SSL certificate info")
    s9.add_argument("host")

    s10 = sub.add_parser("exif", help="Read EXIF from a local image (GPS hidden)")
    s10.add_argument("path")

    return p


def main(argv: Optional[List[str]] = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if not argv:
        run_interactive()
        return 0
    p = build_arg_parser()
    args = p.parse_args(argv)

    try:
        if args.cmd == "headers":
            print(pretty_json(check_security_headers(args.url)))
        elif args.cmd == "info":
            print(pretty_json(website_info(args.url)))
        elif args.cmd == "scanurl":
            print(pretty_json(url_scanner(args.url)))
        elif args.cmd == "ip":
            print(pretty_json(ip_tools(args.target)))
        elif args.cmd == "ports":
            print(pretty_json(port_scan(args.host)))
        elif args.cmd == "ping":
            print(pretty_json(ping_host(args.host, args.count)))
        elif args.cmd == "dns":
            print(pretty_json(dns_lookup(args.name)))
        elif args.cmd == "robots":
            print(pretty_json(fetch_robots(args.url)))
        elif args.cmd == "ssl":
            print(pretty_json(ssl_cert_info(args.host)))
        elif args.cmd == "exif":
            print(pretty_json(image_exif(args.path)))
        else:
            # No subcommand provided -> interactive
            run_interactive()
    except SystemExit as se:
        print(str(se))
        return 2
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())


# ----------------------------- Appendix / README -----------------------------

"""
RedTiger-Lite — Appendix

This appendix contains extra documentation, installation tips, safety notes, and
ideas for future improvements. The main script above is a single-file utility
suitable for interactive use or invocation as a CLI subcommand.

Installation
------------
1. Save the script to a file, for example `redtiger_lite.py`.
2. (Optional) create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   ```
3. Install optional dependencies for richer output (recommended):
   ```bash
   pip install requests beautifulsoup4 dnspython python-whois Pillow
   ```
4. Run interactively:
   ```bash
   python redtiger_lite.py
   ```
5. Run a one-shot command (non-interactive):
   ```bash
   python redtiger_lite.py headers https://example.com
   python redtiger_lite.py ports example.com
   ```

Safety & Ethics
---------------
RedTiger-Lite is intentionally limited to passive, consent-friendly checks:
- No automated attempts at password cracking, exploitation, phishing, or
  social engineering.
- Port scan uses TCP connect (no SYN flood or raw packet crafting).
- Image EXIF reader hides GPS coordinates by default to avoid inadvertent
  location disclosure.

Only run these checks against systems you own or for which you have explicit
permission to perform reconnaissance. Misuse may be illegal in your
jurisdiction.

Extending the Script
--------------------
Some ideas you can implement safely:
- Add colorized terminal output (use `rich` or `colorama`) for nicer readability.
- Add a results export option (JSON/CSV) to save scan outputs.
- Make a simple web UI that runs locally for authorized users only.
- Add concurrency improvements and rate-limiting to avoid overloading targets.

Packaging as a CLI tool
-----------------------
To make this installable via pip locally, create `setup.cfg` and `pyproject.toml`
with an entry point, or use `pipx` to run from source. Example `pyproject.toml`:

```toml
[build-system]
requires = ["setuptools", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "redtiger-lite"
version = "0.1.0"
description = "Ethical recon toolkit (educational)"
readme = "README.md"
requires-python = ">=3.8"

[project.scripts]
redtiger-lite = "redtiger_lite:main"
```

Notes on Optional Dependencies
-------------------------------
- `requests`: used for HTTP/HTTPS interactions; recommended.
- `beautifulsoup4`: extracts titles and small HTML hints; optional.
- `dnspython`: richer DNS queries (MX/NS/AAAA); optional.
- `python-whois`: WHOIS lookups; may be rate-limited by registrars.
- `Pillow`: EXIF extraction from images.

Troubleshooting
---------------
- If `ssl_cert_info` raises an error, ensure the target accepts TLS connections
  on the given port and that your environment allows outbound TCP.
- On restricted networks, `ping` may be blocked or require elevated privileges.
- WHOIS data varies widely; treat it as advisory and potentially incomplete.

Change Log
----------
0.1.0 - Initial ethical release
- Basic passive recon features implemented
- Interactive menu + CLI mode
- ASCII art banner and documentation

License
-------
This project is provided for educational purposes. Use at your own risk. If
you intend to use it commercially, add an appropriate license file (MIT,
Apache-2.0, etc.).

"""
