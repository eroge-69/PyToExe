#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Robux Code Checker - GUI
Full-featured Tkinter application to validate code format and check duplicates
against a persistent history. Can export results to CSV and manage history.

Build to .exe (Windows) with:
    pip install pyinstaller
    pyinstaller --onefile --noconsole robux_checker_gui.py

The executable will be created at: dist/robux_checker_gui.exe
"""

import csv
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Robux Code Checker"
VERSION = "1.0.0"

FORMAT_RE = re.compile(r'^[A-Z0-9]{5}-[A-Z0-9]{5}-[A-Z0-9]{5}$')

# Default history path: user home, hidden folder
DEFAULT_HISTORY_DIR = Path.home() / ".robux_code_checker"
DEFAULT_HISTORY_FILE = DEFAULT_HISTORY_DIR / "code_history.json"


def ensure_history_dir(path: Path) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass


def load_history(path: Path) -> Set[str]:
    if not path.exists():
        return set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        codes = data.get("codes", [])
        return set(map(str, codes))
    except Exception:
        return set()


def save_history(path: Path, history: Set[str]) -> None:
    ensure_history_dir(path)
    data = {
        "updated_at": datetime.utcnow().isoformat() + "Z",
        "codes": sorted(history),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_codes(raw: str) -> List[str]:
    # Split by whitespace or commas; uppercase and strip
    tokens = re.split(r"[\s,]+", raw.strip())
    return [t.upper() for t in tokens if t.strip()]


def analyze_codes(codes: List[str], history: Set[str]) -> Dict[str, List[str]]:
    invalid_format: List[str] = []
    dup_in_batch: Set[str] = set()
    seen: Set[str] = set()

    for c in codes:
        if not FORMAT_RE.match(c):
            invalid_format.append(c)
        if c in seen:
            dup_in_batch.add(c)
        seen.add(c)

    valid_codes = [c for c in codes if c not in invalid_format]
    dup_vs_history = [c for c in valid_codes if c in history]
    unique_new = [c for c in valid_codes if c not in history and c not in dup_in_batch]

    return {
        "invalid_format": invalid_format,
        "duplicates_in_batch": sorted(dup_in_batch),
        "duplicates_vs_history": sorted(set(dup_vs_history)),
        "unique_new": sorted(set(unique_new)),
    }


class RobuxCheckerGUI(tk.Tk):
    def __init.subclass__(cls) -> None:
        return super().__init_subclass__()

    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME} v{VERSION}")
        self.geometry("980x700")
        self.minsize(900, 600)

        # State
        self.history_path: Path = DEFAULT_HISTORY_FILE
        self.history: Set[str] = load_history(self.history_path)

        self._build_menu()
        self._build_widgets()
        self._refresh_statusbar()

    # --------------- UI Construction -----------------
    def _build_menu(self):
        menubar = tk.Menu(self)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open Codes File...", command=self._load_codes_file)
        filemenu.add_command(label="Save Results to CSV...", command=self._export_csv)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        historymenu = tk.Menu(menubar, tearoff=0)
        historymenu.add_command(label="Set History File...", command=self._choose_history_file)
        historymenu.add_command(label="Open History Location...", command=self._open_history_location)
        historymenu.add_command(label="Reset History (Clear All)", command=self._reset_history)
        menubar.add_cascade(label="History", menu=historymenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About", command=self._about)
        menubar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=menubar)

    def _build_widgets(self):
        top = ttk.Frame(self, padding=10)
        top.pack(fill=tk.BOTH, expand=True)

        # Input Section
        input_frame = ttk.LabelFrame(top, text="Input Codes", padding=10)
        input_frame.pack(fill=tk.BOTH, expand=False)

        input_hint = ttk.Label(
            input_frame,
            text="Paste codes below (whitespace/comma separated). Example format: XXXXX-XXXXX-XXXXX",
        )
        input_hint.pack(anchor="w", pady=(0, 6))

        self.text = tk.Text(input_frame, height=8, wrap="word")
        self.text.pack(fill=tk.BOTH, expand=True)

        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X, pady=8)

        ttk.Button(buttons_frame, text="Load File...", command=self._load_codes_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(buttons_frame, text="Clear", command=lambda: self.text.delete("1.0", tk.END)).pack(side=tk.LEFT, padx=6)
        self.save_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(buttons_frame, text="Save unique valid codes to history after check", variable=self.save_var).pack(side=tk.LEFT, padx=12)
        ttk.Button(buttons_frame, text="Check Codes", command=self._check_codes, style="Accent.TButton").pack(side=tk.RIGHT)

        # Results Section
        results_frame = ttk.LabelFrame(top, text="Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        columns = ("code", "status", "notes")
        self.tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=12)
        self.tree.heading("code", text="Code")
        self.tree.heading("status", text="Status")
        self.tree.heading("notes", text="Notes")
        self.tree.column("code", width=260, anchor="w")
        self.tree.column("status", width=180, anchor="center")
        self.tree.column("notes", width=400, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Summary badges
        summary = ttk.Frame(results_frame)
        summary.pack(fill=tk.X, pady=(8, 0))

        self.lbl_total = ttk.Label(summary, text="Total: 0")
        self.lbl_invalid = ttk.Label(summary, text="Invalid: 0")
        self.lbl_dup_batch = ttk.Label(summary, text="Dup (Batch): 0")
        self.lbl_dup_hist = ttk.Label(summary, text="Dup (History): 0")
        self.lbl_unique = ttk.Label(summary, text="Unique New: 0")

        for w in (self.lbl_total, self.lbl_invalid, self.lbl_dup_batch, self.lbl_dup_hist, self.lbl_unique):
            w.pack(side=tk.LEFT, padx=12)

        # Bottom toolbar
        bottom = ttk.Frame(self, padding=(10, 0, 10, 10))
        bottom.pack(fill=tk.X, side=tk.BOTTOM)

        ttk.Button(bottom, text="Save Results to CSV...", command=self._export_csv).pack(side=tk.LEFT)
        ttk.Button(bottom, text="Open History Location...", command=self._open_history_location).pack(side=tk.LEFT, padx=8)
        ttk.Button(bottom, text="Reset History", command=self._reset_history).pack(side=tk.LEFT, padx=8)

        self.status = ttk.Label(bottom, text="Ready", anchor="w")
        self.status.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        # Style tweaks
        style = ttk.Style(self)
        try:
            # On Windows, use clam for nicer look if available
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    # --------------- Actions -----------------
    def _load_codes_file(self):
        path = filedialog.askopenfilename(
            title="Open Codes File",
            filetypes=[("Text files", "*.txt *.csv *.log *.lst"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            # Append to existing text content
            existing = self.text.get("1.0", tk.END).strip()
            combined = (existing + "\n" + content).strip() if existing else content
            self.text.delete("1.0", tk.END)
            self.text.insert("1.0", combined)
            self._set_status(f"Loaded codes from: {path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to read file:\n{e}")

    def _check_codes(self):
        raw = self.text.get("1.0", tk.END)
        codes = parse_codes(raw)
        if not codes:
            messagebox.showinfo(APP_NAME, "No codes to check. Paste or load some codes first.")
            return

        result = analyze_codes(codes, self.history)

        # Clear tree
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Populate results
        def add_row(code: str, status: str, notes: str):
            self.tree.insert("", tk.END, values=(code, status, notes))

        # Build notes map for batch duplicates (count occurrences)
        from collections import Counter
        counts = Counter(codes)

        # Invalid format
        for c in result["invalid_format"]:
            add_row(c, "invalid_format ❌", "Does not match XXXXX-XXXXX-XXXXX")

        # Duplicates within batch
        for c in result["duplicates_in_batch"]:
            add_row(c, "duplicate_in_batch ⚠", f"Appears {counts[c]} times in this input")

        # Duplicates vs history
        for c in result["duplicates_vs_history"]:
            add_row(c, "duplicate_in_history ⚠", "Already exists in saved history")

        # Unique new
        for c in result["unique_new"]:
            add_row(c, "unique ✅", "Valid format and not previously used")

        # Update summary labels
        self.lbl_total.config(text=f"Total: {len(codes)}")
        self.lbl_invalid.config(text=f"Invalid: {len(result['invalid_format'])}")
        self.lbl_dup_batch.config(text=f"Dup (Batch): {len(result['duplicates_in_batch'])}")
        self.lbl_dup_hist.config(text=f"Dup (History): {len(result['duplicates_vs_history'])}")
        self.lbl_unique.config(text=f"Unique New: {len(result['unique_new'])}")

        # Save unique valid codes to history, if toggled
        if self.save_var.get() and result["unique_new"]:
            updated = set(self.history)
            updated.update(result["unique_new"])
            try:
                save_history(self.history_path, updated)
                self.history = updated
                self._set_status(f"History updated: +{len(result['unique_new'])} codes")
            except Exception as e:
                messagebox.showerror(APP_NAME, f"Failed to save history:\n{e}")
        else:
            self._set_status("Check complete")

    def _export_csv(self):
        path = filedialog.asksaveasfilename(
            title="Save Results CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"robux_check_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["code", "status", "notes"])
                for iid in self.tree.get_children():
                    row = self.tree.item(iid, "values")
                    writer.writerow(row)
            self._set_status(f"CSV saved: {path}")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to save CSV:\n{e}")

    def _choose_history_file(self):
        path = filedialog.asksaveasfilename(
            title="Set History File",
            defaultextension=".json",
            initialfile="code_history.json",
            filetypes=[("JSON files", "*.json")],
        )
        if not path:
            return
        new_path = Path(path)
        if not new_path.exists():
            # Initialize empty
            try:
                save_history(new_path, set())
            except Exception as e:
                messagebox.showerror(APP_NAME, f"Failed to initialize history:\n{e}")
                return
        self.history_path = new_path
        self.history = load_history(self.history_path)
        self._set_status(f"History file set to: {self.history_path}")

    def _open_history_location(self):
        try:
            ensure_history_dir(self.history_path)
            folder = self.history_path.parent
            folder.mkdir(parents=True, exist_ok=True)
            if sys.platform == "win32":
                os.startfile(str(folder))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{folder}"')
            else:
                os.system(f'xdg-open "{folder}"')
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to open folder:\n{e}")

    def _reset_history(self):
        if not messagebox.askyesno(APP_NAME, "This will clear ALL saved codes in history.\nContinue?"):
            return
        try:
            save_history(self.history_path, set())
            self.history = set()
            self._set_status("History cleared")
        except Exception as e:
            messagebox.showerror(APP_NAME, f"Failed to reset history:\n{e}")

    def _about(self):
        messagebox.showinfo(
            f"About {APP_NAME}",
            f"{APP_NAME} v{VERSION}\n\n"
            "• Validates format XXXXX-XXXXX-XXXXX\n"
            "• Finds duplicates (in batch & vs history)\n"
            "• Exports results to CSV\n"
            "• Saves unique valid codes to history\n\n"
            "Build to .exe with PyInstaller:\n"
            "  pyinstaller --onefile --noconsole robux_checker_gui.py"
        )

    def _refresh_statusbar(self):
        self._set_status(f"History: {self.history_path}  |  Stored codes: {len(self.history)}")

    def _set_status(self, text: str):
        self.status.config(text=text)


def main():
    # Create default history file if missing
    if not DEFAULT_HISTORY_FILE.exists():
        ensure_history_dir(DEFAULT_HISTORY_FILE)
        save_history(DEFAULT_HISTORY_FILE, set())

    app = RobuxCheckerGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
