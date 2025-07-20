import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Failed to execute: {command}")

def disable_cortana():
    run_command('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f')
    messagebox.showinfo("Done", "Cortana disabled.")

def remove_bloatware():
    apps = [
        "*3dbuilder*", "*zune*", "*solitaire*", "*bing*",
        "*people*", "*xbox*", "*getstarted*", "*skypeapp*", "*officehub*"
    ]
    for app in apps:
        run_command(f'powershell -Command "Get-AppxPackage {app} | Remove-AppxPackage"')
    messagebox.showinfo("Done", "Bloatware removed.")

def disable_telemetry():
    run_command('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f')
    run_command('sc stop DiagTrack')
    run_command('sc config DiagTrack start= disabled')
    messagebox.showinfo("Done", "Telemetry disabled.")

def disable_background_apps():
    run_command('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f')
    messagebox.showinfo("Done", "Background apps disabled.")

def apply_all():
    disable_cortana()
    remove_bloatware()
    disable_telemetry()
    disable_background_apps()
    messagebox.showinfo("All Done", "All tweaks applied.")

def main():
    root = tk.Tk()
    root.title("Var GUI Tweaker")
    root.geometry("350x300")
    root.resizable(False, False)

    tk.Label(root, text="VAR GUI TWEAKER", font=("Arial", 16, "bold")).pack(pady=10)

    tk.Button(root, text="Disable Cortana", command=disable_cortana, width=25).pack(pady=5)
    tk.Button(root, text="Remove Bloatware", command=remove_bloatware, width=25).pack(pady=5)
    tk.Button(root, text="Disable Telemetry", command=disable_telemetry, width=25).pack(pady=5)
    tk.Button(root, text="Disable Background Apps", command=disable_background_apps, width=25).pack(pady=5)
    tk.Button(root, text="Apply All Tweaks", command=apply_all, width=25, bg="green", fg="white").pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
