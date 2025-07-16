import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os

# IP klasörü oluştur
IP_DIR = "ip_kayitlari"
os.makedirs(IP_DIR, exist_ok=True)

# Bölüm isimleri
bolum_isimleri = {
    1: "GYB",
    2: "YDYB",
    3: "KVC",
    4: "Koroner"
}

# Arayüz
window = tk.Tk()
window.title("📡 IP Ping ve İzleme Aracı")
window.geometry("860x660")
window.resizable(False, False)

# Global değişkenler (root sonrası tanımlanmalı!)
ip_results = []
show_only_down = tk.BooleanVar(value=False)
stop_event = threading.Event()

# IP ve açıklamayı ayrıştır
def parse_ip_line(line):
    if "#" in line:
        ip, label = line.split("#", 1)
        return ip.strip(), label.strip()
    return line.strip(), ""

# Ping fonksiyonu
def ping(ip, count=2):
    try:
        output = subprocess.check_output(
            ["ping", "-n", str(count), ip],
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        return "TTL=" in output
    except subprocess.CalledProcessError:
        return False

# Tabloyu güncelle
def update_table():
    result_table.delete(*result_table.get_children())
    for ip, label, status in ip_results:
        if show_only_down.get() and status == "UP":
            continue
        tag = "up" if status == "UP" else "down"
        result_table.insert("", tk.END, values=(ip, label, status), tags=(tag,))

# Ping başlat/durdur
def start_or_stop_ping():
    if ping_button["text"] == "🛑 Ping Durdur":
        stop_event.set()
        ping_button.config(text="🟢 Ping Başlat")
        return

    ip_lines = ip_input.get("1.0", tk.END).strip().splitlines()
    if not ip_lines:
        messagebox.showwarning("Uyarı", "Lütfen IP adreslerini girin.")
        return

    ip_results.clear()
    result_table.delete(*result_table.get_children())
    ping_button.config(text="🛑 Ping Durdur")
    stop_event.clear()

    def run():
        for line in ip_lines:
            if stop_event.is_set():
                break
            ip, label = parse_ip_line(line)
            if ip:
                reachable = ping(ip)
                status = "UP" if reachable else "DOWN"
                ip_results.append((ip, label, status))
                update_table()
        ping_button.config(text="🟢 Ping Başlat")
        if not stop_event.is_set():
            messagebox.showinfo("Tamamlandı", "Ping işlemi tamamlandı.")

    threading.Thread(target=run, daemon=True).start()

# IP dosyalarını yükle/kaydet
def load_ips(bolum):
    filename = os.path.join(IP_DIR, f"bolum{bolum}.txt")
    if not os.path.exists(filename):
        open(filename, "w").close()
    with open(filename, "r", encoding="utf-8") as f:
        content = f.read()
    ip_input.delete("1.0", tk.END)
    ip_input.insert(tk.END, content)
    messagebox.showinfo("Yüklendi", f"{bolum_isimleri[bolum]} IP'leri yüklendi.")

def save_ips(bolum):
    filename = os.path.join(IP_DIR, f"bolum{bolum}.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(ip_input.get("1.0", tk.END).strip())
    messagebox.showinfo("Kaydedildi", f"{bolum_isimleri[bolum]} IP'leri kaydedildi.")

# Stil
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
style.map("Treeview", background=[('selected', '#d0eaff')])

# Açıklama başlığı
tk.Label(window, text="📋 IP Adreslerini Girin (örnek: 10.1.13.90 # GYB Monitör 1)", font=("Segoe UI", 10, "bold")).pack(pady=8)

# IP giriş alanı
ip_input = tk.Text(window, height=6, width=100, font=("Consolas", 10), bd=2, relief="groove")
ip_input.pack()

# Bölüm butonları
bolum_frame = tk.Frame(window)
bolum_frame.pack(pady=5)

for i in range(1, 5):
    ttk.Button(bolum_frame, text=f"{bolum_isimleri[i]} Yükle", width=18, command=lambda b=i: load_ips(b)).grid(row=0, column=i-1, padx=5)
    ttk.Button(bolum_frame, text=f"{bolum_isimleri[i]} Kaydet", width=18, command=lambda b=i: save_ips(b)).grid(row=1, column=i-1, padx=5, pady=3)

# Ping başlat/durdur butonu
ping_button = ttk.Button(window, text="🟢 Ping Başlat", command=start_or_stop_ping)
ping_button.pack(pady=10)

# DOWN filtresi
filter_frame = tk.Frame(window)
filter_frame.pack()
ttk.Checkbutton(filter_frame, text="🔴 Sadece DOWN olanları göster", variable=show_only_down, command=update_table).pack()

# Sonuç alanı (Treeview + Scrollbar)
frame_table = tk.Frame(window)
frame_table.pack(padx=10, pady=10, fill="both", expand=True)

columns = ("ip", "label", "status")
result_table = ttk.Treeview(frame_table, columns=columns, show="headings", height=15)

# Sütun başlıkları ve genişlikleri
result_table.heading("ip", text="IP Adresi")
result_table.heading("label", text="Açıklama")
result_table.heading("status", text="Durum")
result_table.column("ip", width=200, anchor="w")
result_table.column("label", width=430, anchor="w")
result_table.column("status", width=100, anchor="center")

# Grid ile yerleştirme
result_table.grid(row=0, column=0, sticky="nsew")

# Dikey scrollbar
vsb = ttk.Scrollbar(frame_table, orient="vertical", command=result_table.yview)
vsb.grid(row=0, column=1, sticky="ns")

# Yatay scrollbar
hsb = ttk.Scrollbar(frame_table, orient="horizontal", command=result_table.xview)
hsb.grid(row=1, column=0, sticky="ew")

# Treeview'a scrollbar bağlama
result_table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

# Frame içinde satır ve sütunların büyüme davranışı
frame_table.rowconfigure(0, weight=1)
frame_table.columnconfigure(0, weight=1)

# Renk tanımları
result_table.tag_configure("up", foreground="green")
result_table.tag_configure("down", foreground="red")

# Başlat
window.mainloop()
