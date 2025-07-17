import os
import sys
import subprocess
import urllib.request
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

FFMPEG_URL = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
FFMPEG_EXE = "ffmpeg.exe"

def download_ffmpeg():
    messagebox.showinfo("FFmpeg Missing", "Downloading FFmpeg (~80MB), please wait...")
    zip_path = "ffmpeg.zip"
    urllib.request.urlretrieve(FFMPEG_URL, zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith("bin/ffmpeg.exe"):
                zip_ref.extract(file, ".")
                src = os.path.join(".", file)
                dst = os.path.join(".", FFMPEG_EXE)
                os.rename(src, dst)
                break
    os.remove(zip_path)

def ensure_ffmpeg():
    if not os.path.exists(FFMPEG_EXE):
        download_ffmpeg()

def fix_video(input_path):
    output_folder = os.path.join(os.path.dirname(input_path), "processed")
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_folder, f"{filename}_tvfixed.mp4")

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", input_path,
        "-vf", (
            "crop='trunc(iw/2)*2:trunc(ih/2)*2',"
            "scale=768:1152,"
            "pad=768:1154:0:0:color=black"
        ),
        "-c:v", "libx264",
        "-profile:v", "high",
        "-level", "4.0",
        "-pix_fmt", "yuv420p",
        "-preset", "slow",
        "-crf", "22",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]

    subprocess.run(cmd, check=True)
    return output_path

def optimize_image(input_path):
    output_folder = os.path.join(os.path.dirname(input_path), "processed")
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.splitext(os.path.basename(input_path))[0]
    output_path = os.path.join(output_folder, f"{filename}_optimized.jpg")

    img = Image.open(input_path)
    img = img.convert("RGB")
    img.thumbnail((1280, 720))
    img.save(output_path, "JPEG", optimize=True, quality=85)
    return output_path

def process_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext in [".mp4", ".mov", ".avi", ".mkv"]:
            out = fix_video(filepath)
        elif ext in [".jpg", ".jpeg", ".png", ".webp"]:
            out = optimize_image(filepath)
        else:
            messagebox.showerror("Unsupported", "File type not supported.")
            return
        messagebox.showinfo("Success", f"File processed:\n{out}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    ensure_ffmpeg()
    root = tk.Tk()
    root.withdraw()
    filepath = filedialog.askopenfilename(
        filetypes=[
            ("Media Files", "*.mp4 *.mov *.avi *.mkv *.jpg *.jpeg *.png *.webp"),
            ("All Files", "*.*")
        ]
    )
    if filepath:
        process_file(filepath)

if __name__ == "__main__":
    main()
