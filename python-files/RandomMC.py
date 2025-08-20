import tkinter as tk
import random

# Paramètres du loto 5/49 + 1/10
total_numeros = 49
total_chance = 10
choix = 5
num_chance = 1

# Fonction de tirage
def tirage_loto():
    # Tirage aléatoire des 5 premiers numéros parmi les 49
    tirage_numero = set(random.sample(range(1, total_numeros + 1), choix))
    # Tirage du numéro chance parmi les 10
    tirage_chance = random.choice(range(1, total_chance + 1))
    
    result_label.config(text=f"Tirage: {sorted(tirage_numero)} + Chance: {tirage_chance}")

# Créer la fenêtre principale
root = tk.Tk()
root.title("Simulation de Tirage Loto")

# Ajouter un bouton pour lancer le tirage
tirage_button = tk.Button(root, text="Tirer les numéros", command=tirage_loto, font=("Helvetica", 16))
tirage_button.pack(pady=20)

# Ajouter une étiquette pour afficher le résultat
result_label = tk.Label(root, text="Résultat du tirage", font=("Helvetica", 16))
result_label.pack(pady=20)

# Lancer l'application
root.mainloop()
