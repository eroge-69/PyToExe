import os
import zipfile
import sys

def zip_all_subfolders(parent_folder):
    parent_folder = os.path.abspath(parent_folder)

    for folder_name in os.listdir(parent_folder):
        folder_path = os.path.join(parent_folder, folder_name)
        if os.path.isdir(folder_path):
            zip_file_path = os.path.join(parent_folder, f"{folder_name}.zip")

            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        arcname = os.path.relpath(full_path, start=folder_path)
                        zipf.write(full_path, arcname)

            print(f"Zipped: {zip_file_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python zip_subfolders.py <folder_path>")
    else:
        zip_all_subfolders(sys.argv[1])
