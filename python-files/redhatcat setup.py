print("Starting setup...")
import shutil
import os

source_folder = "shellredhatcat"
destination_folder = "c:/"

try:
    shutil.copytree(source_folder, os.path.join(destination_folder, "shellredhatcat"))
    print(f"Folder '{source_folder}' copied successfully to '{destination_folder}'")
except FileNotFoundError:
    print(f"Error: Source folder '{source_folder}' not found.")
except FileExistsError:
    print(f"Error: Destination folder '{destination_folder}/redhatcat_copy' already exists.")
except Exception as e:
    print(f"An error occurred: {e}")


print("please insert disk 3 labeled configuration")
import time
time.sleep(10)