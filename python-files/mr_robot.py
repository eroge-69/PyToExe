import os
import sys

def main():
    # Get the desktop path
    desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
    
    # If the system is in Ukrainian, the desktop might be called 'Робочий стіл'
    # Check if the desktop exists in the usual location, otherwise try the Ukrainian version
    if not os.path.exists(desktop_path):
        desktop_path = os.path.join(os.path.expanduser('~'), 'Робочий стіл')
        if not os.path.exists(desktop_path):
            print("Desktop path not found.")
            return

    # List all directories on the desktop
    folders = [f for f in os.listdir(desktop_path) if os.path.isdir(os.path.join(desktop_path, f))]
    
    # Rename each folder
    for i, folder in enumerate(folders):
        try:
            new_name = f"mr_robot_{i+1}"
            old_path = os.path.join(desktop_path, folder)
            new_path = os.path.join(desktop_path, new_name)
            os.rename(old_path, new_path)
        except Exception as e:
            print(f"Error renaming {folder}: {e}")

if name == "main":
    main()