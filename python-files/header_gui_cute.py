#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎀 Pink Header Analyzer 💖 (Tkinter GUI)
- Offline: DMARC, SPF auth + alignment, DKIM auth + alignment, Return-Path
- Optional enrichment: sender IP + From domain reputation + IP WHOIS (RDAP)
- Parallel provider calls, per-session cache, adjustable timeout
- Cute pink theme, emojis, and a friendly UI
"""
import re
import json
import time
import queue
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from email import policy
from email.parser import Parser
from email.utils import getaddresses
from urllib import request, error
import ipaddress

# ---- Admin settings ----
ORG_DOMAINS = {"qualitest.com", "qualitestgroup.com"}  # Edit for your org

# ---- Global (in-memory only) ----
API_KEYS = {
    "virustotal": "",  # VT v3: X-Apikey
    "abuseipdb": "",   # AbuseIPDB: Key
    "otx": "",         # AlienVault OTX: X-OTX-API-KEY
}
PROVIDER_ENABLED = {
    "virustotal": True,
    "abuseipdb": True,
    "otx": True,
    "rdap": True,      # WHOIS via RDAP (no key required)
}
NET_TIMEOUT = 10  # seconds (default, user changeable)
USER_AGENT = "PinkHeaderAnalyzer/3.0"

# ----------------- Utility: org domain -----------------
def naive_org_domain(domain: str | None) -> str | None:
    if not domain:
        return None
    parts = domain.lower().strip(".").split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:])
    return domain.lower()

def org_domain(domain: str | None) -> str | None:
    if not domain:
        return None
    d = domain.lower().strip(".")
    for org in ORG_DOMAINS:
        if d == org or d.endswith("." + org):
            return org
    return naive_org_domain(d)

# ----------------- Header parsing -----------------
def extract_auth_results(auth_lines: list[str]) -> tuple[set[str], list[str], set[str], str]:
    spf_domains, dkim_domains = set(), set()
    spf_results = []
    lowers = []
    for line in auth_lines:
        lowers.append(line.lower())
        m_res = re.search(r'\bspf=(pass|fail|softfail|neutral|none|temperror|permerror)\b', line, re.I)
        if m_res:
            spf_results.append(m_res.group(1).lower())
        m = re.search(r'smtp\.mailfrom=([^\s;]+)', line, re.I)
        if m:
            spf_domains.add(m.group(1).strip("<>"))
        m2 = re.search(r'\bmailfrom=([^\s;]+)', line, re.I)
        if m2:
            spf_domains.add(m2.group(1).strip("<>"))
        for d in re.findall(r'header\.d=([^\s;]+)', line, re.I):
            dkim_domains.add(d.strip("<>"))
    return spf_domains, spf_results, dkim_domains, " ".join(lowers)

def parse_headers(raw_headers: str) -> dict:
    msg = Parser(policy=policy.default).parsestr(raw_headers, headersonly=True)

    def first_addr(field: str) -> str | None:
        vals = msg.get_all(field, failobj=[])
        addrs = getaddresses(vals)
        if addrs:
            return addrs[0][1] or addrs[0][0]
        return None

    from_addr = first_addr("From")
    from_dom = (from_addr.split("@", 1)[-1].lower()
                if from_addr and "@" in from_addr else None)
    from_org = org_domain(from_dom)

    return_path = (msg.get("Return-Path") or "").strip() or "—"

    auth_lines = msg.get_all("Authentication-Results", failobj=[])

    # DMARC (verbatim from AR)
    dmarc_results = []
    for line in auth_lines:
        m = re.search(r'\bdmarc=([a-z]+)\b', line, re.I)
        if m:
            dmarc_results.append(m.group(1).lower())
    dmarc = dmarc_results[0] if dmarc_results else "unknown"

    spf_domains, spf_results, dkim_domains, ar_text_lower = extract_auth_results(auth_lines)

    # SPF auth (prefer strongest)
    spf_auth = "unknown"
    for pref in ("pass", "fail", "softfail", "neutral", "none", "temperror", "permerror"):
        if pref in spf_results:
            spf_auth = pref
            break

    # SPF alignment
    if from_dom and spf_domains:
        aligned = any(org_domain(d) == org_domain(from_dom) for d in spf_domains)
        spf_align = "aligned" if aligned else "not aligned"
    else:
        spf_align = "unknown"

    # DKIM auth
    dkim_auth = "pass" if ("dkim=pass" in ar_text_lower) else (
        "fail" if ("dkim=fail" in ar_text_lower) else ("none" if ("dkim=none" in ar_text_lower) else "unknown")
    )

    # DKIM alignment
    if from_dom and dkim_domains:
        aligned = any(org_domain(d) == org_domain(from_dom) for d in dkim_domains)
        dkim_align = "aligned" if aligned else "not aligned"
    else:
        dkim_align = "unknown"

    # Received headers
    recvd = msg.get_all("Received", failobj=[])

    return {
        "from": from_addr or "—",
        "from_domain": from_dom or "—",
        "from_org": from_org or "—",
        "return_path": return_path,
        "dmarc": dmarc,
        "spf_auth": spf_auth,
        "spf_align": spf_align,
        "spf_domains": sorted(spf_domains),
        "dkim_auth": dkim_auth,
        "dkim_align": dkim_align,
        "dkim_domains": sorted(dkim_domains),
        "ar_lines": auth_lines,
        "received": recvd,
    }

def find_sender_ip(received_lines: list[str]) -> str | None:
    """Heuristic: return the last public IPv4 seen in the Received chain (oldest hop)."""
    candidates = []
    for line in reversed(received_lines or []):
        ips = re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', line)
        for ip in ips:
            try:
                ipobj = ipaddress.ip_address(ip)
                if ipobj.version == 4 and not (ipobj.is_private or ipobj.is_loopback or ipobj.is_reserved or ipobj.is_multicast):
                    candidates.append(ip)
            except ValueError:
                continue
        if candidates:
            break
    return candidates[0] if candidates else None

# ----------------- HTTP helpers -----------------
def http_get_json(url: str, headers: dict[str,str], timeout: int) -> tuple[dict|None, str|None, float]:
    """Return (json, error, elapsed_seconds)."""
    req = request.Request(url, headers=headers, method="GET")
    t0 = time.time()
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            try:
                j = json.loads(data.decode("utf-8", errors="replace"))
                return j, None, time.time() - t0
            except Exception as je:
                return None, f"JSON parse error: {je}", time.time() - t0
    except error.HTTPError as he:
        try:
            body = he.read().decode("utf-8", errors="replace")
        except Exception:
            body = ""
        return None, f"HTTP {he.code}: {body[:200]}", time.time() - t0
    except Exception as e:
        return None, str(e), time.time() - t0

# ----------------- Providers -----------------
def vt_ip_lookup(ip: str, timeout: int) -> dict:
    if not PROVIDER_ENABLED.get("virustotal", True) or not API_KEYS.get("virustotal"):
        return {"provider":"VirusTotal","status":"skipped"}
    url = f"https://www.virustotal.com/api/v3/ip_addresses/{ip}"
    headers = {"x-apikey": API_KEYS["virustotal"], "User-Agent": USER_AGENT}
    j, err, t = http_get_json(url, headers, timeout)
    if err: return {"provider":"VirusTotal","status":"error","error":err,"time":round(t,2)}
    try:
        attrs = j["data"]["attributes"]
        stats = attrs.get("last_analysis_stats", {})
        return {"provider":"VirusTotal","status":"ok","time":round(t,2),
                "malicious": stats.get("malicious"), "suspicious": stats.get("suspicious"),
                "harmless": stats.get("harmless"), "undetected": stats.get("undetected")}
    except Exception as e:
        return {"provider":"VirusTotal","status":"error","error":f"parse: {e}","time":round(t,2)}

def vt_domain_lookup(domain: str, timeout: int) -> dict:
    if not PROVIDER_ENABLED.get("virustotal", True) or not API_KEYS.get("virustotal"):
        return {"provider":"VirusTotal (domain)","status":"skipped"}
    url = f"https://www.virustotal.com/api/v3/domains/{domain}"
    headers = {"x-apikey": API_KEYS["virustotal"], "User-Agent": USER_AGENT}
    j, err, t = http_get_json(url, headers, timeout)
    if err: return {"provider":"VirusTotal (domain)","status":"error","error":err,"time":round(t,2)}
    try:
        attrs = j["data"]["attributes"]
        stats = attrs.get("last_analysis_stats", {})
        cat = attrs.get("categories", {})
        return {"provider":"VirusTotal (domain)","status":"ok","time":round(t,2),
                "malicious": stats.get("malicious"), "suspicious": stats.get("suspicious"),
                "harmless": stats.get("harmless"), "undetected": stats.get("undetected"),
                "categories": ", ".join(cat.values()) if isinstance(cat, dict) else ""}
    except Exception as e:
        return {"provider":"VirusTotal (domain)","status":"error","error":f"parse: {e}","time":round(t,2)}

def abuseipdb_lookup(ip: str, timeout: int) -> dict:
    if not PROVIDER_ENABLED.get("abuseipdb", True) or not API_KEYS.get("abuseipdb"):
        return {"provider":"AbuseIPDB","status":"skipped"}
    url = f"https://api.abuseipdb.com/api/v2/check?ipAddress={ip}&maxAgeInDays=90"
    headers = {"Key": API_KEYS["abuseipdb"], "Accept":"application/json", "User-Agent": USER_AGENT}
    j, err, t = http_get_json(url, headers, timeout)
    if err: return {"provider":"AbuseIPDB","status":"error","error":err,"time":round(t,2)}
    try:
        data = j["data"]
        return {"provider":"AbuseIPDB","status":"ok","time":round(t,2),
                "abuseConfidenceScore": data.get("abuseConfidenceScore"),
                "totalReports": data.get("totalReports"),
                "isWhitelisted": data.get("isWhitelisted")}
    except Exception as e:
        return {"provider":"AbuseIPDB","status":"error","error":f"parse: {e}","time":round(t,2)}

def otx_ip_lookup(ip: str, timeout: int) -> dict:
    if not PROVIDER_ENABLED.get("otx", True) or not API_KEYS.get("otx"):
        return {"provider":"OTX","status":"skipped"}
    url = f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general"
    headers = {"X-OTX-API-KEY": API_KEYS["otx"], "User-Agent": USER_AGENT}
    j, err, t = http_get_json(url, headers, timeout)
    if err: return {"provider":"OTX","status":"error","error":err,"time":round(t,2)}
    try:
        pulse_info = j.get("pulse_info", {})
        return {"provider":"OTX","status":"ok","time":round(t,2),"pulses": pulse_info.get("count")}
    except Exception as e:
        return {"provider":"OTX","status":"error","error":f"parse: {e}","time":round(t,2)}

def otx_domain_lookup(domain: str, timeout: int) -> dict:
    if not PROVIDER_ENABLED.get("otx", True) or not API_KEYS.get("otx"):
        return {"provider":"OTX (domain)","status":"skipped"}
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/general"
    headers = {"X-OTX-API-KEY": API_KEYS["otx"], "User-Agent": USER_AGENT}
    j, err, t = http_get_json(url, headers, timeout)
    if err: return {"provider":"OTX (domain)","status":"error","error":err,"time":round(t,2)}
    try:
        pulse_info = j.get("pulse_info", {})
        return {"provider":"OTX (domain)","status":"ok","time":round(t,2),"pulses": pulse_info.get("count")}
    except Exception as e:
        return {"provider":"OTX (domain)","status":"error","error":f"parse: {e}","time":round(t,2)}

def rdap_ip_lookup(ip: str, timeout: int) -> dict:
    """WHOIS-style ownership via RDAP (public service, no API key)."""
    if not PROVIDER_ENABLED.get("rdap", True):
        return {"provider":"RDAP","status":"skipped"}
    url = f"https://rdap.org/ip/{ip}"
    headers = {"User-Agent": USER_AGENT}
    j, err, t = http_get_json(url, headers, timeout)
    if err: return {"provider":"RDAP","status":"error","error":err,"time":round(t,2)}
    try:
        name = j.get("name") or j.get("handle")
        country = j.get("country") or ""
        start = j.get("startAddress") or ""
        end = j.get("endAddress") or ""
        org = ""
        for ent in j.get("entities", []) or []:
            v = ent.get("vcardArray")
            if isinstance(v, list) and len(v) > 1 and isinstance(v[1], list):
                for item in v[1]:
                    if isinstance(item, list) and len(item) >= 4 and item[0] == "fn":
                        org = item[3]; break
            if org: break
        return {"provider":"RDAP","status":"ok","time":round(t,2),
                "name": name or "", "org": org, "country": country,
                "range": f"{start} - {end}" if start or end else ""}
    except Exception as e:
        return {"provider":"RDAP","status":"error","error":f"parse: {e}","time":round(t,2)}

# ----------------- Cute Style -----------------
def apply_pink_theme(root: tk.Tk):
    # Colors
    PINK_BG = "#ffe6f2"
    CARD_BG = "#fff0f6"
    TEXT = "#5c2a3e"
    MUTED = "#a64d79"
    ACCENT = "#ff66a3"
    ACCENT_HOVER = "#ff4d94"
    ENTRY_BG = "#fff7fb"
    MONO_BG = "#fff7fb"

    root.configure(bg=PINK_BG)

    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("TFrame", background=PINK_BG)
    style.configure("Card.TFrame", background=CARD_BG, relief="solid", borderwidth=1)
    style.configure("TLabel", background=PINK_BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("H.TLabel", background=PINK_BG, foreground=TEXT, font=("Segoe UI", 13, "bold"))
    style.configure("Card.TLabel", background=CARD_BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("M.TLabel", background=PINK_BG, foreground=MUTED, font=("Segoe UI", 9))

    style.configure("TButton", background=ACCENT, foreground="white", font=("Segoe UI", 10), borderwidth=0, focusthickness=3, focuscolor=ACCENT)
    style.map("TButton", background=[("active", ACCENT_HOVER)])
    style.configure("TCheckbutton", background=PINK_BG, foreground=TEXT, font=("Segoe UI", 10))
    style.configure("TEntry", fieldbackground=ENTRY_BG, foreground=TEXT)

    # Attach colors to root for other widgets usage
    root._pink_colors = {
        "PINK_BG": PINK_BG, "CARD_BG": CARD_BG, "TEXT": TEXT, "MUTED": MUTED,
        "ACCENT": ACCENT, "ACCENT_HOVER": ACCENT_HOVER, "ENTRY_BG": ENTRY_BG, "MONO_BG": MONO_BG
    }

# ----------------- GUI -----------------
class SettingsDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        apply_pink_theme(self)
        self.title("✨ Settings (Enrichment)")
        self.resizable(False, False)

        frm = ttk.Frame(self, style="Card.TFrame"); frm.pack(padx=16, pady=16, fill="both", expand=True)

        ttk.Label(frm, text="VirusTotal API key:").grid(row=0, column=0, sticky="w", pady=4)
        self.vt = ttk.Entry(frm, width=48)
        self.vt.insert(0, API_KEYS.get("virustotal",""))
        self.vt.grid(row=0, column=1, pady=4)

        ttk.Label(frm, text="AbuseIPDB API key:").grid(row=1, column=0, sticky="w", pady=4)
        self.ab = ttk.Entry(frm, width=48)
        self.ab.insert(0, API_KEYS.get("abuseipdb",""))
        self.ab.grid(row=1, column=1, pady=4)

        ttk.Label(frm, text="OTX API key:").grid(row=2, column=0, sticky="w", pady=4)
        self.ot = ttk.Entry(frm, width=48)
        self.ot.insert(0, API_KEYS.get("otx",""))
        self.ot.grid(row=2, column=1, pady=4)

        ttk.Label(frm, text="Network timeout (seconds):").grid(row=3, column=0, sticky="w", pady=(12,4))
        self.timeout_entry = ttk.Entry(frm, width=10)
        self.timeout_entry.insert(0, str(NET_TIMEOUT))
        self.timeout_entry.grid(row=3, column=1, sticky="w", pady=(12,4))

        self.chk_vt = tk.BooleanVar(value=PROVIDER_ENABLED.get("virustotal",True))
        self.chk_ab = tk.BooleanVar(value=PROVIDER_ENABLED.get("abuseipdb",True))
        self.chk_ot = tk.BooleanVar(value=PROVIDER_ENABLED.get("otx",True))
        self.chk_rdap = tk.BooleanVar(value=PROVIDER_ENABLED.get("rdap",True))

        ttk.Checkbutton(frm, text="Enable VirusTotal", variable=self.chk_vt).grid(row=4, column=0, sticky="w", pady=(10,2))
        ttk.Checkbutton(frm, text="Enable AbuseIPDB", variable=self.chk_ab).grid(row=4, column=1, sticky="w", pady=(10,2))
        ttk.Checkbutton(frm, text="Enable OTX", variable=self.chk_ot).grid(row=5, column=0, sticky="w", pady=2)
        ttk.Checkbutton(frm, text="Enable RDAP (WHOIS)", variable=self.chk_rdap).grid(row=5, column=1, sticky="w", pady=2)

        btns = ttk.Frame(frm, style="Card.TFrame")
        btns.grid(row=6, column=0, columnspan=2, pady=(12,0))
        ttk.Button(btns, text="💾 Save", command=self.on_save).pack(side="left")
        ttk.Button(btns, text="✖ Cancel", command=self.destroy).pack(side="left", padx=8)

    def on_save(self):
        global NET_TIMEOUT
        API_KEYS["virustotal"] = self.vt.get().strip()
        API_KEYS["abuseipdb"]  = self.ab.get().strip()
        API_KEYS["otx"]        = self.ot.get().strip()
        PROVIDER_ENABLED["virustotal"] = bool(self.chk_vt.get())
        PROVIDER_ENABLED["abuseipdb"]  = bool(self.chk_ab.get())
        PROVIDER_ENABLED["otx"]        = bool(self.chk_ot.get())
        PROVIDER_ENABLED["rdap"]       = bool(self.chk_rdap.get())
        try:
            NET_TIMEOUT = max(3, int(self.timeout_entry.get().strip()))
        except Exception:
            NET_TIMEOUT = 10
        self.destroy()

class HeaderGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        apply_pink_theme(self)
        self.title("🎀 Pink Header Analyzer 💖")
        self.geometry("1020x780")

        colors = self._pink_colors

        # Header banner
        banner = ttk.Frame(self, style="Card.TFrame"); banner.pack(fill="x", padx=16, pady=(16,8))
        ttk.Label(banner, text="🎀 Pink Header Analyzer 💌", style="H.TLabel").pack(anchor="w")
        ttk.Label(banner, text="Cute & private • No data leaves unless you enable enrichment ✨", style="M.TLabel").pack(anchor="w")

        # Input card
        card_in = ttk.Frame(self, style="Card.TFrame"); card_in.pack(fill="both", expand=False, padx=16, pady=(0,8))
        ttk.Label(card_in, text="Paste raw email headers:", style="Card.TLabel").pack(anchor="w", pady=(6,2))
        self.text = tk.Text(card_in, height=12, wrap="none",
                            bg=colors["ENTRY_BG"], fg=colors["TEXT"],
                            insertbackground=colors["TEXT"],
                            font=("Consolas", 10), relief="flat", bd=6, highlightthickness=1, highlightbackground="#f5c2d7")
        self.text.pack(fill="both", expand=True)

        # Controls
        btns = ttk.Frame(self); btns.pack(fill="x", padx=16, pady=8)
        self.enrich_toggle = tk.BooleanVar(value=False)
        self.fast_mode = tk.BooleanVar(value=True)  # skip domain lookups by default for speed
        ttk.Checkbutton(btns, text="Enable online enrichment (sparkly but optional ✨)", variable=self.enrich_toggle).pack(side="left")
        ttk.Checkbutton(btns, text="Fast mode (skip domain lookups)", variable=self.fast_mode).pack(side="left", padx=(10,0))
        ttk.Button(btns, text="🌸 Analyze", command=self.on_analyze).pack(side="left", padx=(12,0))
        ttk.Button(btns, text="🧼 Clear", command=self.on_clear).pack(side="left", padx=8)
        ttk.Button(btns, text="⚙ Settings", command=self.on_settings).pack(side="left", padx=8)
        self.status_var = tk.StringVar(value="Status: Idle")
        ttk.Label(btns, textvariable=self.status_var).pack(side="right")

        # Offline results card
        card_off = ttk.Frame(self, style="Card.TFrame"); card_off.pack(fill="both", expand=False, padx=16, pady=(0,8))
        ttk.Label(card_off, text="Offline Results 💖", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=(6,8))

        ttk.Label(card_off, text="DMARC authentication:").grid(row=1, column=0, sticky="w")
        self.dmarc_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.dmarc_var).grid(row=1, column=1, sticky="w")

        ttk.Label(card_off, text="SPF authentication:").grid(row=2, column=0, sticky="w")
        self.spf_auth_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.spf_auth_var).grid(row=2, column=1, sticky="w")

        ttk.Label(card_off, text="SPF alignment:").grid(row=3, column=0, sticky="w")
        self.spf_align_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.spf_align_var).grid(row=3, column=1, sticky="w")

        ttk.Label(card_off, text="DKIM authentication:").grid(row=4, column=0, sticky="w")
        self.dkim_auth_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.dkim_auth_var).grid(row=4, column=1, sticky="w")

        ttk.Label(card_off, text="DKIM alignment:").grid(row=5, column=0, sticky="w")
        self.dkim_align_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.dkim_align_var).grid(row=5, column=1, sticky="w")

        ttk.Label(card_off, text="From domain (org):").grid(row=6, column=0, sticky="w", pady=(8,0))
        self.from_org_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.from_org_var).grid(row=6, column=1, sticky="w", pady=(8,0))

        ttk.Label(card_off, text="Return-Path:").grid(row=7, column=0, sticky="w")
        self.return_path_var = tk.StringVar(value="—"); ttk.Label(card_off, textvariable=self.return_path_var).grid(row=7, column=1, sticky="w")

        # Sender IP + override
        ttk.Label(card_off, text="Detected sender IP:").grid(row=8, column=0, sticky="w", pady=(8,0))
        self.sender_ip_var = tk.StringVar(value="—")
        ttk.Label(card_off, textvariable=self.sender_ip_var).grid(row=8, column=1, sticky="w", pady=(8,0))

        ttk.Label(card_off, text="Override sender IP (optional):").grid(row=9, column=0, sticky="w")
        self.override_ip = ttk.Entry(card_off, width=24); self.override_ip.grid(row=9, column=1, sticky="w")

        # Domain to enrich
        ttk.Label(card_off, text="From domain for enrichment:").grid(row=10, column=0, sticky="w", pady=(8,0))
        self.domain_var = tk.StringVar(value="—")
        ttk.Label(card_off, textvariable=self.domain_var).grid(row=10, column=1, sticky="w", pady=(8,0))

        # Enrichment Results card
        card_enr = ttk.Frame(self, style="Card.TFrame"); card_enr.pack(fill="both", expand=True, padx=16, pady=(0,16))
        ttk.Label(card_enr, text="Online Enrichment (optional) ✨", style="Card.TLabel").grid(row=0, column=0, sticky="w", pady=(6,8))

        self.enr_text = tk.Text(card_enr, height=12, wrap="word",
                                bg=colors["MONO_BG"], fg=colors["TEXT"],
                                insertbackground=colors["TEXT"],
                                font=("Consolas", 10), relief="flat", bd=6, highlightthickness=1, highlightbackground="#f5c2d7")
        self.enr_text.grid(row=1, column=0, sticky="nsew")
        card_enr.grid_rowconfigure(1, weight=1)
        card_enr.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Store latest parsed structure + cache
        self._last_result = None
        self._cache = {"ip": {}, "domain": {}}

    def on_settings(self):
        SettingsDialog(self)

    def on_clear(self):
        self.text.delete("1.0", "end")
        self.dmarc_var.set("—")
        self.spf_auth_var.set("—")
        self.spf_align_var.set("—")
        self.dkim_auth_var.set("—")
        self.dkim_align_var.set("—")
        self.from_org_var.set("—")
        self.return_path_var.set("—")
        self.sender_ip_var.set("—")
        self.domain_var.set("—")
        self.override_ip.delete(0, "end")
        self.enr_text.delete("1.0", "end")
        self.status_var.set("Status: Idle")
        self._last_result = None
        self._cache = {"ip": {}, "domain": {}}

    def on_analyze(self):
        raw = self.text.get("1.0", "end").strip()
        if not raw:
            messagebox.showwarning("No input", "Please paste raw email headers first.")
            return
        try:
            result = parse_headers(raw)
        except Exception as e:
            messagebox.showerror("Parse error", f"Failed to parse headers:\n{e}")
            return

        self._last_result = result
        # Update offline fields
        self.dmarc_var.set(result["dmarc"])
        self.spf_auth_var.set(result["spf_auth"])
        self.spf_align_var.set(result["spf_align"])
        self.dkim_auth_var.set(result["dkim_auth"])
        self.dkim_align_var.set(result["dkim_align"])
        self.from_org_var.set(f"{result['from_domain']}  ({result['from_org']})")
        self.return_path_var.set(result["return_path"])
        self.domain_var.set(result["from_domain"] if result["from_domain"] != "—" else "—")

        # Detect sender IP
        sender_ip = find_sender_ip(result.get("received", [])) or "—"
        self.sender_ip_var.set(sender_ip)

        # Optionally run enrichment
        if self.enrich_toggle.get():
            self.run_enrichment(sender_ip if sender_ip != "—" else None,
                                result["from_domain"] if result["from_domain"] != "—" else None,
                                fast=True if self.fast_mode.get() else False)
        else:
            self.enr_text.delete("1.0", "end")
            self.enr_text.insert("end", "Enrichment is disabled. Turn it on to query VT/AbuseIPDB/OTX/RDAP.\n")

    # -------- Enrichment orchestration --------
    def run_enrichment(self, ip: str | None, domain: str | None, fast: bool = True):
        # Warn if no keys present (VT/Abuse/OTX); RDAP needs none.
        if not any(API_KEYS.values()) and not PROVIDER_ENABLED.get("rdap", True):
            if not messagebox.askyesno("No API keys", "No API keys are configured and RDAP is disabled. Continue anyway?"):
                return

        self.status_var.set("Status: Enrichment running... ✨")
        self.enr_text.delete("1.0", "end")
        q = queue.Queue()
        t = threading.Thread(target=self.thread_enrich, args=(ip, domain, fast, q), daemon=True)
        t.start()

        def poll():
            if t.is_alive():
                self.after(150, poll)
            else:
                try:
                    res = q.get_nowait()
                except queue.Empty:
                    res = "No results."
                self.enr_text.insert("end", res + "\n")
                self.status_var.set("Status: Done 💖")
        self.after(150, poll)

    def thread_enrich(self, ip: str | None, domain: str | None, fast: bool, q: queue.Queue):
        """Background enrichment (parallel calls, cached)."""
        lines = []
        lines.append("== Enrichment Results ==\n")

        # Override IP if user provided one
        oip = self.override_ip.get().strip()
        if oip:
            ip = oip

        # --- IP block ---
        if ip:
            lines.append(f"[IP] {ip}\n")
            if ip in self._cache["ip"]:
                lines.append("  (cached)\n")
                for item in self._cache["ip"][ip]:
                    lines.append(f"  - {item['provider']}: {json.dumps(item, ensure_ascii=False)}\n")
            else:
                results = []
                def run_and_store(fn, label):
                    try:
                        res = fn(ip, NET_TIMEOUT)
                    except Exception as e:
                        res = {"provider":label, "status":"error", "error":str(e)}
                    results.append(res)

                providers = []
                if PROVIDER_ENABLED.get("virustotal", True) and API_KEYS.get("virustotal"):
                    providers.append(("VirusTotal", vt_ip_lookup))
                if PROVIDER_ENABLED.get("abuseipdb", True) and API_KEYS.get("abuseipdb"):
                    providers.append(("AbuseIPDB", abuseipdb_lookup))
                if PROVIDER_ENABLED.get("otx", True) and API_KEYS.get("otx"):
                    providers.append(("OTX", otx_ip_lookup))
                if PROVIDER_ENABLED.get("rdap", True):
                    providers.append(("RDAP", rdap_ip_lookup))

                threads = []
                for label, fn in providers:
                    t = threading.Thread(target=run_and_store, args=(fn, label), daemon=True)
                    threads.append(t); t.start()
                for t in threads:
                    t.join(NET_TIMEOUT + 2)

                self._cache["ip"][ip] = results
                for item in results:
                    lines.append(f"  - {item.get('provider')}: {json.dumps(item, ensure_ascii=False)}\n")
        else:
            lines.append("[IP] None detected (you can override and re-run)\n")

        # --- Domain block ---
        if not fast and domain:
            lines.append(f"\n[Domain] {domain}\n")
            if domain in self._cache["domain"]:
                lines.append("  (cached)\n")
                for item in self._cache["domain"][domain]:
                    lines.append(f"  - {item['provider']}: {json.dumps(item, ensure_ascii=False)}\n")
            else:
                results = []
                def run_and_store_dom(fn, label):
                    try:
                        res = fn(domain, NET_TIMEOUT)
                    except Exception as e:
                        res = {"provider":label, "status":"error", "error":str(e)}
                    results.append(res)

                providers = []
                if PROVIDER_ENABLED.get("virustotal", True) and API_KEYS.get("virustotal"):
                    providers.append(("VirusTotal (domain)", vt_domain_lookup))
                if PROVIDER_ENABLED.get("otx", True) and API_KEYS.get("otx"):
                    providers.append(("OTX (domain)", otx_domain_lookup))

                threads = []
                for label, fn in providers:
                    t = threading.Thread(target=run_and_store_dom, args=(fn, label), daemon=True)
                    threads.append(t); t.start()
                for t in threads:
                    t.join(NET_TIMEOUT + 2)

                self._cache["domain"][domain] = results
                for item in results:
                    lines.append(f"  - {item.get('provider')}: {json.dumps(item, ensure_ascii=False)}\n")
        elif fast:
            lines.append("\n[Domain] Skipped (fast mode)\n")
        else:
            lines.append("\n[Domain] None available\n")

        q.put("".join(lines))

    def on_settings(self):
        SettingsDialog(self)

    def on_close(self):
        # Clear secrets + fields, then close
        for k in API_KEYS:
            API_KEYS[k] = ""
        self.on_clear()
        self.destroy()

def main():
    app = HeaderGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
