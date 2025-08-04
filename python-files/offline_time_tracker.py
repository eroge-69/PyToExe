# offline_time_tracker.py

import time
import json
import os
import platform
from datetime import datetime

if platform.system() == "Windows":
    import ctypes
    import win32gui
    import win32process
    import psutil
    from pynput import mouse, keyboard
elif platform.system() == "Linux":
    import subprocess
    from pynput import mouse, keyboard

TRACKING_INTERVAL = 5  # seconds
IDLE_THRESHOLD = 180  # seconds (3 minutes)

DATA_FILE = os.path.expanduser("~/.offline_time_tracker.json")

def get_active_window_title():
    if platform.system() == "Windows":
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            title = win32gui.GetWindowText(hwnd)
            return f"{process.name()} - {title}"
        except Exception:
            return "Unknown"
    elif platform.system() == "Linux":
        try:
            win_id = subprocess.check_output(["xdotool", "getactivewindow"]).decode().strip()
            win_name = subprocess.check_output(["xdotool", "getwindowname", win_id]).decode().strip()
            return win_name
        except Exception:
            return "Unknown"
    return "Unknown"

last_input_time = time.time()

def on_input(_):
    global last_input_time
    last_input_time = time.time()

def is_user_active():
    return time.time() - last_input_time < IDLE_THRESHOLD

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def track():
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    if today not in data:
        data[today] = {}

    while True:
        if is_user_active():
            title = get_active_window_title()
            if title not in data[today]:
                data[today][title] = 0
            data[today][title] += TRACKING_INTERVAL
            save_data(data)
        time.sleep(TRACKING_INTERVAL)

if __name__ == '__main__':
    print("Starting offline time tracker...")

    # Start input listeners
    keyboard_listener = keyboard.Listener(on_press=on_input, on_release=on_input)
    mouse_listener = mouse.Listener(on_click=on_input, on_move=on_input, on_scroll=on_input)
    keyboard_listener.start()
    mouse_listener.start()

    try:
        track()
    except KeyboardInterrupt:
        print("Exiting tracker...")
