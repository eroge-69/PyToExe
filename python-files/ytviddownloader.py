import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pytubefix import YouTube
import os
import re
import pyperclip
import tempfile
import subprocess
import sys

def is_valid_youtube_url(url):
    pattern = r'(https?://)?(www\.)?(youtube\.com|youtu\.be)/.+'
    return re.match(pattern, url) is not None

def paste_from_clipboard():
    url_entry.delete(0, tk.END)
    url_entry.insert(0, pyperclip.paste())

def clear_url():
    url_entry.delete(0, tk.END)

def change_location():
    global download_location
    folder = filedialog.askdirectory()
    if folder:
        download_location = folder
        location_var.set(download_location)

def open_location():
    folder = location_var.get()
    if os.path.exists(folder):
        if sys.platform.startswith("win"):
            os.startfile(folder)
        elif sys.platform.startswith("darwin"):
            subprocess.Popen(["open", folder])
        else:
            subprocess.Popen(["xdg-open", folder])
    else:
        messagebox.showerror("Error", "Folder does not exist")

def update_mode():
    if mode_var.get() == "Video":
        res_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        res_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
    else:
        res_label.grid_remove()
        res_menu.grid_remove()

def merge_video_audio(video_path, audio_path, output_path):
    try:
        cmd = [
            'ffmpeg',
            '-y',
            '-i', video_path,
            '-i', audio_path,
            '-c', 'copy',
            output_path
        ]
        # Run without console window on Windows
        startupinfo = None
        if sys.platform.startswith('win'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

        subprocess.run(cmd, check=True, startupinfo=startupinfo)
    except subprocess.CalledProcessError as e:
        raise RuntimeError("ffmpeg failed to merge video and audio.") from e
    except FileNotFoundError:
        raise RuntimeError("ffmpeg not found. Please install ffmpeg and add it to your PATH.")

def download():
    url = url_entry.get().strip()
    if not is_valid_youtube_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube link.")
        return

    try:
        yt = YouTube(url)
        if mode_var.get() == "Audio":
            stream = yt.streams.filter(only_audio=True).first()
            if not stream:
                messagebox.showerror("Error", "No audio stream available.")
                return
            stream.download(output_path=download_location)
            messagebox.showinfo("Success", "Audio download complete!")
        else:
            # Try progressive stream first (video+audio)
            stream = yt.streams.filter(progressive=True, res=res_var.get()).first()
            if stream:
                stream.download(output_path=download_location)
                messagebox.showinfo("Success", "Video download complete!")
                return

            # Otherwise, download video and audio separately and merge
            video_stream = yt.streams.filter(adaptive=True, res=res_var.get(), file_extension='mp4').first()
            audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()

            if not video_stream or not audio_stream:
                messagebox.showerror("Error", "Selected resolution not available.")
                return

            # Use tempfile for temp files
            with tempfile.TemporaryDirectory() as tmpdir:
                video_path = video_stream.download(output_path=tmpdir, filename="video.mp4")
                audio_path = audio_stream.download(output_path=tmpdir, filename="audio.mp4")

                output_filename = yt.title
                # Remove problematic chars in filename
                output_filename = "".join(x for x in output_filename if x.isalnum() or x in "._- ")
                output_path = os.path.join(download_location, output_filename + ".mp4")

                # Show merging message
                merging_popup = tk.Toplevel(root)
                merging_popup.title("Merging")
                tk.Label(merging_popup, text="Merging video and audio, please wait...").pack(padx=20, pady=20)
                merging_popup.update()

                try:
                    merge_video_audio(video_path, audio_path, output_path)
                finally:
                    merging_popup.destroy()

                messagebox.showinfo("Success", "Video and audio merged successfully!")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("YouTube Downloader")

download_location = os.getcwd()

# URL entry
tk.Label(root, text="YouTube URL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
url_entry = tk.Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=2)

paste_btn = tk.Button(root, text="Paste", command=paste_from_clipboard)
paste_btn.grid(row=1, column=1, sticky="w", padx=5, pady=5)

clear_btn = tk.Button(root, text="Clear", command=clear_url)
clear_btn.grid(row=1, column=2, sticky="w", padx=5, pady=5)

# Mode toggle
mode_var = tk.StringVar(value="Video")
mode_switch = ttk.Combobox(root, textvariable=mode_var, values=["Video", "Audio"], state="readonly")
mode_switch.grid(row=1, column=0, padx=5, pady=5)
mode_switch.bind("<<ComboboxSelected>>", lambda e: update_mode())

# Resolution chooser (placed permanently in correct spot)
res_label = tk.Label(root, text="Resolution:")
res_var = tk.StringVar(value="720p")
res_menu = ttk.Combobox(root, textvariable=res_var, values=["144p", "240p", "360p", "480p", "720p", "1080p", "1440p", "2160p", "4320p"], state="readonly")
res_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)
res_menu.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

# Download location
location_var = tk.StringVar(value=download_location)
tk.Label(root, text="Download location:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
location_entry = tk.Entry(root, textvariable=location_var, state="readonly", width=50)
location_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=2)

# Buttons stacked vertically below the location entry
btn_frame = tk.Frame(root)
btn_frame.grid(row=4, column=1, sticky="w", padx=5, pady=(0,10))

tk.Button(btn_frame, text="Change Location...", command=change_location).pack(fill='x', pady=(0,5))
tk.Button(btn_frame, text="Open Selected Location", command=open_location).pack(fill='x')

# Download button
download_btn = tk.Button(root, text="Download", command=download)
download_btn.grid(row=5, column=0, columnspan=3, pady=10)

root.mainloop()
