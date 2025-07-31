import tkinter as tk
from tkinter import filedialog
import threading
import subprocess
import os
from send2trash import send2trash

ffmpeg_path = r"E:\Compressed\ffmpeg-7.1.1-full_build\bin\ffmpeg.exe"

def process_files(files, status_label):
    for input_path in files:
        folder, filename = os.path.split(input_path)
        name, ext = os.path.splitext(filename)
        if ext.lower() != ".mkv":
            status_label.config(text=f"Skipping non-MKV file: {input_path}")
            continue
        dest_folder = os.path.join(folder, "Converted")
        os.makedirs(dest_folder, exist_ok=True)
        output_path = os.path.join(dest_folder, f"{name}.mkv")
        status_label.config(text=f"Processing: {input_path}")
        ffmpeg_cmd = [
            ffmpeg_path, "-y", "-i", input_path,
            "-map", "0", "-map", "-0:a:0", "-map", "0:a:0",
            "-c:v", "copy", "-c:a:0", "eac3", "-b:a:0", "640k",
            "-af", "volume=2dB",
            "-disposition:a:0", "default",
            "-c:s", "copy", output_path
        ]
        process = subprocess.run(ffmpeg_cmd)
        if process.returncode == 0:
            send2trash(input_path)
            status_label.config(text=f"Done: {output_path} (sent original to recycle bin)")
        else:
            status_label.config(text=f"Error processing {input_path}")

def select_files(status_label):
    files = filedialog.askopenfilenames(filetypes=[("MKV files", "*.mkv"), ("All files", "*.*")])
    if files:
        thread = threading.Thread(target=process_files, args=(files, status_label))
        thread.start()

root = tk.Tk()
root.title("MKV Batch Converter")

select_button = tk.Button(root, text="Select MKV Files", command=lambda: select_files(status_label))
select_button.pack(pady=10)
status_label = tk.Label(root, text="Ready")
status_label.pack(pady=10)

root.mainloop()
