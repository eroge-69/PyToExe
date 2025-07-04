import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Global variables
current_folder = ""
all_files = []
masked_to_original = {}
txt_totals = {}

# Constants
valid_draw_prefixes = ("MSE", "GSE", "MPE", "DNE", "NJE", "HAE", "ADE", "SDE")
valid_dealer_prefixes = ("A", "E", "S")

# Load draw numbers from Today.txt
def load_today_draw_numbers():
    draw_numbers = set()
    try:
        with open("Today.txt", "r") as file:
            for line in file:
                clean = line.strip().upper()
                if clean:
                    draw_numbers.add(clean)
    except FileNotFoundError:
        messagebox.showwarning("Missing File", "Today.txt not found in app folder.")
    return draw_numbers

today_draws = load_today_draw_numbers()

# Load totals from each .txt file
def load_txt_totals():
    txt_totals.clear()
    for filename in all_files:
        filepath = os.path.join(current_folder, filename)
        name_no_ext = os.path.splitext(filename)[0]
        total = 0
        try:
            with open(filepath, "r") as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        start, end = int(parts[0]), int(parts[1])
                        if end >= start:
                            total += (end - start + 1)
            txt_totals[name_no_ext] = total
        except Exception as e:
            print(f"Failed to read {filename}: {e}")

# Browse for .txt files
def browse_folder():
    global current_folder, all_files
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".txt")
            ]
            files.sort()
            all_files = files
            load_txt_totals()
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

# Refresh the file list periodically
def refresh_file_list():
    if current_folder:
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".txt")
            ]
            files.sort()
            global all_files
            all_files = files
            load_txt_totals()
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh folder:\n{e}")
    root.after(5000, refresh_file_list)

# Create masked display text and validation
def mask_filename(filename):
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.strip().split()
    if len(parts) != 4:
        return None, None, None

    dealer_code, keyword, draw_no, file_date = parts

    if not dealer_code.startswith(valid_dealer_prefixes):
        return None, None, None
    if keyword.lower() != "returns":
        return None, None, None
    if not draw_no.startswith(valid_draw_prefixes):
        return None, None, None
    if draw_no.upper() not in today_draws:
        return None, None, None

    # Append total if available
    txt_name = f"{dealer_code} Returns {draw_no} {file_date}"
    total = txt_totals.get(txt_name, "")
    total_str = f" | Total: {total}" if total else ""
    display_text = f"{dealer_code:<10}{draw_no:<12}{file_date}{total_str}"
    return display_text, (dealer_code.upper(), draw_no.upper()), dealer_code.upper()

# Filter and display
def apply_search_filter():
    query = search_var.get().strip().lower()
    if query:
        filtered = [f for f in all_files if f.lower().startswith(query)]
    else:
        filtered = all_files

    processed = []
    masked_to_original.clear()
    dealer_file_count = 0
    dealer_code_found = None

    for f in filtered:
        visible, key, dealer_code = mask_filename(f)
        if visible and key:
            masked_to_original.setdefault(key, []).append((visible, f))
            processed.append(visible)
            if dealer_code and dealer_code.lower() == query:
                dealer_file_count += 1
                dealer_code_found = dealer_code

    processed.sort(key=lambda x: x[:10].strip())
    update_listbox(processed)

    if dealer_code_found:
        count_label.config(text=f"Dealer {dealer_code_found} - Total Files: {dealer_file_count}")
    else:
        count_label.config(text="")

# Update listbox
def update_listbox(display_list):
    listbox.delete(0, tk.END)
    if not display_list:
        listbox.insert(tk.END, "No files found.")
        return
    for line in display_list:
        listbox.insert(tk.END, line)

# Show original filenames on double-click
def on_double_click(event):
    selection = listbox.curselection()
    if not selection:
        return

    clicked_line = listbox.get(selection[0]).strip()
    parts = clicked_line.split()
    if len(parts) < 3:
        return

    dealer_code = parts[0].upper()
    draw_no = parts[1].upper()
    key = (dealer_code, draw_no)

    if key in masked_to_original:
        original_files = [orig_file for _, orig_file in masked_to_original[key]]
        messagebox.showinfo(f"All files for {dealer_code} {draw_no}", "\n".join(original_files))
    else:
        messagebox.showinfo("Not found", "No original files available for selection.")

# --- GUI Setup ---
root = tk.Tk()
root.title("TXT File Name Viewer - Filtered by Today.txt")
root.geometry("1000x550")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)

browse_btn = tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12))
browse_btn.pack(side=tk.LEFT)

search_label = tk.Label(top_frame, text="Search (Dealer Code):", font=("Calibri", 12))
search_label.pack(side=tk.RIGHT)

search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20)
search_entry.pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))
listbox.pack(padx=10, pady=10)
listbox.bind("<Double-Button-1>", on_double_click)

# --- Bottom Label for Count ---
count_label = tk.Label(root, text="", font=("Calibri", 14), fg="blue")
count_label.pack(pady=(0, 10))

# Start background refresh
refresh_file_list()
root.mainloop()
