
import tkinter as tk
from tkinter import messagebox

def calcola_quota(potenza, mentale, concentrazione, rosa, atletica, campo):
    try:
        potenza = float(potenza)
        mentale = float(mentale)
        concentrazione = float(concentrazione)
        rosa = float(rosa)
        atletica = float(atletica)
        campo = float(campo)

        probabilita = (
            potenza * 0.65 +
            mentale * 0.10 +
            concentrazione * 0.10 +
            rosa * 0.05 +
            atletica * 0.02 +
            campo * 0.03
        )

        if probabilita == 0:
            return None, "Probabilità nulla, impossibile calcolare la quota."

        quota_stimata = 100 / probabilita
        return quota_stimata, None
    except ValueError:
        return None, "Inserisci solo numeri validi."

def esegui_calcolo():
    quota_bookmaker = entry_bookmaker.get()
    try:
        quota_bookmaker = float(quota_bookmaker)
    except ValueError:
        messagebox.showerror("Errore", "Inserisci una quota bookmaker valida (numero).")
        return

    quota, errore = calcola_quota(
        entry_potenza.get(),
        entry_mentale.get(),
        entry_concentrazione.get(),
        entry_rosa.get(),
        entry_atletica.get(),
        entry_campo.get()
    )

    if errore:
        messagebox.showerror("Errore", errore)
    else:
        risultato = f"Quota stimata: {quota:.2f}\n"
        if quota < quota_bookmaker:
            risultato += "✅ Possibile VALUE BET!"
        else:
            risultato += "❌ Nessun valore trovato."
        messagebox.showinfo("Risultato", risultato)

root = tk.Tk()
root.title("Analisi Quota Partita - Calcolo Value Bet")
root.geometry("400x450")

labels = [
    "Potenza squadra (0-100)",
    "Condizione mentale (0-100)",
    "Concentrazione partita (0-100)",
    "Rosa completa (0-100)",
    "Condizione atletica (0-100)",
    "Fattore campo (0-100)",
    "Quota Bookmaker"
]

entries = []

for i, text in enumerate(labels):
    label = tk.Label(root, text=text)
    label.pack()
    entry = tk.Entry(root)
    entry.pack()
    entries.append(entry)

entry_potenza = entries[0]
entry_mentale = entries[1]
entry_concentrazione = entries[2]
entry_rosa = entries[3]
entry_atletica = entries[4]
entry_campo = entries[5]
entry_bookmaker = entries[6]

button = tk.Button(root, text="Calcola quota stimata", command=esegui_calcolo)
button.pack(pady=20)

root.mainloop()
