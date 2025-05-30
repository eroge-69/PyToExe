import tkinter as tk
from tkinter import messagebox
import subprocess
import psutil
import threading
import ctypes
import os
import time

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except:
        pass

def optimize_services():
    services = ["DiagTrack", "MapsBroker", "SysMain", "RetailDemo", "WSearch"]
    for svc in services:
        run_command(f"sc stop {svc}")
        run_command(f"sc config {svc} start= disabled")
    messagebox.showinfo("Done", "Dienste optimiert.")

def kill_background_tasks():
    tasks = ["YourPhone.exe", "Cortana.exe", "SkypeApp.exe", "OneDrive.exe"]
    for task in tasks:
        run_command(f"taskkill /f /im {task}")
    messagebox.showinfo("Done", "Tasks beendet.")

def clean_autostart():
    run_command('REG DELETE "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /va /f')
    run_command('REG DELETE "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /va /f')
    messagebox.showinfo("Done", "Autostarts bereinigt.")

def free_ram():
    for proc in psutil.process_iter(['pid']):
        try:
            ctypes.windll.psapi.EmptyWorkingSet(proc.info['pid'])
        except:
            continue
    messagebox.showinfo("Done", "RAM bereinigt.")

def enable_ultra_powerplan():
    run_command("powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61")
    run_command("powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61")
    messagebox.showinfo("Done", "Ultimate Performance aktiviert.")

def update_stats():
    while True:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        proc = len(psutil.pids())
        stat_label.config(text=f"🔥 CPU: {cpu}%   🧠 RAM: {ram}%   💻 Prozesse: {proc}")
        time.sleep(3)

# GUI Setup
root = tk.Tk()
root.title("ICEOUT SYSTEM BOOSTER")
root.geometry("700x500")
root.configure(bg="#10131a")

tk.Label(root, text="ICEOUT SYSTEM BOOSTER", font=("Impact", 36), fg="#00ccff", bg="#10131a").pack(pady=20)

style = {"font": ("Segoe UI", 12), "bg": "#112233", "fg": "#ffffff", "width": 40, "height": 2}

tk.Button(root, text="❄ Dienste optimieren", command=optimize_services, **style).pack(pady=7)
tk.Button(root, text="🔥 Hintergrund-Tasks beenden", command=kill_background_tasks, **style).pack(pady=7)
tk.Button(root, text="🚫 Autostarts löschen", command=clean_autostart, **style).pack(pady=7)
tk.Button(root, text="🧠 RAM optimieren", command=free_ram, **style).pack(pady=7)
tk.Button(root, text="⚡ Ultimate Performance aktivieren", command=enable_ultra_powerplan, **style).pack(pady=7)

stat_label = tk.Label(root, text="Live-Daten werden geladen...", font=("Consolas", 12), bg="#10131a", fg="#00ffcc")
stat_label.pack(pady=20)

threading.Thread(target=update_stats, daemon=True).start()

root.mainloop()
