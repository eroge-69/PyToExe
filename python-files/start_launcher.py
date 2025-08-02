import time
import os
import subprocess
import sys

def main():
    print("[WORK]")
    print("Initializing Fortnite launcher GUI...")
    time.sleep(2)

    
    python_exe = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), "fortnite_gui_launcher.py")
    subprocess.Popen([python_exe, script_path])

if __name__ == "__main__":
    main()