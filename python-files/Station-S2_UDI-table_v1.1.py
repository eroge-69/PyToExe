import tkinter as tk
from tkinter import ttk

# --- Table de sortie fixe (à personnaliser selon tes besoins) ---
# Format : tuple des réponses ("oui"/"non") → sortie
# Il faut couvrir les 2^5 = 32 cas possibles

nb_produits = 5
liste_produits = ["Oxymètre", "Tensiomètre", "Glucomètre", "Télécardia", "Thermomètre"]

table_sortie = {
    ('oui', 'oui', 'oui', 'oui', 'oui'): "3770028219131",
    ('oui', 'oui', 'oui', 'oui', 'non'): "Non Défini 1",
    ('oui', 'oui', 'oui', 'non', 'oui'): "Non Défini 2",
    ('oui', 'oui', 'oui', 'non', 'non'): "Non Défini 3",
    ('oui', 'oui', 'non', 'oui', 'oui'): "Non Défini 4",
    ('oui', 'oui', 'non', 'oui', 'non'): "Non Défini 5",
    ('oui', 'oui', 'non', 'non', 'oui'): "Non Défini 6",
    ('oui', 'oui', 'non', 'non', 'non'): "Non Défini 7",
    ('oui', 'non', 'oui', 'oui', 'oui'): "Non Défini 8",
    ('oui', 'non', 'oui', 'oui', 'non'): "Non Défini 9",
    ('oui', 'non', 'oui', 'non', 'oui'): "Non Défini 10",
    ('oui', 'non', 'oui', 'non', 'non'): "Non Défini 11",
    ('oui', 'non', 'non', 'oui', 'oui'): "Non Défini 12",
    ('oui', 'non', 'non', 'oui', 'non'): "Non Défini 13",
    ('oui', 'non', 'non', 'non', 'oui'): "Non Défini 14",
    ('oui', 'non', 'non', 'non', 'non'): "Non Défini 15",
    ('non', 'oui', 'oui', 'oui', 'oui'): "Non Défini 16",
    ('non', 'oui', 'oui', 'oui', 'non'): "Non Défini 17",
    ('non', 'oui', 'oui', 'non', 'oui'): "Non Défini 18",
    ('non', 'oui', 'oui', 'non', 'non'): "Non Défini 19",
    ('non', 'oui', 'non', 'oui', 'oui'): "Non Défini 20",
    ('non', 'oui', 'non', 'oui', 'non'): "Non Défini 21",
    ('non', 'oui', 'non', 'non', 'oui'): "Non Défini 22",
    ('non', 'oui', 'non', 'non', 'non'): "Non Défini 23",
    ('non', 'non', 'oui', 'oui', 'oui'): "Non Défini 24",
    ('non', 'non', 'oui', 'oui', 'non'): "Non Défini 25",
    ('non', 'non', 'oui', 'non', 'oui'): "Non Défini 26",
    ('non', 'non', 'oui', 'non', 'non'): "Non Défini 27",
    ('non', 'non', 'non', 'oui', 'oui'): "Non Défini 28",
    ('non', 'non', 'non', 'oui', 'non'): "Non Défini 29",
    ('non', 'non', 'non', 'non', 'oui'): "Non Défini 30",
    ('non', 'non', 'non', 'non', 'non'): "Non Défini 31"
}

# Remplissage par défaut (exemple générique)
from itertools import product
for combinaison in product(["oui", "non"], repeat=nb_produits):
    table_sortie.setdefault(combinaison, f"Sortie générique pour {combinaison}")

# --- GUI ---
def mettre_a_jour_sortie():
    etats = tuple("oui" if var.get() else "non" for var in check_vars)
    sortie = table_sortie.get(etats, "Aucune sortie définie")
    label_sortie.config(text=f"L'UDI correspondant est : {sortie}")

# Créer la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Choix d'entrées")

check_vars = []
for i in range(nb_produits):
    var = tk.BooleanVar()
    check = ttk.Checkbutton(fenetre, text=liste_produits[i], variable=var, command=mettre_a_jour_sortie)
    check.grid(row=i, column=0, sticky="w", padx=10, pady=5)
    check_vars.append(var)

label_sortie = ttk.Label(fenetre, text="L'UDI correspondant est : ", font=("Arial", 14))
label_sortie.grid(row=6, column=0, padx=10, pady=20)

fenetre.mainloop()
