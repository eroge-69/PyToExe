import tkinter as tk
from tkinter import messagebox
import json
import os
def enregistrer():
    # Récupérer ce que l'utilisateur a tapé
    cle = entree_cle.get()
    mot_de_passe = entree_mdp.get()

    # Vérifier que les deux champs sont remplis
    if not cle or not mot_de_passe:
        messagebox.showwarning("Erreur", "Remplis les deux champs.")
        return

    # Charger les anciens mots de passe s'ils existent
    if os.path.exists("mots_de_passe.json"):
        with open("mots_de_passe.json", "r") as f:
            data = json.load(f)
    else:
        data = {}

    # Ajouter le nouveau mot de passe
    data[cle] = mot_de_passe

    # Sauvegarder dans le fichier
    with open("mots_de_passe.json", "w") as f:
        json.dump(data, f)

    # Confirmer à l'utilisateur
    messagebox.showinfo("Succès", "Mot de passe enregistré.")

    # Vider les champs
    entree_cle.delete(0, tk.END)
    entree_mdp.delete(0, tk.END)
    def retrouver():
    cle = entree_cle.get()

    if not cle:
        messagebox.showwarning("Erreur", "Tape un mot-clé pour chercher.")
        return

    if os.path.exists("mots_de_passe.json"):
        with open("mots_de_passe.json", "r") as f:
            data = json.load(f)

        mot_de_passe = data.get(cle)

        if mot_de_passe:
            messagebox.showinfo("Mot de passe trouvé", f"{cle} : {mot_de_passe}")
        else:
            messagebox.showerror("Introuvable", "Aucun mot de passe trouvé pour ce mot-clé.")
    else:
        messagebox.showerror("Erreur", "Le fichier des mots de passe n'existe pas encore.")


fenetre = tk.Tk()
fenetre.title("gestionnaire de mot de passe")
tk.Label(fenetre, text="mot cle").grid(row=0, column=0, padx=10, pady=5)
entree_cle= tk.Entry(fenetre)
entree_cle.grid(row=0, column=1, padx=10, pady=5)
tk.Label(fenetre, text="mot de passe").grid(row=1, column=0, padx=10, pady=5)
entree_mdp = tk.Entry(fenetre, show='*')
entree_mdp.grid(row=1, column=1, padx=10, pady=5)
btn_enregistrer = tk.Button(fenetre, text="Enregistrer", command=lambda: enregistrer())
btn_enregistrer.grid(row=2, column=0, padx=10, pady=10)
btn_retrouver = tk.Button(fenetre, text="Retrouver", command=lambda: retrouver())
btn_retrouver.grid(row=2, column=1, padx=10, pady=10)

fenetre.mainloop()