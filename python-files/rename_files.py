import os
import tkinter as tk
from tkinter import filedialog

def parse_line(line: str):
    line = line.strip()
    if not line:
        return None, None

    if "->" in line:
        parts = line.split("->")
    else:
        parts = line.split()

    if len(parts) < 2:
        return None, None

    old = parts[0].strip()
    new = parts[1].strip()
    return old, new


def main():
    root = tk.Tk()
    root.withdraw()

    txt_file = filedialog.askopenfilename(
        title="Select Rename List File",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )

    if not txt_file:
        print("No file selected. Exiting...")
        return

    with open(txt_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        old, new = parse_line(line)
        if not old or not new:
            continue

        if os.path.exists(old):
            try:
                os.rename(old, new)
                print(f"Renamed: {old} -> {new}")
            except Exception as e:
                print(f"Failed to rename {old}: {e}")
        else:
            print(f"File not found: {old}")

    input("\nDone! Press Enter to exit...")


if __name__ == "__main__":
    main()
