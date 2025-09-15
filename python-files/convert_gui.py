import os
import codecs
import tkinter as tk
from tkinter import messagebox

source_root = "01 Revit DXF"
destination_root = "02_NEW Revit DXF"

# Mapper på øverste niveau (materiale-typer)
material_folders = {"Brandgips", "Krydsfiner", "OSB", "Spaanplade_ Sheating", "Ultraboard", "Vindspaerre"}

def find_unique_folders():
    """Find unikke undermapper under materialefolderne."""
    unique = set()
    for material in material_folders:
        material_path = os.path.join(source_root, material)
        if os.path.exists(material_path):
            for entry in os.listdir(material_path):
                entry_path = os.path.join(material_path, entry)
                if os.path.isdir(entry_path):
                    unique.add(entry)
    return sorted(unique)

def convert_selected(selected_folders):
    """Konverter DXF-filer i de valgte undermapper på tværs af materialetyper."""
    for material in material_folders:
        material_path = os.path.join(source_root, material)
        if os.path.exists(material_path):
            for subfolder in os.listdir(material_path):
                if subfolder in selected_folders:
                    subfolder_path = os.path.join(material_path, subfolder)
                    for root, dirs, files in os.walk(subfolder_path):
                        for filename in files:
                            if filename.lower().endswith(".dxf"):
                                source_path = os.path.join(root, filename)
                                relative_path = os.path.relpath(source_path, source_root)
                                destination_path = os.path.join(destination_root, relative_path)
                                destination_dir = os.path.dirname(destination_path)
                                os.makedirs(destination_dir, exist_ok=True)

                                # Læs i UTF-8
                                with codecs.open(source_path, "r", encoding="utf-8", errors="ignore") as f:
                                    content = f.read()

                                # Ret encoding
                                content = content.replace("ANSI_1200", "ANSI_1252")

                                # Skriv i CP1252
                                with codecs.open(destination_path, "w", encoding="cp1252", errors="replace") as f:
                                    f.write(content)

    messagebox.showinfo("Færdig", f"Konvertering færdig!\nResultater gemt i '{destination_root}'")

def start_gui():
    folders = find_unique_folders()
    if not folders:
        messagebox.showwarning("Ingen mapper", "Der blev ikke fundet nogen undermapper at konvertere.")
        return

    root = tk.Tk()
    root.title("Vælg mapper til konvertering")

    tk.Label(root, text="Vælg hvilke mapper (projekter) du vil konvertere:").pack(pady=5)

    selections = {}
    for folder in folders:
        var = tk.BooleanVar()
        chk = tk.Checkbutton(root, text=folder, variable=var)
        chk.pack(anchor="w")
        selections[folder] = var

    def run_conversion():
        selected = [name for name, var in selections.items() if var.get()]
        if not selected:
            messagebox.showwarning("Ingen valg", "Du skal vælge mindst én mappe.")
            return
        root.destroy()
        convert_selected(selected)

    tk.Button(root, text="Konverter valgte", command=run_conversion).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    start_gui()
