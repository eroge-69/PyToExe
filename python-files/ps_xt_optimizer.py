import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import ctypes

# Check for admin rights
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    messagebox.showerror("Admin Rights Required", "Please run this script as Administrator.")
    exit()

# Commands dictionary: tweak label -> actual command
tweaks = {
    "Create Restore Point": "powershell -Command \"Checkpoint-Computer -Description 'PS XT Restore Point' -RestorePointType 'MODIFY_SETTINGS'\"",
    "Delete Temporary Files": "del /q/f/s %TEMP%\*",
    "Disable ConsumerFeatures": "reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager /v SubscribedContent-338393Enabled /t REG_DWORD /d 0 /f",
    "Disable Telemetry": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection /v AllowTelemetry /t REG_DWORD /d 0 /f",
    "Disable Activity History": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System /v PublishUserActivities /t REG_DWORD /d 0 /f",
    "Disable Explorer Auto Folder Discovery": "reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v AutoCheckSelect /t REG_DWORD /d 0 /f",
    "Disable GameDVR": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR /v AppCaptureEnabled /t REG_DWORD /d 0 /f",
    "Disable Hibernation": "powercfg -h off",
    "Disable Homegroup": "sc config HomeGroupListener start= disabled && sc config HomeGroupProvider start= disabled",
    "Disable Location Tracking": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors /v DisableLocation /t REG_DWORD /d 1 /f",
    "Disable Wifi-Sense": "reg add HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f",
    "Enable End Task With Right Click": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v ShowTaskViewButton /t REG_DWORD /d 1 /f",
    "Run Disk Cleanup": "cleanmgr /sagerun:1",
    "Change Terminal Default (PS7)": "reg add HKCU\\Console\\%SystemRoot%_system32_WindowsPowerShell_v1.0_powershell.exe /v ForceV2 /t REG_DWORD /d 1 /f",
    "Disable Copilot": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer /v ShowCopilotButton /t REG_DWORD /d 0 /f",
    "Add Ultimate Performance Plan": "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61",
    "Remove Ultimate Performance Plan": "powercfg -delete e9a42b02-d5df-448d-aa00-03f14749eb61"
}

# Main window
app = tk.Tk()
app.title("PS XT Optimizer")
app.geometry("1000x1000")
app.configure(bg='#8A2BE2')

# Canvas background with gradient
canvas = tk.Canvas(app, width=1000, height=1000)
canvas.pack(fill="both", expand=True)

grad_colors = ['#9400D3', '#4B0082', '#0000FF', '#00FF00', '#FFFF00', '#FF7F00', '#FF0000']
for i, color in enumerate(grad_colors):
    canvas.create_rectangle(0, i * 143, 1000, (i + 1) * 143, fill=color, outline=color)
canvas.create_text(500, 30, text="PS XT OPTIMIZER", fill="white", font=("Arial", 28, "bold"))

# Scrollable frame
main_frame = tk.Frame(canvas, bg='#8A2BE2')
main_frame.place(relx=0.5, rely=0.05, relwidth=0.9, relheight=0.85, anchor='n')

scroll_canvas = tk.Canvas(main_frame, bg='#8A2BE2')
scroll_frame = tk.Frame(scroll_canvas, bg='#8A2BE2')
scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=scroll_canvas.yview)
scroll_canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
scroll_canvas.pack(side="left", fill="both", expand=True)
scroll_canvas.create_window((0, 0), window=scroll_frame, anchor='nw')

# Update scroll region
def update_scroll(event):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

scroll_frame.bind("<Configure>", update_scroll)

# Checkbox dictionary
checkbox_vars = {}
for tweak_name in tweaks.keys():
    var = tk.BooleanVar()
    cb = ttk.Checkbutton(scroll_frame, text=tweak_name, variable=var)
    cb.pack(anchor='w', pady=2)
    checkbox_vars[tweak_name] = var

# Apply selected tweaks
def apply_selected():
    for tweak, var in checkbox_vars.items():
        if var.get():
            try:
                subprocess.run(tweaks[tweak], shell=True, check=True)
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to apply: {tweak}")
    messagebox.showinfo("Done", "Selected tweaks applied.")

# Apply button
ttk.Button(app, text="Apply Tweaks", command=apply_selected).place(relx=0.5, rely=0.95, anchor='s')

app.mainloop()
