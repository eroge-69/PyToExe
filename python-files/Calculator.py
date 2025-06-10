import tkinter as tk
from tkinter import messagebox

def calculeaza_unghiuri():
    try:
        unghi_dorit = float(entry.get())
        if not 0 < unghi_dorit < 180:
            raise ValueError
        unghi_taiere = round((180 - unghi_dorit) / 2, 2)
        rezultat.config(
            text=f"Fiecare profil trebuie tăiat la {unghi_taiere}°"
        )
    except ValueError:
        messagebox.showerror("Eroare", "Introduceți un unghi valid între 0 și 180 (exclusiv).")

# Creare fereastră
root = tk.Tk()
root.title("Calculator unghiuri de debitare profile aluminiu")
root.geometry("400x200")

# Elemente UI
eticheta = tk.Label(root, text="Introduceți unghiul dorit în îmbinare (°):")
eticheta.pack(pady=10)

entry = tk.Entry(root, width=10, justify='center')
entry.pack()

buton = tk.Button(root, text="Calculează", command=calculeaza_unghiuri)
buton.pack(pady=10)

rezultat = tk.Label(root, text="", font=("Helvetica", 12))
rezultat.pack(pady=10)

# Rulează aplicația
root.mainloop()
