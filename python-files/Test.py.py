import shutil
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os

def select_src_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        src_entry.delete(0, tk.END)
        src_entry.insert(0, folder_path)

def select_dst_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        dst_entry.delete(0, tk.END)
        dst_entry.insert(0, folder_path)

def copy_with_progress(src, dst):
    all_files = [f for f in src.rglob("*") if f.is_file()]
    total_files = len(all_files)
    for i, file in enumerate(all_files, 1):
        relative_path = file.relative_to(src)
        dest_file = dst / relative_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest_file)
        progress_var.set(int(i / total_files * 100))
        root.update_idletasks()

def backup_folder_thread():
    src = Path(src_entry.get())
    dst_dir = Path(dst_entry.get())

    if not src.exists():
        messagebox.showerror("Error", "Source folder does not exist!")
        return

    if not dst_dir.exists():
        dst_dir.mkdir(parents=True, exist_ok=True)

    dst = dst_dir / f"{src.name}_backup_{datetime.now():%Y%m%d_%H%M%S}"

    try:
        copy_with_progress(src, dst)
        messagebox.showinfo("Success", f"Backed up:\n{src}\n→ {dst}")
        progress_var.set(0)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        progress_var.set(0)

def start_backup():
    threading.Thread(target=backup_folder_thread, daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Simple Folder Backup Tool")
root.geometry("600x300")

# Source folder
tk.Label(root, text="Source Folder:").pack(pady=5)
src_entry = tk.Entry(root, width=70)
src_entry.pack()
tk.Button(root, text="Browse", command=select_src_folder).pack(pady=5)

# Destination folder
tk.Label(root, text="Backup Destination:").pack(pady=5)
dst_entry = tk.Entry(root, width=70)
dst_entry.insert(0, "D:\\Backups")
dst_entry.pack()
tk.Button(root, text="Browse", command=select_dst_folder).pack(pady=5)

# Checkbox option
include_hidden_var = tk.BooleanVar()
tk.Checkbutton(root, text="Include Hidden Files", variable=include_hidden_var).pack(pady=5)

# Progress bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate", variable=progress_var)
progress_bar.pack(pady=15)
style = ttk.Style()
style.theme_use('default')
style.configure("TProgressbar", thickness=20, troughcolor='gray', background='green')

# Backup button
tk.Button(root, text="Start Backup", command=start_backup).pack(pady=5)

root.mainloop()


