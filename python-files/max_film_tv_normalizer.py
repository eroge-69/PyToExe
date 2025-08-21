#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MAX FiLM e TV File Normalizer e Archiver
Versione: 1.7

Vedi changelog nel messaggio.
"""

import os
import sys
import json
import re
import shutil
import subprocess
import threading
import queue
import time
from pathlib import Path

import tkinter as tk
from tkinter import (
    Tk, StringVar, BooleanVar, END, E, W
)
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk

# ---- Opzionali
try:
    from send2trash import send2trash
    HAVE_SEND2TRASH = True
except Exception:
    HAVE_SEND2TRASH = False

try:
    import zipfile
except Exception:
    zipfile = None

try:
    import py7zr
    HAVE_PY7ZR = True
except Exception:
    HAVE_PY7ZR = False

try:
    import rarfile
    HAVE_RARFILE = True
except Exception:
    HAVE_RARFILE = False

# MediaInfo opzionale (libreria Python)
try:
    from pymediainfo import MediaInfo
    HAVE_PYMEDIAINFO = True
except Exception:
    HAVE_PYMEDIAINFO = False


APP_NAME = "MAX FiLM e TV File Normalizer e Archiver"
CONFIG_PATH = Path.home() / ".max_film_tv_normalizer_config.json"

DEFAULT_VIDEO_EXTS = [
    "mkv","mp4","m4v","mov","avi","wmv","flv","webm","mpg","mpeg","m2v",
    "ts","m2ts","mts","vob","ogv","3gp","3g2","asf","dv","f4v","mxf",
    "iso","img","bin","nrg",
    "rm","rmvb","divx","xvid","y4m","h264","h265","hevc","av1"
]

ARCHIVE_EXTS = [
    "zip","rar","r00","r01","r02","001","7z","tar","gz","bz2","xz","z01","z02",
    "rev","part1.rar","part01.rar"
]

CHECK_OFF = "\u2610"  # ☐
CHECK_ON  = "\u2611"  # ☑
MAX_RECENTS = 10

# --- Helper Windows: nascondere console nelle subprocess ---
CREATE_NO_WINDOW = 0x08000000 if os.name == "nt" else 0
STARTUPINFO = None
if os.name == "nt":
    STARTUPINFO = subprocess.STARTUPINFO()
    STARTUPINFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW


# ---------------------- Config ----------------------

def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        except Exception:
            cfg = {}
    else:
        cfg = {}

    cfg.setdefault("version", "1.7")
    cfg.setdefault("video_extensions", DEFAULT_VIDEO_EXTS[:])
    cfg.setdefault("passwords", [])
    cfg.setdefault("seven_zip_path", None)
    cfg.setdefault("rar_path", None)
    cfg.setdefault("unrar_path", None)
    cfg.setdefault("bsdtar_path", None)
    cfg.setdefault("mediainfo_path", None)  # opzionale CLI
    cfg.setdefault("recent_dirs", [])

    # autodetect 7z
    if not cfg.get("seven_zip_path"):
        seven_zip_path = None
        win_7z = Path(r"C:\Program Files\7-Zip\7z.exe")
        if win_7z.exists():
            seven_zip_path = str(win_7z)
        else:
            for exe in ("7z","7zz","7za"):
                p = shutil.which(exe)
                if p:
                    seven_zip_path = p
                    break
        cfg["seven_zip_path"] = seven_zip_path

    # autodetect rar
    if not cfg.get("rar_path"):
        rar_path = None
        win_rar = Path(r"C:\Program Files\WinRAR\Rar.exe")
        if win_rar.exists():
            rar_path = str(win_rar)
        else:
            p = shutil.which("rar")
            if p:
                rar_path = p
        cfg["rar_path"] = rar_path

    # autodetect unrar
    if not cfg.get("unrar_path"):
        unrar_path = None
        win_unrar = Path(r"C:\Program Files\WinRAR\UnRAR.exe")
        if win_unrar.exists():
            unrar_path = str(win_unrar)
        else:
            for exe in ("unrar", "unrar.exe"):
                p = shutil.which(exe)
                if p:
                    unrar_path = p
                    break
        cfg["unrar_path"] = unrar_path

    # autodetect bsdtar
    if not cfg.get("bsdtar_path"):
        bsdtar_path = None
        for exe in ("bsdtar", "bsdtar.exe", "tar", "tar.exe"):
            p = shutil.which(exe)
            if p:
                bsdtar_path = p
                break
        cfg["bsdtar_path"] = bsdtar_path

    # autodetect mediainfo CLI
    if not cfg.get("mediainfo_path"):
        mi = shutil.which("mediainfo")
        cfg["mediainfo_path"] = mi

    return cfg


def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
    except Exception as e:
        messagebox.showerror("Errore salvataggio", f"Impossibile salvare config:\n{e}")


# ---------------------- Utility ----------------------

def human_size(n):
    try:
        n = float(n)
    except Exception:
        return str(n)
    for unit in ['B','KB','MB','GB','TB']:
        if n < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.0f} PB"


def sanitize_folder_name(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*]', "_", name)
    name = name.rstrip(" .")
    if not name:
        name = "untitled"
    return name


def is_supported_video(path: Path, cfg) -> bool:
    ext = path.suffix.lower().lstrip(".")
    return ext in set(x.lower() for x in cfg["video_extensions"])


def find_largest_supported_file(root: Path, cfg) -> Path | None:
    largest = None
    largest_size = -1
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            if is_supported_video(p, cfg):
                try:
                    sz = p.stat().st_size
                except Exception:
                    continue
                if sz > largest_size:
                    largest = p
                    largest_size = sz
    return largest


def find_archives_in_folder(root: Path) -> list[Path]:
    found = []
    lower_exts = set(ARCHIVE_EXTS)
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = Path(dirpath) / fn
            ext = p.suffix.lower().lstrip(".")
            if ext in lower_exts or re.search(r"\.part\d{1,3}\.rar$", p.name, re.I):
                found.append(p)
    return found


def guess_first_volume(file_path: Path) -> Path:
    name = file_path.name
    parent = file_path.parent

    m = re.match(r"^(.*)\.part(\d{1,3})\.rar$", name, re.I)
    if m:
        base = m.group(1)
        for cand in (f"{base}.part1.rar", f"{base}.part01.rar"):
            target = parent / cand
            if target.exists():
                return target

    m = re.match(r"^(.*)\.r(\d{2})$", name, re.I)
    if m:
        base = m.group(1)
        for cand in (f"{base}.r00", f"{base}.rar"):
            target = parent / cand
            if target.exists():
                return target

    if name.lower().endswith(".001"):
        return file_path

    m = re.match(r"^(.*)\.z(\d{2})$", name, re.I)
    if m:
        base = m.group(1)
        for cand in (f"{base}.z01", f"{base}.zip"):
            target = parent / cand
            if target.exists():
                return target

    return file_path


def same_filesystem(p1: Path, p2: Path) -> bool:
    try:
        if os.name == "nt":
            return p1.drive.lower() == p2.drive.lower()
        return p1.stat().st_dev == p2.stat().st_dev
    except Exception:
        return False


def replace_spaces_with_dots(name: str) -> str:
    s = re.sub(r"\s+", ".", name.strip())
    s = re.sub(r"\.{2,}", ".", s)
    return s


def quality_from_height(h: int | None) -> str | None:
    if not h:
        return None
    if h >= 2160: return "4K"
    if h >= 1440: return "2K"
    if h >= 1080: return "FullHD"
    if h >= 720:  return "HD"
    return "SD"


# ---------------------- Dialogo avanzamento Move ----------------------

class MoveProgressDialog(tk.Toplevel):
    def __init__(self, parent, title="Spostamento in corso…"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.cancel_event = threading.Event()

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        self.lbl_src = ttk.Label(frm, text="Origine: -", width=90)
        self.lbl_src.grid(row=0, column=0, columnspan=2, sticky="w")

        self.lbl_dst = ttk.Label(frm, text="Destinazione: -", width=90)
        self.lbl_dst.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0,6))

        self.pbar = ttk.Progressbar(frm, mode="determinate", length=520, maximum=100)
        self.pbar.grid(row=2, column=0, columnspan=2, sticky="ew")

        self.lbl_info = ttk.Label(frm, text="0%  •  0.0 MB/s  •  ETA —")
        self.lbl_info.grid(row=3, column=0, sticky="w", pady=(6,0))

        self.btn_cancel = ttk.Button(frm, text="Annulla", command=self._on_cancel)
        self.btn_cancel.grid(row=3, column=1, sticky="e", pady=(6,0))

        self.update_idletasks()
        self.grab_set()  # modal

    def set_paths(self, src: Path, dst: Path):
        self.lbl_src.config(text=f"Origine: {src}")
        self.lbl_dst.config(text=f"Destinazione: {dst}")

    def update_progress(self, pct: int, speed_bps: float, remaining_s: float | None):
        self.pbar.configure(value=max(0, min(100, pct)))
        if speed_bps is None:
            info = f"{pct}%"
        else:
            mbps = speed_bps / 1024 / 1024
            if remaining_s is None or remaining_s == float('inf'):
                info = f"{pct}%  •  {mbps:.1f} MB/s  •  ETA —"
            else:
                mins, secs = divmod(int(remaining_s), 60)
                info = f"{pct}%  •  {mbps:.1f} MB/s  •  ETA {mins:02d}:{secs:02d}"
        self.lbl_info.config(text=info)
        self.update_idletasks()

    def _on_cancel(self):
        self.cancel_event.set()

    def was_cancelled(self) -> bool:
        return self.cancel_event.is_set()


# ---------------------- App ----------------------

class App(Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        # finestra più ampia per vedere subito tutto
        self.geometry("1400x900")
        self.minsize(1280, 800)

        self.style = ttk.Style(self)  # tema di sistema

        self.cfg = load_config()
        self._apply_external_tools_to_rarfile()

        self.current_dir = StringVar(value="")
        self.items_checked = set()  # iid selezionati
        self.path_by_iid = {}       # iid -> Path
        self.iid_by_path = {}       # str(Path) -> iid

        self.log_q = queue.Queue()

        self._build_ui()
        self._load_source_into_tab()
        self.after(100, self._drain_log_q)

        # Avvio dall'ultima dir recente, se esiste
        last = (self.cfg.get("recent_dirs") or [None])[0]
        if last and Path(last).exists():
            self.current_dir.set(last)
            self.scan_dir_threaded()

    # ---------- UI ----------

    def _build_ui(self):
        # Top bar
        top_bar = ttk.Frame(self, padding=(12, 10))
        top_bar.pack(fill="x")

        title = ttk.Label(top_bar, text=APP_NAME, font=("Segoe UI", 14, "bold"))
        title.pack(side="left")

        dir_frame = ttk.Frame(top_bar)
        dir_frame.pack(side="right")

        # Recenti combo
        self.recent_var = StringVar()
        self.recent_combo = ttk.Combobox(dir_frame, textvariable=self.recent_var, state="readonly", width=45)
        rec = self.cfg.get("recent_dirs") or []
        self.recent_combo["values"] = rec
        if rec:
            self.recent_combo.current(0)
        ttk.Label(dir_frame, text="Recenti:").grid(row=0, column=0, sticky=E, padx=(0,6))
        self.recent_combo.grid(row=0, column=1, sticky=W)
        ttk.Button(dir_frame, text="Vai", command=self.choose_recent).grid(row=0, column=2, padx=(4,10))

        ttk.Label(dir_frame, text="Directory:").grid(row=0, column=3, sticky=E, padx=(0,6))
        self.dir_entry = ttk.Entry(dir_frame, width=50, textvariable=self.current_dir)
        self.dir_entry.grid(row=0, column=4, sticky=W)
        ttk.Button(dir_frame, text="Sfoglia…", command=self.choose_dir).grid(row=0, column=5, padx=6)
        ttk.Button(dir_frame, text="Scansiona", command=self.scan_dir_threaded).grid(row=0, column=6)

        # Notebook
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill="both", expand=True, padx=12, pady=(0,8))

        # Browser tab
        self.tab_browser = ttk.Frame(self.nb, padding=8)
        self.nb.add(self.tab_browser, text="Browser")
        self._build_browser_tab()

        # Opzioni
        self.tab_opts = ttk.Frame(self.nb, padding=8)
        self.nb.add(self.tab_opts, text="Opzioni")
        self._build_options_tab()

        # Log
        self.tab_log = ttk.Frame(self.nb, padding=8)
        self.nb.add(self.tab_log, text="Log")
        self._build_log_tab()

        # Sorgente
        self.tab_src = ttk.Frame(self.nb, padding=8)
        self.nb.add(self.tab_src, text="Sorgente")
        self._build_source_tab()

        # Status bar
        self.status_var = StringVar(value="Pronto.")
        status = ttk.Frame(self, padding=(12,6))
        status.pack(fill="x", side="bottom")
        self.progress = ttk.Progressbar(status, mode="determinate", length=240)
        self.progress.pack(side="right")
        ttk.Label(status, textvariable=self.status_var).pack(side="left")

    def choose_recent(self):
        val = self.recent_var.get().strip()
        if val and Path(val).exists():
            self.current_dir.set(val)
            self.scan_dir_threaded()

    def _build_browser_tab(self):
        hdr = ttk.Frame(self.tab_browser)
        hdr.pack(fill="x", pady=(0,6))
        self.chk_all_var = BooleanVar(value=False)
        ttk.Checkbutton(hdr, text="Seleziona tutto", variable=self.chk_all_var, command=self.toggle_select_all).pack(side="left")
        ttk.Button(hdr, text="Organizza", command=self.organize_selected_threaded).pack(side="left", padx=(10,0))
        ttk.Button(hdr, text="Reset", command=self.reset_view).pack(side="left", padx=6)

        # Treeview: aggiungo colonna "Media"
        cols = ("check","name","type","size","media","status","actions")
        self.tree = ttk.Treeview(self.tab_browser, columns=cols, show="tree headings", selectmode="browse")
        self.tree.heading("check", text="✔")
        self.tree.heading("name",  text="Nome")
        self.tree.heading("type",  text="Tipo")
        self.tree.heading("size",  text="Dimensione")
        self.tree.heading("media", text="Media")
        self.tree.heading("status",text="Stato")
        self.tree.heading("actions",text="Azioni")

        self.tree.column("#0", width=28)               # freccia
        self.tree.column("check",   width=36,  anchor="center")
        self.tree.column("name",    width=540, anchor="w")
        self.tree.column("type",    width=90,  anchor="w")
        self.tree.column("size",    width=110, anchor="e")
        self.tree.column("media",   width=320, anchor="w")
        self.tree.column("status",  width=120, anchor="center")
        self.tree.column("actions", width=120, anchor="center")

        self.tree.pack(fill="both", expand=True)

        # Interazioni
        self.tree.bind("<Button-1>", self._on_tree_click)        # click su checkbox/azioni
        self.tree.bind("<<TreeviewOpen>>", self._on_tree_open)
        self.tree.bind("<Button-3>", self._on_tree_right_click)  # menu contestuale

        # Menu Azioni (icône/emoji)
        self.actions_menu = tk.Menu(self, tearoff=0)
        self.actions_menu.add_command(label="📝  Rinomina", command=lambda: self._menu_action("rename"))
        self.actions_menu.add_command(label="🔤  Rimuovi spazi", command=lambda: self._menu_action("rmspaces"))
        self.actions_menu.add_command(label="📦  Sposta…", command=lambda: self._menu_action("move"))
        self.actions_menu.add_command(label="📂  Estrai (cancella archivi)", command=lambda: self._menu_action("extract"))
        self.actions_menu.add_separator()
        self.actions_menu.add_command(label="🗑️  Elimina", command=lambda: self._menu_action("delete"))

    def _build_options_tab(self):
        wrap = ttk.Frame(self.tab_opts)
        wrap.pack(fill="both", expand=True)

        # Versione
        lf_ver = ttk.Labelframe(wrap, text="Versione programma")
        lf_ver.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.version_var = StringVar(value=self.cfg.get("version","1.7"))
        ttk.Entry(lf_ver, textvariable=self.version_var, width=12).grid(row=0, column=0, padx=8, pady=8, sticky=W)

        # Estensioni supportate
        lf_ext = ttk.Labelframe(wrap, text="Estensioni video supportate (senza punto)")
        lf_ext.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        lf_ext.grid_rowconfigure(1, weight=1)
        lf_ext.grid_columnconfigure(0, weight=1)

        self.ext_list = ttk.Treeview(lf_ext, columns=("ext",), show="headings", height=8)
        self.ext_list.heading("ext", text="Estensione")
        self.ext_list.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)
        for e in self.cfg["video_extensions"]:
            self.ext_list.insert("", "end", values=(e,))
        self.new_ext_var = StringVar()
        ttk.Entry(lf_ext, textvariable=self.new_ext_var, width=16).grid(row=2, column=0, sticky=W, padx=8, pady=(0,8))
        ttk.Button(lf_ext, text="Aggiungi", command=self.add_ext).grid(row=2, column=1, sticky=W, pady=(0,8))
        ttk.Button(lf_ext, text="Rimuovi selezionate", command=self.remove_selected_exts).grid(row=2, column=2, sticky=W, pady=(0,8))

        # Password archivi
        lf_pwd = ttk.Labelframe(wrap, text="Password archivi (ordine di tentativo)")
        lf_pwd.grid(row=2, column=0, sticky="nsew", padx=8, pady=8)
        lf_pwd.grid_rowconfigure(1, weight=1)
        lf_pwd.grid_columnconfigure(0, weight=1)

        self.pwd_list = ttk.Treeview(lf_pwd, columns=("pwd",), show="headings", height=6)
        self.pwd_list.heading("pwd", text="Password")
        self.pwd_list.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=8, pady=8)
        for p in self.cfg["passwords"]:
            self.pwd_list.insert("", "end", values=(p,))
        self.new_pwd_var = StringVar()
        ttk.Entry(lf_pwd, textvariable=self.new_pwd_var, width=28).grid(row=2, column=0, sticky=W, padx=8, pady=(0,8))
        ttk.Button(lf_pwd, text="Aggiungi", command=self.add_pwd).grid(row=2, column=1, sticky=W, pady=(0,8))
        ttk.Button(lf_pwd, text="Rimuovi selezionate", command=self.remove_selected_pwds).grid(row=2, column=2, sticky=W, pady=(0,8))

        # Binari esterni
        lf_bin = ttk.Labelframe(wrap, text="Percorsi eseguibili (opzionali)")
        lf_bin.grid(row=0, column=1, rowspan=4, sticky="nsew", padx=8, pady=8)
        lf_bin.grid_columnconfigure(1, weight=1)

        self.seven_zip_var = StringVar(value=self.cfg.get("seven_zip_path") or "")
        self.rar_var      = StringVar(value=self.cfg.get("rar_path") or "")
        self.unrar_var    = StringVar(value=self.cfg.get("unrar_path") or "")
        self.bsdtar_var   = StringVar(value=self.cfg.get("bsdtar_path") or "")
        self.mediainfo_var= StringVar(value=self.cfg.get("mediainfo_path") or "")

        rowi = 0
        ttk.Label(lf_bin, text="7-Zip (7z/7zz/7za)").grid(row=rowi, column=0, sticky=E, padx=8, pady=6)
        ttk.Entry(lf_bin, textvariable=self.seven_zip_var).grid(row=rowi, column=1, sticky="ew", padx=(0,8))
        ttk.Button(lf_bin, text="Sfoglia…", command=self.browse_7z).grid(row=rowi, column=2, padx=4); rowi += 1

        ttk.Label(lf_bin, text="WinRAR (rar.exe)").grid(row=rowi, column=0, sticky=E, padx=8, pady=6)
        ttk.Entry(lf_bin, textvariable=self.rar_var).grid(row=rowi, column=1, sticky="ew", padx=(0,8))
        ttk.Button(lf_bin, text="Sfoglia…", command=self.browse_rar).grid(row=rowi, column=2, padx=4); rowi += 1

        ttk.Label(lf_bin, text="UnRAR (unrar.exe)").grid(row=rowi, column=0, sticky=E, padx=8, pady=6)
        ttk.Entry(lf_bin, textvariable=self.unrar_var).grid(row=rowi, column=1, sticky="ew", padx=(0,8))
        ttk.Button(lf_bin, text="Sfoglia…", command=self.browse_unrar).grid(row=rowi, column=2, padx=4); rowi += 1

        ttk.Label(lf_bin, text="bsdtar").grid(row=rowi, column=0, sticky=E, padx=8, pady=6)
        ttk.Entry(lf_bin, textvariable=self.bsdtar_var).grid(row=rowi, column=1, sticky="ew", padx=(0,8))
        ttk.Button(lf_bin, text="Sfoglia…", command=self.browse_bsdtar).grid(row=rowi, column=2, padx=4); rowi += 1

        ttk.Label(lf_bin, text="MediaInfo (CLI)").grid(row=rowi, column=0, sticky=E, padx=8, pady=6)
        ttk.Entry(lf_bin, textvariable=self.mediainfo_var).grid(row=rowi, column=1, sticky="ew", padx=(0,8))
        ttk.Button(lf_bin, text="Sfoglia…", command=self.browse_mediainfo).grid(row=rowi, column=2, padx=4); rowi += 1

        # Azioni opzioni
        btns = ttk.Frame(wrap)
        btns.grid(row=4, column=1, sticky="nsew", padx=8, pady=8)
        ttk.Button(btns, text="Salva opzioni", command=self.save_options).pack(side="left")

        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_columnconfigure(1, weight=1)

    def _build_log_tab(self):
        frm = ttk.Frame(self.tab_log)
        frm.pack(fill="both", expand=True)
        self.log_tree = ttk.Treeview(frm, columns=("msg",), show="headings")
        self.log_tree.heading("msg", text="Log")
        self.log_tree.pack(fill="both", expand=True)
        self._log("Benvenuto! Usa 'Sfoglia' per scegliere la directory, poi 'Scansiona'.")

    def _build_source_tab(self):
        wrap = ttk.Frame(self.tab_src)
        wrap.pack(fill="both", expand=True)
        self.src_text = tk.Text(wrap, wrap="none", height=30)
        ysb = ttk.Scrollbar(wrap, orient="vertical", command=self.src_text.yview)
        xsb = ttk.Scrollbar(wrap, orient="horizontal", command=self.src_text.xview)
        self.src_text.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
        self.src_text.pack(side="top", fill="both", expand=True)
        ysb.pack(side="right", fill="y")
        xsb.pack(side="bottom", fill="x")
        ttk.Button(wrap, text="Ricarica sorgente", command=self._load_source_into_tab).pack(side="left", pady=6)

    def _load_source_into_tab(self):
        try:
            src_file = Path(__file__).resolve()
            with open(src_file, "r", encoding="utf-8") as f:
                code = f.read()
        except Exception:
            code = "# Sorgente non disponibile (eseguire da file per vedere il codice qui)."
        self.src_text.delete("1.0", END)
        self.src_text.insert("1.0", code)

    # ---------- rarfile tools ----------

    def _apply_external_tools_to_rarfile(self):
        if not HAVE_RARFILE:
            return
        try:
            unrar_path = self.cfg.get("unrar_path")
            bsdtar_path = self.cfg.get("bsdtar_path")
            if unrar_path:
                rarfile.UNRAR_TOOL = unrar_path
            if bsdtar_path and hasattr(rarfile, "BSDTAR_TOOL"):
                rarfile.BSDTAR_TOOL = bsdtar_path
        except Exception:
            pass

    # ---------- Utility Thread/Log + UI-safe ----------

    def _log(self, msg: str):
        self.log_q.put(msg)

    def _drain_log_q(self):
        try:
            while True:
                msg = self.log_q.get_nowait()
                self.log_tree.insert("", "end", values=(msg,))
                self.log_tree.yview_moveto(1)
                self.status_var.set(msg)
        except queue.Empty:
            pass
        self.after(150, self._drain_log_q)

    def _set_progress(self, mode="determinate", value=0):
        def _apply():
            self.progress.configure(mode=mode, value=value)
        self.after(0, _apply)

    def _set_status(self, text: str):
        self.after(0, lambda: self.status_var.set(text))

    def _run_thread(self, target, *args):
        t = threading.Thread(target=target, args=args, daemon=True)
        t.start()

    # ---------- Dir & listing ----------

    def choose_dir(self):
        d = filedialog.askdirectory(title="Seleziona directory di lavoro")
        if d:
            self.current_dir.set(d)
            self.scan_dir_threaded()

    def scan_dir_threaded(self):
        self._run_thread(self._scan_dir)

    def _scan_dir(self):
        d = self.current_dir.get().strip()
        if not d or not Path(d).exists():
            self._log("Errore: seleziona una directory valida.")
            return

        self._update_recent_dirs(d)

        self._set_status("Scansione in corso…")
        self._set_progress("indeterminate")
        self.progress.start(15)

        try:
            base = Path(d)
            try:
                entries = sorted(base.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except Exception as e:
                self._log(f"Impossibile leggere la directory: {e}")
                return

            self.after(0, self._rebuild_root_tree, base, entries)
            self._log(f"Scansione completata: {len(entries)} elementi in '{base}'.")
        finally:
            self.progress.stop()
            self._set_progress("determinate", 0)
            self._set_status("Pronto.")

    def _update_recent_dirs(self, d: str):
        rec = self.cfg.get("recent_dirs") or []
        d = str(Path(d))
        if d in rec:
            rec.remove(d)
        rec.insert(0, d)
        if len(rec) > MAX_RECENTS:
            rec = rec[:MAX_RECENTS]
        self.cfg["recent_dirs"] = rec
        save_config(self.cfg)
        def _apply():
            self.recent_combo["values"] = rec
            if rec:
                self.recent_combo.current(0)
        self.after(0, _apply)

    def _rebuild_root_tree(self, base: Path, entries: list[Path]):
        self.tree.delete(*self.tree.get_children(""))
        self.items_checked.clear()
        self.path_by_iid.clear()
        self.iid_by_path.clear()

        for p in entries:
            iid = self._insert_path("", p)
            if p.is_dir():
                self.tree.insert(iid, "end", text="", values=("", "...", "", "", "", ""), tags=("placeholder",))

    def _insert_path(self, parent_iid, path: Path):
        kind = "Cartella" if path.is_dir() else "File"
        try:
            size_txt = human_size(path.stat().st_size) if path.is_file() else ""
        except Exception:
            size_txt = ""
        vals = (CHECK_OFF, path.name, kind, size_txt, "", "", "Azioni ▾")
        iid = self.tree.insert(parent_iid, "end", text="", values=vals)
        self.path_by_iid[iid] = path
        self.iid_by_path[str(path)] = iid

        # Se è file video: avvia probing media in background
        if path.is_file() and is_supported_video(path, self.cfg):
            self._run_thread(self._probe_media_and_update, iid, path)

        return iid

    def _on_tree_open(self, event):
        iid = self.tree.focus()
        if not iid:
            return
        path = self.path_by_iid.get(iid)
        if not path or not path.is_dir():
            return
        children = self.tree.get_children(iid)
        if any("placeholder" in (self.tree.item(c, "tags") or []) for c in children):
            for c in children:
                self.tree.delete(c)
            try:
                entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except Exception as e:
                self._log(f"Impossibile aprire '{path.name}': {e}")
                return
            for p in entries:
                child_iid = self._insert_path(iid, p)
                if p.is_dir():
                    self.tree.insert(child_iid, "end", text="", values=("", "...", "", "", "", ""), tags=("placeholder",))

    def _on_tree_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        col = self.tree.identify_column(event.x)
        if col == "#1":  # checkbox
            self._toggle_check(iid)
            return
        if col == "#7":  # Azioni ▾  (con colonna "media" aggiunta)
            x, y, w, h = self.tree.bbox(iid, col)
            self.tree.selection_set(iid)
            self._open_actions_menu(iid, x + w//2, y + h)

    def _on_tree_right_click(self, event):
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        self.tree.selection_set(iid)
        self._open_actions_menu(iid, event.x, event.y)

    def _open_actions_menu(self, iid, x, y):
        self._menu_iid = iid
        ox, oy = self.tree.winfo_rootx(), self.tree.winfo_rooty()
        self.actions_menu.tk_popup(ox + x, oy + y)

    def _menu_action(self, what):
        iid = getattr(self, "_menu_iid", None)
        if not iid:
            return
        if what == "rename":
            self._action_rename(iid)
        elif what == "rmspaces":
            self._action_remove_spaces(iid)
        elif what == "move":
            self._action_move(iid)
        elif what == "delete":
            self._action_delete(iid)
        elif what == "extract":
            self._action_extract_folder(iid)

    def _toggle_check(self, iid):
        vals = list(self.tree.item(iid, "values"))
        checked = vals[0] == CHECK_ON
        vals[0] = CHECK_OFF if checked else CHECK_ON
        self.tree.item(iid, values=vals)
        if checked:
            self.items_checked.discard(iid)
        else:
            self.items_checked.add(iid)

    def toggle_select_all(self):
        want = self.chk_all_var.get()
        for iid in self.tree.get_children(""):
            self._set_checked_recursive(iid, want)

    def _set_checked_recursive(self, iid, value: bool):
        vals = list(self.tree.item(iid, "values"))
        vals[0] = CHECK_ON if value else CHECK_OFF
        self.tree.item(iid, values=vals)
        if value:
            self.items_checked.add(iid)
        else:
            self.items_checked.discard(iid)
        for c in self.tree.get_children(iid):
            self._set_checked_recursive(c, value)

    # ---------- Azioni: Rinomina / Rimuovi Spazi / Elimina / Sposta / Estrai ----------

    def _action_rename(self, iid):
        path = self.path_by_iid.get(iid)
        if not path:
            return
        new_name = simpledialog.askstring("Rinomina", f"Nuovo nome per:\n{path.name}")
        if not new_name:
            return
        new_name = sanitize_folder_name(new_name)
        new_path = path.parent / new_name
        if new_path.exists():
            messagebox.showerror("Errore", f"Esiste già: {new_path.name}")
            return
        try:
            os.replace(path, new_path)
            self._update_tree_path(iid, path, new_path)
            self._log(f"Rinominato: {path.name} -> {new_path.name}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile rinominare:\n{e}")

    def _action_remove_spaces(self, iid):
        path = self.path_by_iid.get(iid)
        if not path:
            return
        if path.is_file():
            stem = replace_spaces_with_dots(path.stem)
            new_name = stem + path.suffix
        else:
            new_name = replace_spaces_with_dots(path.name)
        new_name = sanitize_folder_name(new_name)
        if new_name == path.name:
            self._log("Nessuna modifica (nessuno spazio da sostituire).")
            return
        new_path = path.parent / new_name
        if new_path.exists():
            messagebox.showerror("Errore", f"Esiste già: {new_path.name}")
            return
        try:
            os.replace(path, new_path)
            self._update_tree_path(iid, path, new_path)
            self._log(f"Rinominato (Rimuovi spazi): {path.name} -> {new_name}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile rinominare:\n{e}")

    def _action_delete(self, iid):
        path = self.path_by_iid.get(iid)
        if not path:
            return
        if not messagebox.askyesno("Conferma eliminazione", f"Eliminare '{path.name}'?"):
            return
        try:
            if HAVE_SEND2TRASH:
                send2trash(str(path))
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
            self.tree.delete(iid)
            self.path_by_iid.pop(iid, None)
            self.iid_by_path.pop(str(path), None)
            self._log(f"Eliminato: {path.name}")
        except Exception as e:
            messagebox.showerror("Errore", f"Impossibile eliminare:\n{e}")

    def _action_move(self, iid):
        path = self.path_by_iid.get(iid)
        if not path:
            return
        dest_dir = filedialog.askdirectory(title="Scegli destinazione")
        if not dest_dir:
            return
        dest_dir = Path(dest_dir)
        try:
            dest_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            messagebox.showerror("Errore", f"Destinazione non accessibile:\n{e}")
            return
        # vieta move dentro se stessi
        try:
            if path.is_dir() and dest_dir.resolve().is_relative_to(path.resolve()):
                messagebox.showerror("Errore", "Non puoi spostare una cartella dentro sé stessa.")
                return
        except Exception:
            pass

        dest_path = self._unique_dest_path(dest_dir / path.name)
        dlg = MoveProgressDialog(self, "Spostamento…")
        dlg.set_paths(path, dest_path)
        self._run_thread(self._move_with_progress, path, dest_dir, dest_path, iid, dlg)

    def _action_extract_folder(self, iid):
        path = self.path_by_iid.get(iid)
        if not path or not path.is_dir():
            messagebox.showinfo("Estrai", "Seleziona una cartella.")
            return
        self._run_thread(self._extract_folder_then_cleanup, path, True)

    # ---------- MOVE with progress & cancel ----------

    def _unique_dest_path(self, base: Path) -> Path:
        if not base.exists():
            return base
        if base.is_file():
            stem, suffix = base.stem, base.suffix
            parent = base.parent
            i = 1
            while True:
                cand = parent / f"{stem} ({i}){suffix}"
                if not cand.exists():
                    return cand
                i += 1
        else:
            stem = base.name
            parent = base.parent
            i = 1
            while True:
                cand = parent / f"{stem} ({i})"
                if not cand.exists():
                    return cand
                i += 1

    def _move_with_progress(self, src: Path, dest_dir: Path, dest_path: Path, iid, dlg: MoveProgressDialog):
        # Stesso FS -> rename
        if same_filesystem(src, dest_dir):
            try:
                os.replace(src, dest_path)
                self._update_tree_path(iid, src, dest_path)
                self._set_status(f"Spostato (rename): {src.name}")
                self._log(f"Spostato (rename): {src} -> {dest_path}")
            except Exception as e:
                self._log(f"Errore spostamento: {e}")
                self._set_item_status(iid, "Errore")
            finally:
                self.after(0, dlg.destroy)
                self.after(0, self.scan_dir_threaded)  # refresh
            return

        try:
            start = time.time()
            if src.is_file():
                self._copy_file_with_progress(src, dest_path, dlg)
                if not dlg.was_cancelled():
                    try: src.unlink()
                    except Exception: pass
            else:
                self._copy_dir_with_progress(src, dest_path, dlg)
                if not dlg.was_cancelled():
                    try: shutil.rmtree(src, ignore_errors=True)
                    except Exception: pass

            if dlg.was_cancelled():
                # pulizia destinazione parziale
                try:
                    if dest_path.is_dir():
                        shutil.rmtree(dest_path, ignore_errors=True)
                    elif dest_path.exists():
                        dest_path.unlink()
                except Exception:
                    pass
                self._set_item_status(iid, "Annullato")
                self._set_status("Spostamento annullato.")
                self._log(f"Spostamento annullato: {src}")
            else:
                elapsed = time.time() - start
                self._update_tree_path(iid, src, dest_path)
                self._set_item_status(iid, "OK")
                self._set_status(f"Spostato: {src.name} (in {elapsed:.1f}s)")
                self._log(f"Spostato: {src} -> {dest_path} (in {elapsed:.1f}s)")
        except Exception as e:
            self._log(f"Errore spostamento: {e}")
            self._set_item_status(iid, "Errore")
        finally:
            self.after(0, dlg.destroy)
            self.after(0, self.scan_dir_threaded)  # refresh

    def _update_tree_path(self, iid, old: Path, new: Path):
        self.path_by_iid[iid] = new
        self.iid_by_path.pop(str(old), None)
        self.iid_by_path[str(new)] = iid
        vals = list(self.tree.item(iid, "values"))
        vals[1] = new.name
        try:
            vals[3] = human_size(new.stat().st_size) if new.is_file() else ""
        except Exception:
            pass
        self.tree.item(iid, values=vals)

    def _copy_file_with_progress(self, src: Path, dst: Path, dlg: MoveProgressDialog, bufsize: int = 8 * 1024 * 1024):
        dst.parent.mkdir(parents=True, exist_ok=True)
        total = src.stat().st_size
        done = 0
        last_ts = time.time()
        last_done = 0

        with open(src, "rb", buffering=0) as fsrc, open(dst, "wb", buffering=0) as fdst:
            while True:
                if dlg.was_cancelled(): break
                chunk = fsrc.read(bufsize)
                if not chunk:
                    break
                fdst.write(chunk)
                done += len(chunk)

                now = time.time()
                if now - last_ts >= 0.25 or done == total:
                    dt = max(now - last_ts, 1e-6)
                    speed = (done - last_done) / dt  # B/s
                    pct = int(done * 100 / total) if total else 100
                    remaining = (total - done) / speed if speed > 0 else None
                    self.after(0, dlg.update_progress, pct, speed, remaining)
                    last_ts, last_done = now, done

        if not dlg.was_cancelled():
            try:
                shutil.copystat(src, dst, follow_symlinks=True)
            except Exception:
                pass

    def _dir_total_bytes(self, root: Path) -> int:
        total = 0
        for dirpath, _, filenames in os.walk(root):
            for fn in filenames:
                p = Path(dirpath) / fn
                try:
                    total += p.stat().st_size
                except Exception:
                    continue
        return total

    def _copy_dir_with_progress(self, src: Path, dst: Path, dlg: MoveProgressDialog, bufsize: int = 8 * 1024 * 1024):
        total = self._dir_total_bytes(src)
        done = 0
        last_ts = time.time()
        last_done = 0

        for dirpath, _, filenames in os.walk(src):
            if dlg.was_cancelled(): break
            rel = Path(dirpath).relative_to(src)
            target_dir = dst / rel
            target_dir.mkdir(parents=True, exist_ok=True)
            for fn in filenames:
                if dlg.was_cancelled(): break
                sp = Path(dirpath) / fn
                dp = target_dir / fn
                with open(sp, "rb", buffering=0) as fsrc, open(dp, "wb", buffering=0) as fdst:
                    while True:
                        if dlg.was_cancelled(): break
                        chunk = fsrc.read(bufsize)
                        if not chunk:
                            break
                        fdst.write(chunk)
                        done += len(chunk)

                        now = time.time()
                        if now - last_ts >= 0.25 or done == total:
                            dt = max(now - last_ts, 1e-6)
                            speed = (done - last_done) / dt
                            pct = int(done * 100 / total) if total else 100
                            remaining = (total - done) / speed if speed > 0 else None
                            self.after(0, dlg.update_progress, pct, speed, remaining)
                            last_ts, last_done = now, done
                try:
                    shutil.copystat(sp, dp, follow_symlinks=True)
                except Exception:
                    pass
        try:
            shutil.copystat(src, dst, follow_symlinks=True)
        except Exception:
            pass

    # ---------- ORGANIZE / EXTRACT ----------

    def reset_view(self):
        for iid in list(self.path_by_iid.keys()):
            vals = list(self.tree.item(iid, "values"))
            if len(vals) >= 6:
                vals[5] = ""  # stato
            self.tree.item(iid, values=vals)
        self.items_checked.clear()
        self.chk_all_var.set(False)
        self._set_status("Reset completato.")
        self._log("Reset completato.")

    def organize_selected_threaded(self):
        self._run_thread(self._organize_selected)

    def _organize_selected(self):
        if not self.items_checked:
            self._log("Nessuna selezione.")
            return

        self._set_status("Organizzazione in corso…")
        self._set_progress("indeterminate")
        self.progress.start(15)

        selected_paths = []
        for iid in list(self.items_checked):
            p = self.path_by_iid.get(iid)
            if p and p.exists():
                selected_paths.append((iid, p))

        try:
            for iid, path in selected_paths:
                try:
                    if path.is_file():
                        self._organize_file(path)
                    elif path.is_dir():
                        # estrai (se necessario) e PULISCI archivi, poi rinomina
                        self._extract_folder_then_cleanup(path, ask_user=True)
                        self._rename_folder_by_largest(path)
                    self._set_item_status(iid, "OK")
                except Exception as e:
                    self._log(f"Errore su '{path.name}': {e}")
                    self._set_item_status(iid, "Errore")
            self._log("Organizza: completato.")
            self._set_status("Operazione completata.")
        finally:
            self.progress.stop()
            self._set_progress("determinate", 0)
            self.after(0, self.scan_dir_threaded)  # refresh

    def _set_item_status(self, iid, text):
        vals = list(self.tree.item(iid, "values"))
        if len(vals) >= 6:
            vals[5] = text
            self.tree.item(iid, values=vals)

    def _organize_file(self, file_path: Path):
        if not is_supported_video(file_path, self.cfg):
            self._log(f"Ignorato (estensione non supportata): {file_path.name}")
            return
        dest_dir = file_path.parent / sanitize_folder_name(file_path.stem)
        if not dest_dir.exists():
            dest_dir.mkdir(parents=True, exist_ok=True)
        new_path = dest_dir / file_path.name
        if new_path.exists():
            i = 1
            while True:
                alt = dest_dir / f"{file_path.stem} ({i}){file_path.suffix}"
                if not alt.exists():
                    new_path = alt
                    break
                i += 1
        shutil.move(str(file_path), str(new_path))
        self._log(f"Spostato in cartella: {file_path.name} -> {dest_dir.name}")

    def _extract_folder_then_cleanup(self, folder_path: Path, ask_user: bool):
        archives = find_archives_in_folder(folder_path)
        if not archives:
            return
        if ask_user:
            if not messagebox.askyesno("Archivi trovati", f"Nella cartella '{folder_path.name}' ci sono archivi. Estrarre ora?"):
                return
        # estrai con progress
        ok_all = self._extract_archives_in_folder_with_progress(folder_path, archives)
        if ok_all:
            # cancella archivi
            self._delete_archives(archives)
            self._log(f"Pulizia archivi completata in '{folder_path.name}'.")

        # post-extract: impacchetta i file video in sottocartelle
        self._post_extract_file_pack(folder_path)

    def _rename_folder_by_largest(self, folder_path: Path):
        largest = find_largest_supported_file(folder_path, self.cfg)
        if not largest:
            self._log("Nessun file video per rinomina.")
            return
        new_name = sanitize_folder_name(largest.stem)
        new_path = folder_path.parent / new_name
        if new_path.exists() and new_path != folder_path:
            i = 1
            base = new_name
            while True:
                cand = folder_path.parent / f"{base} ({i})"
                if not cand.exists():
                    new_path = cand
                    break
                i += 1
        if new_path != folder_path:
            os.replace(folder_path, new_path)
            self._log(f"Cartella rinominata: {folder_path.name} -> {new_path.name}")

    def _post_extract_file_pack(self, folder_path: Path):
        for dirpath, _, filenames in os.walk(folder_path):
            for fn in filenames:
                p = Path(dirpath) / fn
                if is_supported_video(p, self.cfg):
                    dest_dir = p.parent / sanitize_folder_name(p.stem)
                    if not dest_dir.exists():
                        dest_dir.mkdir(parents=True, exist_ok=True)
                    new_path = dest_dir / p.name
                    if new_path.exists():
                        i = 1
                        while True:
                            alt = dest_dir / f"{p.stem} ({i}){p.suffix}"
                            if not alt.exists():
                                new_path = alt
                                break
                            i += 1
                    shutil.move(str(p), str(new_path))
                    self._log(f"[Post-extract] File organizzato: {p.name}")

    # ---------- EXTRACT (with progress) ----------

    def _delete_archives(self, archives: list[Path]):
        # elimina tutti i file di estensione archivio nella lista (se esistono ancora)
        for a in archives:
            try:
                if a.exists():
                    a.unlink()
            except Exception:
                pass

    def _extract_archives_in_folder_with_progress(self, folder: Path, archives: list[Path]) -> bool:
        # tenta recover .rev con rar (senza finestre, auto-yes)
        revs = [a for a in archives if a.suffix.lower()==".rev"]
        if revs and (self.cfg.get("rar_path")):
            try:
                self._try_rar_recover(folder)
            except Exception as e:
                self._log(f"REBUILD .rev fallito: {e}")

        # dedup: solo primo volume per ogni set
        firsts = []
        seen = set()
        for a in archives:
            f = guess_first_volume(a)
            key = str(f).lower()
            if key not in seen:
                seen.add(key)
                firsts.append(f)

        ok_all = True
        for a in firsts:
            try:
                self._extract_one_archive_with_progress(a, folder)
            except Exception as e:
                ok_all = False
                self._log(f"Estr. fallita '{a.name}': {e}")
        return ok_all

    def _try_rar_recover(self, folder: Path):
        rar_cmd = (self.cfg.get("rar_path") or "").strip()
        if not rar_cmd:
            return
        cmd = [rar_cmd, "rc", "-y", "*.*"]
        subprocess.run(
            cmd, cwd=str(folder),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
            startupinfo=STARTUPINFO, creationflags=CREATE_NO_WINDOW
        )

    def _extract_one_archive_with_progress(self, first_volume: Path, outdir: Path):
        seven = (self.cfg.get("seven_zip_path") or "").strip()
        passwords = [row[0] for row in self._read_tree_values(self.pwd_list)] or self.cfg.get("passwords", [])

        if seven:
            tried = [None] + passwords
            for pwd in tried:
                cmd = [seven, "x", "-y", "-bsp1", f"-o{outdir}"]
                cmd.append(f"-p{pwd}" if pwd else "-p")
                cmd.append(str(first_volume))

                self._set_status(f"Estraggo: {first_volume.name}")
                self._set_progress("determinate", 0)

                with subprocess.Popen(
                    cmd, cwd=str(first_volume.parent),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                    startupinfo=STARTUPINFO, creationflags=CREATE_NO_WINDOW
                ) as proc:
                    last_pct = 0
                    for line in proc.stdout:
                        m = re.search(r"(\d+)%", line)
                        if m:
                            pct = int(m.group(1))
                            if pct != last_pct:
                                last_pct = pct
                                self._set_progress("determinate", pct)
                                self._set_status(f"Estraggo {first_volume.name}: {pct}%")
                    ret = proc.wait()
                if ret == 0:
                    self._log(f"Estratto con 7z: {first_volume.name} {'(pwd)' if pwd else ''}")
                    self._set_progress("determinate", 100)
                    return
                else:
                    continue

            prompt_pwd = simpledialog.askstring("Password richiesta", f"Password per: {first_volume.name}", show="*")
            if prompt_pwd:
                cmd = [seven, "x", "-y", "-bsp1", f"-o{outdir}", f"-p{prompt_pwd}", str(first_volume)]
                self._set_status(f"Estraggo: {first_volume.name}")
                self._set_progress("determinate", 0)
                with subprocess.Popen(
                    cmd, cwd=str(first_volume.parent),
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1,
                    startupinfo=STARTUPINFO, creationflags=CREATE_NO_WINDOW
                ) as proc:
                    last_pct = 0
                    for line in proc.stdout:
                        m = re.search(r"(\d+)%", line)
                        if m:
                            pct = int(m.group(1))
                            if pct != last_pct:
                                last_pct = pct
                                self._set_progress("determinate", pct)
                                self._set_status(f"Estraggo {first_volume.name}: {pct}%")
                    ret = proc.wait()
                if ret != 0:
                    raise RuntimeError("Estr. 7z fallita (password errata?)")
                self._log(f"Estratto con 7z (pwd manuale): {first_volume.name}")
                self._set_progress("determinate", 100)
                return

            raise RuntimeError("Impossibile estrarre con 7z (password sconosciuta o archivio danneggiato).")

        # Fallback: zip/rar/python, mostra n/N
        ext = first_volume.suffix.lower().lstrip(".")
        self._set_status(f"Estraggo: {first_volume.name}")
        self._set_progress("determinate", 0)

        if ext == "zip" and zipfile is not None:
            with zipfile.ZipFile(first_volume, "r") as zf:
                members = zf.infolist()
                N = len(members)
                tried = [None] + passwords
                for pwd in tried:
                    ok = True
                    for i, m in enumerate(members, start=1):
                        try:
                            if pwd:
                                zf.extract(m, path=outdir, pwd=pwd.encode("utf-8"))
                            else:
                                zf.extract(m, path=outdir)
                        except RuntimeError:
                            ok = False
                            break
                        pct = int(i * 100 / N) if N else 100
                        self._set_progress("determinate", pct)
                        self._set_status(f"Estraggo (ZIP) {i}/{N}")
                    if ok:
                        self._log(f"Estratto ZIP: {first_volume.name}")
                        return
            raise RuntimeError("ZIP non estratto (probabile AES o password errata).")

        if ext in ("rar","r00","r01","r02") and HAVE_RARFILE:
            self._apply_external_tools_to_rarfile()
            rf = rarfile.RarFile(first_volume)
            members = rf.infolist()
            N = len(members)
            tried = [None] + passwords
            for pwd in tried:
                ok = True
                for i, m in enumerate(members, start=1):
                    try:
                        rf.extract(m, path=str(outdir), pwd=pwd)
                    except Exception:
                        ok = False
                        break
                    pct = int(i * 100 / N) if N else 100
                    self._set_progress("determinate", pct)
                    self._set_status(f"Estraggo (RAR) {i}/{N}")
                if ok:
                    self._log(f"Estratto RAR: {first_volume.name}")
                    return
            raise RuntimeError("RAR non estratto (password/strumenti mancanti?).")

        if ext == "7z" and HAVE_PY7ZR:
            # py7zr: senza progress fine-grain
            try:
                with py7zr.SevenZipFile(first_volume, mode='r') as zf:
                    zf.extractall(path=outdir)
                self._log(f"Estratto 7z (py7zr): {first_volume.name}")
                return
            except Exception as e:
                raise RuntimeError(f"7z non estratto: {e}")

        raise RuntimeError("Nessun motore di estrazione disponibile. Configura 7-Zip/UnRAR nelle Opzioni.")

    # ---------- Media probing ----------

    def _probe_media_and_update(self, iid, path: Path):
        summary = self._probe_media(path)
        if summary:
            vals = list(self.tree.item(iid, "values"))
            if len(vals) >= 5:
                vals[4] = summary
                self.tree.item(iid, values=vals)

    def _probe_media(self, path: Path) -> str | None:
        # 1) pymediainfo (se installato)
        try:
            if HAVE_PYMEDIAINFO:
                mi = MediaInfo.parse(str(path))
                vtrack = next((t for t in mi.tracks if t.track_type == "Video"), None)
                atracks = [t for t in mi.tracks if t.track_type == "Audio"]
                if vtrack:
                    w = getattr(vtrack, "width", None)
                    h = getattr(vtrack, "height", None)
                    codec = getattr(vtrack, "format", None) or getattr(vtrack, "codec_id", None)
                    br = getattr(vtrack, "bit_rate", None) or getattr(vtrack, "overall_bit_rate", None)
                    if br is not None:
                        try:
                            br = float(br)
                        except Exception:
                            br = None
                    langs = [getattr(a, "language", "").lower() for a in atracks if getattr(a, "language", None)]
                    langs = [l for l in langs if l]
                    q = quality_from_height(h)
                    parts = []
                    if q: parts.append(q)
                    if codec: parts.append(str(codec).lower())
                    if w and h: parts.append(f"{w}x{h}")
                    if br: parts.append(f"{br/1000/1000:.1f} Mbps")
                    if langs: parts.append(",".join(langs))
                    return " • ".join(parts) if parts else None
        except Exception:
            pass

        # 2) mediainfo CLI (JSON)
        mi_path = self.cfg.get("mediainfo_path")
        if mi_path:
            try:
                cmd = [mi_path, "--Output=JSON", str(path)]
                proc = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    startupinfo=STARTUPINFO, creationflags=CREATE_NO_WINDOW
                )
                if proc.returncode == 0 and proc.stdout:
                    import json as _json
                    data = _json.loads(proc.stdout)
                    tracks = data.get("media", {}).get("track", [])
                    vtrack = next((t for t in tracks if t.get("@type")=="Video"), {})
                    atracks = [t for t in tracks if t.get("@type")=="Audio"]
                    w = int(vtrack.get("Width", 0)) or None
                    h = int(vtrack.get("Height", 0)) or None
                    codec = vtrack.get("Format") or vtrack.get("CodecID")
                    br = vtrack.get("BitRate") or data.get("media",{}).get("@overallBitRate")
                    try: br = float(br) if br else None
                    except Exception: br = None
                    langs = []
                    for a in atracks:
                        l = a.get("Language") or a.get("Language_String")
                        if l: langs.append(str(l).lower())
                    q = quality_from_height(h)
                    parts = []
                    if q: parts.append(q)
                    if codec: parts.append(str(codec).lower())
                    if w and h: parts.append(f"{w}x{h}")
                    if br: parts.append(f"{br/1000/1000:.1f} Mbps")
                    if langs: parts.append(",".join(langs))
                    return " • ".join(parts) if parts else None
            except Exception:
                pass

        return None

    # ---------- Options helpers ----------

    def add_ext(self):
        v = self.new_ext_var.get().strip().lstrip(".").lower()
        if not v:
            return
        existing = [row[0] for row in self._read_tree_values(self.ext_list)]
        if v in existing:
            return
        self.ext_list.insert("", "end", values=(v,))
        self.new_ext_var.set("")

    def remove_selected_exts(self):
        for sel in self.ext_list.selection():
            self.ext_list.delete(sel)

    def add_pwd(self):
        v = self.new_pwd_var.get()
        if v is None or v == "":
            return
        self.pwd_list.insert("", "end", values=(v,))
        self.new_pwd_var.set("")

    def remove_selected_pwds(self):
        for sel in self.pwd_list.selection():
            self.pwd_list.delete(sel)

    def browse_7z(self):
        p = filedialog.askopenfilename(title="Seleziona 7-Zip (7z/7zz/7za)")
        if p:
            self.seven_zip_var.set(p)

    def browse_rar(self):
        p = filedialog.askopenfilename(title="Seleziona rar.exe")
        if p:
            self.rar_var.set(p)

    def browse_unrar(self):
        p = filedialog.askopenfilename(title="Seleziona unrar.exe")
        if p:
            self.unrar_var.set(p)

    def browse_bsdtar(self):
        p = filedialog.askopenfilename(title="Seleziona bsdtar/tar")
        if p:
            self.bsdtar_var.set(p)

    def browse_mediainfo(self):
        p = filedialog.askopenfilename(title="Seleziona mediainfo.exe")
        if p:
            self.mediainfo_var.set(p)

    def save_options(self):
        self.cfg["version"] = self.version_var.get().strip() or "1.7"
        self.cfg["video_extensions"] = [row[0] for row in self._read_tree_values(self.ext_list)]
        self.cfg["passwords"] = [row[0] for row in self._read_tree_values(self.pwd_list)]
        self.cfg["seven_zip_path"] = self.seven_zip_var.get().strip() or None
        self.cfg["rar_path"]      = self.rar_var.get().strip() or None
        self.cfg["unrar_path"]    = self.unrar_var.get().strip() or None
        self.cfg["bsdtar_path"]   = self.bsdtar_var.get().strip() or None
        self.cfg["mediainfo_path"]= self.mediainfo_var.get().strip() or None
        save_config(self.cfg)
        self._apply_external_tools_to_rarfile()
        messagebox.showinfo("Opzioni", "Salvate.")

    def _read_tree_values(self, tree: ttk.Treeview):
        vals = []
        for iid in tree.get_children(""):
            row = tree.item(iid).get("values") or []
            if row:
                vals.append(tuple(row))
        return vals


if __name__ == "__main__":
    app = App()
    app.mainloop()