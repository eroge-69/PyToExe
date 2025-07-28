import os
import shutil

def sync_folders(source, destination):
    if not os.path.exists(source):
        print(f"[!] Source not found: {source}")
        return
    
    if not os.path.exists(destination):
        os.makedirs(destination)
        print(f"[+] Created destination folder: {destination}")

    for root, dirs, files in os.walk(source):
        rel_path = os.path.relpath(root, source)
        dest_dir = os.path.join(destination, rel_path)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            print(f"[+] Created folder: {dest_dir}")

        for file in files:
            src_file = os.path.join(root, file)
            dst_file = os.path.join(dest_dir, file)

            # Check if file is new or modified
            if not os.path.exists(dst_file):
                shutil.copy2(src_file, dst_file)
                print(f"[+] Copied new: {dst_file}")
            else:
                if os.path.getmtime(src_file) > os.path.getmtime(dst_file):
                    shutil.copy2(src_file, dst_file)
                    print(f"[*] Updated: {dst_file}")

def sync_multiple(pairs):
    for source, destination in pairs:
        print(f"\n=== Syncing ===\nFrom: {source}\nTo:   {destination}")
        sync_folders(source, destination)

if __name__ == "__main__":
    folder_pairs = [
        (r"\\10.103.63.36\jrllab\TB\TB Application",     r"E:\OneDrive - King Faisal University\TB_Python_Task\TB Applicatio"),
        (r"\\10.103.63.36\jrllab\TB\TB DASHBORAD",   r"E:\OneDrive - King Faisal University\TB_Python_Task\TB DASHBORAD"),
        (r"\\10.103.63.36\jrllab\Inventory", r"E:\OneDrive - King Faisal University\TB_Python_Task\Inventory"),
        # Add more (source, destination) pairs as needed
    ]

    sync_multiple(folder_pairs)