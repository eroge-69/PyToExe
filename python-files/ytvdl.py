import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import os
from yt_dlp import YoutubeDL

# Variables
current_downloader = None

def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        path_var.set(folder)

def fetch_title():
    url = url_var.get().strip()
    if not url:
        title_var.set("Enter a valid YouTube URL.")
        return

    def _fetch():
        try:
            with YoutubeDL({}) as ydl:
                info = ydl.extract_info(url, download=False)
                title_var.set(f"Video Title: {info['title']}")
        except Exception as e:
            title_var.set("Could not fetch title.")
            print(e)

    threading.Thread(target=_fetch, daemon=True).start()

def download_video():
    url = url_var.get().strip()
    save_path = path_var.get().strip()
    format_choice = format_var.get()

    if not url or not save_path:
        messagebox.showwarning("Missing Info", "Please enter a URL and select a save folder.")
        return

    def _download():
        global current_downloader

        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
        }

        if format_choice == "MP3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            })
        else:
            ydl_opts['format'] = 'best'

        status_var.set("Downloading...")
        download_button.config(state="disabled")
        cancel_button.config(state="normal")

        try:
            with YoutubeDL(ydl_opts) as ydl:
                current_downloader = ydl
                ydl.download([url])
                status_var.set("Download complete.")
        except Exception as e:
            status_var.set("Download failed.")
            messagebox.showerror("Error", str(e))
        finally:
            current_downloader = None
            download_button.config(state="normal")
            cancel_button.config(state="disabled")
            progress_var.set(0)

    threading.Thread(target=_download, daemon=True).start()

def cancel_download():
    global current_downloader
    if current_downloader:
        current_downloader._download_retcode = 1  # force stop
        status_var.set("Cancelled.")
        download_button.config(state="normal")
        cancel_button.config(state="disabled")
        progress_var.set(0)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%').replace('%', '').strip()
        try:
            progress_var.set(float(percent))
        except:
            pass
    elif d['status'] == 'finished':
        progress_var.set(100)

# GUI setup
root = tk.Tk()
root.title("YouTube Downloader (yt-dlp)")
root.geometry("520x430")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("default")
style.configure("TLabel", background="#1e1e1e", foreground="white")
style.configure("TButton", background="#333333", foreground="white")
style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white")
style.configure("TCombobox", fieldbackground="#2e2e2e", foreground="white")
style.configure("Horizontal.TProgressbar", troughcolor="#2e2e2e", background="#00ff66", thickness=20)

# Variables
url_var = tk.StringVar()
path_var = tk.StringVar()
format_var = tk.StringVar(value="MP4")
title_var = tk.StringVar(value="Video Title: (not fetched)")
status_var = tk.StringVar(value="Idle")
progress_var = tk.DoubleVar(value=0)

# Layout
ttk.Label(root, text="YouTube Video URL:").pack(pady=(15, 5))
ttk.Entry(root, textvariable=url_var, width=60).pack()

ttk.Button(root, text="Fetch Title", command=fetch_title).pack(pady=(5, 5))
ttk.Label(root, textvariable=title_var, wraplength=450).pack(pady=(0, 10))

ttk.Label(root, text="Choose Format:").pack()
ttk.Combobox(root, values=["MP4", "MP3"], textvariable=format_var, state="readonly", width=10).pack()

ttk.Label(root, text="Save to Folder:").pack(pady=(15, 5))
folder_frame = ttk.Frame(root)
folder_frame.pack()
ttk.Entry(folder_frame, textvariable=path_var, width=40).pack(side=tk.LEFT, padx=(0, 5))
ttk.Button(folder_frame, text="Browse", command=browse_folder).pack(side=tk.LEFT)

download_button = ttk.Button(root, text="Start Download", command=download_video)
download_button.pack(pady=(20, 5))

cancel_button = ttk.Button(root, text="Cancel Download", command=cancel_download, state="disabled")
cancel_button.pack(pady=(0, 10))

ttk.Label(root, text="Download Progress:").pack()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=(0, 10))

ttk.Label(root, textvariable=status_var, font=("Segoe UI", 9, "italic")).pack()

root.mainloop()
