import time
import threading
import tkinter as tk
from pynput import mouse
from pynput.mouse import Button, Controller

click_interval = 0.05  # 50ms
clicking = False
bind_button = None
mouse_controller = Controller()

# GUI variables
label = None
status_var = None

def click_loop():
    global clicking
    while True:
        if clicking:
            mouse_controller.click(Button.left)
            time.sleep(click_interval)
        else:
            time.sleep(0.01)

def on_click(x, y, button, pressed):
    global bind_button, clicking
    if bind_button is None and pressed:
        bind_button = button
        print(f"[+] Bound to {bind_button.name.upper()}.")

    if button == bind_button:
        clicking = pressed
        if status_var:
            status_var.set("Clicking..." if pressed else "Waiting...")

def gui_thread():
    global label, status_var
    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.configure(bg="black")
    root.wm_attributes("-alpha", 0.7)

    screen_width = root.winfo_screenwidth()
    status_var = tk.StringVar(value="Waiting...")
    label = tk.Label(root, textvariable=status_var, font=("Arial", 14), fg="white", bg="black", padx=10, pady=5)
    label.pack()
    root.geometry(f"+{screen_width - 150}+20")  # top-right

    root.mainloop()

# Start the GUI in the main thread
print("[*] Click any mouse button to bind for autoclicking.")
print("[*] Hold the bound button to click every 50ms. Ctrl+C to exit.")

# Mouse listener in background
mouse.Listener(on_click=on_click).start()

# Start click thread
threading.Thread(target=click_loop, daemon=True).start()

# Start the GUI (must be in main thread)
gui_thread()
