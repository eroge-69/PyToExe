import time
import threading
import tkinter as tk
from tkinter import ttk
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode


delay = 0.0001
button = Button.left
start_stop_key = KeyCode(char='o')
exit_key = KeyCode(char='l')
shutdown_key = KeyCode(char='k')


mouse = Controller()


class ClickMouse(threading.Thread):
    def __init__(self, delay, button):
        super(ClickMouse, self).__init__()
        self.delay = delay
        self.button = button
        self.running = False
        self.program_running = True

    def start_clicking(self):
        self.running = True

    def stop_clicking(self):
        self.running = False

    def exit(self):
        self.stop_clicking()
        self.program_running = False

    def run(self):
        while self.program_running:
            while self.running:
                mouse.click(self.button)
                time.sleep(self.delay)
            time.sleep(0.1)


click_thread = ClickMouse(delay, button)
click_thread.start()


def on_press(key):
    if key == start_stop_key:
        toggle_clicking()
    elif key == exit_key:
        stop_clicking()
    elif key == shutdown_key:
        shutdown()


def toggle_clicking():
    if click_thread.running:
        click_thread.stop_clicking()
        status_var.set("Stopped")
        start_btn.config(text="Start")
    else:
        click_thread.start_clicking()
        status_var.set("Clicking...")
        start_btn.config(text="Stop")


def stop_clicking():
    click_thread.stop_clicking()
    status_var.set("Stopped")
    start_btn.config(text="Start")


def shutdown():
    click_thread.exit()
    root.quit()


# --- UI Setup ---
root = tk.Tk()
root.title("Auto Clicker")
root.geometry("320x180")
root.resizable(False, False)
root.configure(bg="#23272f")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 12), padding=8, background="#2d333b", foreground="#ffffff")
style.map("TButton", background=[("active", "#3c4251")])

status_var = tk.StringVar(value="Stopped")

title_lbl = tk.Label(root, text="Auto Clicker", font=("Segoe UI", 18, "bold"), bg="#23272f", fg="#00d8ff")
title_lbl.pack(pady=(18, 6))

status_lbl = tk.Label(root, textvariable=status_var, font=("Segoe UI", 12), bg="#23272f", fg="#ffffff")
status_lbl.pack(pady=(0, 12))

btn_frame = tk.Frame(root, bg="#23272f")
btn_frame.pack(pady=6)

start_btn = ttk.Button(btn_frame, text="Start", command=toggle_clicking)
start_btn.grid(row=0, column=0, padx=8)

stop_btn = ttk.Button(btn_frame, text="Stop", command=stop_clicking)
stop_btn.grid(row=0, column=1, padx=8)

shutdown_btn = ttk.Button(btn_frame, text="Shutdown", command=shutdown)
shutdown_btn.grid(row=0, column=2, padx=8)

hint_lbl = tk.Label(
    root,
    text="Hotkeys: [O] Start/Stop  [L] Stop  [K] Shutdown",
    font=("Segoe UI", 10),
    bg="#23272f",
    fg="#888"
)
hint_lbl.pack(pady=(12, 0))


def listen_keyboard():
    with Listener(on_press=on_press) as listener:
        listener.join()


keyboard_thread = threading.Thread(target=listen_keyboard, daemon=True)
keyboard_thread.start()

root.mainloop()
click_thread.exit()
