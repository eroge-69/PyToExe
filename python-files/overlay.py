import tkinter as tk
import keyboard   # pip install keyboard
from pynput import mouse
import threading

# --- Settings ---
overlay_width = 80
overlay_height = 60
opacity = 0.8
poll_ms = 100
# -----------------

# States
caps_on = False
cycle_values = [2, 3, 1]
cycle_index = 0  # starts at 2

state_lock = threading.Lock()

def on_caps_press(e=None):
    global caps_on
    with state_lock:
        caps_on = not caps_on  # toggle state

def on_cycle_press():
    global cycle_index
    with state_lock:
        cycle_index = (cycle_index + 1) % len(cycle_values)

def update_ui():
    with state_lock:
        caps_text = "ON" if caps_on else "OFF"
        caps_color = "lime" if caps_on else "red"
        current_cycle = cycle_values[cycle_index]
    caps_label.config(text=caps_text, fg=caps_color)
    cycle_label.config(text=str(current_cycle))
    root.after(poll_ms, update_ui)

# Tkinter overlay window
root = tk.Tk()
root.overrideredirect(True)       # no border
root.attributes("-topmost", True)
root.attributes("-alpha", opacity)
root.configure(bg="black")

# Position overlay to middle-right
screen_w = root.winfo_screenwidth()
screen_h = root.winfo_screenheight()
x = screen_w - overlay_width - 20
y = (screen_h // 2) - (overlay_height // 2)
root.geometry(f"{overlay_width}x{overlay_height}+{x}+{y}")

# Labels
caps_label = tk.Label(root, text="OFF", font=("Arial", 14, "bold"), fg="red", bg="black")
caps_label.pack()

cycle_label = tk.Label(root, text="2", font=("Arial", 16, "bold"), fg="cyan", bg="black")
cycle_label.pack()

# Keyboard hook for Caps Lock
keyboard.on_press_key("caps lock", on_caps_press)

# Mouse hook for Button.x1
def mouse_click(x, y, button, pressed):
    if pressed and str(button) == "Button.x1":
        on_cycle_press()

listener = mouse.Listener(on_click=mouse_click)
listener.start()

update_ui()
root.mainloop()
