import pyautogui
import time
import threading
from pynput import mouse
import tkinter as tk
from tkinter import messagebox
import keyboard

is_enabled = False  # Controlled by hotkey
is_pulling_mouse = False
original_mouse_position = None
hotkey = 'f8'  # Default hotkey
pixel_step = 10  # Default pixels per step

def pull_mouse_down():
    global is_pulling_mouse
    while is_pulling_mouse:
        x, y = pyautogui.position()
        pyautogui.moveTo(x, y + pixel_step)
        time.sleep(0.01)

def on_click(x, y, button, pressed):
    global is_pulling_mouse, original_mouse_position
    if not is_enabled:
        return
    if button == mouse.Button.left:
        if pressed:
            original_mouse_position = tuple(pyautogui.position())
            is_pulling_mouse = True
            threading.Thread(target=pull_mouse_down, daemon=True).start()
            status_var.set("Status: ON")
        else:
            is_pulling_mouse = False
            if original_mouse_position is not None:
                pyautogui.moveTo(*original_mouse_position)
            status_var.set("Status: ENABLED")

def toggle_enable():
    global is_enabled, is_pulling_mouse
    is_enabled = not is_enabled
    if not is_enabled:
        is_pulling_mouse = False
        status_var.set("Status: OFF")
    else:
        status_var.set("Status: ENABLED")

def set_hotkey():
    def on_key_press(e):
        global hotkey
        hotkey = e.name
        hotkey_var.set(f"Hotkey: {hotkey.upper()}")
        top.destroy()
        messagebox.showinfo("Hotkey Set", f"Hotkey set to: {hotkey.upper()}")

    top = tk.Toplevel(root)
    top.title("Set Hotkey")
    tk.Label(top, text="Press any key to set as hotkey...").pack(padx=20, pady=20)
    top.grab_set()
    top.focus_force()
    keyboard.on_press(on_key_press, suppress=True)
    top.wait_window()
    keyboard.unhook_all()

def listen_hotkey():
    while True:
        keyboard.wait(hotkey)
        toggle_enable()

def update_pixel_step():
    global pixel_step
    try:
        pixel_step = int(pixel_step_var.get())
    except ValueError:
        pixel_step = 1
        pixel_step_var.set("1")

# --- Tkinter UI ---
root = tk.Tk()
root.title("Mouse Puller")

hotkey_var = tk.StringVar(value=f"Hotkey: {hotkey.upper()}")
status_var = tk.StringVar(value="Status: OFF")
pixel_step_var = tk.StringVar(value=str(pixel_step))

tk.Label(root, textvariable=hotkey_var, font=("Arial", 14)).pack(pady=5)
tk.Label(root, textvariable=status_var, font=("Arial", 14)).pack(pady=5)

frame = tk.Frame(root)
frame.pack(pady=5)
tk.Label(frame, text="Pixels per step:").pack(side=tk.LEFT)
pixel_spin = tk.Spinbox(frame, from_=1, to=100, textvariable=pixel_step_var, width=5, command=update_pixel_step)
pixel_spin.pack(side=tk.LEFT)

def on_pixel_step_change(*args):
    update_pixel_step()
pixel_step_var.trace_add("write", on_pixel_step_change)

tk.Button(root, text="Set Hotkey", command=set_hotkey).pack(pady=5)
tk.Button(root, text="Exit", command=root.quit).pack(pady=5)

# Start mouse listener and hotkey listener in background
mouse_listener = mouse.Listener(on_click=on_click)
mouse_listener.start()
threading.Thread(target=listen_hotkey, daemon=True).start()

root.mainloop()