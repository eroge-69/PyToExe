import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import os

class CopyGUI:
    def __init__(self, root):
        self.root = root
        root.title("Datei kopieren")
        root.geometry("600x200")

        # Quelle
        tk.Label(root, text="Quelle:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.source_entry = tk.Entry(root, width=50)
        self.source_entry.grid(row=0, column=1, padx=5)
        tk.Button(root, text="...", command=self.choose_source).grid(row=0, column=2, padx=5)

        # Ziel
        tk.Label(root, text="Ziel:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.dest_entry = tk.Entry(root, width=50)
        self.dest_entry.grid(row=1, column=1, padx=5)
        tk.Button(root, text="...", command=self.choose_dest).grid(row=1, column=2, padx=5)

        # Kopieren-Button
        tk.Button(root, text="Kopieren", command=self.copy_file, width=20, bg="#4CAF50", fg="white").grid(row=2, column=1, pady=20)

        # Drag & Drop aktivieren
        root.drop_target_register('DND_Files')
        root.dnd_bind('<<Drop>>', self.drop)

    def choose_source(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, filename)

    def choose_dest(self):
        folder = filedialog.askdirectory()
        if folder:
            # aktuellen Quell-Dateinamen vorschlagen
            src = self.source_entry.get()
            if src:
                filename = os.path.basename(src)
                full_dest = os.path.join(folder, filename)
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, full_dest)
            else:
                self.dest_entry.delete(0, tk.END)
                self.dest_entry.insert(0, folder)

    def copy_file(self):
        src = self.source_entry.get()
        dst = self.dest_entry.get()

        if not os.path.isfile(src):
            messagebox.showerror("Fehler", "Ungültige Quelldatei")
            return
        if not dst:
            messagebox.showerror("Fehler", "Ungültiges Ziel")
            return

        try:
            shutil.copy(src, dst)
            messagebox.showinfo("Erfolg", f"Datei wurde kopiert nach:\n{dst}")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def drop(self, event):
        # Datei per Drag & Drop ins Fenster ziehen
        file_path = event.data.strip('{}')
        if os.path.isfile(file_path):
            self.source_entry.delete(0, tk.END)
            self.source_entry.insert(0, file_path)
        elif os.path.isdir(file_path):
            self.dest_entry.delete(0, tk.END)
            self.dest_entry.insert(0, file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = CopyGUI(root)
    root.mainloop()
