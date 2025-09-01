
import tkinter as tk
from tkinter import ttk
import threading
import psutil
import os

# Flag to control thread execution
stress_active = False

# Function to simulate CPU load
def cpu_stress_worker():
    while stress_active:
        pass  # Busy loop to consume CPU

# Function to start CPU stress threads
def start_stress():
    global stress_threads, stress_active
    stop_stress()  # Stop any existing threads
    stress_active = True
    num_threads = intensity.get()
    stress_threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=cpu_stress_worker)
        t.daemon = True
        t.start()
        stress_threads.append(t)

# Function to stop all stress threads
def stop_stress():
    global stress_active
    stress_active = False

# Function to update CPU usage label
def update_cpu_usage():
    usage = psutil.cpu_percent(interval=1)
    cpu_label.config(text=f"CPU Usage: {usage}%")
    root.after(1000, update_cpu_usage)

# Create GUI
root = tk.Tk()
root.title("CPU Stress Tester")
root.geometry("300x250")

stress_threads = []

# Intensity slider
intensity = tk.IntVar(value=1)
ttk.Label(root, text="Intensity (Threads):").pack(pady=5)
slider = ttk.Scale(root, from_=1, to=os.cpu_count(), variable=intensity, orient="horizontal")
slider.pack(fill="x", padx=10)

# Start button
start_button = ttk.Button(root, text="Start Stress", command=start_stress)
start_button.pack(pady=10)

# Stop button
stop_button = ttk.Button(root, text="Stop Stress", command=stop_stress)
stop_button.pack(pady=10)

# CPU usage label
cpu_label = ttk.Label(root, text="CPU Usage: 0%")
cpu_label.pack(pady=10)

# Start updating CPU usage
update_cpu_usage()

# Run the GUI loop
root.mainloop()
