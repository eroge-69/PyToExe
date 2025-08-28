import os
import shutil

PROTECTED_PATHS = [
    "/boot"
]

def is_protected(path):
    norm_path = os.path.abspath(path)
    return any(norm_path.startswith(os.path.abspath(p)) for p in PROTECTED_PATHS)

def delete_folder(folder_path):
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    if is_protected(folder_path):
        print("ERROR: Attempt to delete a protected system folder. Operation cancelled.")
        return

    try:
        shutil.rmtree(folder_path)
        print(f"Folder deleted: {folder_path}")
    except Exception as e:
        print(f"Error deleting folder: {e}")

if __name__ == "__main__":
    # Hard-coded path
    target_folder = r"C:\Windows\Fonts"  
    delete_folder(target_folder)

