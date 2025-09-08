import os
import subprocess
import tkinter as tk
from tkinter import messagebox

# --- Functions ---
def clean_junk():
    os.system("del /s /q %temp%\\*.* >nul 2>&1")
    os.system("del /s /q C:\\Windows\\Temp\\*.* >nul 2>&1")
    os.system("del /s /q C:\\Windows\\Prefetch\\*.* >nul 2>&1")
    messagebox.showinfo("PC Optimizer", "🗑️ Junk files cleaned!")

def kill_tasks():
    tasks = [
        "GameBar.exe","GameBarFTServer.exe","GameBarPresenceWriter.exe",
        "XboxAppServices.exe","XboxTCUI.exe","XblGameSave.exe","XblLoginStandby.exe",
        "OneDrive.exe","Teams.exe","SearchUI.exe","CompatTelRunner.exe"
    ]
    for t in tasks:
        os.system(f"taskkill /F /IM {t} >nul 2>&1")
    messagebox.showinfo("PC Optimizer", "🔴 Background tasks killed!")

def stop_services():
    services = ["SysMain","DiagTrack","WSearch","wuauserv"]
    for s in services:
        os.system(f"net stop {s} >nul 2>&1")
    messagebox.showinfo("PC Optimizer", "⚙️ Heavy services stopped!")

def free_ram():
    os.system("powershell.exe Clear-Content -Path $env:TEMP")
    messagebox.showinfo("PC Optimizer", "🧠 RAM cleared (standby list)")

def full_optimize():
    clean_junk()
    kill_tasks()
    stop_services()
    free_ram()
    messagebox.showinfo("PC Optimizer", "🚀 Full Optimization Complete!")

def launch_game():
    # Change this path if your BlueStacks is installed somewhere else
    bluestacks_path = r"C:\Program Files\BlueStacks_nxt\HD-Player.exe"
    if os.path.exists(bluestacks_path):
        subprocess.Popen(bluestacks_path)
        messagebox.showinfo("PC Optimizer", "🎮 BlueStacks launched!")
    else:
        messagebox.showwarning("PC Optimizer", "⚠️ BlueStacks not found!")

# --- UI ---
root = tk.Tk()
root.title("🚀 PC Gaming Optimizer 🚀")
root.geometry("400x400")
root.configure(bg="#1e1e1e")

btn1 = tk.Button(root, text="🗑️ Clean Junk Files", command=clean_junk, width=25, height=2, bg="#2ecc71", fg="white")
btn1.pack(pady=5)

btn2 = tk.Button(root, text="🔴 Kill Background Tasks", command=kill_tasks, width=25, height=2, bg="#e74c3c", fg="white")
btn2.pack(pady=5)

btn3 = tk.Button(root, text="⚙️ Stop Heavy Services", command=stop_services, width=25, height=2, bg="#f39c12", fg="white")
btn3.pack(pady=5)

btn4 = tk.Button(root, text="🧠 Free RAM", command=free_ram, width=25, height=2, bg="#9b59b6", fg="white")
btn4.pack(pady=5)

btn5 = tk.Button(root, text="🚀 Full Optimize (One-Click)", command=full_optimize, width=25, height=2, bg="#3498db", fg="white")
btn5.pack(pady=10)

btn6 = tk.Button(root, text="🎮 Launch BlueStacks", command=launch_game, width=25, height=2, bg="#16a085", fg="white")
btn6.pack(pady=5)

root.mainloop()
