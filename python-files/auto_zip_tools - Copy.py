import os
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox

APP_TITLE = "Auto Zip Tool"

# মূল ফাংশন: EPS & JPG/JPEG মিলে ZIP তৈরি
def find_and_zip_pairs(folder_path):
    created = 0
    for root, dirs, files in os.walk(folder_path):
        eps_files = {os.path.splitext(f)[0]: os.path.join(root, f) for f in files if f.lower().endswith(".eps")}
        jpg_files = {os.path.splitext(f)[0]: os.path.join(root, f) for f in files if f.lower().endswith((".jpg", ".jpeg"))}

        common_files = set(eps_files.keys()) & set(jpg_files.keys())

        for base_name in common_files:
            zip_path = os.path.join(root, f"{base_name}.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                zipf.write(eps_files[base_name], os.path.basename(eps_files[base_name]))
                zipf.write(jpg_files[base_name], os.path.basename(jpg_files[base_name]))
            created += 1

    messagebox.showinfo(APP_TITLE, f"{created} zip files created successfully!")

# Browse button ফাংশন
def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        find_and_zip_pairs(folder_selected)

# Drag & Drop ফাংশন
def drag_drop(event):
    folder_path = event.data
    # উইন্ডোজে path আসতে পারে {C:/Path} ফরম্যাটে, তাই {} সরানো
    folder_path = folder_path.strip("{}")
    if os.path.isdir(folder_path):
        find_and_zip_pairs(folder_path)
    else:
        messagebox.showerror(APP_TITLE, "Please drop a folder, not a file.")

# Tkinter UI
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    root = TkinterDnD.Tk()
except ImportError:
    messagebox.showerror(APP_TITLE, "Please install tkinterdnd2 for drag & drop support.\nCommand: pip install tkinterdnd2")
    root = tk.Tk()

root.title(APP_TITLE)
root.geometry("450x200")

label = tk.Label(root, text="Drag & Drop a folder here OR click Browse", padx=10, pady=20)
label.pack(expand=True, fill='both')

browse_btn = tk.Button(root, text="Browse Folder", command=browse_folder, width=20, pady=5)
browse_btn.pack(pady=20)

# Drag & Drop binding
try:
    label.drop_target_register(DND_FILES)
    label.dnd_bind('<<Drop>>', drag_drop)
except:
    pass  # tkinterdnd2 ইনস্টল না থাকলে skip করবে

root.mainloop()