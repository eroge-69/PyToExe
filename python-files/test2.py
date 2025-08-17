import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext

# 🔧 Mets ici le chemin vers ton fichier Excel
FICHIER = "C:\\Users\\MariemBY\\Downloads\\Etat d'avancement des travaux de migration.xlsx"

# Charger le fichier
df = pd.read_excel(FICHIER)

# Nettoyer la colonne A (codes)
codes = df.iloc[:, 0].astype(str).str.strip().unique().tolist()

# Fonction de recherche
def rechercher():
    code_saisi = combo.get().strip()
    mask = df.iloc[:, 0].astype(str).str.strip() == code_saisi
    
    if mask.any():
        # Colonnes B + D → K
        colonnes = [df.columns[1]] + list(df.columns[3:11])
        resultat = df.loc[mask, colonnes]
        
        # Afficher dans la zone de texte
        output.delete("1.0", tk.END)
        output.insert(tk.END, resultat.to_string(index=False))
    else:
        output.delete("1.0", tk.END)
        output.insert(tk.END, "❌ Code introuvable")

# --- Interface ---
root = tk.Tk()
root.title("Recherche Code Excel")
root.geometry("600x400")

# Liste déroulante
tk.Label(root, text="Sélectionnez un code :", font=("Arial", 12)).pack(pady=5)
combo = ttk.Combobox(root, values=codes, width=30, state="readonly")
combo.pack(pady=5)

# Bouton rechercher
btn = tk.Button(root, text="Rechercher", command=rechercher, font=("Arial", 12), bg="lightblue")
btn.pack(pady=5)

# Zone de texte résultat
output = scrolledtext.ScrolledText(root, width=70, height=15, font=("Consolas", 10))
output.pack(pady=10)

# Lancer l'application
root.mainloop()
