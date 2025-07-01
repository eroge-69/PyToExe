import tkinter as tk
from tkinter import ttk
import threading
import time
import pyautogui
import keyboard
from pynput.mouse import Button, Controller
import sv_ttk  # For theming

mouse = Controller()
clicking = False
click_thread = None
use_fixed_position = False
fixed_pos = (0, 0)

root = tk.Tk()

def click_loop(interval, button, fixed):
    clicks = 0
    global clicking
    btn = Button.left
    while clicking:
        clicks = clicks + 1
        print(clicks)
        root.title(f"Clicc - Clicking ({clicks}) (Press F6 to stop or press Stop Clicking)")
        if fixed:
            pyautogui.click(fixed[0], fixed[1], button='left')
        else:
            mouse.click(btn)
        time.sleep(interval)

def toggle_clicking():
    global clicking, click_thread
    if not clicking:
        
        try:
            root.title("Clicc - Clicking (Press F6 to stop or press Stop Clicking)")
            # Calculate total interval in seconds
            hours = int(hours_var.get())
            minutes = int(minutes_var.get())
            seconds = int(seconds_var.get())
            milliseconds = int(milliseconds_var.get())
            interval = (hours * 3600) + (minutes * 60) + seconds + (milliseconds / 1000.0)

            if interval <= 0:
                update_status("Interval must be > 0")  # Remove color
                return
        except ValueError:
            root.title("Clicc - Invalid Interval")
            update_status("Invalid interval")  # Remove color
            return

        fixed = fixed_pos if use_fixed_position else None
        clicking = True
        click_thread = threading.Thread(target=click_loop, args=(interval, 'left', fixed), daemon=True) #Removed the button
        click_thread.start()
        update_status("Clicking started")  # Remove color
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)
    else:
        root.title("Clicc - Idle (Press F6 to start or click Start Clicking)")
        clicking = False
        update_status("Clicking stopped")  # Remove color
        start_btn.config(state=tk.NORMAL)
        stop_btn.config(state=tk.DISABLED)

def update_status(text):  # Removed color argument
    status_label.config(text=text)  # Removed foreground

def set_fixed_position():
    global use_fixed_position, fixed_pos
    x, y = pyautogui.position()
    fixed_pos = (x, y)
    use_fixed_position = True
    update_status(f"Fixed position set to ({x}, {y})")  # Remove color

def unset_position():
    global use_fixed_position
    use_fixed_position = False
    update_status("Clicking at mouse position")  # Remove color

def on_hotkey():
    toggle_clicking()

def listen_for_hotkey():
    keyboard.add_hotkey("f6", on_hotkey)
    keyboard.wait()

def on_close():
    global clicking
    clicking = False
    root.destroy()

# --- GUI Setup ---

root.title("Clicc - Idle (Press F6 to start or click Start Clicking)")
root.geometry("460x105")  # Reduced height
root.iconbitmap("icon.ico")
root.resizable(False, False)
root.protocol("WM_DELETE_WINDOW", on_close)
sv_ttk.set_theme("dark")  # Set the theme
# root.

# --- Interval Frame ---
interval_frame = ttk.Frame(root, padding=10)
interval_frame.pack(pady=(10, 0), fill=tk.X)  # Padding top only and fill X

# --- Interval Controls ---
hours_var = tk.StringVar(value="0")
minutes_var = tk.StringVar(value="0")
seconds_var = tk.StringVar(value="0")
milliseconds_var = tk.StringVar(value="100")

ttk.Label(interval_frame, text="Hours:").grid(row=0, column=0, padx=2, pady=2, sticky=tk.E)
hours_entry = ttk.Entry(interval_frame, textvariable=hours_var, width=3, justify="center")
hours_entry.grid(row=0, column=1, padx=2, pady=2)

ttk.Label(interval_frame, text="Minutes:").grid(row=0, column=2, padx=2, pady=2, sticky=tk.E)
minutes_entry = ttk.Entry(interval_frame, textvariable=minutes_var, width=3, justify="center")
minutes_entry.grid(row=0, column=3, padx=2, pady=2)

ttk.Label(interval_frame, text="Seconds:").grid(row=0, column=4, padx=2, pady=2, sticky=tk.E)
seconds_entry = ttk.Entry(interval_frame, textvariable=seconds_var, width=3, justify="center")
seconds_entry.grid(row=0, column=5, padx=2, pady=2)

ttk.Label(interval_frame, text="Milliseconds:").grid(row=0, column=6, padx=2, pady=2, sticky=tk.E)
milliseconds_entry = ttk.Entry(interval_frame, textvariable=milliseconds_var, width=5, justify="center")
milliseconds_entry.grid(row=0, column=7, padx=2, pady=2, sticky=tk.W) # changed to W from E


# --- Other Controls Frame (Button, Location, etc.) ---
other_controls_frame = ttk.Frame(root, padding=10)
other_controls_frame.pack(pady=(0, 0))  # No vertical padding


# --- Start/Stop Buttons ---
button_frame = ttk.Frame(root) #new frame
button_frame.pack(pady=0, fill=tk.X) #pack with fill

start_btn = ttk.Button(button_frame, text="Start Clicking", command=toggle_clicking)
start_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5) # Side by side
stop_btn = ttk.Button(button_frame, text="Stop Clicking", command=toggle_clicking, state=tk.DISABLED)
stop_btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5) # Side by side


# --- Status Label ---
status_label = ttk.Label(root, text="Ready (F6 to toggle)") # removed the foreground
status_label.pack(pady=(0, 10))  # Reduced top padding

# --- Hotkey Listener ---
hotkey_thread = threading.Thread(target=listen_for_hotkey, daemon=True)
hotkey_thread.start()

# --- Run ---
root.mainloop()