import sys
import subprocess

# === Auto-install missing modules ===
for pkg in ["yt_dlp"]:
    try:
        __import__(pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import os
import urllib.request
import zipfile
import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from yt_dlp import YoutubeDL

# === Basic Config ===
DEFAULT_DOWNLOAD_PATH = os.path.join(os.path.expanduser("~"), "Downloads")
BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
FFMPEG_PATH = os.path.join(BASE_DIR, "ffmpeg.exe")

# === GUI Setup ===
root = tk.Tk()
root.title("YouTube Playlist/Video Downloader - By Abdullah El Shamashergy")
root.geometry("1000x700")
root.configure(bg="#f8f8f8")

# === GUI State Variables ===
path_var = tk.StringVar(value=DEFAULT_DOWNLOAD_PATH)
quality_var = tk.StringVar(value="Best Available")
mode_var = tk.StringVar(value="full")

# === Quality Map ===
quality_map = {
    "144p": "bestvideo[height<=144]+bestaudio/best[height<=144]",
    "240p": "bestvideo[height<=240]+bestaudio/best[height<=240]",
    "360p": "bestvideo[height<=360]+bestaudio/best[height<=360]",
    "480p": "bestvideo[height<=480]+bestaudio/best[height<=480]",
    "720p (HD)": "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "1080p (Full HD)": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "Best Available": "bestvideo+bestaudio/best"
}

# === Logging with fallback ===
def log(msg):
    try:
        log_box.insert(tk.END, msg + "\n")
        log_box.see(tk.END)
        root.update()
    except:
        print(msg)

# === Internet Check ===
def has_internet():
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        return False

# === Auto-download ffmpeg ===
def download_ffmpeg():
    log("🔻 ffmpeg.exe not found. Downloading...")
    if not has_internet():
        messagebox.showerror("No Internet", "⚠️ No internet connection. Cannot download ffmpeg.")
        sys.exit(1)
    try:
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = os.path.join(BASE_DIR, "ffmpeg.zip")
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zf:
            for f in zf.namelist():
                if f.endswith("ffmpeg.exe") and "/bin/" in f:
                    zf.extract(f, BASE_DIR)
                    os.rename(os.path.join(BASE_DIR, f), FFMPEG_PATH)
                    break
        os.remove(zip_path)
        log("✅ ffmpeg.exe downloaded successfully.")
    except Exception as e:
        messagebox.showerror("FFmpeg Error", f"Failed to download ffmpeg:\n{e}")
        sys.exit(1)

if not os.path.exists(FFMPEG_PATH):
    download_ffmpeg()

# === Browse Folder ===
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        path_var.set(folder)

# === Download progress hook with progress bar and status ===
def log_progress(d):
    if d['status'] == 'downloading':
        pct_str = d.get('_percent_str', '').strip().replace('%', '')
        pct = float(pct_str) if pct_str else 0
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('eta', '?')
        text = f"⬇ Downloading... {pct_str}% at {speed} (ETA: {eta}s)"
        status_label.config(text=text)
        progress_bar["value"] = pct
        root.update()
    elif d['status'] == 'finished':
        status_label.config(text="🔄 Merging audio & video...")
        progress_bar["value"] = 100
        root.update()

# === Download handler ===
def threaded_download():
    threading.Thread(target=start_download).start()

# === Main logic ===
def start_download():
    url = url_entry.get().strip()
    download_path = path_var.get().strip() or DEFAULT_DOWNLOAD_PATH
    quality = quality_var.get()
    mode = mode_var.get()

    log_box.delete("1.0", tk.END)
    status_label.config(text="")
    progress_bar["value"] = 0

    if not url.startswith("http"):
        messagebox.showerror("Invalid URL", "❌ Please enter a valid video or playlist URL.")
        return

    if not has_internet():
        messagebox.showerror("No Internet", "❌ Internet connection is required.")
        return

    try:
        os.makedirs(download_path, exist_ok=True)
    except Exception as e:
        messagebox.showerror("Folder Error", f"Cannot create download path:\n{e}")
        return

    selected_format = quality_map.get(quality, "bestvideo+bestaudio/best")

    try:
        log(f"🔍 Extracting from URL: {url}")
        with YoutubeDL({'quiet': True, 'extract_flat': False, 'dump_single_json': True}) as ydl:
            info = ydl.extract_info(url, download=False)
        entries = info['entries'] if 'entries' in info else [info]
        log(f"✅ Found {len(entries)} video(s).")
    except Exception as e:
        messagebox.showerror("Extraction Error", f"Failed to extract video/playlist:\n{e}")
        return

    if not entries:
        messagebox.showerror("No Videos", "❌ No downloadable videos found.")
        return

    if mode == "range":
        try:
            start_idx = int(start_entry.get())
            end_idx = int(end_entry.get())
            if not (1 <= start_idx <= end_idx <= len(entries)):
                raise ValueError
            entries = entries[start_idx - 1:end_idx]
        except ValueError:
            messagebox.showerror("Range Error", "⚠️ Enter valid numeric range within playlist.")
            return

    video_urls = [e.get('webpage_url') for e in entries if e.get('webpage_url')]

    if not video_urls:
        messagebox.showerror("Missing URLs", "⚠️ No valid video URLs found in playlist.")
        return

    opts = {
        'format': selected_format,
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'ffmpeg_location': FFMPEG_PATH,
        'merge_output_format': 'mp4',
        'progress_hooks': [log_progress],
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    }

    try:
        with YoutubeDL(opts) as ydl:
            for i, link in enumerate(video_urls, 1):
                log(f"\n🎬 Downloading video {i}/{len(video_urls)}")
                ydl.download([link])
        messagebox.showinfo("Success", "✅ All downloads completed successfully.")
        log("✅ All done.")
    except Exception as e:
        messagebox.showerror("Download Failed", str(e))
        log(f"❌ Error: {e}")

# === GUI ===
title_font = ("Segoe UI", 20, "bold")
label_font = ("Segoe UI", 12)
small_font = ("Segoe UI", 10)

# Header
tk.Label(root, text="🎥 YouTube Video/Playlist Downloader", font=title_font, fg="#2c3e50", bg="#f8f8f8").pack(pady=(20, 5))
tk.Label(root, text="By Abdullah El Shamashergy", font=small_font, fg="#666", bg="#f8f8f8").pack(pady=(0, 20))

form_frame = tk.Frame(root, bg="#f8f8f8")
form_frame.pack(padx=30, fill="x")

# URL Entry
tk.Label(form_frame, text="Video or Playlist URL:", font=label_font, bg="#f8f8f8").grid(row=0, column=0, sticky="w")
url_entry = tk.Entry(form_frame, width=80)
url_entry.grid(row=0, column=1, columnspan=3, pady=5)

# Quality
tk.Label(form_frame, text="Select Quality:", font=label_font, bg="#f8f8f8").grid(row=1, column=0, sticky="w")
tk.OptionMenu(form_frame, quality_var, *quality_map.keys()).grid(row=1, column=1, sticky="w", pady=5)

# Path
path_label = tk.Label(form_frame, text="Download Path:", font=label_font, bg="#f8f8f8")
path_label.grid(row=2, column=0, sticky="w")
tk.Entry(form_frame, textvariable=path_var, width=60).grid(row=2, column=1, pady=5)
tk.Button(form_frame, text="Browse", command=browse_folder).grid(row=2, column=2, padx=10)

# Mode
mode_label = tk.Label(form_frame, text="Download Mode:", font=label_font, bg="#f8f8f8")
mode_label.grid(row=3, column=0, sticky="w")
tk.Radiobutton(form_frame, text="Full Playlist / Video", variable=mode_var, value="full", bg="#f8f8f8").grid(row=3, column=1, sticky="w")
tk.Radiobutton(form_frame, text="Range", variable=mode_var, value="range", bg="#f8f8f8").grid(row=3, column=2, sticky="w")

# Range Inputs
tk.Label(form_frame, text="Start #:", font=label_font, bg="#f8f8f8").grid(row=4, column=0, sticky="w")
start_entry = tk.Entry(form_frame, width=5)
start_entry.grid(row=4, column=1, sticky="w")
tk.Label(form_frame, text="End #:", font=label_font, bg="#f8f8f8").grid(row=4, column=2, sticky="e")
end_entry = tk.Entry(form_frame, width=5)
end_entry.grid(row=4, column=3, sticky="w")

# Start Button
tk.Button(root, text="⬇ Start Download", command=threaded_download, bg="#27ae60", fg="white",
          font=("Segoe UI", 13, "bold"), padx=20, pady=10).pack(pady=20)

# Status display (progress terminal line)
status_label = tk.Label(root, text="", font=("Consolas", 11), bg="#000000", fg="#00FF00", anchor="w", justify="left")
status_label.pack(fill="x", padx=20, pady=(5, 0))

# Green progress bar
style = ttk.Style()
style.theme_use('default')
style.configure("green.Horizontal.TProgressbar", troughcolor='#eee', background='#2ecc71', thickness=20)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=800, mode="determinate",
                               style="green.Horizontal.TProgressbar", maximum=100)
progress_bar.pack(padx=20, pady=(5, 10))

# Log box for scrolling messages
log_box = scrolledtext.ScrolledText(root, height=13, width=120, font=("Consolas", 10), bg="#ffffff")
log_box.pack(padx=20, pady=(5, 10))

root.mainloop()
