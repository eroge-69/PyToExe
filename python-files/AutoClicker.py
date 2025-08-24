
import threading
import time
from pynput.mouse import Button, Controller as MouseController
from pynput import keyboard
import tkinter as tk
from tkinter import ttk, messagebox

# Global variables
mouse = MouseController()
clicking = False
click_thread = None
click_interval = 0.1
click_button = Button.left  # Default click button

# Start/stop hotkeys
START_HOTKEY = keyboard.Key.f6
STOP_HOTKEY = keyboard.Key.f7


def click_loop():
    global clicking
    while clicking:
        mouse.click(click_button)
        time.sleep(click_interval)


def on_press(key):
    global clicking, click_thread
    if key == START_HOTKEY and not clicking:
        clicking = True
        click_thread = threading.Thread(target=click_loop)
        click_thread.start()
        print("Started clicking.")
    elif key == STOP_HOTKEY and clicking:
        clicking = False
        click_thread.join()
        print("Stopped clicking.")


def start_keyboard_listener():
    listener = keyboard.Listener(on_press=on_press)
    listener.daemon = True
    listener.start()


def start_gui():
    def apply_interval():
        global click_interval
        try:
            interval = float(interval_input.get())
            if interval < 0:
                raise ValueError
            click_interval = interval
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number (0 or greater) for seconds between clicks.")

    def update_click_button(event=None):
        global click_button
        selected = click_type.get()
        click_button = Button.left if selected == "Left Click" else Button.right

    root = tk.Tk()
    root.title("Auto Clicker")
    root.geometry("300x220")
    root.resizable(False, False)

    # Interval input
    ttk.Label(root, text="Seconds Between Clicks:").pack(pady=(10, 0))
    interval_input = ttk.Entry(root)
    interval_input.insert(0, "0.1")
    interval_input.pack(pady=5)

    apply_btn = ttk.Button(root, text="Apply Interval", command=apply_interval)
    apply_btn.pack(pady=5)

    # Click type selection
    ttk.Label(root, text="Click Type:").pack(pady=(10, 0))
    click_type = tk.StringVar()
    click_type_dropdown = ttk.Combobox(root, textvariable=click_type, state="readonly")
    click_type_dropdown['values'] = ("Left Click", "Right Click")
    click_type_dropdown.current(0)
    click_type_dropdown.bind("<<ComboboxSelected>>", update_click_button)
    click_type_dropdown.pack(pady=5)
    update_click_button()

    # Instructions
    ttk.Label(root, text=f"Hotkeys:").pack(pady=(15, 0))
    ttk.Label(root, text=f"Start: F6  |  Stop: F7").pack()

    root.mainloop()


if __name__ == "__main__":
    start_keyboard_listener()
    start_gui()
