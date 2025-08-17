import os
import shutil
import sys
import ctypes


def get_to_keep(root_dir):
    # 1. Config file
    config_path = os.path.join(root_dir, 'list_of_file_to_keep.txt')
    if os.path.isfile(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            keep = [line.strip() for line in f if line.strip()]
            if keep:
                print(f"Using config file list_of_file_to_keep.txt: {keep}")
                return keep

    # 2. Command-line argument
    if len(sys.argv) > 1:
        keep = sys.argv[1:]
        print(f"Using files/folders from command line: {keep}")
        return keep

    # 3. Interactive input
    print("Enter comma-separated names of files/folders to keep:")
    user_input = input("To keep: ")
    keep = [x.strip() for x in user_input.split(',') if x.strip()]
    print(f"Using user input: {keep}")
    return keep

def main():

    root_dir = os.path.abspath(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__))
    items_in_root = set(os.listdir(root_dir))
    memory_list = list(items_in_root)

    mods_disabled_dir = os.path.join(root_dir, "mods_disabled")
    if not os.path.exists(mods_disabled_dir):
        os.mkdir(mods_disabled_dir)

    to_keep = get_to_keep(root_dir)
    # Always keep mods_disabled itself
    to_keep.append("mods_disabled")

    for item in items_in_root:
        if item in to_keep:
            continue
        src_path = os.path.join(root_dir, item)
        dest_path = os.path.join(mods_disabled_dir, item)
        try:
            shutil.move(src_path, dest_path)
            print(f"Moved {item} to mods_disabled")
        except Exception as e:
            print(f"Could not move {item}: {e}")

if __name__ == "__main__":
    main()
