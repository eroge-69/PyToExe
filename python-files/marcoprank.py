import os
import time
import tkinter as tk
from tkinter import messagebox
import subprocess
import sys

def main():
    # Step 1: Show message box
    root = tk.Tk()
    root.withdraw()  # Hide main Tk window
    messagebox.showinfo("Prank", "Imagine du bist ein Marco_scm Mod")

    # Step 2: Wait 5 seconds
    time.sleep(5)

    # Step 3: Open 9 command prompts
    for i in range(9):
        subprocess.Popen("start", shell=True)
        time.sleep(0.2)

    # Wait 2 seconds then close them all
    time.sleep(2)
    os.system("taskkill /IM cmd.exe /F")

    # Step 4: Delete itself
    script_path = os.path.abspath(sys.argv[0])
    deleter = script_path + ".bat"

    with open(deleter, "w") as f:
        f.write("@echo off\n")
        f.write("ping 127.0.0.1 -n 3 > nul\n")
        f.write(f"del \"{script_path}\"\n")
        f.write("del \"%~f0\"\n")

    subprocess.Popen(f"start {deleter}", shell=True)

if __name__ == "__main__":
    main()
