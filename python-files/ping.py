import tkinter as tk
from tkinter import Canvas
import subprocess
import threading
import time

# List of IP addresses to monitor
ip_addresses = [
    "10.3.4.54",
    "10.4.2.24",
    "10.4.2.25",
    "10.3.4.52",
    "10.3.16.1",
    "10.234.148.1",
    "10.234.151.200"
]

# Function to ping an IP
def ping(ip):
    try:
        output = subprocess.run(["ping", "-n", "1", "-w", "1000", ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        return "TTL=" in output.stdout
    except Exception:
        return False

# Update the status lights
def update_status():
    while True:
        for i, ip in enumerate(ip_addresses):
            status = ping(ip)
            canvas.itemconfig(circles[i], fill="green" if status else "red")
time.sleep(5)

# Set up UI
root = tk.Tk()
root.title("SRB Pings")
canvas = Canvas(root, width=1000, height=200)
canvas.pack()

circles = []
for i in range(len(ip_addresses)):
    x = 140 * i + 70
    circle = canvas.create_oval(x, 30, x + 40, 60, fill="gray")
    circles.append(circle)
    canvas.create_text(x + 20, 80, text=ip_addresses[i], font=('Helvetica', 11))

# Start the pinging in a separate thread
threading.Thread(target=update_status, daemon=True).start()

root.mainloop()