import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import subprocess
import os
import platform

# Main window
root = tk.Tk()
root.withdraw()

# Intro message
messagebox.showinfo("Info", "Method By cark12345 On Discord.")

def choose_resolution_and_fps():
    def submit():
        selected_res = res_combo.get()
        selected_fps = fps_combo.get()
        if selected_res not in options_res or selected_fps not in options_fps:
            messagebox.showerror("Error", "Please select valid options.")
        else:
            popup.selected_res = selected_res
            popup.selected_fps = selected_fps
            popup.destroy()

    popup = tk.Toplevel()
    popup.title("Video Settings")
    popup.geometry("300x150")

    tk.Label(popup, text="Select max resolution:").pack(pady=5)
    res_combo = ttk.Combobox(popup, values=list(options_res.keys()), state="readonly")
    res_combo.current(0)
    res_combo.pack(pady=5)

    tk.Label(popup, text="Select max FPS:").pack(pady=5)
    fps_combo = ttk.Combobox(popup, values=list(options_fps.keys()), state="readonly")
    fps_combo.current(0)
    fps_combo.pack(pady=5)

    tk.Button(popup, text="OK", command=submit).pack(pady=10)

    popup.selected_res = None
    popup.selected_fps = None
    popup.grab_set()
    popup.wait_window()
    return popup.selected_res, popup.selected_fps

# Options
options_res = {"2160p": 2160, "1440p": 1440, "1080p": 1080}
options_fps = {"60 FPS": 60, "30 FPS": 30, "24 FPS": 24, "15 FPS": 15}

# Ask user to select input file
input_file = filedialog.askopenfilename(title="Select input.mp4", filetypes=[("MP4 files", "*.mp4")])
if not input_file:
    messagebox.showerror("Error", "No file selected.")
    exit()

# Require the file to be named "input.mp4"
if os.path.splitext(os.path.basename(input_file))[0].lower() != "input":
    messagebox.showerror("Error", "The file must be named 'input.mp4'.")
    exit()

# Ask user to choose max resolution and fps
max_res_str, max_fps_str = choose_resolution_and_fps()
if not max_res_str or not max_fps_str:
    messagebox.showerror("Error", "No resolution or FPS selected.")
    exit()
max_res = options_res[max_res_str]
max_fps = options_fps[max_fps_str]

# Define output paths
base_dir = os.path.dirname(input_file)
out_video = os.path.join(base_dir, "output.mp4")
out_audio = os.path.join(base_dir, "audio.mp3")

# Get input video FPS safely
try:
    ffprobe_result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate", "-of", "default=nokey=1:noprint_wrappers=1", input_file],
        capture_output=True, text=True, check=True
    )
    input_fps = eval(ffprobe_result.stdout.strip())
except Exception:
    input_fps = max_fps  # fallback

# Use min(input FPS, selected FPS) to avoid increasing FPS
final_fps = min(input_fps, max_fps)

# Process video: scale down if needed, limit FPS safely, video only
scale_filter = f"scale='min({max_res},iw)':'min({max_res},ih)':force_original_aspect_ratio=decrease"
subprocess.run([
    "ffmpeg", "-i", input_file,
    "-vf", scale_filter,
    "-c:v", "libx264", "-crf", "18", "-preset", "slow",
    "-r", str(final_fps), "-an", out_video,
    "-y"
])

# Extract audio as mp3, duration matches video perfectly
subprocess.run([
    "ffmpeg", "-i", input_file,
    "-vn", "-acodec", "libmp3lame", "-q:a", "2", out_audio,
    "-y"
])

# Completion message
messagebox.showinfo("Video Completed", "Video Completed")

# Open the folder with the outputs
try:
    if platform.system() == "Windows":
        # Open folder and select output.mp4
        subprocess.run(f'explorer /select,"{out_video}"')
    elif platform.system() == "Darwin":  # macOS
        subprocess.run(["open", base_dir])
    else:  # Linux
        subprocess.run(["xdg-open", base_dir])
except Exception:
    pass
