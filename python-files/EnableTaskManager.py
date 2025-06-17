import winreg
import ctypes

def enable_task_manager():
    try:
        # Open registry key
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
        
        # Delete "DisableTaskMgr" value
        winreg.DeleteValue(key, "DisableTaskMgr")
        winreg.CloseKey(key)
        print("Task Manager has been enabled.")
    except FileNotFoundError:
        print("Task Manager setting not found; it may already be enabled.")
    except PermissionError:
        print("Permission denied. Run the script as administrator.")
    except Exception as e:
        print(f"Error: {e}")

if name == "main":
    # Ask for admin privileges
    if ctypes.windll.shell32.IsUserAnAdmin():
        enable_task_manager()
    else:
        print("Please run this script as Administrator.")