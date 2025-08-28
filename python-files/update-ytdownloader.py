import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import yt_dlp
import os


class YouTubeDownloader(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Modern YouTube Downloader")
        self.geometry("600x450")
        ctk.set_appearance_mode("dark")  # or "light"
        ctk.set_default_color_theme("blue")

        # Variables
        self.download_path = tk.StringVar(value="Select a folder...")
        self.url_var = tk.StringVar()
        self.choice = tk.StringVar(value="video")
        self.playlist_mode = tk.BooleanVar(value=False)

        # Widgets
        self.create_widgets()

    def create_widgets(self):
        # Title
        ctk.CTkLabel(
            self,
            text="🎬 YouTube / Playlist Downloader",
            font=("Arial", 20, "bold")
        ).pack(pady=15)

        # URL Entry
        ctk.CTkEntry(
            self,
            textvariable=self.url_var,
            width=500,
            placeholder_text="Enter video or playlist URL"
        ).pack(pady=10)

        # Folder selection
        ctk.CTkButton(self, text="Choose Folder", command=self.choose_folder).pack(pady=5)
        ctk.CTkLabel(self, textvariable=self.download_path, wraplength=500, text_color="gray").pack(pady=5)

        # Download type
        mode_frame = ctk.CTkFrame(self)
        mode_frame.pack(pady=10)
        ctk.CTkRadioButton(mode_frame, text="Video", variable=self.choice, value="video").grid(row=0, column=0, padx=10, pady=5)
        ctk.CTkRadioButton(mode_frame, text="Audio (mp3)", variable=self.choice, value="audio").grid(row=0, column=1, padx=10, pady=5)

        # Playlist toggle
        ctk.CTkCheckBox(self, text="Download entire playlist (if available)", variable=self.playlist_mode).pack(pady=5)

        # Download button
        ctk.CTkButton(
            self,
            text="⬇️ Start Download",
            command=self.start_download,
            width=200,
            height=40
        ).pack(pady=15)

        # Progress bar
        self.progressbar = ctk.CTkProgressBar(self, width=400)
        self.progressbar.set(0)
        self.progressbar.pack(pady=10)

        # Status text
        self.status_label = ctk.CTkLabel(self, text="", wraplength=500)
        self.status_label.pack(pady=10)

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.download_path.set(folder)

    def start_download(self):
        url = self.url_var.get().strip()
        folder = self.download_path.get()
        if not url:
            messagebox.showerror("Error", "Please enter a valid URL")
            return
        if folder == "Select a folder...":
            messagebox.showerror("Error", "Please select a folder")
            return

        self.progressbar.set(0)
        self.status_label.configure(text="Starting download...")

        # Run download in background thread
        threading.Thread(
            target=self.download_media,
            args=(url, folder, self.choice.get()),
            daemon=True
        ).start()

    def download_media(self, url, folder, mode):
        try:
            ydl_opts = {
                "outtmpl": os.path.join(folder, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
                "quiet": True,
                "no_color": True,       # ✅ avoids escape code errors
                "ignoreerrors": True,
                "noplaylist": not self.playlist_mode.get(),  # ✅ user toggle
            }

            if mode == "audio":
                ydl_opts.update({
                    "format": "bestaudio/best",
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }],
                })
            else:  # video
                ydl_opts.update({
                    "format": "bestvideo+bestaudio/best",  # ✅ highest quality
                    "merge_output_format": "mp4",          # ✅ always mp4
                })

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            self.status_label.configure(text="✅ All downloads completed")

        except Exception as e:
            self.status_label.configure(text=f"❌ Error: {str(e)}")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)

            if total:
                percent = downloaded / total
                self.progressbar.set(percent)
                filename = d.get("filename", "File")
                self.status_label.configure(
                    text=f"⬇️ Downloading: {os.path.basename(filename)} ({percent*100:.1f}%)"
                )
            else:
                self.status_label.configure(text="⬇️ Downloading...")

        elif d["status"] == "finished":
            self.status_label.configure(text="Processing... ⏳")


if __name__ == "__main__":
    app = YouTubeDownloader()
    app.mainloop()
