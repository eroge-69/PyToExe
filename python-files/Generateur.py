import random
import string
import tkinter as tk

def generer_mdp():
    longueur = 12
    speciaux = '*!?@%$&'
    mdp = []

    # Forcer au moins 3 types différents
    mdp.append(random.choice(string.ascii_uppercase))  # majuscule
    mdp.append(random.choice(string.ascii_lowercase))  # minuscule
    mdp.append(random.choice(string.digits))           # chiffre
    mdp.append(random.choice(speciaux))                # spécial

    # Compléter le reste aléatoirement
    tous = string.ascii_letters + string.digits + speciaux
    while len(mdp) < longueur:
        mdp.append(random.choice(tous))

    # Mélanger pour éviter un ordre fixe
    random.shuffle(mdp)
    mot_de_passe = ''.join(mdp)

    # Afficher dans le label
    label_resultat.config(text=mot_de_passe)

# Création de la fenêtre
fenetre = tk.Tk()
fenetre.title("Générateur de mot de passe")
fenetre.geometry("350x180")
fenetre.resizable(False, False)

# Affichage du mot de passe
label_resultat = tk.Label(fenetre, text="Cliquez sur Générer", font=("Arial", 14))
label_resultat.pack(pady=20)

# Bouton pour générer
bouton_generer = tk.Button(fenetre, text="🔐 Générer", command=generer_mdp, font=("Arial", 12), bg="#4a90e2", fg="white")
bouton_generer.pack(pady=10)

# Lancer l’interface
fenetre.mainloop()
