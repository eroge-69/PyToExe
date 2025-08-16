# -*- coding: utf-8 -*-
import sys, subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

APP_TITLE = "InstaQris Launcher"

TOOLS = [
    ("Download TikTok", "DownloadTikTok.exe", "download_tiktok.py"),
    ("Audio → SRT",     "Audio2SRT.exe",     "audio2srt_gui.py"),
    ("Video Merger",    "VideoMerger.exe",   "video_merger_gui.py"),
    ("Video Overlay",   "VideoOverlay.exe",  "video_overlay_gui.py"),
]

def run_tool(exe_name: str, py_name: str):
    try:
        if getattr(sys, "frozen", False):
            # Saat sudah di-pack (.exe)
            current = Path(sys.executable).resolve()
            candidates = [
                current.with_name("tools").joinpath(exe_name),  # dist/tools/xxx.exe
                current.with_name(exe_name),                    # dist/xxx.exe (fallback)
            ]
            for p in candidates:
                if p.exists():
                    subprocess.Popen([str(p)], close_fds=False)
                    return
            messagebox.showerror("Tidak ditemukan",
                                 f"Tidak menemukan {exe_name} di folder:\n- tools\\\n- {current.parent}")
        else:
            # Saat masih .py (dev mode)
            here = Path(__file__).resolve().parent
            src = here / py_name
            if not src.exists():
                messagebox.showerror("Tidak ditemukan",
                                     f"File tidak ditemukan:\n{src}")
                return
            subprocess.Popen([sys.executable, str(src)], close_fds=False)
    except Exception as e:
        messagebox.showerror("Error", str(e))

def main():
    root = tk.Tk()
    root.title(APP_TITLE)
    root.geometry("360x260")
    frm = ttk.Frame(root, padding=14)
    frm.pack(fill="both", expand=True)

    ttk.Label(frm, text="Pilih tool yang ingin dijalankan:",
              font=("Segoe UI", 10, "bold")).pack(pady=(0,10))

    for text, exe, py in TOOLS:
        ttk.Button(frm, text=text, width=28,
                   command=lambda e=exe, p=py: run_tool(e, p)).pack(pady=6)

    ttk.Label(frm, text="Tips: setelah build, .exe ada di folder dist/ (launcher + tools/)",
              foreground="#666").pack(pady=(14,0))
    root.mainloop()

if __name__ == "__main__":
    main()
