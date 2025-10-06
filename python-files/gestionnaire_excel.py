
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess

# Dictionnaire pour stocker les fichiers par catégories et sous-catégories
file_structure = {}

# Fonction pour ajouter un fichier Excel
def add_file():
    filepath = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not filepath:
        return

    category = category_entry.get().strip()
    subcategory = subcategory_entry.get().strip()

    if not category or not subcategory:
        messagebox.showwarning("Champs manquants", "Veuillez entrer une catégorie et une sous-catégorie.")
        return

    # Créer la structure si elle n'existe pas
    if category not in file_structure:
        file_structure[category] = {}
    if subcategory not in file_structure[category]:
        file_structure[category][subcategory] = []

    # Ajouter le fichier
    file_structure[category][subcategory].append(filepath)
    update_treeview()

# Fonction pour mettre à jour l'arborescence
def update_treeview():
    tree.delete(*tree.get_children())
    for category, subcats in file_structure.items():
        cat_id = tree.insert("", "end", text=category)
        for subcategory, files in subcats.items():
            subcat_id = tree.insert(cat_id, "end", text=subcategory)
            for f in files:
                tree.insert(subcat_id, "end", text=os.path.basename(f), values=(f,))

# Fonction pour ouvrir un fichier Excel
def open_file(event):
    selected_item = tree.focus()
    file_path = tree.item(selected_item, "values")
    if file_path:
        try:
            subprocess.Popen(["start", "", file_path[0]], shell=True)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier : {e}")

# Interface graphique
def main():
    global category_entry, subcategory_entry, tree

    root = tk.Tk()
    root.title("Gestionnaire de fichiers Excel")
    root.geometry("700x500")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    tk.Label(frame, text="Catégorie :").grid(row=0, column=0, padx=5)
    category_entry = tk.Entry(frame)
    category_entry.grid(row=0, column=1, padx=5)

    tk.Label(frame, text="Sous-catégorie :").grid(row=0, column=2, padx=5)
    subcategory_entry = tk.Entry(frame)
    subcategory_entry.grid(row=0, column=3, padx=5)

    add_button = tk.Button(frame, text="Ajouter un fichier Excel", command=add_file)
    add_button.grid(row=0, column=4, padx=5)

    tree = ttk.Treeview(root)
    tree["columns"] = ("Chemin complet",)
    tree.column("#0", width=250)
    tree.column("Chemin complet", width=400)
    tree.heading("#0", text="Nom")
    tree.heading("Chemin complet", text="Chemin complet")
    tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree.bind("<Double-1>", open_file)

    root.mainloop()

if __name__ == "__main__":
    main()
