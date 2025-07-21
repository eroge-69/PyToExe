import os
import shutil

def copy_latest_file(source_folder, destination_folder):
    try:
        if not os.path.exists(source_folder):
            print(f"Source folder does not exist: {source_folder}")
            return
        if not os.path.exists(destination_folder):
            print(f"Destination folder does not exist: {destination_folder}")
            return

        files = [os.path.join(source_folder, f) for f in os.listdir(source_folder)
                 if os.path.isfile(os.path.join(source_folder, f))]

        if not files:
            print("No files found in the source folder.")
            return

        latest_file = max(files, key=os.path.getmtime)
        shutil.copy(latest_file, destination_folder)
        print(f"Copied latest file: {os.path.basename(latest_file)} to {destination_folder}")

    except Exception as e:
        print(f"An error occurred: {e}")

source = r"\\CH3-DVPP829\d$\Daily_Database_Backup"
destination = r"\\tsclient\Z\Engineering\Daily Backup"

copy_latest_file(source, destination)
