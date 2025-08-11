import tkinter as tk
from tkinter import messagebox
import csv
import os
import ctypes
import sys

if sys.platform == "win32":
    # Get the handle to the console window
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        # Hide the console window
        ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE



# Load CSV from same folder as script/EXE
csv_filename = "parts.csv"
csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), csv_filename)
if not os.path.exists(csv_path):
    messagebox.showerror("Error", f"CSV file not found:\n{csv_path}")
    raise SystemExit

# Read CSV into a list of dicts
with open(csv_path, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    data = list(reader)

search_column = "PART NUMBER"  # must match header exactly

def search_part():
    part_num = entry.get().strip()
    if not part_num:
        messagebox.showwarning("Input Error", "Please enter a part number.")
        return

    match = None
    for row in data:
        val = row.get(search_column, "").strip()
        if val.lower() == part_num.lower():
            match = row
            break

    # Clear previous details widgets
    for widget in details_frame.winfo_children():
        widget.destroy()

    if not match:
        lbl_partnum.config(text="")
        no_result_lbl = tk.Label(details_frame, text=f"No results found for: {part_num}", font=("Segoe UI", 12))
        no_result_lbl.grid(row=0, column=0, sticky="w")
        return

    # Set part number (big bold)
    lbl_partnum.config(text=match[search_column])

    # Add title-data pairs in two columns
    row_idx = 0
    for col, value in match.items():
        if col != search_column and value.strip():
            title_lbl = tk.Label(details_frame, text=col + ":", font=("Segoe UI", 12, "bold"), anchor="w", wraplength=160, justify="left")
            data_lbl = tk.Label(details_frame, text=value.strip(), font=("Segoe UI", 12), anchor="w", wraplength=200, justify="left")
            title_lbl.grid(row=row_idx, column=0, sticky="w", padx=(0, 10), pady=2)
            data_lbl.grid(row=row_idx, column=1, sticky="w", pady=2)
            row_idx += 1

            # Add a bold black separator after "MATERIAL"
            if col.strip().upper() == "MATERIAL":
                sep = tk.Frame(details_frame, bg="black", height=3)  # 3 pixels tall
                sep.grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=6)
                row_idx += 1
                
            # Add a bold black separator after "MATERIAL"            
            if col.strip().upper() == "CUT 1 PROGRAM NUMBER":
                sep = tk.Frame(details_frame, bg="black", height=3)  # 3 pixels tall
                sep.grid(row=row_idx, column=0, columnspan=2, sticky="ew", pady=6)
                row_idx += 1
                

# --- UI Setup ---
root = tk.Tk()
root.title("Part Search")
root.geometry("375x1000")

# Search entry
entry = tk.Entry(root, font=("Segoe UI", 12))
entry.pack(padx=10, pady=10, fill=tk.X)

# Search button
btn = tk.Button(root, text="Search", font=("Segoe UI", 10), command=search_part)
btn.pack(pady=5)

# Part number label (big bold)
lbl_partnum = tk.Label(root, text="", font=("Segoe UI", 28, "bold"))
lbl_partnum.pack(pady=10)

# Details frame replaces lbl_details
details_frame = tk.Frame(root)
details_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Bind Enter key
entry.bind("<Return>", lambda event: search_part())

root.mainloop()
