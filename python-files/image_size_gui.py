import os
import io
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageTk
import pandas as pd
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from typing import Dict

# ------------------ Image helpers ------------------

def to_px(value: float, unit: str, dpi: int = 300) -> int:
    """Convert mm/cm to pixels at given DPI."""
    unit = unit.lower().strip()
    if unit == "mm":
        inches = value / 25.4
    elif unit == "cm":
        inches = value / 2.54
    else:
        raise ValueError("Unit must be 'mm' or 'cm'.")
    return max(1, int(round(inches * dpi)))

def add_border(img: Image.Image, thickness: int = 2, color: str = "black") -> Image.Image:
    """Add a solid border around the image."""
    return ImageOps.expand(img, border=thickness, fill=color)

def add_bottom_text(img: Image.Image, text: str) -> Image.Image:
    """Add bottom-centered black text on yellow background. Auto font size."""
    if not text:
        return img

    draw = ImageDraw.Draw(img)
    # Auto font size: ~ 1/18 of width, min 18px
    font_size = max(18, img.width // 18)
    # Try common fonts; fallback to default
    font = None
    for candidate in (
        "arial.ttf",
        "DejaVuSans.ttf",                  # common on Linux
        "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS
        "C:/Windows/Fonts/arial.ttf",      # Windows absolute
    ):
        try:
            font = ImageFont.truetype(candidate, font_size)
            break
        except Exception:
            continue
    if font is None:
        font = ImageFont.load_default()

    # Measure text via textbbox (Pillow 10+)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (img.width - text_w) // 2
    y = img.height - text_h - max(10, img.height // 50)  # bottom margin

    pad_x = max(10, img.width // 100)
    pad_y = max(6, img.height // 150)

    # Yellow background rectangle
    draw.rectangle([x - pad_x, y - pad_y, x + text_w + pad_x, y + text_h + pad_y], fill="yellow")
    # Black text
    draw.text((x, y), text, fill="black", font=font)
    return img

def compress_to_max_kb(img: Image.Image, max_kb: float) -> bytes:
    """
    Return JPEG bytes at or under max_kb by sweeping quality down.
    Uses subsampling=0 and optimize=True for quality.
    """
    if max_kb is None or max_kb <= 0:
        # No cap: save high quality
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95, subsampling=0, optimize=True)
        return buf.getvalue()

    q = 95
    while True:
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=q, subsampling=0, optimize=True)
        kb = buf.tell() / 1024
        if kb <= max_kb or q <= 10:
            return buf.getvalue()
        q -= 5

# ------------------ App ------------------

class BulkImageApp(tb.Window):
    def __init__(self):
        super().__init__(themename="cosmo")  # try: cosmo, minty, flatly, darkly, etc.
        self.title("Bulk Image Editor")
        self.geometry("980x640")
        self.minsize(920, 580)

        # State vars
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.unit = tk.StringVar(value="mm")
        self.width_val = tk.StringVar()
        self.height_val = tk.StringVar()
        self.max_kb = tk.StringVar()  # optional; empty = no cap

        self.text_mode = tk.StringVar(value="none")  # none | fixed | file
        self.fixed_text = tk.StringVar()
        self.mapping_path = tk.StringVar()

        self._stop_flag = threading.Event()
        self._worker = None

        self._build_ui()

    # ---------- UI Layout ----------
    def _build_ui(self):
        # Top title bar
        title = tb.Label(self, text="Bulk Image Editor", font=("Segoe UI", 18, "bold"))
        title.pack(side=TOP, anchor="w", padx=16, pady=(14, 8))

        # Main split: controls left, preview right
        main = tb.Panedwindow(self, orient=HORIZONTAL)
        main.pack(fill=BOTH, expand=YES, padx=14, pady=10)

        # Left panel (controls)
        left = tb.Frame(main)
        main.add(left, weight=3)

        # Right panel (preview)
        right = tb.Frame(main)
        main.add(right, weight=5)

        # ----- Controls: Folders -----
        folders = tb.Labelframe(left, text="Folders", padding=12)
        folders.pack(fill=X, pady=(0, 10))

        tb.Label(folders, text="Input folder").grid(row=0, column=0, sticky="w")
        tb.Entry(folders, textvariable=self.input_dir, width=48).grid(row=0, column=1, padx=6, pady=4, sticky="we")
        tb.Button(folders, text="Browse", bootstyle=PRIMARY, command=self._choose_input).grid(row=0, column=2, padx=4)

        tb.Label(folders, text="Output folder").grid(row=1, column=0, sticky="w")
        tb.Entry(folders, textvariable=self.output_dir, width=48).grid(row=1, column=1, padx=6, pady=4, sticky="we")
        tb.Button(folders, text="Browse", bootstyle=PRIMARY, command=self._choose_output).grid(row=1, column=2, padx=4)

        folders.grid_columnconfigure(1, weight=1)

        # ----- Controls: Dimensions & Size -----
        dims = tb.Labelframe(left, text="Dimensions & File Size", padding=12)
        dims.pack(fill=X, pady=(0, 10))

        tb.Label(dims, text="Unit").grid(row=0, column=0, sticky="w")
        tb.Combobox(dims, values=["mm", "cm"], textvariable=self.unit, state="readonly", width=6)\
            .grid(row=0, column=1, sticky="w", padx=(6, 10))

        tb.Label(dims, text="Width").grid(row=0, column=2, sticky="e")
        tb.Entry(dims, textvariable=self.width_val, width=10).grid(row=0, column=3, padx=6)

        tb.Label(dims, text="Height").grid(row=0, column=4, sticky="e")
        tb.Entry(dims, textvariable=self.height_val, width=10).grid(row=0, column=5, padx=6)

        tb.Label(dims, text="Max file size (KB)  ").grid(row=1, column=0, sticky="w", pady=(8,0))
        tb.Entry(dims, textvariable=self.max_kb, width=10).grid(row=1, column=1, sticky="w", padx=(6, 10), pady=(8,0))
        tb.Label(dims, text="(leave empty for no cap)").grid(row=1, column=2, columnspan=4, sticky="w", pady=(8,0))

        # ----- Controls: Text Options -----
        textgrp = tb.Labelframe(left, text="Text on Image", padding=12)
        textgrp.pack(fill=X, pady=(0, 10))

        tb.Radiobutton(textgrp, text="None", value="none", variable=self.text_mode).grid(row=0, column=0, sticky="w")
        tb.Radiobutton(textgrp, text="Fixed", value="fixed", variable=self.text_mode).grid(row=0, column=1, sticky="w")
        tb.Radiobutton(textgrp, text="From File (CSV/Excel)", value="file", variable=self.text_mode).grid(row=0, column=2, sticky="w")

        tb.Label(textgrp, text="Fixed text").grid(row=1, column=0, sticky="e", pady=6)
        tb.Entry(textgrp, textvariable=self.fixed_text, width=38).grid(row=1, column=1, columnspan=2, sticky="we", padx=6)

        tb.Label(textgrp, text="Mapping file").grid(row=2, column=0, sticky="e")
        tb.Entry(textgrp, textvariable=self.mapping_path, width=38).grid(row=2, column=1, sticky="we", padx=6)
        tb.Button(textgrp, text="Browse", bootstyle=SECONDARY, command=self._choose_mapping).grid(row=2, column=2, padx=4)

        textgrp.grid_columnconfigure(1, weight=1)

        # ----- Controls: Actions -----
        actions = tb.Frame(left)
        actions.pack(fill=X, pady=(2, 4))

        self.start_btn = tb.Button(actions, text="Start Processing", bootstyle=SUCCESS, command=self._start)
        self.start_btn.pack(side=LEFT, padx=(0,6))
        self.stop_btn = tb.Button(actions, text="Stop", bootstyle=DANGER, command=self._stop, state=DISABLED)
        self.stop_btn.pack(side=LEFT)

        # ----- Preview & Progress -----
        preview_frame = tb.Labelframe(right, text="Live Preview", padding=8)
        preview_frame.pack(fill=BOTH, expand=YES)

        self.preview_canvas = tk.Canvas(preview_frame, bg=self.style.colors.get("light"), highlightthickness=0)
        self.preview_canvas.pack(fill=BOTH, expand=YES)

        progress_frame = tb.Frame(right)
        progress_frame.pack(fill=X, pady=(8,0))

        self.progress = tb.Progressbar(progress_frame, mode="determinate", bootstyle=STRIPED)
        self.progress.pack(fill=X, padx=4, pady=(4, 2))

        self.status_label = tb.Label(progress_frame, text="Idle", anchor="w")
        self.status_label.pack(fill=X, padx=6, pady=(0,6))

    # ---------- Browsers ----------
    def _choose_input(self):
        d = filedialog.askdirectory(title="Select input folder")
        if d:
            self.input_dir.set(d)

    def _choose_output(self):
        d = filedialog.askdirectory(title="Select output folder")
        if d:
            self.output_dir.set(d)

    def _choose_mapping(self):
        f = filedialog.askopenfilename(
            title="Select CSV/Excel mapping file",
            filetypes=[("CSV/Excel", "*.csv *.xls *.xlsx")]
        )
        if f:
            self.mapping_path.set(f)

    # ---------- Start/Stop ----------
    def _start(self):
        # Validate inputs
        if not os.path.isdir(self.input_dir.get()):
            messagebox.showerror("Error", "Please choose a valid input folder.")
            return
        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please choose a valid output folder.")
            return
        try:
            unit = self.unit.get().strip().lower()
            w = float(self.width_val.get())
            h = float(self.height_val.get())
            if unit not in ("mm", "cm"):
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Width/Height must be numbers and unit must be mm/cm.")
            return
        # Max KB optional
        try:
            max_kb = float(self.max_kb.get()) if self.max_kb.get().strip() else None
            if max_kb is not None and max_kb <= 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Max file size (KB) must be a positive number or left empty.")
            return

        # Load mapping if needed
        mapping: Dict[str, str] = {}
        if self.text_mode.get() == "file":
            if not self.mapping_path.get().strip():
                messagebox.showerror("Error", "Please choose a CSV/Excel mapping file.")
                return
            try:
                if self.mapping_path.get().lower().endswith(".csv"):
                    df = pd.read_csv(self.mapping_path.get())
                else:
                    df = pd.read_excel(self.mapping_path.get())
                mapping = dict(zip(
                    df.iloc[:,0].astype(str).str.strip().str.lower(),
                    df.iloc[:,1].astype(str)
                ))
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read mapping file:\n{e}")
                return

        # Prepare worker
        self._stop_flag.clear()
        self.start_btn.configure(state=DISABLED)
        self.stop_btn.configure(state=NORMAL)
        self.progress.configure(value=0)
        self.status_label.configure(text="Starting...")

        args = dict(
            input_dir=self.input_dir.get(),
            output_dir=self.output_dir.get(),
            unit=self.unit.get(),
            width=float(self.width_val.get()),
            height=float(self.height_val.get()),
            max_kb=max_kb,
            text_mode=self.text_mode.get(),
            fixed_text=self.fixed_text.get(),
            mapping=mapping
        )
        self._worker = threading.Thread(target=self._process_all, kwargs=args, daemon=True)
        self._worker.start()

    def _stop(self):
        self._stop_flag.set()
        self.status_label.configure(text="Stopping...")

    # ---------- Worker ----------
    def _process_all(self, input_dir, output_dir, unit, width, height, max_kb, text_mode, fixed_text, mapping):
        # Gather images
        files = [f for f in os.listdir(input_dir) if f.lower().endswith((".jpg",".jpeg",".png",".bmp",".tif",".tiff"))]
        total = len(files)
        if total == 0:
            self._ui_after(lambda: messagebox.showinfo("Info", "No images found in input folder."))
            self._ui_after(lambda: self._reset_controls())
            return

        # Target pixels
        target_w = to_px(width, unit)
        target_h = to_px(height, unit)

        # Progress setup
        self._ui_after(lambda: self.progress.configure(maximum=total, value=0))

        for idx, fname in enumerate(files, start=1):
            if self._stop_flag.is_set():
                self._ui_after(lambda: self.status_label.configure(text="Stopped by user."))
                break

            in_path = os.path.join(input_dir, fname)
            try:
                img = Image.open(in_path).convert("RGB")
                # Resize
                img = img.resize((target_w, target_h), Image.LANCZOS)
                # Border
                img = add_border(img, thickness=2, color="black")
                # Text
                if text_mode == "fixed" and fixed_text.strip():
                    img = add_bottom_text(img, fixed_text.strip())
                elif text_mode == "file":
                    key = os.path.splitext(fname)[0].strip().lower()
                    if key in mapping:
                        img = add_bottom_text(img, mapping[key])

                # Compress & save
                jpeg_bytes = compress_to_max_kb(img, max_kb)
                out_name = os.path.splitext(fname)[0] + ".jpg"
                out_path = os.path.join(output_dir, out_name)
                with open(out_path, "wb") as f:
                    f.write(jpeg_bytes)

                # Update UI (preview & progress)
                def _update_ui():
                    self.status_label.configure(text=f"Processing: {fname}  ({idx}/{total})")
                    self.progress.configure(value=idx)
                    self._update_preview(img, label=f"{fname}  -  {int(idx/total*100)}%")
                self._ui_after(_update_ui)

            except Exception as e:
                self._ui_after(lambda: self.status_label.configure(text=f"Error: {fname} -> {e}"))

        # Wrap up
        self._ui_after(lambda: self.status_label.configure(text="✅ Done"))
        self._ui_after(lambda: self._reset_controls())

    # ---------- UI helpers ----------
    def _reset_controls(self):
        self.start_btn.configure(state=NORMAL)
        self.stop_btn.configure(state=DISABLED)

    def _ui_after(self, func):
        """Schedule UI update from worker thread."""
        self.after(0, func)

    def _update_preview(self, pil_image: Image.Image, label: str = ""):
        # Fit into canvas while preserving aspect
        cw = self.preview_canvas.winfo_width() or 640
        ch = self.preview_canvas.winfo_height() or 360
        img_copy = pil_image.copy()
        img_copy.thumbnail((cw-16, ch-32))
        tk_img = ImageTk.PhotoImage(img_copy)
        self.preview_canvas.delete("all")
        x = cw // 2
        y = ch // 2
        self.preview_canvas.create_image(x, y, image=tk_img)
        self.preview_canvas.image = tk_img  # keep reference
        if label:
            self.preview_canvas.create_text(12, 12, anchor="nw", text=label, fill="#111", font=("Segoe UI", 10, "bold"))

# ------------------ Main ------------------

if __name__ == "__main__":
    app = BulkImageApp()
    app.mainloop()
