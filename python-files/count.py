import tkinter as tk
from tkinter import messagebox
import requests
import time
import threading

# Ana uygulama penceresini oluşturma
app = tk.Tk()
app.title("Web Sayfası Ziyaret Aracı")
app.geometry("450x250") # Pencere boyutunu ayarla

# Arayüz elemanları için bir çerçeve oluşturma
frame = tk.Frame(app, padx=10, pady=10)
frame.pack(expand=True, fill=tk.BOTH)

# URL giriş alanı
tk.Label(frame, text="Blog Sayfası Linki (URL):").pack(pady=5)
url_entry = tk.Entry(frame, width=50)
url_entry.pack(pady=5)

# Tekrar sayısı giriş alanı
tk.Label(frame, text="Ziyaret Sayısı:").pack(pady=5)
count_entry = tk.Entry(frame, width=20)
count_entry.pack(pady=5)

# Durum etiketi
status_label = tk.Label(frame, text="Durum: Beklemede", fg="blue")
status_label.pack(pady=10)

# Ziyaret işlemini gerçekleştiren fonksiyon
def start_visiting():
    url = url_entry.get()
    try:
        count = int(count_entry.get())
    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli bir sayı girin.")
        return

    if not url.startswith('http://' ) and not url.startswith('https://' ):
        messagebox.showerror("Hata", "Lütfen 'http://' veya 'https://' ile başlayan geçerli bir URL girin." )
        return

    start_button.config(state=tk.DISABLED)
    status_label.config(text=f"İşlem başladı... 0/{count}", fg="orange")
    threading.Thread(target=visit_loop, args=(url, count), daemon=True).start()

def visit_loop(url, count):
    for i in range(count):
        try:
            requests.get(url, timeout=10)
            status_label.config(text=f"İşlem devam ediyor... {i+1}/{count}", fg="orange")
            time.sleep(0.5)
        except requests.RequestException as e:
            status_label.config(text=f"Hata oluştu: {i+1}. denemede işlem durdu.", fg="red")
            start_button.config(state=tk.NORMAL)
            return

    status_label.config(text=f"İşlem tamamlandı! {count} ziyaret gerçekleştirildi.", fg="green")
    start_button.config(state=tk.NORMAL)

# Başlat butonu
start_button = tk.Button(frame, text="Ziyaretleri Başlat", command=start_visiting)
start_button.pack(pady=20)

# Uygulamayı başlat
app.mainloop()
