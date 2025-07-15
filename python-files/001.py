import pytesseract
import time
import tkinter as tk
from PIL import ImageGrab
from playsound import playsound
import requests
import datetime
import threading
import os
import sys

# ------------ Sozlamalar ------------ #

# Tesseract OCR yo‘lini aniqlash (agar .exe ichida bo'lsa, shunchaki 'tesseract' deb yozing)
pytesseract.pytesseract.tesseract_cmd = 'tesseract'

# Telegram ma’lumotlaringiz
TELEGRAM_TOKEN = '8143395237:AAFZ5fMyJ_TWQ12-ODhpaRZKuQXU2dSq5yA'   # <-- bu yerga tokenni kiriting
CHAT_ID = '7203340883'        # <-- bu yerga chat_id ni kiriting

# Musiqa fayli
AUDIO_FILE = "alert_sound.mp3"

# ------------ Telegram funksiyasi ------------ #
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram xato:", e)

# ------------ Popup ko‘rsatish ------------ #
def show_popup(msg):
    def run():
        popup = tk.Tk()
        popup.title("SIGNAL")
        label = tk.Label(popup, text=f"So‘z topildi: {msg}", font=("Arial", 20))
        label.pack(padx=20, pady=20)
        popup.after(3000, popup.destroy)
        popup.mainloop()
    threading.Thread(target=run).start()

# ------------ Asosiy funksiya ------------ #
def check_screen():
    while True:
        screenshot = ImageGrab.grab()
        text = pytesseract.image_to_string(screenshot).lower()

        if "long" in text or "short" in text:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            found = "long" if "long" in text else "short"
            print(f"[{now}] Topildi: {found.upper()}")

            # Musiqa chalish
            if os.path.exists(AUDIO_FILE):
                try:
                    playsound(AUDIO_FILE)
                except Exception as e:
                    print("Audio xato:", e)

            # Telegram xabar
            send_telegram(f"📢 Signal: {found.upper()}\n🕒 {now}")

            # Pop-up
            show_popup(found.upper())

        time.sleep(2)

# ------------ Dastur ishga tushirish ------------ #
name = "test001"
if name == "test001":
    print("Nomi to'g'ri!")
    check_screen()
