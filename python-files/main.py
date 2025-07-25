import tkinter as tk
from tkinter import filedialog
import os
import shutil
import zipfile
import sys
import time

BANNER = """-- ██████╗░███████╗██████╗░██╗░░░░░███████╗░█████╗░██╗░░██╗░██████╗
-- ██╔══██╗██╔════╝██╔══██╗██║░░░░░██╔════╝██╔══██╗██║░██╔╝██╔════╝
-- ██████╔╝█████╗░░██║░░██║██║░░░░░█████╗░░███████║█████═╝░╚█████╗░
-- ██╔══██╗██╔══╝░░██║░░██║██║░░░░░██╔══╝░░██╔══██║██╔═██╗░░╚═══██╗
-- ██║░░██║███████╗██████╔╝███████╗███████╗██║░░██║██║░╚██╗██████╔╝
-- ╚═╝░░╚═╝╚══════╝╚═════╝░╚══════╝╚══════╝╚═╝░░╚═╝╚═╝░░╚═╝╚═════╝░

--  This File Leaked By RedLeaks Team, Join Our Server For More
--  DISCORD: - discord.gg/nwtKnk8hvG discord.gg/redleaks
"""

URL_CONTENT = """[InternetShortcut]
URL=https://discord.gg/redleaks
"""

def copy_to_output_folder(source_dir):
    folder_name = os.path.basename(source_dir.rstrip("\\/"))
    target_dir = os.path.join("output", folder_name)

    if os.path.exists(target_dir):
        print(f"[!] Removing existing output: {target_dir}")
        shutil.rmtree(target_dir)

    shutil.copytree(source_dir, target_dir)
    print(f"[✓] Copied to: {target_dir}")
    return target_dir

def zip_output_folder(folder_path):
    folder_name = os.path.basename(folder_path)
    zip_dir = "output_zips"
    os.makedirs(zip_dir, exist_ok=True)
    zip_path = os.path.join(zip_dir, f"{folder_name}.zip")
    print(f"[ZIP] Creating archive: {zip_path}")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(folder_path):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, folder_path)
                zipf.write(full_path, arcname)
    print(f"[✓] Zipped to {zip_path}")

def is_already_modified(content):
    return "This File Leaked By RedLeaks Team" in content

def generate_files(base_dir):
    folder_count = 0
    lua_file_count = 0

    print(f"\n[INFO] Processing: {base_dir}")

    for root, dirs, files in os.walk(base_dir):
        print(f"[+] Folder: {root}")

        # readme.txt
        readme_path = os.path.join(root, "readme.txt")
        with open(readme_path, "w", encoding="utf-8") as f:
            for _ in range(10):
                f.write(BANNER + "\n\n")
        print("    ✔ readme.txt created")

        # .url shortcut
        url_path = os.path.join(root, "best fivem leak server.url")
        with open(url_path, "w", encoding="utf-8") as f:
            f.write(URL_CONTENT)
        print("    ✔ URL shortcut created")

        # .lua file injection
        for filename in files:
            if filename.lower().endswith(".lua"):
                file_path = os.path.join(root, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as lua_file:
                        content = lua_file.read()

                    if is_already_modified(content):
                        print(f"    ↩ Skipped {filename} (already modified)")
                        continue

                    top = (BANNER + "\n\n") * 10
                    bottom = ("\n\n" + BANNER) * 10
                    new_content = top + content + bottom

                    with open(file_path, "w", encoding="utf-8") as lua_file:
                        lua_file.write(new_content)

                    print(f"    ✔ Modified {filename}")
                    lua_file_count += 1
                except Exception as e:
                    print(f"    ✖ Failed to modify {filename}: {e}")

        folder_count += 1

    print(f"\n[✓] Completed. Folders: {folder_count} | Modified .lua files: {lua_file_count}")

def process_batch(folders):
    start = time.time()
    print("╔════════════════════════════════════════════╗")
    print("║         RedLeaks Batch Deployment         ║")
    print("╚════════════════════════════════════════════╝\n")

    for folder in folders:
        print(f"📁 Selected: {folder}")
        if not os.path.isdir(folder):
            print(f"[!] Skipped invalid folder: {folder}")
            continue
        copied = copy_to_output_folder(folder)
        generate_files(copied)
        zip_output_folder(copied)
        print("────────────────────────────────────────────")

    elapsed = time.time() - start
    print(f"\n⏱️ Operation completed in {elapsed:.2f} seconds.\n")

def open_gui_and_run():
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(mustexist=True, title="Select folder to copy & modify")
    if selected:
        process_batch([selected])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Drag & drop mode
        folders = sys.argv[1:]
        process_batch(folders)
    else:
        open_gui_and_run()
