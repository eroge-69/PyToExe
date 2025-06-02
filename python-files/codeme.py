import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import pyperclip
import os

class YouxRadApp:
    def __init__(self, root):
        self.root = root
        self.root.title("YOUxRAD - YouTube Downloader")
        self.root.geometry("650x550")
        self.root.configure(bg="#1e1e1e")

        self.download_folder = tk.StringVar(value=os.getcwd())
        self.dark_mode = True

        self.create_widgets()
        self.auto_paste_clipboard_url()

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        colors = self.get_theme_colors()
        self.root.configure(bg=colors['bg'])
        for widget in self.root.winfo_children():
            try:
                widget.configure(bg=colors['bg'], fg=colors['fg'])
            except:
                pass

    def get_theme_colors(self):
        return {"bg": "#1e1e1e", "fg": "#ffffff"} if self.dark_mode else {"bg": "#ffffff", "fg": "#000000"}

    def create_widgets(self):
        colors = self.get_theme_colors()

        # URL Entry
        self.url_entry = tk.Entry(self.root, width=65, font=("Arial", 12))
        self.url_entry.insert(0, "Paste YouTube URL here")
        self.url_entry.pack(pady=10)

        # Download Options
        self.option_var = tk.StringVar(value="best")
        options = [
            ("Best Video + Audio", "best"),
            ("Only Audio (Best Quality)", "audio"),
            ("Playlist (Best Audio + Video)", "playlist"),
            ("Thumbnail Download", "thumbnail"),
            ("Transcript", "transcript"),
            ("Captions and Description", "captions"),
            ("Comments", "comments"),
        ]
        for text, val in options:
            tk.Radiobutton(
                self.root, text=text, variable=self.option_var, value=val,
                bg=colors['bg'], fg=colors['fg'], selectcolor=colors['bg'],
                font=("Arial", 10)
            ).pack(anchor="w", padx=20)

        # Resolution Selector
        ttk.Label(self.root, text="Select Quality (for video):").pack()
        self.quality_var = tk.StringVar(value="best")
        self.quality_menu = ttk.Combobox(self.root, textvariable=self.quality_var, state="readonly")
        self.quality_menu['values'] = ["best", "720p", "1080p", "4K"]
        self.quality_menu.pack(pady=5)

        # Folder Picker
        tk.Button(self.root, text="Choose Download Folder", command=self.select_folder).pack(pady=5)

        # Download Button
        tk.Button(self.root, text="Download", command=self.start_download).pack(pady=10)

        # Dark Mode
        tk.Button(self.root, text="Toggle Dark Mode", command=self.toggle_dark_mode).pack()

        # Console Output
        self.console = tk.Text(self.root, height=10, bg="#000000", fg="#00FF00")
        self.console.pack(pady=10)

    def auto_paste_clipboard_url(self):
        try:
            clip = pyperclip.paste()
            if "youtube.com" in clip or "youtu.be" in clip:
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, clip)
        except:
            pass

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.download_folder.set(path)

    def start_download(self):
        url = self.url_entry.get()
        option = self.option_var.get()
        quality = self.quality_var.get()

        thread = threading.Thread(target=self.download, args=(url, option, quality))
        thread.start()

    def download(self, url, option, quality):
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, f"Starting download: {url}\n")

        cmd = ["yt-dlp", url, "-P", self.download_folder.get()]

        # Format Selector
        if option == "best":
            cmd += ["-f", self.get_format_string(quality)]
        elif option == "audio":
            cmd += ["-f", "bestaudio", "--extract-audio", "--audio-format", "mp3"]
        elif option == "playlist":
            cmd += ["-f", "bestvideo+bestaudio", "--yes-playlist"]
        elif option == "thumbnail":
            cmd += ["--write-thumbnail", "--skip-download"]
        elif option == "transcript":
            cmd += ["--write-auto-sub", "--sub-lang", "en", "--skip-download"]
        elif option == "captions":
            cmd += ["--write-description", "--write-info-json", "--skip-download"]
        elif option == "comments":
            cmd += ["--get-comments", "--skip-download"]

        # Run yt-dlp
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            self.console.insert(tk.END, line)
            self.console.see(tk.END)

        process.wait()
        if process.returncode == 0:
            self.console.insert(tk.END, "\n✅ Download Completed!\n")
        else:
            self.console.insert(tk.END, "\n❌ Error during download.\n")

    def get_format_string(self, quality):
        return {
            "720p": "bestvideo[height<=720]+bestaudio",
            "1080p": "bestvideo[height<=1080]+bestaudio",
            "4K": "bestvideo[height<=2160]+bestaudio",
        }.get(quality, "bestvideo+bestaudio")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouxRadApp(root)
    root.mainloop()
