Python 3.13.5 (tags/v3.13.5:6cb20a2, Jun 11 2025, 16:15:46) [MSC v.1943 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import tkinter as tk
from tkinter import messagebox

def calculer_prime():
    try:
        salaire_base = float(entry_salaire_base.get())
        iep = float(entry_iep.get())

        # Calculs
        prime_brute = (salaire_base * 0.30) + iep
        cnas = prime_brute * 0.09
        prime_nette = prime_brute - cnas

        # Formatage des résultats
        resultat = (
            f"Prime brute : {prime_brute:,.2f} DA\n"
            f"Retenue CNAS (9%) : {cnas:,.2f} DA\n"
            f"Prime nette : {prime_nette:,.2f} DA"
        )
        label_resultat.config(text=resultat)

    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides.")

def reinitialiser():
    entry_salaire_base.delete(0, tk.END)
    entry_iep.delete(0, tk.END)
    label_resultat.config(text="")
    entry_salaire_base.focus()

# Création de l'interface
fenetre = tk.Tk()
fenetre.title("Calcul de la prime de rendement")
fenetre.geometry("400x350")
fenetre.resizable(False, False)

# Police
font_label = ('Arial', 10)
font_entry = ('Arial', 10)
font_button = ('Arial', 10, 'bold')

# Cadre principal
main_frame = tk.Frame(fenetre, padx=20, pady=20)
main_frame.pack(expand=True, fill='both')

# Entrée salaire
tk.Label(main_frame, text="Salaire de base (DA)", font=font_label).pack(pady=(0, 5))
entry_salaire_base = tk.Entry(main_frame, font=font_entry, justify='center')
entry_salaire_base.pack(pady=(0, 10))

# Entrée IEP
tk.Label(main_frame, text="IEP (ancienneté)", font=font_label).pack(pady=(0, 5))
entry_iep = tk.Entry(main_frame, font=font_entry, justify='center')
entry_iep.pack(pady=(0, 15))

... # Boutons
... tk.Button(
...     main_frame,
...     text="Calculer",
...     command=calculer_prime,
...     font=font_button,
...     bg='#4CAF50',
...     fg='white',
...     relief=tk.FLAT,
...     padx=10,
...     pady=5
... ).pack(pady=(0, 5))
... 
... tk.Button(
...     main_frame,
...     text="Réinitialiser",
...     command=reinitialiser,
...     font=font_button,
...     bg='#f44336',
...     fg='white',
...     relief=tk.FLAT,
...     padx=10,
...     pady=5
... ).pack()
... 
... # Résultat
... label_resultat = tk.Label(
...     main_frame,
...     text="",
...     font=('Arial', 11, 'bold'),
...     fg='#333333',
...     pady=20
... )
... label_resultat.pack()
... 
... # Focus initial
... entry_salaire_base.focus()
... 
... fenetre.mainloop()
