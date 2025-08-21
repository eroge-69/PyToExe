import os
import random
import shutil

# Define your folders
FOLDER1 = "folder1"
FOLDER2 = "folder2"
FOLDER3 = "folder3"
DEST_FOLDER = "output"

SOURCE_FOLDERS = [FOLDER1, FOLDER2, FOLDER3]

# Map each folder to its suffix
SUFFIX_MAP = {
    FOLDER1: "RBC",
    FOLDER2: "PLT",
    FOLDER3: "WBC"
}

def setup_test_environment():
    """Create folders and some test .bmp files if they don't exist."""
    for idx, folder in enumerate(SOURCE_FOLDERS, start=1):
        os.makedirs(folder, exist_ok=True)
        # Create 3 dummy bmp files per folder if empty
        if not os.listdir(folder):
            for j in range(1, 4):
                file_path = os.path.join(folder, f"test{idx}{j}.bmp")
                with open(file_path, "wb") as f:
                    f.write(b"BM")  # minimal BMP header placeholder

    os.makedirs(DEST_FOLDER, exist_ok=True)

def pick_and_copy(user_number):
    """Pick one random file from each folder and copy to output with new fixed name."""
    for folder in SOURCE_FOLDERS:
        files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]

        if not files:
            print(f"No files found in {folder}, skipping.")
            continue

        # Pick a random file
        chosen_file = random.choice(files)

        # New name based on folder type
        suffix = SUFFIX_MAP[folder]
        new_name = f"{user_number}{suffix}.bmp"

        # Source and destination paths
        src_path = os.path.join(folder, chosen_file)
        dest_path = os.path.join(DEST_FOLDER, new_name)

        shutil.copy2(src_path, dest_path)
        print(f"Copied from {folder}: {chosen_file} → {new_name}")

if __name__ == "__main__":
    setup_test_environment()
    user_number = input("Enter a number: ").strip()
    pick_and_copy(user_number)
    print("\n✅ Done! Files copied to 'output' folder with new names.")