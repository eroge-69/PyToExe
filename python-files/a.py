import os
import json
import subprocess
from datetime import datetime

BACKUP_FILE = r"C:\UnseenLight\regb.json"
os.makedirs(os.path.dirname(BACKUP_FILE), exist_ok=True)

# ------------------------------------------------------------------
# Registry helpers
# ------------------------------------------------------------------
def _run(cmd):
    """Run a shell command and return (stdout, stderr, returncode)."""
    proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return proc.stdout, proc.stderr, proc.returncode

def reg_get(path: str, name: str):
    """Return the current value of a REG_DWORD / REG_SZ key or None if missing."""
    out, _, code = _run(f'reg query "{path}" /v "{name}"')
    if code != 0:
        return None
    # REG_SZ  ->  "ValueName    REG_SZ    TheValue"
    # REG_DWORD -> "ValueName    REG_DWORD    0x123"
    for line in out.splitlines():
        if name in line:
            parts = line.split()
            if "REG_DWORD" in line:
                return int(parts[-1], 0)
            if "REG_SZ" in line:
                return " ".join(parts[2:])
    return None

def reg_set(path: str, name: str, val, reg_type="REG_DWORD"):
    """Write a value and record the previous one in the backup file."""
    old = reg_get(path, name)
    _run(f'reg add "{path}" /v "{name}" /t {reg_type} /d "{val}" /f')
    _append_backup(path, name, old, val, reg_type)

def _append_backup(path, name, old, new, reg_type):
    entry = {
        "timestamp": str(datetime.now()),
        "path": path,
        "name": name,
        "old": old,
        "new": new,
        "type": reg_type
    }
    data = []
    if os.path.isfile(BACKUP_FILE):
        with open(BACKUP_FILE, encoding="utf-8") as f:
            data = json.load(f)
    data.append(entry)
    with open(BACKUP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def restore_all():
    if not os.path.isfile(BACKUP_FILE):
        print("No backup file found.")
        return
    with open(BACKUP_FILE, encoding="utf-8") as f:
        entries = json.load(f)
    for e in entries:
        if e["old"] is None:
            # Key did not exist – delete it
            subprocess.run(f'reg delete "{e["path"]}" /v "{e["name"]}" /f', shell=True)
        else:
            reg_type = e.get("type", "REG_DWORD")
            reg_set(e["path"], e["name"], e["old"], reg_type)
    print("Registry restored from backup.")
    os.remove(BACKUP_FILE)

# ------------------------------------------------------------------
# New tweak definitions
# ------------------------------------------------------------------
TWEAKS = {
    "Move Start Menu to Left": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "name": "TaskbarAl",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Classic Right-Click Menu": {
        "path": r"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32",
        "name": "",
        "on": "",  # (Default) empty string creates the key
        "off": None,  # Deleting the key restores Win11 menu
        "type": "REG_SZ"
    },
    "Disable Bing in Search": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\SearchSettings",
        "name": "IsBingSearchEnabled",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Classic Volume/Clock Flyouts": {
        "path": r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Shell\Update\Packages",
        "name": "UndockingDisabled",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Disable Rounded Corners": {
        "path": r"HKLM\SOFTWARE\Microsoft\Windows\Dwm",
        "name": "RoundCorners",
        "on": 2,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Enable Transparent Taskbar": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        "name": "EnableTransparency",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Enable Full Context Menu": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "name": "ShowStartMenuClassicMode",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Disable Snap Assist Flyout": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "name": "EnableSnapAssistFlyout",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Hide Widgets Button": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "name": "TaskbarDa",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Hide Chat (Teams) Button": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "name": "TaskbarMn",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Disable Lock-Screen Blur": {
        "path": r"HKLM\SOFTWARE\Policies\Microsoft\Windows\System",
        "name": "DisableAcrylicBackgroundOnLogon",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Disable Windows Ink Workspace": {
        "path": r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsInkWorkspace",
        "name": "AllowWindowsInkWorkspace",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Restore Classic Photo Viewer": {
        "path": r"HKCR\Applications\photoviewer.dll\shell\open\command",
        "name": "",
        "on": r'"%SystemRoot%\System32\rundll32.exe" "%ProgramFiles%\Windows Photo Viewer\PhotoViewer.dll", ImageView_Fullscreen %1',
        "off": None,
        "type": "REG_SZ"
    },
    "Disable Recall (AI snapshots)": {
        "path": r"HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsAI",
        "name": "DisableAIDataAnalysis",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Disable Copilot": {
        "path": r"HKCU\Software\Policies\Microsoft\Windows\WindowsCopilot",
        "name": "TurnOffWindowsCopilot",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Disable Suggested Content in Settings": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager",
        "name": "SubscribedContent-338393Enabled",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    },
    "Disable Background Apps": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
        "name": "GlobalUserDisabled",
        "on": 1,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Remove ‘3D Objects’ from Explorer": {
        "path": r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\MyComputer\NameSpace\{0DB7E03F-FC29-4DC6-9020-FF41B59E513A}",
        "name": "",
        "on": None,  # delete key
        "off": 1,    # restore key (dummy)
        "type": "REG_DWORD"
    },
    "Disable News & Interests": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Feeds",
        "name": "ShellFeedsTaskbarViewMode",
        "on": 2,
        "off": 0,
        "type": "REG_DWORD"
    },
    "Show File Extensions": {
        "path": r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
        "name": "HideFileExt",
        "on": 0,
        "off": 1,
        "type": "REG_DWORD"
    }
}

# ------------------------------------------------------------------
# New menu helpers
# ------------------------------------------------------------------
def _toggle_tweak(title, action):
    cfg = TWEAKS[title]
    val = cfg["on"] if action == "on" else cfg["off"]
    typ = cfg.get("type", "REG_DWORD")
    if val is None:
        # Delete the value/key
        subprocess.run(f'reg delete "{cfg["path"]}" /v "{cfg["name"]}" /f', shell=True)
        _append_backup(cfg["path"], cfg["name"], reg_get(cfg["path"], cfg["name"]), None, typ)
    else:
        reg_set(cfg["path"], cfg["name"], val, typ)

def tweaks_menu():
    while True:
        print("\nTweaks Menu:")
        print("1. Enable Tweaks")
        print("2. Disable Tweaks")
        print("3. Restart Explorer")
        print("4. Back to Main Menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            _tweak_submenu("Enable")
        elif choice == "2":
            _tweak_submenu("Disable")
        elif choice == "3":
            os.system('taskkill /f /im explorer.exe & start explorer.exe')
        elif choice == "4":
            break
        else:
            print("Invalid input.")

def _tweak_submenu(mode):
    """mode = 'Enable' or 'Disable'."""
    action = "on" if mode == "Enable" else "off"
    while True:
        print(f"\n{mode} Tweaks:")
        for idx, title in enumerate(TWEAKS.keys(), 1):
            print(f"{idx}. {title}")
        print("0. Back")
        choice = input("Select tweak: ").strip()
        if choice == "0":
            break
        try:
            title = list(TWEAKS.keys())[int(choice) - 1]
            _toggle_tweak(title, action)
            print(f"{title} – {mode}d.")
        except (IndexError, ValueError):
            print("Invalid input.")

# ------------------------------------------------------------------
# Everything else remains the same
# ------------------------------------------------------------------
def dns_menu():
    while True:
        print("\nDNS Options:")
        print("1. Set DNS to Cloudflare (1.1.1.1)")
        print("2. Set DNS to Google (8.8.8.8)")
        print("3. Reset to default")
        print("4. Back to Main Menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            os.system('netsh interface ip set dns name="Wi-Fi" static 1.1.1.1')
        elif choice == "2":
            os.system('netsh interface ip set dns name="Wi-Fi" static 8.8.8.8')
        elif choice == "3":
            os.system('netsh interface ip set dns name="Wi-Fi" dhcp')
        elif choice == "4":
            break
        else:
            print("Invalid input.")

def privacy_menu():
    while True:
        print("\nPrivacy Menu:")
        print("1. Disable Telemetry")
        print("2. Disable Location Services")
        print("3. Disable Advertising ID")
        print("4. Restore from backup")
        print("5. Back to Main Menu")
        choice = input("Select option: ").strip()
        if choice == "1":
            os.system('reg add "HKLM\\SOFTWARE\\Policies\\Microsoft\\Windows\\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f')
        elif choice == "2":
            os.system('reg add "HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location" /v Value /t REG_SZ /d Deny /f')
        elif choice == "3":
            os.system('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\AdvertisingInfo" /v Enabled /t REG_DWORD /d 0 /f')
        elif choice == "4":
            restore_all()
        elif choice == "5":
            break
        else:
            print("Invalid input.")

def main_menu():
    while True:
        print("\nWindows 11 Tweaker Z")
        print("1. Tweaks and UI changes")
        print("2. DNS and Internet")
        print("3. Privacy Settings")
        print("4. Exit")
        choice = input("Select category: ").strip()
        if choice == "1":
            tweaks_menu()
        elif choice == "2":
            dns_menu()
        elif choice == "3":
            privacy_menu()
        elif choice == "4":
            break
        else:
            print("Invalid input.")

if __name__ == "__main__":
    main_menu()