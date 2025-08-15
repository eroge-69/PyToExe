#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Image Compressor & Resizer (No External Dependencies)
- GUI: Tkinter (stdlib)
- Imaging: Windows GDI+ via ctypes (JPEG/PNG/BMP/GIF/TIFF)
- Batch target size (KB) with binary search (JPEG), dimension limits,
  optional format conversion, progress bar, log.
Note: GDI+ does not support WebP. PNG has no "quality" knob; for PNG
targets, this tool can downscale or convert to JPEG.
"""
import os
import sys
import math
import ctypes
import threading
import tempfile
from ctypes import wintypes
from tkinter import ttk, filedialog, messagebox
import tkinter as tk

APP_NAME = "Image Compressor (No-Deps)"
SUPPORTED_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tif', '.tiff'}

# --------- GDI+ ctypes setup ----------
gdiplus = ctypes.windll.gdiplus
kernel32 = ctypes.windll.kernel32
ole32 = ctypes.windll.ole32

class GdiplusStartupInput(ctypes.Structure):
    _fields_ = [('GdiplusVersion', ctypes.c_uint32),
                ('DebugEventCallback', ctypes.c_void_p),
                ('SuppressBackgroundThread', ctypes.c_bool),
                ('SuppressExternalCodecs', ctypes.c_bool)]

class EncoderParameter(ctypes.Structure):
    _fields_ = [('Guid', ctypes.c_byte * 16),
                ('NumberOfValues', ctypes.c_uint),
                ('Type', ctypes.c_uint),
                ('Value', ctypes.c_void_p)]

class EncoderParameters(ctypes.Structure):
    _fields_ = [('Count', ctypes.c_uint),
                ('Parameter', EncoderParameter * 1)]

class ImageCodecInfo(ctypes.Structure):
    _fields_ = [
        ('Clsid', ctypes.c_byte * 16),
        ('FormatID', ctypes.c_byte * 16),
        ('CodecName', ctypes.c_wchar_p),
        ('DllName', ctypes.c_wchar_p),
        ('FormatDescription', ctypes.c_wchar_p),
        ('FilenameExtension', ctypes.c_wchar_p),
        ('MimeType', ctypes.c_wchar_p),
        ('Flags', ctypes.c_uint32),
        ('Version', ctypes.c_uint32),
        ('SigCount', ctypes.c_uint32),
        ('SigSize', ctypes.c_uint32),
        ('SigPattern', ctypes.c_void_p),
        ('SigMask', ctypes.c_void_p),
    ]

# GUID helpers
import uuid
def _guid_bytes(u):
    # GDI+ expects GUID as 16 bytes in little-endian structure order.
    g = uuid.UUID(str(u))
    # Rebuild to match Windows GUID binary layout
    data = g.bytes_le
    arr = (ctypes.c_byte * 16)()
    for i,b in enumerate(data):
        arr[i] = b
    return arr

# Known encoder parameter GUIDs
EncoderQuality = _guid_bytes("1d5be4b5-fa4a-452d-9cdd-5db35105e7eb")  # Quality (long)
EncoderCompression = _guid_bytes("e09d739d-ccd4-44ee-8eba-3fbf8be4fc58")
# Data types
EncoderParameterValueTypeLong = 4

# Start/Stop GDI+
_token = ctypes.c_ulonglong()

def gdip_start():
    input = GdiplusStartupInput(1, None, False, False)
    gdiplus.GdiplusStartup(ctypes.byref(_token), ctypes.byref(input), None)

def gdip_shutdown():
    if _token.value:
        gdiplus.GdiplusShutdown(_token)

# Basic GDI+ wrappers
class GpImage(ctypes.Structure):
    pass

class GpBitmap(GpImage):
    pass

gdiplus.GdipLoadImageFromFile.argtypes = [wintypes.LPCWSTR, ctypes.POINTER(ctypes.POINTER(GpImage))]
gdiplus.GdipLoadImageFromFile.restype = ctypes.c_int

gdiplus.GdipDisposeImage.argtypes = [ctypes.POINTER(GpImage)]
gdiplus.GdipDisposeImage.restype = ctypes.c_int

gdiplus.GdipGetImageWidth.argtypes = [ctypes.POINTER(GpImage), ctypes.POINTER(ctypes.c_uint)]
gdiplus.GdipGetImageWidth.restype = ctypes.c_int
gdiplus.GdipGetImageHeight.argtypes = [ctypes.POINTER(GpImage), ctypes.POINTER(ctypes.c_uint)]
gdiplus.GdipGetImageHeight.restype = ctypes.c_int

gdiplus.GdipCreateBitmapFromScan0.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.POINTER(GpBitmap))]
gdiplus.GdipCreateBitmapFromScan0.restype = ctypes.c_int

gdiplus.GdipGetImageEncodersSize.argtypes = [ctypes.POINTER(ctypes.c_uint), ctypes.POINTER(ctypes.c_uint)]
gdiplus.GdipGetImageEncodersSize.restype = ctypes.c_int
gdiplus.GdipGetImageEncoders.argtypes = [ctypes.c_uint, ctypes.c_uint, ctypes.c_void_p]
gdiplus.GdipGetImageEncoders.restype = ctypes.c_int

gdiplus.GdipSaveImageToFile.argtypes = [ctypes.POINTER(GpImage), wintypes.LPCWSTR, ctypes.POINTER(ctypes.c_byte), ctypes.c_void_p]
gdiplus.GdipSaveImageToFile.restype = ctypes.c_int

# Draw to resize
class GpGraphics(ctypes.Structure):
    pass
gdiplus.GdipGetImageGraphicsContext.argtypes = [ctypes.POINTER(GpImage), ctypes.POINTER(ctypes.POINTER(GpGraphics))]
gdiplus.GdipGetImageGraphicsContext.restype = ctypes.c_int
gdiplus.GdipDeleteGraphics.argtypes = [ctypes.POINTER(GpGraphics)]
gdiplus.GdipDeleteGraphics.restype = ctypes.c_int
gdiplus.GdipDrawImageRectRectI.argtypes = [ctypes.POINTER(GpGraphics), ctypes.POINTER(GpImage),
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                            ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
gdiplus.GdipDrawImageRectRectI.restype = ctypes.c_int
gdiplus.GdipSetInterpolationMode = gdiplus.GdipSetInterpolationMode
gdiplus.GdipSetInterpolationMode.argtypes = [ctypes.POINTER(GpGraphics), ctypes.c_int]
InterpolationModeHighQualityBicubic = 7

PixelFormat32bppARGB = 0x26200A

def load_image(path):
    img = ctypes.POINTER(GpImage)()
    status = gdiplus.GdipLoadImageFromFile(path, ctypes.byref(img))
    if status != 0:
        raise OSError(f"GDI+ load failed ({status}) for {path}")
    return img

def get_size(img):
    w = ctypes.c_uint()
    h = ctypes.c_uint()
    gdiplus.GdipGetImageWidth(img, ctypes.byref(w))
    gdiplus.GdipGetImageHeight(img, ctypes.byref(h))
    return int(w.value), int(h.value)

def create_bitmap(w, h):
    bmp = ctypes.POINTER(GpBitmap)()
    status = gdiplus.GdipCreateBitmapFromScan0(w, h, 0, PixelFormat32bppARGB, None, ctypes.byref(bmp))
    if status != 0:
        raise OSError("CreateBitmap failed")
    return ctypes.cast(bmp, ctypes.POINTER(GpImage))

def resize_image(img, max_w, max_h):
    if max_w <= 0 and max_h <= 0:
        return img  # no resize
    w, h = get_size(img)
    new_w, new_h = w, h
    if max_w > 0 and new_w > max_w:
        s = max_w / new_w
        new_w = int(new_w * s); new_h = int(h * s)
    if max_h > 0 and new_h > max_h:
        s = max_h / new_h
        new_w = int(new_w * s); new_h = int(new_h * s)
    if new_w <= 0 or new_h <= 0 or (new_w == w and new_h == h):
        return img
    dst = create_bitmap(new_w, new_h)
    g = ctypes.POINTER(GpGraphics)()
    gdiplus.GdipGetImageGraphicsContext(dst, ctypes.byref(g))
    gdiplus.GdipSetInterpolationMode(g, InterpolationModeHighQualityBicubic)
    gdiplus.GdipDrawImageRectRectI(g, img, 0, 0, new_w, new_h, 0, 0, w, h, 2, None, None, None)
    gdiplus.GdipDeleteGraphics(g)
    # dispose original
    gdiplus.GdipDisposeImage(img)
    return dst

def list_encoders():
    num = ctypes.c_uint()
    size = ctypes.c_uint()
    gdiplus.GdipGetImageEncodersSize(ctypes.byref(num), ctypes.byref(size))
    buf = (ctypes.c_byte * size.value)()
    gdiplus.GdipGetImageEncoders(num.value, size.value, ctypes.byref(buf))
    # Cast to ImageCodecInfo array
    array_type = ImageCodecInfo * num.value
    infos = ctypes.cast(ctypes.byref(buf), ctypes.POINTER(array_type)).contents
    return infos

_ENCODERS = None
def get_encoder_clsid(mime):
    global _ENCODERS
    if _ENCODERS is None:
        _ENCODERS = list_encoders()
    for info in _ENCODERS:
        if info.MimeType == mime:
            return info.Clsid
    return None

def save_image(img, path, mime="image/jpeg", quality=None):
    clsid = get_encoder_clsid(mime)
    if not clsid:
        raise OSError(f"Encoder not found for {mime}")
    params = None
    if quality is not None and mime in ("image/jpeg", "image/jpg"):
        ep = EncoderParameters()
        ep.Count = 1
        ep.Parameter[0].Guid = EncoderQuality
        ep.Parameter[0].NumberOfValues = 1
        ep.Parameter[0].Type = EncoderParameterValueTypeLong
        q = ctypes.c_ulong(int(quality))
        ep.Parameter[0].Value = ctypes.cast(ctypes.byref(q), ctypes.c_void_p)
        params = ctypes.byref(ep)
    status = gdiplus.GdipSaveImageToFile(img, path, ctypes.byref(clsid), params)
    if status != 0:
        raise OSError(f"Save failed ({status}) to {path}")

def guess_mime_from_ext(ext):
    ext = ext.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".bmp": "image/bmp",
        ".gif": "image/gif",
        ".tif": "image/tiff",
        ".tiff": "image/tiff",
    }.get(ext, "image/jpeg")

def ext_for_mime(mime):
    return {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/bmp": ".bmp",
        "image/gif": ".gif",
        "image/tiff": ".tif",
    }.get(mime, ".jpg")

# --------- Compression logic ----------
def save_with_target(img, out_path, mime, target_kb, under_mode, tmpdir, allow_convert_png_to_jpeg=True):
    """
    For JPEG: binary search quality to meet target.
    For PNG: no quality knob; we just save once. If target given and allow_convert_png_to_jpeg,
             convert to JPEG and try quality search.
    """
    target_bytes = int(target_kb * 1024)
    if mime == "image/jpeg":
        lo, hi = 10, 95
        best_bytes = None
        best_q = None
        for _ in range(12):
            mid = (lo + hi) // 2
            tmp = os.path.join(tmpdir, "tmp.jpg")
            save_image(img, tmp, "image/jpeg", quality=mid)
            sz = os.path.getsize(tmp)
            if under_mode:
                if sz <= target_bytes:
                    best_bytes = sz; best_q = mid; lo = mid + 1
                else:
                    hi = mid - 1
            else:
                if sz < target_bytes:
                    best_bytes = sz; best_q = mid; lo = mid + 1
                else:
                    hi = mid - 1
        q = best_q if best_q is not None else max(10, min(hi, 95))
        save_image(img, out_path, "image/jpeg", quality=q)
        return True
    elif mime == "image/png":
        # Save once as PNG
        save_image(img, out_path, "image/png", quality=None)
        if target_kb is None:
            return True
        if os.path.getsize(out_path) <= target_bytes:
            return True
        if allow_convert_png_to_jpeg:
            # Convert to JPEG to meet tight targets
            jpeg_out = os.path.splitext(out_path)[0] + ".jpg"
            return save_with_target(img, jpeg_out, "image/jpeg", target_kb, under_mode, tmpdir, True)
        return True
    else:
        # Other formats: just save
        save_image(img, out_path, mime, quality=None)
        return True

# --------- GUI ----------
def human_size(n):
    for unit in ["B","KB","MB","GB"]:
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit=="B" else f"{n/1024:.1f} {unit}"
        n /= 1024

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1000x640")
        self.files = []  # list of (path, size)
        self.output_dir = None
        self.stop_flag = False
        self.create_ui()
        gdip_start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        try:
            gdip_shutdown()
        finally:
            self.destroy()

    def create_ui(self):
        frm_top = ttk.Frame(self); frm_top.pack(fill="x", padx=10, pady=8)
        ttk.Button(frm_top, text="Add Files", command=self.add_files).pack(side="left")
        ttk.Button(frm_top, text="Add Folder", command=self.add_folder).pack(side="left", padx=(6,0))
        ttk.Button(frm_top, text="Clear", command=self.clear_files).pack(side="left", padx=(6,0))
        ttk.Button(frm_top, text="Choose Output", command=self.choose_output).pack(side="left", padx=(6,0))
        self.lbl_out = ttk.Label(frm_top, text="Output: (same as source)"); self.lbl_out.pack(side="left", padx=10)

        # Options
        frm_opt = ttk.LabelFrame(self, text="Options"); frm_opt.pack(fill="x", padx=10, pady=6)

        ttk.Label(frm_opt, text="Preset target:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.preset = ttk.Combobox(frm_opt, values=["None","50 KB","100 KB","Under 100 KB","Under 500 KB","Under 1 MB"], state="readonly")
        self.preset.current(0)
        self.preset.grid(row=0, column=1, sticky="w", padx=6)

        ttk.Label(frm_opt, text="Custom target (KB):").grid(row=0, column=2, sticky="w", padx=6)
        self.var_target = tk.DoubleVar(value=0.0)
        self.ent_target = ttk.Entry(frm_opt, textvariable=self.var_target, width=10)
        self.ent_target.grid(row=0, column=3, sticky="w", padx=6)

        self.under_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_opt, text="Keep file ≤ target (Under mode)", variable=self.under_mode).grid(row=0, column=4, sticky="w", padx=6)

        ttk.Label(frm_opt, text="Max width:").grid(row=1, column=0, sticky="w", padx=6)
        self.var_w = tk.IntVar(value=0); ttk.Entry(frm_opt, textvariable=self.var_w, width=8).grid(row=1, column=1, sticky="w", padx=6)
        ttk.Label(frm_opt, text="Max height:").grid(row=1, column=2, sticky="w", padx=6)
        self.var_h = tk.IntVar(value=0); ttk.Entry(frm_opt, textvariable=self.var_h, width=8).grid(row=1, column=3, sticky="w", padx=6)

        ttk.Label(frm_opt, text="Output format:").grid(row=2, column=0, sticky="w", padx=6)
        self.out_fmt = ttk.Combobox(frm_opt, values=["ORIGINAL","JPEG","PNG","BMP","GIF","TIFF"], state="readonly"); self.out_fmt.current(0)
        self.out_fmt.grid(row=2, column=1, sticky="w", padx=6)

        self.allow_png_to_jpeg = tk.BooleanVar(value=True)
        ttk.Checkbutton(frm_opt, text="Allow PNG→JPEG to hit target", variable=self.allow_png_to_jpeg).grid(row=2, column=2, sticky="w", padx=6)

        ttk.Label(frm_opt, text="Rename pattern:").grid(row=3, column=0, sticky="w", padx=6)
        self.var_pattern = tk.StringVar(value="{name}_compressed")
        ttk.Entry(frm_opt, textvariable=self.var_pattern, width=24).grid(row=3, column=1, sticky="w", padx=6)

        self.overwrite = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm_opt, text="Overwrite if exists", variable=self.overwrite).grid(row=3, column=2, sticky="w", padx=6)

        # Table
        frm_tbl = ttk.Frame(self); frm_tbl.pack(fill="both", expand=True, padx=10, pady=6)
        self.tree = ttk.Treeview(frm_tbl, columns=("size","status"), show="headings", height=12)
        self.tree.heading("size", text="Original Size")
        self.tree.heading("status", text="Status")
        self.tree.column("size", width=120, anchor="center")
        self.tree.column("status", width=400, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.heading("#0", text="File")
        self.tree["show"] = ("#0","size","status")

        sb = ttk.Scrollbar(frm_tbl, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Bottom
        frm_bot = ttk.Frame(self); frm_bot.pack(fill="x", padx=10, pady=6)
        self.progress = ttk.Progressbar(frm_bot, length=500, mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True)
        self.btn_start = ttk.Button(frm_bot, text="Start", command=self.start)
        self.btn_start.pack(side="left", padx=8)
        self.btn_stop = ttk.Button(frm_bot, text="Stop", command=self.stop, state="disabled")
        self.btn_stop.pack(side="left")

        # Log
        frm_log = ttk.LabelFrame(self, text="Log"); frm_log.pack(fill="both", expand=False, padx=10, pady=6)
        self.txt_log = tk.Text(frm_log, height=8)
        self.txt_log.pack(fill="both", expand=True)

    def log(self, s):
        self.txt_log.insert("end", s + "\n")
        self.txt_log.see("end")
        self.update_idletasks()

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select images",
            filetypes=[("Images","*.jpg *.jpeg *.png *.bmp *.gif *.tif *.tiff")])
        self._add_paths(paths)

    def add_folder(self):
        folder = filedialog.askdirectory(title="Select folder")
        if not folder: return
        paths = []
        for root, _, files in os.walk(folder):
            for fn in files:
                if os.path.splitext(fn)[1].lower() in SUPPORTED_EXT:
                    paths.append(os.path.join(root, fn))
        self._add_paths(paths)

    def _add_paths(self, paths):
        added = 0
        for p in paths:
            if not os.path.isfile(p): continue
            ext = os.path.splitext(p)[1].lower()
            if ext not in SUPPORTED_EXT: continue
            try:
                sz = os.path.getsize(p)
            except Exception:
                sz = 0
            self.files.append((p, sz))
            self.tree.insert("", "end", iid=p, text=os.path.basename(p),
                             values=(human_size(sz), "Queued"))
            added += 1
        if added:
            self.progress["value"] = 0

    def clear_files(self):
        self.files.clear()
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.progress["value"] = 0
        self.txt_log.delete("1.0","end")

    def choose_output(self):
        d = filedialog.askdirectory(title="Choose output folder")
        if d:
            self.output_dir = d
            self.lbl_out.config(text=f"Output: {d}")

    def stop(self):
        self.stop_flag = True

    def start(self):
        if not self.files:
            messagebox.showwarning("No files", "Add some images first.")
            return
        # preset mapping
        preset = self.preset.get()
        preset_map = {"50 KB":50, "100 KB":100, "Under 100 KB":100, "Under 500 KB":500, "Under 1 MB":1024}
        target_kb = None
        if preset in preset_map:
            target_kb = preset_map[preset]
        custom = float(self.var_target.get() or 0)
        if custom > 0:
            target_kb = custom
        max_w = int(self.var_w.get() or 0)
        max_h = int(self.var_h.get() or 0)
        fmt = self.out_fmt.get()
        under_mode = self.under_mode.get()
        pattern = self.var_pattern.get().strip() or "{name}_compressed"
        overwrite = self.overwrite.get()
        allow_png_to_jpeg = self.allow_png_to_jpeg.get()

        opts = dict(target_kb=target_kb, max_w=max_w, max_h=max_h, fmt=fmt,
                    under_mode=under_mode, pattern=pattern, overwrite=overwrite,
                    allow_png_to_jpeg=allow_png_to_jpeg)
        self.stop_flag = False
        self.btn_start.config(state="disabled")
        self.btn_stop.config(state="normal")
        t = threading.Thread(target=self.worker, args=(opts,))
        t.daemon = True
        t.start()

    def worker(self, opts):
        total = len(self.files)
        done = 0
        with tempfile.TemporaryDirectory() as tmpdir:
            for path, _ in self.files:
                if self.stop_flag:
                    break
                try:
                    self.tree.set(path, "status", "Processing...")
                    # Load
                    img = load_image(path)
                    try:
                        # Resize
                        img = resize_image(img, opts["max_w"], opts["max_h"])
                        # Out dir and format
                        base = os.path.splitext(os.path.basename(path))[0]
                        out_dir = self.output_dir or os.path.dirname(path)
                        os.makedirs(out_dir, exist_ok=True)
                        out_fmt = opts["fmt"]
                        if out_fmt == "ORIGINAL":
                            mime = guess_mime_from_ext(os.path.splitext(path)[1])
                        else:
                            mime = guess_mime_from_ext("." + out_fmt.lower())
                        out_ext = ext_for_mime(mime)
                        out_name = opts["pattern"].format(name=base) + out_ext
                        out_path = os.path.join(out_dir, out_name)

                        if (not opts["overwrite"]) and os.path.exists(out_path):
                            k = 1
                            while os.path.exists(out_path):
                                out_path = os.path.join(out_dir, f"{os.path.splitext(out_name)[0]}_{k}{out_ext}")
                                k += 1

                        # Save with target if any
                        if opts["target_kb"]:
                            save_with_target(img, out_path, mime, opts["target_kb"], opts["under_mode"], tmpdir, allow_convert_png_to_jpeg=opts["allow_png_to_jpeg"])
                        else:
                            # Default save
                            q = 85 if mime == "image/jpeg" else None
                            save_image(img, out_path, mime, q)
                        self.tree.set(path, "status", f"OK → {os.path.basename(out_path)}")
                        self.log(f"Saved: {out_path}")
                    finally:
                        gdiplus.GdipDisposeImage(img)
                except Exception as e:
                    self.tree.set(path, "status", "Error")
                    self.log(f"[ERROR] {path}: {e}")
                done += 1
                pct = int((done/total)*100)
                self.progress["value"] = pct
        self.btn_start.config(state="normal")
        self.btn_stop.config(state="disabled")
        messagebox.showinfo("Done", "All tasks finished.")

def main():
    if os.name != "nt":
        tk.messagebox.showerror("Windows Only", "This no-dependency build uses Windows GDI+. Run on Windows.")
        return
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
