import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import os

# Function to hardsub with selected mode
def hardsub():
    video_path = filedialog.askopenfilename(title="Select Video", filetypes=[("MP4 files", "*.mp4")])
    if not video_path:
        return

    subtitle_path = filedialog.askopenfilename(title="Select ASS Subtitle", filetypes=[("ASS Subtitle", "*.ass")])
    if not subtitle_path:
        return

    output_path = os.path.splitext(video_path)[0] + "_hardsub.mkv"

    # Ask user to choose mode
    mode = mode_var.get()

    if mode == "crf":
        cq_value = cq_entry.get()
        if not cq_value.isdigit():
            messagebox.showerror("Error", "Invalid CRF/CQ value.")
            return
        ffmpeg_cmd = [
            "ffmpeg", "-hwaccel", "cuda",
            "-i", video_path,
            "-vf", f"ass={subtitle_path}",
            "-c:v", "hevc_nvenc", "-cq", cq_value, "-preset", "slow",
            "-c:a", "copy",
            output_path
        ]
    else:
        # Get bitrate using ffprobe
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=bit_rate",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]
        try:
            result = subprocess.run(probe_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
            bitrate = str(int(int(result.stdout.strip()) / 1000)) + "k"
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get bitrate: {e}")
            return

        ffmpeg_cmd = [
            "ffmpeg", "-hwaccel", "cuda",
            "-i", video_path,
            "-vf", f"ass={subtitle_path}",
            "-c:v", "hevc_nvenc", "-b:v", bitrate, "-preset", "slow",
            "-c:a", "copy",
            output_path
        ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        messagebox.showinfo("Done", f"Subtitle burned successfully to:\n{output_path}")
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "FFmpeg failed. Make sure it is installed and in your system PATH.")


# GUI setup
root = tk.Tk()
root.title("FFmpeg Hardsub Tool")
root.geometry("460x280")
root.resizable(False, False)

title = tk.Label(root, text="🧪 Hardsub Subtitles with FFmpeg (NVIDIA)", font=("Arial", 12, "bold"))
title.pack(pady=10)

mode_var = tk.StringVar(value="crf")
crf_radio = tk.Radiobutton(root, text="Use CRF/CQ (Target Quality)", variable=mode_var, value="crf", font=("Arial", 10))
bitrate_radio = tk.Radiobutton(root, text="Use Bitrate (Match Source Size)", variable=mode_var, value="bitrate", font=("Arial", 10))
crf_radio.pack(anchor="w", padx=20)
bitrate_radio.pack(anchor="w", padx=20)

cq_label = tk.Label(root, text="CQ Value (18–28, lower = better):", font=("Arial", 10))
cq_label.pack(anchor="w", padx=20, pady=(10, 0))
cq_entry = tk.Entry(root)
cq_entry.insert(0, "20")
cq_entry.pack(padx=20, fill="x")

run_button = tk.Button(root, text="Start Hardsub", font=("Arial", 11), command=hardsub)
run_button.pack(pady=20)

root.mainloop()
