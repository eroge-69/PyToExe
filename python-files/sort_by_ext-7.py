# -*- coding: utf-8 -*-
"""
Created on Sun Aug 24 19:18:20 2025

@author: Administrator
"""

import os
import shutil
import hashlib
from datetime import datetime
import time
import platform

def get_file_hash(filepath):
    """Calculate MD5 hash of a file with improved error handling"""
    hash_md5 = hashlib.md5()
    try:
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        if not os.access(filepath, os.R_OK):
            raise PermissionError(f"No read permission: {filepath}")
        if not os.path.isfile(filepath):
            raise IsADirectoryError(f"Not a file: {filepath}")

        file_size = os.path.getsize(filepath)
        if file_size > 100 * 1024 * 1024:  # >100MB
            print("~", end='', flush=True)

        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        raise Exception(f"Hash calculation failed for {filepath}: {str(e)}")

def log_problematic_file(log_file, filename, source_path, error, attempted_dest=None):
    """Log problematic files to a dedicated log file with formatting"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = [
            f"\n[{timestamp}] Problematic File: {filename}",
            f"Source Path: {source_path}",
            f"Error Type: {type(error).__name__}" if not isinstance(error, str) else "Error Type: StringError",
            f"Error Details: {str(error)}"
        ]
        if attempted_dest:
            log_entry.append(f"Attempted Destination: {attempted_dest}")
        log_entry.append("-" * 50)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n".join(log_entry) + "\n")
    except Exception as e:
        print(f"CRITICAL: Failed to write to log file: {str(e)}")

def get_user_input(prompt):
    """Get validated user input for directory paths"""
    while True:
        path = input(prompt).strip()
        if not path:
            print("Error: Please enter a non-empty path.")
            continue
        path = os.path.expanduser(os.path.expandvars(path))
        return os.path.normpath(path)

def handle_file_move(source_path, dest_path):
    """Move file safely with retries and duplicate renaming"""
    try:
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source file not found: {source_path}")

        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)

        if os.path.exists(dest_path):
            base, ext = os.path.splitext(dest_path)
            counter = 1
            while os.path.exists(f"{base}_{counter}{ext}"):
                counter += 1
            dest_path = f"{base}_{counter}{ext}"

        if platform.system() == 'Windows':
            try:
                shutil.move(source_path, dest_path)
            except PermissionError:
                time.sleep(0.1)
                shutil.move(source_path, dest_path)
        else:
            shutil.move(source_path, dest_path)
        return dest_path
    except Exception as e:
        raise Exception(f"File move error: {str(e)}")

def create_directory_safely(dir_path):
    try:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        raise Exception(f"Error creating directory {dir_path}: {str(e)}")

def sort_files_by_extension():
    print("\n=== File Sorter ===")
    source_dir = get_user_input("Enter source directory to sort from: ")
    destination_dir = get_user_input("Enter destination directory for sorted files: ")

    if not os.path.exists(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
    create_directory_safely(destination_dir)

    start_time = time.time()
    processed_count = duplicate_count = problematic_count = other_issues_count = skipped_count = 0

    parent_dir = os.path.dirname(os.path.abspath(destination_dir))
    unknown_dir = os.path.join(parent_dir, "000-unknown")
    duplicate_dir = os.path.join(parent_dir, "000-duplicate")
    empty_dir = os.path.join(parent_dir, "000-empty-dir")
    skipped_dir = os.path.join(parent_dir, "000-skipped")
    problematic_dir = os.path.join(parent_dir, "000-problematic")
    problematic_log = os.path.join(parent_dir, "problematic_files.log")

    for d in [unknown_dir, duplicate_dir, empty_dir, skipped_dir, problematic_dir]:
        create_directory_safely(d)

    with open(problematic_log, 'w', encoding='utf-8') as f:
        f.write(f"Problematic Files Log - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Source: {source_dir}\nDest: {destination_dir}\n")
        f.write("=" * 50 + "\n")

    known_hashes = set()
    directories_to_check = set()

    print("\nStarting file sorting...")
    print("'.' = Sorted, '*' = Duplicate, '!' = Problematic, '?' = Other, '~' = Large File, 'K' = Skipped\n")

    for root, dirs, files in os.walk(source_dir, topdown=True):
        dirs[:] = [d for d in dirs if not (d.startswith('.') or d.startswith('$'))]
        directories_to_check.add(root)

        for filename in files:
            source_path = os.path.join(root, filename)

            # Handle skipped files
            if filename.startswith('.') or filename.startswith('$') or filename == 'desktop.ini':
                skipped_count += 1
                dest_path = os.path.join(skipped_dir, filename)
                try:
                    handle_file_move(source_path, dest_path)
                    print('K', end='', flush=True)
                except Exception as e:
                    print('!', end='', flush=True)
                    log_problematic_file(problematic_log, filename, source_path, e)
                continue

            if any(d in source_path for d in [destination_dir, unknown_dir, duplicate_dir, empty_dir, skipped_dir, problematic_dir]):
                continue

            try:
                file_hash = get_file_hash(source_path)

                if file_hash in known_hashes:
                    dest_path = os.path.join(duplicate_dir, filename)
                    handle_file_move(source_path, dest_path)
                    duplicate_count += 1
                    print('*', end='', flush=True)
                    continue
                known_hashes.add(file_hash)

                _, ext = os.path.splitext(filename)
                ext = ext.lower().strip(".")

                if ext:
                    ext_folder = os.path.join(destination_dir, ext)
                    create_directory_safely(ext_folder)
                    dest_path = os.path.join(ext_folder, filename)
                else:
                    dest_path = os.path.join(unknown_dir, filename)

                handle_file_move(source_path, dest_path)
                processed_count += 1
                print('.', end='', flush=True)

            except Exception as e:
                problematic_count += 1
                log_problematic_file(problematic_log, filename, source_path, e)
                try:
                    dest_path = os.path.join(problematic_dir, filename)
                    handle_file_move(source_path, dest_path)
                except Exception as move_err:
                    log_problematic_file(problematic_log, filename, source_path, f"Failed final move: {move_err}")
                print('!', end='', flush=True)

    # Handle empty directories
    for directory in sorted(directories_to_check, key=lambda x: -len(x)):
        if directory in [source_dir, destination_dir, unknown_dir, duplicate_dir, empty_dir, skipped_dir, problematic_dir]:
            continue
        try:
            if not os.listdir(directory):
                dest_path = os.path.join(empty_dir, os.path.basename(directory))
                counter = 1
                while os.path.exists(dest_path):
                    dest_path = f"{dest_path}_{counter}"
                    counter += 1
                shutil.move(directory, dest_path)
        except Exception as e:
            other_issues_count += 1
            log_problematic_file(problematic_log, f"Directory: {os.path.basename(directory)}", directory, str(e))
            try:
                dest_path = os.path.join(problematic_dir, os.path.basename(directory))
                handle_file_move(directory, dest_path)
            except Exception as move_err:
                log_problematic_file(problematic_log, directory, directory, f"Failed final dir move: {move_err}")
            print('!', end='', flush=True)

    elapsed_time = time.time() - start_time
    print("\n\n=== SORTING COMPLETE ===")
    print(f"Sorted: {processed_count}, Duplicates: {duplicate_count}, Problematic: {problematic_count}, Other: {other_issues_count}, Skipped: {skipped_count}")
    print(f"Time: {elapsed_time:.2f}s")
    print(f"Logs: {problematic_log}\nUnknown: {unknown_dir}\nDuplicate: {duplicate_dir}\nEmpty: {empty_dir}\nSkipped: {skipped_dir}\nProblematic: {problematic_dir}")

if __name__ == "__main__":
    try:
        sort_files_by_extension()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")