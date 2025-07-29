
import os
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile

def extract_pngs(pak_path, output_dir):
    if not zipfile.is_zipfile(pak_path):
        messagebox.showerror("Invalid File", "The selected file is not a valid .pak (zip) archive.")
        return
    with zipfile.ZipFile(pak_path, 'r') as z:
        png_files = [f for f in z.namelist() if f.lower().endswith('.png')]
        if not png_files:
            messagebox.showinfo("No PNGs", "No PNG files found in the archive.")
            return
        for f in png_files:
            z.extract(f, output_dir)
        messagebox.showinfo("Success", f"Extracted {len(png_files)} PNG files to {output_dir}")

def browse_pak():
    file_path.set(filedialog.askopenfilename(title="Select .pak File", filetypes=[("PAK files", "*.pak"), ("All files", "*.*")]))

def browse_output():
    output_path.set(filedialog.askdirectory(title="Select Output Folder"))

def start_extraction():
    pak = file_path.get()
    out_dir = output_path.get()
    if not pak or not out_dir:
        messagebox.showwarning("Missing Info", "Please select both input file and output folder.")
        return
    extract_pngs(pak, out_dir)

root = tk.Tk()
root.title("PNG Extractor from .pak")
root.geometry("500x200")

file_path = tk.StringVar()
output_path = tk.StringVar()

tk.Label(root, text="Select .pak File:").pack(pady=5)
tk.Entry(root, textvariable=file_path, width=50).pack(pady=2)
tk.Button(root, text="Browse", command=browse_pak).pack(pady=2)

tk.Label(root, text="Select Output Folder:").pack(pady=5)
tk.Entry(root, textvariable=output_path, width=50).pack(pady=2)
tk.Button(root, text="Browse", command=browse_output).pack(pady=2)

tk.Button(root, text="Extract PNGs", command=start_extraction, bg="#4CAF50", fg="white").pack(pady=10)

root.mainloop()
