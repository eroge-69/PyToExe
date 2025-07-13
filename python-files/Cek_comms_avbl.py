import socket
import psutil
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk

def get_ip_addresses():
    results = []
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    
    for interface_name, interface_addresses in addrs.items():
        if stats.get(interface_name) and stats[interface_name].isup:
            results.append(f"Interface: {interface_name}")
            for address in interface_addresses:
                if address.family == socket.AF_INET:
                    results.append(f"  IPv4: {address.address}")
                elif address.family == socket.AF_INET6:
                    results.append(f"  IPv6: {address.address}")
    if not results:
        results.append("Teu aya interface nu aktif.")
    return "\n".join(results)

def get_serial_ports():
    results = []
    ports = serial.tools.list_ports.comports()
    if not ports:
        results.append("Teu aya COM port nu kapanggih.")
    for port in ports:
        results.append(f"{port.device} - {port.description}")
    return "\n".join(results)

def update_info():
    ip_text = get_ip_addresses()
    com_text = get_serial_ports()
    ip_label.config(text=ip_text)
    com_label.config(text=com_text)
    root.after(1000, update_info)  # Update tiap 1000ms (1 detik)

# GUI setup
root = tk.Tk()
root.title("IP Address & COM Port Monitor")
root.geometry("600x500")

title_label = ttk.Label(root, text="🖧 IP & Serial Port Monitor", font=("Helvetica", 16, "bold"))
title_label.pack(pady=10)

ip_label = ttk.Label(root, text="", font=("Courier", 10), justify="left")
ip_label.pack(padx=10, pady=10, anchor="w")

com_title = ttk.Label(root, text="🔌 COM Ports:", font=("Helvetica", 12, "bold"))
com_title.pack(pady=5, anchor="w", padx=10)

com_label = ttk.Label(root, text="", font=("Courier", 10), justify="left")
com_label.pack(padx=10, pady=5, anchor="w")

update_info()  # Mimitian update otomatis
root.mainloop()
