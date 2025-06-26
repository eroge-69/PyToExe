#!/usr/bin/env python3
"""
PNG ➜ WebP Converter GUI  (v3 – sleek style, fix)
-------------------------------------------------
• ttkbootstrap Flatly/Darkly theme
• Drag-and-drop (opsional), bulk browse, auto-output ‘output/’
"""

import os, sys, importlib, subprocess, pathlib, traceback
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import scrolledtext

# ── helper: auto-install pip package ────────────────────────────────────────────
def _ensure(pkg: str, import_name: str | None = None):
    try:
        return importlib.import_module(import_name or pkg)
    except ModuleNotFoundError:
        print(f"[INFO] Installing {pkg} …")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])
        return importlib.import_module(import_name or pkg)

# ── deps ────────────────────────────────────────────────────────────────────────
PIL = _ensure("Pillow", "PIL")
from PIL import Image

tb = _ensure("ttkbootstrap")
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.scrolled import ScrolledText   # <─ widget scroll bawaan

try:
    _ensure("tkinterdnd2")
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_OK = True
except Exception:
    DND_OK = False

# ── const ───────────────────────────────────────────────────────────────────────
BASE_DIR    = pathlib.Path(__file__).resolve().parent
DEFAULT_OUT = BASE_DIR / "output"
DEFAULT_OUT.mkdir(exist_ok=True)

LIGHT_THEME = "flatly"
DARK_THEME  = "darkly"

# ── main app ────────────────────────────────────────────────────────────────────
class App:
    def __init__(self):
        self.dark = False

        if DND_OK:
            self.root = TkinterDnD.Tk()
            self.style = tb.Style()               # manual style obj
            self.style.theme_use(LIGHT_THEME)
        else:
            self.root = tb.Window(themename=LIGHT_THEME)
            self.style = self.root.style

        self.root.title("PNG ➜ WebP Converter")
        self.root.geometry("560x340")
        self.root.resizable(False, False)

        # state
        self.files: list[str] = []
        self.out_dir = tb.StringVar(value=str(DEFAULT_OUT))

        self._build_widgets()

        if DND_OK:
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind("<<Drop>>", self._on_drop)

    # ---------------------------------------------------------------------------
    def _build_widgets(self):
        pad = {"padx": 10, "pady": 6}

        main = tb.Frame(self.root, bootstyle=SECONDARY, relief="flat")
        main.place(relx=0.5, rely=0.5, anchor="c", relwidth=0.96, relheight=0.92)

        # ScrolledText frame
        list_frame = tb.Frame(main)
        list_frame.pack(fill="both", expand=True, **pad)

        self.lst = scrolledtext.ScrolledText(list_frame, height=7, wrap="none")
        self.lst.pack(fill="both", expand=True)

        # Insert drag-and-drop hint
        self.lst.configure(state="normal")
        self.lst.insert("1.0", "\n🚀 You can also drag and drop PNG files here!\n\n")
        self.lst.configure(state="disabled")

        # row buttons
        row = tb.Frame(main)
        row.pack(fill="x", **pad)

        tb.Button(row, text="Add Single", bootstyle=PRIMARY,
                command=self.add_single).pack(side="left", padx=4)
        tb.Button(row, text="Add Bulk", bootstyle=PRIMARY,
                command=self.add_bulk).pack(side="left", padx=4)
        tb.Button(row, text="Clear", bootstyle=SECONDARY,
                command=self.clear_list).pack(side="left", padx=4)
        tb.Button(row, text="Output…", bootstyle=SECONDARY,
                command=self.choose_out).pack(side="left", padx=4)
        tb.Button(row, text="🌓 Mode", bootstyle=INFO,
                command=self.toggle_theme).pack(side="right")

        # output label & progress
        tb.Label(main, textvariable=self.out_dir, anchor="w",
                bootstyle="secondary").pack(fill="x", padx=12)

        self.bar = tb.Progressbar(main, maximum=100, bootstyle=SUCCESS)
        self.bar.pack(fill="x", padx=12, pady=(4, 10))

        tb.Button(main, text="Convert ➜ WebP", bootstyle=SUCCESS,
                command=self.convert, width=25).pack(pady=(0, 8))

    # ========== file helpers ====================================================
    def add_single(self):
        p = filedialog.askopenfilename(
            title="Select a PNG", filetypes=[("PNG Images", "*.png")]
        )
        if p: self._add_file(p)

    def add_bulk(self):
        for p in filedialog.askopenfilename(
            title="Select PNG files", filetypes=[("PNG Images", "*.png")]
        ):
            self._add_file(p)

    def _on_drop(self, event):
        for raw in self.splitlist(event.data):
            p = raw.strip("{}")
            if p.lower().endswith(".png"):
                self._add_file(p)

    def clear_list(self):
        self.files.clear()
        self.lst.configure(state="normal")
        self.lst.delete("1.0", "end")
        self.lst.insert("1.0", "\n🚀 You can also drag and drop PNG files here!\n\n")
        self.lst.configure(state="disabled")

    def clear_list(self):
        self.files.clear()
        self.lst.delete("1.0", "end")

    def choose_out(self):
        d = filedialog.askdirectory(title="Select output folder")
        if d: self.out_dir.set(d)

    # ========== convert =========================================================
    def convert(self):
        if not self.files:
            Messagebox.show_warning("No files added."); return
        total = len(self.files)
        self.bar.configure(value=0, maximum=total)
        ok, fail = 0, []

        for idx, src in enumerate(self.files, 1):
            try:
                with Image.open(src) as im:
                    dst = pathlib.Path(self.out_dir.get()) / (pathlib.Path(src).stem + ".webp")
                    im.save(dst, "WEBP", quality=90, method=6)
                    ok += 1
            except Exception:
                traceback.print_exc()
                fail.append(pathlib.Path(src).name)
            self.bar.configure(value=idx)
            self.root.update_idletasks()

        msg = f"Converted {ok}/{total}"
        if fail: msg += f"\nFailed: {', '.join(fail)}"
        Messagebox.ok(msg, title="Done", alert=True)

    # ========== theme toggle ====================================================
    def toggle_theme(self):
        self.dark = not self.dark
        self.style.theme_use(DARK_THEME if self.dark else LIGHT_THEME)

    # ========== utils ===========================================================
    @staticmethod
    def splitlist(s: str):
        return s.strip().split() if "{" not in s else \
               [part.strip("{}") for part in s.split("} {")]

# ── run ─────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = App()
    app.root.mainloop()
