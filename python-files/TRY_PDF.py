import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox

# 👉 Update this path after installing Ghostscript
GS_PATH = r"C:\Program Files\gs\gs10.06.0\bin\gswin64c.exe"

# Ghostscript compression settings
GS_QUALITY = {
    "Low": "/screen",
    "Medium": "/ebook",
    "High": "/printer",
    "Very High": "/prepress"
}

# Page size options
PAGE_SIZES = {
    "Keep Original": None,
    "A4": "595x842",
    "Letter": "612x792",
    "Legal": "612x1008"
}

def compress_pdf(input_path, output_path, quality="/ebook", page_size=None):
    try:
        cmd = [
            GS_PATH, "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            "-dPDFSETTINGS={}".format(quality),
            "-dNOPAUSE", "-dQUIET", "-dBATCH",
        ]

        # Add page size if chosen
        if page_size:
            cmd.append(f"-dDEVICEWIDTHPOINTS={page_size.split('x')[0]}")
            cmd.append(f"-dDEVICEHEIGHTPOINTS={page_size.split('x')[1]}")
            cmd.append("-dFIXEDMEDIA")

        cmd.append(f"-sOutputFile={output_path}")
        cmd.append(input_path)

        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        print(f"Error compressing {input_path}: {e}")
        return False

def select_folder():
    src_folder = filedialog.askdirectory(title="Select Source Folder with PDFs")
    if not src_folder:
        return
    
    dst_folder = filedialog.askdirectory(title="Select Destination Folder")
    if not dst_folder:
        return

    quality = quality_var.get()
    page_size = PAGE_SIZES[page_size_var.get()]

    for file in os.listdir(src_folder):
        if file.lower().endswith(".pdf"):
            input_path = os.path.join(src_folder, file)
            output_path = os.path.join(dst_folder, file)
            success = compress_pdf(input_path, output_path, GS_QUALITY[quality], page_size)
            if success:
                print(f"✅ Compressed: {file}")
            else:
                print(f"❌ Failed: {file}")

    messagebox.showinfo("Done", f"All PDFs compressed and saved in:\n{dst_folder}")

# GUI
root = tk.Tk()
root.title("Bulk PDF Size Reducer (Ghostscript)")
root.geometry("420x300")

tk.Label(root, text="Bulk PDF Compressor", font=("Arial", 16, "bold")).pack(pady=10)

# Quality dropdown
tk.Label(root, text="Select Compression Quality:", font=("Arial", 12)).pack()
quality_var = tk.StringVar(value="Medium")
tk.OptionMenu(root, quality_var, *GS_QUALITY.keys()).pack(pady=5)

# Page size dropdown
tk.Label(root, text="Select Page Size:", font=("Arial", 12)).pack()
page_size_var = tk.StringVar(value="Keep Original")
tk.OptionMenu(root, page_size_var, *PAGE_SIZES.keys()).pack(pady=5)

# Action button
tk.Button(root, text="Select Source & Destination Folders", command=select_folder,
          font=("Arial", 12), bg="lightblue").pack(pady=20)

root.mainloop()
