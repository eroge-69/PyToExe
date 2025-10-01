#!/usr/bin/env python3
"""Simple GUI for updating toc_version_number.pot

Features:
- Text entry to set the major.minor version (default: 1.0)
- File chooser for the .pot file (defaults to localization path used by the CLI script)
- Preview (dry-run) and Apply buttons
- Scrollable output area that shows OLD/NEW msgid and status messages
"""
from __future__ import annotations
import datetime as dt
import re
from pathlib import Path
import shutil
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox


if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    APP_ROOT = Path(sys.executable).parent
else:
    APP_ROOT = Path(__file__).parent

DEFAULT_REL = APP_ROOT / "localizations" / "default" / "interface" / "text" / "toc_version_number.pot"
ROOT_NAME = APP_ROOT.name


def read_mod_name(root: Path) -> str | None:
    """Try to parse mod.info in the root folder and return the {name ...} value, or None."""
    modinfo = root / 'mod.info'
    if not modinfo.exists():
        return None
    try:
        text = modinfo.read_text(encoding='utf-8')
    except Exception:
        try:
            text = modinfo.read_text(encoding='utf-8-sig')
        except Exception:
            return None
    # naive parse: look for {name "..."}
    m = re.search(r'\{name\s+"([^"]+)"\}', text)
    if m:
        return m.group(1)
    return None


def prepare_update(pot_path: Path, version: str) -> tuple[str | None, str | None, str]:
    """Return (old_block, new_block, message). old_block/new_block will be None on errors."""
    if not pot_path.exists():
        return None, None, f"[ERROR] Not found: {pot_path}"

    today = dt.date.today()
    build = f"{today:%m%d%y}"

    try:
        text = pot_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = pot_path.read_text(encoding="utf-8-sig")

    block_pattern = re.compile(
        r'(msgctxt\s+"version_short_string"\s+msgid\s*")(?P<body>.*?)(?=\nmsgstr\s*")',
        flags=re.DOTALL,
    )

    m = block_pattern.search(text)
    if not m:
        return None, None, "[ERROR] No msgid Version string found to update."

    body = m.group('body')

    marker = '<c(FFD700)>TOC - Conquest Expansion Patch - '
    idx = body.find(marker)
    if idx == -1:
        marker = 'TOC - Conquest Expansion Patch - '
        idx = body.find(marker)

    if idx == -1:
        new_body = re.sub(r'\$?\d+\.\d+\.\d{6}', f'Version {version}.{build}', body)
    else:
        prefix = body[: idx + len(marker)]
        new_body = prefix + f'Version {version}.{build}'

    old_block = m.group(0)
    new_block = m.group(1) + new_body + '"'
    return old_block, new_block, f"[OK] Prepared Version {version}.{build}"


def apply_update(pot_path: Path, new_text: str) -> tuple[bool, str]:
    try:
        stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = pot_path.with_suffix(pot_path.suffix + f".{stamp}.bak")
        shutil.copy2(pot_path, backup_path)
        pot_path.write_text(new_text, encoding="utf-8")
        return True, f"[OK] Backup saved: {backup_path}\n[OK] Wrote: {pot_path}"
    except Exception as exc:
        return False, f"[ERROR] Writing file failed: {exc}"


class App(ttk.Frame):
    def __init__(self, master: tk.Tk):
        super().__init__(master)
        self.master = master
        master.title("Update TOC Version")
        master.geometry("683x360")
        # Try to set a custom window icon (png or ico) located next to the script/exe
        try:
            png_icon = APP_ROOT / 'toc_icon_black_title.png'
            png_icon2 = APP_ROOT / 'toc_icon_white_title.png'
            ico_icon = APP_ROOT / 'toc_icon_white_title.ico'
            chosen = None
            if png_icon.exists():
                chosen = png_icon
            elif png_icon2.exists():
                chosen = png_icon2
            elif ico_icon.exists():
                chosen = ico_icon

            if chosen:
                # PhotoImage supports PNG; for ICO some Tk builds accept it via PhotoImage too
                img = tk.PhotoImage(file=str(chosen))
                master.iconphoto(True, img)
        except Exception:
            # ignore if icon can't be set
            pass

        # Dark theme colors (VS Code-like)
        bg = '#1e1e1e'           # main background
        panel = '#252526'        # panel/background for frames
        entry_bg = '#3c3c3c'      # entry/background
        fg = '#d4d4d4'           # foreground text
        accent = '#007acc'       # button accent (blue)

        # Configure ttk style for a dark theme
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('TFrame', background=panel)
        style.configure('TLabel', background=panel, foreground=fg)
        style.configure('TEntry', fieldbackground=entry_bg, background=entry_bg, foreground=fg)
        style.map('TEntry', fieldbackground=[('disabled', entry_bg)])
        style.configure('TButton', background=panel, foreground=fg)
        style.configure('Accent.TButton', background=accent, foreground='white')
        style.configure('TScrollbar', background=panel)
        style.configure('Status.TLabel', background=panel, foreground=fg)

        master.configure(background=bg)
        self.grid(sticky="nsew")

        # Controls frame
        frm = ttk.Frame(self)
        frm.grid(row=0, column=0, sticky="ew", padx=8, pady=8)

        ttk.Label(frm, text="Version:").grid(row=0, column=0, sticky="w")
        self.version_var = tk.StringVar(value="1.0")
        self.version_entry = ttk.Entry(frm, width=12, textvariable=self.version_var)
        self.version_entry.grid(row=0, column=1, sticky="w", padx=(4, 12))

        ttk.Label(frm, text="POT file:").grid(row=0, column=2, sticky="w")
        self.path_var = tk.StringVar(value=str(DEFAULT_REL))
        self.path_entry = ttk.Entry(frm, width=60, textvariable=self.path_var)
        self.path_entry.grid(row=0, column=3, sticky="ew", padx=(4, 4))
        ttk.Button(frm, text="Browse...", command=self.browse).grid(row=0, column=4, sticky="w")

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=1, column=0, sticky="w", padx=8)
        ttk.Button(btn_frame, text="Preview", command=self.preview, style='Accent.TButton').grid(row=0, column=0, padx=4)
        ttk.Button(btn_frame, text="Apply", command=self.apply, style='Accent.TButton').grid(row=0, column=1, padx=4)
        ttk.Button(btn_frame, text="Quit", command=master.quit).grid(row=0, column=2, padx=4)

        # Output text
        self.text = tk.Text(self, wrap="word", height=16, bg='#1e1e1e', fg='#d4d4d4', insertbackground='#d4d4d4')
        self.text.grid(row=2, column=0, sticky="nsew", padx=8, pady=(4, 8))
        scrollbar = ttk.Scrollbar(self, command=self.text.yview)
        scrollbar.grid(row=2, column=1, sticky="nsw", pady=(4, 8))
        self.text.configure(yscrollcommand=scrollbar.set)

        # Configure resizing
        self.master.rowconfigure(2, weight=1)
        self.master.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Status bar
        name0 = Path(self.path_var.get()).name
        mod_name = read_mod_name(APP_ROOT) or ''
        suffix = f" — {mod_name}" if mod_name else ''
        self.status_var = tk.StringVar(value=f"Loaded: {name0} from {ROOT_NAME}{suffix}")
        status = ttk.Label(self, textvariable=self.status_var, style='Status.TLabel', anchor='w')
        status.grid(row=3, column=0, columnspan=2, sticky='ew', padx=8, pady=(0,8))
        self.rowconfigure(3, weight=0)

    def log(self, *lines: str) -> None:
        for line in lines:
            self.text.insert("end", line + "\n")
        self.text.see("end")

    def update_status(self) -> None:
        path = Path(self.path_var.get())
        name = path.name if path.name else str(path)
        mod_name = read_mod_name(APP_ROOT) or ''
        suffix = f" — {mod_name}" if mod_name else ''
        if path.exists():
            self.status_var.set(f"Loaded: {name} from {ROOT_NAME}{suffix}")
        else:
            self.status_var.set(f"Loaded: {name} from {ROOT_NAME}{suffix} (not found)")

    def browse(self) -> None:
        path = filedialog.askopenfilename(title="Select toc_version_number.pot",
                                          initialdir=str(APP_ROOT),
                                          filetypes=[("POT files", "*.pot"), ("All files", "*")])
        if path:
            self.path_var.set(path)
            self.update_status()

    def preview(self) -> None:
        self.text.delete("1.0", "end")
        pot = Path(self.path_var.get())
        self.update_status()
        version = self.version_var.get().strip()
        old_block, new_block, msg = prepare_update(pot, version)
        self.log(msg)
        if old_block is None:
            return
        self.log("\nOLD MSGID:")
        self.log(old_block)
        self.log("\nNEW MSGID:")
        self.log(new_block)

    def apply(self) -> None:
        pot = Path(self.path_var.get())
        self.update_status()
        version = self.version_var.get().strip()
        old_block, new_block, msg = prepare_update(pot, version)
        self.text.delete("1.0", "end")
        self.log(msg)
        if old_block is None:
            return
        # build new full text by replacing the block
        try:
            text = pot.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = pot.read_text(encoding="utf-8-sig")
        new_text = re.sub(r'(msgctxt\s+"version_short_string"\s+msgid\s*").*?(?=\nmsgstr\s*")',
                          lambda m: m.group(1) + new_block[len(m.group(1)):], text, flags=re.DOTALL)
        ok, writemsg = apply_update(pot, new_text)
        self.log(writemsg)
        if ok:
            messagebox.showinfo("Done", "Update applied and backup created.")


def main() -> None:
    root = tk.Tk()
    app = App(root)
    app.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
