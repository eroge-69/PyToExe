import winreg
import ctypes

def is_admin():
    """Check if the script is running with admin privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def disable_idle_time_limit():
    key_path = r"SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services"
    try:
        # Open or create the registry key
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)
        
        # Set MaxIdleTime to 0 (Disabled)
        winreg.SetValueEx(key, "MaxIdleTime", 0, winreg.REG_DWORD, 0)
        
        winreg.CloseKey(key)
        print("[✔] 'Set time limit for active but idle RDP sessions' has been disabled.")
        print("You may need to restart your system or run 'gpupdate /force' for changes to take effect.")
    except PermissionError:
        print("[✘] Permission denied. Please run this script as Administrator.")
    except Exception as e:
        print(f"[✘] Error: {e}")

if __name__ == "__main__":
    if not is_admin():
        print("[!] Please run this script as Administrator.")
    else:
        disable_idle_time_limit()
