import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

VIDEO_EXTENSIONS = ('.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv')

def get_video_height(filepath):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=height', '-of', 'csv=p=0', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return int(result.stdout.strip())
    except Exception as e:
        return None

def rename_video_file(filepath, height, log_func):
    dir_name, original_name = os.path.split(filepath)
    name, ext = os.path.splitext(original_name)
    resolution_map = {480: "480p", 720: "720p", 1080: "1080p"}

    if height not in resolution_map:
        return

    resolution_tag = f"- {resolution_map[height]}"
    if resolution_tag in name:
        log_func(f"[SKIP] {original_name} already has tag.")
        return

    new_name = f"{name} {resolution_tag}{ext}"
    new_path = os.path.join(dir_name, new_name)
    os.rename(filepath, new_path)
    log_func(f"[RENAMED] {original_name} → {new_name}")

def process_directory(directory, log_func):
    files_found = False
    for filename in os.listdir(directory):
        if filename.lower().endswith(VIDEO_EXTENSIONS):
            files_found = True
            full_path = os.path.join(directory, filename)
            height = get_video_height(full_path)
            if height:
                rename_video_file(full_path, height, log_func)
            else:
                log_func(f"[ERROR] Could not read resolution: {filename}")
    if not files_found:
        log_func("[INFO] No video files found in folder.")

# GUI Setup
class VideoRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Renamer by Resolution")
        self.folder_path = ""

        self.frame = tk.Frame(root, padx=10, pady=10)
        self.frame.pack()

        self.select_button = tk.Button(self.frame, text="Select Folder", command=self.select_folder)
        self.select_button.grid(row=0, column=0, padx=5, pady=5)

        self.rename_button = tk.Button(self.frame, text="Rename Videos", command=self.rename_videos)
        self.rename_button.grid(row=0, column=1, padx=5, pady=5)

        self.status_box = scrolledtext.ScrolledText(self.frame, width=60, height=20)
        self.status_box.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

    def log(self, message):
        self.status_box.insert(tk.END, message + '\n')
        self.status_box.see(tk.END)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path = folder
            self.log(f"[FOLDER SELECTED] {folder}")

    def rename_videos(self):
        if not self.folder_path:
            messagebox.showwarning("No folder selected", "Please select a folder first.")
            return
        self.log("[STARTING] Renaming videos...")
        process_directory(self.folder_path, self.log)
        self.log("[DONE]")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoRenamerApp(root)
    root.mainloop()
