import os
import tkinter as tk
from tkinter import filedialog, messagebox

current_folder = ""
all_files = []  # To keep original list for searching

def browse_folder():
    global current_folder, all_files
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_folder = folder_selected
        try:
            files = [f for f in os.listdir(current_folder) if os.path.isfile(os.path.join(current_folder, f))]
            files.sort()
            all_files = files
            update_listbox(all_files)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")

def refresh_file_list():
    if current_folder:
        try:
            files = [f for f in os.listdir(current_folder) if os.path.isfile(os.path.join(current_folder, f))]
            files.sort()
            global all_files
            all_files = files
            apply_search_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Could not refresh folder:\n{e}")
    root.after(5000, refresh_file_list)

def apply_search_filter():
    query = search_var.get().strip().lower()
    if query:
        filtered = [f for f in all_files if f.lower().startswith(query)]
    else:
        filtered = all_files
    update_listbox(filtered)

def update_listbox(file_list):
    listbox.delete(0, tk.END)
    if not file_list:
        listbox.insert(tk.END, "No files found.")
        return

    shortened_files = [f[:8] for f in file_list]
    col_width = 16
    columns = 5
    rows = [shortened_files[i:i+columns] for i in range(0, len(shortened_files), columns)]
    for row in rows:
        line = "".join(f"{f:<{col_width}}" for f in row)
        listbox.insert(tk.END, line)

# GUI Setup
root = tk.Tk()
root.title("File Name Viewer")
root.geometry("1000x500")

top_frame = tk.Frame(root)
top_frame.pack(fill=tk.X, pady=5, padx=10)

browse_btn = tk.Button(top_frame, text="Browse Folder", command=browse_folder, font=("Calibri", 12))
browse_btn.pack(side=tk.LEFT)

search_label = tk.Label(top_frame, text="Search (first 4 chars):", font=("Calibri", 12))
search_label.pack(side=tk.RIGHT)

search_var = tk.StringVar()
search_entry = tk.Entry(top_frame, textvariable=search_var, font=("Calibri", 12), width=20)
search_entry.pack(side=tk.RIGHT, padx=5)
search_var.trace_add("write", lambda *args: apply_search_filter())

listbox = tk.Listbox(root, width=120, height=20, font=("Courier New", 12))  # Monospaced for better alignment
listbox.pack(padx=10, pady=10)

refresh_file_list()
root.mainloop()
