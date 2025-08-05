import tkinter as tk
from tkinter import messagebox
import re

def texte_en_hashtags(texte):
    texte = texte.strip().lower()
    # Autoriser lettres arabes, lettres latines, chiffres, underscore et espace
    texte = re.sub(r'[^\w\u0600-\u06FF\s]', '', texte)  # \w = [a-zA-Z0-9_]
    mots = texte.split()
    hashtags = ['#' + mot for mot in mots if mot]
    return ' '.join(hashtags)

def generer_hashtags():
    texte = entree.get()
    if not texte:
        messagebox.showwarning("تنبيه / Attention", "Veuillez entrer un texte.")
        return
    resultat = texte_en_hashtags(texte)
    sortie.config(state='normal')
    sortie.delete(0, tk.END)
    sortie.insert(0, resultat)
    sortie.config(state='readonly')

# Interface graphique
fenetre = tk.Tk()
fenetre.title("مولد الوسوم / Générateur de Hashtags")
fenetre.geometry("600x250")
fenetre.resizable(False, False)

# Texte d'entrée
label = tk.Label(fenetre, text="أدخل نصك / Entrez votre texte :", font=("Arial", 12))
label.pack(pady=10)

entree = tk.Entry(fenetre, width=70, justify='right', font=("Arial", 12))
entree.pack(pady=5)

# Bouton
btn = tk.Button(fenetre, text="توليد الوسوم / Générer les hashtags", command=generer_hashtags)
btn.pack(pady=10)

# Sortie
sortie = tk.Entry(fenetre, width=70, state='readonly', justify='right', font=("Arial", 12))
sortie.pack(pady=5)

# Boucle
fenetre.mainloop()
