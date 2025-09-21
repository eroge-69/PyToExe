import time
import random
import threading
import tkinter as tk
from tkinter import ttk
import mouse
import pyautogui
import keyboard

running = True

# Default ranges
left_min_cps = 5
left_max_cps = 15
right_min_cps = 5
right_max_cps = 15

def left_clicker():
    global left_min_cps, left_max_cps
    while running:
        if mouse.is_pressed("left"):
            cps = random.randint(left_min_cps, left_max_cps)
            delay = 1.0 / cps
            pyautogui.click(button="left")
            time.sleep(delay)
        else:
            time.sleep(0.01)

def right_clicker():
    global right_min_cps, right_max_cps
    while running:
        if mouse.is_pressed("right"):
            cps = random.randint(right_min_cps, right_max_cps)
            delay = 1.0 / cps
            pyautogui.click(button="right")
            time.sleep(delay)
        else:
            time.sleep(0.01)

def start_threads():
    threading.Thread(target=left_clicker, daemon=True).start()
    threading.Thread(target=right_clicker, daemon=True).start()

def update_left_min(val):
    global left_min_cps
    left_min_cps = int(float(val))
    if left_min_cps > left_max_cps:
        left_min_cps = left_max_cps
        min_left_slider.set(left_min_cps)

def update_left_max(val):
    global left_max_cps
    left_max_cps = int(float(val))
    if left_max_cps < left_min_cps:
        left_max_cps = left_min_cps
        max_left_slider.set(left_max_cps)

def update_right_min(val):
    global right_min_cps
    right_min_cps = int(float(val))
    if right_min_cps > right_max_cps:
        right_min_cps = right_max_cps
        min_right_slider.set(right_min_cps)

def update_right_max(val):
    global right_max_cps
    right_max_cps = int(float(val))
    if right_max_cps < right_min_cps:
        right_max_cps = right_min_cps
        max_right_slider.set(right_max_cps)

# GUI (main settings window)
root = tk.Tk()
root.title("👻 GhostzClickz Settings")
root.geometry("350x300")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use("clam")

title_label = ttk.Label(root, text="👻 GhostzClickz", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=10)

frame = ttk.LabelFrame(root, text=" Left Click CPS ", padding=10)
frame.pack(fill="x", padx=10, pady=5)

min_left_slider = ttk.Scale(frame, from_=1, to=20, orient="horizontal", command=update_left_min)
min_left_slider.set(left_min_cps)
min_left_slider.pack(fill="x", pady=5)
ttk.Label(frame, text="Minimum CPS").pack()

max_left_slider = ttk.Scale(frame, from_=1, to=20, orient="horizontal", command=update_left_max)
max_left_slider.set(left_max_cps)
max_left_slider.pack(fill="x", pady=5)
ttk.Label(frame, text="Maximum CPS").pack()

frame2 = ttk.LabelFrame(root, text=" Right Click CPS ", padding=10)
frame2.pack(fill="x", padx=10, pady=5)

min_right_slider = ttk.Scale(frame2, from_=1, to=20, orient="horizontal", command=update_right_min)
min_right_slider.set(right_min_cps)
min_right_slider.pack(fill="x", pady=5)
ttk.Label(frame2, text="Minimum CPS").pack()

max_right_slider = ttk.Scale(frame2, from_=1, to=20, orient="horizontal", command=update_right_max)
max_right_slider.set(right_max_cps)
max_right_slider.pack(fill="x", pady=5)
ttk.Label(frame2, text="Maximum CPS").pack()

info_label = ttk.Label(root, text="Hold LMB or RMB to auto-click.\nPress END to quit.", font=("Segoe UI", 10))
info_label.pack(pady=10)

# Floating overlay window (topmost always)
overlay = tk.Toplevel(root)
overlay.overrideredirect(True)  # remove window borders
overlay.attributes("-topmost", True)
overlay.attributes("-alpha", 0.8)  # transparent background

overlay_label = tk.Label(
    overlay,
    text="👻 GhostzClickz",
    font=("Segoe UI", 12, "bold"),
    fg="white",
    bg="black"
)
overlay_label.pack()

# place in top-left
overlay.geometry("+10+10")

# Start threads
start_threads()

def quit_app():
    global running
    running = False
    root.destroy()
    overlay.destroy()

root.protocol("WM_DELETE_WINDOW", quit_app)

# Keyboard stop
def check_quit():
    global running
    while running:
        if keyboard.is_pressed("end"):
            quit_app()
        time.sleep(0.1)

threading.Thread(target=check_quit, daemon=True).start()

root.mainloop()
