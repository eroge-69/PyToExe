```python
import os
import subprocess
import ctypes
import sys
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import json
import wmi

# HWID generation (using motherboard serial number)
def get_hwid():
    try:
        c = wmi.WMI()
        for board in c.Win32_BaseBoard():
            return board.SerialNumber.strip() or "unknown_hwid"
    except:
        return "unknown_hwid"

# Predefined owner HWID (replace with your motherboard serial number after running once)
OWNER_HWID = "your_hwid_here"  # Run the script to get your HWID and replace this

# Check if running as administrator
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# Elevate privileges if not admin
def run_as_admin():
    if not is_admin():
        messagebox.showwarning("Admin Required", "This script requires administrative privileges. Attempting to elevate...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# Load users from JSON file
def load_users():
    users_file = "users.json"
    default_users = {"admin": "cleanup123"}  # Default user
    if os.path.exists(users_file):
        try:
            with open(users_file, "r") as f:
                return json.load(f)
        except:
            return default_users
    else:
        with open(users_file, "w") as f:
            json.dump(default_users, f)
        return default_users

# Save users to JSON file
def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

# Full Bypass cleanup function
def full_bypass():
    commands = [
        'reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU" /va /f',
        'for /f "tokens=*" %G in (\'wevtutil el\') do wevtutil cl "%G"',
        'vssadmin delete shadows /all /quiet',
        'for /f "tokens=2 delims= " %a in (\'cmdkey /list ^| findstr Target\') do cmdkey /delete %a',
        'del /s /q "%LOCALAPPDATA%\\D3DSCache\\*.*"',
        'net stop WSearch',
        'del /s /q "C:\\ProgramData\\Microsoft\\Search\\Data\\Applications\\Windows\\*.*"',
        'net start WSearch',
        'taskkill /f /im explorer.exe',
        'del /s /q "%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db"',
        'start explorer.exe',
        'net stop wuauserv',
        'net stop bits',
        'del /s /q "C:\\Windows\\SoftwareDistribution\\*.*"',
        'net start bits',
        'net start wuauserv',
        'del /s /q "C:\\ProgramData\\Microsoft\\Windows\\WER\\*.*"',
        'del /s /q "C:\\Windows\\Prefetch\\*.*"',
        'del /s /q "C:\\Windows\\*.dmp"',
        'del /s /q "%LOCALAPPDATA%\\CrashDumps\\*.*"',
        'netsh wlan delete profile name=*',
        'WSReset.exe',
        'RunDll32.exe InetCpl.cpl,ClearMyTracksByProcess 8',
        'echo. | clip',
        'del /s /q "C:\\ProgramData\\Microsoft\\Windows Defender\\Scans\\History\\Service\\*.*"',
        'del /s /q "%APPDATA%\\Microsoft\\Windows\\Recent\\*.*"',
        'net stop FontCache',
        'del /s /q "C:\\Windows\\System32\\FNTCACHE.DAT"',
        'net start FontCache',
        'powershell -Command "Clear-EventLog -LogName \'Directory Service\'"',
        'powershell -Command "Clear-EventLog -LogName \'Microsoft-Windows-TaskScheduler/Operational\'"',
        'del /s /q "C:\\ProgramData\\Microsoft\\Windows Defender\\Quarantine\\*.*"',
        'net stop Spooler',
        'del /s /q "C:\\Windows\\System32\\spool\\PRINTERS\\*.*"',
        'net start Spooler',
        'cleanmgr /sagerun:1',
        'del /s /q "C:\\Windows\\System32\\WDI\\LogFiles\\*.*"',
        'del /s /q "%APPDATA%\\Microsoft\\Office\\Recent\\*.*"',
        'powershell -Command "Clear-EventLog -LogName \'Microsoft-Windows-Debug\'"',
        'reg delete "HKLM\\SYSTEM\\CurrentControlSet\\Enum\\USBSTOR" /f',
        'del /s /q "%LOCALAPPDATA%\\Roblox\\logs\\*.*"',
        'del /s /q "C:\\Windows\\Temp\\*.*"',
        'del /s /q "%TEMP%\\*.*"',
        'powershell -Command "Clear-RecycleBin -Force"'
    ]

    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            pass
    messagebox.showinfo("Cleanup Complete", "Full Bypass Cleanup completed. Some operations may require a restart.")

# Generate batch file
def generate_bat_file():
    bat_content = """@echo off
:: Ultimate Windows Cleanup Script
:: WARNING: This script performs destructive operations that may delete important data.
:: Run as Administrator. Use at your own risk. Backup important data before running.

:: Check for admin rights
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script requires administrative privileges. Please run as Administrator.
    pause
    exit /b
)

:: Full Bypass function
:FullBypass
echo Performing Full Bypass Cleanup...

:: 2. Clear Run Dialog History
reg delete "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\RunMRU" /va /f >nul 2>&1

:: 3. Clear Windows Event Logs
for /f "tokens=*" %%G in ('wevtutil el') do wevtutil cl "%%G" >nul 2>&1

:: 6. Clear System Restore Points
vssadmin delete shadows /all /quiet >nul 2>&1

:: 7. Clear Network Shares History
for /f "tokens=2 delims= " %%a in ('cmdkey /list ^| findstr Target') do cmdkey /delete %%a >nul 2>&1

:: 8. Clear DirectX Shader Cache
del /s /q "%LOCALAPPDATA%\\D3DSCache\\*.*" >nul 2>&1

:: 9. Clear Windows Search Index
net stop WSearch >nul 2>&1
del /s /q "C:\\ProgramData\\Microsoft\\Search\\Data\\Applications\\Windows\\*.*" >nul 2>&1
net start WSearch >nul 2>&1

:: 10. Clear Thumbnail Cache
taskkill /f /im explorer.exe >nul 2>&1
del /s /q "%LOCALAPPDATA%\\Microsoft\\Windows\\Explorer\\thumbcache_*.db" >nul 2>&1
start explorer.exe >nul 2>&1

:: 11. Clear Windows Update Files
net stop wuauserv >nul 2>&1
net stop bits >nul 2>&1
del /s /q "C:\\Windows\\SoftwareDistribution\\*.*" >nul 2>&1
net start bits >nul 2>&1
net start wuauserv >nul 2>&1

:: 12. Clear Windows Error Reporting
del /s /q "C:\\ProgramData\\Microsoft\\Windows\\WER\\*.*" >nul 2>&1

:: 13. Clear Windows Prefetch Metadata
del /s /q "C:\\Windows\\Prefetch\\*.*" >nul 2>&1

:: 14. Clear Memory Dumps
del /s /q "C:\\Windows\\*.dmp" >nul 2>&1
del /s /q "%LOCALAPPDATA%\\CrashDumps\\*.*" >nul 2>&1

:: 15. Clear Network and Sharing Center History
netsh wlan delete profile name=* >nul 2>&1

:: 16. Clear Windows Store Cache
WSReset.exe

:: 17. Clear Windows Explorer History
RunDll32.exe Inet