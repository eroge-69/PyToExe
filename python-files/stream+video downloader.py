import subprocess
import sys

def install_package(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", package])
    except subprocess.CalledProcessError:
        print(f"Fehler beim Installieren von {package}. Bitte installiere es manuell.")

def check_and_install_packages():
    required_packages = ["yt-dlp", "ffpyplayer", "Pillow", "streamlink"]
    import importlib
    for pkg in required_packages:
        pkg_import_name = pkg.replace("-", "_")  # yt-dlp → yt_dlp
        try:
            importlib.import_module(pkg_import_name)
        except ImportError:
            print(f"{pkg} nicht gefunden. Installiere...")
            install_package(pkg)

check_and_install_packages()

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import locale
from ffpyplayer.player import MediaPlayer

try:
    from PIL import Image, ImageTk
except ImportError:
    messagebox.showerror("Fehler", "Pillow konnte nicht geladen werden. Bitte installiere es manuell (pip install Pillow).")
    sys.exit(1)

class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root

        # Sprache erkennen
        lang, _ = locale.getdefaultlocale()
        self.is_german = lang and lang.startswith("de")

        self.strings = self.get_localized_strings()

        self.root.title(self.strings["title"])
        self.root.geometry("800x840")
        self.root.configure(bg="#1e1e1e")

        self.player = None
        self.is_playing = False
        self.is_paused = False
        self.muted = False
        self.video_path = None
        self.after_id = None

        self.setup_style()
        self.create_widgets()
        self.create_controls()

    def get_localized_strings(self):
        if self.is_german:
            return {
                "title": "🎬 Video Downloader & Player",
                "platform_label": "🌐 Plattform wählen:",
                "twitch": "Twitch",
                "youtube": "YouTube",
                "url_label": "🔗 Video-URL:",
                "quality_label": "🎞️ Qualität (nur Twitch):",
                "filename_label": "💾 Dateiname (ohne Endung):",
                "folder_label": "📁 Zielordner:",
                "browse": "Durchsuchen",
                "download": "⬇️ Download starten",
                "status_downloading_twitch": "📡 Twitch-Download läuft...",
                "status_downloading_youtube": "📡 YouTube-Download läuft...",
                "status_finished": "✅ Download abgeschlossen:\n{}",
                "status_error": "❌ Fehler beim Herunterladen.",
                "last_video_play": "▶️ Letztes Video abspielen",
                "open_local_video": "📂 Video von Festplatte öffnen",
                "no_video_warn": "Es wurde noch kein Video heruntergeladen.",
                "error_title": "Fehler",
                "warning_title": "Warnung",
                "mute": "🔇 Stummschalten",
                "unmute": "🔈 Laut",
                "skip_back": "⏮️ -10s",
                "pause": "⏸️ Pause",
                "play": "▶️ Wiedergabe",
                "stop": "⏹️ Stop",
                "skip_forward": "⏭️ +10s",
                "error_no_url_folder": "Bitte URL und Zielordner angeben."
            }
        else:
            return {
                "title": "🎬 Video Downloader & Player",
                "platform_label": "🌐 Select platform:",
                "twitch": "Twitch",
                "youtube": "YouTube",
                "url_label": "🔗 Video URL:",
                "quality_label": "🎞️ Quality (Twitch only):",
                "filename_label": "💾 Filename (without extension):",
                "folder_label": "📁 Destination folder:",
                "browse": "Browse",
                "download": "⬇️ Start download",
                "status_downloading_twitch": "📡 Downloading Twitch stream...",
                "status_downloading_youtube": "📡 Downloading YouTube video...",
                "status_finished": "✅ Download finished:\n{}",
                "status_error": "❌ Error during download.",
                "last_video_play": "▶️ Play last video",
                "open_local_video": "📂 Open local video",
                "no_video_warn": "No video has been downloaded yet.",
                "error_title": "Error",
                "warning_title": "Warning",
                "mute": "🔇 Mute",
                "unmute": "🔈 Unmute",
                "skip_back": "⏮️ -10s",
                "pause": "⏸️ Pause",
                "play": "▶️ Play",
                "stop": "⏹️ Stop",
                "skip_forward": "⏭️ +10s",
                "error_no_url_folder": "Please specify URL and destination folder."
            }

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 11))
        style.configure("TEntry", fieldbackground="#2e2e2e", background="#2e2e2e", foreground="#ffffff", padding=5)
        style.configure("TButton", background="#3a3a3a", foreground="#ffffff", font=("Segoe UI", 10), padding=6)
        style.configure("TRadiobutton", background="#1e1e1e", foreground="#ffffff", font=("Segoe UI", 10))
        style.configure("TProgressbar", troughcolor="#333333", bordercolor="#333333",
                        background="#00cc66", lightcolor="#00cc66", darkcolor="#00cc66")
        style.map("TButton", background=[("active", "#4a4a4a")])

    def create_widgets(self):
        self.platform = tk.StringVar(value="twitch")

        ttk.Label(self.root, text=self.strings["platform_label"]).pack(pady=(10, 2), anchor="w", padx=20)
        platform_frame = ttk.Frame(self.root)
        platform_frame.pack(pady=5, padx=20, anchor="w")

        ttk.Radiobutton(platform_frame, text=self.strings["twitch"], variable=self.platform, value="twitch").pack(side="left", padx=10)
        ttk.Radiobutton(platform_frame, text=self.strings["youtube"], variable=self.platform, value="youtube").pack(side="left", padx=10)

        self.add_label(self.strings["url_label"])
        self.url_entry = self.add_entry()

        self.add_label(self.strings["quality_label"])
        self.quality_entry = self.add_entry()
        self.quality_entry.insert(0, "best")

        self.add_label(self.strings["filename_label"])
        self.filename_entry = self.add_entry()
        self.filename_entry.insert(0, "video")

        self.add_label(self.strings["folder_label"])
        folder_frame = ttk.Frame(self.root)
        folder_frame.pack(pady=2, padx=20, fill="x")
        self.folder_entry = ttk.Entry(folder_frame, width=50)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(folder_frame, text=self.strings["browse"], command=self.choose_folder).pack(side="left", padx=5)

        ttk.Button(self.root, text=self.strings["download"], command=self.download_video).pack(pady=10)

        self.status_label = ttk.Label(self.root, text="", wraplength=760, justify="center", font=("Segoe UI", 10))
        self.status_label.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, length=700, mode='determinate')
        self.progress.pack(pady=5)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text=self.strings["last_video_play"], command=self.play_last_video).pack(side="left", padx=10)
        ttk.Button(button_frame, text=self.strings["open_local_video"], command=self.choose_local_video).pack(side="left", padx=10)

        # Canvas ohne fixe Größe - wird dynamisch angepasst
        self.video_panel = tk.Canvas(self.root, bg="black")
        self.video_panel.pack(padx=20, pady=10, fill="both", expand=True)

    def create_controls(self):
        control_frame = ttk.Frame(self.root)
        control_frame.pack(pady=10)

        ttk.Button(control_frame, text=self.strings["skip_back"], command=self.skip_back).pack(side="left", padx=5)
        self.pause_button = ttk.Button(control_frame, text=self.strings["pause"], command=self.toggle_pause)
        self.pause_button.pack(side="left", padx=5)
        ttk.Button(control_frame, text=self.strings["stop"], command=self.stop_video).pack(side="left", padx=5)
        self.mute_button = ttk.Button(control_frame, text=self.strings["mute"], command=self.toggle_mute)
        self.mute_button.pack(side="left", padx=5)
        ttk.Button(control_frame, text=self.strings["skip_forward"], command=self.skip_forward).pack(side="left", padx=5)

    def add_label(self, text):
        lbl = ttk.Label(self.root, text=text)
        lbl.pack(pady=(10, 2), anchor="w", padx=20)

    def add_entry(self):
        entry = ttk.Entry(self.root, width=70)
        entry.pack(pady=2, padx=20)
        return entry

    def choose_folder(self):
        folder = filedialog.askdirectory(title=self.strings["folder_label"])
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def choose_local_video(self):
        path = filedialog.askopenfilename(
            filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov *.ts"), ("All files", "*.*")]
        )
        if path:
            self.play_video(path)

    def download_video(self):
        self.progress["value"] = 0
        self.root.update_idletasks()

        platform = self.platform.get()
        url = self.url_entry.get().strip()
        quality = self.quality_entry.get().strip() or "best"
        filename = self.filename_entry.get().strip() or "video"
        folder = self.folder_entry.get().strip()

        if not url or not folder:
            messagebox.showerror(self.strings["error_title"], self.strings["error_no_url_folder"])
            return

        if platform == "twitch":
            ext = ".ts"
            output_path = os.path.join(folder, filename + ext)
            self.last_video_path = output_path
            self.status_label.config(text=self.strings["status_downloading_twitch"], foreground="#bbbbbb")
            self.root.update_idletasks()
            command = ["streamlink", url, quality, "-o", output_path]
            try:
                subprocess.run(command, check=True)
                self.status_label.config(text=self.strings["status_finished"].format(output_path), foreground="lightgreen")
            except subprocess.CalledProcessError as e:
                self.status_label.config(text=self.strings["status_error"], foreground="red")
                messagebox.showerror(self.strings["error_title"], str(e))
        else:
            ext = ".mp4"
            output_path = os.path.join(folder, filename + ext)
            self.last_video_path = output_path
            self.status_label.config(text=self.strings["status_downloading_youtube"], foreground="#bbbbbb")
            self.root.update_idletasks()

            def progress_hook(d):
                if d['status'] == 'downloading':
                    if d.get('total_bytes') and d.get('downloaded_bytes'):
                        percent = d['downloaded_bytes'] / d['total_bytes'] * 100
                        self.progress["value"] = percent
                        status_text = f"📥 YouTube: {percent:.1f}% heruntergeladen" if self.is_german else f"📥 YouTube: {percent:.1f}% downloaded"
                        self.status_label.config(text=status_text, foreground="#cccccc")
                        self.root.update_idletasks()
                elif d['status'] == 'finished':
                    self.progress["value"] = 100
                    self.status_label.config(text=self.strings["status_finished"].format(output_path), foreground="lightgreen")

            ydl_opts = {
                'outtmpl': output_path,
                'progress_hooks': [progress_hook],
                'quiet': False,  # Für Debugging, ggf auf True setzen
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
            }

            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
            except Exception as e:
                self.status_label.config(text=self.strings["status_error"], foreground="red")
                messagebox.showerror(self.strings["error_title"], str(e))

    def play_last_video(self):
        if not hasattr(self, "last_video_path") or not os.path.exists(self.last_video_path):
            messagebox.showwarning(self.strings["warning_title"], self.strings["no_video_warn"])
            return
        self.play_video(self.last_video_path)

    def play_video(self, path):
        self.stop_video()
        self.video_path = path
        self.player = MediaPlayer(path, ff_opts={'paused': False})
        self.is_playing = True
        self.is_paused = False
        self.muted = False
        self.pause_button.config(text=self.strings["pause"])
        self.mute_button.config(text=self.strings["mute"])
        self.update_frame()

    def update_frame(self):
        if not self.is_playing or not self.player:
            return
        frame, val = self.player.get_frame()
        if val == 'eof':
            self.stop_video()
            return
        if frame is not None:
            img, pts = frame
            try:
                w, h = img.get_size()
                pix_fmt = img.get_pixel_format()
                img_bytes, *rest = img.to_bytearray()

                if pix_fmt in ('rgb24', 'bgr24'):
                    pil_img = Image.frombytes('RGB', (w, h), bytes(img_bytes))
                elif pix_fmt in ('rgba', 'bgra'):
                    pil_img = Image.frombytes('RGBA', (w, h), bytes(img_bytes))
                else:
                    img_bytes, *_ = img.to_bytearray(fmt='rgba')
                    pil_img = Image.frombytes('RGBA', (w, h), bytes(img_bytes))

                max_width, max_height = 760, 480
                scale = min(max_width / w, max_height / h, 1)

                new_w, new_h = int(w * scale), int(h * scale)
                pil_img = pil_img.resize((new_w, new_h), Image.LANCZOS)

                self.video_panel.config(width=new_w, height=new_h)

                self.photo = ImageTk.PhotoImage(image=pil_img)
                self.video_panel.delete("all")
                self.video_panel.create_image(0, 0, anchor="nw", image=self.photo)
            except Exception as e:
                self.status_label.config(text="Videoanzeige-Fehler: " + str(e), foreground="orange")
                self.stop_video()
                return
        self.after_id = self.root.after(30, self.update_frame)

    def toggle_pause(self):
        if not self.player:
            return
        if self.is_paused:
            self.player.set_pause(False)
            self.is_paused = False
            self.pause_button.config(text=self.strings["pause"])
        else:
            self.player.set_pause(True)
            self.is_paused = True
            self.pause_button.config(text=self.strings["play"])

    def toggle_mute(self):
        if not self.player:
            return
        self.muted = not self.muted
        self.player.set_volume(0.0 if self.muted else 1.0)
        self.mute_button.config(text=self.strings["unmute"] if self.muted else self.strings["mute"])

    def skip_forward(self):
        if self.player:
            current_time = self.player.get_pts()
            if current_time is None:
                current_time = 0
            self.player.seek(current_time + 10, relative=False)

    def skip_back(self):
        if self.player:
            current_time = self.player.get_pts()
            if current_time is None:
                current_time = 0
            self.player.seek(max(0, current_time - 10), relative=False)

    def stop_video(self):
        self.is_playing = False
        self.is_paused = False
        if self.player:
            self.player.close_player()
            self.player = None
        if self.after_id:
            self.root.after_cancel(self.after_id)
            self.after_id = None
        self.video_panel.delete("all")
        self.pause_button.config(text=self.strings["pause"])
        self.mute_button.config(text=self.strings["mute"])

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.mainloop()
