import os
import re
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

# Regex pattern to extract show name, season, and episode
FILENAME_PATTERN = re.compile(
    r'(?P<show>.+?)[. _-]+[Ss](?P<season>\d{1,2})[Ee](?P<episode>\d{1,2})',
    re.IGNORECASE
)

def normalize_filename(filename):
    match = FILENAME_PATTERN.search(filename)
    if not match:
        return None

    show_raw = match.group('show')
    season = int(match.group('season'))
    episode = int(match.group('episode'))
    ext = Path(filename).suffix

    show_clean = re.sub(r'[._-]+', ' ', show_raw).strip().title()
    new_name = f"{show_clean} - S{season:02d}E{episode:02d}{ext}"
    return new_name

def rename_files_in_directory(directory):
    renamed = 0
    skipped = 0
    for file in os.listdir(directory):
        full_path = os.path.join(directory, file)
        if os.path.isfile(full_path):
            new_name = normalize_filename(file)
            if new_name:
                new_path = os.path.join(directory, new_name)
                try:
                    os.rename(full_path, new_path)
                    print(f"✅ Renamed: {file} → {new_name}")
                    renamed += 1
                except Exception as e:
                    print(f"❌ Error renaming {file}: {e}")
            else:
                print(f"⚠️ Skipped: {file} (no match)")
                skipped += 1
    messagebox.showinfo("Done", f"Renamed: {renamed} files\nSkipped: {skipped} files")

def pick_folder_and_run():
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    folder = filedialog.askdirectory(title="Select TV Show Folder")
    if folder:
        rename_files_in_directory(folder)
    else:
        messagebox.showwarning("Cancelled", "No folder selected.")

if __name__ == "__main__":
    pick_folder_and_run()
