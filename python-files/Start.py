import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json

INJECT_RECORD = ".injected.json"
SOURCE_DIR = "data"

class ModLoaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GTAV Mod Loader")
        self.root.geometry("400x200")
        self.root.resizable(False, False)

        self.target_dir = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=20)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Zielordner:").pack(anchor="w")
        entry = ttk.Entry(frm, textvariable=self.target_dir, width=50)
        entry.pack(fill="x", pady=5)

        ttk.Button(frm, text="Durchsuchen...", command=self.select_folder).pack(anchor="e", pady=(0, 10))

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(fill="x", pady=10)

        ttk.Button(btn_frame, text="Inject", command=self.inject_mods).pack(side="left", expand=True, padx=5)
        ttk.Button(btn_frame, text="Eject", command=self.eject_mods).pack(side="right", expand=True, padx=5)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.target_dir.set(folder)

    def inject_mods(self):
        target = self.target_dir.get()
        if not target:
            messagebox.showerror("Fehler", "Bitte Zielordner auswählen.")
            return

        if not os.path.exists(SOURCE_DIR):
            messagebox.showerror("Fehler", f"Quellordner '{SOURCE_DIR}' nicht gefunden.")
            return

        injected_paths = []

        for root_dir, dirs, files in os.walk(SOURCE_DIR):
            rel_path = os.path.relpath(root_dir, SOURCE_DIR)
            dest_dir = os.path.join(target, rel_path)
            os.makedirs(dest_dir, exist_ok=True)

            for file in files:
                src_file = os.path.join(root_dir, file)
                dst_file = os.path.join(dest_dir, file)
                shutil.copy2(src_file, dst_file)
                injected_paths.append(os.path.relpath(dst_file, target))

            for folder in dirs:
                injected_folder = os.path.join(dest_dir, folder)
                injected_paths.append(os.path.relpath(injected_folder, target))

        record_path = os.path.join(target, INJECT_RECORD)
        with open(record_path, "w") as f:
            json.dump(injected_paths, f, indent=2)

        messagebox.showinfo("Fertig", f"{len(injected_paths)} Dateien/Ordner injected.")

    def eject_mods(self):
        target = self.target_dir.get()
        record_path = os.path.join(target, INJECT_RECORD)

        if not os.path.exists(record_path):
            messagebox.showerror("Fehler", "Keine Inject-Daten vorhanden.")
            return

        with open(record_path, "r") as f:
            injected_paths = json.load(f)

        deleted = 0
        for rel_path in sorted(injected_paths, key=lambda p: -len(p.split(os.sep))):
            full_path = os.path.join(target, rel_path)
            try:
                if os.path.isfile(full_path):
                    os.remove(full_path)
                    deleted += 1
                elif os.path.isdir(full_path):
                    shutil.rmtree(full_path, ignore_errors=True)
                    deleted += 1
            except Exception as e:
                print(f"Fehler beim Entfernen: {full_path} - {e}")

        os.remove(record_path)
        messagebox.showinfo("Eject abgeschlossen", f"{deleted} Elemente entfernt.")

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style(root)
    style.theme_use("clam")  # Modern look
    ModLoaderApp(root)
    root.mainloop()
