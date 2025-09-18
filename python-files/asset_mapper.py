import os
import shutil
import sys

# Stats
total_scanned = 0
total_moved = 0
total_duplicates = 0
total_errors = 0
fallback_used = 0

THIS_SCRIPT = os.path.basename(__file__)

def safe_move(src, dest, fallback_dir):
    """File ko safe move karta hai with duplicate handling"""
    global total_moved, total_duplicates, total_errors, fallback_used
    try:
        if dest is None:
            dest = os.path.join(fallback_dir, os.path.basename(src))
            fallback_used += 1

        base, ext = os.path.splitext(dest)
        counter = 1
        new_dest = dest

        while os.path.exists(new_dest):
            new_dest = f"{base}_{counter}{ext}"
            counter += 1
            total_duplicates += 1

        os.makedirs(os.path.dirname(new_dest), exist_ok=True)
        shutil.move(src, new_dest)

        total_moved += 1
        print(f"[MOVED] {src} -> {new_dest}")

    except Exception as e:
        total_errors += 1
        print(f"[ERROR] Could not move {src} -> {dest} | {e}")

def extract_files(unpack_dir, output_dir):
    global total_scanned
    for root, dirs, files in os.walk(unpack_dir):
        for file in files:
            if file.endswith(".py") or file == THIS_SCRIPT:
                print(f"[SKIP] Ignored script file: {file}")
                continue

            total_scanned += 1
            src_path = os.path.join(root, file)

            # abhi hum file ke andar se real path detect karne ka logic add kar sakte hain
            rel_path = os.path.relpath(src_path, unpack_dir)
            if rel_path.strip() == "" or rel_path.startswith("file_"):
                dest_path = None
            else:
                dest_path = os.path.join(output_dir, rel_path)

            safe_move(src_path, dest_path, output_dir)

if __name__ == "__main__":
    # Default: script ke folder ka path
    script_dir = os.path.dirname(os.path.abspath(__file__))

    unpack_dir = input(f"Enter source (UNPACK) folder [default={script_dir}]: ").strip()
    if unpack_dir == "":
        unpack_dir = script_dir

    output_dir = input(f"Enter destination (Content) folder [default={os.path.join(script_dir,'Content')}]: ").strip()
    if output_dir == "":
        output_dir = os.path.join(script_dir, "Content")

    print(f"\n[INFO] Using source: {unpack_dir}")
    print(f"[INFO] Using destination: {output_dir}\n")

    extract_files(unpack_dir, output_dir)

    print("\n=== Summary ===")
    print(f"Total files scanned: {total_scanned}")
    print(f"Files successfully moved: {total_moved}")
    print(f"Duplicate handled (renamed): {total_duplicates}")
    print(f"Fallback used (no path found): {fallback_used}")
    print(f"Errors: {total_errors}")
    print(f"Output directory: {output_dir}")