import random
import tkinter as tk
from tkinter import messagebox

def generer_numeros_principaux():
    return sorted(random.sample(range(1, 51), 5))

def generer_etoiles():
    return sorted(random.sample(range(1, 13), 2))

def generer_et_afficher():
    numeros_principaux = generer_numeros_principaux()
    etoiles = generer_etoiles()
    resultat = f"Numéros principaux : {numeros_principaux}\nÉtoiles : {etoiles}"
    resultat_label.config(text=resultat)

def quitter():
    if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
        fenetre.destroy()  # Utiliser destroy() au lieu de quit()

# Création de la fenêtre principale
fenetre = tk.Tk()
fenetre.title("Générateur Euromillions")
fenetre.geometry("300x200")

# Création des widgets
titre_label = tk.Label(fenetre, text="Générateur de numéros Euromillions", font=("Arial", 12, "bold"))
titre_label.pack(pady=10)

generer_bouton = tk.Button(fenetre, text="Générer", command=generer_et_afficher)
generer_bouton.pack(pady=5)

resultat_label = tk.Label(fenetre, text="", font=("Arial", 10))
resultat_label.pack(pady=10)

quitter_bouton = tk.Button(fenetre, text="Quitter", command=quitter)
quitter_bouton.pack(pady=5)

# Lancement de la boucle principale
fenetre.mainloop()
