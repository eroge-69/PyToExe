
import tkinter as tk
from tkinter import filedialog, messagebox
import schedule
import time
import threading
from playsound import playsound
from datetime import datetime
import os

# Global state
bell_thread = None
bell_running = False
schedule_jobs = []

# Default bell sound
bell_sound_path = "bell.wav"
schedule_file = "schedule.txt"

def ring_bell():
    try:
        print(f"🔔 Bell rung at {datetime.now().strftime('%H:%M:%S')}")
        playsound(bell_sound_path)
    except Exception as e:
        print("Error playing bell sound:", e)

def load_schedule():
    global schedule_jobs
    schedule.clear()
    schedule_jobs = []
    if not os.path.exists(schedule_file):
        return
    with open(schedule_file, 'r') as f:
        for line in f:
            time_str = line.strip()
            if time_str:
                job = schedule.every().day.at(time_str).do(ring_bell)
                schedule_jobs.append(job)

def schedule_runner():
    while bell_running:
        schedule.run_pending()
        time.sleep(1)

def start_bell():
    global bell_thread, bell_running
    if not bell_running:
        load_schedule()
        bell_running = True
        bell_thread = threading.Thread(target=schedule_runner, daemon=True)
        bell_thread.start()
        status_var.set("🟢 Running")
    else:
        messagebox.showinfo("Info", "Bell is already running!")

def stop_bell():
    global bell_running
    bell_running = False
    schedule.clear()
    status_var.set("🔴 Stopped")

def browse_sound():
    global bell_sound_path
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        bell_sound_path = file_path
        sound_path_var.set(bell_sound_path)

def edit_schedule():
    os.system(f"notepad {schedule_file}")

# ---------------- GUI ------------------
app = tk.Tk()
app.title("🏫 School Bell System")
app.geometry("400x300")
app.resizable(False, False)

# Fonts
font_label = ("Segoe UI", 10)
font_btn = ("Segoe UI", 10)

# Sound path
sound_path_var = tk.StringVar(value=bell_sound_path)

tk.Label(app, text="🔔 Bell Sound:", font=font_label).pack(pady=(10, 2))
tk.Entry(app, textvariable=sound_path_var, width=40).pack()
tk.Button(app, text="Browse...", command=browse_sound).pack(pady=5)

tk.Label(app, text="📅 Schedule (in schedule.txt):", font=font_label).pack(pady=(15, 2))
tk.Button(app, text="Edit Schedule", command=edit_schedule).pack(pady=5)

tk.Button(app, text="▶ Start Bell", font=font_btn, bg="green", fg="white", command=start_bell).pack(pady=(20, 5))
tk.Button(app, text="■ Stop Bell", font=font_btn, bg="red", fg="white", command=stop_bell).pack()

status_var = tk.StringVar(value="🔴 Stopped")
tk.Label(app, textvariable=status_var, font=("Segoe UI", 12, "bold")).pack(pady=10)

tk.Label(app, text="Created by ChatGPT ❤️", font=("Segoe UI", 8), fg="gray").pack(side="bottom")

app.mainloop()
