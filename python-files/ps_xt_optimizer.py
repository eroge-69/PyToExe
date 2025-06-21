import customtkinter as ctk
import subprocess
import tkinter.messagebox as messagebox
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("PS XT OPTIMIZER")
app.geometry("650x700")

frame = ctk.CTkScrollableFrame(app, width=620, height=600)
frame.pack(padx=10, pady=10)

# Tweak options with real commands
tweaks = {
    "Create Restore Point": 'powershell -command "Checkpoint-Computer -Description \\"PS XT Optimizer\\" -RestorePointType \\"MODIFY_SETTINGS\\""',
    "Delete Temporary Files": 'del /s /q "%temp%\\*"',
    "Disable ConsumerFeatures": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\CloudContent" /v DisableConsumerFeatures /t REG_DWORD /d 1 /f',
    "Disable Telemetry": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f',
    "Disable Activity History": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\System" /v EnableActivityFeed /t REG_DWORD /d 0 /f',
    "Disable Explorer Automatic Folder Discovery": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v AutoExpandDLs /t REG_DWORD /d 0 /f',
    "Disable GameDVR": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\GameDVR" /v AllowGameDVR /t REG_DWORD /d 0 /f',
    "Disable Hibernation": "powercfg -h off",
    "Disable Homegroup": 'sc config HomeGroupListener start= disabled & sc config HomeGroupProvider start= disabled',
    "Disable Location Tracking": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\lfsvc\\Service\\Configuration" /v Status /t REG_DWORD /d 0 /f',
    "Disable Storage Sense": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\StorageSense\\Parameters\\StoragePolicy" /v 01 /t REG_DWORD /d 0 /f',
    "Disable Wifi-Sense": 'reg add "HKLM\\SOFTWARE\\Microsoft\\WcmSvc\\wifinetworkmanager\\config" /v AutoConnectAllowedOEM /t REG_DWORD /d 0 /f',
    "Enable End Task With Right Click": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v ShowTaskManager /t REG_DWORD /d 1 /f',
    "Run Disk Cleanup": "cleanmgr /sagerun:1",
    "Change Windows Terminal default": 'reg add "HKCU\\Console" /v ForceV2 /t REG_DWORD /d 1 /f',
    "Disable Powershell 7 Telemetry": 'reg add "HKCU\\SOFTWARE\\Microsoft\\PowerShell\\Core\\Telemetry" /v Enabled /t REG_DWORD /d 0 /f',
    "Disable Recall": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsAI" /v DisableAIRecall /t REG_DWORD /d 1 /f',
    "Set Hibernation default (Laptop)": "powercfg /hibernate on",
    "Set Services to Manual": 'sc config DiagTrack start= demand',
    "Debloat Edge": 'powershell -command "Get-AppxPackage *Microsoft.MicrosoftEdge.Stable* | Remove-AppxPackage"',
    "Adobe Network Block": 'netsh advfirewall firewall add rule name="Block Adobe" dir=out action=block program="C:\\Program Files\\Adobe\\*" enable=yes',
    "Adobe Debloat": 'powershell -command "Get-AppxPackage *Adobe* | Remove-AppxPackage"',
    "Disable IPv6": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 255 /f',
    "Prefer IPv4 over IPv6": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Services\\Tcpip6\\Parameters" /v DisabledComponents /t REG_DWORD /d 32 /f',
    "Disable Teredo": 'netsh interface teredo set state disabled',
    "Disable Background Apps": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f',
    "Disable Fullscreen Optimizations": 'reg add "HKCU\\System\\GameConfigStore" /v GameDVR_FSEBehavior /t REG_DWORD /d 2 /f',
    "Disable Microsoft Copilot": 'reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f',
    "Disable Intel MM (vPro LMS)": 'sc config LMS start= disabled',
    "Disable Notification Tray/Calendar": 'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\Explorer" /v HideClock /t REG_DWORD /d 1 /f',
    "Disable WPBT": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Memory Management" /v DisablePagingExecutive /t REG_DWORD /d 1 /f',
    "Set Display for Performance": 'rundll32.exe advapi32.dll,ProcessIdleTasks',
    "Set Classic Right-Click Menu": 'reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}" /f & reg add "HKCU\\Software\\Classes\\CLSID\\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\\InprocServer32" /f',
    "Set Time to UTC (Dual Boot)": 'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\TimeZoneInformation" /v RealTimeIsUniversal /t REG_DWORD /d 1 /f',
    "Remove ALL MS Store Apps": 'powershell -command "Get-AppxPackage | Remove-AppxPackage"',
    "Remove Microsoft Edge": 'powershell -command "Get-AppxPackage *Microsoft.MicrosoftEdge* | Remove-AppxPackage"',
    "Remove Home and Gallery from explorer": 'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Advanced" /v ShowHomeButton /f',
    "Remove OneDrive": '%SystemRoot%\\SysWOW64\\OneDriveSetup.exe /uninstall',
    "Block Razer Software Installs": 'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Device Metadata" /v PreventDeviceMetadataFromNetwork /t REG_DWORD /d 1 /f',
    "Add Ultimate Performance Profile": 'powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61',
    "Remove Ultimate Performance Profile": 'powercfg -delete e9a42b02-d5df-448d-aa00-03f14749eb61'
}

checkboxes = {}

# Create checkbox for each tweak
for tweak in tweaks:
    cb = ctk.CTkCheckBox(frame, text=tweak)
    cb.pack(anchor="w")
    checkboxes[tweak] = cb

# Apply button logic
def apply_tweaks():
    selected = [key for key, box in checkboxes.items() if box.get() == 1]
    if not selected:
        messagebox.showinfo("No Tweaks Selected", "Please select at least one tweak.")
        return

    success = []
    failed = []

    for tweak in selected:
        try:
            subprocess.run(tweaks[tweak], shell=True, check=True)
            success.append(tweak)
        except:
            failed.append(tweak)

    # Show popup result
    msg = ""
    if success:
        msg += f"✅ Applied:\n" + "\n".join(success) + "\n\n"
    if failed:
        msg += f"❌ Failed:\n" + "\n".join(failed)
    messagebox.showinfo("Tweaks Applied", msg)

    # Restart prompt
    if messagebox.askyesno("Restart", "Some changes may require a restart. Restart now?"):
        os.system("shutdown /r /t 0")

# Apply Button
ctk.CTkButton(app, text="Apply Selected Tweaks", command=apply_tweaks).pack(pady=10)

app.mainloop()
