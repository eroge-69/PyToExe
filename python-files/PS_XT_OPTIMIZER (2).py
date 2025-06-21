import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import ctypes
import sys

# Ensure the script runs with administrator privileges
def run_as_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, ' '.join(sys.argv), None, 1)
        sys.exit()

run_as_admin()

# Define all tweak commands
tweaks = {
    # Essential Tweaks
    "Create Restore Point": "powershell -Command \"Checkpoint-Computer -Description 'PS XT Restore Point' -RestorePointType 'MODIFY_SETTINGS'\"",
    "Delete Temporary Files": "del /q/f/s %TEMP%\\*",
    "Disable ConsumerFeatures": "reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\ContentDeliveryManager /v SubscribedContent-338393Enabled /t REG_DWORD /d 0 /f",
    "Disable Telemetry": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection /v AllowTelemetry /t REG_DWORD /d 0 /f",
    "Disable Activity History": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System /v PublishUserActivities /t REG_DWORD /d 0 /f",
    "Disable Explorer Automatic Folder Discovery": "reg add HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v AutoCheckSelect /t REG_DWORD /d 0 /f",
    "Disable GameDVR": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\GameDVR /v AppCaptureEnabled /t REG_DWORD /d 0 /f",
    "Disable Hibernation": "powercfg -h off",
    "Disable Homegroup": "sc config HomeGroupListener start= disabled && sc config HomeGroupProvider start= disabled",
    "Disable Location Tracking": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\LocationAndSensors /v DisableLocation /t REG_DWORD /d 1 /f",
    "Disable Storage Sense": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense /v AllowStorageSenseGlobal /t REG_DWORD /d 0 /f",
    "Disable Wifi-Sense": "reg add HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f",
    "Enable End Task With Right Click": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v ShowTaskViewButton /t REG_DWORD /d 1 /f",
    "Run Disk Cleanup": "cleanmgr /sagerun:1",
    "Change Terminal Default": "reg add HKCU\\Console\\%SystemRoot%_system32_WindowsPowerShell_v1.0_powershell.exe /v ForceV2 /t REG_DWORD /d 1 /f",
    "Disable Powershell 7 Telemetry": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Telemetry /v DisableTelemetry /t REG_DWORD /d 1 /f",
    "Disable Recall": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System /v DisableAIDataAnalysis /t REG_DWORD /d 1 /f",
    "Set Hibernation as Default": "powercfg -hibernate on",
    "Set Services to Manual": "sc config wuauserv start= demand",
    "Debloat Edge": "powershell -Command \"Get-AppxPackage *Microsoft.MicrosoftEdge* | Remove-AppxPackage\"",

    # Advanced Tweaks
    "Adobe Network Block": "netsh advfirewall firewall add rule name=\"Block Adobe\" dir=out action=block program=\"%ProgramFiles%\\Adobe\\*\" enable=yes",
    "Adobe Debloat": "powershell -Command \"Get-AppxPackage *Adobe* | Remove-AppxPackage\"",
    "Disable IPv6": "reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters /v DisabledComponents /t REG_DWORD /d 255 /f",
    "Prefer IPv4 over IPv6": "reg add HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters /v DisabledComponents /t REG_DWORD /d 32 /f",
    "Disable Teredo": "netsh interface teredo set state disabled",
    "Disable Background Apps": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications /v GlobalUserDisabled /t REG_DWORD /d 1 /f",
    "Disable Fullscreen Optimizations": "reg add HKCU\\System\\GameConfigStore /v GameDVR_FSEBehaviorMode /t REG_DWORD /d 2 /f",
    "Disable Microsoft Copilot": "reg add HKCU\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f",
    "Disable Intel MM (vPro LMS)": "sc config LMS start= disabled",
    "Disable Notification Tray/Calendar": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer /v HideClock /t REG_DWORD /d 1 /f",
    "Disable WPBT": "reg add HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management /v DisableWPBTExecution /t REG_DWORD /d 1 /f",
    "Set Display for Performance": "SystemPropertiesPerformance.exe",
    "Set Classic Right-Click Menu": "reg add HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32 /f /ve",
    "Set Time to UTC": "reg add HKLM\\SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation /v RealTimeIsUniversal /t REG_DWORD /d 1 /f",
    "Remove ALL MS Store Apps": "powershell -Command \"Get-AppxPackage | Remove-AppxPackage\"",
    "Remove Microsoft Edge": "powershell -Command \"Get-AppxPackage *Microsoft.MicrosoftEdge* | Remove-AppxPackage\"",
    "Remove Home and Gallery from Explorer": "reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced /v ShowGallery /t REG_DWORD /d 0 /f",
    "Remove OneDrive": "powershell -Command \"Get-AppxPackage *OneDrive* | Remove-AppxPackage\"",
    "Block Razer Software Installs": "reg add HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DeviceInstall\\Restrictions /v DenyDeviceIDs /t REG_MULTI_SZ /d USB\\VID_1532&PID_007A /f",

    # Performance Plans
    "Add and Activate Ultimate Performance Profile": "powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61",
    "Remove Ultimate Performance Profile": "powercfg -delete e9a42b02-d5df-448d-aa00-03f14749eb61"
}

# Main window
app = tk.Tk()
app.title("PS XT OPTIMIZER")
app.geometry("640x480")
app.configure(bg='black')

# Title
title_label = tk.Label(app, text="PS XT OPTIMIZER", bg="black", fg="white", font=("Arial", 20, "bold"))
title_label.pack(pady=10)

# Frame with scroll
frame = tk.Frame(app, bg="black")
frame.pack(fill="both", expand=True, padx=10, pady=10)
canvas = tk.Canvas(frame, bg="black")
scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
scroll_frame = tk.Frame(canvas, bg="black")

scroll_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Checkboxes
checkbox_vars = {}
for tweak in tweaks:
    var = tk.BooleanVar()
    chk = ttk.Checkbutton(scroll_frame, text=tweak, variable=var)
    chk.pack(anchor="w", pady=2)
    checkbox_vars[tweak] = var

# Apply selected tweaks
def apply_selected():
    for name, var in checkbox_vars.items():
        if var.get():
            try:
                subprocess.run(tweaks[name], shell=True, check=True)
            except subprocess.CalledProcessError:
                messagebox.showerror("Error", f"Failed to apply: {name}")
    messagebox.showinfo("Done", "Selected tweaks applied successfully.")

# Apply button
apply_btn = ttk.Button(app, text="Apply Tweaks", command=apply_selected)
apply_btn.pack(pady=10)

app.mainloop()
