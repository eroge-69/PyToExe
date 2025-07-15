
import tkinter as tk
from tkinter import messagebox

def calculer_prime():
    try:
        salaire_base = float(entry_salaire_base.get())
        iep = float(entry_iep.get())

        # Calcul brut
        prime_brute = (salaire_base * 0.30) + iep

        # Retenue CNAS 9%
        cnas = prime_brute * 0.09
        prime_nette = prime_brute - cnas

        # Affichage des résultats
        label_resultat.config(
            text=f"Prime brute : {prime_brute:.2f} DA\nRetenue CNAS (9%) : {cnas:.2f} DA\nPrime nette : {prime_nette:.2f} DA"
        )

    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

# Interface
fenetre = tk.Tk()
fenetre.title("Calcul de la prime de rendement")

tk.Label(fenetre, text="Salaire de base (DA)").pack()
entry_salaire_base = tk.Entry(fenetre)
entry_salaire_base.pack()

tk.Label(fenetre, text="IEP (ancienneté)").pack()
entry_iep = tk.Entry(fenetre)
entry_iep.pack()

tk.Button(fenetre, text="Calculer", command=calculer_prime).pack(pady=10)
label_resultat = tk.Label(fenetre, text="")
label_resultat.pack()

fenetre.mainloop()
pyinstaller --onefile --windowed calcul_prime.py


