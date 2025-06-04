import datetime
import os
import tkinter as tk
from tkinter import simpledialog

LOG_FILE = r"C:\Users\kesl\OneDrive - SEFIRA spol. s r.o\Dokumenty\TimeTracker\time_log.txt"

def get_task_name():
    root = tk.Tk()
    root.withdraw()
    task_name = simpledialog.askstring("New Task", "What are you working on?")
    return task_name if task_name else "Unnamed Task"

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("Time Tracking Log\n\n")

current_time = datetime.datetime.now()
time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
task_name = get_task_name()

with open(LOG_FILE, "a") as f:
    f.write(f"Start: {time_str} | Task: {task_name}\n")

os.system(f'powershell -command "Add-Type -AssemblyName System.Windows.Forms; [Windows.Forms.MessageBox]::Show(\'Started: {task_name}\', \'Time Tracking\')"')