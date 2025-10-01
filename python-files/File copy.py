import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class FileCopyApp:
    def _init_(self, root):
        self.root = root
        self.root.title("Smart File Copier")
        self.root.geometry("600x400")

        # Source folder
        tk.Label(root, text="Source Folder:").pack(pady=2)
        self.source_entry = tk.Entry(root, width=80)
        self.source_entry.pack(pady=2)
        tk.Button(root, text="Browse Source", command=self.browse_source).pack(pady=2)

        # Destination folder
        tk.Label(root, text="Destination Folder:").pack(pady=2)
        self.dest_entry = tk.Entry(root, width=80)
        self.dest_entry.pack(pady=2)
        tk.Button(root, text="Browse Destination", command=self.browse_dest).pack(pady=2)

        # File list text file
        tk.Label(root, text="Text File with File Names:").pack(pady=2)
        self.file_entry = tk.Entry(root, width=80)
        self.file_entry.pack(pady=2)
        tk.Button(root, text="Browse Text File", command=self.browse_file).pack(pady=2)

        # Run button
        tk.Button(root, text="Run Copy", command=self.run_copy).pack(pady=10)

        # Log area
        self.log = scrolledtext.ScrolledText(root, width=80, height=10)
        self.log.pack(pady=5)

    def browse_source(self):
        folder = filedialog.askdirectory()
        if folder:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, folder)

    def browse_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, folder)

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def run_copy(self):
        src = self.source_entry.get()
        dest = self.dest_entry.get()
        txt_file = self.file_entry.get()

        if not all([src, dest, txt_file]):
            messagebox.showwarning("Error", "Please select all paths!")
            return

        if not os.path.exists(txt_file):
            messagebox.showerror("Error", "Text file not found!")
            return

        # Read file names
        with open(txt_file, "r") as f:
            file_names = [line.strip() for line in f if line.strip()]

        if not file_names:
            messagebox.showinfo("Info", "No file names found in text file!")
            return

        copied = 0
        self.log.delete(1.0, tk.END)
        for fname in file_names:
            src_file = os.path.join(src, fname)
            if os.path.exists(src_file):
                shutil.copy(src_file, dest)
                self.log.insert(tk.END, f"Copied: {fname}\n")
                copied += 1
            else:
                self.log.insert(tk.END, f"Not found: {fname}\n")

        self.log.insert(tk.END, f"\nDone! Total files copied: {copied}")

if _name_ == "_main_":
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()