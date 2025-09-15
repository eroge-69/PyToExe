#!/usr/bin/env python3
import tkinter as tk
from datetime import datetime
from time import time

TARGET = datetime(2025, 10, 1, 0, 0, 0)   # Local time

def format_remaining():
    now = datetime.fromtimestamp(time())
    diff = TARGET - now
    total = int(diff.total_seconds())
    if total < 0:
        return "Time's up!"
    days, rem = divmod(total, 86400)
    hrs, rem = divmod(rem, 3600)
    mins, secs = divmod(rem, 60)
    return f"{days:02d} days  {hrs:02d}:{mins:02d}:{secs:02d}"

def update():
    label.config(text=format_remaining())
    root.after(1000, update)

root = tk.Tk()
root.title("Countdown to 1 Oct 2025")
root.resizable(False, False)

label = tk.Label(
    root,
    text="",
    font=("Helvetica", 32, "bold"),
    fg="white",
    bg="black",
    padx=20,
    pady=20
)
label.pack()

update()
root.mainloop()
