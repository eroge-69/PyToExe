import tkinter as tk
from tkinter import filedialog, messagebox
import csv
import os

# Fixed and exclusion keywords
FIXED_KEYWORDS = [
    "    writes:",
    "    reads:",
    "  Ann {*  SE_CMD label:"
]

EXCLUDE_KEYWORDS = [
    "HDBG",
    "IR.IR",
    ".DR",
    "-var_length",
    "TESSENT_PRAGMA",
    "TESSENT_MARKER"
]

def filter_lines(input_file, user_keywords):
    filtered_lines = []
    with open(input_file, 'r') as file:
        for line in file:
            if (any(fk in line for fk in FIXED_KEYWORDS) or any(uk in line for uk in user_keywords)) \
               and not any(ex in line for ex in EXCLUDE_KEYWORDS):
                filtered_lines.append([line.strip()])
    return filtered_lines

def browse_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

def browse_output():
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, file_path)

def run_filter():
    input_file = entry_file.get()
    output_file = entry_output.get()
    keywords = entry_keywords.get()
    user_keywords = [kw.strip() for kw in keywords.split(",") if kw.strip()]

    if not os.path.isfile(input_file):
        messagebox.showerror("Error", "Please select a valid input file.")
        return

    if not user_keywords:
        messagebox.showerror("Error", "Please enter at least one keyword.")
        return

    if not output_file:
        messagebox.showerror("Error", "Please specify an output file path.")
        return

    filtered = filter_lines(input_file, user_keywords)
    if not filtered:
        messagebox.showinfo("Result", "No matching lines found.")
        return

    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Filtered Lines"])
        writer.writerows(filtered)

    messagebox.showinfo("Success", f"Filtered lines saved to {output_file}")

# GUI setup
root = tk.Tk()
root.title("Test TAP Pattern Filter")

tk.Label(root, text="Input File:").grid(row=0, column=0, sticky="e")
entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1)
tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

tk.Label(root, text="Test TAP Keywords (comma-separated):").grid(row=1, column=0, sticky="e")
entry_keywords = tk.Entry(root, width=50)
entry_keywords.grid(row=1, column=1, columnspan=2)

tk.Label(root, text="Output File:").grid(row=2, column=0, sticky="e")
entry_output = tk.Entry(root, width=50)
entry_output.grid(row=2, column=1)
tk.Button(root, text="Browse", command=browse_output).grid(row=2, column=2)

tk.Button(root, text="Run Filter", command=run_filter).grid(row=3, column=1, pady=10)

root.mainloop()
