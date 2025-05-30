import tkinter as tk
from tkinter import messagebox
import subprocess
import psutil  # Für Prozessanzeige
import threading
import time

# Befehlsausführung
def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Fehler", f"Fehler bei: {command}")

# Dienste deaktivieren
def disable_services():
    services = ["Fax", "wuauserv", "DiagTrack", "SysMain", "WerSvc", "RetailDemo", "MapsBroker"]
    for svc in services:
        run_command(f"sc stop {svc}")
        run_command(f"sc config {svc} start= disabled")
    messagebox.showinfo("Erfolg", "Dienste wurden deaktiviert.")

# Prozesse killen
def kill_tasks():
    tasks = ["OneDrive.exe", "Skype.exe", "Teams.exe", "YourPhone.exe", "Cortana.exe", "SearchIndexer.exe"]
    for task in tasks:
        run_command(f"taskkill /f /im {task}")
    messagebox.showinfo("Erfolg", "Hintergrundprozesse wurden beendet.")

# Autostarts löschen
def disable_autostarts():
    run_command('REG DELETE "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /va /f')
    run_command('REG DELETE "HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" /va /f')
    messagebox.showinfo("Erfolg", "Autostarts wurden entfernt.")

# Prozesszähler
def update_process_count():
    while True:
        count = len(psutil.pids())
        process_label.config(text=f"🧠 Aktive Prozesse: {count}")
        time.sleep(2)

# GUI erstellen
root = tk.Tk()
root.title("ICEOUT SERVICE")
root.geometry("700x520")
root.configure(bg="#0b0f18")

# ICEOUT Titel
title = tk.Label(root, text="ICEOUT", font=("Impact", 48), fg="#00ccff", bg="#0b0f18")
title.pack(pady=15)

# Buttons
style = {"font": ("Segoe UI", 12, "bold"), "bg": "#112233", "fg": "#ffffff", "width": 40, "height": 2}

btn1 = tk.Button(root, text="❄️ Dienste deaktivieren", command=disable_services, **style)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="🔥 Hintergrundprozesse killen", command=kill_tasks, **style)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="🚫 Autostarts entfernen", command=disable_autostarts, **style)
btn3.pack(pady=10)

# Prozessanzahl (Live)
process_label = tk.Label(root, text="🧠 Aktive Prozesse: Lade...", font=("Segoe UI", 12), fg="#00ccff", bg="#0b0f18")
process_label.pack(pady=20)

# Footer
footer = tk.Label(root, text="ICEOUT SERVICE 2025 – All rights reserved", font=("Arial", 8), fg="#555", bg="#0b0f18")
footer.pack(side="bottom", pady=10)

# Starte Prozesszähler in extra Thread
threading.Thread(target=update_process_count, daemon=True).start()

root.mainloop()
