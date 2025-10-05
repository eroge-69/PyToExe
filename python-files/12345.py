import ctypes
import sys
import os

def run_as_admin():
    # If not running as admin, relaunch the script with admin rights
    if ctypes.windll.shell32.IsUserAnAdmin():
        # Already running as admin → open cmd
        os.system("start cmd")
    else:
        # Relaunch with admin rights
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, __file__, None, 1
        )

if __name__ == "__main__":
    run_as_admin()
