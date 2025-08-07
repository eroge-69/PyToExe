
import os
import shutil

source_folder = r"C:\Users\sumit\Desktop\ss"
destination_folder = r"C:\Users\sumit\Desktop\ALL"

os.makedirs(destination_folder, exist_ok=True)

for file_name in os.listdir(source_folder):
    if file_name.lower().endswith(('.docx', '.xml')):
        full_source_path = os.path.join(source_folder, file_name)
        full_dest_path = os.path.join(destination_folder, file_name)
        shutil.move(full_source_path, full_dest_path)
        print(f"Moved: {file_name}")

input("Done. Press Enter to exit...")
