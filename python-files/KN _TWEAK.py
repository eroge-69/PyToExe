import os
import subprocess
import shutil
import sys
import requests

# ======= KeyAuth Class =======
class KeyAuth:
    def __init__(self, name, ownerid, secret, version):
        self.name = name
        self.ownerid = ownerid
        self.secret = secret
        self.version = version
        self.sessionid = None
        self.base = "https://keyauth.win/api/1.2/"

    def init(self):
        response = requests.post(self.base, data={
            "type": "init",
            "ver": self.version,
            "name": self.name,
            "ownerid": self.ownerid
        })
        result = response.json()
        if result["success"]:
            self.sessionid = result["sessionid"]
            return True
        else:
            print(f"[!] Init Error: {result['message']}")
            return False

    def license(self, key):
        response = requests.post(self.base, data={
            "type": "license",
            "key": key,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        })
        result = response.json()
        if result["success"]:
            if result.get("info", {}).get("subscriptions", [{}])[0].get("remaining") == 0:
                print("[!] This key has already been used.")
                return False
            return True
        else:
            print(f"[!] License Error: {result['message']}")
            return False

# ======= Helpers =======
def center_text(text, width=None):
    if width is None:
        width = shutil.get_terminal_size((80, 20)).columns
    return text.center(width)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clear_last_line():
    sys.stdout.write('\x1b[1A')  # move cursor up one line
    sys.stdout.write('\x1b[2K')  # erase entire line
    sys.stdout.flush()

def banner():
    RED = "\033[91m"
    RESET = "\033[0m"
    art = r'''
██╗  ██╗███╗   ██╗              ████████╗██╗    ██╗███████╗ █████╗ ██╗  ██╗
██║ ██╔╝████╗  ██║              ╚══██╔══╝██║    ██║██╔════╝██╔══██╗██║ ██╔╝
█████╔╝ ██╔██╗ ██║    █████╗       ██║   ██║ █╗ ██║█████╗  ███████║█████╔╝ 
██╔═██╗ ██║╚██╗██║    ╚════╝       ██║   ██║███╗██║██╔══╝  ██╔══██║██╔═██╗ 
██║  ██╗██║ ╚████║                 ██║   ╚███╔███╔╝███████╗██║  ██║██║  ██╗
  ╚═╝  ╚═╝╚═╝  ╚═══╝                 ╚═╝    ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝  
'''
    width = shutil.get_terminal_size((80, 20)).columns
    for line in art.splitlines():
        print(RED + line.center(width) + RESET)
    print()
    print(RED + ("-" * 55).center(width) + RESET)
    print(RED + "KN STORE - PERFORMANCE BOOST TOOL".center(width) + RESET)
    print(RED + ("-" * 55).center(width) + RESET)
    print(RED + "Maded By @KN STORE ".center(width) + RESET)
    print()

def run(command):
    subprocess.run(command, shell=True)

# ===== Features =====

def create_restore_point():
    run('powershell "Checkpoint-Computer -Description \"Louder Restore Point\" -RestorePointType MODIFY_SETTINGS"')

def system_optimizations():
    run('del /f /s /q %temp%\\*')
    run('del /f /s /q C:\\Windows\\Temp\\*')
    run('rd /s /q %temp%')
    run('md %temp%')
    run('del /f /s /q C:\\Windows\\Prefetch\\*')
    run('ipconfig /flushdns')
    run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\VisualEffects" /v VisualFXSetting /t REG_DWORD /d 2 /f')
    run('reg add "HKCU\\Control Panel\\Desktop" /v UserPreferencesMask /t REG_BINARY /d 9012038010000000 /f')

def gpu_optimizations():
    run('reg add "HKCU\\Software\\Microsoft\\DirectX" /v MaxFrameLatency /t REG_DWORD /d 1 /f')

def debloat():
    apps = [
        "*xbox*", "*zune*", "*onenote*", "*skype*", "*officehub*", "*solitairecollection*", "*getstarted*",
        "*bingweather*", "*soundrecorder*", "*3dviewer*", "*windowscommunicationsapps*", "*people*",
        "*mixedreality*", "*gamingoverlay*"
    ]
    for app in apps:
        run(f'powershell "Get-AppxPackage {app} | Remove-AppxPackage -ErrorAction SilentlyContinue"')
    run('powershell "Get-AppxPackage *Microsoft.549981C3F5F10* | Remove-AppxPackage -ErrorAction SilentlyContinue"')
    run('reg add "HKCU\\Software\\Policies\\Microsoft\\Windows\\WindowsCopilot" /v TurnOffWindowsCopilot /t REG_DWORD /d 1 /f')
    run('taskkill /f /im explorer.exe')
    run('start explorer.exe')

def power_optimizations():
    run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61')
    run('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61')

def cpu_optimizations():
    run('bcdedit /set useplatformclock true')

def network_tweaks():
    run('netsh int ip reset')
    run('netsh winsock reset')
    run('ipconfig /flushdns')
    run('ipconfig /release')
    run('ipconfig /renew')
    run('ipconfig /all')

def clear_ram_cache():
    run('powershell "[System.GC]::Collect()"')

def disable_services():
    for service in ["DiagTrack", "SysMain", "Fax", "PrintSpooler"]:
        run(f'sc config "{service}" start= disabled')

def view_system_info():
    run('systeminfo')

def clean_system_files():
    run('cleanmgr /sagerun:1')

def optimize_startup():
    run('powershell "Get-CimInstance Win32_StartupCommand | Select-Object Name, Command, Location | Format-Table -AutoSize"')

def coming_soon():
    print(center_text("This feature is coming soon... Stay tuned!"))

def restore_defaults():
    print(center_text("[!] Restoring default packages... (Close apps like WhatsApp, Xbox, etc)"))
    run(r'powershell "Get-AppxPackage -AllUsers | Foreach {Add-AppxPackage -DisableDevelopmentMode -Register ($_.InstallLocation + \\AppXManifest.xml)}"')

# ======= New Features =======

def games_specific_tweak():  # not safe
    run('reg add "HKCU\\Software\\Microsoft\\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f')
    run('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v HwSchMode /t REG_DWORD /d 2 /f')

def mouse_tweak():
    run('reg add "HKCU\\Control Panel\\Mouse" /v MouseSensitivity /t REG_SZ /d 10 /f')
    run('reg add "HKCU\\Control Panel\\Mouse" /v MouseSpeed /t REG_SZ /d 1 /f')

def system_bug_fixes():
    run('sfc /scannow')
    run('DISM /Online /Cleanup-Image /RestoreHealth')

def server_changer():  # not safe
    run('reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings" /v AutoConfigURL /t REG_SZ /d http://example.com/proxy.pac /f')

def internet_tweaker():
    run('netsh int tcp set global autotuninglevel=highlyrestricted')
    run('netsh int tcp set global rss=enabled')
    run('netsh int tcp set global chimney=enabled')

def cache_log_cleaner():
    run('del /f /s /q %localappdata%\\Microsoft\\Windows\\INetCache\\*')
    run('del /f /s /q %localappdata%\\Temp\\*')
    run('del /f /s /q C:\\Windows\\Logs\\*')

def better_vram():  # not safe
    run('reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\GraphicsDrivers" /v TdrDelay /t REG_DWORD /d 10 /f')

def timer_resolution_services():
    run('bcdedit /set useplatformtick yes')
    run('bcdedit /set tscsyncpolicy Enhanced')

# ======= Menu =======
def show_menu():
    RED = "\033[91m"
    WHITE = "\033[97m"
    RESET = "\033[0m"
    clear_screen()
    banner()
    indent = ' ' * 52  # to align with your style

    menu_items = [
        (1, "Create Restore Point", ""),
        (2, "System Optimizations", ""),
        (3, "GPU Optimizations", ""),
        (4, "System Debloat", ""),
        (5, "Power Optimizations", ""),
        (6, "CPU Optimizations", ""),
        (7, "Network Tweaks", ""),
        (8, "Clear RAM Cache", ""),
        (9, "Disable Unnecessary Services", ""),
        (10, "View System Information", ""),
        (11, "Clean System Files", ""),
        (12, "Optimize Startup Programs", ""),
        (13, "Games Specific Tweak", "not safe"),
        (14, "Mouse Tweak", ""),
        (15, "System Bug Fixes", ""),
        (16, "Server Changer", "not safe"),
        (17, "Internet Tweaker", ""),
        (18, "Cache and Log Cleaner", ""),
        (19, "Better VRAM", "not safe"),
        (20, "Timer Resolution Services", ""),
        (21, "Restore All Defaults", ""),
        (22, "Coming Soon...", ""),
        (23, "Exit", "")
    ]

    width = shutil.get_terminal_size().columns
    max_text_len = max(len(text) + (len(note) + 2 if note else 0) for _, text, note in menu_items)
    total_width = max_text_len + 6

    print(RED + ("-" * total_width).center(width) + RESET)
    for num, text, note in menu_items:
        line = f"{RED}[{num}]{RESET} {WHITE}{text}{RESET}"
        if note:
            line += "  " + RED + note + RESET
        print(indent + line)
    print(RED + ("-" * total_width).center(width) + RESET)

def main():
    banner()
    input(center_text("Press Enter to show menu..."))
    show_menu()

    options = {
        "1": create_restore_point,
        "2": system_optimizations,
        "3": gpu_optimizations,
        "4": debloat,
        "5": power_optimizations,
        "6": cpu_optimizations,
        "7": network_tweaks,
        "8": clear_ram_cache,
        "9": disable_services,
        "10": view_system_info,
        "11": clean_system_files,
        "12": optimize_startup,
        "13": games_specific_tweak,
        "14": mouse_tweak,
        "15": system_bug_fixes,
        "16": server_changer,
        "17": internet_tweaker,
        "18": cache_log_cleaner,
        "19": better_vram,
        "20": timer_resolution_services,
        "21": restore_defaults,
        "22": coming_soon,
        "23": exit
    }

    while True:
        choice = input("\n" + center_text("Choose an option: ")).strip()
        action = options.get(choice)
        if action:
            clear_screen()
            banner()
            action()
            input("\n" + center_text("\u2714 Press Enter to return to the menu..."))
            show_menu()
        else:
            print(center_text("[!] Invalid choice."))

if __name__ == "__main__":
    if os.name != "nt":
        print("This script is only for Windows.")
        exit()

    # KeyAuth setup
    keyauth = KeyAuth(
        name="My tweak @ louder",
        ownerid="483MGi5LHQ",
        secret="d5ad5524bcda51416eaa74fe88f7c153ccd8a4a0e1f1f83d9de34b7faff028e6",
        version="1.0"
    )

    if not keyauth.init():
        input("Press Enter to exit...")
        exit()

    user_key = input("\033[91mEnter your one-time license key: \033[0m")
    clear_last_line()

    if keyauth.license(user_key):
        print(center_text("Thank you for using KN Tweak <3"))
        input(center_text("Press Enter to continue..."))
        main()
    else:
        input(center_text("Invalid or already used key. Press Enter to exit..."))
        exit()
