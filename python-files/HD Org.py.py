import os
import shutil
import sys
import time

# Get the folder the script is in.
# This logic correctly finds the path whether it's a .py script or a frozen .exe
if getattr(sys, 'frozen', False):
    TARGET_FOLDER = os.path.dirname(sys.executable)
    script_name = os.path.basename(sys.executable)
else:
    TARGET_FOLDER = os.path.dirname(os.path.abspath(__file__))
    script_name = os.path.basename(__file__)

FILE_CATEGORIES = {
    "Pictures": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".heic"],
    "Movies": [".mp4", ".mov", ".avi", ".mkv", ".wmv"],
    "Documents": [".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt", ".txt"],
    "Music": [".mp3", ".wav", ".aac", ".flac"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "Installers": [".exe", ".msi"],
}

print(f"Starting to organize files in: {TARGET_FOLDER}")
print(f"Ignoring self: {script_name}\n")

# --- Create all destination folders beforehand, including "Other" ---
all_dest_folders = list(FILE_CATEGORIES.keys()) + ["Other"]
for folder_name in all_dest_folders:
    folder_path = os.path.join(TARGET_FOLDER, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_name}")

time.sleep(2) # Brief pause to let user read the output

try:
    all_items = os.listdir(TARGET_FOLDER)
except FileNotFoundError:
    print(f"Error: The folder '{TARGET_FOLDER}' does not exist.")
    exit()

# --- Main Loop ---
for item_name in all_items:
    item_path = os.path.join(TARGET_FOLDER, item_name)

    # --- FIX: Skip directories AND the script's own file ---
    if os.path.isdir(item_path) or item_name.lower() == script_name.lower():
        continue

    moved = False
    for category, extensions in FILE_CATEGORIES.items():
        if any(item_name.lower().endswith(ext) for ext in extensions):
            destination_folder_path = os.path.join(TARGET_FOLDER, category)
            destination_file_path = os.path.join(destination_folder_path, item_name)

            # --- FIX: Handle duplicate file names ---
            if os.path.exists(destination_file_path):
                # If file with same name exists, add a number to the name
                base, extension = os.path.splitext(item_name)
                counter = 1
                while os.path.exists(destination_file_path):
                    new_name = f"{base} ({counter}){extension}"
                    destination_file_path = os.path.join(destination_folder_path, new_name)
                    counter += 1
                print(f"WARNING: '{item_name}' already existed. Renaming to '{new_name}'.")

            # --- FIX: Handle permissions and other errors ---
            try:
                shutil.move(item_path, destination_file_path)
                print(f"Moved '{item_name}' to '{category}'.")
                moved = True
            except Exception as e:
                print(f"ERROR: Could not move '{item_name}'. Reason: {e}")
                moved = True # Mark as "moved" to prevent it from going to "Other"
            break

    # --- Move remaining files to "Other" ---
    if not moved:
        other_folder_path = os.path.join(TARGET_FOLDER, "Other")
        try:
            shutil.move(item_path, os.path.join(other_folder_path, item_name))
            print(f"Moved '{item_name}' to 'Other'.")
        except Exception as e:
            print(f"ERROR: Could not move '{item_name}'. Reason: {e}")


print("\nOrganization complete.")
# Keep the window open for 5 seconds to read the output before closing
time.sleep(5)