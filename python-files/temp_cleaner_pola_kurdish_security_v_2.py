#!/usr/bin/env python3
"""
Windows Temp File Cleaner — PolaKurdish Security Edition (v2)

• Professional security-themed UI with dark/light mode
• Real-time progress tracking and statistics (files/dirs/freed/skipped/errors)
• System information panel
• Enhanced logging (console + rotating file log) with visual indicators
• Telegram integration button
• Modern animations and visual feedback
• Works on Windows 7 → 11 (x86/x64)
• Python standard library only
• GUI + CLI modes (argparse)
• Logging, dry-run, admin-awareness + auto-elevate option for protected targets
• Modular structure for maintainability
• Cancel-safe (Stop button), thread-safe stats

Developer: PolaKurdish
Telegram: https://t.me/pola_security
License: MIT
"""

from __future__ import annotations
import os
import sys
import json
import time
import shutil
import ctypes
import threading
import webbrowser
import queue
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, List, Optional

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception:
    tk = None  # CLI mode still works without Tk

# ============ CONFIG ============ #
APP_NAME = "TempCleaner"
ORG_DIR = Path(os.environ.get("APPDATA", Path.home() / "AppData/Roaming")) / APP_NAME
SETTINGS_PATH = ORG_DIR / "settings.json"
LOG_PATH = ORG_DIR / "cleaner.log"

# Modern Security-Themed Color Scheme - Inspired by Cyberpunk & Professional Security Tools
SECURITY_COLORS = {
    "dark_bg": "#0a0f1d",
    "dark_panel": "#131a2d",
    "dark_accent": "#00a8ff",
    "dark_accent_hover": "#00d2ff",
    "dark_text": "#e0e6f0",
    "dark_text_dim": "#a0aec0",
    "dark_success": "#00c853",
    "dark_warning": "#ffab00",
    "dark_error": "#ff5252",

    "light_bg": "#f0f4f8",
    "light_panel": "#ffffff",
    "light_accent": "#0066cc",
    "light_accent_hover": "#0055b3",
    "light_text": "#2d3748",
    "light_text_dim": "#718096",
    "light_success": "#00a641",
    "light_warning": "#e68a00",
    "light_error": "#cc0000",

    "card_bg": "#1a2235",
    "card_bg_light": "#edf2f7"
}

DEFAULT_SETTINGS = {
    "targets": {
        "user_temp": True,
        "windows_temp": False,
        "edge_chrome_cache": False,
        "firefox_cache": False,
        "recent_files": False,
        "prefetch": False
    },
    "dry_run": False,
    "days_older": 0,
    "follow_symlinks": False,
    "threads": 4,
    "theme": "dark",  # "dark" or "light"
    "auto_elevate": True
}

# ============ UTILITIES ============ #

def ensure_dirs():
    ORG_DIR.mkdir(parents=True, exist_ok=True)


def human_bytes(n: int) -> str:
    size = float(n)
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} EB"


def is_admin() -> bool:
    if os.name != "nt":
        return os.geteuid() == 0  # type: ignore[attr-defined]
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())  # type: ignore[attr-defined]
    except Exception:
        return False


def elevate_if_needed(argv: List[str]) -> None:
    """Re-launch self as admin on Windows if needed and allowed by settings."""
    if os.name != "nt":
        return
    # Only elevate if any protected targets are enabled
    try:
        settings = load_settings()
    except Exception:
        settings = DEFAULT_SETTINGS.copy()
    protected = settings.get("targets", {}).get("windows_temp") or settings.get("targets", {}).get("prefetch")
    if not protected:
        return
    if settings.get("auto_elevate", True) and not is_admin():
        # Relaunch with runas
        params = " ".join(argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{Path(__file__)}" {params}', None, 1)  # type: ignore[attr-defined]
        sys.exit(0)


def get_system_info():
    import platform
    return {
        "os": f"{platform.system()} {platform.release()}",
        "arch": platform.architecture()[0],
        "admin": "Yes" if is_admin() else "No",
        "temp_path": os.environ.get("TEMP", "N/A"),
        "appdata": os.environ.get("APPDATA", "N/A")
    }

# ============ SETTINGS ============ #

def _deep_merge(base: dict, incoming: dict) -> dict:
    out = json.loads(json.dumps(base))
    for k, v in incoming.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load_settings() -> dict:
    ensure_dirs()
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                saved = json.load(f)
            return _deep_merge(DEFAULT_SETTINGS, saved)
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    ensure_dirs()
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

# ============ LOGGING ============ #
class FileLogger:
    """Thread-safe file logger with rotation (standard library only)."""
    def __init__(self, path: Path, max_bytes: int = 1_000_000, backups: int = 3):
        self.path = path
        self.max_bytes = max_bytes
        self.backups = backups
        self.lock = threading.Lock()
        ensure_dirs()

    def _rotate(self):
        if not self.path.exists() or self.path.stat().st_size < self.max_bytes:
            return
        for i in range(self.backups, 0, -1):
            src = self.path.with_suffix(f".log.{i}")
            dst = self.path.with_suffix(f".log.{i+1}")
            if dst.exists():
                try:
                    dst.unlink()
                except Exception:
                    pass
            if self.path if i == 1 else src:
                pass
        # Shift chain
        for i in range(self.backups, 0, -1):
            src = self.path.with_suffix(f".log.{i-1}") if i > 1 else self.path
            dst = self.path.with_suffix(f".log.{i}")
            try:
                if src.exists():
                    src.rename(dst)
            except Exception:
                pass

    def log_line(self, line: str):
        with self.lock:
            try:
                self._rotate()
                with open(self.path, "a", encoding="utf-8", newline="") as f:
                    f.write(line + "\n")
            except Exception:
                pass

# ============ CLEANER LOGIC ============ #
@dataclass
class Stats:
    files: int = 0
    dirs: int = 0
    bytes: int = 0
    skipped: int = 0
    errors: int = 0
    start_time: float = 0
    end_time: float = 0


class ThreadSafeStats:
    def __init__(self):
        self.s = Stats()
        self.lock = threading.Lock()

    def begin(self):
        with self.lock:
            self.s.start_time = time.time()

    def end(self):
        with self.lock:
            self.s.end_time = time.time()

    def add_file(self, size: int):
        with self.lock:
            self.s.files += 1
            self.s.bytes += max(0, size)

    def add_dir(self):
        with self.lock:
            self.s.dirs += 1

    def add_skipped(self, n: int = 1):
        with self.lock:
            self.s.skipped += n

    def add_error(self, n: int = 1):
        with self.lock:
            self.s.errors += n

    def snapshot(self) -> Stats:
        with self.lock:
            return Stats(**self.s.__dict__)


@dataclass
class Cleaner:
    settings: dict
    log_func: Callable[[str, str], None]
    stats: ThreadSafeStats = field(default_factory=ThreadSafeStats)
    age_cutoff: Optional[float] = field(init=False, default=None)
    stop_flag: threading.Event = field(default_factory=threading.Event)
    file_logger: Optional[FileLogger] = None

    def __post_init__(self):
        self.stats.begin()
        days = self.settings.get("days_older", 0)
        self.age_cutoff = time.time() - days * 86400 if days > 0 else None
        self.file_logger = FileLogger(LOG_PATH)

    def _log(self, msg: str, level: str = "info"):
        ts = time.strftime('%Y-%m-%d %H:%M:%S')
        line = f"[{ts}] {level.upper():7} {msg}"
        if self.file_logger:
            self.file_logger.log_line(line)
        if self.log_func:
            self.log_func(msg, level)

    def delete_file(self, file_path: Path):
        if self.stop_flag.is_set():
            return
        try:
            if self.age_cutoff and file_path.stat().st_mtime > self.age_cutoff:
                self.stats.add_skipped()
                return
            size = 0
            try:
                size = file_path.stat().st_size
            except Exception:
                pass
            if self.settings.get("dry_run", False):
                self._log(f"Would delete: {file_path}", "info")
                return
            file_path.unlink(missing_ok=True)
            self.stats.add_file(size)
        except PermissionError as e:
            try:
                os.chmod(file_path, 0o666)
                file_path.unlink(missing_ok=True)
                self.stats.add_file(0)
            except Exception as e2:
                self.stats.add_error()
                self._log(f"PERMISSION ERROR deleting file {file_path}: {e2}", "error")
        except Exception as e:
            self.stats.add_error()
            self._log(f"ERROR deleting file {file_path}: {e}", "error")

    def delete_dir(self, dir_path: Path):
        if self.stop_flag.is_set():
            return
        if not dir_path.exists():
            return
        try:
            for root, dirs, files in os.walk(dir_path, topdown=False, followlinks=self.settings.get("follow_symlinks", False)):
                if self.stop_flag.is_set():
                    return
                for f in files:
                    self.delete_file(Path(root) / f)
                for d in dirs:
                    p = Path(root) / d
                    try:
                        p.rmdir()
                        self.stats.add_dir()
                    except OSError:
                        self.stats.add_skipped()
            try:
                dir_path.rmdir()
                self.stats.add_dir()
            except OSError:
                self.stats.add_skipped()
        except Exception as e:
            self.stats.add_error()
            self._log(f"ERROR deleting directory {dir_path}: {e}", "error")

    def run(self, target_paths: List[List[Path]], progress_cb: Optional[Callable[[float], None]] = None) -> Stats:
        self.stats.begin()
        tasks: List = []
        with ThreadPoolExecutor(max_workers=int(self.settings.get("threads", 4))) as ex:
            # Queue all work first
            for group in target_paths:
                for path in group:
                    if self.stop_flag.is_set():
                        break
                    if path.exists():
                        self._log(f"Processing: {path}", "info")
                        if path.is_dir():
                            tasks.append(ex.submit(self.delete_dir, path))
                        else:
                            tasks.append(ex.submit(self.delete_file, path))
            total = len(tasks) or 1
            done = 0
            for fut in as_completed(tasks):
                _ = fut.result()
                done += 1
                if progress_cb:
                    progress_cb(done / total * 100)
        self.stats.end()
        return self.stats.snapshot()

# ============ TARGETS DISCOVERY ============ #

def discover_targets(settings: dict) -> List[List[Path]]:
    targets: List[List[Path]] = []
    # User temp
    if settings["targets"].get("user_temp"):
        targets.append([Path(os.environ.get("TEMP", str(Path.home() / "AppData/Local/Temp")))])
    # Windows temp (protected)
    if settings["targets"].get("windows_temp"):
        targets.append([Path(os.environ.get("SystemRoot", "C:/Windows")) / "Temp"])
    # Recent files
    if settings["targets"].get("recent_files"):
        targets.append([Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming"))) / "Microsoft/Windows/Recent"])
    # Prefetch (protected)
    if settings["targets"].get("prefetch"):
        targets.append([Path(os.environ.get("SystemRoot", "C:/Windows")) / "Prefetch"])
    # Edge/Chrome
    if settings["targets"].get("edge_chrome_cache"):
        local_appdata = Path(os.environ.get("LOCALAPPDATA", str(Path.home() / "AppData/Local")))
        targets.append([
            local_appdata / "Google/Chrome/User Data/Default/Cache",
            local_appdata / "Microsoft/Edge/User Data/Default/Cache"
        ])
    # Firefox
    if settings["targets"].get("firefox_cache"):
        appdata = Path(os.environ.get("APPDATA", str(Path.home() / "AppData/Roaming")))
        profiles = appdata / "Mozilla/Firefox/Profiles"
        if profiles.exists():
            for prof in profiles.glob("*.default*"):
                targets.append([prof / "cache2"])
    return targets

# ============ GUI ============ #

class AnimatedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg_color=None, fg_color=None, hover_color=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.command = command
        self.text_value = text
        self.bg_color = bg_color or SECURITY_COLORS["dark_accent"]
        self.fg_color = fg_color or "white"
        self.hover_color = hover_color or SECURITY_COLORS["dark_accent_hover"]
        self.radius = 20
        self.width = kwargs.get("width", 160)
        self.height = kwargs.get("height", 42)
        self.config(width=self.width, height=self.height, highlightthickness=0, bg=parent.cget('bg'))
        self.button = self.create_rounded_rect(0, 0, self.width, self.height, self.radius, fill=self.bg_color, outline="")
        self.text_id = self.create_text(self.width/2, self.height/2, text=self.text_value, fill=self.fg_color, font=('Segoe UI', 10, 'bold'))
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2, x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1]
        return self.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self, _):
        self.itemconfig(self.button, fill=self.hover_color)

    def on_leave(self, _):
        self.itemconfig(self.button, fill=self.bg_color)

    def on_click(self, _):
        if self.command:
            self.command()


class ProgressTracker:
    def __init__(self, master):
        self.frame = tk.Frame(master, bg=master.cget('bg'))
        self.frame.pack(fill="x", pady=(5, 10))
        self.label = tk.Label(self.frame, text="Ready to clean", font=("Segoe UI", 9), bg=master.cget('bg'))
        self.label.pack(fill="x", pady=(0, 5))
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", mode="determinate", length=100)
        self.progress.pack(fill="x")
        self.progress['value'] = 0

    def update_progress(self, percent: float):
        self.progress['value'] = percent
        self.label.config(text=f"Cleaning in progress... {percent:.1f}%")
        self.frame.update_idletasks()


class StatsPanel:
    def __init__(self, master, theme="dark"):
        self.frame = tk.Frame(master, bg=master.cget('bg'))
        self.frame.pack(fill="x", pady=10)
        self.theme = theme
        self.card_bg = SECURITY_COLORS["card_bg"] if theme == "dark" else SECURITY_COLORS["card_bg_light"]
        self.cards = {}
        for i, (title, value, color_key) in enumerate([
            ("Files", "0", "dark_accent" if theme=="dark" else "light_accent"),
            ("Directories", "0", "dark_accent" if theme=="dark" else "light_accent"),
            ("Freed Space", "0 B", "dark_success" if theme=="dark" else "light_success"),
            ("Skipped", "0", "dark_warning" if theme=="dark" else "light_warning"),
            ("Errors", "0", "dark_error" if theme=="dark" else "light_error"),
            ("Duration", "0s", "dark_warning" if theme=="dark" else "light_warning"),
        ]):
            card = self._card(self.frame, title, value, SECURITY_COLORS[color_key])
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            self.cards[title.lower().replace(" ", "_")] = card

    def _card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg=self.card_bg, highlightbackground=color, highlightthickness=1, bd=0)
        frame.columnconfigure(0, weight=1)
        tk.Label(frame, text=title, font=("Segoe UI", 9, "bold"), bg=self.card_bg,
                 fg=SECURITY_COLORS["dark_text_dim"] if self.theme=="dark" else SECURITY_COLORS["light_text_dim"]).pack(pady=(5,2))
        val = tk.Label(frame, text=value, font=("Segoe UI", 12, "bold"), bg=self.card_bg, fg=color)
        val.pack(pady=(2,5))
        return frame

    def update_stats(self, s: Stats):
        self.cards["files"].winfo_children()[1].config(text=str(s.files))
        self.cards["directories"].winfo_children()[1].config(text=str(s.dirs))
        self.cards["freed_space"].winfo_children()[1].config(text=human_bytes(s.bytes))
        self.cards["skipped"].winfo_children()[1].config(text=str(s.skipped))
        self.cards["errors"].winfo_children()[1].config(text=str(s.errors))
        self.cards["duration"].winfo_children()[1].config(text=f"{(s.end_time - s.start_time):.1f}s")


class SystemInfoPanel:
    def __init__(self, master, theme="dark"):
        self.frame = tk.Frame(master, bg=master.cget('bg'))
        self.frame.pack(fill="x", pady=(0, 10))
        tk.Label(self.frame, text="System Information", font=("Segoe UI", 10, "bold"),
                 bg=master.cget('bg'), fg=SECURITY_COLORS["dark_accent"] if theme=="dark" else SECURITY_COLORS["light_accent"]).pack(anchor="w", pady=(0,5))
        info = get_system_info()
        for key, value in info.items():
            row = tk.Frame(self.frame, bg=master.cget('bg'))
            row.pack(fill="x", anchor="w")
            tk.Label(row, text=f"{key.title()}:", font=("Segoe UI", 9, "bold"), bg=master.cget('bg'),
                     fg=SECURITY_COLORS["dark_text_dim"] if theme=="dark" else SECURITY_COLORS["light_text_dim"], width=15, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 9), bg=master.cget('bg'),
                     fg=SECURITY_COLORS["dark_text"] if theme=="dark" else SECURITY_COLORS["light_text"]).pack(side="left", fill="x", expand=True)


class LogViewer:
    def __init__(self, master, theme="dark"):
        self.frame = tk.Frame(master, bg=master.cget('bg'))
        self.frame.pack(fill="both", expand=True, pady=(0, 10))
        self.text = tk.Text(self.frame, height=12,
                            bg=SECURITY_COLORS["dark_bg"] if theme=="dark" else SECURITY_COLORS["light_bg"],
                            fg=SECURITY_COLORS["dark_text"] if theme=="dark" else SECURITY_COLORS["light_text"],
                            insertbackground="white" if theme=="dark" else "black",
                            selectbackground=SECURITY_COLORS["dark_accent"] if theme=="dark" else SECURITY_COLORS["light_accent"],
                            padx=10, pady=10)
        scrollbar = ttk.Scrollbar(self.frame, command=self.text.yview)
        self.text.configure(yscrollcommand=scrollbar.set)
        self.text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.text.tag_config("info", foreground=SECURITY_COLORS["dark_text_dim"] if theme=="dark" else SECURITY_COLORS["light_text_dim"])
        self.text.tag_config("success", foreground=SECURITY_COLORS["dark_success"] if theme=="dark" else SECURITY_COLORS["light_success"])
        self.text.tag_config("warning", foreground=SECURITY_COLORS["dark_warning"] if theme=="dark" else SECURITY_COLORS["light_warning"])
        self.text.tag_config("error", foreground=SECURITY_COLORS["dark_error"] if theme=="dark" else SECURITY_COLORS["light_error"])
        self.log("TempCleaner initialized. Ready to clean system temp files.", "info")

    def log(self, message: str, msg_type: str = "info"):
        self.text.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n", msg_type)
        self.text.see("end")

    def clear(self):
        self.text.delete("1.0", "end")


class ThemeManager:
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.theme = settings.get("theme", "dark")
        self._apply_root()
        self.style = ttk.Style()
        self.update_style()

    def _apply_root(self):
        self.root.configure(bg=SECURITY_COLORS["dark_bg"] if self.theme=="dark" else SECURITY_COLORS["light_bg"])

    def update_style(self):
        self.style.theme_use('clam')
        if self.theme == "dark":
            self.style.configure('TFrame', background=SECURITY_COLORS["dark_bg"])
            self.style.configure('TLabel', background=SECURITY_COLORS["dark_bg"], foreground=SECURITY_COLORS["dark_text"])
            self.style.configure('TButton', background=SECURITY_COLORS["dark_panel"], foreground=SECURITY_COLORS["dark_text"])
            self.style.map('TButton', background=[('active', SECURITY_COLORS["dark_accent_hover"])], foreground=[('active', 'white')])
            self.style.configure('TProgressbar', troughcolor=SECURITY_COLORS["dark_panel"], background=SECURITY_COLORS["dark_accent"])
        else:
            self.style.configure('TFrame', background=SECURITY_COLORS["light_bg"])
            self.style.configure('TLabel', background=SECURITY_COLORS["light_bg"], foreground=SECURITY_COLORS["light_text"])
            self.style.configure('TButton', background=SECURITY_COLORS["light_panel"], foreground=SECURITY_COLORS["light_text"])
            self.style.map('TButton', background=[('active', SECURITY_COLORS["light_accent_hover"])], foreground=[('active', 'white')])
            self.style.configure('TProgressbar', troughcolor=SECURITY_COLORS["light_panel"], background=SECURITY_COLORS["light_accent"])

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings["theme"] = self.theme
        save_settings(self.settings)
        self._apply_root()
        self.update_style()


class GuiApp:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        self.theme = self.settings.get("theme", "dark")
        self.theme_manager = ThemeManager(root, self.settings)

        self.root.title("TempCleaner — PolaKurdish Security")
        self.root.geometry("900x640")
        self.root.minsize(700, 520)
        self.stop_event = threading.Event()

        self._build_ui()
        self._add_security_badge()

    # ---------- UI ---------- #
    def _build_ui(self):
        self.main_container = tk.Frame(self.root, bg=SECURITY_COLORS["dark_bg"] if self.theme=="dark" else SECURITY_COLORS["light_bg"])
        self.main_container.pack(fill="both", expand=True, padx=20, pady=15)

        header = tk.Frame(self.main_container, bg=self.main_container.cget('bg'))
        header.pack(fill="x", pady=(0, 10))
        tk.Label(header, text="Windows Temp File Cleaner", font=("Segoe UI", 18, "bold"),
                 fg=SECURITY_COLORS["dark_accent"] if self.theme=="dark" else SECURITY_COLORS["light_accent"],
                 bg=self.main_container.cget('bg')).pack(side="left")

        self.theme_btn = tk.Button(header, text="🌓 Dark Mode" if self.theme=="light" else "☀️ Light Mode",
                                   command=self._toggle_theme,
                                   bg=SECURITY_COLORS["dark_panel"] if self.theme=="dark" else SECURITY_COLORS["light_panel"],
                                   fg=SECURITY_COLORS["dark_text"] if self.theme=="dark" else SECURITY_COLORS["light_text"],
                                   relief="flat", padx=10)
        self.theme_btn.pack(side="right")

        self.system_info = SystemInfoPanel(self.main_container, self.theme)
        self.stats_panel = StatsPanel(self.main_container, self.theme)
        self.progress_tracker = ProgressTracker(self.main_container)
        self.log_viewer = LogViewer(self.main_container, self.theme)

        btn_frame = tk.Frame(self.main_container, bg=self.main_container.cget('bg'))
        btn_frame.pack(fill="x", pady=(10,0))

        self.telegram_btn = AnimatedButton(btn_frame, text="Join Security Channel",
                                           command=lambda: webbrowser.open("https://t.me/pola_security"),
                                           bg_color=SECURITY_COLORS["dark_accent"] if self.theme=="dark" else SECURITY_COLORS["light_accent"],
                                           fg_color="white", width=220, height=42)
        self.telegram_btn.pack(side="left", padx=5)

        self.settings_btn = AnimatedButton(btn_frame, text="Settings", command=self.open_settings,
                                           bg_color=SECURITY_COLORS["dark_warning"] if self.theme=="dark" else SECURITY_COLORS["light_warning"],
                                           fg_color="white", width=140, height=42)
        self.settings_btn.pack(side="right", padx=5)

        self.stop_btn = AnimatedButton(btn_frame, text="Stop", command=self.stop_clean,
                                       bg_color=SECURITY_COLORS["dark_error"] if self.theme=="dark" else SECURITY_COLORS["light_error"],
                                       fg_color="white", width=120, height=42)
        self.stop_btn.pack(side="right", padx=5)

        self.clean_btn = AnimatedButton(btn_frame, text="Start Cleaning Now", command=self.start_clean,
                                        bg_color=SECURITY_COLORS["dark_success"] if self.theme=="dark" else SECURITY_COLORS["light_success"],
                                        fg_color="white", hover_color=SECURITY_COLORS["dark_success"] if self.theme=="dark" else SECURITY_COLORS["light_success"],
                                        width=220, height=42)
        self.clean_btn.pack(side="right", padx=5)

    def _add_security_badge(self):
        badge = tk.Frame(self.root, bg=SECURITY_COLORS["dark_success"] if self.theme=="dark" else SECURITY_COLORS["light_success"], bd=1, relief="solid")
        badge.place(relx=0.98, rely=0.02, anchor="ne", width=150, height=30)
        tk.Label(badge, text="SECURITY VERIFIED", font=("Segoe UI", 8, "bold"),
                 fg="white" if self.theme=="dark" else "black",
                 bg=SECURITY_COLORS["dark_success"] if self.theme=="dark" else SECURITY_COLORS["light_success"]).pack(fill="both", expand=True)

    # ---------- Actions ---------- #
    def _toggle_theme(self):
        self.theme_manager.toggle_theme()
        self.theme = self.theme_manager.theme
        self.theme_btn.config(text="🌓 Dark Mode" if self.theme=="light" else "☀️ Light Mode")
        # Rebuild badge to update colors
        for widget in list(self.root.children.values()):
            if isinstance(widget, tk.Frame) and widget.place_info():
                widget.destroy()
        self._add_security_badge()

    def open_settings(self):
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Settings")
        settings_win.geometry("520x420")
        settings_win.transient(self.root)
        settings_win.grab_set()
        bg_color = SECURITY_COLORS["dark_bg"] if self.theme=="dark" else SECURITY_COLORS["light_bg"]
        settings_win.configure(bg=bg_color)

        notebook = ttk.Notebook(settings_win)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        targets_frame = ttk.Frame(notebook)
        notebook.add(targets_frame, text="Targets")
        # Keep tkinter variables in this dict to read later
        self._ui_vars = getattr(self, "_ui_vars", {})
        self._ui_vars.setdefault("targets", {})
        for target, enabled in self.settings["targets"].items():
            var = tk.BooleanVar(value=bool(enabled))
            self._ui_vars["targets"][target] = var
            chk = ttk.Checkbutton(targets_frame, text=target.replace("_", " ").title(), variable=var)
            chk.pack(anchor="w", padx=20, pady=5)

        options_frame = ttk.Frame(notebook)
        notebook.add(options_frame, text="Options")
        # Days older
        days_frame = ttk.Frame(options_frame)
        days_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(days_frame, text="Delete files older than:").pack(side="left")
        days_var = tk.IntVar(value=int(self.settings.get("days_older", 0)))
        self._ui_vars["days_older"] = days_var
        ttk.Spinbox(days_frame, from_=0, to=365, width=5, textvariable=days_var).pack(side="left", padx=5)
        ttk.Label(days_frame, text="days").pack(side="left")
        # Dry run
        dry_run_var = tk.BooleanVar(value=bool(self.settings.get("dry_run", False)))
        self._ui_vars["dry_run"] = dry_run_var
        ttk.Checkbutton(options_frame, text="Dry Run (Show what would be deleted)", variable=dry_run_var).pack(anchor="w", padx=20, pady=5)
        # Threads
        threads_frame = ttk.Frame(options_frame)
        threads_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(threads_frame, text="Threads:").pack(side="left")
        threads_var = tk.IntVar(value=int(self.settings.get("threads", 4)))
        self._ui_vars["threads"] = threads_var
        ttk.Spinbox(threads_frame, from_=1, to=16, width=5, textvariable=threads_var).pack(side="left", padx=5)
        # Follow symlinks
        follow_var = tk.BooleanVar(value=bool(self.settings.get("follow_symlinks", False)))
        self._ui_vars["follow_symlinks"] = follow_var
        ttk.Checkbutton(options_frame, text="Follow Symlinks", variable=follow_var).pack(anchor="w", padx=20, pady=5)
        # Auto-elevate
        elev_var = tk.BooleanVar(value=bool(self.settings.get("auto_elevate", True)))
        self._ui_vars["auto_elevate"] = elev_var
        ttk.Checkbutton(options_frame, text="Auto-elevate for protected folders (Windows)", variable=elev_var).pack(anchor="w", padx=20, pady=5)

        ttk.Button(settings_win, text="Save Settings", command=lambda: self._save_settings(settings_win)).pack(pady=10)

    def _save_settings(self, window):
        # Targets
        for t, var in self._ui_vars["targets"].items():
            self.settings["targets"][t] = bool(var.get())
        # Others
        self.settings["days_older"] = int(self._ui_vars["days_older"].get())
        self.settings["dry_run"] = bool(self._ui_vars["dry_run"].get())
        self.settings["threads"] = int(self._ui_vars["threads"].get())
        self.settings["follow_symlinks"] = bool(self._ui_vars["follow_symlinks"].get())
        self.settings["auto_elevate"] = bool(self._ui_vars["auto_elevate"].get())
        save_settings(self.settings)
        window.destroy()
        self.log_viewer.log("Settings saved successfully.", "success")

    def stop_clean(self):
        self.stop_event.set()
        self.log_viewer.log("Stop requested — finishing current tasks...", "warning")

    def start_clean(self):
        # Reset stop flag
        self.stop_event.clear()
        # Disable start during operation
        self.clean_btn.config(state="disabled")
        self.log_viewer.log("Starting cleaning process...", "info")
        targets = discover_targets(self.settings)
        if not targets:
            self.log_viewer.log("No targets selected. Enable at least one target in Settings.", "warning")
            self.clean_btn.config(state="normal")
            return

        def progress_cb(pct: float):
            self.progress_tracker.update_progress(pct)

        def thread_run():
            cleaner = Cleaner(self.settings, log_func=self.log_viewer.log)
            cleaner.stop_flag = self.stop_event
            stats = cleaner.run(targets, progress_cb=progress_cb)
            self.stats_panel.update_stats(stats)
            if stats.errors == 0:
                self.log_viewer.log(f"Cleaning completed successfully! Freed {human_bytes(stats.bytes)} in {stats.files} files.", "success")
            else:
                self.log_viewer.log(f"Cleaning completed with {stats.errors} errors. Freed {human_bytes(stats.bytes)} in {stats.files} files.", "warning")
            self.clean_btn.config(state="normal")

        threading.Thread(target=thread_run, daemon=True).start()

# ============ CLI MODE ============ #

def run_cli(argv: List[str]) -> int:
    import argparse
    ensure_dirs()
    parser = argparse.ArgumentParser(description="TempCleaner — PolaKurdish Security (CLI)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be deleted")
    parser.add_argument("--days", type=int, default=None, help="Only delete files older than N days")
    parser.add_argument("--threads", type=int, default=None, help="Number of worker threads (default from settings)")
    parser.add_argument("--follow-symlinks", action="store_true", help="Follow symlinks when walking directories")
    parser.add_argument("--targets", type=str, default=None,
                        help="Comma list: user_temp,windows_temp,edge_chrome_cache,firefox_cache,recent_files,prefetch")
    parser.add_argument("--no-elevate", action="store_true", help="Do not auto-elevate on Windows")
    parser.add_argument("--stats-only", action="store_true", help="Print final stats only")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode")

    args = parser.parse_args(argv[1:])

    if args.gui:
        return launch_gui()

    settings = load_settings()
    if args.dry_run:
        settings["dry_run"] = True
    if args.days is not None:
        settings["days_older"] = max(0, args.days)
    if args.threads is not None:
        settings["threads"] = max(1, args.threads)
    if args.follow_symlinks:
        settings["follow_symlinks"] = True
    if args.no_elevate:
        settings["auto_elevate"] = False
    if args.targets:
        # reset all to False then enable provided ones
        for k in list(settings["targets"].keys()):
            settings["targets"][k] = False
        for name in [t.strip() for t in args.targets.split(',') if t.strip()]:
            if name in settings["targets"]:
                settings["targets"][name] = True
            else:
                print(f"Unknown target: {name}")

    # Auto elevate if needed
    if os.name == 'nt' and settings.get("auto_elevate", True):
        protected = settings["targets"].get("windows_temp") or settings["targets"].get("prefetch")
        if protected and not is_admin():
            elevate_if_needed(sys.argv)
            return 0

    qlog = queue.Queue()

    def log_func(msg: str, level: str="info"):
        line = f"[{time.strftime('%H:%M:%S')}] {level.upper():7} {msg}"
        if not args.stats_only:
            print(line)
        qlog.put((msg, level))

    cleaner = Cleaner(settings, log_func=log_func)
    targets = discover_targets(settings)
    total_steps = max(1, sum(len(g) for g in targets))
    done = 0

    def progress_cb(p):
        nonlocal done
        done = p

    stats = cleaner.run(targets, progress_cb=lambda pct: None)

    print("\n=== Final Stats ===")
    print(f"Files deleted : {stats.files}")
    print(f"Dirs removed  : {stats.dirs}")
    print(f"Freed space   : {human_bytes(stats.bytes)}")
    print(f"Skipped       : {stats.skipped}")
    print(f"Errors        : {stats.errors}")
    print(f"Duration      : {(stats.end_time - stats.start_time):.1f}s")
    return 0

# ============ MAIN ============ #

def launch_gui() -> int:
    if tk is None:
        print("Tkinter not available. Run with Python that includes Tk support, or use --gui only on systems with Tk.")
        return 1
    root = tk.Tk()
    GuiApp(root)
    root.mainloop()
    return 0


def main():
    ensure_dirs()
    # Auto-elevate if settings require and on Windows
    try:
        elevate_if_needed(sys.argv)
    except Exception:
        pass

    # If running in a non-Windows TTY without Tk, fall back to CLI
    if len(sys.argv) > 1 and "--gui" not in sys.argv:
        sys.exit(run_cli(sys.argv))
    else:
        code = launch_gui()
        if code != 0:
            # fallback to CLI if GUI not available
            sys.exit(run_cli(sys.argv))


if __name__ == "__main__":
    main()
