import tkinter as tk
from tkinter import filedialog
import wmi
import psutil
import cpuinfo
import GPUtil
import platform
import socket
from datetime import datetime

c = wmi.WMI()

def get_system_info():
    info = {}

    # SYSTEM
    info["SYSTEM"] = {
        "Hostname": socket.gethostname(),
        "OS": f"{platform.system()} {platform.release()} ({platform.version()})",
        "Architecture": platform.architecture()[0],
        "Boot Time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")
    }

    # CPU
    cpu = cpuinfo.get_cpu_info()
    info["CPU"] = {
        "Name": cpu['brand_raw'],
        "Physical Cores": psutil.cpu_count(logical=False),
        "Threads": psutil.cpu_count(logical=True),
        "Frequency": f"{psutil.cpu_freq().current:.2f} MHz",
        "Usage Per Core": ", ".join([f"{i}={x}%" for i,x in enumerate(psutil.cpu_percent(percpu=True, interval=1))]),
        "Total Usage": f"{psutil.cpu_percent()}%"
    }

    # GPU
    gpus = GPUtil.getGPUs()
    gpu_info = []
    if gpus:
        for i, gpu in enumerate(gpus):
            gpu_info.append(f"{gpu.name}, Memory: {gpu.memoryTotal}MB, Load: {gpu.load*100:.2f}%, Temp: {gpu.temperature}°C")
    else:
        gpu_info.append("N/A")
    info["GPU"] = gpu_info

    # Motherboard
    for board in c.Win32_BaseBoard():
        info["Motherboard"] = f"{board.Manufacturer} {board.Product}"

    # RAM
    ram_modules = []
    for mem in c.Win32_PhysicalMemory():
        ram_modules.append(f"{mem.DeviceLocator}: {int(mem.Capacity)/(1024**3):.2f}GB {mem.Speed}MHz {mem.Manufacturer}")
    ram = psutil.virtual_memory()
    info["RAM"] = {
        "Total": f"{ram.total / (1024**3):.2f} GB",
        "Usage": f"{ram.percent}%",
        "Modules": ram_modules
    }

    # Storage
    disks = []
    for disk in c.Win32_DiskDrive():
        disks.append(f"{disk.Caption}: {disk.Model}, {int(disk.Size)/(1024**3):.2f}GB, {disk.InterfaceType}")
    info["Storage"] = disks

    # Network Adapters (including Wi-Fi)
    network = []
    for nic in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
        network.append(f"{nic.Description}: IP={nic.IPAddress[0]}, MAC={nic.MACAddress}")
    info["Network"] = network

    # Other devices (optional, like sound cards, optical drives, Wi-Fi cards)
    other_devices = []
    for dev in c.Win32_PnPEntity():
        if dev.Description and dev.PNPClass not in ["System", "Processor", "MemoryController", "DiskDrive", "Display", "Network", "BaseBoard"]:
            other_devices.append(f"{dev.PNPClass}: {dev.Description}")
    info["Other Devices"] = other_devices if other_devices else ["None detected"]

    # Battery
    battery = {}
    if hasattr(psutil, "sensors_battery"):
        bat = psutil.sensors_battery()
        if bat:
            battery["Percent"] = f"{bat.percent}%"
            battery["Charging"] = bat.power_plugged
    info["Battery"] = battery if battery else "N/A"

    # PSU
    info["PSU"] = "Not detectable via software"

    return info

def display_info():
    data = get_system_info()
    text_box.config(state="normal")
    text_box.delete(1.0, tk.END)

    # Clear all previous tags
    text_box.tag_remove("main", "1.0", tk.END)

    for section, details in data.items():
        text_box.insert(tk.END, f"===== {section} =====\n", "main")
        if isinstance(details, dict):
            for k, v in details.items():
                if isinstance(v, list):
                    text_box.insert(tk.END, f"{k}:\n")
                    for item in v:
                        text_box.insert(tk.END, f"  - {item}\n")
                else:
                    text_box.insert(tk.END, f"{k}: {v}\n")
        elif isinstance(details, list):
            for item in details:
                text_box.insert(tk.END, f"{item}\n")
        else:
            text_box.insert(tk.END, f"{details}\n")
        text_box.insert(tk.END, "\n")

    text_box.config(state="disabled")

def save_info():
    data = get_system_info()
    file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")])
    if file_path:
        with open(file_path, "w") as f:
            for section, details in data.items():
                f.write(f"===== {section} =====\n")
                if isinstance(details, dict):
                    for k, v in details.items():
                        if isinstance(v, list):
                            f.write(f"{k}:\n")
                            for item in v:
                                f.write(f"  - {item}\n")
                        else:
                            f.write(f"{k}: {v}\n")
                elif isinstance(details, list):
                    for item in details:
                        f.write(f"{item}\n")
                else:
                    f.write(f"{details}\n")
                f.write("\n")

def change_font_size():
    size = font_size_var.get()
    text_box.config(font=("Consolas", size))

root = tk.Tk()
root.title("Full PC Specs Viewer")
root.geometry("900x700")
root.configure(bg="#1e1e1e")

# Settings
font_size_var = tk.IntVar(value=12)
settings_frame = tk.Frame(root, bg="#1e1e1e")
settings_frame.pack(fill="x", pady=5)
tk.Label(settings_frame, text="Font Size:", bg="#1e1e1e", fg="white").pack(side="left", padx=5)
tk.Spinbox(settings_frame, from_=8, to=32, textvariable=font_size_var, command=change_font_size, width=5).pack(side="left")

# Text box
text_box = tk.Text(root, bg="#2e2e2e", fg="white", font=("Consolas", 12))
text_box.pack(expand=True, fill="both", padx=5, pady=5)
text_box.config(state="disabled")

# Highlight main headings
text_box.tag_configure("main", foreground="cyan", font=("Consolas", 12, "bold"))

# Buttons
button_frame = tk.Frame(root, bg="#1e1e1e")
button_frame.pack(fill="x", pady=5)
tk.Button(button_frame, text="Refresh Info", command=display_info, bg="#3e3e3e", fg="white").pack(side="left", padx=5)
tk.Button(button_frame, text="Download All", command=save_info, bg="#3e3e3e", fg="white").pack(side="left", padx=5)

display_info()
root.mainloop()
