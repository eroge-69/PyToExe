#!/usr/bin/env python3
"""
simple_av_gui_online.py

A small, self-contained GUI-based educational "antivirus" designed to be
compatible with online converters like https://py2exe.com/convert.

Notes:
- Uses only Python standard library (tkinter, hashlib, re, json, os, threading).
- No network calls; does not modify files except when writing the scan_log.json
  file into the current working directory or when the user chooses to save the log.
- Intended for educational/testing use only. It is NOT production antivirus.

Usage after converting to EXE:
- Run the exe, click "Select Folder", then "Start Scan".
- Findings are shown in the list. Click "Save Log" to write JSON log file.

"""

import os
import hashlib
import json
import re
import threading
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ---------- Simple signature database (edit as needed) ----------
# Only standard-library types (set/dict) so the converter won't fail.
BAD_HASHES = {
    # example placeholder (not a real malicious hash)
    "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
}

# patterns are compiled as bytes-patterns for scanning file bytes quickly
BAD_PATTERNS = {
    "example_malware_text": re.compile(b"evil_function", re.IGNORECASE),
    "suspicious_keyword": re.compile(b"ransom", re.IGNORECASE),
}

READ_LIMIT = 2 * 1024 * 1024  # read up to 2 MB per file for speed/safety


def sha256_of_file(path):
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:
        return None


def scan_file(path):
    """Scan a single file for bad hashes or patterns. Return list of findings."""
    findings = []
    file_hash = sha256_of_file(path)
    if file_hash and file_hash in BAD_HASHES:
        findings.append({"type": "hash", "value": file_hash})

    try:
        with open(path, "rb") as f:
            data = f.read(READ_LIMIT)
    except Exception:
        return findings

    for name, pattern in BAD_PATTERNS.items():
        try:
            if pattern.search(data):
                findings.append({"type": "pattern", "name": name})
        except Exception:
            continue

    return findings


class ScannerThread(threading.Thread):
    def __init__(self, folder, result_callback, progress_callback, stop_event):
        super().__init__(daemon=True)
        self.folder = folder
        self.result_callback = result_callback
        self.progress_callback = progress_callback
        self.stop_event = stop_event

    def run(self):
        results = []
        total_files = 0
        # quick pre-count (non-recursive speed safe option) but we will count while scanning
        for root, dirs, files in os.walk(self.folder):
            total_files += len(files)

        scanned = 0
        for root, dirs, files in os.walk(self.folder):
            if self.stop_event.is_set():
                break
            for fname in files:
                if self.stop_event.is_set():
                    break
                path = os.path.join(root, fname)
                scanned += 1
                try:
                    findings = scan_file(path)
                    if findings:
                        entry = {
                            "file": path,
                            "findings": findings,
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                        }
                        results.append(entry)
                        self.result_callback(entry)
                except Exception:
                    # ignore unreadable files
                    pass
                # update progress
                if total_files > 0:
                    percent = int((scanned / total_files) * 100)
                else:
                    percent = 0
                self.progress_callback(scanned, total_files, percent)
        # final callback with full results
        # (the gui stores entries as they come; we don't need to return anything)
        return


class AVGUI:
    def __init__(self, root):
        self.root = root
        root.title("Simple AV (Educational)")
        root.resizable(False, False)

        self.folder = tk.StringVar()
        self.status_var = tk.StringVar(value="Idle")
        self.progress_var = tk.IntVar(value=0)

        self.results = []
        self.scan_thread = None
        self.stop_event = threading.Event()

        # UI layout
        frm = ttk.Frame(root, padding=10)
        frm.grid()

        path_row = ttk.Frame(frm)
        path_row.grid(row=0, column=0, sticky="w", pady=(0, 8))

        ttk.Label(path_row, text="Folder to scan:").grid(row=0, column=0, sticky="w")
        self.path_entry = ttk.Entry(path_row, width=50, textvariable=self.folder)
        self.path_entry.grid(row=0, column=1, padx=(8, 8))
        ttk.Button(path_row, text="Select Folder", command=self.select_folder).grid(row=0, column=2)

        btn_row = ttk.Frame(frm)
        btn_row.grid(row=1, column=0, sticky="w", pady=(0, 8))
        self.start_btn = ttk.Button(btn_row, text="Start Scan", command=self.start_scan)
        self.start_btn.grid(row=0, column=0)
        self.stop_btn = ttk.Button(btn_row, text="Stop Scan", command=self.stop_scan, state="disabled")
        self.stop_btn.grid(row=0, column=1, padx=(8, 0))
        ttk.Button(btn_row, text="Save Log", command=self.save_log).grid(row=0, column=2, padx=(8, 0))

        status_row = ttk.Frame(frm)
        status_row.grid(row=2, column=0, sticky="w", pady=(0, 8))
        ttk.Label(status_row, textvariable=self.status_var).grid(row=0, column=0, sticky="w")
        self.progress = ttk.Progressbar(status_row, length=300, variable=self.progress_var)
        self.progress.grid(row=0, column=1, padx=(8, 0))

        list_row = ttk.Frame(frm)
        list_row.grid(row=3, column=0, pady=(8, 0))
        self.listbox = tk.Listbox(list_row, width=90, height=12)
        self.listbox.grid(row=0, column=0)
        sb = ttk.Scrollbar(list_row, orient="vertical", command=self.listbox.yview)
        sb.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=sb.set)

        # double click to show details
        self.listbox.bind('<Double-1>', self.show_details)

    def select_folder(self):
        chosen = filedialog.askdirectory()
        if chosen:
            self.folder.set(chosen)

    def start_scan(self):
        folder = self.folder.get().strip()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder to scan.")
            return
        # reset
        self.results = []
        self.listbox.delete(0, tk.END)
        self.status_var.set("Scanning...")
        self.progress_var.set(0)
        self.stop_event.clear()
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")

        # start background thread
        self.scan_thread = ScannerThread(folder, self.on_result, self.on_progress, self.stop_event)
        self.scan_thread.start()
        # poll thread status
        self.root.after(200, self.check_thread)

    def stop_scan(self):
        if messagebox.askyesno("Stop", "Stop the ongoing scan?"):
            self.stop_event.set()
            self.status_var.set("Stopping...")

    def check_thread(self):
        if self.scan_thread and self.scan_thread.is_alive():
            self.root.after(200, self.check_thread)
        else:
            # finished
            self.start_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            if self.stop_event.is_set():
                self.status_var.set("Stopped")
            else:
                self.status_var.set("Done")
            self.progress_var.set(100)

    def on_result(self, entry):
        # called from worker thread; schedule UI update on main thread
        def _add():
            self.results.append(entry)
            display = f"{entry['file']} -> {len(entry['findings'])} finding(s)"
            self.listbox.insert(tk.END, display)
        self.root.after(1, _add)

    def on_progress(self, scanned, total, percent):
        def _upd():
            self.status_var.set(f"Scanning... ({scanned}/{total})")
            self.progress_var.set(percent)
        self.root.after(1, _upd)

    def show_details(self, event=None):
        sel = self.listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        entry = self.results[idx]
        details = json.dumps(entry, indent=2)
        # show details in a simple popup
        detail_win = tk.Toplevel(self.root)
        detail_win.title("Details")
        txt = tk.Text(detail_win, width=100, height=25)
        txt.pack()
        txt.insert(tk.END, details)
        txt.config(state=tk.DISABLED)

    def save_log(self):
        if not self.results:
            messagebox.showinfo("Save Log", "No findings to save. The log will still be created (empty array).")
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")], initialfile="scan_log.json")
        if not filename:
            return
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2)
            messagebox.showinfo("Save Log", f"Log saved to: {filename}")
        except Exception as e:
            messagebox.showerror("Save Log", f"Failed to save log: {e}")


def main():
    root = tk.Tk()
    app = AVGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
