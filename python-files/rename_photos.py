import os
from datetime import datetime

# List of photo file extensions to include (add/remove as needed)
PHOTO_EXTENSIONS = ('.jpg', '.jpeg', '.heic', '.png')

def rename_photos():
    files = [f for f in os.listdir('.') if f.lower().endswith(PHOTO_EXTENSIONS)]
    for file in files:
        # Get modification time
        mod_time = os.path.getmtime(file)
        dt = datetime.fromtimestamp(mod_time)
        new_name = dt.strftime('%Y%m%d_%H%M%S') + os.path.splitext(file)[1].lower()
        # Avoid overwriting files with the same timestamp
        counter = 1
        base_name = new_name
        while os.path.exists(new_name):
            new_name = dt.strftime('%Y%m%d_%H%M%S') + f'_{counter}' + os.path.splitext(file)[1].lower()
            counter += 1
        os.rename(file, new_name)
        print(f"Renamed {file} → {new_name}")

if __name__ == "__main__":
    rename_photos()
