import tkinter as tk
from tkinter import ttk, messagebox
import scapy.all as scapy
import threading, time, ipaddress, subprocess, os, requests, tempfile, webbrowser
import pygame
from gtts import gTTS
import folium
import json
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import socket

INTERFACES = ["eth0", "lo"]
PROTECTED_IPS = ["10.0.2.15"]
SUBNET = ipaddress.ip_network("103.211.52.0/24")
BLOCKED_IPS = set()
WHITELISTED_IPS = set()
SCAN_COUNT = {}
LOCATION_CACHE = {}
ASN_CACHE = {}
REVERSE_DNS_CACHE = {}
GEO_POINTS = []
ALERTED_BLOCKED = set()
ALERTED_SCAN_ONCE = set()
PROTOCOL_COUNT = Counter()
PORT_COUNT = Counter()
LOG_FILE = "packet_log.txt"
ABUSE_API_KEY = "your_abuseipdb_api_key"  # replace with your real API key

pygame.mixer.init()

def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
            tts.save(f.name)
            pygame.mixer.music.load(f.name)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
    except Exception as e:
        print("Voice error:", e)

root = tk.Tk()
root.title("AI Guardian Advanced")
root.geometry("1400x800")

menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label="Unblock IP", command=lambda: unblock_popup())
menubar.add_cascade(label="Options", menu=filemenu)
root.config(menu=menubar)

main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

cols = ("Direction", "Attacker IP:Port", "Your IP:Port", "Protocol", "Info")
tree = ttk.Treeview(main_frame, columns=cols, show="headings", height=20)
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=250)
tree.pack(fill=tk.BOTH, expand=True)
tree.tag_configure("red", foreground="red")
tree.tag_configure("black", foreground="black")

def unblock_popup():
    top = tk.Toplevel()
    top.title("Unblock IP")
    tk.Label(top, text="Enter IP to Unblock:").pack()
    entry = tk.Entry(top)
    entry.pack()
    def do_unblock():
        ip = entry.get()
        if ip in BLOCKED_IPS:
            subprocess.call(["iptables", "-D", "INPUT", "-s", ip, "-j", "DROP"])
            BLOCKED_IPS.remove(ip)
            messagebox.showinfo("Unblocked", f"{ip} has been unblocked.")
        else:
            messagebox.showinfo("Not Blocked", f"{ip} was not blocked.")
    tk.Button(top, text="Unblock", command=do_unblock).pack()

status = ttk.Label(root, text="Status: Monitoring", relief=tk.SUNKEN, anchor='w')
status.pack(side=tk.BOTTOM, fill=tk.X)

plot_frame = ttk.Frame(root)
plot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(5, 5))
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

plot_visible = True

def toggle_plot():
    global plot_visible
    if plot_visible:
        canvas_widget.pack_forget()
    else:
        canvas_widget.pack()
    plot_visible = not plot_visible

def animate(i):
    ax1.clear()
    ax2.clear()
    if PROTOCOL_COUNT:
        ax1.pie(PROTOCOL_COUNT.values(), labels=PROTOCOL_COUNT.keys(), autopct='%1.1f%%')
        ax1.set_title("Live Protocol Distribution")
    if PORT_COUNT:
        top_ports = dict(Counter(PORT_COUNT).most_common(5))
        ax2.bar(top_ports.keys(), top_ports.values(), color='orange')
        ax2.set_title("Top Targeted Ports")
        ax2.set_ylabel("Attempts")

ani = FuncAnimation(fig, animate, interval=3000)
canvas.draw()

def get_geo_any_ip(ip):
    if ip in LOCATION_CACHE:
        return LOCATION_CACHE[ip]
    try:
        if ipaddress.ip_address(ip).is_private:
            LOCATION_CACHE[ip] = (None, None, "Private Network")
            return LOCATION_CACHE[ip]
        r = requests.get(f"http://ip-api.com/json/{ip}").json()
        if r['status'] == 'success':
            LOCATION_CACHE[ip] = (r['lat'], r['lon'], r['country'])
            return LOCATION_CACHE[ip]
    except:
        pass
    LOCATION_CACHE[ip] = (None, None, "Unknown")
    return LOCATION_CACHE[ip]

def get_asn_info(ip):
    if ip in ASN_CACHE:
        return ASN_CACHE[ip]
    try:
        r = requests.get(f"https://ipinfo.io/{ip}/json").json()
        ASN_CACHE[ip] = r.get("org", "Unknown")
    except:
        ASN_CACHE[ip] = "Unknown"
    return ASN_CACHE[ip]

def get_abuse_score(ip):
    try:
        r = requests.get("https://api.abuseipdb.com/api/v2/check", params={"ipAddress": ip, "maxAgeInDays": "90"},
                         headers={"Key": ABUSE_API_KEY, "Accept": "application/json"})
        return r.json()["data"]["abuseConfidenceScore"]
    except:
        return None

def get_reverse_dns(ip):
    if ip in REVERSE_DNS_CACHE:
        return REVERSE_DNS_CACHE[ip]
    try:
        host = socket.gethostbyaddr(ip)[0]
        REVERSE_DNS_CACHE[ip] = host
        return host
    except:
        return "Unknown"

def add_packet(direction, src, dst, proto, info, alert=False):
    color = "red" if alert else "black"
    tree.insert("", tk.END, values=(direction, src, dst, proto, info), tags=(color,))
    with open(LOG_FILE, "a") as f:
        f.write(f"{direction},{src},{dst},{proto},{info}\n")

def honeypot(pkt):
    try:
        scapy.send(scapy.IP(dst=pkt[scapy.IP].src)/scapy.TCP(flags="R"), verbose=0)
    except:
        pass

def block_ip(ip):
    subprocess.call(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
    BLOCKED_IPS.add(ip)

def is_exploit(pkt):
    if pkt.haslayer(scapy.TCP):
        return pkt[scapy.TCP].flags in [0x00, 0x01, 0x29, 0x02]
    if pkt.haslayer(scapy.ICMP):
        return True
    return False

def is_targeted(ip):
    try:
        return ip in PROTECTED_IPS or ipaddress.ip_address(ip) in SUBNET
    except:
        return False

def trace_host(ip):
    try:
        print("Traceroute for", ip)
        result = subprocess.check_output(["traceroute", "-n", ip], stderr=subprocess.STDOUT)
        print(result.decode())
    except Exception as e:
        print("Traceroute error:", e)

def handle_packet(pkt):
    if pkt.haslayer(scapy.IP):
        src = pkt[scapy.IP].src
        dst = pkt[scapy.IP].dst
        proto = {1: "ICMP", 6: "TCP", 17: "UDP"}.get(pkt[scapy.IP].proto, str(pkt[scapy.IP].proto))
        sport = pkt[scapy.TCP].sport if pkt.haslayer(scapy.TCP) else ""
        dport = pkt[scapy.TCP].dport if pkt.haslayer(scapy.TCP) else ""
        direction = "Incoming" if dst in PROTECTED_IPS else "Outgoing"
        info = "OK"
        alert = False
        if is_targeted(dst):
            if is_exploit(pkt):
                honeypot(pkt)
                SCAN_COUNT[src] = SCAN_COUNT.get(src, 0) + 1
                info = f"Scan #{SCAN_COUNT[src]}"
                alert = True
                PORT_COUNT[dport] += 1
                PROTOCOL_COUNT[proto] += 1
                if src not in WHITELISTED_IPS:
                    if SCAN_COUNT[src] >= 3 and src not in BLOCKED_IPS:
                        block_ip(src)
                        speak(f"Blocked IP {src} after multiple scans.")
                    if src not in ALERTED_SCAN_ONCE:
                        geo = get_geo_any_ip(src)
                        abuse = get_abuse_score(src)
                        org = get_asn_info(src)
                        dns = get_reverse_dns(src)
                        trace_host(src)
                        GEO_POINTS.append({'ip': src, 'lat': geo[0], 'lon': geo[1], 'proto': proto, 'blocked': src in BLOCKED_IPS})
                        speak(f"Attack from {src} ({dns}) in {geo[2]}, Org: {org}, Abuse score: {abuse}")
                        ALERTED_SCAN_ONCE.add(src)
        add_packet(direction, f"{src}:{sport}", f"{dst}:{dport}", proto, info, alert)

def start_sniff():
    for iface in INTERFACES:
        threading.Thread(target=lambda: scapy.sniff(iface=iface, prn=handle_packet, store=False), daemon=True).start()

def draw_map():
    fmap = folium.Map(location=[20, 0], zoom_start=2)
    for p in GEO_POINTS:
        if p['lat'] and p['lon']:
            folium.Marker(
                location=[p['lat'], p['lon']],
                popup=f"{p['ip']} - {p['proto']}",
                icon=folium.Icon(color='red' if p['blocked'] else 'orange')
            ).add_to(fmap)
    fmap.save("attack_map.html")
    webbrowser.open("attack_map.html")

btn_frame = ttk.Frame(root)
btn_frame.pack(pady=5)
ttk.Button(btn_frame, text="Show GeoMap", command=draw_map).pack(side=tk.LEFT, padx=10)
ttk.Button(btn_frame, text="Toggle Plot", command=toggle_plot).pack(side=tk.LEFT, padx=10)

speak("AI Guardian initialized with advanced intelligence.")
start_sniff()
root.mainloop()
