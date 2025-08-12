#!/usr/bin/env python3
# skindrops_splitter_embedded.py
# Self-contained friendly: works with system FFmpeg, OR with bundled ffmpeg/ffprobe when built by PyInstaller.
#
# How to build one-click EXE (Windows):
#   1) Put this script and ffmpeg binaries in a subfolder "ffmpeg_win" like:
#        ffmpeg_win/ffmpeg.exe
#        ffmpeg_win/ffprobe.exe
#   2) Install PyInstaller:  pip install pyinstaller
#   3) Build:
#        pyinstaller --onefile --noconsole ^
#          --add-binary "ffmpeg_win/ffmpeg.exe;ffmpeg_win" ^
#          --add-binary "ffmpeg_win/ffprobe.exe;ffmpeg_win" ^
#          skindrops_splitter_embedded.py
#
# After build, distribute only the created .exe. No Python/FFmpeg install needed.
#
import os, sys, subprocess, shlex, random, json, tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

APP_NAME = "Skindrops Splitter"
VERSION = "1.1 (embedded ffmpeg support)"

def resource_path(rel):
    """Get absolute path to resource, works for dev and for PyInstaller bundling."""
    base = getattr(sys, "_MEIPASS", Path(__file__).parent)
    return str(Path(base) / rel)

def bundled_ffmpeg_paths():
    # If built with --add-binary "...;ffmpeg_win", they'll live under <_MEIPASS>/ffmpeg_win/
    ffmpeg_p = Path(resource_path("ffmpeg_win")) / ("ffmpeg.exe" if os.name == "nt" else "ffmpeg")
    ffprobe_p = Path(resource_path("ffmpeg_win")) / ("ffprobe.exe" if os.name == "nt" else "ffprobe")
    return ffmpeg_p if ffmpeg_p.exists() else None, ffprobe_p if ffprobe_p.exists() else None

def which(cmd):
    from shutil import which as _which
    return _which(cmd)

def resolve_bins():
    """Return (ffmpeg, ffprobe) executable paths to use."""
    b_ffmpeg, b_ffprobe = bundled_ffmpeg_paths()
    if b_ffmpeg and b_ffprobe:
        return str(b_ffmpeg), str(b_ffprobe)
    # fallback to system PATH
    ffmpeg = which("ffmpeg")
    ffprobe = which("ffprobe")
    return ffmpeg, ffprobe

def probe_duration(ffprobe, infile):
    try:
        p = subprocess.run(
            [ffprobe,"-v","error","-show_entries","format=duration","-of","json", infile],
            capture_output=True, text=True, check=False
        )
        if p.returncode != 0: return None
        data = json.loads(p.stdout or "{}")
        d = float(data.get("format",{}).get("duration",0.0))
        return d if d > 0 else None
    except Exception:
        return None

def build_cmd(ffmpeg, infile, outfile, start, dur=1.0):
    # Re-encode for exact 1.000s cuts regardless of keyframes
    return " ".join(shlex.quote(x) for x in [
        ffmpeg, "-y", "-ss", f"{start:.3f}", "-i", infile,
        "-t", f"{dur:.3f}", "-c:v","libx264","-preset","veryfast","-crf","20",
        "-c:a","aac","-b:a","128k", outfile
    ])

def run_cmd(cmd):
    print(">>>", cmd)
    return subprocess.call(cmd, shell=True) == 0

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("640x360")
        self.resizable(False, False)
        self.infile = tk.StringVar()
        self.outdir = tk.StringVar(value="")
        self.ffmpeg, self.ffprobe = resolve_bins()
        self.create_widgets()

    def create_widgets(self):
        pad = {'padx':10, 'pady':6}
        frm = ttk.Frame(self); frm.pack(fill='both', expand=True, **pad)

        ttk.Label(frm, text="Input video:").grid(row=0,column=0,sticky='w')
        ttk.Entry(frm, textvariable=self.infile, width=60).grid(row=0,column=1,sticky='we')
        ttk.Button(frm, text="Browse", command=self.pick_in).grid(row=0,column=2,sticky='we',padx=5)

        ttk.Label(frm, text="Output folder (optional):").grid(row=1,column=0,sticky='w')
        ttk.Entry(frm, textvariable=self.outdir, width=60).grid(row=1,column=1,sticky='we')
        ttk.Button(frm, text="Browse", command=self.pick_out).grid(row=1,column=2,sticky='we',padx=5)

        sep = ttk.Separator(frm); sep.grid(row=2,column=0,columnspan=3,sticky='we',pady=6)

        btns = ttk.Frame(frm); btns.grid(row=3,column=0,columnspan=3,sticky='we')
        ttk.Button(btns, text="Random 1s", command=self.do_random).grid(row=0,column=0,padx=5,pady=6)
        ttk.Button(btns, text="First 1s",  command=self.do_first).grid(row=0,column=1,padx=5,pady=6)
        ttk.Button(btns, text="Middle 1s", command=self.do_middle).grid(row=0,column=2,padx=5,pady=6)
        ttk.Button(btns, text="Last 1s",   command=self.do_last).grid(row=0,column=3,padx=5,pady=6)
        ttk.Button(btns, text="Generate All 4", command=self.do_all).grid(row=0,column=4,padx=12,pady=6)

        self.status = tk.StringVar(value="Ready")
        ttk.Label(frm, textvariable=self.status, foreground="#0a7").grid(row=4,column=0,columnspan=3,sticky='w')

        for i in range(3):
            frm.grid_columnconfigure(i, weight=1)

    def pick_in(self):
        f = filedialog.askopenfilename(title="Choose a video",
            filetypes=[("Video","*.mp4 *.mov *.mkv *.webm"),("All","*.*")])
        if f: self.infile.set(f)

    def pick_out(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d: self.outdir.set(d)

    def ensure_ready(self):
        if not self.ffmpeg or not self.ffprobe:
            messagebox.showerror(APP_NAME, "FFmpeg/ffprobe not found.\nIf using the EXE build, make sure they were bundled. Otherwise, add to PATH.")
            return None, None, None
        infile = self.infile.get().strip()
        if not infile or not os.path.isfile(infile):
            messagebox.showerror(APP_NAME, "Please choose a valid input video.")
            return None, None, None
        outdir = self.outdir.get().strip() or str(Path(infile).parent)
        Path(outdir).mkdir(parents=True, exist_ok=True)
        dur = probe_duration(self.ffprobe, infile)
        if not dur or dur <= 1.0:
            messagebox.showerror(APP_NAME, "Could not read duration or video shorter than 1s.")
            return None, None, None
        return infile, outdir, dur

    def base_out(self, outdir, tag):
        base = Path(self.infile.get()).stem
        return str(Path(outdir) / f"{base}_{tag}.mp4")

    def cut_at(self, start, tag):
        ready = self.ensure_ready()
        if not ready: return
        infile, outdir, dur = ready
        start = max(0.0, min(start, max(0.0, dur-1.0)))
        outfile = self.base_out(outdir, tag)
        cmd = build_cmd(self.ffmpeg, infile, outfile, start, dur=1.0)
        self.status.set(f"Working: {tag} ...")
        self.update_idletasks()
        ok = run_cmd(cmd)
        self.status.set(f"Done: {outfile}" if ok else "Error — see console.")

    def do_random(self):
        ready = self.ensure_ready()
        if not ready: return
        infile, outdir, dur = ready
        start = 0.0 if dur<=1.0 else random.uniform(0.0, max(0.0, dur-1.0))
        self.cut_at(start, "random1s")

    def do_first(self):
        self.cut_at(0.0, "first1s")

    def do_middle(self):
        ready = self.ensure_ready()
        if not ready: return
        infile, outdir, dur = ready
        mid = max(0.0, (dur/2.0) - 0.5)
        self.cut_at(mid, "middle1s")

    def do_last(self):
        ready = self.ensure_ready()
        if not ready: return
        infile, outdir, dur = ready
        last = max(0.0, dur - 1.0)
        self.cut_at(last, "last1s")

    def do_all(self):
        ready = self.ensure_ready()
        if not ready: return
        infile, outdir, dur = ready
        self.cut_at(0.0, "first1s")
        self.cut_at(max(0.0, (dur/2.0) - 0.5), "middle1s")
        self.cut_at(max(0.0, dur - 1.0), "last1s")
        rand = 0.0 if dur<=1.0 else random.uniform(0.0, max(0.0, dur-1.0))
        self.cut_at(rand, "random1s")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
