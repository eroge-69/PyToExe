
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import ImageGrab
import threading
import requests
import json
import os
import time

CONFIG_FILE = "biomes_config.json"
running = False
sent_states = {}

def get_pixel_color(x, y):
    img = ImageGrab.grab(bbox=(x, y, x+1, y+1))
    return img.getpixel((0, 0))

def send_webhook(message, url):
    try:
        data = {"content": message}
        requests.post(url, json=data)
    except Exception as e:
        print(f"Webhook error: {e}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def start_detection(entries, webhook_entry, interval_entry):
    global running
    running = True
    config = {}
    for biome, values in entries.items():
        x = int(values["x"].get())
        y = int(values["y"].get())
        color = tuple(map(int, values["color"].get().split(",")))
        config[biome] = {"x": x, "y": y, "color": color}

    webhook = webhook_entry.get()
    interval = float(interval_entry.get())

    def loop():
        global sent_states
        sent_states = {k: False for k in config.keys()}
        while running:
            for biome, data in config.items():
                x, y = data["x"], data["y"]
                target_color = tuple(data["color"])
                pixel = get_pixel_color(x, y)
                if pixel == target_color and not sent_states[biome]:
                    send_webhook(f"🌍 Биом обнаружен: {biome}", webhook)
                    sent_states[biome] = True
                elif pixel != target_color:
                    sent_states[biome] = False
            time.sleep(interval)

    save_config(config)
    threading.Thread(target=loop, daemon=True).start()

def stop_detection():
    global running
    running = False

def build_gui():
    app = tk.Tk()
    app.title("Sol's RNG — Биом Детектор")
    app.geometry("600x700")

    config = load_config()

    entries = {}
    biome_list = [
        "Normal", "Snow", "Desert", "Crystal", "Underground", "Corruption",
        "Volcano", "Heaven", "Underworld", "Lush", "Cave", "Darkzone"
    ]

    for biome in biome_list:
        frame = tk.LabelFrame(app, text=f"Настройки: {biome}")
        frame.pack(fill="x", padx=10, pady=3)

        tk.Label(frame, text="X:").grid(row=0, column=0)
        entry_x = tk.Entry(frame, width=5)
        entry_x.grid(row=0, column=1)

        tk.Label(frame, text="Y:").grid(row=0, column=2)
        entry_y = tk.Entry(frame, width=5)
        entry_y.grid(row=0, column=3)

        tk.Label(frame, text="Цвет (R,G,B):").grid(row=0, column=4)
        entry_color = tk.Entry(frame, width=12)
        entry_color.grid(row=0, column=5)

        biome_config = config.get(biome, {})
        entry_x.insert(0, biome_config.get("x", ""))
        entry_y.insert(0, biome_config.get("y", ""))
        entry_color.insert(0, ",".join(map(str, biome_config.get("color", []))))

        entries[biome] = {"x": entry_x, "y": entry_y, "color": entry_color}

    tk.Label(app, text="🔗 Discord Webhook URL:").pack(pady=5)
    webhook_entry = tk.Entry(app, width=60)
    webhook_entry.pack()

    tk.Label(app, text="⏱️ Интервал проверки (сек):").pack()
    interval_entry = tk.Entry(app)
    interval_entry.insert(0, "1")
    interval_entry.pack()

    btn_frame = tk.Frame(app)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="▶️ Запустить", command=lambda: start_detection(entries, webhook_entry, interval_entry)).pack(side="left", padx=10)
    tk.Button(btn_frame, text="⛔ Остановить", command=stop_detection).pack(side="left", padx=10)

    app.mainloop()

if __name__ == "__main__":
    build_gui()
