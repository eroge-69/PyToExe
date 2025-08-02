
import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui

shaking_event = threading.Event()

def start_shaking(interval, x_offset, y_offset):
    def shake():
        while shaking_event.is_set():
            x, y = pyautogui.position()
            pyautogui.moveTo(x + x_offset, y + y_offset)
            time.sleep(0.01)
            pyautogui.moveTo(x - x_offset, y - y_offset)
            time.sleep(interval / 1000.0)
    threading.Thread(target=shake, daemon=True).start()

def create_gui():
    def toggle_shake():
        if shaking_event.is_set():
            shaking_event.clear()
            start_button.config(text="Start")
        else:
            shaking_event.set()
            interval = int(interval_var.get())
            x_offset = int(x_var.get())
            y_offset = int(y_var.get())
            start_shaking(interval, x_offset, y_offset)
            start_button.config(text="Stop")

    root = tk.Tk()
    root.title("Shaker")
    root.geometry("180x160")
    root.resizable(False, False)

    ttk.Label(root, text="Shake Interval").pack(pady=5)
    interval_var = tk.StringVar(value="20")
    ttk.Spinbox(root, from_=1, to=1000, textvariable=interval_var).pack()

    ttk.Label(root, text="X").pack(pady=5)
    x_var = tk.StringVar(value="10")
    ttk.Spinbox(root, from_=0, to=100, textvariable=x_var).pack()

    ttk.Label(root, text="Y").pack(pady=5)
    y_var = tk.StringVar(value="10")
    ttk.Spinbox(root, from_=0, to=100, textvariable=y_var).pack()

    global start_button
    start_button = ttk.Button(root, text="Start", command=toggle_shake)
    start_button.pack(pady=10)

    root.mainloop()

create_gui()
