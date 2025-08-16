# ================================
# File: app.py
# Simple Windows GUI that downloads 1080p or 720p and merges to one MP4.
# Requires: Python 3.10+, yt-dlp, FFmpeg in PATH
# ================================
import os
import sys
import threading
import queue
from tkinter import Tk, Text, END, DISABLED, NORMAL, filedialog, messagebox
from tkinter import ttk, StringVar

try:
    from yt_dlp import YoutubeDL
except Exception as e:
    raise SystemExit("yt-dlp is required. Install it with: pip install yt-dlp")

APP_TITLE = "MP4 Downloader (1080p/720p)"

# Restrict to two presets, always merged to MP4
FORMAT_PRESETS = {
    "1080p MP4": "bestvideo[height<=1080][vcodec^=avc1]/bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p MP4": "bestvideo[height<=720][vcodec^=avc1]/bestvideo[height<=720]+bestaudio/best[height<=720]",
}

class App:
    def __init__(self, root: Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("780x520")
        self.msg_queue = queue.Queue()
        self.worker = None
        self.stop_flag = False

        self.url_box = None
        self.out_var = StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads"))
        self.preset_var = StringVar(value="1080p MP4")

        self._build_ui()
        self.root.after(100, self._poll)

    def _build_ui(self):
        pad = {"padx": 10, "pady": 8}
        frm = ttk.Frame(self.root)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="Paste video/playlist URLs (one per line)").grid(row=0, column=0, sticky='w', **pad)
        self.url_box = Text(frm, height=6, wrap='word')
        self.url_box.grid(row=1, column=0, columnspan=3, sticky='nsew', **pad)

        ttk.Label(frm, text="Save to:").grid(row=2, column=0, sticky='w', **pad)
        ent = ttk.Entry(frm, textvariable=self.out_var, width=50)
        ent.grid(row=2, column=1, sticky='we', **pad)
        ttk.Button(frm, text="Browse…", command=self._browse).grid(row=2, column=2, sticky='we', **pad)

        ttk.Label(frm, text="Quality:").grid(row=3, column=0, sticky='w', **pad)
        cb = ttk.Combobox(frm, textvariable=self.preset_var, values=list(FORMAT_PRESETS.keys()), state='readonly')
        cb.grid(row=3, column=1, sticky='we', **pad)

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, sticky='w', **pad)
        ttk.Button(btns, text="Start", command=self._start).pack(side='left', padx=6)
        ttk.Button(btns, text="Stop", command=self._stop).pack(side='left', padx=6)
        ttk.Button(btns, text="Open Folder", command=self._open).pack(side='left', padx=6)
        ttk.Button(btns, text="Clear Log", command=self._clear_log).pack(side='left', padx=6)

        ttk.Label(frm, text="Progress:").grid(row=5, column=0, sticky='w', **pad)
        self.pbar = ttk.Progressbar(frm, orient='horizontal', mode='determinate', maximum=100)
        self.pbar.grid(row=5, column=1, columnspan=2, sticky='we', **pad)

        ttk.Label(frm, text="Log:").grid(row=6, column=0, sticky='w', **pad)
        self.log = Text(frm, height=12, wrap='word', state=DISABLED)
        self.log.grid(row=7, column=0, columnspan=3, sticky='nsew', **pad)

        frm.rowconfigure(7, weight=1)
        frm.columnconfigure(1, weight=1)

    def _browse(self):
        path = filedialog.askdirectory(initialdir=self.out_var.get() or os.path.expanduser("~"))
        if path:
            self.out_var.set(path)

    def _open(self):
        p = self.out_var.get()
        if os.path.isdir(p):
            if sys.platform == 'win32':
                os.startfile(p)
            elif sys.platform == 'darwin':
                os.system(f'open "{p}"')
            else:
                os.system(f'xdg-open "{p}"')
        else:
            messagebox.showerror(APP_TITLE, "Folder does not exist.")

    def _clear_log(self):
        self.log.configure(state=NORMAL)
        self.log.delete('1.0', END)
        self.log.configure(state=DISABLED)

    def _start(self):
        urls = [u.strip() for u in self.url_box.get('1.0', END).splitlines() if u.strip()]
        if not urls:
            messagebox.showwarning(APP_TITLE, "Please paste at least one URL.")
            return
        out = self.out_var.get().strip()
        if not out:
            messagebox.showwarning(APP_TITLE, "Please choose a save folder.")
            return
        os.makedirs(out, exist_ok=True)

        if self.worker and self.worker.is_alive():
            messagebox.showinfo(APP_TITLE, "Already running.")
            return

        self.stop_flag = False
        fmt = FORMAT_PRESETS.get(self.preset_var.get(), "bestvideo[height<=1080]+bestaudio")

        ydl_opts = {
            'outtmpl': os.path.join(out, '%(title)s.%(ext)s'),
            'format': fmt,
            'merge_output_format': 'mp4',  # force MP4 merge
            'noplaylist': False,
            'ignoreerrors': True,
            'retries': 5,
            'concurrent_fragment_downloads': 4,
            'progress_hooks': [self._hook],
            'quiet': True,
            'no_warnings': True,
        }

        self.worker = threading.Thread(target=self._run, args=(urls, ydl_opts), daemon=True)
        self.worker.start()
        self._log("Started…\n")

    def _stop(self):
        self.stop_flag = True
        self._log("Stop requested.\n")

    def _hook(self, d):
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            done = d.get('downloaded_bytes') or 0
            pct = (done/total*100.0) if total else 0.0
            spd = d.get('speed') or 0
            eta = d.get('eta')
            status = f"{pct:.1f}% — {self._hs(done)} of {self._hs(total)}"
            if spd:
                status += f" @ {self._hs(spd)}/s"
            if eta is not None:
                status += f" (ETA {eta}s)"
            self.msg_queue.put(("progress", pct, status))
        elif d.get('status') in ('finished', 'postprocessing'):
            self.msg_queue.put(("progress", 100.0, 'Processing…'))

    def _run(self, urls, ydl_opts):
        try:
            with YoutubeDL(ydl_opts) as ydl:
                total = len(urls)
                for i, u in enumerate(urls, 1):
                    if self.stop_flag:
                        self._log("Stopped by user.\n")
                        break
                    self._log(f"[{i}/{total}] {u}\n")
                    try:
                        ydl.download([u])
                        self._log("   ✔ Done\n")
                    except Exception as e:
                        self._log(f"   ✖ Error: {e}\n")
            self.msg_queue.put(("progress", 0.0, APP_TITLE))
            self._log("All tasks finished.\n")
        except Exception as e:
            self._log(f"Fatal error: {e}\n")

    def _poll(self):
        try:
            while True:
                item = self.msg_queue.get_nowait()
                if item[0] == 'progress':
                    _, pct, title = item
                    self.pbar['value'] = max(0, min(100, pct))
                    if title:
                        self.root.title(f"{APP_TITLE} — {title}")
                elif item[0] == 'log':
                    self.log.configure(state=NORMAL)
                    self.log.insert(END, item[1])
                    self.log.see(END)
                    self.log.configure(state=DISABLED)
                self.msg_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll)

    def _log(self, s: str):
        self.msg_queue.put(("log", s))

    @staticmethod
    def _hs(n):
        try:
            n = float(n)
        except Exception:
            return "0B"
        units = ['B','KB','MB','GB','TB']
        i = 0
        while n >= 1024 and i < len(units)-1:
            n /= 1024.0
            i += 1
        return f"{n:.1f}{units[i]}"


def main():
    root = Tk()
    try:
        # Optional: if you have a ttk theme file available
        root.call("set_theme", "light")
    except Exception:
        pass
    app = App(root)
    root.mainloop()

if __name__ == '__main__':
    main()

# ================================
# File: build.bat
# Double-click this on Windows to build a single .exe in .\dist\MP4Downloader.exe
# ================================
# --- Save the following into a separate file named build.bat (Windows Batch) ---
# @echo off
# setlocal
# echo Checking Python...
# where python >nul 2>nul || (
#   echo Python not found. Install Python 3.10+ and re-run.
#   pause & exit /b 1
# )
# echo Installing dependencies...
# python -m pip install --upgrade pip yt-dlp pyinstaller
# echo Building EXE...
# pyinstaller --onefile --noconsole --name MP4Downloader app.py
# if %errorlevel% neq 0 (
#   echo Build failed.
#   pause & exit /b 1
# )
# echo Build complete: dist\MP4Downloader.exe
# echo NOTE: FFmpeg must be in your PATH to merge to MP4.
# pause

# ================================
# File: README.txt
# ================================
# 1) Install Python 3.10+ (make sure "Add Python to PATH" is checked).
# 2) Install FFmpeg and add its bin folder to PATH (so merging works):
#    - Easiest (Chocolatey): choco install ffmpeg
#    - Or manual: download a Windows FFmpeg build and add \bin to PATH.
# 3) Save app.py and build.bat in the same folder.
# 4) Double-click build.bat.
# 5) Your EXE will be at .\dist\MP4Downloader.exe
# 6) Run it, paste URLs, pick 1080p or 720p, Start.
