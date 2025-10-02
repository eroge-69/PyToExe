import tkinter as tk
import threading
import time
import keyboard  # pip install keyboard

running = False
active_key = None

def hold_key(key):
    global running, active_key
    active_key = key
    running = True
    while running:
        keyboard.press(key)
        time.sleep(0.05)  # keep key "held"

def start_press(key):
    global running
    stop_press()  # stop any previously pressed key
    t = threading.Thread(target=hold_key, args=(key,), daemon=True)
    t.start()

def stop_press():
    global running, active_key
    running = False
    if active_key:
        keyboard.release(active_key)
    active_key = None

def on_close():
    stop_press()
    root.destroy()

# GUI
root = tk.Tk()
root.title("Select button long press")
root.geometry("300x150")

label = tk.Label(root, text="Select button long press", font=("Arial", 14))
label.pack(pady=10)

btn_f3 = tk.Button(root, text="F3", width=10, command=lambda: start_press("f3"))
btn_f3.pack(pady=5)

btn_f4 = tk.Button(root, text="F4", width=10, command=lambda: start_press("f4"))
btn_f4.pack(pady=5)

btn_f5 = tk.Button(root, text="F5", width=10, command=lambda: start_press("f5"))
btn_f5.pack(pady=5)

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
