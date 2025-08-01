import tkinter as tk
from tkinter import ttk
import psutil
import GPUtil
import wmi
from datetime import datetime
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import requests
import csv
import os

# ========== CONFIG ==========
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/..."  # Paste your real webhook
CPU_ALERT_THRESHOLD = 90
ALERT_COOLDOWN_SECONDS = 300
# ============================

log_file = "pc_monitor_log.csv"
if not os.path.exists(log_file):
    with open(log_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Time", "CPU%", "RAM%", "Disk%", "Net Sent", "Net Recv", "CPU Temp", "GPU Load", "GPU Temp"])

last_alert_time = None
w = wmi.WMI(namespace="root\wmi")

def send_discord_alert(cpu_percent):
    global last_alert_time
    now = datetime.now()
    if last_alert_time and (now - last_alert_time).total_seconds() < ALERT_COOLDOWN_SECONDS:
        return
    last_alert_time = now
    msg = {
        "content": f"🚨 High CPU usage: {cpu_percent}% at {now.strftime('%H:%M:%S')}"
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=msg)
        print("[✅] Discord alert sent.")
    except Exception as e:
        print(f"[❌] Discord alert failed: {e}")

def get_cpu_temperature():
    try:
        temps = w.MSAcpi_ThermalZoneTemperature()
        if temps:
            temp = temps[0].CurrentTemperature
            return round((temp / 10 - 273.15), 1)  # Kelvin to Celsius
    except:
        pass
    return "N/A"

def get_gpu_info():
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]
            return gpu.name, gpu.load * 100, gpu.memoryUsed, gpu.memoryTotal, gpu.temperature
    except:
        pass
    return "N/A", 0, 0, 0, "N/A"

class PCMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🖥️ PC Monitor - GPU + Temp")
        self.root.geometry("700x600")
        self.cpu_data, self.ram_data, self.timestamps = [], [], []

        self.frame = ttk.Frame(root)
        self.frame.pack(pady=10)

        self.labels = {}
        keys = ["CPU", "RAM", "Disk", "Network", "Battery", "CPU Temp", "GPU", "GPU Load", "GPU Temp"]
        for i, key in enumerate(keys):
            ttk.Label(self.frame, text=key + ":").grid(row=i, column=0, sticky="w", padx=5, pady=4)
            val = ttk.Label(self.frame, text="Loading...", width=45)
            val.grid(row=i, column=1, sticky="w", padx=5)
            self.labels[key] = val

        self.fig = Figure(figsize=(6.5, 2.8), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.update_stats()

    def update_stats(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.timestamps.append(now)

        # CPU
        cpu = psutil.cpu_percent()
        self.cpu_data.append(cpu)
        self.labels["CPU"].config(text=f"{cpu}%")
        if cpu > CPU_ALERT_THRESHOLD:
            self.labels["CPU"].config(foreground="red")
            send_discord_alert(cpu)
        else:
            self.labels["CPU"].config(foreground="black")

        # RAM
        ram = psutil.virtual_memory().percent
        self.ram_data.append(ram)
        self.labels["RAM"].config(text=f"{ram}%")

        # Disk
        disk = psutil.disk_usage('/')
        self.labels["Disk"].config(text=f"{disk.percent}% used")

        # Network
        net = psutil.net_io_counters()
        sent = net.bytes_sent // (1024**2)
        recv = net.bytes_recv // (1024**2)
        self.labels["Network"].config(text=f"Sent: {sent} MB | Recv: {recv} MB")

        # Battery
        battery = psutil.sensors_battery()
        if battery:
            self.labels["Battery"].config(text=f"{battery.percent}% {'(Charging)' if battery.power_plugged else '(On Battery)'}")
        else:
            self.labels["Battery"].config(text="N/A")

        # Temps
        cpu_temp = get_cpu_temperature()
        self.labels["CPU Temp"].config(text=f"{cpu_temp}°C" if cpu_temp != "N/A" else "Unavailable")

        # GPU Info
        gpu_name, gpu_load, gpu_mem_used, gpu_mem_total, gpu_temp = get_gpu_info()
        self.labels["GPU"].config(text=gpu_name)
        self.labels["GPU Load"].config(text=f"{gpu_load:.1f}% - {gpu_mem_used}/{gpu_mem_total} MB")
        self.labels["GPU Temp"].config(text=f"{gpu_temp}°C" if gpu_temp != "N/A" else "Unavailable")

        # Graph
        self.cpu_data = self.cpu_data[-10:]
        self.ram_data = self.ram_data[-10:]
        self.timestamps = self.timestamps[-10:]
        self.ax.clear()
        self.ax.plot(self.timestamps, self.cpu_data, label="CPU %", color="red")
        self.ax.plot(self.timestamps, self.ram_data, label="RAM %", color="blue")
        self.ax.set_title("CPU & RAM Usage")
        self.ax.set_xticklabels(self.timestamps, rotation=45)
        self.ax.legend(loc="upper left")
        self.canvas.draw()

        # Log
        with open(log_file, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([now, cpu, ram, disk.percent, sent, recv, cpu_temp, gpu_load, gpu_temp])

        self.root.after(5000, self.update_stats)

if __name__ == "__main__":
    root = tk.Tk()
    app = PCMonitorApp(root)
    root.mainloop()
