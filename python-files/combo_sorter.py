import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import re
import os
from email_validator import validate_email, EmailNotValidError
from collections import defaultdict

def is_valid_email(email):
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False

def extract_domain(email):
    return email.split('@')[-1]

def extract_region(domain):
    parts = domain.split('.')
    return parts[-1] if len(parts) > 1 else 'unknown'

def process_file(filepath, sort_by, remove_dupes, remove_invalid, export_mode):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [line.strip() for line in f if ':' in line]

    processed = []
    seen = set()

    for line in lines:
        email, password = line.split(':', 1)
        if remove_invalid and not is_valid_email(email):
            continue
        if remove_dupes:
            key = f"{email}:{password}"
            if key in seen:
                continue
            seen.add(key)
        processed.append((email, password))

    grouped = defaultdict(list)

    for email, password in processed:
        if sort_by == "Domain":
            key = extract_domain(email)
        elif sort_by == "Region":
            key = extract_region(extract_domain(email))
        else:
            key = "All"
        grouped[key].append(f"{email}:{password}")

    output_dir = os.path.join(os.path.dirname(filepath), "sorted_output")
    os.makedirs(output_dir, exist_ok=True)

    if export_mode == "Single file":
        output_file = os.path.join(output_dir, f'sorted_output.txt')
        with open(output_file, 'w') as f:
            for group in grouped.values():
                f.write('\n'.join(group) + '\n')
    else:
        for key, lines in grouped.items():
            output_file = os.path.join(output_dir, f"{key}_combos.txt")
            with open(output_file, 'w') as f:
                f.write('\n'.join(lines) + '\n')

    messagebox.showinfo("Success", f"Sorted combos saved in:\n{output_dir}")

# GUI
def start_gui():
    root = tk.Tk()
    root.title("Combo Sorter - Email:Pass")

    tk.Label(root, text="Select Combo File (.txt):").grid(row=0, column=0, sticky='w')
    file_path_var = tk.StringVar()

    def browse_file():
        filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        file_path_var.set(filename)

    tk.Entry(root, textvariable=file_path_var, width=50).grid(row=0, column=1)
    tk.Button(root, text="Browse", command=browse_file).grid(row=0, column=2)

    tk.Label(root, text="Sort by:").grid(row=1, column=0, sticky='w')
    sort_var = tk.StringVar(value="Domain")
    ttk.Combobox(root, textvariable=sort_var, values=["Domain", "Region", "None"]).grid(row=1, column=1)

    remove_dupes_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Remove duplicates", variable=remove_dupes_var).grid(row=2, column=0, sticky='w')

    remove_invalid_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Remove invalid emails", variable=remove_invalid_var).grid(row=3, column=0, sticky='w')

    tk.Label(root, text="Export mode:").grid(row=4, column=0, sticky='w')
    export_var = tk.StringVar(value="Single file")
    ttk.Combobox(root, textvariable=export_var, values=["Single file", "Split per group"]).grid(row=4, column=1)

    def run_sort():
        path = file_path_var.get()
        if not os.path.isfile(path):
            messagebox.showerror("Error", "Invalid file path.")
            return
        process_file(
            filepath=path,
            sort_by=sort_var.get(),
            remove_dupes=remove_dupes_var.get(),
            remove_invalid=remove_invalid_var.get(),
            export_mode=export_var.get()
        )

    tk.Button(root, text="Sort & Export", command=run_sort, bg="green", fg="white").grid(row=5, column=1, pady=10)

    root.mainloop()

if name == "__main__":
    start_gui()