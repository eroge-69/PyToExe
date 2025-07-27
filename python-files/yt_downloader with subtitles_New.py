import os
import shutil
import subprocess
import yt_dlp
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import tempfile
import ttkbootstrap as tb
from ttkbootstrap.constants import *

def get_video_info(url):
    ydl_opts = {'quiet': True, 'skip_download': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)

def choose_format(formats):
    filtered = [f for f in formats if f.get('vcodec') != 'none' and f.get('height') is not None]
    seen = set()
    unique = []
    for f in filtered:
        key = (f.get('height'), f.get('ext'))
        if key not in seen:
            seen.add(key)
            unique.append(f)
    return unique

def merge_subtitles_to_video(video_path, srt_path, output_path, update_progress):
    escaped_srt_path = srt_path.replace('\\', '/').replace(':', '\\:').replace("'", "\\'")
    update_progress("🔧 Merging subtitles with video... please wait")
    merge_cmd = [
        'ffmpeg', '-i', video_path,
        '-vf', f"subtitles='{escaped_srt_path}'",
        '-c:v', 'libx264', '-crf', '20', '-preset', 'fast',
        '-c:a', 'aac', '-b:a', '128k', output_path
    ]
    subprocess.run(merge_cmd, check=True)

def download_video(url, download_directory, format_id, subtitle_lang, update_progress, progress_bar, on_complete):
    temp_dir = tempfile.mkdtemp(prefix="yt_download_", dir=download_directory)

    def progress_hook(d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip().replace('%', '')
            try:
                percent_val = float(percent)
                percent_val = max(0, min(percent_val, 100))
                update_progress(f"📥 Downloading... {percent_val:.1f}%")
                progress_bar['value'] = percent_val
            except:
                pass
        elif d['status'] == 'finished':
            update_progress("✅ Download complete! Processing video...")

    ydl_opts = {
        'outtmpl': f'{temp_dir}/%(title)s.%(ext)s',
        'format': f'{format_id}+bestaudio/best',
        'writesubtitles': subtitle_lang is not None,
        'subtitleslangs': [subtitle_lang] if subtitle_lang else [],
        'merge_output_format': 'mp4',
        'progress_hooks': [progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'final_video')

        video_file = next((f for f in os.listdir(temp_dir) if f.endswith(".mp4")), None)
        video_path = os.path.join(temp_dir, video_file) if video_file else None

        srt_path = None
        vtt_file = next((f for f in os.listdir(temp_dir) if f.endswith(".vtt")), None)
        if vtt_file:
            vtt_path = os.path.join(temp_dir, vtt_file)
            srt_path = os.path.join(temp_dir, "output.srt")
            subprocess.run(['ffmpeg', '-y', '-i', vtt_path, srt_path], check=True)
            os.remove(vtt_path)

        safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "-", "_", ".")).rstrip()
        final_path = os.path.join(download_directory, f"{safe_title}.mp4")

        if srt_path and video_path:
            merge_subtitles_to_video(video_path, srt_path, final_path, update_progress)
            os.remove(srt_path)
            os.remove(video_path)
        elif video_path:
            shutil.move(video_path, final_path)

        shutil.rmtree(temp_dir, ignore_errors=True)
        update_progress(f"✅ All done!\n📁 Saved to:\n{final_path}\nYou may now download another video or close the app.")
        progress_bar['value'] = 100
        on_complete(final_path)

    except Exception as e:
        update_progress("")
        messagebox.showerror("Error", f"Download failed:\n{e}")

class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Downloader + Subtitles")
        self.root.geometry("960x750")
        self.root.resizable(False, False)

        self.style = tb.Style("sandstone")
        self.download_directory = os.path.join(os.path.expanduser("~"), "Downloads")

        self.video_info = None
        self.formats = []
        self.selected_quality_index = None
        self.subtitle_options = []

        self.build_ui()

    def build_ui(self):
        self.frame = tb.Frame(self.root, padding=20)
        self.frame.pack(fill="both", expand=True)

        tb.Label(self.frame, text="🎬 YouTube URL:", font=("Segoe UI", 14, "bold")).pack(anchor="w")
        self.url_entry = tb.Entry(self.frame, width=90, font=("Segoe UI", 12))
        self.url_entry.pack(pady=5)

        tb.Button(self.frame, text="🔍 Fetch Video Info", command=self.fetch_info, bootstyle="info").pack(pady=5)

        folder_frame = tb.Frame(self.frame)
        folder_frame.pack(pady=(10, 5), anchor="w")
        tb.Label(folder_frame, text="📁 Save To:", font=("Segoe UI", 11)).pack(side="left")
        self.folder_display = tb.Entry(folder_frame, width=60)
        self.folder_display.insert(0, self.download_directory)
        self.folder_display.pack(side="left", padx=5)
        tb.Button(folder_frame, text="Browse", command=self.browse_folder, bootstyle="secondary").pack(side="left")

        self.quality_label = tb.Label(self.frame, text="", font=("Segoe UI", 11))
        self.quality_label.pack()

        self.quality_dropdown = tb.Combobox(self.frame, font=("Segoe UI", 11), state="readonly")
        self.quality_dropdown.pack(pady=5)

        self.subtitles_var = tk.BooleanVar()
        self.subtitles_check = tb.Checkbutton(self.frame, text="Download and Embed Subtitles",
                                              variable=self.subtitles_var, bootstyle="success",
                                              command=self.toggle_subtitle_dropdown)
        self.subtitles_check.pack(anchor="w", pady=5)

        self.subtitle_dropdown = tb.Combobox(self.frame, font=("Segoe UI", 11), state="readonly")
        self.subtitle_dropdown.pack(pady=5)
        self.subtitle_dropdown.pack_forget()

        self.download_button = tb.Button(self.frame, text="⬇ Start Download", command=self.start_download,
                                         bootstyle="primary", width=30, padding=10, state="disabled")
        self.download_button.pack(pady=10)

        self.progress_label = tb.Label(self.frame, text="", foreground="blue", font=("Segoe UI", 12, "bold"))
        self.progress_label.pack(pady=5)

        self.progress_bar = tb.Progressbar(self.frame, length=600, mode='determinate', bootstyle="info")
        self.progress_bar.pack(pady=10)

        tb.Button(self.frame, text="🔄 Reset", command=self.reset_app, bootstyle="warning-outline").pack(pady=5)

    def toggle_subtitle_dropdown(self):
        if self.subtitles_var.get() and self.subtitle_options:
            self.subtitle_dropdown.pack(pady=5)
        else:
            self.subtitle_dropdown.pack_forget()

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_directory = folder
            self.folder_display.delete(0, tk.END)
            self.folder_display.insert(0, folder)

    def update_status(self, message):
        self.progress_label.config(text=message)
        self.root.update()

    def fetch_info(self):
        url = self.url_entry.get().strip()
        self.download_directory = self.folder_display.get().strip()

        if not url:
            messagebox.showerror("Error", "URL cannot be empty!")
            return

        self.update_status("📡 Fetching video info...")
        try:
            self.video_info = get_video_info(url)
            self.formats = choose_format(self.video_info.get('formats', []))
            if not self.formats:
                self.update_status("No downloadable video formats found.")
                return

            quality_options = [f"{f['height']}p ({f['ext']})" for f in self.formats]
            self.quality_dropdown['values'] = quality_options
            self.quality_dropdown.current(0)
            self.quality_label.config(text="Available Qualities:")

            subtitles = self.video_info.get('subtitles', {})
            self.subtitle_options = list(subtitles.keys())
            if self.subtitle_options:
                self.subtitle_dropdown['values'] = self.subtitle_options
                self.subtitle_dropdown.current(0)
                if self.subtitles_var.get():
                    self.subtitle_dropdown.pack(pady=5)

            self.download_button.config(state="normal")
            self.update_status("Video info fetched. Select quality and start download.")

        except Exception as e:
            self.update_status("")
            messagebox.showerror("Error", f"Failed to fetch video info:\n{e}")

    def start_download(self):
        url = self.url_entry.get().strip()
        self.download_directory = self.folder_display.get().strip()

        if not url:
            messagebox.showerror("Error", "URL cannot be empty!")
            return
        if not os.path.isdir(self.download_directory):
            messagebox.showerror("Error", "Download folder does not exist.")
            return

        selected_idx = self.quality_dropdown.current()
        if selected_idx == -1:
            messagebox.showerror("Error", "Please select a quality.")
            return

        format_id = self.formats[selected_idx]['format_id']
        subtitle_lang = None
        if self.subtitles_var.get() and self.subtitle_dropdown.winfo_ismapped():
            subtitle_lang = self.subtitle_dropdown.get()

        thread = threading.Thread(target=download_video, args=(
            url, self.download_directory, format_id, subtitle_lang,
            self.update_status, self.progress_bar, self.on_download_complete
        ))
        thread.daemon = True
        thread.start()

    def on_download_complete(self, final_path):
        self.update_status("✅ Download complete. You may reset or close the app.")

    def reset_app(self):
        self.url_entry.delete(0, tk.END)
        self.folder_display.delete(0, tk.END)
        self.folder_display.insert(0, self.download_directory)
        self.quality_label.config(text="")
        self.quality_dropdown.set("")
        self.subtitle_dropdown.set("")
        self.subtitle_dropdown.pack_forget()
        self.progress_label.config(text="")
        self.progress_bar['value'] = 0
        self.download_button.config(state="disabled")
        self.video_info = None
        self.formats = []
        self.selected_quality_index = None
        self.subtitle_options = []

if __name__ == '__main__':
    root = tb.Window(themename="sandstone")
    app = YouTubeDownloaderApp(root)
    root.mainloop()