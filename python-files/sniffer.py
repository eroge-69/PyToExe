import tkinter as tk
from tkinter import ttk, scrolledtext
from threading import Thread, Event
from scapy.all import sniff, IP, TCP, UDP, Raw, DNS, DNSQR
from collections import Counter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime
import json
import mysql.connector
import requests
import ipaddress
import re
import whois
from collections import defaultdict
import math
import time
import queue
import threading

# Configure matplotlib to use dark theme
plt.style.use('dark_background')

# Create a modern dark theme
DARK_BG = "#2e2e2e"
DARKER_BG = "#1e1e1e"
ACCENT_COLOR = "#4e79a7"
HIGHLIGHT_COLOR = "#f1fa8c"
TEXT_COLOR = "#f8f8f2"
BUTTON_COLOR = "#44475a"

data_queue = queue.Queue()

# State for rate limiting and timestamp tracking per source IP
ntp_request_counters = defaultdict(lambda: {"count": 0, "first_seen": time.time()})
ntp_last_transmit_time = {}

# Example vulnerable NTP commands (in raw payload hex form, simplified)
VULNERABLE_COMMAND_PATTERNS = [
    b'\x17\x00\x03\x2a',  # monlist (mode 7, opcode 3, ref id 42)
    b'\x17\x00\x02\x2a',  # readvar (mode 7, opcode 2, ref id 42)
]

# Suspicious TLDs
SUSPICIOUS_TLDS = {'.xyz', '.top', '.club', '.pw', '.info', '.icu', '.online', '.site', '.buzz', '.work', '.link'}

# Regex for Base64
BASE64_REGEX = re.compile(r'^[A-Za-z0-9+/=]{20,}$')

# Known suspicious public DNS resolvers
SUSPICIOUS_RESOLVERS = {'8.26.56.26', '37.235.1.174', '77.88.8.1', '94.140.14.14'}

# Suspicious query types
SUSPICIOUS_QTYPES = {255, 33, 99}

query_tracker = defaultdict(list)


# --- SETTINGS ---
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1394367324777222165/yG58rf5Jxr287dvwkuXLZoByAmqUiP_eOUXWFLiztP6ZnrTvticddY4QkuKs8gLYSXtB"
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Masinuta224#$%',
    'database': 'iot_defender'
}

def shannon_entropy(data):
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy -= p_x * math.log2(p_x)
    return entropy


def get_domain_age(domain):
    try:
        w = whois.whois(domain)
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        if creation_date:
            age_days = (datetime.datetime.now() - creation_date).days
            return age_days
    except Exception:
        return None
    return None


# --- WHITELISTED SERVICES ---
WHITELISTED_IPS = {
    "89.36.93.9",       # example NTP server
    "129.6.15.28",      # time.nist.gov (NTP)
    "8.8.8.8",          # Google DNS
    "8.8.4.4",          # Google DNS secondary
    "1.1.1.1",          # Cloudflare DNS
    "1.0.0.1",          # Cloudflare DNS secondary,
    "192.168.1.1",      # Local router
    "192.168.1.100"     # Local device
}

WHITELISTED_PORTS = {
    53,     # DNS
    123,    # NTP
    80,     # HTTP
    443,    # HTTPS
    67, 68, # DHCP
    1900,   # SSDP
    5353    # mDNS
}


def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return False


def is_weird_port(port):
    if 0 <= port < 10 and port not in (7, 9):
        return True
    if 10000 <= port <= 20000:
        return True
    if port > 55555:
        return True
    return False


def check_tcp_flags(pkt):
    if TCP in pkt:
        flags = pkt[TCP].flags

        suspicious_flag_combinations = [
            0x03,  # SYN + FIN
            0x06,  # SYN + RST
            0x05,  # FIN + RST
            0x3F,  # All flags set (FIN, SYN, RST, PSH, ACK, URG)
            0x00,  # No flags set
            0x29,  # FIN + PSH + URG
            0x07,  # SYN + FIN + RST
        ]

        if flags in suspicious_flag_combinations:
            return True

    return False


def analyze_http(pkt):
    suspicious_patterns = [
        "UNION SELECT",      # SQLi
        "' OR '1'='1",       # SQLi
        "<script>",          # XSS
        "../",               # Directory traversal
        "%00",               # Null byte injection
        "file://",           # LFI
        "<?php",             # PHP injection
        "wget ", "curl ",    # Command injection tools
        "admin'--",          # SQLi bypass
    ]

    # Only analyze TCP packets on port 80 (HTTP)
    if TCP in pkt:
        dport = pkt[TCP].dport
        sport = pkt[TCP].sport
        if dport == 80 or sport == 80:
            if Raw in pkt:
                data = pkt[Raw].load.decode(errors='ignore')
                if not data.strip():
                    return True  # Empty payload on HTTP port? Suspicious.

                # Check for common HTTP methods
                methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'CONNECT', 'TRACE', 'PATCH']
                if any(data.upper().startswith(m) for m in methods):
                    # Search for suspicious payload patterns
                    data_lower = data.lower()
                    for pattern in suspicious_patterns:
                        if pattern.lower() in data_lower:
                            return True  # Detected attack pattern
                    
                    return False  # Looks normal HTTP
                else:
                    return True  # Non-standard request on HTTP port
    return False

def analyze_https(pkt):
    # Only analyze TCP packets on port 443 (HTTPS)
    if TCP in pkt:
        dport = pkt[TCP].dport
        sport = pkt[TCP].sport

        if dport == 443 or sport == 443:
            if Raw in pkt:
                data = pkt[Raw].load

                # TLS Handshake Content Type (0x16) and minimum size
                if len(data) > 5 and data[0] == 0x16:
                    # TLS Version check (basic sanity)
                    version = data[1:3]
                    if version not in [b'\x03\x00', b'\x03\x01', b'\x03\x02', b'\x03\x03']:
                        return True  # Suspicious TLS version (0x0304 is TLS 1.3, could add)

                    # Flag abnormally large Client Hello packets (could indicate abuse, fuzzing)
                    if len(data) > 4000:
                        return True
                    
                    # Detect onion domains (Tor usage) in SNI
                    if b".onion" in data:
                        return True
                    
                    # Extract potential SNI for additional checks
                    sni_match = re.search(rb"\x00[\x00-\xff]{0,2}([\w\.-]+\.[a-z]{2,})", data)
                    if sni_match:
                        sni = sni_match.group(1).decode(errors='ignore')
                        if len(sni) > 100 or any(c in sni for c in ['..', '/', '\\']):
                            return True  # Abnormal SNI format
                        if sni.endswith('.onion'):
                            return True
                    
                    # Unusual cipher suites length (abnormally large list)
                    if len(data) > 2000 and b'\x00\x2f' not in data:  # 0x002f is common TLS_RSA_WITH_AES_128_CBC_SHA
                        return True
                    
                # Abnormal content types on 443 (could be non-TLS traffic trying to exploit port 443)
                if data[0] not in [0x14, 0x15, 0x16, 0x17]:
                    return True

            # Flag empty packets on port 443 as abnormal unless part of handshake
            if Raw not in pkt and len(pkt[TCP].payload) == 0:
                return True

    return False

def analyze_dns(pkt):
    if UDP in pkt and (pkt[UDP].dport == 53 or pkt[UDP].sport == 53):
        if DNS in pkt and pkt[DNS].qr == 0:  # DNS query
            try:
                src_ip = pkt[IP].src
                qname = pkt[DNSQR].qname.decode(errors='ignore').strip('.').lower()

                now = datetime.datetime.now().timestamp()
                query_tracker[src_ip] = [t for t in query_tracker[src_ip] if now - t < 10]
                query_tracker[src_ip].append(now)
                if len(query_tracker[src_ip]) > 10:
                    return True

                if len(qname) > 255:
                    return True

                if any(c in qname for c in [';', '|', '&', '$']):
                    return True

                if any(qname.endswith(tld) for tld in SUSPICIOUS_TLDS):
                    return True

                subdomains = qname.split('.')
                for sub in subdomains:
                    if len(sub) > 20 and BASE64_REGEX.match(sub):
                        return True

                if any(sum(c.isalpha() for c in sub) / len(sub) < 0.3 for sub in subdomains if len(sub) > 5):
                    return True
                if shannon_entropy(qname) > 4.0:
                    return True

                suspicious_keywords = ['dnslog', 'tunnel', 'exfil', 'c2']
                if any(word in qname for word in suspicious_keywords):
                    return True

                if pkt[DNS].qd.qtype in SUSPICIOUS_QTYPES:
                    return True

                if UDP in pkt and pkt[UDP].len > 512:
                    return True

                dst_ip = pkt[IP].dst
                if dst_ip in SUSPICIOUS_RESOLVERS:
                    return True

                if pkt[DNS].qd.qtype == 16 and len(qname) > 100:
                    return True

                if '.' in qname:
                    domain = '.'.join(qname.split('.')[-2:])
                    age = get_domain_age(domain)
                    if age is not None and age < 30:
                        return True

            except Exception:
                return True

    return False

def analyze_ntp(pkt, rate_limit_threshold=10, rate_limit_period=60):
    # Check UDP packets on port 123 (NTP)
    if UDP in pkt and (pkt[UDP].dport == 123 or pkt[UDP].sport == 123):
        if Raw in pkt:
            data = pkt[Raw].load
            
            # Basic size check
            if len(data) < 48:  # NTP packet size minimum
                return True
            
            li_vn_mode = data[0]
            mode = li_vn_mode & 0x7
            if mode not in range(1, 8):  # Valid modes: 1-7
                return True
            
            # --- 1. Check for suspicious extension fields ---
            # Extension fields start after 48 bytes, must be multiples of 4 bytes
            if len(data) > 48:
                ext_len = len(data) - 48
                if ext_len % 4 != 0 or ext_len > 1024:  # Arbitrary max extension length
                    return True
            
            # --- 2. Detect known vulnerable commands ---
            for pattern in VULNERABLE_COMMAND_PATTERNS:
                if pattern in data:
                    return True
            
            # --- 3. Rate limiting per source IP ---
            src_ip = pkt[IP].src
            now = time.time()
            counter = ntp_request_counters[src_ip]
            # Reset counter if time window expired
            if now - counter["first_seen"] > rate_limit_period:
                counter["count"] = 0
                counter["first_seen"] = now
            counter["count"] += 1
            if counter["count"] > rate_limit_threshold:
                # Too many requests from one IP in short time: potential abuse
                return True
            
            # --- 4. Transmit timestamp sanity check ---
            # Transmit timestamp is bytes 40-47 (64 bits)
            if len(data) >= 48:
                transmit_ts_bytes = data[40:48]
                # Convert NTP timestamp to float seconds
                ntp_sec = int.from_bytes(transmit_ts_bytes[:4], 'big')
                ntp_frac = int.from_bytes(transmit_ts_bytes[4:], 'big')
                transmit_ts = ntp_sec + ntp_frac / (1 << 32)
                
                # NTP epoch starts 1900, convert to UNIX epoch
                UNIX_EPOCH_OFFSET = 2208988800
                transmit_unix_ts = transmit_ts - UNIX_EPOCH_OFFSET
                
                now_unix = time.time()
                # Flag if transmit timestamp differs from now by > 24h (possible spoof)
                if abs(transmit_unix_ts - now_unix) > 86400:
                    return True
                
                # Check for replayed transmit timestamp
                last_ts = ntp_last_transmit_time.get(src_ip)
                if last_ts and transmit_unix_ts <= last_ts:
                    return True  # Possible replay attack
                ntp_last_transmit_time[src_ip] = transmit_unix_ts

        else:
            # No Raw data on NTP port -> suspicious
            return True

    return False


def is_suspicious(pkt):
    if IP in pkt:
        src_ip = pkt[IP].src
        dest_ip = pkt[IP].dst
        proto = None
        sport = None
        dport = None

        if TCP in pkt:
            proto = 'TCP'
            sport = pkt[TCP].sport
            dport = pkt[TCP].dport
        elif UDP in pkt:
            proto = 'UDP'
            sport = pkt[UDP].sport
            dport = pkt[UDP].dport
        else:
            proto = 'OTHER'

        # WHITELIST checks: if either IP or ports are whitelisted, ignore
        if src_ip in WHITELISTED_IPS or dest_ip in WHITELISTED_IPS:
            return False
        if (sport in WHITELISTED_PORTS) or (dport in WHITELISTED_PORTS):
            return False

        # Basic IP checks
        try:
            ip_obj = ipaddress.ip_address(dest_ip)
            if ip_obj.is_multicast or ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_reserved:
                return False
        except ValueError:
            return True

        # Ignore broadcast address
        if dest_ip == '255.255.255.255':
            return False

        # Basic suspicious port checks
        if is_weird_port(dport) or is_weird_port(sport):
            return True

        # TCP flags anomaly check
        if check_tcp_flags(pkt):
            return True

        # Protocol-specific analysis
        if proto == 'TCP':
            if analyze_http(pkt):
                return True
            if analyze_https(pkt):
                return True
        if proto == 'UDP':
            if analyze_dns(pkt):
                return True
            if analyze_ntp(pkt):
                return True

        # Flag if destination IP is not private (from previous logic)
        if not dest_ip.startswith(('10.', '192.168.', '172.16.', '172.17.', '172.18.', '172.19.', '172.20.',
                                  '172.21.', '172.22.', '172.23.', '172.24.', '172.25.', '172.26.', '172.27.',
                                  '172.28.', '172.29.', '172.30.', '172.31.')):
            return True

    return False


# --- LOGGING FUNCTIONS ---
def log_to_file(pkt_summary):
    with open("alerts.json", "a") as f:
        json.dump(pkt_summary, f)
        f.write("\n")


def log_to_mysql(pkt_summary):
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        sql = "INSERT INTO alerts (timestamp, src_ip, dest_ip, protocol, details) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(sql, (
            pkt_summary["timestamp"],
            pkt_summary["src_ip"],
            pkt_summary["dest_ip"],
            pkt_summary["protocol"],
            pkt_summary["details"]
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"MySQL error: {e}")


def alert_discord(pkt_summary):
    data = {
        "embeds": [{
            "title": "🚨 IoT Defender Alert",
            "description": f"Suspicious Packet Detected\n"
                           f"Source: {pkt_summary['src_ip']}\n"
                           f"Destination: {pkt_summary['dest_ip']}\n"
                           f"Protocol: {pkt_summary['protocol']}\n"
                           f"Details: {pkt_summary['details']}",
            "color": 15158332
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Discord error: {e}")


class IoTDefenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("IoT Defender Sniffer")
        self.root.geometry("1200x800")
        self.root.configure(bg=DARK_BG)
        
        # Apply modern theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=DARK_BG, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        style.configure('TFrame', background=DARK_BG)
        style.configure('TLabel', background=DARK_BG, foreground=TEXT_COLOR, font=('Segoe UI', 10))
        style.configure('TButton', background=BUTTON_COLOR, foreground=TEXT_COLOR, 
                        font=('Segoe UI', 10, 'bold'), borderwidth=1)
        style.map('TButton', background=[('active', ACCENT_COLOR)])
        style.configure('TNotebook', background=DARKER_BG, borderwidth=0)
        style.configure('TNotebook.Tab', background=DARKER_BG, foreground=TEXT_COLOR, 
                        padding=[10, 5], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', ACCENT_COLOR)], 
                 foreground=[('selected', TEXT_COLOR)])
        
        self.packet_count = 0
        self.alerts_counter = Counter()
        self.suspicious_ips_counter = Counter()

        # Create main frame
        main_frame = ttk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.logs_tab = ttk.Frame(self.notebook)
        self.stats_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text='Dashboard')
        self.notebook.add(self.logs_tab, text='Packet Logs')
        self.notebook.add(self.stats_tab, text='Statistics')
        
        # Build dashboard tab
        self.build_dashboard_tab()
        
        # Build logs tab
        self.build_logs_tab()
        
        # Build stats tab
        self.build_stats_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.sniff_thread = None
        self.stop_event = Event()

        # Start periodic updates
        self.periodic_packet_update()
        self.periodic_full_update()

    def build_dashboard_tab(self):
        # Dashboard layout using frames
        top_frame = ttk.Frame(self.dashboard_tab)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        bottom_frame = ttk.Frame(self.dashboard_tab)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control panel on top
        control_frame = ttk.LabelFrame(top_frame, text="Sniffer Controls")
        control_frame.pack(side=tk.LEFT, fill=tk.X, padx=5, pady=5, expand=True)
        
        self.start_button = ttk.Button(control_frame, text="▶ Start Sniffing", command=self.start_sniffing)
        self.start_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.stop_button = ttk.Button(control_frame, text="⏹ Stop Sniffing", command=self.stop_sniffing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # Packet counter
        counter_frame = ttk.LabelFrame(top_frame, text="Packet Statistics")
        counter_frame.pack(side=tk.RIGHT, fill=tk.X, padx=5, pady=5, expand=True)
        
        self.packet_label = ttk.Label(counter_frame, text="Packets processed: 0", font=("Segoe UI", 10))
        self.packet_label.pack(pady=5)
        
        self.alert_count_label = ttk.Label(counter_frame, text="Alerts detected: 0", font=("Segoe UI", 10))
        self.alert_count_label.pack(pady=5)
        
        # Charts in bottom frame
        chart_frame = ttk.Frame(bottom_frame)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create charts with better sizing
        self.fig, (self.ax_alerts, self.ax_ips) = plt.subplots(1, 2, figsize=(10, 4))
        self.fig.set_facecolor(DARKER_BG)
        self.fig.tight_layout(pad=4)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Initialize empty charts
        self.ax_alerts.set_title("Alerts by Protocol/Type", color=HIGHLIGHT_COLOR)
        self.ax_ips.set_title("Top Suspicious Source IPs", color=HIGHLIGHT_COLOR)
        self.canvas.draw()

    def build_logs_tab(self):
        # Logs tab content
        log_frame = ttk.Frame(self.logs_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create log viewer
        self.text_area = scrolledtext.ScrolledText(
            log_frame, 
            width=100, 
            height=30,
            bg=DARKER_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            font=('Consolas', 9)
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add clear button
        clear_btn = ttk.Button(log_frame, text="Clear Logs", command=self.clear_logs)
        clear_btn.pack(pady=5)

    def build_stats_tab(self):
        # Stats tab content
        stats_frame = ttk.Frame(self.stats_tab)
        stats_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create two columns
        left_frame = ttk.Frame(stats_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        right_frame = ttk.Frame(stats_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Alerts frame
        alerts_frame = ttk.LabelFrame(left_frame, text="Alerts by Protocol/Type")
        alerts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.alerts_text = tk.Text(
            alerts_frame, 
            height=15, 
            width=40,
            bg=DARKER_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            font=('Consolas', 9)
        )
        self.alerts_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Suspicious IPs frame
        ips_frame = ttk.LabelFrame(right_frame, text="Top Suspicious Source IPs")
        ips_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.suspicious_text = tk.Text(
            ips_frame, 
            height=15, 
            width=40,
            bg=DARKER_BG,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            font=('Consolas', 9)
        )
        self.suspicious_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def clear_logs(self):
        self.text_area.delete(1.0, tk.END)

    def periodic_packet_update(self):
        # Update packet count every second
        self.packet_label.config(text=f"Packets processed: {self.packet_count}")
        self.alert_count_label.config(text=f"Alerts detected: {sum(self.alerts_counter.values())}")
        self.root.after(1000, self.periodic_packet_update)

    def periodic_full_update(self):
        # Update stats every 10 seconds
        self.update_stats()
        self.root.after(10000, self.periodic_full_update)

    def append_text(self, text):
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.tag_configure("alert", foreground="#ff5555")
        if "ALERT" in text:
            self.text_area.tag_add("alert", "end-1c linestart", "end-1c lineend")

    def start_sniffing(self):
        if not self.sniff_thread or not self.sniff_thread.is_alive():
            self.stop_event.clear()
            self.sniff_thread = Thread(target=self.sniff_packets)
            self.sniff_thread.daemon = True
            self.sniff_thread.start()
            self.append_text("[*] Started sniffing...\n")
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Sniffing network traffic...")

    def stop_sniffing(self):
        self.stop_event.set()
        self.append_text("[*] Stopping sniffing...\n")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Sniffing stopped")

    def sniff_packets(self):
        sniff(prn=self.process_packet, store=False, stop_filter=lambda x: self.stop_event.is_set())

    def process_packet(self, packet):
        try:
            self.packet_count += 1

            if is_suspicious(packet):
                # Extract details
                if packet.haslayer(IP):
                    src_ip = packet[IP].src
                    dst_ip = packet[IP].dst
                    protocol = packet.sprintf("%IP.proto%")
                else:
                    src_ip = "N/A"
                    dst_ip = "N/A"
                    protocol = "N/A"

                # Create summary
                timestamp = datetime.datetime.now().isoformat()
                details = f"Suspicious activity: {protocol} from {src_ip} to {dst_ip}"
                pkt_summary = {
                    "timestamp": timestamp,
                    "src_ip": src_ip,
                    "dest_ip": dst_ip,
                    "protocol": protocol,
                    "details": details
                }

                # Log to file, MySQL, Discord
                log_to_file(pkt_summary)
                log_to_mysql(pkt_summary)
                alert_discord(pkt_summary)

                # Update counters
                self.alerts_counter[(protocol.upper(), "Suspicious")] += 1
                self.suspicious_ips_counter[src_ip] += 1

                # Update GUI
                text = f"ALERT! Packet #{self.packet_count}: {protocol} from {src_ip} to {dst_ip}\n"
                self.root.after(0, self.append_text, text)
                self.root.after(0, self.update_stats)

        except Exception as e:
            error_text = f"Error processing packet: {e}\n"
            self.root.after(0, self.append_text, error_text)

    def update_stats(self):
        # Update alerts text
        self.alerts_text.config(state=tk.NORMAL)
        self.alerts_text.delete(1.0, tk.END)
        for (proto, alert), count in self.alerts_counter.most_common(10):
            self.alerts_text.insert(tk.END, f"{proto} - {alert}: {count}\n")
        self.alerts_text.config(state=tk.DISABLED)

        # Update suspicious IPs text
        self.suspicious_text.config(state=tk.NORMAL)
        self.suspicious_text.delete(1.0, tk.END)
        for ip, count in self.suspicious_ips_counter.most_common(10):
            self.suspicious_text.insert(tk.END, f"{ip}: {count}\n")
        self.suspicious_text.config(state=tk.DISABLED)

        # Update matplotlib charts
        self.ax_alerts.clear()
        alert_labels = [f"{p}/{a}" for (p, a) in self.alerts_counter.keys()][:10]
        alert_values = list(self.alerts_counter.values())[:10]
        if alert_labels and alert_values:
            self.ax_alerts.bar(alert_labels, alert_values, color=ACCENT_COLOR)
        self.ax_alerts.set_title("Alerts by Protocol/Type", color=HIGHLIGHT_COLOR)
        self.ax_alerts.tick_params(axis='x', rotation=45, labelsize=8, colors=TEXT_COLOR)
        self.ax_alerts.tick_params(axis='y', colors=TEXT_COLOR)
        self.ax_alerts.set_facecolor(DARKER_BG)

        self.ax_ips.clear()
        top_ips = self.suspicious_ips_counter.most_common(10)
        if top_ips:
            ips = [ip for ip, count in top_ips]
            counts = [count for ip, count in top_ips]
            self.ax_ips.bar(ips, counts, color='#ff5555')
        self.ax_ips.set_title("Top Suspicious Source IPs", color=HIGHLIGHT_COLOR)
        self.ax_ips.tick_params(axis='x', rotation=45, labelsize=8, colors=TEXT_COLOR)
        self.ax_ips.tick_params(axis='y', colors=TEXT_COLOR)
        self.ax_ips.set_facecolor(DARKER_BG)

        self.fig.tight_layout()
        self.canvas.draw()


if __name__ == "__main__":
    root = tk.Tk()
    gui_instance = IoTDefenderGUI(root)
    root.mainloop()
