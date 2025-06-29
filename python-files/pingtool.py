# Murat Özbey - Pardus Toplu Ping Aracı
# Tasarlandı: Haziran 2025
# Kullanım: Windows ve Linux (özellikle Pardus) sistemlerde
# Pardus hakkında daha fazla bilgi için: https://www.pardus.org.tr

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import subprocess
import threading
import time
import platform
import socket
import os

# --- Global Değişkenler ---
drag_start_x = 0
drag_start_y = 0
tamamlanan_sayac = 0
kutu_pingleri = {}  # IP -> (label, kutu, sayaç_label) mapping

# --- Yardımcı Fonksiyonlar ---
def get_local_ip_subnet():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "192.168.1.1"
    finally:
        s.close()
    return ".".join(ip.split(".")[:3])

def resolve_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return None

def extract_delay(output):
    for line in output.split("\n"):
        if "time=" in line:
            return line.split("time=")[1].split(" ")[0]
        elif "time<" in line:
            return "<" + line.split("time<")[1].split(" ")[0]
    return None

def ping(ip, label, kutu):
    try:
        param = "-n" if platform.system().lower() == "windows" else "-c"
        sonuc = subprocess.run(f"ping {param} 1 {ip}", capture_output=True, text=True, timeout=10, shell=True)
        gecikme = extract_delay(sonuc.stdout)
        hostname = resolve_hostname(ip)

        if hostname and hostname != ip:
            kutu.config(text=f"{ip}\n({hostname})")

        if any(x in sonuc.stdout for x in ["TTL=", "ttl=", "bytes from"]):
            delay_text = gecikme if gecikme else "?"
            label.config(text=f"OK\n{delay_text}ms", bg="#28B463", fg="white")
            kutu.config(bg="#28B463")
        else:
            label.config(text="HATA", bg="#CB4335", fg="white")
            kutu.config(bg="#CB4335")
    except:
        label.config(text="HATA", bg="#CB4335", fg="white")
        kutu.config(bg="#CB4335")

# --- Ping Başlatma Fonksiyonu ---
def baslat():
    global tamamlanan_sayac, kutu_pingleri
    tamamlanan_sayac = 0
    kutu_pingleri.clear()
    for widget in kutu_frame.winfo_children():
        widget.destroy()

    try:
        bas = int(ip_baslangic_giris.get().split(".")[-1])
        bit = int(ip_bitis_giris.get().split(".")[-1])
        temel_ip = ".".join(ip_baslangic_giris.get().split(".")[:3])
        tekrar_suresi_dk = float(tekrar_suresi_giris.get())
    except:
        return

    toplam = bit - bas + 1
    ilerleme['maximum'] = toplam
    ilerleme['value'] = 0

    pencere.update_idletasks()
    pencere_genisligi = pencere.winfo_width()
    kutu_genisligi = 130
    columns = max(3, pencere_genisligi // kutu_genisligi)

    def update_progress():
        global tamamlanan_sayac
        tamamlanan_sayac += 1
        ilerleme['value'] = tamamlanan_sayac
        percent = int((tamamlanan_sayac / ilerleme['maximum']) * 100)
        ilerleme_label.config(text=f"%{percent}")

    def thread_ping(ip, label, kutu, sayaç_label):
        def run():
            global tamamlanan_sayac
            while True:
                ping(ip, label, kutu)
                if not auto_repeat.get():
                    pencere.after(0, update_progress)
                    sayaç_label.config(text="")
                    break
                for remaining in range(int(tekrar_suresi_dk * 60), 0, -1):
                    sayaç_label.config(text=f"{remaining}s")
                    time.sleep(1)
                    if not auto_repeat.get():
                        sayaç_label.config(text="")
                        return
                pencere.after(0, update_progress)
        threading.Thread(target=run, daemon=True).start()

    for index, i in enumerate(range(bas, bit + 1)):
        ip = f"{temel_ip}.{i}"
        kutu = tk.LabelFrame(kutu_frame, bg="#2C3E50", fg="white", text=ip, width=125, height=70)
        kutu.grid(row=index // columns, column=index % columns, padx=2, pady=2)
        kutu.pack_propagate(False)

        sonuc_label = tk.Label(kutu, text="...", bg="#2C3E50", fg="white", font=("Consolas", 12, "bold"))
        sonuc_label.pack(expand=True, fill='both')

        sayaç_label = tk.Label(kutu, text="", bg="#2C3E50", fg="white", font=("Consolas", 9))
        sayaç_label.place(relx=1.0, rely=1.0, anchor='se', x=-2, y=-2)

        kutu_pingleri[ip] = (sonuc_label, kutu, sayaç_label)

        def on_double_click(event, ip=ip):
            lbl, kutu_obj, sayaç = kutu_pingleri[ip]
            kutu_obj.config(bg="#85C1E9")
            pencere.after(300, lambda: kutu_obj.config(bg="#2C3E50"))
            threading.Thread(target=lambda: ping(ip, lbl, kutu_obj), daemon=True).start()

        kutu.bind("<Double-1>", on_double_click)
        thread_ping(ip, sonuc_label, kutu, sayaç_label)

# --- Arayüz Tanımı ---
pencere = tk.Tk()
pencere.title("Pardus Toplu Ping Aracı - Murat Özbey")
pencere.configure(bg="#1C2833")
pencere.geometry("1200x720")
pencere.minsize(900, 600)

# --- Üst Logo ve İlk IP Kutularını Yan Yana Koy ---
ust_alan = tk.Frame(pencere, bg="#1C2833")
ust_alan.pack(pady=10, fill="x")

# Logo
try:
    logo_path = os.path.join(os.path.dirname(__file__), "pardus.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path)
        img = img.resize((100, 100))
        pardus_logo = ImageTk.PhotoImage(img)
        logo_label = tk.Label(ust_alan, image=pardus_logo, bg="#1C2833")
        logo_label.image = pardus_logo  # referans tut
        logo_label.pack(side="left", padx=10)
except:
    pass

# IP giriş çerçevesi
ust_cerceve = tk.Frame(ust_alan, bg="#1C2833")
ust_cerceve.pack(side="left")

subnet = get_local_ip_subnet()

tk.Label(ust_cerceve, text="Başlangıç IP:", fg="#27AE60", bg="#1C2833").grid(row=0, column=0)
ip_baslangic_giris = tk.Entry(ust_cerceve)
ip_baslangic_giris.grid(row=0, column=1, padx=5)
ip_baslangic_giris.insert(0, f"{subnet}.1")

tk.Label(ust_cerceve, text="Bitiş IP:", fg="#27AE60", bg="#1C2833").grid(row=0, column=2)
ip_bitis_giris = tk.Entry(ust_cerceve)
ip_bitis_giris.grid(row=0, column=3, padx=5)
ip_bitis_giris.insert(0, f"{subnet}.5")

tk.Label(ust_cerceve, text="Tekrar Süresi (dk):", fg="#27AE60", bg="#1C2833").grid(row=0, column=4)
tekrar_suresi_giris = tk.Entry(ust_cerceve, width=5)
tekrar_suresi_giris.grid(row=0, column=5, padx=5)
tekrar_suresi_giris.insert(0, "1")

auto_repeat = tk.BooleanVar()
tk.Checkbutton(ust_cerceve, text="Otomatik Tekrarla", variable=auto_repeat,
               bg="#1C2833", fg="#27AE60", selectcolor="#1C2833").grid(row=0, column=6, padx=10)

tk.Button(ust_cerceve, text="Ping Başlat", command=baslat,
          bg="#27AE60", fg="#1C2833").grid(row=0, column=7, padx=10)

# --- Kutu Alanı ---
canvas_frame = tk.Frame(pencere, bg="#1C2833")
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, bg="#1C2833", highlightthickness=0)
scroll_y = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scroll_x = tk.Scrollbar(canvas_frame, orient="horizontal", command=canvas.xview)
canvas.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

canvas.pack(side="left", fill="both", expand=True)
kutu_frame = tk.Frame(canvas, bg="#1C2833")
canvas_window = canvas.create_window((0, 0), window=kutu_frame, anchor="nw")

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

kutu_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# --- İlerleme Alanı ---
ilerleme_frame = tk.Frame(pencere, bg="#1C2833")
ilerleme_frame.pack(pady=5)

ilerleme = ttk.Progressbar(ilerleme_frame, length=300, mode='determinate')
ilerleme.pack(side="left")

ilerleme_label = tk.Label(ilerleme_frame, text="%0", fg="white", bg="#1C2833")
ilerleme_label.pack(side="left", padx=10)

# --- Footer ---
footer = tk.Label(pencere,
    text="Bu ping aracı Murat Özbey tarafından geliştirilmiştir. Pardus hakkında daha fazla bilgi için: https://www.pardus.org.tr",
    fg="#27AE60", bg="#1C2833")
footer.pack(side='bottom', pady=10)

pencere.mainloop()
