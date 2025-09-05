# cNaps_eagle_eyes.py
import psutil
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import threading, time
from datetime import datetime
import socket, os, platform
from scapy.all import sniff, Raw, IP, TCP, UDP, ICMP, Ether
from queue import Queue

# -----------------------
# Config
# -----------------------
LOGO_FILENAME = "cNaPs.jpg"
REFRESH_INTERVAL = 1
SNIFF_FILTER = ""
MAX_LINES_IN_TEXT = 2000

# -----------------------
# Host info
# -----------------------
try:
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
except:
    host_name = "UnknownHost"
    host_ip = "0.0.0.0"

# -----------------------
# Sound control
# -----------------------
sound_alert_enabled = True

def toggle_sound_alert():
    global sound_alert_enabled
    sound_alert_enabled = not sound_alert_enabled
    if sound_alert_enabled:
        sound_btn.config(text="Son Activé ✅", bg="#33ff66")
    else:
        sound_btn.config(text="Son Désactivé ❌", bg="#ff4d4d")

def alert_sound():
    if not sound_alert_enabled:
        return
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 400)
        else:
            os.system('echo -e "\a"')
    except:
        pass

# -----------------------
# Network utils
# -----------------------
def get_network_speed(interval=1):
    old = psutil.net_io_counters()
    time.sleep(interval)
    new = psutil.net_io_counters()
    sent = (new.bytes_sent - old.bytes_sent) / interval
    recv = (new.bytes_recv - old.bytes_recv) / interval
    return sent, recv

def get_active_connections():
    connections = psutil.net_connections()
    conn_list = []
    for c in connections:
        if c.raddr:
            try:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                src_ip = c.laddr.ip
                src_port = c.laddr.port
                dst_ip = c.raddr.ip
                dst_port = c.raddr.port
                conn_list.append((timestamp, host_name, host_ip, src_ip, src_port, dst_ip, dst_port))
            except:
                continue
    return conn_list

# -----------------------
# Firewall actions
# -----------------------
def block_ip_command(ip):
    system = platform.system()
    if system == "Windows":
        return f'netsh advfirewall firewall add rule name="Block_{ip}" dir=in action=block remoteip={ip}'
    elif system == "Linux":
        return f'sudo iptables -A INPUT -s {ip} -j DROP'
    else:
        return None

def unblock_ip_command(ip):
    system = platform.system()
    if system == "Windows":
        return f'netsh advfirewall firewall delete rule name="Block_{ip}"'
    elif system == "Linux":
        return f'sudo iptables -D INPUT -s {ip} -j DROP'
    else:
        return None

def block_ip():
    ip = simpledialog.askstring("Bloquer IP", "Entrez l'IP à bloquer :")
    if ip:
        cmd = block_ip_command(ip)
        if not cmd:
            messagebox.showerror("Erreur", "OS non supporté")
            return
        try:
            os.system(cmd)
            messagebox.showinfo("Chef Action", f"IP {ip} bloquée ✅")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

def unblock_ip():
    ip = simpledialog.askstring("Débloquer IP", "Entrez l'IP à débloquer :")
    if ip:
        cmd = unblock_ip_command(ip)
        if not cmd:
            messagebox.showerror("Erreur", "OS non supporté")
            return
        try:
            os.system(cmd)
            messagebox.showinfo("Chef Action", f"IP {ip} débloquée ✅")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# -----------------------
# Identification utils
# -----------------------
def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

# -----------------------
# Packet sniffer
# -----------------------
packet_queue = Queue()

def detect_attack(packet):
    alerts = []
    if IP in packet:
        ip_src = packet[IP].src
        if TCP in packet:
            flags = packet[TCP].flags
            if flags == 2:
                alerts.append((ip_src, "SYN flood"))
            elif flags == 1 or flags == 41:
                alerts.append((ip_src, "TCP scan"))
        elif UDP in packet:
            alerts.append((ip_src, "UDP flood"))
        elif ICMP in packet:
            alerts.append((ip_src, "ICMP flood"))
    return alerts

def highlight_suspect_ip(ip_src):
    for item in conn_table.get_children():
        values = conn_table.item(item, "values")
        if values[3] == ip_src:
            conn_table.item(item, tags=("suspect",))

def format_packet_to_queue(packet):
    lines = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines.append((f"[{ts}] Packet captured\n", None))

    if Ether in packet:
        eth = packet[Ether]
        lines.append((f"Ethernet: src={eth.src} dst={eth.dst} type={eth.type}\n", None))

    if IP in packet:
        ip = packet[IP]
        lines.append(("IP: ", None))
        lines.append((ip.src, "src"))
        lines.append((" -> ", None))
        lines.append((ip.dst, "dst"))
        lines.append((f" TTL={ip.ttl} Len={ip.len}\n", None))

    if TCP in packet:
        tcp = packet[TCP]
        lines.append(("TCP: sport=", None))
        lines.append((str(tcp.sport), "port"))
        lines.append((" dport=", None))
        lines.append((str(tcp.dport)+"\n", "port"))
        lines.append((f"Flags={tcp.flags}\n", "tcp"))
    elif UDP in packet:
        udp = packet[UDP]
        lines.append(("UDP: sport=", None))
        lines.append((str(udp.sport), "port"))
        lines.append((" dport=", None))
        lines.append((str(udp.dport)+"\n", "port"))
        lines.append((f"Len={udp.len}\n", "udp"))
    elif ICMP in packet:
        lines.append(("ICMP packet\n", "icmp"))

    if Raw in packet:
        raw_bytes = bytes(packet[Raw])
        lines.append(("HEX DUMP:\n", "hexlabel"))
        for i in range(0, len(raw_bytes), 16):
            chunk = raw_bytes[i:i+16]
            hex_str = ' '.join(f"{b:02X}" for b in chunk)
            ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in chunk)
            lines.append((f"{i:04X}  {hex_str:<48}  {ascii_str}\n", "hex"))

    alerts = detect_attack(packet)
    for ip_src, atype in alerts:
        alert_text = f"⚠️ Attack detected: {atype} from {ip_src}\n"
        lines.append((alert_text, "alert"))
        alert_sound()
        highlight_suspect_ip(ip_src)

    packet_queue.put(lines)

def packet_sniffer():
    sniff(filter=SNIFF_FILTER, prn=format_packet_to_queue, store=False)

# -----------------------
# GUI setup
# -----------------------
root = tk.Tk()
root.title("cNaPs Eagle Eyes ")
root.geometry("1000x780")
root.configure(bg="#1e1e1e")

# --- Top frame
top_frame = tk.Frame(root, bg="#1e1e1e")
top_frame.pack(pady=8, anchor="w", fill="x")

try:
    logo_img = Image.open(LOGO_FILENAME).resize((80, 80))
    logo_tk = ImageTk.PhotoImage(logo_img)
    logo_label = tk.Label(top_frame, image=logo_tk, bg="#1e1e1e")
    logo_label.image = logo_tk
    logo_label.pack(side="left", padx=12)
except:
    logo_label = tk.Label(top_frame, width=12, height=5, bg="#2e2e2e")
    logo_label.pack(side="left", padx=12)

text_frame = tk.Frame(top_frame, bg="#1e1e1e")
text_frame.pack(side="left", padx=8)
title_label = tk.Label(text_frame, text="cNaPs Eagle Eyes", font=("Helvetica", 20, "bold"), fg="#00ff00", bg="#1e1e1e")
title_label.pack(anchor="w")
slogan_label = tk.Label(text_frame, text="Surveillez – Analysez – Contrôlez", font=("Helvetica", 11, "italic"), fg="#00ffaa", bg="#1e1e1e")
slogan_label.pack(anchor="w")

# --- Metrics + buttons
metrics_frame = tk.Frame(root, bg="#1e1e1e")
metrics_frame.pack(pady=4, fill="x")
upload_label = tk.Label(metrics_frame, text="Upload : 0 KB/s", font=("Helvetica", 12), fg="#00ff00", bg="#1e1e1e")
upload_label.pack(side="left", padx=8)
download_label = tk.Label(metrics_frame, text="Download : 0 KB/s", font=("Helvetica", 12), fg="#00ff00", bg="#1e1e1e")
download_label.pack(side="left", padx=8)

button_frame = tk.Frame(metrics_frame, bg="#1e1e1e")
button_frame.pack(side="right", padx=12)
block_btn = tk.Button(button_frame, text="Bloquer IP", command=block_ip, bg="#ff4d4d", fg="#000", width=14)
block_btn.pack(side="left", padx=6)
unblock_btn = tk.Button(button_frame, text="Débloquer IP", command=unblock_ip, bg="#33ff66", fg="#000", width=14)
unblock_btn.pack(side="left", padx=6)
sound_btn = tk.Button(button_frame, text="Son Activé ✅", command=toggle_sound_alert, bg="#33ff66", fg="#000", width=14)
sound_btn.pack(side="left", padx=6)

# --- Table of connections
table_frame = tk.Frame(root, bg="#1e1e1e")
table_frame.pack(padx=10, pady=6, fill="both", expand=False)
columns = ("Date/Heure", "Host Name", "Host IP", "Source IP", "Src Port", "Destination IP", "Dst Port")
conn_table = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
for col in columns:
    conn_table.heading(col, text=col)
    conn_table.column(col, width=120, anchor="center")
conn_table.pack(side="left", fill="both", expand=True)
table_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=conn_table.yview)
conn_table.configure(yscrollcommand=table_scroll.set)
table_scroll.pack(side="right", fill="y")
conn_table.tag_configure("suspect", background="#FF0000", foreground="#FFFFFF", font=("Helvetica", 10, "bold"))

# --- Bottom frame: packet logs
bottom_frame = tk.Frame(root, bg="#1e1e1e")
bottom_frame.pack(padx=10, pady=6, fill="both", expand=True)
packet_text = scrolledtext.ScrolledText(bottom_frame, bg="#111111", fg="#e6ffe6", font=("Consolas", 10), wrap="none")
packet_text.pack(fill="both", expand=True)
packet_text.tag_config("src", foreground="#7CFC00", font=("Consolas", 10, "bold"))
packet_text.tag_config("dst", foreground="#00FFFF", font=("Consolas", 10, "bold"))
packet_text.tag_config("tcp", foreground="#FF8C00", font=("Consolas", 10))
packet_text.tag_config("udp", foreground="#1E90FF", font=("Consolas", 10))
packet_text.tag_config("icmp", foreground="#FFFF00", font=("Consolas", 10))
packet_text.tag_config("hex", foreground="#00ff00", font=("Consolas", 10))
packet_text.tag_config("port", foreground="#FFD700", font=("Consolas", 10))
packet_text.tag_config("hexlabel", foreground="#00ffaa", font=("Consolas", 10, "bold"))
packet_text.tag_config("alert", foreground="#FF0000", font=("Consolas", 11, "bold"))

# --- Double-click event to show IP details with hex dump
def open_ip_detail(event):
    selected_item = conn_table.selection()
    if not selected_item:
        return
    values = conn_table.item(selected_item[0], "values")
    src_ip = values[3]
    dst_ip = values[5]
    src_port = values[4]
    dst_port = values[6]
    timestamp = values[0]

    detail_win = tk.Toplevel(root)
    detail_win.title(f"Détails IP: {src_ip}")
    detail_win.geometry("700x520")
    detail_win.configure(bg="#1e1e1e")

    info_text = f"Date/Heure: {timestamp}\n"
    info_text += f"Source IP: {src_ip}  Port: {src_port}\n"
    info_text += f"Destination IP: {dst_ip}  Port: {dst_port}\n"
    info_text += f"Host Name: {values[1]}\n"

    label = tk.Label(detail_win, text=info_text, font=("Consolas", 11), fg="#00ff00", bg="#1e1e1e", justify="left")
    label.pack(anchor="w", padx=10, pady=4)

    # --- Bouton Blocage rapide
    def quick_block():
        cmd = block_ip_command(src_ip)
        if cmd:
            try:
                os.system(cmd)
                messagebox.showinfo("Chef Action", f"IP {src_ip} bloquée ✅")
            except:
                messagebox.showerror("Erreur", f"Impossible de bloquer {src_ip}")
        else:
            messagebox.showerror("Erreur", "OS non supporté")

    block_btn = tk.Button(detail_win, text=f"Bloquer {src_ip}", command=quick_block, bg="#ff4d4d", fg="#000", width=20)
    block_btn.pack(pady=6)

    # --- Hex dump sous IP
    hex_text_ip = scrolledtext.ScrolledText(detail_win, bg="#111111", fg="#e6ffe6", font=("Consolas", 10), height=12, wrap="none")
    hex_text_ip.pack(fill="both", expand=True, padx=10, pady=6)

    for item in packet_queue.queue:
        for line, tag in item:
            if src_ip in line or dst_ip in line:
                if tag:
                    hex_text_ip.insert(tk.END, line, tag)
                else:
                    hex_text_ip.insert(tk.END, line)
    hex_text_ip.see(tk.END)

conn_table.bind("<Double-1>", open_ip_detail)

# --- GUI updater
def gui_updater():
    try:
        sent, recv = get_network_speed(interval=0.5)
        upload_label.config(text=f"Upload : {sent/1024:.2f} KB/s")
        download_label.config(text=f"Download : {recv/1024:.2f} KB/s")
    except:
        pass

    try:
        connections = get_active_connections()
        conn_table.delete(*conn_table.get_children())
        for row in connections:
            conn_table.insert("", "end", values=row)
    except:
        pass

    try:
        inserted = 0
        while not packet_queue.empty():
            lines = packet_queue.get_nowait()
            for text, tag in lines:
                if tag:
                    packet_text.insert(tk.END, text, tag)
                else:
                    packet_text.insert(tk.END, text)
            inserted += 1
        if float(packet_text.index('end-1c').split('.')[0]) > MAX_LINES_IN_TEXT:
            packet_text.delete('1.0', f'{int(MAX_LINES_IN_TEXT/2)}.0')
        if inserted:
            packet_text.see(tk.END)
    except:
        pass

    root.after(1000, gui_updater)

# --- Start threads
threading.Thread(target=packet_sniffer, daemon=True).start()
root.after(500, gui_updater)
root.mainloop()

