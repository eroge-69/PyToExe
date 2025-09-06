import tkinter as tk
from tkinter import ttk
import time
import threading

# Fake messages
messages = [
    "Cleaning C:\\Windows\\System32\\drivers\\etc\\hosts",
    "Scanning for programs using C:\\Program Files\\",
    "Adding checksums in C:\\Steam\\steamapps",
    "Moving C:\\Users\\Admin\\AppData\\Temp files",
    "Cleaning C:\\Users\\Admin\\Desktop\\logs.txt"
]

def fake_loading():
    for i, msg in enumerate(messages):
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)
        progress['value'] += 20
        time.sleep(1.5)
    status_label.config(text="Status: Stuck loading... Please wait.")

root = tk.Tk()
root.title("Clean Fight - Loading")
root.geometry("600x300")

# Status text
status_label = tk.Label(root, text="Status: Initializing...", anchor="w")
status_label.pack(fill="x", padx=10, pady=5)

# Progress bar
progress = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
progress.pack(pady=10)
progress["maximum"] = 100

# Log area
log_box = tk.Text(root, height=10, width=70)
log_box.pack(padx=10, pady=5)

# Run loading in background thread
threading.Thread(target=fake_loading, daemon=True).start()

root.mainloop()
