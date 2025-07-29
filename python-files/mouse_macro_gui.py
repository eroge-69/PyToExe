
import keyboard
import time
import json
import threading
from pynput.mouse import Button, Controller
import tkinter as tk
from tkinter import ttk

mouse = Controller()
running = True
paused = False

config = {
    "mode": "none",
    "delay": 20,
    "gforce": 2,
    "gforce_time": 700,
    "scope": False,
    "dual": False,
    "burst": False
}

def update_gui():
    mode_label.config(text=f"Mode Aktif: {config['mode'].upper()}")
    delay_label.config(text=f"Delay: {config['delay']} ms")
    gforce_label.config(text=f"GForce: {config['gforce']}")
    gforce_time_label.config(text=f"GForce Time: {config['gforce_time']} ms")
    scope_label.config(text=f"Scope: {'ON' if config['scope'] else 'OFF'}")
    dual_label.config(text=f"Dual: {'ON' if config['dual'] else 'OFF'}")
    burst_label.config(text=f"Burst Mode: {'ON' if config['burst'] else 'OFF'}")
    pause_label.config(text=f"Status: {'PAUSED' if paused else 'RUNNING'}")
    root.after(500, update_gui)

def recoil_loop():
    global running, paused
    while running:
        if not paused and config["mode"] == "recoil":
            mouse.press(Button.left)
            start = time.time()
            while (time.time() - start) * 1000 < config["gforce_time"]:
                mouse.move(0, config["gforce"])
                time.sleep(config["delay"] / 1000)
            mouse.release(Button.left)
        time.sleep(0.01)

threading.Thread(target=recoil_loop, daemon=True).start()

def save_config():
    with open("weapon_config.json", "w") as f:
        json.dump(config, f)

def load_config():
    global config
    try:
        with open("weapon_config.json", "r") as f:
            config.update(json.load(f))
    except:
        pass

def toggle_pause():
    global paused
    paused = not paused

def toggle(key): config.update({key: not config[key]})
def update(key, val): config[key] = max(1, config[key] + val)
def update_gforce_time(val): config["gforce_time"] = max(0, config["gforce_time"] + val)

keyboard.add_hotkey("f1+f2", lambda: config.update({"mode": "sg"}))
keyboard.add_hotkey("f1+f3", lambda: config.update({"mode": "recoil"}))
keyboard.add_hotkey("f1+f4", lambda: config.update({"mode": "awp"}))
keyboard.add_hotkey("f1+f11", lambda: config.update({"mode": "none"}))
keyboard.add_hotkey("f1+f12", lambda: exit())

keyboard.add_hotkey("f1+up", lambda: update("delay", 1))
keyboard.add_hotkey("f1+down", lambda: update("delay", -1))
keyboard.add_hotkey("f1+right", lambda: update("gforce", 1))
keyboard.add_hotkey("f1+left", lambda: update("gforce", -1))
keyboard.add_hotkey("f1++", lambda: update_gforce_time(50))
keyboard.add_hotkey("f1+-", lambda: update_gforce_time(-50))

keyboard.add_hotkey("v", lambda: toggle("scope"))
keyboard.add_hotkey("n", lambda: toggle("dual"))
keyboard.add_hotkey("h", toggle_pause)

keyboard.add_hotkey("f1+f9", save_config)
keyboard.add_hotkey("f1+f8", load_config)
keyboard.add_hotkey("f1+f10", lambda: toggle("burst"))

root = tk.Tk()
root.title("Mouse Macro Controller")
root.geometry("300x280")
root.resizable(False, False)

style = ttk.Style(root)
style.configure("TLabel", font=("Segoe UI", 10))

mode_label = ttk.Label(root, text="Mode Aktif: None")
delay_label = ttk.Label(root, text="Delay: 20 ms")
gforce_label = ttk.Label(root, text="GForce: 2")
gforce_time_label = ttk.Label(root, text="GForce Time: 700 ms")
scope_label = ttk.Label(root, text="Scope: OFF")
dual_label = ttk.Label(root, text="Dual: OFF")
burst_label = ttk.Label(root, text="Burst Mode: OFF")
pause_label = ttk.Label(root, text="Status: RUNNING")

for widget in [mode_label, delay_label, gforce_label, gforce_time_label,
               scope_label, dual_label, burst_label, pause_label]:
    widget.pack(pady=5)

update_gui()
root.mainloop()
