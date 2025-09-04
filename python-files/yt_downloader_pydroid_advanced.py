#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Downloader GUI for Pydroid 3 (Android)
- Full-screen window
- Scrollable UI (works on small screens)
- Video up to 4K, Audio-only -> auto-convert to MP3 (requires ffmpeg)
- Playlist support with automatic playlist subfolder
- Playlist range selection (e.g., 1-5 or 2,4,6)
- Progress bar + log
- Persist settings between runs
"""
import os
import sys
import json
import threading
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    import yt_dlp as ytdlp
except Exception as e:
    raise SystemExit(
        "yt-dlp is not installed. In Pydroid 3 install it via Pip (pip install yt-dlp).\nImport error: " + str(e)
    )

# ---------- Config ----------
APP_TITLE = "YouTube Downloader (Pydroid)"
SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".yt_downloader_settings.json")

DEFAULT_DIRS = [
    "/sdcard/Download",
    "/storage/emulated/0/Download",
    "/sdcard",
    os.path.expanduser("~"),
    os.getcwd()
]

QUALITY_PRESETS = [
    "Best available",
    "2160p (4K)",
    "1440p (2K)",
    "1080p",
    "720p",
    "480p",
    "360p",
    "240p",
    "144p",
    "Audio only"
]

# ---------- Utilities ----------
def get_writable_default_dir():
    for d in DEFAULT_DIRS:
        try:
            if os.path.isdir(d) and os.access(d, os.W_OK):
                return d
        except Exception:
            continue
    return os.getcwd()

def load_settings():
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
    except Exception:
        pass
    return {
        "download_dir": get_writable_default_dir(),
        "quality": "Best available",
        "audio_to_mp3": False,
        "embed_subs": False,
        "write_description": False,
        "write_infojson": False,
        "auto_playlist_folder": True,
        "playlist_range": "",
        "outtmpl": "%(title)s [%(id)s].%(ext)s"
    }

def save_settings(s):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(s, f, indent=2)
    except Exception:
        pass

# ---------- App ----------
class ScrollableFrame(ttk.Frame):
    """
    A scrollable frame using a Canvas and a vertical scrollbar.
    Place your widgets inside `frame` attribute.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.frame = ttk.Frame(self.canvas)
        self.frame_id = self.canvas.create_window((0,0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Allow mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)  # Windows/Android (may vary)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)    # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)    # Linux scroll down

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Update the inner frame's width to fill canvas
        canvas_width = event.width
        self.canvas.itemconfig(self.frame_id, width=canvas_width)

    def _on_mousewheel(self, event):
        # Delta handling across platforms
        if event.num == 5 or event.delta == -120:
            self.canvas.yview_scroll(1, "units")
        elif event.num == 4 or event.delta == 120:
            self.canvas.yview_scroll(-1, "units")

class DownloaderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        # Fullscreen-ish: use screen size
        try:
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            # small margin to prevent oversize in some Android environments
            self.geometry(f"{sw}x{sh}")
        except Exception:
            self.geometry("800x600")

        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except Exception:
            pass

        self.settings = load_settings()
        self.downloader = None
        self.stop_requested = False

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        self.container = ScrollableFrame(self)
        self.container.pack(fill="both", expand=True)

        frm = self.container.frame
        padx = 10
        pady = 8

        # URL
        ttk.Label(frm, text="YouTube URL (video or playlist):", font=("Arial", 11, "bold")).grid(row=0, column=0, sticky="w", padx=padx, pady=(pady,2))
        self.url_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.url_var).grid(row=1, column=0, columnspan=3, sticky="we", padx=padx)

        # Download folder
        ttk.Label(frm, text="Download folder:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", padx=padx, pady=(8,2))
        self.dir_var = tk.StringVar(value=self.settings.get("download_dir", get_writable_default_dir()))
        ent_dir = ttk.Entry(frm, textvariable=self.dir_var)
        ent_dir.grid(row=3, column=0, sticky="we", padx=(padx,4))
        ttk.Button(frm, text="Browse", command=self._browse_dir).grid(row=3, column=1, sticky="w")

        # Playlist range
        ttk.Label(frm, text="Playlist range (e.g., 1-5 or 2,4,6) [optional]:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", padx=padx, pady=(8,2))
        self.playlist_range_var = tk.StringVar(value=self.settings.get("playlist_range",""))
        ttk.Entry(frm, textvariable=self.playlist_range_var).grid(row=5, column=0, columnspan=2, sticky="we", padx=padx)

        # Quality
        ttk.Label(frm, text="Quality:", font=("Arial", 10)).grid(row=6, column=0, sticky="w", padx=padx, pady=(8,2))
        self.quality_var = tk.StringVar(value=self.settings.get("quality","Best available"))
        cmb = ttk.Combobox(frm, textvariable=self.quality_var, values=QUALITY_PRESETS, state="readonly")
        cmb.grid(row=7, column=0, columnspan=2, sticky="we", padx=padx)

        # Advanced options
        row = 8
        self.audio_to_mp3_var = tk.BooleanVar(value=self.settings.get("audio_to_mp3", False))
        ttk.Checkbutton(frm, text="Convert audio to MP3 (requires ffmpeg)", variable=self.audio_to_mp3_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=padx, pady=(8,0))

        row += 1
        self.embed_subs_var = tk.BooleanVar(value=self.settings.get("embed_subs", False))
        ttk.Checkbutton(frm, text="Embed subtitles if available", variable=self.embed_subs_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=padx)

        row += 1
        self.write_desc_var = tk.BooleanVar(value=self.settings.get("write_description", False))
        ttk.Checkbutton(frm, text="Write video description to file", variable=self.write_desc_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=padx)

        row += 1
        self.write_infojson_var = tk.BooleanVar(value=self.settings.get("write_infojson", False))
        ttk.Checkbutton(frm, text="Write video info JSON", variable=self.write_infojson_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=padx)

        row += 1
        self.auto_playlist_folder_var = tk.BooleanVar(value=self.settings.get("auto_playlist_folder", True))
        ttk.Checkbutton(frm, text="Create subfolder for playlist (playlist title)", variable=self.auto_playlist_folder_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=padx)

        # Outtmpl entry (advanced)
        row += 1
        ttk.Label(frm, text="Filename template (yt-dlp outtmpl):", font=("Arial", 10)).grid(row=row, column=0, sticky="w", padx=padx, pady=(8,2))
        row += 1
        self.outtmpl_var = tk.StringVar(value=self.settings.get("outtmpl", "%(title)s [%(id)s].%(ext)s"))
        ttk.Entry(frm, textvariable=self.outtmpl_var).grid(row=row, column=0, columnspan=2, sticky="we", padx=padx)

        # Progress
        row += 1
        ttk.Label(frm, text="Progress:", font=("Arial", 10)).grid(row=row, column=0, sticky="w", padx=padx, pady=(10,2))
        row += 1
        self.progress = ttk.Progressbar(frm, orient="horizontal", mode="determinate", maximum=100)
        self.progress.grid(row=row, column=0, columnspan=2, sticky="we", padx=padx)

        row += 1
        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(frm, textvariable=self.status_var).grid(row=row, column=0, columnspan=2, sticky="w", padx=padx, pady=(6,4))

        # Log
        row += 1
        ttk.Label(frm, text="Log:", font=("Arial", 10)).grid(row=row, column=0, sticky="w", padx=padx, pady=(8,2))
        row += 1
        self.txt_log = tk.Text(frm, height=10, wrap="word")
        self.txt_log.grid(row=row, column=0, columnspan=2, sticky="we", padx=padx, pady=(4,8))

        # Buttons
        row += 1
        btn_frame = ttk.Frame(frm)
        btn_frame.grid(row=row, column=0, columnspan=2, sticky="we", padx=padx, pady=(8,12))
        self.btn_start = ttk.Button(btn_frame, text="Start Download", command=self._on_start)
        self.btn_start.pack(side="left", padx=(0,6))
        self.btn_stop = ttk.Button(btn_frame, text="Stop", command=self._on_stop, state="disabled")
        self.btn_stop.pack(side="left", padx=(6,6))
        ttk.Button(btn_frame, text="Save Settings", command=self._save_settings).pack(side="right")
        ttk.Button(btn_frame, text="Clear Log", command=lambda: self.txt_log.delete("1.0", "end")).pack(side="right", padx=(6,0))

        # Make grid expand properly
        for c in range(2):
            frm.grid_columnconfigure(c, weight=1)

    # ---------- helpers ----------
    def _log(self, msg):
        try:
            self.txt_log.insert("end", msg + "\n")
            self.txt_log.see("end")
        except Exception:
            pass

    def _set_status(self, msg):
        try:
            self.status_var.set(msg)
        except Exception:
            pass

    def _browse_dir(self):
        start = self.dir_var.get() or get_writable_default_dir()
        p = filedialog.askdirectory(initialdir=start, title="Choose download folder")
        if p:
            self.dir_var.set(p)

    def _save_settings(self):
        s = {
            "download_dir": self.dir_var.get(),
            "quality": self.quality_var.get(),
            "audio_to_mp3": bool(self.audio_to_mp3_var.get()),
            "embed_subs": bool(self.embed_subs_var.get()),
            "write_description": bool(self.write_desc_var.get()),
            "write_infojson": bool(self.write_infojson_var.get()),
            "auto_playlist_folder": bool(self.auto_playlist_folder_var.get()),
            "playlist_range": self.playlist_range_var.get().strip(),
            "outtmpl": self.outtmpl_var.get().strip() or "%(title)s [%(id)s].%(ext)s"
        }
        save_settings(s)
        self._log("Settings saved.")
        messagebox.showinfo("Saved", "Settings saved.")

    # ---------- yt-dlp options builders ----------
    def _format_for_quality(self):
        q = self.quality_var.get()
        if q == "Audio only":
            return "bestaudio/best"
        if q == "Best available":
            return "bestvideo*+bestaudio/best"
        mapping = {
            "2160p (4K)": 2160,
            "1440p (2K)": 1440,
            "1080p": 1080,
            "720p": 720,
            "480p": 480,
            "360p": 360,
            "240p": 240,
            "144p": 144,
        }
        for name, h in mapping.items():
            if q.startswith(name):
                return f"bestvideo[height<={h}]+bestaudio/best[height<={h}]"
        return "bestvideo*+bestaudio/best"

    def _safe_outtmpl(self, tpl):
        # Prevent absolute path injections
        tpl = (tpl or "%(title)s [%(id)s].%(ext)s").strip()
        tpl = tpl.replace("../", "").replace("..\\", "")
        return tpl

    def _build_ytdlp_opts(self, out_dir):
        fmt = self._format_for_quality()
        outtmpl_template = self._safe_outtmpl(self.outtmpl_var.get())

        if self.auto_playlist_folder_var.get():
            outtmpl = os.path.join(out_dir, "%(playlist_title)s", outtmpl_template)
        else:
            outtmpl = os.path.join(out_dir, outtmpl_template)

        postprocessors = []
        # If user explicitly checked convert to mp3 OR quality is Audio only -> add mp3 extractor
        audio_choice = (self.quality_var.get() == "Audio only")
        if self.audio_to_mp3_var.get() or audio_choice:
            postprocessors.append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            })
        if self.embed_subs_var.get():
            postprocessors.append({"key": "FFmpegEmbedSubtitle"})

        opts = {
            "format": fmt,
            "outtmpl": outtmpl,
            "noplaylist": False,  # allow playlist URLs
            "ignoreerrors": True,
            "retries": 5,
            "concurrent_fragment_downloads": 3,
            "progress_hooks": [self._progress_hook],
            "no_warnings": True,
            "quiet": True,
            "nocheckcertificate": True,
        }

        if postprocessors:
            opts["postprocessors"] = postprocessors
        if self.write_desc_var.get():
            opts["writedescription"] = True
        if self.write_infojson_var.get():
            opts["writeinfojson"] = True

        pr = self.playlist_range_var.get().strip()
        if pr:
            opts["playlist_items"] = pr

        return opts

    # ---------- progress hook ----------
    def _progress_hook(self, d):
        try:
            status = d.get("status")
            if status == "downloading":
                percent = 0.0
                pct_str = d.get("_percent_str")
                if pct_str:
                    try:
                        percent = float(pct_str.strip().replace("%", ""))
                    except Exception:
                        percent = 0.0
                else:
                    try:
                        downloaded = d.get("downloaded_bytes") or 0
                        total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
                        if total:
                            percent = (downloaded / total) * 100.0
                    except Exception:
                        percent = 0.0
                filename = os.path.basename(d.get("filename") or "")
                speed = d.get("_speed_str", "")
                eta = d.get("_eta_str", "")
                self.after(0, lambda p=percent: self.progress.configure(value=min(max(p, 0.0), 100.0)))
                self.after(0, lambda: self._set_status(f"Downloading: {filename} — {percent:.1f}%  ETA: {eta}  Speed: {speed}"))
            elif status == "finished":
                self.after(0, lambda: self._set_status("Post-processing..."))
                self.after(0, lambda: self.progress.configure(value=100))
            elif status == "error":
                self.after(0, lambda: self._set_status("Error during download"))
        except Exception:
            pass

    # ---------- start/stop/download worker ----------
    def _on_start(self):
        if self.downloader is not None:
            return
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("Missing URL", "Please paste a video or playlist URL.")
            return

        out_dir = self.dir_var.get().strip() or get_writable_default_dir()
        try:
            os.makedirs(out_dir, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Folder Error", f"Cannot create or write to:\n{out_dir}\n\n{e}")
            return

        # persist settings
        self.settings.update({
            "download_dir": out_dir,
            "quality": self.quality_var.get(),
            "audio_to_mp3": bool(self.audio_to_mp3_var.get()),
            "embed_subs": bool(self.embed_subs_var.get()),
            "write_description": bool(self.write_desc_var.get()),
            "write_infojson": bool(self.write_infojson_var.get()),
            "auto_playlist_folder": bool(self.auto_playlist_folder_var.get()),
            "playlist_range": self.playlist_range_var.get().strip(),
            "outtmpl": self.outtmpl_var.get().strip() or "%(title)s [%(id)s].%(ext)s"
        })
        save_settings(self.settings)

        self.txt_log.delete("1.0", "end")
        self.progress.configure(value=0)
        self._set_status("Starting...")
        self._log(f"Start: {url}")
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        self.stop_requested = False

        t = threading.Thread(target=self._worker_thread, args=(url, out_dir), daemon=True)
        t.start()

    def _on_stop(self):
        self.stop_requested = True
        self._log("Stop requested.")
        self._set_status("Stopping...")

    def _worker_thread(self, url, out_dir):
        try:
            opts = self._build_ytdlp_opts(out_dir)
            self.after(0, lambda: self._log(f"Options: format={opts.get('format')}, outtmpl={opts.get('outtmpl')}"))
            with ytdlp.YoutubeDL(opts) as ydl:
                self.downloader = ydl
                # If we need to abort, raise KeyboardInterrupt from here if stop_requested flagged
                try:
                    if self.stop_requested:
                        raise KeyboardInterrupt("User requested stop.")
                    ydl.download([url])
                except KeyboardInterrupt:
                    self.after(0, lambda: self._log("Download interrupted by user."))
                except Exception as e:
                    self.after(0, lambda: self._log("Downloader error: " + str(e)))
                    self.after(0, lambda: self._log(traceback.format_exc()))
                    raise
        except Exception as e:
            self.after(0, lambda: self._set_status("Failed ❌"))
            self.after(0, lambda: self._log("Error: " + str(e)))
        else:
            self.after(0, lambda: self._set_status("Done ✅"))
            self.after(0, lambda: self._log("Download completed."))
        finally:
            self.downloader = None
            self.after(0, lambda: self.btn_start.config(state="normal"))
            self.after(0, lambda: self.btn_stop.config(state="disabled"))

    def _on_close(self):
        if self.downloader is not None:
            if not messagebox.askyesno("Exit", "A download may be in progress. Exit anyway?"):
                return
        self.destroy()

# ---------- run ----------
def main():
    app = DownloaderApp()
    app.mainloop()

if __name__ == "__main__":
    main()