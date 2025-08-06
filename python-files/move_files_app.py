import tkinter as tk
from tkinter import filedialog, messagebox
import shutil

class FileMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Move Files to Folders (1-to-1)")

        self.files = []
        self.folders = []

        tk.Button(root, text="Select Files", command=self.select_files).pack(pady=10)
        tk.Button(root, text="Select Folders", command=self.select_folders).pack(pady=10)
        tk.Button(root, text="Move Files", command=self.move_files).pack(pady=20)

        self.status = tk.Label(root, text="", fg="blue")
        self.status.pack()

    def select_files(self):
        self.files = filedialog.askopenfilenames(title="Select Files")
        count = len(self.files)
        self.status.config(text=f"{count} file(s) selected.")

    def select_folders(self):
        self.folders = []
        while True:
            folder = filedialog.askdirectory(title=f"Select Folder ({len(self.folders)+1}) or Cancel to Stop")
            if not folder:
                break
            self.folders.append(folder)
        count = len(self.folders)
        self.status.config(text=f"{count} folder(s) selected.")

    def move_files(self):
        if len(self.files) != len(self.folders):
            messagebox.showerror("Mismatch", f"Number of files ({len(self.files)}) and folders ({len(self.folders)}) must match.")
            return

        try:
            for i in range(len(self.files)):
                shutil.move(self.files[i], self.folders[i])
            messagebox.showinfo("Success", f"Moved {len(self.files)} files successfully!")
            self.status.config(text="Files moved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("420x250")
    app = FileMoverApp(root)
    root.mainloop()
