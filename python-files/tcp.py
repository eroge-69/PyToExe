import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import cv2
import numpy as np
import pyautogui
import pydirectinput
import random

running = False
default_click_offset = 38
cooldown_targets = []  # [(x, y, time)]

# ---------------- EMBERIBB SHIFT+JOBB KATTINTÁS ----------------
def shift_right_click(x, y, hold_time=0.5):
    try:
        pydirectinput.keyDown('shift')
        pydirectinput.moveTo(x, y)
        pydirectinput.mouseDown(button='right')
        time.sleep(hold_time)
        pydirectinput.mouseUp(button='right')
        pydirectinput.keyUp('shift')
        # extra szünet, hogy biztosan felengedje a kattintást
        time.sleep(random.uniform(0.15, 0.3))
    except Exception as e:
        log_message(f"Hiba a kattintásnál: {e}")

# ---------------- COOLDOWN KEZELÉS ----------------
def is_recent_target(x, y, cooldown_time, radius):
    global cooldown_targets
    current_time = time.time()
    new_list = []
    for tx, ty, ttime in cooldown_targets:
        if current_time - ttime < cooldown_time:
            new_list.append((tx, ty, ttime))
            dist = ((x - tx)**2 + (y - ty)**2)**0.5
            if dist < radius:
                return True
    cooldown_targets[:] = new_list
    return False

def add_target_to_cooldown(x, y):
    global cooldown_targets
    cooldown_targets.append((x, y, time.time()))

# ---------------- TARGET KERESÉS ----------------
def find_targets(img, gray_template, threshold, max_targets):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    res = cv2.matchTemplate(gray_img, gray_template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)

    screen_h, screen_w = img.shape[:2]
    cx, cy = screen_w // 2, screen_h // 2

    targets = []
    for pt in zip(*loc[::-1]):
        base_x = pt[0] + gray_template.shape[1] // 2
        base_y = pt[1] + gray_template.shape[0] // 2
        targets.append((base_x, base_y))

    targets.sort(key=lambda t: ((t[0]-cx)**2 + (t[1]-cy)**2)**0.5)
    return targets[:max_targets]

# ---------------- KATTINTÁSOK ----------------
def click_targets(targets, click_offset, num_clicks, x_offset, y_offset, cooldown_time, radius):
    for base_x, base_y in targets:
        # ha túl közel van egy régi targethez, kihagyjuk
        if is_recent_target(base_x, base_y, cooldown_time, radius):
            continue  

        click_offsets_list = [(0, click_offset)]
        for i in range(1, num_clicks):
            dx = x_offset * ((-1)**i)
            dy = click_offset + y_offset
            click_offsets_list.append((dx, dy))

        # Szekvenciális kattintások
        for dx, dy in click_offsets_list:
            click_x = base_x + dx + random.randint(-2, 2)
            click_y = base_y + dy + random.randint(-2, 2)
            
            shift_right_click(click_x, click_y, hold_time=random.uniform(0.4, 0.6))
            
            # extra szünet, mielőtt a következő target jön
            time.sleep(random.uniform(0.3, 0.5))
            
            log_message(f"Kattintás: ({click_x}, {click_y})")

        add_target_to_cooldown(base_x, base_y)

# ---------------- BOT FUNKCIÓ ----------------
def bot_function(template_path, interval, click_offset, num_clicks, x_offset, y_offset, num_targets, cooldown_time, radius):
    global running
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        messagebox.showerror("Hiba", "A minta kép nem található!")
        running = False
        return

    gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    while running:
        screenshot = pyautogui.screenshot()
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        targets = find_targets(img, gray_template, threshold=0.8, max_targets=num_targets)
        if targets:
            click_targets(targets, click_offset, num_clicks, x_offset, y_offset, cooldown_time, radius)
        else:
            log_message("Nincs találat.")

        time.sleep(interval)

    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

# ---------------- GUI FUNKCIÓK ----------------
def select_template():
    path = filedialog.askopenfilename(filetypes=[("PNG files","*.png"),("All files","*.*")])
    if path:
        template_entry.delete(0, tk.END)
        template_entry.insert(0, path)

def start_bot():
    global running
    if running:
        messagebox.showwarning("Figyelmeztetés", "A bot már fut!")
        return

    template_path = template_entry.get()
    if not template_path:
        messagebox.showerror("Hiba", "Válassz mintaképet!")
        return

    try:
        interval = float(interval_entry.get())
        click_offset = int(offset_entry.get())
        num_clicks = int(num_clicks_entry.get())
        x_offset = int(x_offset_entry.get())
        y_offset = int(y_offset_entry.get())
        num_targets = int(num_targets_entry.get())
        cooldown_time = float(cooldown_entry.get())
        radius = int(radius_entry.get())
    except ValueError:
        messagebox.showerror("Hiba", "Minden mezőbe számot írj!")
        return

    running = True
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

    threading.Thread(
        target=bot_function,
        args=(template_path, interval, click_offset, num_clicks, x_offset, y_offset, num_targets, cooldown_time, radius),
        daemon=True
    ).start()

def stop_bot():
    global running
    running = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    log_message("Bot leállítva.")

def log_message(msg):
    log_box.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {msg}\n")
    log_box.yview(tk.END)

# ---------------- GUI ----------------
root = tk.Tk()
root.title("Kép alapú bot (Cooldown + Radius + Szekvenciális)")
root.geometry("600x750")

tk.Label(root, text="Minta kép:").pack(pady=(10,0))
template_entry = tk.Entry(root, width=40)
template_entry.pack()
tk.Button(root, text="Tallózás", command=select_template).pack(pady=5)

fields = [
    ("Ismétlés időköze (mp):", "2"),
    ("Alap kattintás offset (px):", str(default_click_offset)),
    ("Kattintások száma:", "3"),
    ("Vízszintes eltolás (px):", "20"),
    ("Függőleges eltolás (px):", "10"),
    ("Targetek száma:", "2"),
    ("Cooldown idő (mp):", "15"),
    ("Target radius (px):", "50"),
]

entries = []
for label, default in fields:
    tk.Label(root, text=label).pack(pady=(10,0))
    entry = tk.Entry(root)
    entry.insert(0, default)
    entry.pack()
    entries.append(entry)

interval_entry, offset_entry, num_clicks_entry, x_offset_entry, y_offset_entry, num_targets_entry, cooldown_entry, radius_entry = entries

start_button = tk.Button(root, text="Indítás", command=start_bot)
start_button.pack(pady=5)

stop_button = tk.Button(root, text="Leállítás", command=stop_bot, state=tk.DISABLED)
stop_button.pack(pady=5)

tk.Label(root, text="Log:").pack(pady=(10,0))
log_box = tk.Text(root, height=10, width=70)
log_box.pack(pady=5)

def on_closing():
    stop_bot()
    root.destroy()

root.bind('<Escape>', lambda e: stop_bot())
root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
