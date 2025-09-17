import tkinter as tk
from tkinter import simpledialog
import time
import threading
from datetime import datetime

# Main Window
root = tk.Tk()
root.title("Stopwatch, Timer, Date & Time App")
root.geometry("400x300")

# Global variables
running = False
counter = 0

# --- Stopwatch Functions ---
def start_stopwatch():
    global running
    running = True
    update_stopwatch()

def stop_stopwatch():
    global running
    running = False

def reset_stopwatch():
    global running, counter
    running = False
    counter = 0
    stopwatch_label.config(text="00:00:00")

def update_stopwatch():
    global counter
    if running:
        counter += 1
        hours, remainder = divmod(counter, 3600)
        minutes, seconds = divmod(remainder, 60)
        stopwatch_label.config(text=f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        root.after(1000, update_stopwatch)

# --- Timer Functions ---
def start_timer():
    t = simpledialog.askinteger("Timer", "Enter time in seconds:")
    if t:
        threading.Thread(target=run_timer, args=(t,)).start()

def run_timer(t):
    while t > 0:
        mins, secs = divmod(t, 60)
        timer_label.config(text=f"{mins:02d}:{secs:02d}")
        time.sleep(1)
        t -= 1
    timer_label.config(text="Time's up!")

# --- Date & Time Function ---
def update_datetime():
    now = datetime.now()
    date_time_label.config(text=now.strftime("%Y-%m-%d %H:%M:%S"))
    root.after(1000, update_datetime)

# --- Labels ---
stopwatch_label = tk.Label(root, text="00:00:00", font=("Helvetica", 24))
stopwatch_label.pack(pady=10)

timer_label = tk.Label(root, text="00:00", font=("Helvetica", 24))
timer_label.pack(pady=10)

date_time_label = tk.Label(root, text="", font=("Helvetica", 16))
date_time_label.pack(pady=10)
update_datetime()

# --- Buttons ---
frame = tk.Frame(root)
frame.pack(pady=10)

tk.Button(frame, text="Start Stopwatch", command=start_stopwatch).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Stop Stopwatch", command=stop_stopwatch).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Reset Stopwatch", command=reset_stopwatch).grid(row=0, column=2, padx=5)

tk.Button(root, text="Start Timer", command=start_timer).pack(pady=5)

root.mainloop()
