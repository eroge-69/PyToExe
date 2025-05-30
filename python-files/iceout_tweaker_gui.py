import os
import subprocess
import tkinter as tk
from tkinter import messagebox

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Fehler", f"Befehl fehlgeschlagen: {command}")

def optimize_ram():
    run_command("EmptyStandbyList.exe workingsets")
    run_command("EmptyStandbyList.exe standbylist")

def clean_temp():
    run_command("del /f /s /q %temp%\*")
    run_command("del /f /s /q C:\\Windows\\Temp\\*")

def clean_autostart():
    run_command('reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /f')

def disable_services():
    run_command("sc config DiagTrack start= disabled")
    run_command("sc config WSearch start= disabled")
    run_command("sc config SysMain start= disabled")

def high_perf_mode():
    run_command("powercfg -setactive SCHEME_MIN")

def tweak_network():
    run_command("netsh int tcp set global autotuninglevel=highlyrestricted")
    run_command("netsh int tcp set global chimney=enabled")
    run_command("netsh int tcp set global rss=enabled")

def run_all():
    optimize_ram()
    clean_temp()
    clean_autostart()
    disable_services()
    high_perf_mode()
    tweak_network()
    messagebox.showinfo("Erfolg", "PC wurde erfolgreich optimiert!")

root = tk.Tk()
root.title("ICE OUT FPS-Booster")
root.geometry("400x400")
root.config(bg="#111111")

title = tk.Label(root, text="ICE OUT Tweaker Pro", font=("Helvetica", 16, "bold"), fg="cyan", bg="#111111")
title.pack(pady=10)

btn_all = tk.Button(root, text="🧊 Alles optimieren", font=("Helvetica", 12), command=run_all, bg="cyan", fg="black")
btn_all.pack(pady=10)

btn_ram = tk.Button(root, text="💾 RAM leeren", command=optimize_ram, width=25)
btn_ram.pack(pady=5)
btn_temp = tk.Button(root, text="🧹 Temp-Dateien löschen", command=clean_temp, width=25)
btn_temp.pack(pady=5)
btn_auto = tk.Button(root, text="🚫 Autostart säubern", command=clean_autostart, width=25)
btn_auto.pack(pady=5)
btn_services = tk.Button(root, text="❌ Dienste deaktivieren", command=disable_services, width=25)
btn_services.pack(pady=5)
btn_perf = tk.Button(root, text="⚡ High Performance aktivieren", command=high_perf_mode, width=25)
btn_perf.pack(pady=5)
btn_net = tk.Button(root, text="🌐 Netzwerk verbessern", command=tweak_network, width=25)
btn_net.pack(pady=5)

root.mainloop()
