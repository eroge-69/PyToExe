import subprocess
import threading
import socket
import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

def get_local_subnet():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        parts = local_ip.split('.')
        return f"{parts[0]}.{parts[1]}.{parts[2]}"
    except:
        return "192.168.1"

def ping_ip(ip, results=None, index=None):
    try:
        result = subprocess.run(["ping", "-n", "1", str(ip)], capture_output=True, text=True)
        status = "Reachable" if "TTL=" in result.stdout else "Unreachable"
    except Exception as e:
        status = f"Error: {e}"
    if results is not None and index is not None:
        results[index] = (str(ip), status)
    return (str(ip), status)

def scan_ip_range(base_ip, start, end, output_box, scan_button, progress_var):
    output_box.delete(1.0, tk.END)
    scan_button.config(state=tk.DISABLED)
    progress_var.set(0)
    progress_bar["value"] = 0

    try:
        start = int(start)
        end = int(end)
        if not (0 <= start <= 255 and 0 <= end <= 255 and start <= end):
            raise ValueError("Invalid range")
    except ValueError:
        output_box.insert(tk.END, "❌ Invalid IP range. Use numbers between 0–255.\n")
        scan_button.config(state=tk.NORMAL)
        return

    ip_list = [f"{base_ip}.{i}" for i in range(start, end + 1)]
    total_ips = len(ip_list)
    results = [None] * total_ips

    def threaded_scan():
        threads = []
        for idx, ip in enumerate(ip_list):
            t = threading.Thread(target=ping_ip, args=(ip, results, idx))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        for idx, (ip, status) in enumerate(results):
            output_box.insert(tk.END, f"{ip:<15} {status}\n")
            output_box.see(tk.END)
            progress_var.set(idx + 1)
            progress_bar["value"] = ((idx + 1) / total_ips) * 100

        scan_button.config(state=tk.NORMAL)

    threading.Thread(target=threaded_scan).start()

def start_range_scan():
    base_ip = base_ip_entry.get().strip()
    start = start_entry.get().strip()
    end = end_entry.get().strip()
    scan_ip_range(base_ip, start, end, output_box, scan_button, progress_var)

def start_single_ping():
    ip = single_ip_entry.get().strip()
    if not ip:
        output_box.insert