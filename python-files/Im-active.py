import tkinter as tk
from tkinter import ttk
import threading
import pyautogui
import time
import random
import string
import ttkbootstrap as tb

# ------------- Setup -------------
running = False
activity_levels = {
    "Low": (40, 50),
    "Medium": (60, 70),
    "High": (70, 80),
    "Ultra High": (80, 100)
}

# ------------- Actions -------------

def move_mouse():
    x = random.randint(100, 1000)
    y = random.randint(100, 600)
    pyautogui.moveTo(x, y, duration=0.5)

def scroll():
    amount = random.randint(-10, 10)
    pyautogui.scroll(amount)

def switch_window():
    count = random.randint(1, 4)
    pyautogui.keyDown('alt')
    for _ in range(count):
        pyautogui.press('tab')
        time.sleep(0.1)
    pyautogui.keyUp('alt')

def mouse_click():
    x = random.randint(100, 1000)
    y = random.randint(100, 600)
    pyautogui.click(x, y)

def type_random_letter():
    char = random.choice(string.ascii_lowercase)
    pyautogui.write(char)

# ------------- Main Loop -------------

def run_actions():
    global running
    while running:
        min_chance, max_chance = activity_levels[level_var.get()]
        mouse_chance = random.randint(0, 100)

        if mouse_var.get() and mouse_chance <= random.randint(min_chance, max_chance):
            move_mouse()
            status_label.config(text="Performed: move_mouse")

        if click_var.get() and random.random() < 0.2:
            mouse_click()
            status_label.config(text="Performed: mouse_click")

        if scroll_var.get() and random.random() < 0.4:
            scroll()
            status_label.config(text="Performed: scroll")

        if tab_var.get() and random.random() < 0.3:
            switch_window()
            status_label.config(text="Performed: switch_window")

        if keyboard_var.get() and random.random() < 0.2:
            type_random_letter()
            status_label.config(text="Performed: type_random_letter")

        time.sleep(random.uniform(2, 5))

# ------------- Control -------------

def start_activity():
    global running
    if not running:
        running = True
        t = threading.Thread(target=run_actions)
        t.daemon = True
        t.start()
        status_label.config(text="Running...")

def stop_activity():
    global running
    running = False
    status_label.config(text="Stopped")

# ------------- UI Setup -------------

app = tb.Window(themename="darkly")
app.title("I'm Active")
app.geometry("420x500")
app.resizable(False, False)

tb.Label(app, text="I'm Active - Basic Mode", font=("Segoe UI", 16, "bold")).pack(pady=15)

# ---- Toggles ----
mouse_var = tk.BooleanVar(value=True)
scroll_var = tk.BooleanVar(value=True)
click_var = tk.BooleanVar()
keyboard_var = tk.BooleanVar()
tab_var = tk.BooleanVar(value=True)

frame = ttk.Frame(app)
frame.pack(pady=5, padx=30, fill="x")

ttk.Checkbutton(frame, text="Mouse Movement", variable=mouse_var).pack(anchor="w", pady=2)
ttk.Checkbutton(frame, text="Mouse Scrolling", variable=scroll_var).pack(anchor="w", pady=2)
ttk.Checkbutton(frame, text="Mouse Click", variable=click_var).pack(anchor="w", pady=2)
ttk.Checkbutton(frame, text="Keyboard Activity", variable=keyboard_var).pack(anchor="w", pady=2)
ttk.Checkbutton(frame, text="App Switching", variable=tab_var).pack(anchor="w", pady=2)

# ---- Preset Levels ----
ttk.Label(app, text="Preset Activity Level", font=("Segoe UI", 11, "bold")).pack(pady=10)

level_var = tk.StringVar(value="Medium")
for level in activity_levels:
    ttk.Radiobutton(app, text=f"{level} ({activity_levels[level][0]}-{activity_levels[level][1]}%)",
                    variable=level_var, value=level).pack(anchor="w", padx=40, pady=2)

# ---- Buttons ----
btn_frame = ttk.Frame(app)
btn_frame.pack(pady=20)

ttk.Button(btn_frame, text="▶ Start", width=15, bootstyle="success", command=start_activity).pack(side="left", padx=10)
ttk.Button(btn_frame, text="⏹ Stop", width=15, bootstyle="danger", command=stop_activity).pack(side="left")

# ---- Status ----
status_label = ttk.Label(app, text="Idle", bootstyle="info")
status_label.pack(pady=10)

app.iconbitmap("Logo.ico")

app.mainloop()
