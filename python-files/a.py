#!/usr/bin/env python3
"""
Convert all .docx files in the current directory to UTF-16 .txt using docx2txt.
Usage: python convert_docx_to_txt.py
"""

import os
import sys
import glob

def ensure_docx2txt():
    try:
        import docx2txt  # noqa: F401
        return True
    except ImportError:
        print("docx2txt not found. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "docx2txt"])
            return True
        except Exception as e:
            print(f"Failed to install docx2txt: {e}")
            return False

def main():
    if not ensure_docx2txt():
        sys.exit(1)
    import docx2txt

    cwd = os.getcwd()
    files = glob.glob("*.docx")
    if not files:
        print(f"No .docx files found in: {cwd}")
        return

    count = 0
    for file in files:
        try:
            txt = docx2txt.process(file) or ""
            out = os.path.splitext(file)[0] + ".txt"
            with open(out, "w", encoding="utf-16") as f:
                f.write(txt)
            print(f"Converted: {file} -> {out}")
            count += 1
        except Exception as e:
            print(f"Error converting {file}: {e}")

    print(f"\nDone. Converted {count} file(s) in {cwd}.")

if __name__ == "__main__":
    main()
