import os
import shutil
from datetime import datetime

# Set the target drive and base folder
TARGET_DRIVE = "D:"
BASE_FOLDER = "Archived_Desktop"

# Get today's date for folder name
date_str = datetime.now().strftime("%Y-%m-%d")

# Get path to user's Desktop
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

# Create target folder with date
target_folder = os.path.join(TARGET_DRIVE, BASE_FOLDER, date_str)
os.makedirs(target_folder, exist_ok=True)

# Move files and folders
for item in os.listdir(desktop_path):
    item_path = os.path.join(desktop_path, item)
    dest_path = os.path.join(target_folder, item)
    
    try:
        shutil.move(item_path, dest_path)
        print(f"Moved: {item}")
    except Exception as e:
        print(f"Failed to move {item}: {e}")

print(f"\n✅ All desktop files moved to: {target_folder}")

