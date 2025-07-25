import os
import hashlib
import shutil

def get_file_hash(filepath):
    """Compute SHA256 hash of a file."""
    hash_func = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def sync_folders(folder1, folder2):
    # Hashes of files in folder2 for comparison
    folder2_hashes = {
        get_file_hash(os.path.join(folder2, fname))
        for fname in os.listdir(folder2)
        if os.path.isfile(os.path.join(folder2, fname))
    }

    for fname in os.listdir(folder1):
        f1_path = os.path.join(folder1, fname)
        if os.path.isfile(f1_path):
            file_hash = get_file_hash(f1_path)

            if file_hash in folder2_hashes:
                # Duplicate found in folder2 — do nothing
                continue
            else:
                # File not in folder2 — copy it over
                dest_path = os.path.join(folder2, fname)
                print(f"Copying new file to folder2: {dest_path}")
                shutil.copy2(f1_path, dest_path)

    # Optional: remove exact duplicates from folder2
    folder1_hashes = {
        get_file_hash(os.path.join(folder1, fname))
        for fname in os.listdir(folder1)
        if os.path.isfile(os.path.join(folder1, fname))
    }

    for fname in os.listdir(folder2):
        f2_path = os.path.join(folder2, fname)
        if os.path.isfile(f2_path):
            file_hash = get_file_hash(f2_path)
            if file_hash in folder1_hashes:
                # Duplicate detected — already handled above
                continue

# 🛠 Example usage
folder1_path = "/path/to/folder1"
folder2_path = "/path/to/folder2"
sync_folders(folder1_path, folder2_path)
