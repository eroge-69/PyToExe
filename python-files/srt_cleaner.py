#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SRT Cleaner — removes dots and commas from subtitle TEXT ONLY (keeps timecodes/index lines).
Works with .srt files (UTF-8).

Build .exe (Windows):
    pip install pyinstaller
    pyinstaller --onefile --windowed srt_cleaner.py

Usage (double-click): choose one or more .srt files; cleaned files are saved next to originals with _cleaned suffix.
"""

import re
import sys
import os
from tkinter import Tk, filedialog, messagebox

APP_TITLE = "SRT Cleaner — keep timecodes intact"

TIME_PATTERN = re.compile(r"\d{2}:\d{2}:\d{2},\d{3}")

def is_index_line(line: str) -> bool:
    return line.strip().isdigit()

def is_timecode_line(line: str) -> bool:
    # SRT timecode lines usually contain '-->'; also protect any line that contains a time pattern
    if '-->' in line:
        return True
    return TIME_PATTERN.search(line) is not None

def clean_text_line(line: str) -> str:
    # Remove ASCII dots and commas only from text lines
    return re.sub(r"[.,]", "", line)

def clean_srt_content(content: str) -> str:
    out_lines = []
    for line in content.splitlines():
        if is_index_line(line) or is_timecode_line(line):
            out_lines.append(line)
        else:
            out_lines.append(clean_text_line(line))
    # Preserve original newline style by joining with '\n' (safe for most players)
    return "\n".join(out_lines) + ("\n" if content.endswith(("\\n", "\r\n", "\r")) else "")

def process_file(path: str) -> str:
    # Read with utf-8-sig to handle BOM gracefully
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        content = f.read()
    cleaned = clean_srt_content(content)
    base, ext = os.path.splitext(path)
    out_path = base + "_cleaned" + ext
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(cleaned)
    return out_path

def main():
    root = Tk()
    root.withdraw()
    root.title(APP_TITLE)
    try:
        file_paths = filedialog.askopenfilenames(
            title="Select one or more .srt files",
            filetypes=[("SRT Subtitles", "*.srt"), ("All files", "*.*")]
        )
        if not file_paths:
            sys.exit(0)

        out_files = []
        for p in file_paths:
            try:
                out_files.append(process_file(p))
            except Exception as e:
                messagebox.showerror(APP_TITLE, f"Failed to process:\n{p}\n\n{e}")
        if out_files:
            msg = "Cleaned files:\n\n" + "\n".join(out_files)
            messagebox.showinfo(APP_TITLE, msg)
    except Exception as e:
        messagebox.showerror(APP_TITLE, f"Unexpected error:\n{e}")
    finally:
        root.destroy()

if __name__ == "__main__":
    main()
