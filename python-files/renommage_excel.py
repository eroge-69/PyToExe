
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
from openpyxl import Workbook

def select_directory():
    path = filedialog.askdirectory()
    if path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, path)
        update_extensions(path)

def update_extensions(path):
    extensions = set()
    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if os.path.isfile(full_path):
            ext = os.path.splitext(item)[1]
            if ext:
                extensions.add(ext)
    combo_extension['values'] = sorted(list(extensions))
    combo_extension.set('')

def export_to_excel():
    path = entry_path.get()
    if not path:
        messagebox.showerror("Erreur", "Veuillez sélectionner un dossier racine.")
        return

    item_type = combo_type.get()
    selected_ext = combo_extension.get()
    items = []

    for item in os.listdir(path):
        full_path = os.path.join(path, item)
        if item_type == "Fichier" and os.path.isfile(full_path):
            if selected_ext:
                if os.path.splitext(item)[1] == selected_ext:
                    items.append(item)
            else:
                items.append(item)
        elif item_type == "Dossier" and os.path.isdir(full_path):
            items.append(item)

    df = pd.DataFrame({'Nom actuel': items, 'Nouveau nom': [''] * len(items)})
    excel_path = os.path.join(path, 'liste_renommage.xlsx')
    df.to_excel(excel_path, index=False)
    messagebox.showinfo("Exporté", f"Fichier Excel créé : {excel_path}")

def apply_renaming():
    path = entry_path.get()
    excel_path = os.path.join(path, 'liste_renommage.xlsx')
    if not os.path.exists(excel_path):
        messagebox.showerror("Erreur", "Fichier liste_renommage.xlsx introuvable dans le dossier sélectionné.")
        return

    df = pd.read_excel(excel_path, engine='openpyxl')
    for _, row in df.iterrows():
        old_name = row['Nom actuel']
        new_name = row['Nouveau nom']
        if pd.notna(new_name) and new_name != old_name:
            old_path = os.path.join(path, old_name)
            new_path = os.path.join(path, new_name)
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                messagebox.showerror("Erreur", f"Échec du renommage de '{old_name}': {e}")
    messagebox.showinfo("Succès", "Renommage terminé selon le fichier Excel.")

root = tk.Tk()
root.title("Renommage via fichier Excel")

frame_top = tk.Frame(root)
frame_top.pack(padx=10, pady=5)

entry_path = tk.Entry(frame_top, width=50)
entry_path.pack(side=tk.LEFT)

btn_browse = tk.Button(frame_top, text="Parcourir", command=select_directory)
btn_browse.pack(side=tk.LEFT, padx=5)

frame_options = tk.Frame(root)
frame_options.pack(padx=10, pady=5)

combo_type = ttk.Combobox(frame_options, values=["Fichier", "Dossier"], state="readonly")
combo_type.set("Fichier")
combo_type.pack(side=tk.LEFT)

combo_extension = ttk.Combobox(frame_options, state="readonly")
combo_extension.pack(side=tk.LEFT, padx=5)

btn_export = tk.Button(frame_options, text="Exporter vers Excel", command=export_to_excel)
btn_export.pack(side=tk.LEFT, padx=5)

btn_apply = tk.Button(root, text="Appliquer le renommage", command=apply_renaming)
btn_apply.pack(pady=10)

root.mainloop()
