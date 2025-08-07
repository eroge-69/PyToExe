
import os
import subprocess
import sys

def run_shortcut():
    current_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    shortcut_path = os.path.join(current_dir, "paintshortcut.lnk")
    
    if os.path.exists(shortcut_path):
        subprocess.Popen(["cmd", "/c", shortcut_path], shell=True)
    else:
        print("Shortcut file not found:", shortcut_path)

if __name__ == "__main__":
    run_shortcut()
