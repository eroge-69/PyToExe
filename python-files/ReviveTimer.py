import time
import json
import os
import tkinter as tk
from tkinter import messagebox

# File to store numbers and timestamps
DATA_FILE = "revive_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def cleanup_data(data):
    """Remove entries older than 2 hours (7200 seconds)."""
    current_time = time.time()
    return {num: ts for num, ts in data.items() if current_time - ts < 7200}

def submit_number(event=None):  # event=None allows Enter key binding
    number = entry.get().strip()
    if not number:
        messagebox.showwarning("Warning", "Please enter a number!")
        return

    current_time = time.time()
    data = load_data()

    # Clean up old entries
    data = cleanup_data(data)

    if number in data:
        last_time = data[number]
        elapsed = current_time - last_time
        if elapsed < 1800:  # 30 minutes
            messagebox.showerror("Blocked", "You can't pick them up.")
            return

    # Save new timestamp
    data[number] = current_time
    save_data(data)
    messagebox.showinfo("Success", f"Number {number} stored successfully!")
    entry.delete(0, tk.END)

def clear_all():
    """Delete all stored data."""
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        messagebox.showinfo("Cleared", "All stored numbers have been cleared!")
    else:
        messagebox.showinfo("Nothing to Clear", "No stored numbers found.")

# GUI setup
root = tk.Tk()
root.title("Revive Checker")
root.geometry("320x200")

label = tk.Label(root, text="Enter a number:", font=("Arial", 12))
label.pack(pady=10)

entry = tk.Entry(root, font=("Arial", 12))
entry.pack(pady=5)

# Auto-focus the entry box on startup
entry.focus()

# Bind Enter key to submit
entry.bind("<Return>", submit_number)

button = tk.Button(root, text="Submit", command=submit_number, font=("Arial", 12))
button.pack(pady=10)

clear_button = tk.Button(root, text="Clear All", command=clear_all, font=("Arial", 12), fg="red")
clear_button.pack(pady=5)

root.mainloop()
