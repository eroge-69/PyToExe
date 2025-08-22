Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import pandas as pd
import tkinter as tk
from tkinter import ttk

# === 1) Charger ton fichier Excel ===
FICHIER = r"C:\Users\MariemBY\Downloads\Etat d'avancement des travaux de migration.xlsx"
df = pd.read_excel(FICHIER)

# Nettoyer la première colonne (codes)
df.iloc[:, 0] = df.iloc[:, 0].astype(str).str.replace('\u00A0', ' ', regex=False).str.strip()

# === 2) Création de la fenêtre principale ===
root = tk.Tk()
root.title("Suivi Migration")
root.geometry("800x400")

# === 3) Combobox pour sélectionner agence ===
label = tk.Label(root, text="Sélectionnez une agence :")
label.pack(pady=5)

# Exemple : suppose que la 1ère colonne contient les agences/codes
agences = df.iloc[:, 0].dropna().unique().tolist()
combo = ttk.Combobox(root, values=agences)
combo.pack(pady=5)

# === 4) Bouton de recherche ===
def rechercher():
    # Récupérer la sélection
    code_saisi = combo.get().strip()
    if not code_saisi:
        return
... 
...     # Filtrer
...     mask = df.iloc[:, 0] == code_saisi
...     if not mask.any():
...         return
... 
...     colonnes_a_afficher = [df.columns[1]] + list(df.columns[3:11])
...     resultat = df.loc[mask, colonnes_a_afficher]
... 
...     # Supprimer titre "Statuts"
...     resultat = resultat.rename(columns={"Statuts": ""})
... 
...     # === 5) Remplir le Treeview ===
...     for item in tree.get_children():
...         tree.delete(item)
... 
...     tree["columns"] = list(resultat.columns)
...     tree["show"] = "headings"
... 
...     for col in resultat.columns:
...         tree.heading(col, text=col)  # col sera "" pour Statuts → pas de titre
...         tree.column(col, width=80, anchor="center")
... 
...     # Ajouter les lignes
...     for _, row in resultat.iterrows():
...         tree.insert("", "end", values=list(row))
... 
... btn = tk.Button(root, text="Rechercher", command=rechercher, bg="lightblue")
... btn.pack(pady=5)
... 
... # === 6) Tableau Treeview ===
... tree = ttk.Treeview(root)
... tree.pack(fill="both", expand=True, padx=10, pady=10)
... 
... # === 7) Lancer l'application ===
... root.mainloop()
... 
SyntaxError: multiple statements found while compiling a single statement
>>> 
