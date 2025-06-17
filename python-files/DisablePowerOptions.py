import winreg as reg
import ctypes

def disable_power_options():
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer"
        reg_key = reg.CreateKey(reg.HKEY_CURRENT_USER, key_path)
        
        # 1 = hide shutdown
        reg.SetValueEx(reg_key, "NoClose", 0, reg.REG_DWORD, 1)
        # 1 = hide sleep
        reg.SetValueEx(reg_key, "NoSleep", 0, reg.REG_DWORD, 1)
        # 1 = hide hibernate
        reg.SetValueEx(reg_key, "NoHibernate", 0, reg.REG_DWORD, 1)
        
        reg.CloseKey(reg_key)
        print("Power options disabled. You may need to log off or restart.")
        
    except Exception as e:
        print("Failed to modify registry:", e)

# Request Admin Privileges
if ctypes.windll.shell32.IsUserAnAdmin():
    disable_power_options()
else:
    print("This script requires administrative privileges.")