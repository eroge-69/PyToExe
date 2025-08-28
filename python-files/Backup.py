import os
import shutil
from datetime import datetime

# Prompt user for source folder
source_path = input("Enter the full path of the folder to back up: ").strip()
if not os.path.exists(source_path):
    print("ERROR: Source path does not exist.")
    exit(1)

# Define destination network path
share_path = r"\\10.30.18.40\DriveBackups"
source_folder_name = os.path.basename(source_path)
dest_path = os.path.join(share_path, source_folder_name)

# Create log file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_path = os.path.join(os.getcwd(), f"BackupLog_{timestamp}.txt")

# Log function
def log(message):
    print(message)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(message + "\n")

log(f"Backup started at {datetime.now()}")
log(f"Source: {source_path}")
log(f"Destination: {dest_path}")

# Create destination directory if it doesn't exist
try:
    os.makedirs(dest_path, exist_ok=True)
    log("Destination directory verified or created.")
except Exception as e:
    log(f"ERROR: Failed to create destination directory: {e}")
    exit(1)

# Copy files
file_count = 0
error_count = 0
for root_dir, _, files in os.walk(source_path):
    for file in files:
        src_file = os.path.join(root_dir, file)
        rel_path = os.path.relpath(src_file, source_path)
        dest_file = os.path.join(dest_path, rel_path)
        dest_dir = os.path.dirname(dest_file)
        try:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.copy2(src_file, dest_file)
            file_count += 1
        except Exception as e:
            log(f"ERROR copying {src_file}: {e}")
            error_count += 1

log(f"Backup completed. Files copied: {file_count}, Errors: {error_count}")
log(f"Log file saved to: {log_path}")
