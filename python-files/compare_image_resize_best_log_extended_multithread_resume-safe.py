import os
import shutil
import csv
import json
from PIL import Image
import imagehash
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def process_image(file_path, hash_size):
    """Compute perceptual hash, resolution, and file size for one image."""
    try:
        with Image.open(file_path) as img:
            img_hash = imagehash.phash(img, hash_size=hash_size)
            resolution = img.width * img.height
        file_size = os.path.getsize(file_path)
        return (file_path, img_hash, resolution, file_size)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def load_processed_from_log(log_file, log_format):
    """Load already processed file paths from an existing log (if any)."""
    processed = set()
    if os.path.exists(log_file):
        try:
            if log_format.lower() == "csv":
                with open(log_file, newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        processed.add(row["Kept File"])
                        processed.add(row["Duplicate Removed"])
            elif log_format.lower() == "json":
                with open(log_file, encoding="utf-8") as f:
                    entries = json.load(f)
                    for entry in entries:
                        processed.add(entry["kept_file"])
                        processed.add(entry["duplicate_removed"])
        except Exception as e:
            print(f"⚠️ Could not load log file {log_file}: {e}")
    return processed

def save_log(log_entries, log_file, log_format):
    """Save log entries to CSV or JSON (append if exists)."""
    if log_format.lower() == "csv":
        file_exists = os.path.exists(log_file)
        with open(log_file, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:  # Write header if new file
                writer.writerow(["Kept File", "Duplicate Removed", "Reason"])
            for entry in log_entries:
                writer.writerow([entry["kept_file"], entry["duplicate_removed"], entry["reason"]])
    elif log_format.lower() == "json":
        existing = []
        if os.path.exists(log_file):
            with open(log_file, encoding="utf-8") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    pass
        existing.extend(log_entries)
        with open(log_file, mode="w", encoding="utf-8") as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
    else:
        print(f"⚠️ Unsupported log format: {log_format}. No log saved.")

def find_and_move_duplicates(src_folder,
                             dup_folder="duplicates",
                             log_file="duplicates_log.csv",
                             log_format="csv",
                             hash_size=16,
                             threshold=5,
                             extensions=(".jpg", ".jpeg", ".png", ".gif", ".bmp"),
                             max_workers=8):
    """
    Multi-threaded + resume-safe duplicate finder.
    Keeps highest-resolution/size image, moves duplicates, logs decisions.
    Skips already-processed files on rerun.
    Key resume-safe features:
Loads previous CSV/JSON log and skips those files.
Appends new results to the existing log.
If interrupted, just run again → it will continue where it left off.
    """
    if not os.path.exists(dup_folder):
        os.makedirs(dup_folder)

    # Load already processed files
    processed_files = load_processed_from_log(log_file, log_format)
    print(f"Resuming... {len(processed_files)} file(s) already logged.")

    # Collect candidate files
    all_files = []
    for root, _, files in os.walk(src_folder):
        for file in files:
            if file.lower().endswith(extensions):
                full_path = os.path.join(root, file)
                if full_path not in processed_files:
                    all_files.append(full_path)

    print(f"Found {len(all_files)} new images to process.")

    # Process images in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_image, f, hash_size): f for f in all_files}
        for future in as_completed(future_to_file):
            result = future.result()
            if result:
                results.append(result)

    print("Hashing complete. Checking for duplicates...")

    # Shared data
    seen = []  # list of (hash, filepath, resolution, file_size)
    log_entries = []
    duplicate_count = 0
    lock = threading.Lock()

    for file_path, img_hash, resolution, file_size in results:
        is_duplicate = False
        with lock:
            for i, (seen_hash, seen_file, seen_res, seen_size) in enumerate(seen):
                if abs(img_hash - seen_hash) <= threshold:
                    is_duplicate = True
                    if resolution > seen_res or (resolution == seen_res and file_size > seen_size):
                        # Current file is better → move old one
                        duplicate_count += 1
                        new_path = os.path.join(dup_folder, os.path.basename(seen_file))

                        base, ext = os.path.splitext(os.path.basename(seen_file))
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(dup_folder, f"{base}_{counter}{ext}")
                            counter += 1

                        shutil.move(seen_file, new_path)
                        print(f"[DUPLICATE] {seen_file} → {new_path} (kept {file_path})")

                        log_entries.append({
                            "kept_file": file_path,
                            "duplicate_removed": seen_file,
                            "reason": "Replaced with higher resolution/size"
                        })

                        # Replace old with new
                        seen[i] = (img_hash, file_path, resolution, file_size)
                    else:
                        # Current file is worse → move it
                        duplicate_count += 1
                        new_path = os.path.join(dup_folder, os.path.basename(file_path))

                        base, ext = os.path.splitext(os.path.basename(file_path))
                        counter = 1
                        while os.path.exists(new_path):
                            new_path = os.path.join(dup_folder, f"{base}_{counter}{ext}")
                            counter += 1

                        shutil.move(file_path, new_path)
                        print(f"[DUPLICATE] {file_path} → {new_path} (kept {seen_file})")

                        log_entries.append({
                            "kept_file": seen_file,
                            "duplicate_removed": file_path,
                            "reason": "Kept existing higher resolution/size"
                        })
                    break

            if not is_duplicate:
                seen.append((img_hash, file_path, resolution, file_size))

    # Save new log entries (append)
    save_log(log_entries, log_file, log_format)

    print(f"\nDone! {duplicate_count} duplicate(s) moved to '{dup_folder}'. Log updated at '{log_file}'.")

# Example usage
if __name__ == "__main__":
    source_folder = "images"   # Replace with your folder path
    find_and_move_duplicates(source_folder,
                             dup_folder="duplicates",
                             log_file="duplicates_log.json",   # or "duplicates_log.csv"
                             log_format="json",                # "csv" or "json"
                             hash_size=16,
                             threshold=5,
                             extensions=(".jpg", ".jpeg", ".png", ".gif", ".bmp"),
                             max_workers=8)                    # number of threads
