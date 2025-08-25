import subprocess
import threading
import tkinter as tk
from tkinter import scrolledtext, ttk

def ping_ip(ip, results=None, index=None):
    try:
        result = subprocess.run(["ping", "-n", "1", str(ip)], capture_output=True, text=True)
        status = "✅ Reachable" if "TTL=" in result.stdout else "❌ Unreachable"
    except Exception as e:
        status = f"❌ Error: {e}"
    if results is not None and index is not None:
        results[index] = f"{str(ip):<15} {status}"
    return f"{str(ip):<15} {status}"

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

        for idx, result in enumerate(results):
            output_box.insert(tk.END, result + "\n")
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
        output_box.insert(tk.END, "❌ Please enter a valid IP address.\n")
        return

    output_box.insert(tk.END, f"Pinging {ip}...\n")
    result = ping_ip(ip)
    output_box.insert(tk.END, result + "\n")
    output_box.see(tk.END)

# 🖼️ GUI Setup
window = tk.Tk()
window.title("IP Scanner")
window.geometry("600x580")

# 🔹 Single IP Ping Section
tk.Label(window, text="Ping Single IP (e.g. 8.8.8.8):").pack(pady=5)
single_ip_entry = tk.Entry(window, width=30)
single_ip_entry.pack(pady=5)
tk.Button(window, text="Ping IP", command=start_single_ping).pack(pady=5)

# 🔹 IP Range Scan Section
tk.Label(window, text="Base IP (e.g. 192.168.1)").pack(pady=5)
base_ip_entry = tk.Entry(window, width=30)
base_ip_entry.pack(pady=5)

tk.Label(window, text="Start Range (e.g. 1)").pack(pady=5)
start_entry = tk.Entry(window, width=10)
start_entry.pack(pady=5)

tk.Label(window, text="End Range (e.g. 4)").pack(pady=5)
end_entry = tk.Entry(window, width=10)
end_entry.pack(pady=5)

scan_button = tk.Button(window, text="Scan Range", command=start_range_scan)
scan_button.pack(pady=10)

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(window, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, padx=20, pady=5)

output_box = scrolledtext.ScrolledText(window, width=70, height=20)
output_box.pack(pady=10)

window.mainloop()