
import tkinter as tk
from tkinter import ttk
import threading
import random
import time
import keyboard
import pyautogui

running = False

def click_and_type(keys, min_interval, max_interval):
    global running
    while running:
        interval = random.uniform(min_interval, max_interval)
        if 'Mouse' in keys:
            pyautogui.click()
        for key in keys:
            if key != 'Mouse':
                keyboard.write(key)
        time.sleep(interval)

def start():
    global running
    running = True
    selected_keys = [key for key, var in key_vars.items() if var.get()]
    try:
        min_interval = float(min_interval_entry.get())
        max_interval = float(max_interval_entry.get())
    except ValueError:
        log_label.config(text="Invalid interval value")
        return
    if not selected_keys:
        log_label.config(text="Select at least one key or mouse")
        return
    threading.Thread(target=click_and_type, args=(selected_keys, min_interval, max_interval), daemon=True).start()
    log_label.config(text="Running... Press Stop to end")

def stop():
    global running
    running = False
    log_label.config(text="Stopped")

root = tk.Tk()
root.title("Auto Clicker & Typer")
root.geometry("400x500")

key_list = ['Mouse', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i',
            'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's',
            't', 'u', 'v', 'w', 'x', 'y', 'z', 'Enter', 'Space']

key_vars = {}
for key in key_list:
    var = tk.BooleanVar()
    chk = ttk.Checkbutton(root, text=key, variable=var)
    chk.pack(anchor='w')
    key_vars[key] = var

ttk.Label(root, text="Min Interval (sec):").pack()
min_interval_entry = ttk.Entry(root)
min_interval_entry.pack()
min_interval_entry.insert(0, "2")

ttk.Label(root, text="Max Interval (sec):").pack()
max_interval_entry = ttk.Entry(root)
max_interval_entry.pack()
max_interval_entry.insert(0, "5")

ttk.Button(root, text="Start", command=start).pack(pady=10)
ttk.Button(root, text="Stop", command=stop).pack(pady=5)

log_label = ttk.Label(root, text="")
log_label.pack()

root.mainloop()
