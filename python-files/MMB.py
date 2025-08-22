#!/usr/bin/env python3
"""
GT Scanner - Professional malware/virus scanner with modern UI.

⚠️ Disclaimer
This tool is for educational and defensive purposes only. It does NOT guarantee
complete malware detection. Use at your own risk.

Features:
- Modern, professional UI
- Real-time scanning statistics and progress visualization
- Professional color-coded risk indicators
- Quarantine management and CSV export
"""
from __future__ import annotations

import base64
import csv
import hashlib
import json
import math
import os
import queue
import shutil
import string
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.font import Font

APP_NAME = "GT Scanner"
APP_VERSION = "2.0"
HOME = Path.home()
DATA_DIR = HOME / ".gt_scanner"
QUARANTINE_DIR = DATA_DIR / "quarantine"
MANIFEST_PATH = QUARANTINE_DIR / "manifest.json"
REPORTS_DIR = DATA_DIR / "reports"

# Color scheme with black text
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#34495e',
    'accent': '#3498db',
    'success': '#27ae60',
    'warning': '#f39c12',
    'danger': '#e74c3c',
    'light': '#ecf0f1',
    'dark': '#2c3e50',
    'text': '#000000',  # Changed to black
    'text_light': '#666666',  # Darker gray for better contrast
    'background': '#ffffff',
    'card': '#f8f9fa',
    'border': '#dee2e6'
}

# --- Simple local signature set (placeholders) ---------------------------------
BAD_HASHES = {
    "md5": {
        # "44d88612fea8a8f36de82e1278abb02f",  # EICAR test file MD5
    },
    "sha256": {
        # "275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f",
    },
}

SUSPICIOUS_PATTERNS = [
    "powershell", "wscript", "cscript", "rundll32", "wmic", "regsvr32",
    "bitsadmin", "mimikatz", "metasploit", "shellcode", "invoke-", "amsi",
    "/system32/", "certutil", "-enc", "base64", "vssadmin", "bcdedit",
]

EXECUTABLE_EXTS = {"exe", "dll", "scr", "bat", "cmd", "com", "ps1", "vbs", "js", "jse", "msi"}
SCRIPT_EXTS = {"ps1", "vbs", "js", "jse", "bat", "cmd", "py"}
ARCHIVE_EXTS = {"zip", "rar", "7z", "gz", "bz2"}
OFFICE_EXTS = {"doc", "docm", "xls", "xlsm", "ppt", "pptm"}

# --- Data models ----------------------------------------------------------------
@dataclass
class Detection:
    kind: str
    message: str
    score: int

@dataclass
class ScanResult:
    path: Path
    md5: str
    sha256: str
    size: int
    detections: List[Detection] = field(default_factory=list)

    @property
    def risk(self) -> int:
        return max(0, sum(d.score for d in self.detections))

    @property
    def verdict(self) -> str:
        if any(d.kind == "signature" for d in self.detections):
            return "Malicious"
        if self.risk >= 60:
            return "Suspicious"
        return "Clean"

    @property
    def color(self) -> str:
        if self.verdict == "Malicious":
            return COLORS['danger']
        elif self.verdict == "Suspicious":
            return COLORS['warning']
        return COLORS['success']

# --- Utilities ------------------------------------------------------------------

def read_chunks(path: Path, chunk_size: int = 1024 * 1024):
    with open(path, "rb") as f:
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            yield data

def file_hashes(path: Path) -> Tuple[str, str]:
    md5 = hashlib.md5()
    sha256 = hashlib.sha256()
    for chunk in read_chunks(path):
        md5.update(chunk)
        sha256.update(chunk)
    return md5.hexdigest(), sha256.hexdigest()

def shannon_entropy(data: bytes) -> float:
    if not data:
        return 0.0
    freq = [0] * 256
    for b in data:
        freq[b] += 1
    entropy = 0.0
    length = len(data)
    for c in freq:
        if c:
            p = c / length
            entropy -= p * math.log2(p)
    return entropy

def peek_bytes(path: Path, n: int = 1024 * 64) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read(n)
    except Exception:
        return b""

def is_hidden(path: Path) -> bool:
    name = path.name
    if name.startswith('.'):
        return True
    return False

def format_size(size: int) -> str:
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

# --- Heuristics -----------------------------------------------------------------

def heuristic_checks(path: Path, head: bytes, ext: str) -> List[Detection]:
    dets: List[Detection] = []

    # Check PE header (MZ)
    if len(head) >= 2 and head[:2] == b"MZ":
        dets.append(Detection("heuristic", "Windows PE executable", 25))

    # Entropy spike (packed/obfuscated)
    entropy = shannon_entropy(head)
    if entropy >= 7.3:
        dets.append(Detection("heuristic", f"High entropy ({entropy:.2f})", 20))

    # Double extension trick
    parts = path.name.split('.')
    if len(parts) >= 3:
        last, prev = parts[-1].lower(), parts[-2].lower()
        if last in {"exe", "scr", "bat", "cmd"} and prev in {"txt", "pdf", "doc", "jpg", "png"}:
            dets.append(Detection("heuristic", "Double extension (disguised exec)", 25))

    # Suspicious strings
    lower_head = head.lower()
    for s in SUSPICIOUS_PATTERNS:
        if s.encode(errors="ignore") in lower_head:
            dets.append(Detection("heuristic", f"Suspicious string: {s}", 10))

    # Script heaviness
    if ext in SCRIPT_EXTS:
        dets.append(Detection("heuristic", f"Script file ({ext})", 10))
        if b"eval(" in lower_head or b"exec(" in lower_head:
            dets.append(Detection("heuristic", "Dynamic eval/exec", 15))
        if b"base64" in lower_head or b"b64decode" in lower_head:
            dets.append(Detection("heuristic", "Base64 presence", 10))

    # Office macros hint
    if ext in OFFICE_EXTS and (b"VBA" in head or b"_VBA_PROJECT" in head or b"Attribute VB_" in head):
        dets.append(Detection("heuristic", "Possible Office macros", 20))

    # Hidden file
    if is_hidden(path):
        dets.append(Detection("heuristic", "Hidden file", 5))

    return dets

# --- Scanner --------------------------------------------------------------------

def scan_file(path: Path) -> Optional[ScanResult]:
    try:
        if not path.is_file():
            return None
        size = path.stat().st_size
        if size > 200 * 1024 * 1024:
            return None

        md5, sha256 = file_hashes(path)
        dets: List[Detection] = []

        # Signature checks
        if md5 in BAD_HASHES["md5"] or sha256 in BAD_HASHES["sha256"]:
            dets.append(Detection("signature", "Matched known‑bad hash", 100))

        head = peek_bytes(path)
        ext = path.suffix.lower().lstrip('.')
        dets.extend(heuristic_checks(path, head, ext))

        return ScanResult(path=path, md5=md5, sha256=sha256, size=size, detections=dets)
    except Exception as e:
        return ScanResult(path=path, md5="", sha256="", size=0,
                          detections=[Detection("error", f"Error: {e}", 0)])

def iter_files(root: Path) -> List[Path]:
    files: List[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        for fn in filenames:
            try:
                p = Path(dirpath) / fn
                files.append(p)
            except Exception:
                pass
    return files

# --- Quarantine -----------------------------------------------------------------

def ensure_dirs():
    for p in (DATA_DIR, QUARANTINE_DIR, REPORTS_DIR):
        p.mkdir(parents=True, exist_ok=True)

def load_manifest() -> Dict[str, Dict[str, str]]:
    if MANIFEST_PATH.exists():
        try:
            return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_manifest(m: Dict[str, Dict[str, str]]):
    MANIFEST_PATH.write_text(json.dumps(m, indent=2), encoding="utf-8")

def quarantine_file(path: Path) -> Optional[Path]:
    try:
        ensure_dirs()
        qname = f"{int(time.time())}_{path.name}"
        dest = QUARANTINE_DIR / qname
        shutil.move(str(path), str(dest))
        manifest = load_manifest()
        manifest[str(dest)] = {"original": str(path), "timestamp": datetime.utcnow().isoformat()}
        save_manifest(manifest)
        return dest
    except Exception as e:
        messagebox.showerror(APP_NAME, f"Failed to quarantine: {e}")
        return None

def restore_file(qpath: Path) -> bool:
    try:
        manifest = load_manifest()
        rec = manifest.get(str(qpath))
        if not rec:
            raise RuntimeError("No manifest entry")
        original = Path(rec["original"])
        original.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(qpath), str(original))
        manifest.pop(str(qpath), None)
        save_manifest(manifest)
        return True
    except Exception as e:
        messagebox.showerror(APP_NAME, f"Failed to restore: {e}")
        return False

# --- Modern UI Components -------------------------------------------------------

class ModernButton(ttk.Button):
    def __init__(self, master, **kwargs):
        style = kwargs.pop('style', 'Modern.TButton')
        super().__init__(master, style=style, **kwargs)

class ModernEntry(ttk.Entry):
    def __init__(self, master, **kwargs):
        style = kwargs.pop('style', 'Modern.TEntry')
        super().__init__(master, style=style, **kwargs)

class ModernProgressbar(ttk.Progressbar):
    def __init__(self, master, **kwargs):
        style = kwargs.pop('style', 'Modern.Horizontal.TProgressbar')
        super().__init__(master, style=style, **kwargs)

class RiskBadge(ttk.Label):
    def __init__(self, master, risk_level: str = "clean", **kwargs):
        self.risk_level = risk_level
        style_map = {
            "clean": "Risk.Clean.TLabel",
            "suspicious": "Risk.Suspicious.TLabel",
            "malicious": "Risk.Malicious.TLabel"
        }
        style = style_map.get(risk_level, "Risk.Clean.TLabel")
        super().__init__(master, style=style, **kwargs)

# --- Main Application -----------------------------------------------------------

class GTScannerApp(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master.title(f"{APP_NAME} {APP_VERSION}")
        self.master.geometry("1200x600")
        self.master.minsize(1000, 500)
        self.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self._setup_styles()
        self._build_ui()
        
        self.selected_dir: Optional[Path] = None
        self.executor: Optional[ThreadPoolExecutor] = None
        self.stop_event = threading.Event()
        self.results: List[ScanResult] = []
        self.scan_stats = {'total': 0, 'scanned': 0, 'suspicious': 0, 'malicious': 0, 'clean': 0}
        ensure_dirs()

    def _setup_styles(self):
        style = ttk.Style()
        
        # Configure main styles with black text
        style.configure('TFrame', background=COLORS['background'])
        style.configure('TLabel', background=COLORS['background'], foreground=COLORS['text'])
        style.configure('TButton', padding=6, foreground=COLORS['text'])
        
        # Modern button styles
        style.configure('Modern.TButton', 
                       background=COLORS['accent'],
                       foreground='black',
                       borderwidth=0,
                       focuscolor=COLORS['accent'])
        
        style.map('Modern.TButton',
                 background=[('active', COLORS['primary']), ('pressed', COLORS['dark'])])
        
        # Risk badge styles
        style.configure('Risk.Clean.TLabel',
                       background=COLORS['success'],
                       foreground='white',
                       padding=(8, 4),
                       font=('Segoe UI', 9, 'bold'))
        
        style.configure('Risk.Suspicious.TLabel',
                       background=COLORS['warning'],
                       foreground='white',
                       padding=(8, 4),
                       font=('Segoe UI', 9, 'bold'))
        
        style.configure('Risk.Malicious.TLabel',
                       background=COLORS['danger'],
                       foreground='white',
                       padding=(8, 4),
                       font=('Segoe UI', 9, 'bold'))
        
        # Progress bar style
        style.configure('Modern.Horizontal.TProgressbar',
                       background=COLORS['accent'],
                       troughcolor=COLORS['light'],
                       borderwidth=0)

    def _build_ui(self):
        # Main container with modern layout
        main_container = ttk.Frame(self)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Header section
        self._build_header(main_container)
        
        # Control panel
        self._build_control_panel(main_container)
        
        # Results area - full width table
        results_frame = ttk.Frame(main_container)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(15, 0))
        
        self._build_file_table(results_frame)
        
        # Status bar
        self._build_status_bar(main_container)

    def _build_header(self, parent):
        header = ttk.Frame(parent)
        header.pack(fill=tk.X, pady=(0, 20))
        
        # Title section
        title_frame = ttk.Frame(header)
        title_frame.pack(fill=tk.X)
        
        title = ttk.Label(title_frame, 
                         text=APP_NAME, 
                         font=('Segoe UI', 24, 'bold'),
                         foreground=COLORS['text'])  # Black text
        title.pack(side=tk.LEFT)
        
        version = ttk.Label(title_frame,
                           text=f"v{APP_VERSION}",
                           font=('Segoe UI', 12),
                           foreground=COLORS['text'])  # Black text
        version.pack(side=tk.LEFT, padx=(10, 0), pady=(8, 0))
        
        subtitle = ttk.Label(title_frame,
                            text="Professional Malware Scanner",
                            font=('Segoe UI', 11),
                            foreground=COLORS['text'])  # Black text
        subtitle.pack(side=tk.LEFT, padx=(15, 0), pady=(8, 0))
        
        # Action buttons
        action_frame = ttk.Frame(header)
        action_frame.pack(side=tk.RIGHT)
        
        ModernButton(action_frame, text="About", command=self._show_about).pack(side=tk.LEFT, padx=(5, 0))
        ModernButton(action_frame, text="Help", command=self._show_help).pack(side=tk.LEFT, padx=5)

    def _build_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Scan Controls", padding=15)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Directory selection
        dir_frame = ttk.Frame(control_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="Scan Directory:", font=('Segoe UI', 10, 'bold'), foreground=COLORS['text']).pack(side=tk.LEFT)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ModernEntry(dir_frame, textvariable=self.dir_var, width=60)
        self.dir_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        ModernButton(dir_frame, text="Browse…", command=self._choose_dir).pack(side=tk.LEFT, padx=(5, 0))
        
        # Action buttons
        action_frame = ttk.Frame(control_frame)
        action_frame.pack(fill=tk.X)
        
        self.scan_btn = ModernButton(action_frame, text="▶ Start Scan", command=self._scan)
        self.scan_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_btn = ModernButton(action_frame, text="⏹ Stop", command=self._stop, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ModernButton(action_frame, text="📊 Export CSV", command=self._export_csv).pack(side=tk.LEFT, padx=(0, 10))
        ModernButton(action_frame, text="🗑️ Clear Results", command=self._clear_results).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ModernProgressbar(control_frame, mode="determinate")
        self.progress.pack(fill=tk.X, pady=(10, 0))

    def _build_file_table(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Table header
        header_frame = ttk.Frame(frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header_frame, text="Scan Results", font=('Segoe UI', 12, 'bold'), foreground=COLORS['text']).pack(side=tk.LEFT)
        
        # Treeview with scrollbar
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("verdict", "risk", "file", "size", "modified")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Configure columns
        self.tree.heading("verdict", text="Status")
        self.tree.heading("risk", text="Risk Score")
        self.tree.heading("file", text="File Path")
        self.tree.heading("size", text="Size")
        self.tree.heading("modified", text="Modified")
        
        self.tree.column("verdict", width=120, anchor=tk.CENTER)
        self.tree.column("risk", width=80, anchor=tk.CENTER)
        self.tree.column("file", width=600)
        self.tree.column("size", width=100, anchor=tk.E)
        self.tree.column("modified", width=120, anchor=tk.CENTER)
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind events
        self.tree.bind("<Button-3>", self._popup_menu)

    def _build_status_bar(self, parent):
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, border=1)
        status_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Left status
        self.status_var = tk.StringVar(value="Ready to scan")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, font=('Segoe UI', 9), foreground=COLORS['text'])
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Right stats
        stats_frame = ttk.Frame(status_frame)
        stats_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.stats_var = tk.StringVar(value="Total: 0 | Scanned: 0 | Suspicious: 0 | Malicious: 0")
        stats_label = ttk.Label(stats_frame, textvariable=self.stats_var, font=('Segoe UI', 9), foreground=COLORS['text'])
        stats_label.pack(side=tk.RIGHT)

    # --- Event handlers ---
    def _show_about(self):
        about_text = f"""{APP_NAME} {APP_VERSION}

A professional educational malware scanner with modern UI.

Features:
• Signature-based detection (MD5/SHA-256)
• Advanced heuristic analysis
• Real-time scanning with progress monitoring
• Professional quarantine management
• Detailed CSV reporting
"""

        messagebox.showinfo("About", about_text)

    def _show_help(self):
        help_text = """Quick Help:

1. Select a directory to scan
2. Click 'Start Scan' to begin
3. Review results in the table
4. Use right-click menu for actions

Right-click options:
• Quarantine suspicious files
• Reveal in file explorer
• Copy file hashes"""

        messagebox.showinfo("Help", help_text)

    def _choose_dir(self):
        d = filedialog.askdirectory(title="Choose a folder to scan")
        if d:
            self.selected_dir = Path(d)
            self.dir_var.set(str(self.selected_dir))

    def _scan(self):
        if not self.dir_var.get().strip():
            messagebox.showwarning(APP_NAME, "Please choose a folder to scan.")
            return
        root = Path(self.dir_var.get())
        if not root.exists():
            messagebox.showerror(APP_NAME, "Folder does not exist.")
            return

        self.tree.delete(*self.tree.get_children())
        self.results.clear()
        self.stop_event.clear()
        self.scan_stats = {'total': 0, 'scanned': 0, 'suspicious': 0, 'malicious': 0, 'clean': 0}

        files = iter_files(root)
        total = len(files)
        if total == 0:
            messagebox.showinfo(APP_NAME, "No files found to scan.")
            return

        self.scan_stats['total'] = total
        self._update_stats()
        
        self.progress.configure(maximum=total, value=0)
        self.status_var.set(f"Scanning {total} files…")
        self.scan_btn.config(state='disabled')
        self.stop_btn.config(state='normal')

        self.executor = ThreadPoolExecutor(max_workers=min(os.cpu_count() or 4, 8))

        self._futures = []
        for p in files:
            if self.stop_event.is_set():
                break
            self._futures.append(self.executor.submit(scan_file, p))

        self.master.after(50, self._poll_futures)

    def _poll_futures(self):
        if not hasattr(self, "_futures"):
            return
        
        done = [f for f in list(self._futures) if f.done()]
        for f in done:
            try:
                res = f.result()
            except Exception as e:
                res = None
            self._futures.remove(f)
            if res:
                self._add_result(res)
                self.scan_stats['scanned'] += 1
                if res.verdict == "Suspicious":
                    self.scan_stats['suspicious'] += 1
                elif res.verdict == "Malicious":
                    self.scan_stats['malicious'] += 1
                else:
                    self.scan_stats['clean'] += 1
                
                self.progress.step(1)
                self._update_stats()

        if self._futures and not self.stop_event.is_set():
            self.master.after(50, self._poll_futures)
        else:
            self._finish_scan()

    def _finish_scan(self):
        self.progress.stop()
        self.status_var.set("Scan complete.")
        self.scan_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        if self.executor:
            self.executor.shutdown(wait=False, cancel_futures=True)
            self.executor = None
        
        # Show scan completion popup
        self._show_scan_report()

    def _show_scan_report(self):
        stats = self.scan_stats
        report_text = f"""Scan Completed Successfully!

📊 Scan Summary:
• Total Files: {stats['total']}
• Files Scanned: {stats['scanned']}
• Clean Files: {stats['clean']}
• Suspicious Files: {stats['suspicious']}
• Malicious Files: {stats['malicious']}

File Health Status:
✅ Clean: {stats['clean']} files
⚠️ Suspicious: {stats['suspicious']} files
❌ Malicious: {stats['malicious']} files

Would you like to scan another folder?"""

        result = messagebox.askyesno("Scan Complete", report_text, 
                                   detail="Click 'Yes' to choose another folder, or 'No' to continue with current results.")
        
        if result:
            self._choose_dir()

    def _stop(self):
        self.stop_event.set()
        self._finish_scan()

    def _add_result(self, res: ScanResult):
        verdict = res.verdict
        risk = res.risk
        size_fmt = format_size(res.size) if res.size else "—"
        
        try:
            modified = datetime.fromtimestamp(res.path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        except:
            modified = "—"
        
        item = self.tree.insert("", tk.END, iid=str(res.path), 
                               values=(verdict, risk, str(res.path), size_fmt, modified))
        
        # Color code based on risk
        if verdict == "Malicious":
            self.tree.set(item, "verdict", "🔴 MALICIOUS")
        elif verdict == "Suspicious":
            self.tree.set(item, "verdict", "🟡 SUSPICIOUS")
        else:
            self.tree.set(item, "verdict", "🟢 CLEAN")

    def _update_stats(self):
        stats = self.scan_stats
        self.stats_var.set(f"Total: {stats['total']} | Scanned: {stats['scanned']} | "
                          f"Suspicious: {stats['suspicious']} | Malicious: {stats['malicious']}")

    def _selected_item(self) -> Optional[ScanResult]:
        sel = self.tree.selection()
        if not sel:
            return None
        path = Path(sel[0])
        for r in self.results:
            if r.path == path:
                return r
        return None

    def _popup_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            self.tree.selection_set(iid)
            try:
                menu = tk.Menu(self, tearoff=0)
                menu.add_command(label="Quarantine", command=self._quarantine_selected)
                menu.add_command(label="Reveal in folder", command=self._reveal_selected)
                menu.add_separator()
                menu.add_command(label="Copy MD5", command=lambda: self._copy_selected_hash("md5"))
                menu.add_command(label="Copy SHA256", command=lambda: self._copy_selected_hash("sha256"))
                menu.tk_popup(event.x_root, event.y_root)
            finally:
                menu.grab_release()

    def _quarantine_selected(self):
        res = self._selected_item()
        if not res:
            return
        if res.verdict == "Clean":
            if not messagebox.askyesno(APP_NAME, "File seems clean. Quarantine anyway?"):
                return
        qpath = quarantine_file(res.path)
        if qpath:
            messagebox.showinfo(APP_NAME, f"Moved to quarantine:\n{qpath}")
            self.tree.item(str(res.path), values=("QUARANTINED", res.risk, f"{res.path} (quarantined)", 
                                                 format_size(res.size), "—"))

    def _reveal_selected(self):
        res = self._selected_item()
        if not res:
            return
        p = res.path
        try:
            if sys.platform.startswith("win"):
                os.startfile(os.path.dirname(p))
            elif sys.platform == "darwin":
                os.system(f"open '{os.path.dirname(p)}'")
            else:
                os.system(f"xdg-open '{os.path.dirname(p)}'")
        except Exception:
            messagebox.showerror(APP_NAME, "Unable to open folder.")

    def _copy_selected_hash(self, kind: str = "md5"):
        res = self._selected_item()
        if not res:
            return
        value = res.md5 if kind == "md5" else res.sha256
        self.master.clipboard_clear()
        self.master.clipboard_append(value)
        self.status_var.set(f"Copied {kind.upper()} to clipboard.")

    def _export_csv(self):
        if not self.results:
            messagebox.showwarning(APP_NAME, "No results to export.")
            return
        ensure_dirs()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = REPORTS_DIR / f"gt_scanner_report_{ts}.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Verdict", "Risk", "File", "Size(bytes)", "MD5", "SHA256", "Detections"])
            for r in self.results:
                det_text = " | ".join(f"[{d.kind}] {d.message}" for d in r.detections)
                w.writerow([r.verdict, r.risk, str(r.path), r.size, r.md5, r.sha256, det_text])
        messagebox.showinfo(APP_NAME, f"CSV saved to:\n{path}")

    def _clear_results(self):
        self.tree.delete(*self.tree.get_children())
        self.results.clear()
        self.scan_stats = {'total': 0, 'scanned': 0, 'suspicious': 0, 'malicious': 0, 'clean': 0}
        self._update_stats()
        self.status_var.set("Results cleared")

# --- Main -----------------------------------------------------------------------

def main():
    root = tk.Tk()
    app = GTScannerApp(root)
    
    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main()
