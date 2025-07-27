import tkinter as tk
from tkinter import font
import time
import json
import os

APP_TITLE = "Dante by Revolut UK Ltd"
LICENSE_NO = "UKREV0927125010"
PARTNER = "Contragenix"
EMPLOYEE_CODE = "EMP63933"
ASSOCIATE_NAME = "Muhammad Aqib Zargar"
DEVICE_STATUS = "inprogress (30 new devices attached, est. time: {hours_left} hours)"
SERVER = "Bangalore (INDIA)"
MESSAGE = "You can shut down the server for the remainder"

STATE_FILE = "dante_state.json"
TOTAL_HOURS = 110

def load_start_time():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            data = json.load(f)
            return data.get("start_time")
    else:
        start_time = time.time()
        with open(STATE_FILE, 'w') as f:
            json.dump({"start_time": start_time}, f)
        return start_time

def calculate_remaining_time(start_time):
    elapsed_seconds = time.time() - float(start_time)
    remaining_seconds = max(0, TOTAL_HOURS * 3600 - elapsed_seconds)
    return remaining_seconds

def format_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def update_timer():
    remaining = calculate_remaining_time(start_time)
    timer_label.config(text=f"Timer: {format_time(remaining)}")
    if remaining > 0:
        root.after(1000, update_timer)
    else:
        timer_label.config(text="Timer: 00:00:00")

root = tk.Tk()
root.title("Dante App")
root.geometry("500x400")
root.resizable(False, False)

custom_font = font.Font(family="Helvetica", size=14, weight="bold")
body_font = font.Font(family="Helvetica", size=11)

heading = tk.Label(root, text=APP_TITLE, font=custom_font)
heading.pack(pady=10)

start_time = load_start_time()

info_text = (
    f"License No: {LICENSE_NO}\n"
    f"Partner: {PARTNER}\n"
    f"Employee Code: {EMPLOYEE_CODE}\n"
    f"Associate Name: {ASSOCIATE_NAME}\n\n"
    f"Current Enroll Status: {DEVICE_STATUS.format(hours_left=TOTAL_HOURS)}\n"
    f"Server: {SERVER}\n\n"
    f"{MESSAGE}"
)

info_label = tk.Label(root, text=info_text, font=body_font, justify="left")
info_label.pack(pady=10)

timer_label = tk.Label(root, text="", font=body_font)
timer_label.pack(pady=5)

update_timer()
root.mainloop()