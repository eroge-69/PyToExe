import customtkinter as ctk
import re
import requests
from email.parser import Parser
from email.utils import parsedate_to_datetime
from tkinter import messagebox

# === AbuseIPDB API key ===
ABUSE_API_KEY = "a83311470c2a374d1d3943bbe8faf9ab5d6eb0260d74abb8ed49e0cb03cb812e3c345a363327a5c8"  # Replace with your key

def extract_ip_addresses(header):
    return re.findall(r'[0-9]+(?:\.[0-9]+){3}', header)

def get_geo_info(ip):
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}").json()
        if geo["status"] == "success":
            return f"{geo['country']}, {geo['city']} (ISP: {geo['isp']})"
        else:
            return "Geo lookup failed"
    except:
        return "Geo lookup error"

def check_abuse_ipdb(ip):
    try:
        headers = {
            "Key": ABUSE_API_KEY,
            "Accept": "application/json"
        }
        params = {
            "ipAddress": ip,
            "maxAgeInDays": 90
        }
        response = requests.get("https://api.abuseipdb.com/api/v2/check", headers=headers, params=params)
        data = response.json()["data"]
        return f"Abuse Score: {data['abuseConfidenceScore']} | Reports: {data['totalReports']}"
    except:
        return "Abuse check failed"

def analyze_auth_results(headers):
    auth_results = headers.get('Authentication-Results', '')
    spf = re.search(r'spf=(pass|fail|neutral|softfail|none)', auth_results, re.I)
    dkim = re.search(r'dkim=(pass|fail|none)', auth_results, re.I)
    dmarc = re.search(r'dmarc=(pass|fail|none)', auth_results, re.I)
    return {
        "SPF": spf.group(1) if spf else "Not Found",
        "DKIM": dkim.group(1) if dkim else "Not Found",
        "DMARC": dmarc.group(1) if dmarc else "Not Found"
    }

def analyze_spam_score(headers):
    score = headers.get('X-Spam-Score') or headers.get('X-Spam-Status', '')
    return score.strip() if score else "No spam score detected"

def check_return_path(headers):
    from_addr = headers.get('From', '').lower()
    reply_to = headers.get('Reply-To', '').lower()
    return_path = headers.get('Return-Path', '').lower()

    issues = []
    if reply_to and reply_to not in from_addr:
        issues.append("Reply-To mismatch.")
    if return_path and return_path not in from_addr:
        issues.append("Return-Path mismatch.")
    return " | ".join(issues) if issues else "OK"

def analyze_routing(received_headers):
    suspicious = []
    timestamps = []
    for rcv in received_headers:
        ips = extract_ip_addresses(rcv)
        times = re.findall(r';\s+(.*)', rcv)
        if times:
            try:
                dt = parsedate_to_datetime(times[0])
                timestamps.append(dt)
            except:
                pass
        if "unknown" in rcv.lower() or "localhost" in rcv.lower():
            suspicious.append(f"Suspicious relay: {rcv}")

    # Safe timestamp gap detection
    delays = []
    for i in range(1, len(timestamps)):
        try:
            dt1 = timestamps[i].astimezone().replace(tzinfo=None)
            dt2 = timestamps[i - 1].astimezone().replace(tzinfo=None)
            delta = (dt1 - dt2).total_seconds()
            if delta > 300:
                delays.append(f"Delay >5 min between hop {i} and {i+1}: {delta:.1f}s")
        except Exception as e:
            delays.append(f"Timestamp gap error at hop {i}: {e}")

    return suspicious + delays if suspicious or delays else ["Routing appears normal"]

def parse_email_headers(header_text):
    try:
        headers = Parser().parsestr(header_text)
        lines = []

        # Header Info
        lines.append("╔══════════════════ EMAIL METADATA ══════════════════╗")
        lines.append(f"From       : {headers.get('From')}")
        lines.append(f"To         : {headers.get('To')}")
        lines.append(f"Subject    : {headers.get('Subject')}")
        lines.append(f"Date       : {headers.get('Date')}")
        lines.append("╚════════════════════════════════════════════════════╝\n")

        # Auth
        auth = analyze_auth_results(headers)
        lines.append("╔═══════════ AUTHENTICATION RESULTS ═══════════╗")
        lines.append(f"{'Method':<10} | {'Status':<10}")
        lines.append(f"{'-'*10}-+-{'-'*10}")
        lines.append(f"{'SPF':<10} | {auth['SPF']:<10}")
        lines.append(f"{'DKIM':<10} | {auth['DKIM']:<10}")
        lines.append(f"{'DMARC':<10} | {auth['DMARC']:<10}")
        lines.append("╚══════════════════════════════════════════════╝\n")

        # Spam
        spam_score = analyze_spam_score(headers)
        lines.append("Spam Filter Status: " + spam_score)

        # Return-Path
        return_status = check_return_path(headers)
        lines.append("Return-Path Check : " + return_status)

        # Routing Analysis
        received_headers = headers.get_all('Received', [])
        routing_checks = analyze_routing(received_headers)
        lines.append("\n╔═════════════════ ROUTING CHECKS ═════════════════╗")
        for check in routing_checks:
            lines.append("• " + check)
        lines.append("╚══════════════════════════════════════════════════╝")

        # IP Info Table
        lines.append("\n╔═════════════════ IP GEO & REPUTATION ═════════════════╗")
        lines.append(f"{'IP Address':<16} | {'Geo':<25} | {'Abuse Score'}")
        lines.append(f"{'-'*16}-+-{'-'*25}-+-{'-'*13}")
        added_ips = set()
        for rcv in received_headers:
            ips = extract_ip_addresses(rcv)
            for ip in ips:
                if ip not in added_ips:
                    geo = get_geo_info(ip)
                    abuse = check_abuse_ipdb(ip)
                    abuse_score = abuse.replace("Abuse Score: ", "")
                    lines.append(f"{ip:<16} | {geo:<25} | {abuse_score}")
                    added_ips.add(ip)
        lines.append("╚══════════════════════════════════════════════════════╝")

        return "\n".join(lines)
    except Exception as e:
        return f"Error: {str(e)}"

def analyze():
    header_text = header_input.get("1.0", "end").strip()
    if not header_text:
        messagebox.showwarning("Input Required", "Please paste email headers.")
        return
    result_output.delete("1.0", "end")
    result_output.insert("end", parse_email_headers(header_text))

# GUI
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Advanced Email Header Analyzer by Khalid Dris")
app.geometry("1100x720")

title = ctk.CTkLabel(app, text="Advanced Email Header Analyzer", font=ctk.CTkFont(size=20, weight="bold"))
title.pack(pady=10)

header_input = ctk.CTkTextbox(app, width=1000, height=250, corner_radius=10)
header_input.pack(pady=10)

analyze_btn = ctk.CTkButton(app, text="Analyze Headers", command=analyze, fg_color="#1f6aa5", hover_color="#144e75")
analyze_btn.pack(pady=10)

result_output = ctk.CTkTextbox(app, width=1050, height=370, corner_radius=10)
result_output.pack(pady=10)

app.mainloop()
