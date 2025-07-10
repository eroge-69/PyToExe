
import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

# Disques à scanner
DRIVES = ['C:\\', 'D:\\', 'E:\\', 'G:\\']

# Extensions de fichiers karaoké
EXTENSIONS = ['.kfn', '.kar', '.mp3', '.cdg']

def find_files():
    files = []
    for drive in DRIVES:
        for root, dirs, filenames in os.walk(drive):
            for file in filenames:
                if any(file.lower().endswith(ext) for ext in EXTENSIONS):
                    files.append(os.path.join(root, file))
    return files

class KaraokeApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Amorona Player")
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}")
        self.create_widgets()
        self.karaoke_files = []

    def create_widgets(self):
        # Barre de recherche
        self.search_var = tk.StringVar()
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side='left')
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<Return>', lambda e: self.search_files())

        ttk.Button(search_frame, text="Search", command=self.search_files).pack(side='left', padx=5)

        # Liste des fichiers
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill='both', expand=True, padx=10, pady=5)
        self.listbox.bind('<Double-Button-1>', lambda e: self.play_selected())

        # Boutons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill='x', padx=10, pady=5)

        ttk.Button(btn_frame, text="Play", command=self.play_selected).pack(side='left')
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_files).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Exit", command=self.destroy).pack(side='right')

        self.refresh_files()

    def refresh_files(self):
        self.listbox.delete(0, tk.END)
        self.karaoke_files = find_files()
        for f in self.karaoke_files:
            self.listbox.insert(tk.END, os.path.basename(f))

    def search_files(self):
        query = self.search_var.get().lower()
        self.listbox.delete(0, tk.END)
        filtered = [f for f in self.karaoke_files if query in os.path.basename(f).lower()]
        for f in filtered:
            self.listbox.insert(tk.END, os.path.basename(f))

    def play_selected(self):
        try:
            idx = self.listbox.curselection()[0]
            filename = self.listbox.get(idx)
            full_path = next(f for f in self.karaoke_files if os.path.basename(f) == filename)
            # Lancer KaraFun Player (modifier le chemin si nécessaire)
            karafun_path = r"C:\Program Files (x86)\KaraFun\KaraFun.exe"
            if os.path.exists(karafun_path):
                subprocess.Popen([karafun_path, full_path])
            else:
                messagebox.showerror("Error", "KaraFun Player not found!")
        except IndexError:
            messagebox.showwarning("Warning", "Select a file first.")

if __name__ == "__main__":
    app = KaraokeApp()
    app.mainloop()
