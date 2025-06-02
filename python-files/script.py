import os

def remove_non_papa_files(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if not filename.endswith('.papa'):
                file_path = os.path.join(dirpath, filename)
                try:
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

# Replace this path with your target directory
target_directory = "C:\Users\maxim\Desktop\exiles.faction"

remove_non_papa_files(target_directory)
