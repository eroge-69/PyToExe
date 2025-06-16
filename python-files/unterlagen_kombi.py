import tkinter as tk
from tkinter import messagebox, scrolledtext
from itertools import combinations
from collections import Counter

# Unterlagen-Daten (Breite x Höhe, 2 Stück pro Größe)
unterlagen_liste = [
    (8, 12), (8, 16), (8, 21), (8, 26), (8, 31), (8, 36),
    (10, 13), (10, 18), (10, 23), (10, 28), (10, 33), (10, 38),
    (12, 15), (12, 20), (12, 25), (12, 30), (12, 35), (12, 40),
    (14, 17), (14, 22), (14, 27), (14, 32), (14, 37), (14, 42)
] * 2  # jeweils 2 Stück pro Größe

def finde_kombis(ziel):
    ergebnisse = set()
    for n in range(1, 7):
        for kombi in combinations(sorted(range(len(unterlagen_liste))), n):
            zaehler = Counter([unterlagen_liste[i] for i in kombi])
            if any(v > 2 for v in zaehler.values()):
                continue
            summe = sum(unterlagen_liste[i][1] for i in kombi)
            if summe == ziel:
                # Kombination nach Größe sortieren, damit "doppelte" erkannt werden
                kombi_sortiert = sorted([unterlagen_liste[i] for i in kombi])
                beschreibung = ' + '.join([f"{b}x{h}" for b, h in kombi_sortiert])
                ergebnisse.add(beschreibung)
    return sorted(ergebnisse)

def suche():
    ausgabe.config(state='normal')
    ausgabe.delete('1.0', tk.END)
    try:
        zielhoehe = int(eingabe.get())
    except ValueError:
        messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben.")
        return
    if zielhoehe > 50:
        messagebox.showwarning("Hinweis", "Maximal 50 mm Höhe erlaubt!")
        return
    kombis = finde_kombis(zielhoehe)
    if kombis:
        ausgabe.insert(tk.END, "\n".join(kombis))
    else:
        ausgabe.insert(tk.END, "Keine Kombination gefunden.")
    ausgabe.config(state='disabled')

# Fenster bauen
root = tk.Tk()
root.title("Unterlagen-Kombinator")

tk.Label(root, text="Benötigte Höhe (mm):").pack()
eingabe = tk.Entry(root, font=("Arial", 16))
eingabe.pack(pady=5)

tk.Button(root, text="Kombinationen suchen", font=("Arial", 14), command=suche).pack(pady=5)

ausgabe = scrolledtext.ScrolledText(root, width=50, height=15, font=("Arial", 16))
ausgabe.pack(pady=5)
ausgabe.config(state='disabled')

root.mainloop()
