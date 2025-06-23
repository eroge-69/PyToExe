import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def browse_jpeg_folder():
    folder = filedialog.askdirectory(title="Select JPEG Folder")
    if folder:
        jpeg_folder_var.set(folder)

def browse_raw_folder():
    folder = filedialog.askdirectory(title="Select RAW Folder")
    if folder:
        raw_folder_var.set(folder)

def start_processing():
    jpeg_folder = jpeg_folder_var.get()
    raw_folder = raw_folder_var.get()
    raw_ext = raw_ext_var.get().strip()

    if not jpeg_folder or not raw_folder or not raw_ext:
        messagebox.showwarning("Missing Info", "Please fill in all fields.")
        return

    selects_folder = os.path.join(raw_folder, "selects")
    os.makedirs(selects_folder, exist_ok=True)

    count = 0
    for filename in os.listdir(jpeg_folder):
        if filename.lower().endswith(".jpg"):
            base = os.path.splitext(filename)[0]
            raw_file = os.path.join(raw_folder, base + raw_ext)
            if os.path.exists(raw_file):
                shutil.copy2(raw_file, os.path.join(selects_folder, base + raw_ext))
                count += 1

    messagebox.showinfo("Done", f"{count} RAW files copied to:\n{selects_folder}")

# GUI Setup
root = tk.Tk()
root.title("RAW Selector Tool")
root.geometry("600x250")
root.resizable(False, False)

tk.Label(root, text="📸 Select JPEG Folder:").grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
jpeg_folder_var = tk.StringVar()
tk.Entry(root, textvariable=jpeg_folder_var, width=60).grid(row=1, column=0, padx=10)
tk.Button(root, text="Browse...", command=browse_jpeg_folder).grid(row=1, column=1, padx=10)

tk.Label(root, text="🖼️ Select RAW Folder:").grid(row=2, column=0, sticky="w", padx=10, pady=(10, 0))
raw_folder_var = tk.StringVar()
tk.Entry(root, textvariable=raw_folder_var, width=60).grid(row=3, column=0, padx=10)
tk.Button(root, text="Browse...", command=browse_raw_folder).grid(row=3, column=1, padx=10)

tk.Label(root, text="✏️ RAW Extension (e.g., .NEF, .CR2):").grid(row=4, column=0, sticky="w", padx=10, pady=(10, 0))
raw_ext_var = tk.StringVar()
tk.Entry(root, textvariable=raw_ext_var, width=20).grid(row=5, column=0, padx=10, sticky="w")

tk.Button(root, text="🚀 Start Processing", command=start_processing, height=2, width=30).grid(row=6, column=0, columnspan=2, pady=20)

root.mainloop()
