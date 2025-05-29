import os
import requests
import zipfile
import shutil
import tempfile
import subprocess
import sys

APP_EXECUTABLE = "main.exe"  # Your main app's .exe name
ZIP_URL = "https://drive.google.com/uc?export=download&id=1Gi7oMtnzNMwEo1p5Uv45F3uXqto-ceE0"

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.getcwd()

def download_zip(url, dest_path):
    response = requests.get(url, stream=True)
    with open(dest_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def extract_to_resources(zip_path, resource_dir):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if member.startswith(('images/', 'data/', 'shortcuts/')):
                target_path = os.path.join(resource_dir, member)
                if member.endswith('/'):
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, 'wb') as f:
                        f.write(zip_ref.read(member))

def main():
    base_path = get_base_path()
    resource_dir = os.path.join(base_path, "resources")
    temp_zip_path = os.path.join(tempfile.gettempdir(), "update.zip")

    try:
        print("Downloading update...")
        download_zip(ZIP_URL, temp_zip_path)
        print("Extracting update to resources...")
        extract_to_resources(temp_zip_path, resource_dir)
        print("Update complete.")
    except Exception as e:
        print(f"Error during update: {e}")
    finally:
        if os.path.exists(temp_zip_path):
            os.remove(temp_zip_path)

    app_path = os.path.join(base_path, APP_EXECUTABLE)
    if os.path.exists(app_path):
        subprocess.Popen([app_path], shell=True)

if __name__ == "__main__":
    main()
