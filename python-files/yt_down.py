import os
import threading
import yt_dlp
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import requests
from io import BytesIO

# ---------------- FFmpeg PATH ---------------- #
FFMPEG_PATH = r"C:\ffmpeg\bin"
if FFMPEG_PATH not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + FFMPEG_PATH

# ---------------- Default Download Folder ---------------- #
default_folder = os.path.join(os.getcwd(), "YT Download")
if not os.path.exists(default_folder):
    os.makedirs(default_folder)

# ---------------- Functions ---------------- #
def get_thumbnail(url):
    try:
        ydl_opts = {"quiet": True, "skip_download": True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            thumb_url = info.get("thumbnail")
            if thumb_url:
                response = requests.get(thumb_url)
                img_data = BytesIO(response.content)
                img = Image.open(img_data)
                img = img.resize((250, 140))
                return ImageTk.PhotoImage(img)
    except:
        return None

def show_thumbnail():
    url = url_var.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return
    thumb_img = get_thumbnail(url)
    if thumb_img:
        thumbnail_label.config(image=thumb_img)
        thumbnail_label.image = thumb_img
    else:
        thumbnail_label.config(image="")
        thumbnail_label.image = None

def progress_hook(d):
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0%')
        percent_clean = percent_str.replace('%', '').replace('\x1b[0;94m','').replace('\x1b[0m','').strip()
        try:
            progress_bar['value'] = float(percent_clean)
            status_label.config(text=f"Downloading... {percent_str}")
            root.update_idletasks()
        except:
            pass
    elif d['status'] == 'finished':
        status_label.config(text="✅ Download Completed!")
        messagebox.showinfo("Success", "Download completed successfully!")

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        folder_var.set(folder)

def run_yt_dlp(ydl_opts, url):
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        messagebox.showerror("Download Failed", str(e))

def download_video():
    url = url_var.get().strip()
    if not url:
        messagebox.showerror("Error", "Please enter a YouTube URL!")
        return

    folder = folder_var.get()
    if not folder:
        folder = default_folder  # fallback
        folder_var.set(folder)
        if not os.path.exists(folder):
            os.makedirs(folder)

    format_choice = format_var.get()
    quality = quality_var.get()

    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': not playlist_var.get(),
        'ffmpeg_location': FFMPEG_PATH,
        'quiet': True
    }

    if format_choice == "Video":
        ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    threading.Thread(target=run_yt_dlp, args=(ydl_opts, url), daemon=True).start()

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("YouTube Video Downloader")
root.geometry("600x650")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("TButton", background="#333", foreground="white")
style.configure("TCombobox", fieldbackground="#333", foreground="white")
style.configure("TEntry", fieldbackground="#333", foreground="white")

tk.Label(root, text="🎥 YouTube Downloader", font=("Arial", 16, "bold"), fg="red", bg="#1e1e1e").pack(pady=5)

# URL Entry
tk.Label(root, text="YouTube URL:", font=("Arial", 12), bg="#1e1e1e", fg="white").pack()
url_var = tk.StringVar()
tk.Entry(root, textvariable=url_var, width=60, bg="#333", fg="white", insertbackground="white").pack(pady=5)

# Thumbnail Button
tk.Button(root, text="Show Thumbnail", command=show_thumbnail, bg="#444", fg="white").pack(pady=5)
thumbnail_label = tk.Label(root, bg="#1e1e1e")
thumbnail_label.pack(pady=5)

# Output Folder
folder_var = tk.StringVar(value=default_folder)
tk.Button(root, text="Select Download Folder", command=browse_folder, bg="#444", fg="white").pack(pady=5)
tk.Label(root, textvariable=folder_var, fg="#00ff99", bg="#1e1e1e").pack()

# Format Selection
format_var = tk.StringVar(value="Video")
tk.Label(root, text="Select Format:", font=("Arial", 12), bg="#1e1e1e", fg="white").pack(pady=5)
tk.Radiobutton(root, text="Video", variable=format_var, value="Video", bg="#1e1e1e", fg="white", selectcolor="#333").pack()
tk.Radiobutton(root, text="Audio (MP3)", variable=format_var, value="Audio", bg="#1e1e1e", fg="white", selectcolor="#333").pack()

# Quality Selection
tk.Label(root, text="Select Quality:", font=("Arial", 12), bg="#1e1e1e", fg="white").pack(pady=5)
quality_var = tk.StringVar(value="720")
quality_menu = ttk.Combobox(root, textvariable=quality_var, values=["144","240","360","480","720","1080","1440","2160"], width=10)
quality_menu.pack()

# Playlist Option
playlist_var = tk.BooleanVar()
tk.Checkbutton(root, text="Download Entire Playlist", variable=playlist_var, bg="#1e1e1e", fg="white", selectcolor="#333").pack(pady=5)

# Download Button
tk.Button(root, text="Download", command=download_video, bg="#00cc66", fg="white", font=("Arial", 12, "bold"), width=15).pack(pady=15)

# Progress Bar
progress_bar = ttk.Progressbar(root, length=400, mode="determinate")
progress_bar.pack(pady=10)
status_label = tk.Label(root, text="", font=("Arial", 10), bg="#1e1e1e", fg="white")
status_label.pack()

root.mainloop()
