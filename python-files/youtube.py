import tkinter as tk
from tkinter import messagebox
import subprocess
import threading
import os
import sys
import platform

def download_video():
    url = url_entry.get().strip()
    start = start_entry.get().strip()
    end = end_entry.get().strip()

    if not url:
        messagebox.showerror("Input Error", "Please enter a YouTube URL.")
        return

    # Find the directory where this script is running
    script_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

    # Path to yt-dlp in the same folder
    yt_dlp_file = "yt-dlp.exe" if platform.system() == "Windows" else "yt-dlp"
    yt_dlp_path = os.path.join(script_dir, yt_dlp_file)

    if not os.path.isfile(yt_dlp_path):
        messagebox.showerror("yt-dlp Not Found", f"yt-dlp was not found in:\n{yt_dlp_path}")
        return

    # Output file path with safe filename
    output_path = os.path.join(script_dir, "%(title)s.%(ext)s")

    # Construct yt-dlp command
    cmd = [
        yt_dlp_path,
        "--restrict-filenames",                # Avoid illegal characters
        "-f", "bv*+ba",
        "--merge-output-format", "mp4",
        "-o", output_path
    ]

    if start and end:
        cmd += ["--postprocessor-args", f"-ss {start} -to {end}"]

    cmd.append(url)

    # Disable the button and update status
    download_btn.config(state=tk.DISABLED)
    status_label.config(text="Downloading...")

    def run():
        try:
            print("Running command:", " ".join(cmd))  # Debug
            subprocess.run(cmd, check=True)
            status_label.config(text="✅ Download completed!")
        except subprocess.CalledProcessError as e:
            status_label.config(text="❌ Download failed.")
            messagebox.showerror("Download Error", str(e))
        finally:
            download_btn.config(state=tk.NORMAL)

    threading.Thread(target=run).start()

# GUI Setup
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("450x300")
root.resizable(False, False)

tk.Label(root, text="YouTube URL:").pack(pady=5)
url_entry = tk.Entry(root, width=55)
url_entry.pack()

tk.Label(root, text="Start Time (optional, e.g., 00:01:00):").pack(pady=5)
start_entry = tk.Entry(root, width=20)
start_entry.pack()

tk.Label(root, text="End Time (optional, e.g., 00:02:00):").pack(pady=5)
end_entry = tk.Entry(root, width=20)
end_entry.pack()

download_btn = tk.Button(root, text="Download", command=download_video)
download_btn.pack(pady=15)

status_label = tk.Label(root, text="")
status_label.pack(pady=5)

root.mainloop()
