# text_with_launcher.py
import tkinter as tk
import time
import os
import sys
import subprocess
from tkinter import messagebox

# Configuration (same as your original)
WIDTH, HEIGHT = 800, 450
FONT = ("Segoe UI", 48, "bold")
BG_COLOR = "#0b67ff"
TEXT_COLOR = "white"
FIRST_TEXT = "Hi"
SECOND_TEXT = "Welcome to uc.zz lock"
FIRST_DURATION = 1500      # ms
FADE_STEPS = 20
FADE_DELAY = 25            # ms between fade steps

# Name of the exe to launch (must be in same folder)
EXE_NAME = "crxck.exe"

def fade(window, start, end, steps=FADE_STEPS, delay=FADE_DELAY):
    delta = (end - start) / steps
    alpha = start
    for _ in range(steps):
        alpha += delta
        alpha = max(0.0, min(1.0, alpha))
        window.attributes("-alpha", alpha)
        window.update()
        window.after(delay)

def launch_exe_visible():
    # Build path to exe located next to this script or bundled exe
    if getattr(sys, "frozen", False):  # when bundled by PyInstaller
        base_path = sys._MEIPASS  # PyInstaller temp folder for added data
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    exe_path = os.path.join(base_path, EXE_NAME)

    if not os.path.isfile(exe_path):
        messagebox.showerror("Error", f"Could not find {EXE_NAME} at:\n{exe_path}")
        return

    # Inform the user (transparent)
    messagebox.showinfo("Launching", f"{EXE_NAME} will now be launched.\nThis will open a separate program.")
    try:
        # Use Popen so this script doesn't block
        subprocess.Popen([exe_path], shell=False)
    except Exception as e:
        messagebox.showerror("Launch failed", f"Failed to launch {EXE_NAME}:\n{e}")

def do_transition(root, label):
    fade(root, 1.0, 0.0)
    label.config(text=SECOND_TEXT)
    root.after(100, lambda: fade(root, 0.0, 1.0))
    # After the second message completes (wait a short moment), launch exe visibly:
    root.after(1000, launch_exe_visible)  # 1s after fade-in

def main():
    root = tk.Tk()
    root.title("uc.zz lock")
    root.geometry(f"{WIDTH}x{HEIGHT}")
    root.resizable(False, False)

    frame = tk.Frame(root, bg=BG_COLOR, width=WIDTH, height=HEIGHT)
    frame.pack(fill="both", expand=True)

    label = tk.Label(frame, text=FIRST_TEXT, font=FONT, bg=BG_COLOR, fg=TEXT_COLOR)
    label.place(relx=0.5, rely=0.5, anchor="center")

    root.attributes("-alpha", 1.0)
    root.after(FIRST_DURATION, lambda: do_transition(root, label))

    root.mainloop()

if __name__ == "__main__":
    main()
