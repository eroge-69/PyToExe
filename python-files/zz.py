import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

# Function to ping the target
def ping(target):
    # Determine the command based on the OS (Windows or Unix-based)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        # Ping the target
        response = subprocess.run(["ping", param, "4", target], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        if response.returncode == 0:
            return True
        else:
            return False
    except Exception as e:
        messagebox.showerror("Error", f"Failed to ping: {e}")
        return False

# Function to handle the ping button click event
def on_ping_button_click():
    target = target_entry.get()
    if not target:
        messagebox.showerror("Error", "Please enter a target to ping.")
        return
    
    # Ping the target and update the UI accordingly
    if ping(target):
        result_label.config(text=f"Ping to {target} was successful!", fg="green")
    else:
        result_label.config(text=f"Ping to {target} failed.", fg="red")

# Create the main window
root = tk.Tk()
root.title("Ping Test")
root.geometry("400x200")

# Add a Label for the title
title_label = tk.Label(root, text="Ping Test Application", font=("Arial", 18))
title_label.pack(pady=20)

# Target input field
target_label = tk.Label(root, text="Enter target IP/Domain:")
target_label.pack(pady=5)

target_entry = tk.Entry(root, width=30)
target_entry.pack(pady=5)

# Ping button
ping_button = tk.Button(root, text="Ping", command=on_ping_button_click)
ping_button.pack(pady=10)

# Label to display the result of the ping
result_label = tk.Label(root, text="", font=("Arial", 14))
result_label.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()
