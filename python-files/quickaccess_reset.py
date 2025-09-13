import os
import shutil
import ctypes
import subprocess

def reset_quick_access():
    """Quick Access ডেটা রিসেট করে"""
    qpath = os.path.expandvars(r"%AppData%\Microsoft\Windows\Recent\AutomaticDestinations")
    if os.path.exists(qpath):
        for file in os.listdir(qpath):
            file_path = os.path.join(qpath, file)
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Could not delete {file_path}: {e}")
    print("Quick Access reset complete.")

def pin_desktop_quick_access():
    """Desktop Quick Access এ পিন করার চেষ্টা"""
    desktop_path = os.path.expanduser("~/Desktop")
    try:
        # PowerShell কমান্ড ব্যবহার করে pin করার চেষ্টা
        cmd = f'''powershell -Command "$s = New-Object -ComObject shell.application; $f = $s.Namespace('{desktop_path}'); $f.Self.InvokeVerb('Pin to Quick Access')"'''
        subprocess.run(cmd, shell=True)
        print("Desktop pinned to Quick Access.")
    except Exception as e:
        print(f"Could not pin Desktop: {e}")

if __name__ == "__main__":
    # Admin rights চেক
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("Please run this script as Administrator!")
    else:
        reset_quick_access()
        pin_desktop_quick_access()