import tkinter as tk
from tkinter import ttk
import psutil
import shutil

# Function to get storage status
def get_storage_status():
    total, used, free = shutil.disk_usage("C:/")
    total_gb = total // (2**30)
    free_gb = free // (2**30)
    
    # Determine storage rating
    if free_gb < 10:
        status = "Poor"
    elif free_gb < 20:
        status = "Bad"
    elif free_gb < 30:
        status = "Decent"
    else:
        status = "Good"
        
    return total_gb, free_gb, status

# Function to get CPU usage
def get_cpu_usage():
    return psutil.cpu_percent(interval=1)

# Function to get RAM usage
def get_ram_usage():
    mem = psutil.virtual_memory()
    return mem.percent

# Function to update all stats
def update_stats():
    total, free, storage_status = get_storage_status()
    cpu = get_cpu_usage()
    ram = get_ram_usage()
    
    storage_label.config(text=f"Local Disk Space: {free}GB free / {total}GB total ({storage_status})")
    cpu_label.config(text=f"CPU Usage: {cpu}%")
    ram_label.config(text=f"RAM Usage: {ram}%")
    
    # Schedule the update every 2 seconds
    root.after(2000, update_stats)

# Create the Tkinter window
root = tk.Tk()
root.title("sts")
root.iconbitmap(r"Z:/info_medium.ico")
root.geometry("450x220")
root.resizable(False, False)

# Font settings
font_style = ("Segoe UI", 12, "bold")

# Labels for stats
storage_label = ttk.Label(root, text="", font=font_style)
storage_label.pack(pady=10)

cpu_label = ttk.Label(root, text="", font=font_style)
cpu_label.pack(pady=10)

ram_label = ttk.Label(root, text="", font=font_style)
ram_label.pack(pady=10)

gpu_label = ttk.Label(root, text="GPU Usage: Not detected", font=font_style)
gpu_label.pack(pady=10)

# Start updating stats
update_stats()

root.mainloop()
