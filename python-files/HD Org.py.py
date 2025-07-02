import os
import shutil
import sys

# This script organizes the folder it is currently placed in.
TARGET_FOLDER = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))

FILE_CATEGORIES = {
    "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"],
    "Movies": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi"],
    "Other": [] 
}

print(f"Starting to organize files in: {TARGET_FOLDER}")

try:
    all_items = os.listdir(TARGET_FOLDER)
except FileNotFoundError:
    print(f"Error: The folder '{TARGET_FOLDER}' does not exist.")
    exit()

for category in FILE_CATEGORIES.keys():
    folder_path = os.path.join(TARGET_FOLDER, category)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

for item_name in all_items:
    item_path = os.path.join(TARGET_FOLDER, item_name)
    if os.path.isdir(item_path):
        continue

    moved = False
    for category, extensions in FILE_CATEGORIES.items():
        if any(item_name.lower().endswith(ext) for ext in extensions):
            destination_folder = os.path.join(TARGET_FOLDER, category)
            shutil.move(item_path, os.path.join(destination_folder, item_name))
            moved = True
            break

    if not moved:
        other_folder = os.path.join(TARGET_FOLDER, "Other")
        if not os.path.exists(other_folder):
            os.makedirs(other_folder)
        shutil.move(item_path, os.path.join(other_folder, item_name))

print("\nOrganization complete.")