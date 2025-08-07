import tkinter as tk
from tkinter import messagebox
import pyautogui
import threading
import datetime
import time

claim_start_time = None
claim_countdown_running = False
claim_countdown_thread = None

def wait_until(target_time):
    while True:
        now = datetime.datetime.now()
        diff = (target_time - now).total_seconds()
        if diff <= 0:
            break
        time.sleep(min(diff, 0.001))  # 1 ms aralıklarla kontrol

def start_timed_click():
    try:
        hour = int(hour_entry.get())
        minute = int(minute_entry.get())
        second = int(second_entry.get())
        millisecond = int(ms_entry.get())
        x = int(x_entry.get())
        y = int(y_entry.get())

        target_time = datetime.datetime.now().replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=millisecond * 1000
        )

        # Eğer hedef zaman geçmişse bir sonraki güne kaydır
        if target_time < datetime.datetime.now():
            target_time += datetime.timedelta(days=1)

        def wait_and_click():
            wait_until(target_time)
            pyautogui.click(x, y)
            print(f"Tıklama yapıldı! Zaman: {datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

        threading.Thread(target=wait_and_click, daemon=True).start()
        messagebox.showinfo("Zamanlayıcı Başladı", f"Tıklama {target_time.strftime('%H:%M:%S.%f')[:-3]} saatinde yapılacak.")

    except ValueError:
        messagebox.showerror("Hata", "Lütfen geçerli sayı değerleri girin.")

# --- CLAIM PATLAMA İÇİN --- 

def claim_patladı():
    global claim_start_time, claim_countdown_running, claim_countdown_thread
    claim_start_time = datetime.datetime.now()
    claim_countdown_running = True

    def claim_countdown():
        global claim_countdown_running
        while claim_countdown_running:
            elapsed = (datetime.datetime.now() - claim_start_time).total_seconds()
            remaining = 600 - elapsed  # 10 dakika = 600 sn
            if remaining <= 0:
                claim_countdown_label.config(text="00:00.000 - Süre Doldu!")
                claim_countdown_running = False
                yeni_claim_zamani = claim_start_time + datetime.timedelta(seconds=600)
                messagebox.showinfo("Yeni Claim Zamanı",
                                    f"Yeni claim zamanı: {yeni_claim_zamani.strftime('%H:%M:%S.%f')[:-3]}")
                break
            else:
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                millis = int((remaining - int(remaining)) * 1000)
                claim_countdown_label.config(text=f"{mins:02}:{secs:02}.{millis:03}")
            time.sleep(0.05)

    claim_countdown_thread = threading.Thread(target=claim_countdown, daemon=True)
    claim_countdown_thread.start()

def stop_claim_countdown():
    global claim_countdown_running
    claim_countdown_running = False

def reset_claim_countdown():
    global claim_countdown_running, claim_start_time
    claim_countdown_running = False
    claim_start_time = None
    claim_countdown_label.config(text="Claim Geri Sayımı: Hazır")

def get_position():
    messagebox.showinfo("İpucu", "5 saniye içinde imleci tıklanacak noktaya götürün.")
    time.sleep(5)
    x, y = pyautogui.position()
    x_entry.delete(0, tk.END)
    y_entry.delete(0, tk.END)
    x_entry.insert(0, str(x))
    y_entry.insert(0, str(y))
    messagebox.showinfo("Alındı", f"X: {x}, Y: {y}")

# --- Arayüz ---
root = tk.Tk()
root.title("Saatte Tıklayan Bot + Claim Geri Sayım")

# Zaman girişleri
tk.Label(root, text="Saat (0-23):").grid(row=0, column=0)
hour_entry = tk.Entry(root)
hour_entry.grid(row=0, column=1)

tk.Label(root, text="Dakika (0-59):").grid(row=1, column=0)
minute_entry = tk.Entry(root)
minute_entry.grid(row=1, column=1)

tk.Label(root, text="Saniye (0-59):").grid(row=2, column=0)
second_entry = tk.Entry(root)
second_entry.grid(row=2, column=1)

tk.Label(root, text="Salise (0-999):").grid(row=3, column=0)
ms_entry = tk.Entry(root)
ms_entry.grid(row=3, column=1)

# Koordinat girişleri
tk.Label(root, text="X Koordinat:").grid(row=4, column=0)
x_entry = tk.Entry(root)
x_entry.grid(row=4, column=1)

tk.Label(root, text="Y Koordinat:").grid(row=5, column=0)
y_entry = tk.Entry(root)
y_entry.grid(row=5, column=1)

# Butonlar
tk.Button(root, text="Konumu Al", command=get_position).grid(row=6, column=0, columnspan=2, pady=5)
tk.Button(root, text="Zamanlı Tıklama Başlat", command=start_timed_click).grid(row=7, column=0, columnspan=2, pady=5)

# Claim patlama geri sayımı butonları
tk.Button(root, text="Claim Patladı!", command=claim_patladı).grid(row=8, column=0, pady=10)
tk.Button(root, text="Claim Geri Sayım Durdur", command=stop_claim_countdown).grid(row=8, column=1, pady=10)
tk.Button(root, text="Claim Geri Sayım Sıfırla", command=reset_claim_countdown).grid(row=9, column=0, columnspan=2, pady=5)

# Claim geri sayım etiketi
claim_countdown_label = tk.Label(root, text="Claim Geri Sayımı: Hazır", font=("Arial", 14), fg="blue")
claim_countdown_label.grid(row=10, column=0, columnspan=2, pady=10)

root.mainloop()
