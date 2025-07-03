import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import hashlib
import os

class SHA256DualCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SHA-256 Dual File Hash Checker")
        self.root.geometry("800x500")
        self.root.configure(bg="#f4f4f4")

        self.file1_path = None
        self.file2_path = None

        # Title
        title_label = ttk.Label(root, text="Compare SHA-256 Hashes of Two Files", font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Frames for drop areas
        frame = ttk.Frame(root)
        frame.pack(pady=10)

        self.create_drop_area(frame, "File 1", 0)
        self.create_drop_area(frame, "File 2", 1)

        # Output
        self.output = tk.Text(root, height=10, wrap="word", bg="#ffffff", relief="sunken")
        self.output.pack(padx=20, pady=20, fill="both", expand=True)

    def create_drop_area(self, parent, label_text, column):
        container = ttk.Frame(parent)
        container.grid(row=0, column=column, padx=40)

        label = ttk.Label(container, text=label_text)
        label.pack()

        drop_area = tk.Label(container, text=f"Drop {label_text} here", bg="#e0e0e0",
                             relief="ridge", width=40, height=5)
        drop_area.pack(pady=5)
        drop_area.drop_target_register('DND_Files')
        drop_area.dnd_bind('<<Drop>>', lambda e, idx=column: self.handle_drop(e, idx))
        drop_area.bind("<Button-1>", lambda e, idx=column: self.browse_file(idx))

        if column == 0:
            self.drop_area1 = drop_area
        else:
            self.drop_area2 = drop_area

    def browse_file(self, index):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.set_file_path(file_path, index)

    def handle_drop(self, event, index):
        file_path = self.root.splitlist(event.data)[0].strip('{}')
        if os.path.isfile(file_path):
            self.set_file_path(file_path, index)
        else:
            messagebox.showerror("Error", "Invalid file dropped.")

    def set_file_path(self, file_path, index):
        if index == 0:
            self.file1_path = file_path
            self.drop_area1.config(text=os.path.basename(file_path))
        else:
            self.file2_path = file_path
            self.drop_area2.config(text=os.path.basename(file_path))
        self.try_compare()

    def compute_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def try_compare(self):
        if self.file1_path and self.file2_path:
            try:
                hash1 = self.compute_sha256(self.file1_path)
                hash2 = self.compute_sha256(self.file2_path)

                result = (
                    f"File 1: {os.path.basename(self.file1_path)}\nSHA-256: {hash1}\n\n"
                    f"File 2: {os.path.basename(self.file2_path)}\nSHA-256: {hash2}\n\n"
                )

                if hash1 == hash2:
                    result += "✅ Hash Identik — File kemungkinan sama."
                else:
                    result += "❌ Hash Berbeda — File berbeda."

                self.output.delete("1.0", tk.END)
                self.output.insert(tk.END, result)
            except Exception as e:
                messagebox.showerror("Error", f"Gagal memproses file:\n{e}")

if __name__ == "__main__":
    try:
        import tkinterdnd2 as tkdnd
    except ImportError:
        print("Please install tkinterdnd2:\n pip install tkinterdnd2")
        exit(1)

    class CustomApp(tkdnd.TkinterDnD.Tk, SHA256DualCheckerApp):
        def __init__(self):
            tkdnd.TkinterDnD.Tk.__init__(self)
            SHA256DualCheckerApp.__init__(self, self)

    app = CustomApp()
    app.mainloop()
