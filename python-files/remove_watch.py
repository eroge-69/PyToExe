
import os
import sys

def rename_files_in_folder(folder_path):
    for filename in os.listdir(folder_path):
        if 'watch' in filename.lower():
            index = filename.lower().find('watch')
            new_filename = filename[:index] + filename[index+5:]
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_filename)
            os.rename(old_path, new_path)
            print(f'Renamed: {filename} → {new_filename}')

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Drag and drop a folder onto this .exe to run.")
        input("Press Enter to exit...")
    else:
        folder_path = sys.argv[1]
        if os.path.isdir(folder_path):
            rename_files_in_folder(folder_path)
            print("\nDone.")
        else:
            print("That was not a valid folder.")
        input("Press Enter to exit...")
