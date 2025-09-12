
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class PDFRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF File Renamer")
        self.root.geometry("650x500")

        # Title
        tk.Label(root, text="📂 PDF File & Folder Renamer", font=("Arial", 16, "bold")).pack(pady=10)

        # Folder selection
        frame = tk.Frame(root)
        frame.pack(pady=5, fill="x", padx=10)

        self.folder_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.folder_var, font=("Arial", 12)).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(frame, text="Browse", command=self.browse_folder).pack(side="left", padx=5)

        # Preview area
        self.tree = ttk.Treeview(root, columns=("Old", "New"), show="headings")
        self.tree.heading("Old", text="Old File Name")
        self.tree.heading("New", text="New File Name")
        self.tree.column("Old", width=280)
        self.tree.column("New", width=280)
        self.tree.pack(pady=10, fill="both", expand=True)

        # Buttons for files
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Preview Files", command=self.preview_files, width=15).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Rename Files", command=self.rename_files, width=15).pack(side="left", padx=10)

        # Folder rename section
        folder_frame = tk.Frame(root)
        folder_frame.pack(pady=10, fill="x", padx=10)

        tk.Label(folder_frame, text="New Folder Name:", font=("Arial", 12)).pack(side="left", padx=5)
        self.new_folder_var = tk.StringVar()
        tk.Entry(folder_frame, textvariable=self.new_folder_var, font=("Arial", 12)).pack(side="left", fill="x", expand=True, padx=5)
        tk.Button(folder_frame, text="Rename Folder", command=self.rename_folder).pack(side="left", padx=5)

        # Status bar
        self.status = tk.Label(root, text="Select a folder to begin.", relief="sunken", anchor="w")
        self.status.pack(fill="x", side="bottom")

        self.preview_list = []

    def browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder with PDF files")
        if folder:
            self.folder_var.set(folder)

    def preview_files(self):
        folder = self.folder_var.get()
        if not folder or not os.path.exists(folder):
            messagebox.showwarning("Error", "Please select a valid folder.")
            return

        files = os.listdir(folder)
        pdf_files = sorted([f for f in files if f.lower().endswith(".pdf") or "." not in f])

        self.tree.delete(*self.tree.get_children())  # Clear old preview
        self.preview_list = []

        for i, file in enumerate(pdf_files, start=1):
            if file.lower().endswith(".pdf"):
                name, ext = os.path.splitext(file)
            else:
                name, ext = file, ""

            new_name = f"{name}_PAGE {i}{ext}"
            self.preview_list.append((file, new_name))
            self.tree.insert("", "end", values=(file, new_name))

        self.status.config(text=f"Found {len(self.preview_list)} files for renaming.")

    def rename_files(self):
        if not self.preview_list:
            messagebox.showwarning("No Preview", "Please preview files before renaming.")
            return

        folder = self.folder_var.get()
        for old, new in self.preview_list:
            old_path = os.path.join(folder, old)
            new_path = os.path.join(folder, new)
            os.rename(old_path, new_path)

        messagebox.showinfo("Success", f"Renamed {len(self.preview_list)} files successfully!")
        self.status.config(text=f"Renamed {len(self.preview_list)} files.")
        self.preview_list = []
        self.tree.delete(*self.tree.get_children())

    def rename_folder(self):
        old_folder = self.folder_var.get()
        new_folder_name = self.new_folder_var.get().strip()

        if not old_folder or not os.path.exists(old_folder):
            messagebox.showwarning("Error", "Please select a valid folder first.")
            return

        if not new_folder_name:
            messagebox.showwarning("Error", "Please enter a new folder name.")
            return

        parent_dir = os.path.dirname(old_folder)
        new_folder_path = os.path.join(parent_dir, new_folder_name)

        try:
            os.rename(old_folder, new_folder_path)
            self.folder_var.set(new_folder_path)
            messagebox.showinfo("Success", f"Folder renamed to {new_folder_name}")
            self.status.config(text=f"Folder renamed: {new_folder_name}")
        except Exception as e:
            messagebox.showerror("Error", f"Could not rename folder:\n{e}")

# Run app
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFRenamerApp(root)
    root.mainloop()
