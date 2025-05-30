import tkinter as tk
from tkinter import messagebox
import subprocess
import psutil
import threading
import time

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Fehler: {e}")

def disable_services():
    services = ["Fax", "wuauserv", "DiagTrack", "SysMain"]
    for svc in services:
        run_command(f"sc stop {svc}")
        run_command(f"sc config {svc} start= disabled")
    messagebox.showinfo("Fertig", "Dienste deaktiviert.")

def kill_tasks():
    tasks = ["OneDrive.exe", "Skype.exe", "Teams.exe"]
    for task in tasks:
        run_command(f"taskkill /f /im {task}")
    messagebox.showinfo("Fertig", "Prozesse beendet.")

def disable_autostarts():
    run_command('REG DELETE "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /va /f')
    run_command('REG DELETE "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /va /f')
    messagebox.showinfo("Fertig", "Autostarts gelöscht.")

def update_process_count():
    while True:
        count = len(psutil.pids())
        process_label.config(text=f"🧠 Aktive Prozesse: {count}")
        time.sleep(2)

# GUI
root = tk.Tk()
root.title("ICEOUT Service")
root.geometry("600x450")
root.configure(bg="#0b0f18")

title = tk.Label(root, text="ICEOUT", font=("Impact", 36), fg="#00ccff", bg="#0b0f18")
title.pack(pady=15)

btn1 = tk.Button(root, text="❄️ Dienste deaktivieren", command=disable_services, bg="#112233", fg="white", width=40, height=2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="🔥 Prozesse killen", command=kill_tasks, bg="#112233", fg="white", width=40, height=2)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="🚫 Autostarts entfernen", command=disable_autostarts, bg="#112233", fg="white", width=40, height=2)
btn3.pack(pady=10)

process_label = tk.Label(root, text="Aktive Prozesse: Lade...", fg="#00ccff", bg="#0b0f18", font=("Segoe UI", 12))
process_label.pack(pady=20)

threading.Thread(target=update_process_count, daemon=True).start()

root.mainloop()
