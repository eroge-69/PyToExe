import csv
import tkinter as tk
from tkinter import messagebox

# Fehlerdaten aus der CSV-Datei laden
def lade_fehlerkombinationen(dateipfad):
    fehler_dict = {}
    with open(dateipfad, encoding='latin1') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for row in reader:
            if len(row) == 2:
                try:
                    code = int(row[0].strip())
                    beschreibung = row[1].strip()
                    fehler_dict[code] = beschreibung
                except ValueError:
                    continue
    return fehler_dict

# Funktion zur Anzeige der Fehlerbeschreibung
def fehler_suchen():
    eingabe = entry_code.get()
    try:
        code = int(eingabe)
        beschreibung = fehler_dict.get(code, "Unbekannter Fehlercode.")
        label_ergebnis.config(text=f"Fehlercode {code}: {beschreibung}")
    except ValueError:
        messagebox.showerror("Ungültige Eingabe", "Bitte eine gültige Zahl eingeben.")

# Fehlerdaten laden
fehler_dict = lade_fehlerkombinationen("fehlerkombinationen 1.csv")

# GUI erstellen
root = tk.Tk()
root.title("Fehlercode-Suche")

tk.Label(root, text="Fehlercode eingeben:").pack(pady=5)
entry_code = tk.Entry(root)
entry_code.pack(pady=5)

tk.Button(root, text="Suchen", command=fehler_suchen).pack(pady=5)

label_ergebnis = tk.Label(root, text="", wraplength=400, justify="left")
label_ergebnis.pack(pady=10)

# GUI starten
root.mainloop()
