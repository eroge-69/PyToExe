from pynput.keyboard import Controller as PynputController
import keyboard
import tkinter as tk
import threading
import time
import tkinter.font as tkFont

# Initialize keyboard controller
keyboard_controller = PynputController()

# Global state variables
spammer_on = False
last_toggle_time = 0
debounce_delay = 0.3  # 300 ms debounce

def spam_keys():
    global spammer_on
    while True:
        if spammer_on:
            keyboard_controller.press('a')
            keyboard_controller.release('a')
            time.sleep(0.01)
            keyboard_controller.press('d')
            keyboard_controller.release('d')
            time.sleep(0.01)
        else:
            time.sleep(0.1)  # Reduce CPU usage when idle

def toggle_spammer():
    global spammer_on, last_toggle_time
    now = time.time()
    if now - last_toggle_time >= debounce_delay:
        spammer_on = not spammer_on
        print("Spammer is now", "ON" if spammer_on else "OFF")
        last_toggle_time = now

# GUI Setup
def create_gui():
    root = tk.Tk()
    root.title("Fnaf hunted auto key spammer")
    root.geometry("400x200")
    root.resizable(False, False)

    # Set code-style font
    font_style = tkFont.Font(family="Courier", size=16, weight="bold")

    label = tk.Label(root, text="Press H to toggle", font=font_style, fg="#00ff00")
    label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    root.mainloop()

# Start GUI in a separate thread
gui_thread = threading.Thread(target=create_gui, daemon=True)
gui_thread.start()

# Start spammer thread
spammer_thread = threading.Thread(target=spam_keys, daemon=True)
spammer_thread.start()

# Register H key with debounce-aware toggle
keyboard.add_hotkey('h', toggle_spammer)

# Keep program alive
keyboard.wait()
