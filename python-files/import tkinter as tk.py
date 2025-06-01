import tkinter as tk
from tkinter import ttk
import psutil
import platform
import subprocess
import socket

def get_ip():
    try:
        return socket.gethostbyname(socket.gethostname())
    except:
        return "?"

def shutdown():
    subprocess.call(["shutdown", "/s", "/t", "0"])

def reboot():
    subprocess.call(["shutdown", "/r", "/t", "0"])

def update_system_tab():
    cpu_label.config(text=f"{psutil.cpu_percent()} %")
    ram_label.config(text=f"{psutil.virtual_memory().percent} %")
    disk_label.config(text=f"{psutil.disk_usage('/').percent} %")
    system_tab.after(1000, update_system_tab)

def update_network_tab():
    net = psutil.net_io_counters()
    net_label.config(text=f"Gesendet: {net.bytes_sent // (1024*1024)} MB\nEmpfangen: {net.bytes_recv // (1024*1024)} MB\nIP: {get_ip()}")
    network_tab.after(1000, update_network_tab)

root = tk.Tk()
root.title("Touch-PC Dashboard")
root.geometry("800x480")  # Passe an deine Auflösung an
root.configure(bg="black")

tab_control = ttk.Notebook(root)

# System-Tab
system_tab = tk.Frame(tab_control, bg="black")
tab_control.add(system_tab, text='System')
tk.Label(system_tab, text="CPU-Auslastung:", fg="white", bg="black", font=("Arial", 18)).pack(pady=10)
cpu_label = tk.Label(system_tab, fg="lime", bg="black", font=("Arial", 18))
cpu_label.pack()

tk.Label(system_tab, text="RAM-Auslastung:", fg="white", bg="black", font=("Arial", 18)).pack(pady=10)
ram_label = tk.Label(system_tab, fg="cyan", bg="black", font=("Arial", 18))
ram_label.pack()

tk.Label(system_tab, text="Festplattennutzung:", fg="white", bg="black", font=("Arial", 18)).pack(pady=10)
disk_label = tk.Label(system_tab, fg="yellow", bg="black", font=("Arial", 18))
disk_label.pack()

# Netzwerk-Tab
network_tab = tk.Frame(tab_control, bg="black")
tab_control.add(network_tab, text='Netzwerk')
tk.Label(network_tab, text="Netzwerkstatus:", fg="white", bg="black", font=("Arial", 18)).pack(pady=10)
net_label = tk.Label(network_tab, fg="lightgreen", bg="black", font=("Arial", 18))
net_label.pack()

# Steuerung-Tab
control_tab = tk.Frame(tab_control, bg="black")
tab_control.add(control_tab, text='Steuerung')
tk.Button(control_tab, text="Herunterfahren", command=shutdown, font=("Arial", 18), bg="red", fg="white").pack(pady=20)
tk.Button(control_tab, text="Neustarten", command=reboot, font=("Arial", 18), bg="orange", fg="white").pack(pady=20)

tab_control.pack(expand=1, fill="both")

# Start der Updates
update_system_tab()
update_network_tab()

root.mainloop()
