import tkinter as tk
from tkinter import ttk
import threading
import time
import psutil

# Name of the second app executable (change this)
TARGET_PROCESS = "second_app.exe"

# Check if the target app is running
def is_target_running():
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] and TARGET_PROCESS.lower() in proc.info['name'].lower():
            return True
    return False

# Simulate progress bar while waiting for second app
def wait_for_app():
    i = 0
    while not is_target_running():
        if i < 99:
            progress['value'] = i
            percent_label.config(text=f"{i}%")
            i += 1
        time.sleep(3)
    # Once second app is detected
    progress['value'] = 100
    percent_label.config(text="100%")
    status_label.config(text="Downloads complete")

app = tk.Tk()
app.title("Apps Downloading")
app.geometry("1080x400")
app.resizable(False, False)

ttk.Label(app, text="Downloading files...").pack(pady=100)
progress = ttk.Progressbar(app, length=600, mode='determinate')
progress.pack()
percent_label = ttk.Label(app, text="0%")
percent_label.pack()
status_label = ttk.Label(app, text="You Can you your computor in the mean time.                                   This is version 3H1 this app is in beta")
status_label.pack()

threading.Thread(target=wait_for_app, daemon=True).start()
app.mainloop()