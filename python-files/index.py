# Build by https://github.com/yoni-tad

import os
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import yt_dlp

# ---------- CONFIG -----------
DOWNLOAD_FOLDER = "./videos"
VIDEO_FORMAT = 'best[ext=mp4][height<=360]'

# ---------- Ensure download folder exists ----------
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# ---------- GUI App Class ----------
class YouTubeDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Bulk Downloader")

        # Input area
        tk.Label(root, text="Enter YouTube Links (line separated): ").pack()
        self.text_links = tk.Text(root, height=8, width=80)
        self.text_links.pack(padx=10, pady=5)

        # controllers
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)

        self.start_btn = tk.Button(btn_frame, text="Start Download", command=self.start_download)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = tk.Button(btn_frame, text="Stop", command=self.stop_download)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Logs
        tk.Label(root, text="Status / Logs: ").pack()
        self.log_area = scrolledtext.ScrolledText(root, height=15, width=80, state=tk.DISABLED)
        self.log_area.pack(padx=10, pady=5)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(root, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill=tk.X, padx=10, pady=5)

        # Status label for speed/ETA
        self.status_label = tk.Label(root, text='Ready')
        self.status_label.pack()

        self.stop_flag = False
        self.thread = None
        self.failed_links = []

    def log(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
    
    def start_download(self):
        self.progress_var.set(0)
        self.progress_bar.update()
        self.status_label.config(text="Starting...")

        links_input = self.text_links.get("1.0", tk.END).strip()
        if not links_input:
            messagebox.showwarning("Warning", "Please enter at least one link!")
            return
        
        links = links_input.split()
        if not links:
            messagebox.showwarning("Warning", "No valid links found!")
            return

        self.stop_flag = False
        self.failed_links = []
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete("1.0", tk.END)
        self.log_area.config(state=tk.DISABLED)

        self.thread = threading.Thread(target=self.download_videos, args=(links,))
        self.thread.start()

    def stop_download(self):
        self.stop_flag = True
        self.log("❗️ Stop requested. Will halt after current download.")

        self.progress_var.set(0)
        self.progress_bar.update()
        self.status_label.config(text="Stopped")

    def download_videos(self, links):
        ydl_opts = {
            'format': VIDEO_FORMAT,
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'progress_hooks': [self.progress_hook],
            'quiet': True,
            'merge_output_format': 'mp4',
        }

        self.log("✅ Download started...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for idx, link in enumerate(links, 1):
                if self.stop_flag:
                    self.log("🛑 Stopped by user.")
                    break
                self.log(f"🔗 ({idx}/{len(links)}) Downloading: {link}")
                try:
                    ydl.download([link])
                    self.log(f"✅ Finished: {link}")
                except Exception as e:
                    self.log(f"❌ Error with {link}: {e}")
                    self.failed_links.append(link)

        # log
        if self.failed_links:
            fail_log_path = os.path.join(DOWNLOAD_FOLDER, "failed_downloads.txt")
            with open(fail_log_path, "w") as f:
                for failed in self.failed_links:
                    f.write(failed + "\n")
            self.log(f"⚠️ Failed downloads saved to {fail_log_path}")
        else:
            self.log("✅ No failed downloads!")


        self.log("🎯 All done (or stopped).")
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate')
            downloaded = d.get('downloaded_bytes', 0)

            if total:
                percent = downloaded / total * 100
                self.progress_var.set(percent)
                self.progress_bar.update()

            speed = d.get('speed', 0)
            eta = d.get('eta', 0)

            speed_str = f"{speed/1024:.1f} KB/s" if speed < 1024*1024 else f"{speed/1024/1024:.2f} MB/s"
            status_msg = f"{percent:.1f}% | {speed_str} | ETA: {eta}s"
            self.status_label.config(text=status_msg)

            self.log_area.config(state=tk.NORMAL)
            self.log_area.insert(tk.END, status_msg + "\n")
            self.log_area.see(tk.END)
            self.log_area.config(state=tk.DISABLED)
        elif d['status'] == 'finished':
            self.progress_var.set(100)
            self.progress_bar.update()
            self.status_label.config(text="✅ Download completed!")
            self.log("✅ Download completed!")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderApp(root)
    root.mainloop()


