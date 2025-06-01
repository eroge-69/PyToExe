import tkinter as tk
import threading
import time
import pyautogui
import pydirectinput
from pynput import keyboard
import sys
import os

pyautogui.FAILSAFE = True

# --- PyInstaller-friendly resource path ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# --- GUI Setup ---
root = tk.Tk()
root.title("FH5 Bot HUD")
root.geometry("320x140")
root.resizable(False, False)

status_var = tk.StringVar(value="Bot is OFF")
step_var = tk.StringVar(value="Next Step: None")
countdown_var = tk.StringVar(value="")

tk.Label(root, textvariable=status_var, font=("Arial", 14)).pack(pady=5)
tk.Label(root, textvariable=step_var, font=("Arial", 12)).pack()
tk.Label(root, textvariable=countdown_var, font=("Arial", 12), fg="blue").pack()

# --- Globals ---
bot_running = False
current_step_index = 0

# --- Steps (image or key, delay in seconds) ---
steps = [
    ("Creative.png", 2),
    ("event.png", 2),
    ("Blue.png", 2),
    ("Best.png", 2),
    ("superfast.png", 2),
    ("superfast2.png", 2),
    ("solo.png", 2),
    ("car.png", 30),
    ("start.png", 0),
    ("hold_w", 7),
    ("hold_space", 24),
    ("tap_enter", 10),
    ("tap_enter", 4),
    ("tap_enter", 12),
    ("tap_esc", 20)
]

# --- HUD Update ---
def update_gui(next_step, countdown=None):
    step_var.set(f"Next Step: {next_step}")
    if countdown is not None:
        for i in range(int(countdown), 0, -1):
            countdown_var.set(f"Waiting: {i}s")
            root.update()
            time.sleep(1)
    countdown_var.set("")

# --- Locate image with error handling ---
def locate_image(image_path):
    try:
        full_path = resource_path(image_path)
        location = pyautogui.locateCenterOnScreen(full_path, confidence=0.7)
        if location:
            return map(int, location)
    except Exception:
        pass
    return None

# --- Click on image or fallback ---
def click_image(image_path):
    print(f"[INFO] Looking for {image_path}...")
    timeout = 30
    start_time = time.time()

    while time.time() - start_time < timeout and bot_running:
        remaining = timeout - int(time.time() - start_time)
        countdown_var.set(f"Finding: {image_path} ({remaining}s left)")
        root.update()

        location = locate_image(image_path)
        if location:
            x, y = location
            pyautogui.moveTo(x, y)
            time.sleep(0.2)
            pydirectinput.mouseDown()
            time.sleep(0.1)
            pydirectinput.mouseUp()
            countdown_var.set("")
            print(f"[CLICKED] {image_path}")
            return True
        time.sleep(1)

    countdown_var.set("")
    root.update()
    print(f"[TIMEOUT] Could not find {image_path}. Scanning all images...")

    # Fallback: Try each image for 5s
    for idx, (step, _) in enumerate(steps):
        if step.endswith(".png"):
            print(f"[SCAN] Trying {step} for 5 seconds...")
            scan_start = time.time()
            while time.time() - scan_start < 5 and bot_running:
                countdown_var.set(f"Scanning: {step}")
                root.update()

                location = locate_image(step)
                if location:
                    x, y = location
                    pyautogui.moveTo(x, y)
                    time.sleep(0.2)
                    pydirectinput.mouseDown()
                    time.sleep(0.1)
                    pydirectinput.mouseUp()
                    print(f"[RECOVERED] Found {step}, resuming from here.")
                    global current_step_index
                    current_step_index = idx
                    countdown_var.set("")
                    return True
                time.sleep(1)

    print("[FAILED] No known images found.")
    return False

# --- Hold key ---
def hold_key(key, duration):
    print(f"[HOLD] {key} for {duration}s")
    pydirectinput.keyDown(key)
    time.sleep(duration)
    pydirectinput.keyUp(key)

# --- Tap key ---
def tap_key(key):
    print(f"[TAP] {key}")
    pydirectinput.press(key)

# --- Main bot logic ---
def bot_logic():
    global current_step_index
    while True:
        if bot_running:
            if current_step_index >= len(steps):
                print("[BOT] Sequence complete. Restarting.")
                current_step_index = 0

            step, delay = steps[current_step_index]
            update_gui(step)

            if step.endswith(".png"):
                found = click_image(step)
                if found and delay > 0:
                    update_gui(step, delay)
            elif step == "hold_w":
                hold_key("w", delay)
            elif step == "hold_space":
                hold_key("space", delay)
            elif step == "tap_enter":
                update_gui(step, delay)
                tap_key("enter")
            elif step == "tap_esc":
                update_gui(step, delay)
                tap_key("esc")

            current_step_index += 1
        else:
            time.sleep(0.2)

# --- Hotkey listener ---
def on_press(key):
    global bot_running
    if key == keyboard.Key.f8:
        bot_running = not bot_running
        status_var.set("Bot is ON" if bot_running else "Bot is OFF")
        print("[BOT] Resumed." if bot_running else "[BOT] Paused.")

listener = keyboard.Listener(on_press=on_press)
listener.daemon = True
listener.start()

# --- Run Bot ---
threading.Thread(target=bot_logic, daemon=True).start()
print("Press F8 to start/pause the bot.")
root.mainloop()
