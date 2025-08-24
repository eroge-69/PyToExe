import psutil
import os
import time
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

def check_running_files():
    print(f"=== Running File Scan ({time.strftime('%H:%M:%S')}) ===\n")
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            exe_path = proc.info['exe']
            if exe_path:  # Some system processes may not have a path
                timestamp = time.strftime("%H:%M:%S")
                if os.path.exists(exe_path):
                    print(f"[{timestamp}] {Fore.GREEN}File is present{Style.RESET_ALL}: {exe_path}")
                else:
                    print(f"[{timestamp}] {Fore.RED}File is deleted{Style.RESET_ALL}: {exe_path}")
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue

if __name__ == "__main__":
    check_running_files()
    input("\nPress Enter to exit...")
