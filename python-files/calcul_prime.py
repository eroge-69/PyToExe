Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import messagebox
... 
... def calculer_prime():
...     try:
...         salaire_base = float(entry_salaire_base.get())
...         iep = float(entry_iep.get())
... 
...         prime_brute = (salaire_base * 0.30) + iep
...         cnas = prime_brute * 0.09
...         prime_nette = prime_brute - cnas
... 
...         label_resultat.config(
...             text=f"Prime brute : {prime_brute:,.2f} DA\n"
...                  f"Retenue CNAS (9%) : {cnas:,.2f} DA\n"
...                  f"Prime nette : {prime_nette:,.2f} DA"
...         )
...     except ValueError:
...         messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")
... 
... # Interface améliorée
... fenetre = tk.Tk()
... fenetre.title("Calculateur de Prime v1.0")
... fenetre.geometry("400x300")
... 
... # Style
... font = ('Arial', 10)
... tk.Label(fenetre, text="Salaire de base (DA)", font=font).pack(pady=5)
... entry_salaire_base = tk.Entry(fenetre, font=font, justify='center')
... entry_salaire_base.pack()
... 
... tk.Label(fenetre, text="IEP (ancienneté)", font=font).pack(pady=5)
... entry_iep = tk.Entry(fenetre, font=font, justify='center')
... entry_iep.pack()
... 
... tk.Button(fenetre, text="Calculer", command=calculer_prime, 
...           bg='#4CAF50', fg='white', font=font).pack(pady=15)
... label_resultat = tk.Label(fenetre, text="", font=font)
... label_resultat.pack()
... pip install pyinstaller
pyinstaller --onefile --windowed --name CalculateurPrime calcul_prime.py
