# offline_time_tracker_windows_gui.py

import threading
import time
import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import ctypes
import win32gui
import win32process
import psutil
from pynput import mouse, keyboard

TRACKING_INTERVAL = 5  # seconds
IDLE_THRESHOLD = 180  # seconds
DATA_FILE = os.path.expanduser("~/.offline_time_tracker_windows.json")

last_input_time = time.time()
tracking = False
data_lock = threading.Lock()
data = {}

def get_active_window_title():
    hwnd = win32gui.GetForegroundWindow()
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    try:
        process = psutil.Process(pid)
        title = win32gui.GetWindowText(hwnd)
        return f"{process.name()} - {title}"
    except Exception:
        return "Unknown"

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

def save_data():
    global data
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def export_to_csv():
    global data
    if not data:
        messagebox.showinfo("Export CSV", "No data to export.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if not file_path:
        return
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("date,window_title,total_seconds\n")
        for date, entries in data.items():
            for title, seconds in entries.items():
                line = f'"{date}","{title.replace("\"","\"\"")}",{seconds}\n'
                f.write(line)
    messagebox.showinfo("Export CSV", f"Exported data to {file_path}")

def track_loop():
    global tracking, data
    while tracking:
        if is_user_active():
            title = get_active_window_title()
            today = datetime.now().strftime("%Y-%m-%d")
            with data_lock:
                if today not in data:
                    data[today] = {}
                if title not in data[today]:
                    data[today][title] = 0
                data[today][title] += TRACKING_INTERVAL
            save_data()
        time.sleep(TRACKING_INTERVAL)

def update_status():
    if tracking:
        today = datetime.now().strftime("%Y-%m-%d")
        with data_lock:
            today_data = data.get(today, {})
            total_seconds = sum(today_data.values())
            current_title = get_active_window_title() if is_user_active() else "Idle"
        time_str = time.strftime('%H:%M:%S', time.gmtime(total_seconds))
        status_label.config(text=f"Today tracked time: {time_str}\nCurrent window: {current_title}")
    else:
        status_label.config(text="Tracking stopped.")
    root.after(1000, update_status)

def toggle_tracking():
    global tracking, track_thread, data
    if not tracking:
        data = load_data()
        tracking = True
        track_thread = threading.Thread(target=track_loop, daemon=True)
        track_thread.start()
        toggle_btn.config(text="Stop Tracking")
    else:
        tracking = False
        toggle_btn.config(text="Start Tracking")

root = tk.Tk()
root.title("Offline Time Tracker (Windows)")

toggle_btn = tk.Button(root, text="Start Tracking", width=20, command=toggle_tracking)
toggle_btn.pack(pady=10)

status_label = tk.Label(root, text="Tracking stopped.", justify=tk.LEFT)
status_label.pack(pady=10)

export_btn = tk.Button(root, text="Export to CSV", width=20, command=export_to_csv)
export_btn.pack(pady=10)

update_status()
root.mainloop()
