import pyautogui
import os
from datetime import datetime

target_folder = r"C:\Users\shobhit\OneDrive\Desktop\screen shots new"
os.makedirs(target_folder, exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"screenshot_{timestamp}.png"
file_path = os.path.join(target_folder, file_name)

pyautogui.screenshot().save(file_path)
