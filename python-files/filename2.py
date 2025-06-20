import os
import tkinter as tk
from tkinter import filedialog, messagebox
import datetime

current_folder = ""
all_files = []
masked_to_original = {}

valid_draw_prefixes = ("MSE", "GSE", "MPE", "DNE", "NJE", "HAE", "ADE", "SDE")
valid_dealer_prefixes = ("A", "E", "S")

# Change this date as needed
target_date = "2025.06.20"

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

def browse_folder():
    global current_folder, all_files
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".pdf")
            ]
            files.sort()
            all_files = files
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

def refresh_file_list():
    if current_folder:
        try:
            files = [
                f for f in os.listdir(current_folder)
                if os.path.isfile(os.path.join(current_folder, f)) and f.lower().endswith(".pdf")
            ]
            files.sort()
            global all_files
            all_files = files
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh folder:\n{e}")
    root.after(5000, refresh_file_list)

def mask_filename(filename):
    filename_no_ext = os.path.splitext(filename)[0]
    parts = filename_no_ext.strip().split()
    if len(parts) != 4:
        return None

    dealer_code, keyword, draw_no, file_date = parts

    if not dealer_code.startswith(valid_dealer_prefixes):
        return None
    if keyword.lower() != "returns":
        return None
    if not draw_no.startswith(valid_draw_prefixes):
        return None
    if draw_no.upper() not in today_draws:
        return None
    if file_date != target_date:
        return None

    display_text = f"{dealer_code:<10}{draw_no:<12}{file_date}"
    masked_to_original[display_text] = filename
    return display_text

def apply_search_filter():
    query = search_var.get().strip().lower()
    if query:
        filtered = [f for f in all_files if f.lower().startswith(query)]
    else:
        filtered = all_files

    processed = []
    masked_to_original.clear()
    for f in filtered:
        visible = mask_filename(f)
        if visible:
            processed.append(visible)

    # Sort by dealer code
    processed.sort(key=lambda x: x[:10].strip())
    update_listbox(processed)

def update_listbox(display_list):
    listbox.delete(0, tk.END)
    if not display_list:
        listbox.insert(tk.END, "No files found.")
        return

    for line in display_list:
        listbox.insert(tk.END, line)

def on_double_click(event):
    selection = listbox.curselection()
    if not selection:
        return

    clicked_line = listbox.get(selection[0]).strip()
    for masked, original in masked_to_original.items():
        if masked in clicked_line:
            messagebox.showinfo("Original File Name", original)
            break

# --- GUI Setup ---
root = tk.Tk()
root.title("PDF File Name Viewer - Filtered by Today.txt")
root.geometry("1000x500")

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

refresh_file_list()
root.mainloop()
