import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os

class RenameTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Datei-Umbenennungstool")
        self.files = []

        # Datei-Auswahl
        self.file_frame = ttk.LabelFrame(root, text="Dateien")
        self.file_frame.pack(fill="x", padx=10, pady=5)
        self.file_listbox = tk.Listbox(self.file_frame, height=6)
        self.file_listbox.pack(side="left", fill="both", expand=True)
        self.scrollbar = tk.Scrollbar(self.file_frame, orient="vertical", command=self.file_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=self.scrollbar.set)

        self.add_button = ttk.Button(root, text="Dateien hinzufügen", command=self.add_files)
        self.add_button.pack(pady=5)

        # Optionen für Start und Ende
        self.options_frame = ttk.LabelFrame(root, text="Umbenennungsoptionen")
        self.options_frame.pack(fill="x", padx=10, pady=5)

        self.start_mode = tk.StringVar(value="search")
        self.end_mode = tk.StringVar(value="search")

        ttk.Label(self.options_frame, text="Start:").grid(row=0, column=0, sticky="w")
        self.start_search = ttk.Entry(self.options_frame)
        self.start_search.grid(row=0, column=1)
        self.start_pos = ttk.Spinbox(self.options_frame, from_=0, to=100, width=5)
        self.start_pos.grid(row=0, column=2)
        self.start_mode_menu = ttk.Combobox(self.options_frame, textvariable=self.start_mode, values=["search", "position"], width=10)
        self.start_mode_menu.grid(row=0, column=3)

        ttk.Label(self.options_frame, text="Ende:").grid(row=1, column=0, sticky="w")
        self.end_search = ttk.Entry(self.options_frame)
        self.end_search.grid(row=1, column=1)
        self.end_pos = ttk.Spinbox(self.options_frame, from_=0, to=100, width=5)
        self.end_pos.grid(row=1, column=2)
        self.end_mode_menu = ttk.Combobox(self.options_frame, textvariable=self.end_mode, values=["search", "position"], width=10)
        self.end_mode_menu.grid(row=1, column=3)

        # Vorschau und Umbenennen
        self.preview_button = ttk.Button(root, text="Vorschau", command=self.preview)
        self.preview_button.pack(pady=5)

        self.preview_listbox = tk.Listbox(root, height=6)
        self.preview_listbox.pack(fill="x", padx=10, pady=5)

        self.rename_button = ttk.Button(root, text="Umbenennen", command=self.rename_files)
        self.rename_button.pack(pady=5)

        self.undo_log = []

    def add_files(self):
        new_files = filedialog.askopenfilenames(title="Dateien auswählen")
        for f in new_files:
            if f not in self.files:
                self.files.append(f)
                self.file_listbox.insert("end", os.path.basename(f))

    def extract_name(self, filename):
        base = os.path.basename(filename)
        name = os.path.splitext(base)[0]

        start = 0
        end = len(name)

        if self.start_mode.get() == "search":
            s = self.start_search.get()
            if s in name:
                start = name.find(s)
        else:
            try:
                start = int(self.start_pos.get())
            except ValueError:
                start = 0

        if self.end_mode.get() == "search":
            e = self.end_search.get()
            if e in name[start:]:
                end = name.find(e, start)
        else:
            try:
                end = int(self.end_pos.get())
            except ValueError:
                end = len(name)

        if start < end:
            return name[start:end].strip()
        else:
            return None

    def preview(self):
        self.preview_listbox.delete(0, "end")
        for f in self.files:
            newname = self.extract_name(f)
            if newname:
                self.preview_listbox.insert("end", f"{os.path.basename(f)} -> {newname}{os.path.splitext(f)[1]}")
            else:
                self.preview_listbox.insert("end", f"{os.path.basename(f)} -> [ungültig]")

    def rename_files(self):
        self.undo_log = []
        for f in self.files:
            newname = self.extract_name(f)
            if newname:
                newpath = os.path.join(os.path.dirname(f), newname + os.path.splitext(f)[1])
                if not os.path.exists(newpath):
                    os.rename(f, newpath)
                    self.undo_log.append((newpath, f))
        if self.undo_log:
            with open("undo_rename.log", "w", encoding="utf-8") as log:
                for new, old in self.undo_log:
                    log.write(f"{new} <- {old}\n")
            messagebox.showinfo("Fertig", "Dateien wurden umbenannt. Undo-Datei: undo_rename.log")
        else:
            messagebox.showwarning("Hinweis", "Keine Dateien wurden umbenannt.")

