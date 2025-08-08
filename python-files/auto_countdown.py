
import tkinter as tk
import time
from datetime import datetime

target_hour = 16
target_minute = 25

root = tk.Tk()
root.title("Countdown")
root.configure(bg="black")

# Klein klok-label
small_label = tk.Label(root, text="", font=("Arial", 30), fg="white", bg="black")
small_label.pack(pady=20)

# Groot countdown-label
big_label = tk.Label(root, text="", font=("Arial", 200, "bold"), fg="red", bg="black")
big_label.pack(expand=True)

def wait_until_target():
    now = datetime.now()
    target_time = datetime(now.year, now.month, now.day, target_hour, target_minute, 0)
    remaining = (target_time - now).total_seconds()

    if remaining > 0:
        mins, secs = divmod(int(remaining), 60)
        small_label.config(text=f"Start over: {mins:02}:{secs:02}")
        root.after(1000, wait_until_target)
    else:
        start_big_countdown(60)

def start_big_countdown(t):
    small_label.config(text="")
    root.attributes("-fullscreen", True)
    if t >= 0:
        mins, secs = divmod(t, 60)
        big_label.config(text=f"{secs:02}")
        root.after(1000, start_big_countdown, t - 1)
    else:
        root.destroy()

wait_until_target()
root.mainloop()
