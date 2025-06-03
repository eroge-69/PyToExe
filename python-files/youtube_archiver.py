import os
import tkinter as tk
from tkinter import filedialog, messagebox
import requests

# Download a single video
def download_video(video_id, save_folder):
    url = f"https://web.archive.org/web/2oe_/http://wayback-fakeurl.archive.org/yt/{video_id}"
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(save_folder, f"{video_id}.mp4")
            with open(file_path, "wb") as f:
                for chunk in response.iter_content(8192):
                    f.write(chunk)
            return True
        else:
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Start download process
def start_download():
    ids = text_box.get("1.0", tk.END).strip().splitlines()
    folder = folder_path.get()

    if not ids:
        messagebox.showerror("Error", "Please enter at least one video ID.")
        return

    if not folder:
        messagebox.showerror("Error", "Please choose a download folder.")
        return

    for video_id in ids:
        success = download_video(video_id.strip(), folder)
        status = "Downloaded" if success else "Failed"
        output_box.insert(tk.END, f"{status}: {video_id.strip()}\n")
    output_box.insert(tk.END, "Done!\n")

# Choose folder
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_path.set(folder)

# GUI setup
root = tk.Tk()
root.title("YouTube Archive Downloader")
root.geometry("500x500")

# Video ID input
tk.Label(root, text="Enter YouTube Video IDs (one per line):").pack(pady=5)
text_box = tk.Text(root, height=10, width=60)
text_box.pack()

# Folder chooser
folder_path = tk.StringVar()
tk.Button(root, text="Choose Download Folder", command=browse_folder).pack(pady=5)
tk.Label(root, textvariable=folder_path).pack()

# Start download button
tk.Button(root, text="Start Download", command=start_download).pack(pady=10)

# Output box
tk.Label(root, text="Download Status:").pack()
output_box = tk.Text(root, height=10, width=60)
output_box.pack()

root.mainloop()
