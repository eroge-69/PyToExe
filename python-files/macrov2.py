import threading
import time
import keyboard
from pynput.mouse import Controller, Button
import tkinter as tk
from tkinter import simpledialog
import random
import queue

# -------------------- Kullanıcıdan Hedef CPS --------------------
root_input = tk.Tk()
root_input.withdraw()
try:
    TARGET_CPS = float(simpledialog.askstring("CPS Ayarı", "Auto Clicker CPS değerini girin:", initialvalue="14"))
    if TARGET_CPS <= 0:
        TARGET_CPS = 14
except:
    TARGET_CPS = 14
root_input.destroy()

MIN_CPS = max(1, TARGET_CPS - 3)
MAX_CPS = TARGET_CPS + 3
MOVE_SPEED = 1.0
auto_clicker_active = False
last_toggle_time = 0
m = Controller()

# -------------------- GUI Overlay --------------------
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.geometry("+10+10")
label = tk.Label(root, text="", font=("Arial", 16), fg="white", bg="black")
label.pack()
root.update()

gui_queue = queue.Queue()

def process_gui_queue():
    try:
        while True:
            func, args = gui_queue.get_nowait()
            func(*args)
    except queue.Empty:
        pass
    root.after(50, process_gui_queue)

def fade_out_label(duration=500, steps=10):
    interval = duration // steps
    def step(i):
        if i >= steps:
            label.config(text="")
            root.attributes("-alpha", 1)
            return
        alpha = 1 - (i+1)/steps
        root.attributes("-alpha", alpha)
        root.after(interval, lambda: step(i+1))
    step(0)

def update_overlay(text):
    label.config(text=text)
    root.attributes("-alpha", 1)
    fade_out_label()

# -------------------- Auto Clicker Fonksiyonu --------------------
def drag_click():
    active_duration = 3.0   # 3 saniye tıklama
    pause_duration = 0.5    # 0.5 saniye duraklama

    while True:
        if auto_clicker_active:
            start_time = time.time()
            # Aktif döngü
            while time.time() - start_time < active_duration and auto_clicker_active:
                cps = random.gauss(TARGET_CPS, 1.0)
                cps = max(MIN_CPS, min(MAX_CPS, cps))
                move_x = random.uniform(-MOVE_SPEED, MOVE_SPEED)
                move_y = random.uniform(-MOVE_SPEED, MOVE_SPEED)
                m.move(move_x, move_y)
                m.press(Button.left)
                m.release(Button.left)
                time.sleep(1 / cps)
            # Duraklama
            time.sleep(pause_duration)
        else:
            time.sleep(0.05)

# -------------------- Toggle --------------------
def toggle_bot():
    global auto_clicker_active, last_toggle_time
    if time.time() - last_toggle_time > 0.3:
        auto_clicker_active = not auto_clicker_active
        last_toggle_time = time.time()
        msg = "Godbridge Aktif" if auto_clicker_active else "Godbridge Kapalı"
        gui_queue.put((update_overlay, (msg,)))

# X tuşu ve kombinasyonları ile toggle
def check_toggle_key():
    while True:
        if keyboard.is_pressed('x'):
            toggle_bot()
        time.sleep(0.05)

# -------------------- Thread Başlat --------------------
threading.Thread(target=drag_click, daemon=True).start()
threading.Thread(target=check_toggle_key, daemon=True).start()
root.after(50, process_gui_queue)
root.mainloop()
