import os
import shutil
import winreg
import ctypes
import time

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("bruh you really tryna run this without admin? SKILL ISSUE 🤡")
    time.sleep(2)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit()

def clean_fivem_cheats():
    print('''
██╗  ██╗ ██████╗ ██╗  ██╗     ██████╗██╗     ███████╗ █████╗ ███╗   ██╗███████╗██████╗ 
██║  ██║██╔═████╗██║  ██║    ██╔════╝██║     ██╔════╝██╔══██╗████╗  ██║██╔════╝██╔══██╗
███████║██║██╔██║███████║    ██║     ██║     █████╗  ███████║██╔██╗ ██║█████╗  ██████╔╝
╚════██║████╔╝██║╚════██║    ██║     ██║     ██╔══╝  ██╔══██║██║╚██╗██║██╔══╝  ██╔══██╗
     ██║╚██████╔╝     ██║    ╚██████╗███████╗███████╗██║  ██║██║ ╚████║███████╗██║  ██║
     ╚═╝ ╚═════╝      ╚═╝     ╚═════╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
    ''')

    print('''
╔══════════════════════ SYSTEM INFO ══════════════════════╗
║                                                                   ║
║ Status: ONLINE                                          ║
║ Version: 1.0.0                                             ║
║ Discord: discord.gg/nqyAzEAZ                  ║
╚═════════════════════════════════════════════════════════╝
    ''')

    print("[!] Preparing to clean system for optimal spoofer compatibility.")
    print("[!] This free tool removes all relevant data to provide a clean environment for spoofing.")
    input("[+] Press Enter to continue...")

    choice = input("DO YOU WANT TO CLEAN? (Y/N): ").strip().lower()
    if choice != 'y':
        print("lil bch scared to clean? BYE BOZO 👋")
        time.sleep(1)
        sys.exit()

    print("BRUHHHHH LET'S NUKE THESE CHEATS 💥")

    # Common cheat directories (adjust as needed)
    cheat_paths = [
        os.path.expandvars("%APPDATA%\\FiveM"),
        os.path.expandvars("%LOCALAPPDATA%\\FiveM"),
        os.path.expandvars("%PROGRAMDATA%\\FiveM"),
        os.path.expandvars("%USERPROFILE%\\Documents\\FiveM"),
        "C:\\FiveM",
        "C:\\Program Files\\FiveM",
        "C:\\Program Files (x86)\\FiveM"
    ]

    # Registry keys to delete
    reg_keys = [
        "Software\\FiveM",
        "Software\\CitizenFX",
        "Software\\RedM",
        "Software\\CheatEngine",
        "Software\\Lua Scripts"
    ]

    # Known cheat process names (add more if needed)
    cheat_processes = [
        "fivemcheat.exe",
        "fivemhack.exe",
        "fivemspoofer.exe",
        "cheatengine.exe",
        "luaengine.exe",
        "injector.exe"
        "nd.exe",
        "n0d3.exe",
        "systemhost.exe",
        "chromehelper.exe"
        "core.exe",
        "core64.exe",
        "syscore.exe",
        "WinUpdate.exe",
        "MicrosoftHost.exe",
        "banana.exe",
        "banana32.exe",
        "music.exe",
        "media.exe",
        "susano.exe",
        "svc.exe",
        "dxsvc.exe",
        "ventiq.exe",
        "servicehost.exe",
        "vservice.exe",
        "chromeupdate.exe",
        "taskruntime.exe",
        "updatecheck.exe",
        "dwmhost.exe",
        "keyser.exe",
        "windowsupdate.exe",
        "dxdiaghost.exe",
        "wuauserv.exe",
        "driverhost.exe",
        "tz.exe",
        "tzx.exe",
        "tzloader.exe",
        "tzclient.exe",
        "tzinject.exe",
        "tzghost.exe",
        "ts3host.exe"
        "plughost.exe"
        "webhost.exe"
    ]

    # KILL CHEAT PROCESSES FIRST
    print("\n[🔥] KILLING CHEAT PROCESSES...")
    for proc in cheat_processes:
        try:
            os.system(f"taskkill /f /im {proc} >nul 2>&1")
            print(f"  [+] NUKED: {proc}")
        except:
            print(f"  [-] FAILED TO KILL: {proc} (probably already dead)")

    # DELETE FILES & FOLDERS
    print("\n[🔥] DELETING CHEAT FILES...")
    for path in cheat_paths:
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                else:
                    shutil.rmtree(path, ignore_errors=True)
                print(f"  [+] DELETED: {path}")
            except:
                print(f"  [-] FAILED TO DELETE: {path} (skill issue?)")

    # CLEAN REGISTRY
    print("\n[🔥] CLEANING REGISTRY...")
    for key in reg_keys:
        try:
            winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key)
            print(f"  [+] REG DELETED: HKCU\\{key}")
        except:
            pass
        try:
            winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, key)
            print(f"  [+] REG DELETED: HKLM\\{key}")
        except:
            pass

    # CLEAN TEMP FILES
    print("\n[🔥] PURGING TEMP FILES...")
    os.system("del /q /f /s %temp%\\* >nul 2>&1")
    os.system("del /q /f /s %windir%\\temp\\* >nul 2>&1")
    print("  [+] TEMP FILES ANNIHILATED")

    print("\n[✅] SYSTEM CLEANED! NO MORE CHEATS, LIL NPC 🤡")
    time.sleep(3)

if __name__ == "__main__":
    import sys
    clean_fivem_cheats()