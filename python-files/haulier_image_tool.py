#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Haulier Image Renamer & Resizer (with Preview & Custom Output Folder)

Änderungen:
- Kein optimize=True mehr (verhindert Temp-Datei-Probleme bei Pillow in gesperrten Ordnern)
- Schreibtest im Output-Ordner (klare Fehlermeldung, falls OneDrive/AV blockiert)
- Fallback: Speichern über System-Temp + Verschieben, wenn direktes Speichern fehlschlägt
- Status-Texte korrigiert („processed“ statt „proccssed“)
"""

import sys
import threading
import queue
from datetime import datetime, timedelta
from pathlib import Path
import re
import shutil
import tempfile

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:
    ZoneInfo = None

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Optional drag & drop
_HAS_DND = True
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    _HAS_DND = False

# Optional recycle bin deletion
try:
    from send2trash import send2trash
    _HAS_TRASH = True
except Exception:
    _HAS_TRASH = False

from PIL import Image, ImageOps, ImageTk

APP_TITLE = "Haulier Image Renamer & Resizer"
MAX_SIDE = 1600
PREVIEW_MAX = 480

HAULIERS = [
    "DLG Logistics",
    "DFDS Nijmegen",
    "DFDS Logistics",
    "Freight Line",
    "Wolter Koops",
    "HZ Logistics",
    "Van Vliet",
    "A2B-Online",
    "Windhorst",
    "Vorex",
    "AB Texel",
    "Smyril Line Cargo",
    "Brouwer Urk",
    "De Rijke",
    "Yormax",
    "KDS Logistics",
]

PERSONS = ["Alexander", "Jan", "Arien", "Joke", "Len", "Carl"]
INITIALS_MAP = {
    "Alexander": "AR",
    "Jan": "JE",
    "Arien": "AD",
    "Joke": "JD",
    "Len": "LH",
    "Carl": "CL",
}

DATE_OPTIONS = {
    "vandaag": 0,
    "gisteren": 1,
}

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".bmp"}


def natural_key(path_or_str):
    s = str(path_or_str)
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def get_script_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def dutch_today_yesterday(which: str) -> datetime:
    tz = None
    if ZoneInfo:
        try:
            tz = ZoneInfo("Europe/Amsterdam")
        except Exception:
            tz = None
    base = datetime.now(tz) if tz else datetime.now()
    if which == "gisteren":
        return base - timedelta(days=1)
    return base


def format_date_ddmmyyyy(dt: datetime) -> str:
    return dt.strftime("%d-%m-%Y")


def compute_new_size(w: int, h: int, max_side: int = MAX_SIDE):
    longest = max(w, h)
    if longest <= max_side:
        return w, h
    scale = max_side / float(longest)
    return int(round(w * scale)), int(round(h * scale))


def smart_open_image(path: Path) -> Image.Image:
    im = Image.open(path)
    try:
        im = ImageOps.exif_transpose(im)
    except Exception:
        pass
    return im


def ensure_writable_dir(dir_path: Path) -> None:
    dir_path.mkdir(parents=True, exist_ok=True)
    test_file = dir_path / "__write_test__.tmp"
    try:
        with open(test_file, "wb") as f:
            f.write(b".")
    except Exception as e:
        raise PermissionError(f"Kann im Output-Ordner nicht schreiben: {dir_path}\n{e}")
    finally:
        try:
            test_file.unlink(missing_ok=True)
        except Exception:
            pass


def save_image(im: Image.Image, out_path: Path):
    out_ext = out_path.suffix.lower()
    try:
        if out_ext in {".jpg", ".jpeg"}:
            im.convert("RGB").save(out_path, quality=92)
        elif out_ext == ".png":
            im.save(out_path)
        elif out_ext == ".webp":
            if im.mode in ("RGBA", "LA"):
                im.save(out_path, lossless=True)
            else:
                im.convert("RGB").save(out_path, quality=92)
        else:
            out_path = out_path.with_suffix(".jpg")
            im.convert("RGB").save(out_path, quality=92)
        return out_path
    except Exception:
        # Fallback: erst ins System-Temp schreiben, dann verschieben
        with tempfile.NamedTemporaryFile(suffix=out_ext or ".jpg", delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            if out_ext in {".jpg", ".jpeg"}:
                im.convert("RGB").save(tmp_path, quality=92)
            elif out_ext == ".png":
                im.save(tmp_path)
            elif out_ext == ".webp":
                if im.mode in ("RGBA", "LA"):
                    im.save(tmp_path, lossless=True)
                else:
                    im.convert("RGB").save(tmp_path, quality=92)
            else:
                tmp_path = tmp_path.with_suffix(".jpg")
                im.convert("RGB").save(tmp_path, quality=92)
            shutil.move(str(tmp_path), str(out_path))
            return out_path
        finally:
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:
                pass


def move_to_trash_or_delete(p: Path):
    try:
        if _HAS_TRASH:
            send2trash(str(p))
        else:
            p.unlink(missing_ok=True)
    except Exception:
        pass


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(APP_TITLE)
        self.script_dir = get_script_dir()

        self.files = []
        self.queue = queue.Queue()
        self._preview_photo = None
        # Standard: OneDrive\Fotos (kannst du jederzeit ändern)
        self.output_dir_var = tk.StringVar(value=r"C:\Users\Gebruiker\OneDrive\Fotos")


        outer = ttk.Frame(root, padding=12)
        outer.pack(fill=tk.BOTH, expand=True)
        outer.columnconfigure(0, weight=3)
        outer.columnconfigure(1, weight=2)
        outer.rowconfigure(3, weight=1)

        ttk.Label(outer, text="Person:").grid(row=0, column=1, sticky="w")
        self.person = ttk.Combobox(outer, values=PERSONS, state="readonly")
        self.person.grid(row=0, column=1, sticky="ew", padx=(60, 0))
        self.person.current(0)

        ttk.Label(outer, text="Trailer Nummer:").grid(row=0, column=0, sticky="w")
        self.trailer_var = tk.StringVar()
        self.trailer = ttk.Entry(outer, textvariable=self.trailer_var)
        self.trailer.grid(row=0, column=0, sticky="ew", padx=(110, 6))
        self._attach_context_menu(self.trailer)

        ttk.Label(outer, text="Datum:").grid(row=1, column=0, sticky="w")
        self.date_choice = tk.StringVar(value="vandaag")
        date_frame = ttk.Frame(outer)
        date_frame.grid(row=1, column=0, sticky="w", padx=(60, 0))
        ttk.Radiobutton(date_frame, text="vandaag", variable=self.date_choice, value="vandaag").pack(side=tk.LEFT)
        ttk.Radiobutton(date_frame, text="gisteren", variable=self.date_choice, value="gisteren").pack(side=tk.LEFT, padx=(8, 0))

        outf = ttk.Frame(outer)
        outf.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        outf.columnconfigure(1, weight=1)
        ttk.Label(outf, text="Output Ordner:").grid(row=0, column=0, sticky="w")
        self.output_entry = ttk.Entry(outf, textvariable=self.output_dir_var)
        self.output_entry.grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(outf, text="Change…", command=self.choose_output_dir).grid(row=0, column=2)
        self._attach_context_menu(self.output_entry)

        ttk.Label(outer, text="Images:").grid(row=3, column=0, sticky="nw", pady=(6, 0))
        self.files_var = tk.StringVar(value=self.files)
        self.listbox = tk.Listbox(outer, listvariable=self.files_var, height=16, selectmode=tk.EXTENDED)
        self.listbox.grid(row=4, column=0, sticky="nsew", pady=6)
        self.listbox.bind("<<ListboxSelect>>", self.show_preview)
        self.listbox.bind("<Double-Button-1>", self.open_full_preview)

        if _HAS_DND and isinstance(root, TkinterDnD.Tk):
            self.listbox.drop_target_register(DND_FILES)
            self.listbox.dnd_bind('<<Drop>>', self.on_drop)
        else:
            ttk.Label(outer, text="(Drag & Drop benötigt 'tkinterdnd2' – sonst Dateidialog nutzen)", foreground="#777").grid(row=5, column=0, sticky="w")

        preview_frame = ttk.LabelFrame(outer, text="Preview")
        preview_frame.grid(row=3, column=1, rowspan=2, sticky="nsew", padx=(12, 0), pady=(6, 0))
        outer.rowconfigure(4, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        preview_frame.columnconfigure(0, weight=1)
        self.preview_canvas = tk.Canvas(preview_frame, width=PREVIEW_MAX, height=PREVIEW_MAX, highlightthickness=0)
        self.preview_canvas.grid(row=0, column=0, sticky="nsew")

        btns = ttk.Frame(outer)
        btns.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        ttk.Button(btns, text="Add Images", command=self.add_files).pack(side=tk.LEFT)
        ttk.Button(btns, text="Remove selection", command=self.remove_selected).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Empty list", command=self.clear_files).pack(side=tk.LEFT)
        ttk.Button(btns, text="Preview…", command=self.open_full_preview).pack(side=tk.LEFT, padx=12)

        self.delete_originals = tk.BooleanVar(value=False)
        ttk.Checkbutton(btns, text="Delete originals", variable=self.delete_originals).pack(side=tk.RIGHT)

        self.progress = ttk.Progressbar(outer, mode="determinate")
        self.progress.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(10, 6))
        self.status = ttk.Label(outer)
        self.status.grid(row=8, column=0, columnspan=2, sticky="w")

        self.process_btn = ttk.Button(outer, text="Start", command=self.start_processing)
        self.process_btn.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        self.root.after(100, self._poll_queue)

    # === UI helpers ===
    def choose_output_dir(self):
        path = filedialog.askdirectory(title="Choose output folder", mustexist=True)
        if path:
            self.output_dir_var.set(path)

    def on_drop(self, event):
        paths = self._split_dnd_paths(event.data)
        self._add_paths(paths)

    @staticmethod
    def _split_dnd_paths(data: str):
        items, token, in_brace = [], "", False
        for ch in data:
            if ch == '{':
                in_brace, token = True, ""
            elif ch == '}':
                in_brace = False
                items.append(token)
                token = ""
            elif ch == ' ' and not in_brace:
                if token:
                    items.append(token)
                    token = ""
            else:
                token += ch
        if token:
            items.append(token)
        return items

    def _attach_context_menu(self, widget: tk.Widget):
        menu = tk.Menu(widget, tearoff=0)
        menu.add_command(label="Cut", command=lambda: widget.event_generate("<<Cut>>"))
        menu.add_command(label="Copy", command=lambda: widget.event_generate("<<Copy>>"))
        menu.add_command(label="Insert", command=lambda: widget.event_generate("<<Paste>>"))
        menu.add_separator()

        def select_all():
            try:
                widget.select_range(0, 'end')
                widget.icursor('end')
            except Exception:
                pass
        menu.add_command(label="Select all", command=select_all)

        def show_menu(event):
            try:
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

        widget.bind("<Button-3>", show_menu)           # Windows/Linux
        widget.bind("<Control-Button-1>", show_menu)   # macOS Ctrl-Klick

    def add_files(self):
        paths = filedialog.askopenfilenames(title="Select images", filetypes=[
            ("Images", ".jpg .jpeg .png .webp .tif .tiff .bmp"),
            ("All Files", "*.*")
        ])
        self._add_paths(paths)

    def _add_paths(self, paths):
        new = []
        for p in paths:
            if Path(p).suffix.lower() in SUPPORTED_EXTS:
                new.append(str(p))
        if not new:
            return
        self.files.extend(new)
        self.files = sorted(set(self.files), key=natural_key)
        self.files_var.set(self.files)
        self.status.config(text=f"{len(self.files)} files in the list.")
        self.show_preview()

    def remove_selected(self):
        sel = list(self.listbox.curselection())
        sel.reverse()
        for idx in sel:
            try:
                del self.files[idx]
            except Exception:
                pass
        self.files_var.set(self.files)
        self.status.config(text=f"{len(self.files)} files in the list.")
        self.preview_canvas.delete("all")
        self._preview_photo = None

    def clear_files(self):
        self.files = []
        self.files_var.set(self.files)
        self.status.config(text="list cleared.")
        self.preview_canvas.delete("all")
        self._preview_photo = None

    def show_preview(self, event=None):
        idxs = self.listbox.curselection()
        if not idxs and self.files:
            path = self.files[0]
        elif idxs:
            path = self.files[idxs[0]]
        else:
            self.preview_canvas.delete("all")
            self._preview_photo = None
            return
        try:
            p = Path(path)
            with smart_open_image(p) as im:
                im.thumbnail((PREVIEW_MAX, PREVIEW_MAX), Image.LANCZOS)
                self._preview_photo = ImageTk.PhotoImage(im)
                self.preview_canvas.delete("all")
                x = (self.preview_canvas.winfo_width() or PREVIEW_MAX) // 2
                y = (self.preview_canvas.winfo_height() or PREVIEW_MAX) // 2
                self.preview_canvas.create_image(x, y, image=self._preview_photo, anchor="center")
        except Exception as e:
            self.status.config(text=f"Preview Error: {e}")

    def open_full_preview(self, event=None):
        idxs = self.listbox.curselection()
        if not idxs:
            return
        path = self.files[idxs[0]]
        p = Path(path)
        try:
            with smart_open_image(p) as im:
                top = tk.Toplevel(self.root)
                top.title(f"Preview - {p.name}")
                max_w, max_h = 1200, 900
                w, h = im.size
                scale = min(max_w / w, max_h / h, 1.0)
                if scale < 1.0:
                    im = im.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
                photo = ImageTk.PhotoImage(im)
                lbl = ttk.Label(top, image=photo)
                lbl.image = photo
                lbl.pack()
        except Exception as e:
            messagebox.showerror(APP_TITLE, f"Preview failed: {e}")

    # === processing ===
    def start_processing(self):
        if not self.files:
            messagebox.showwarning(APP_TITLE, "Please add images.")
            return
        person = self.person.get().strip()
        trailer = self.trailer_var.get().strip()
        date_key = self.date_choice.get()

        if not (person and trailer):
            messagebox.showwarning(APP_TITLE, "Please fill in person and trailer number")
            return

        self.files = sorted(self.files, key=natural_key)

        initials = INITIALS_MAP.get(person, (person[:2] or "XX").upper())
        dt = dutch_today_yesterday(date_key)
        date_str = format_date_ddmmyyyy(dt)

        out_dir = Path(self.output_dir_var.get().strip() or str(self.script_dir))
        try:
            ensure_writable_dir(out_dir)
        except Exception as e:
            messagebox.showerror(
                APP_TITLE,
                "Der Output-Ordner ist nicht beschreibbar.\n\n"
                f"{e}\n\n"
                "Tipp: Wähle einen Ordner außerhalb von OneDrive/„Geschützte Ordner“, "
                "z. B. C:\\Users\\…\\Pictures\\HaulierOutput, oder erlaube der EXE Zugriff "
                "in F-Secure/Windows Defender."
            )
            return

        self.progress.configure(value=0, maximum=len(self.files))
        self.process_btn.configure(state=tk.DISABLED)
        self.status.config(text="Process…")

        t = threading.Thread(
            target=self._process_worker,
            args=(trailer, initials, date_str, self.delete_originals.get(), out_dir),
            daemon=True
        )
        t.start()

    def _process_worker(self, trailer, initials, date_str, delete_originals, out_dir: Path):
        processed = 0
        errors = 0

        for idx, src in enumerate(list(self.files)):
            src_path = Path(src)
            try:
                with smart_open_image(src_path) as im:
                    new_w, new_h = compute_new_size(*im.size, MAX_SIDE)
                    if (new_w, new_h) != im.size:
                        im = im.resize((new_w, new_h), Image.LANCZOS)

                    ext = src_path.suffix.lower()
                    if ext not in {".jpg", ".jpeg", ".png", ".webp"}:
                        ext = ".jpg"

                    seq = f"{idx:03d}"
                    # Neues Namensschema: <Trailer>_<Datum>_<XXX>_<Initialen>.<ext>
                    base_name = f"{trailer}_{date_str}_{seq}_{initials}"
                    out_path = out_dir / f"{base_name}{ext}"

                    dup = 1
                    while out_path.exists():
                        out_path = out_dir / f"{base_name}_{dup}{ext}"
                        dup += 1

                    save_image(im, out_path)

                if delete_originals:
                    move_to_trash_or_delete(src_path)

                processed += 1
                self.queue.put(("progress", processed))
            except Exception as e:
                errors += 1
                self.queue.put(("error", f"Fehler bei {src_path.name}: {e}"))

        self.queue.put(("done", processed, errors, str(out_dir)))

    def _poll_queue(self):
        try:
            while True:
                msg = self.queue.get_nowait()
                if not msg:
                    break
                kind = msg[0]
                if kind == "progress":
                    processed = msg[1]
                    self.progress.configure(value=processed)
                    self.status.config(text=f"{processed}/{len(self.files)} processed…")
                elif kind == "error":
                    err = msg[1]
                    self.status.config(text=err)
                elif kind == "done":
                    processed, errors, out_dir = msg[1], msg[2], msg[3]
                    self.process_btn.configure(state=tk.NORMAL)
                    self.status.config(text=f"Done: {processed} processed, {errors} error(s). Saved in: {out_dir}")
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self._poll_queue)


def main():
    if _HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()

    try:
        from tkinter import font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(size=10)
    except Exception:
        pass

    style = ttk.Style(root)
    try:
        if sys.platform == "win32":
            style.theme_use("vista")
        else:
            style.theme_use(style.theme_use())
    except Exception:
        pass

    App(root)
    # Etwas kleinere Start-/Mindestgröße
    root.geometry("840x580")
    root.minsize(760, 520)
    root.mainloop()


if __name__ == "__main__":
    main()
