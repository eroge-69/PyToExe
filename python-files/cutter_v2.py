import os
import math
import subprocess
import ffmpeg
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

# ✅ FFmpeg/FFprobe path override (set this if not in PATH)
FFMPEG_PATH = "C:/ffmpeg/bin/ffmpeg.exe"       # or full path like: "C:/ffmpeg/bin/ffmpeg.exe"
FFPROBE_PATH = "C:/ffmpeg/bin/ffprobe.exe"     # or full path like: "C:/ffmpeg/bin/ffprobe.exe"

# ✅ Get duration using ffprobe
def get_duration(path):
    try:
        result = subprocess.run(
            [FFPROBE_PATH, "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        return float(result.stdout.strip())
    except Exception as e:
        messagebox.showerror("Error", f"FFprobe error:\n{str(e)}")
        return None

# ✅ Split the video
def split_video_ffmpeg(path, interval_seconds, progress_callback):
    duration = get_duration(path)
    if duration is None:
        return

    filename = os.path.splitext(os.path.basename(path))[0]
    ext = os.path.splitext(path)[1]
    output_dir = os.path.join(os.path.dirname(path), f"{filename}_splits")
    os.makedirs(output_dir, exist_ok=True)

    total_parts = math.ceil(duration / interval_seconds)
    for i in range(total_parts):
        start = i * interval_seconds
        output_file = os.path.join(output_dir, f"{filename}_part{i+1}{ext}")

        try:
            (
                ffmpeg
                .input(path, ss=start, t=interval_seconds)
                .output(output_file, c='copy')
                .run(cmd=FFMPEG_PATH, overwrite_output=True, quiet=True)
            )
            progress_callback(i + 1, total_parts)
        except Exception as e:
            messagebox.showerror("FFmpeg Error", f"Error splitting part {i+1}:\n{str(e)}")
            break

    return output_dir

# ✅ File browse
def browse_file():
    path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.mkv *.avi *.mov")])
    if path:
        file_path_var.set(path)

# ✅ Start split
def start_cutting():
    path = file_path_var.get()
    if not path:
        messagebox.showerror("Error", "Please select a video file.")
        return

    try:
        interval = int(interval_entry.get()) * 60
        if interval <= 0:
            raise ValueError
    except:
        messagebox.showerror("Error", "Invalid interval. Use number (minutes).")
        return

    progress_bar["value"] = 0
    root.update_idletasks()

    def progress_callback(done, total):
        percent = int((done / total) * 100)
        progress_bar["value"] = percent
        root.update_idletasks()

    output = split_video_ffmpeg(path, interval, progress_callback)
    if output:
        messagebox.showinfo("Success", f"Split completed!\nSaved in:\n{output}")

# ✅ GUI Setup
root = tk.Tk()
root.title("Video Cutter - Every N Minutes (FFmpeg Fast Mode)")
root.geometry("500x300")

file_path_var = tk.StringVar()

tk.Label(root, text="Select Video File:", font=('Arial', 11)).pack(pady=10)
tk.Entry(root, textvariable=file_path_var, width=55).pack()
tk.Button(root, text="Browse", command=browse_file).pack(pady=5)

tk.Label(root, text="Split every N minutes:", font=('Arial', 11)).pack(pady=10)
interval_entry = tk.Entry(root, width=10, justify='center')
interval_entry.insert(0, "10")
interval_entry.pack()

tk.Button(root, text="Start Splitting", command=start_cutting, bg="#4CAF50", fg="white", padx=10, pady=5).pack(pady=15)

progress_bar = Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)

tk.Label(root, text="Made by Mama 😎", font=('Arial', 9, 'italic')).pack(pady=5)

root.mainloop()
