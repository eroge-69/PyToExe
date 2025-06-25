
import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import ctypes
import threading
import time

# Ensure script is running as admin
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Core optimization functions
def apply_selected():
    for key, var in vars_dict.items():
        if var.get():
            func = optimizations.get(key)
            if func:
                func()
    messagebox.showinfo("Done", "Selected optimizations applied.")

def revert_selected():
    for key, var in vars_dict.items():
        if var.get():
            func = reverts.get(key)
            if func:
                func()
    messagebox.showinfo("Done", "Selected changes reverted.")

# Placeholder optimization commands
def disable_startup_apps():
    subprocess.run('powershell "Get-CimInstance -ClassName Win32_StartupCommand | Remove-CimInstance"', shell=True)

def high_perf_power_plan():
    subprocess.run('powercfg -setactive SCHEME_MIN', shell=True)

def kill_indexing():
    subprocess.run('sc stop "WSearch" && sc config "WSearch" start=disabled', shell=True)

def disable_onedrive():
    subprocess.run('taskkill /f /im OneDrive.exe', shell=True)
    subprocess.run('%SystemRoot%\System32\OneDriveSetup.exe /uninstall', shell=True)

def disable_telemetry():
    subprocess.run('sc stop DiagTrack && sc config DiagTrack start= disabled', shell=True)

def fixed_pagefile():
    subprocess.run('wmic computersystem where name="%computername%" set AutomaticManagedPagefile=False', shell=True)
    subprocess.run('wmic pagefileset where name="C:\\pagefile.sys" set InitialSize=4096,MaximumSize=6144', shell=True)

def debloat_edge():
    subprocess.run('powershell "Get-AppxPackage *Microsoft.MicrosoftEdge.Stable* | Remove-AppxPackage"', shell=True)

def limit_windows_security_ram():
    subprocess.run('powershell "Set-MpPreference -DisableRealtimeMonitoring $true"', shell=True)

def disable_useless_services():
    for service in ['Fax', 'MapsBroker', 'RetailDemo']:
        subprocess.run(f'sc config "{service}" start= disabled', shell=True)

def clear_temp():
    subprocess.run('del /q/f/s %TEMP%\*', shell=True)

def clear_prefetch():
    subprocess.run('del /q/f/s C:\Windows\Prefetch\*', shell=True)

def empty_recycle_bin():
    subprocess.run('PowerShell -Command "$Shell = New-Object -ComObject Shell.Application; $Shell.Namespace(0xA).Items() | ForEach-Object {Remove-Item $_.Path -Recurse -Force}"', shell=True)

def disable_sysmain():
    subprocess.run('sc stop "SysMain" && sc config "SysMain" start=disabled', shell=True)

def disable_hibernate():
    subprocess.run('powercfg -h off', shell=True)

def turn_off_tips():
    subprocess.run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager" /v SubscribedContent-338389Enabled /t REG_DWORD /d 0 /f', shell=True)

def disable_updates_except_security():
    subprocess.run('sc config wuauserv start= demand', shell=True)

def disable_xbox_etc():
    subprocess.run('powershell "Get-AppxPackage *xbox* | Remove-AppxPackage"', shell=True)

def remove_cortana():
    subprocess.run('powershell "Get-AppxPackage *Microsoft.549981C3F5F10* | Remove-AppxPackage"', shell=True)

# Define optimization and revert dictionaries
optimizations = {
    "disable_startup_apps": disable_startup_apps,
    "high_perf_power_plan": high_perf_power_plan,
    "kill_indexing": kill_indexing,
    "disable_onedrive": disable_onedrive,
    "disable_telemetry": disable_telemetry,
    "fixed_pagefile": fixed_pagefile,
    "debloat_edge": debloat_edge,
    "limit_windows_security_ram": limit_windows_security_ram,
    "disable_useless_services": disable_useless_services,
    "clear_temp": clear_temp,
    "clear_prefetch": clear_prefetch,
    "empty_recycle_bin": empty_recycle_bin,
    "disable_sysmain": disable_sysmain,
    "disable_hibernate": disable_hibernate,
    "turn_off_tips": turn_off_tips,
    "disable_updates_except_security": disable_updates_except_security,
    "disable_xbox_etc": disable_xbox_etc,
    "remove_cortana": remove_cortana
}

# Placeholder for revert functions
reverts = {key: lambda: print(f"Revert not implemented: {key}") for key in optimizations}

# GUI setup
root = tk.Tk()
root.title("Farabi's Optimizer - Lite")
root.geometry("550x650")
root.config(bg="#f5f5f5")

header = tk.Label(root, text="🧪 Vivobook Optimization Menu", font=("Helvetica", 16, "bold"), bg="#f5f5f5", pady=10)
header.pack()

frame = tk.Frame(root, bg="#f5f5f5")
frame.pack()

vars_dict = {}

for key in optimizations:
    var = tk.BooleanVar()
    chk = tk.Checkbutton(frame, text=key.replace("_", " ").capitalize(), variable=var, bg="#f5f5f5")
    chk.pack(anchor='w')
    vars_dict[key] = var

apply_btn = tk.Button(root, text="Apply Selected", command=apply_selected, bg="#4caf50", fg="white", font=("Helvetica", 12))
apply_btn.pack(pady=10)

revert_btn = tk.Button(root, text="Revert Selected", command=revert_selected, bg="#e53935", fg="white", font=("Helvetica", 12))
revert_btn.pack(pady=10)

# Auto reapply every 2 minutes
def auto_reapply():
    while True:
        time.sleep(120)
        for key, var in vars_dict.items():
            if var.get():
                func = optimizations.get(key)
                if func:
                    func()

threading.Thread(target=auto_reapply, daemon=True).start()

# Ensure admin access
if not is_admin():
    messagebox.showerror("Admin Required", "Please run this script as administrator.")
    root.destroy()

root.mainloop()
