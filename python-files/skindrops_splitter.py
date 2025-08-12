#!/usr/bin/env python3
# skindrops_splitter.py
# A tiny Windows-friendly GUI app that creates 1-second variants of a video.
# Modes:
#   - Random 1s
#   - First 1s
#   - Middle 1s
#   - Last 1s
#   - Generate All 4
#
# Requirements:
#   - Python 3.8+
#   - ffmpeg + ffprobe in PATH (download from ffmpeg.org; on Windows place ffmpeg.exe and ffprobe.exe next to the .exe or add to PATH)
#
# Build as .exe (Windows):
#   pip install pyinstaller
#   pyinstaller --onefile --noconsole skindrops_splitter.py
#   (Place ffmpeg.exe and ffprobe.exe in the same folder as the generated .exe, or ensure they are on PATH)
#
# Notes:
#   - We re-encode for exact 1.000s cuts, independent of keyframes.
#   - Output files are saved next to the input by default, or choose an output folder.
#   - File names: <basename>_random1s.mp4, _first1s.mp4, _middle1s.mp4, _last1s.mp4
#
import os
import sys
import subprocess
import shlex
import random
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

APP_NAME = "Skindrops Splitter"
VERSION = "1.0"

def which(cmd):
    from shutil import which as _which
    return _which(cmd)

def has_ffmpeg():
    return which("ffmpeg") is not None and which("ffprobe") is not None

def probe_duration(infile):
    try:
        p = subprocess.run(
            ["ffprobe","-v","error","-show_entries","format=duration","-of","json", infile],
            capture_output=True, text=True, check=False
        )
        if p.returncode != 0:
            return None
        data = json.loads(p.stdout or "{}")
        d = float(data.get("format",{}).get("duration",0.0))
        if d <= 0: return None
        return d
    except Exception:
        return None

def build_cmd(infile, outfile, start, dur=1.0):
    # Use re-encode for accuracy
    cmd = [
        "ffmpeg","-y",
        "-ss", f"{start:.3f}",
        "-i", infile,
        "-t", f"{dur:.3f}",
        "-c:v","libx264","-preset","veryfast","-crf","20",
        "-c:a","aac","-b:a","128k",
        outfile
    ]
    return " ".join(shlex.quote(x) for x in cmd)

def run_cmd(cmd):
    try:
        print(">>>", cmd)
        rc = subprocess.call(cmd, shell=True)
        return rc == 0
    except Exception:
        return False

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("640x360")
        self.resizable(False, False)
        self.infile = tk.StringVar()
        self.outdir = tk.StringVar(value="")
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

    def ensure_in(self):
        if not has_ffmpeg():
            messagebox.showerror(APP_NAME, "ffmpeg/ffprobe not found. Install FFmpeg and retry.\n(Place ffmpeg.exe & ffprobe.exe next to this app or add to PATH)")
            return None, None, None
        infile = self.infile.get().strip()
        if not infile or not os.path.isfile(infile):
            messagebox.showerror(APP_NAME, "Please choose a valid input video.")
            return None, None, None
        outdir = self.outdir.get().strip()
        if not outdir:
            outdir = str(Path(infile).parent)
        Path(outdir).mkdir(parents=True, exist_ok=True)
        dur = probe_duration(infile)
        if not dur or dur <= 1.0:
            messagebox.showerror(APP_NAME, "Could not read duration or video shorter than 1s.")
            return None, None, None
        return infile, outdir, dur

    def base_out(self, outdir, tag):
        base = Path(self.infile.get()).stem
        return str(Path(outdir) / f"{base}_{tag}.mp4")

    def cut_at(self, start, tag):
        infile, outdir, dur = self.ensure_in()
        if not infile: return
        start = max(0.0, min(start, max(0.0, dur-1.0)))
        outfile = self.base_out(outdir, tag)
        cmd = build_cmd(infile, outfile, start=start, dur=1.0)
        self.status.set(f"Working: {tag} ...")
        self.update_idletasks()
        ok = run_cmd(cmd)
        if ok:
            self.status.set(f"Done: {outfile}")
        else:
            self.status.set("Error. See console window for details.")
            messagebox.showerror(APP_NAME, "FFmpeg failed.")

    def do_random(self):
        infile, outdir, dur = self.ensure_in()
        if not infile: return
        start = 0.0 if dur<=1.0 else random.uniform(0.0, max(0.0, dur-1.0))
        self.cut_at(start, "random1s")

    def do_first(self):
        self.cut_at(0.0, "first1s")

    def do_middle(self):
        infile, outdir, dur = self.ensure_in()
        if not infile: return
        mid = max(0.0, (dur/2.0) - 0.5)
        self.cut_at(mid, "middle1s")

    def do_last(self):
        infile, outdir, dur = self.ensure_in()
        if not infile: return
        last = max(0.0, dur - 1.0)
        self.cut_at(last, "last1s")

    def do_all(self):
        infile, outdir, dur = self.ensure_in()
        if not infile: return
        # Sequence: first, middle, last, random
        self.cut_at(0.0, "first1s")
        mid = max(0.0, (dur/2.0) - 0.5)
        self.cut_at(mid, "middle1s")
        last = max(0.0, dur - 1.0)
        self.cut_at(last, "last1s")
        rand = 0.0 if dur<=1.0 else random.uniform(0.0, max(0.0, dur-1.0))
        self.cut_at(rand, "random1s")

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
