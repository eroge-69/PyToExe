import os
import glob

def delete_oldest_file(folder_path):
    # Get all files in the folder
    files = glob.glob(os.path.join(folder_path, '*'))

    if not files:
        print("No files found in the folder.")
        return

    # Find the oldest file by modification time
    oldest_file = min(files, key=os.path.getmtime)

    # Delete the oldest file
    try:
        os.remove(oldest_file)
        print(f"Deleted the oldest file: {oldest_file}")
    except Exception as e:
        print(f"Error deleting file: {e}")

# Example usage:
delete_oldest_file(r'C:\Users\Давид\Pictures\Screenshots')