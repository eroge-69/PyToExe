import tkinter as tk
from tkinter import ttk

def aktualisiere_auswahl():
    label_ergebnis.config(text=f"Du hast {auswahl.get()} ausgewählt.")

# Hauptfenster erstellen
root = tk.Tk()
root.title("Zahlenauswahl")
root.geometry("300x150")

# Label mit Anweisung
label_anweisung = ttk.Label(root, text="Wähle eine Zahl von 1 bis 10:")
label_anweisung.pack(pady=10)

# Dropdown-Menü (Combobox)
auswahl = tk.StringVar()
dropdown = ttk.Combobox(root, textvariable=auswahl, values=[i for i in range(1, 11)])
dropdown.pack(pady=5)
dropdown.set(1)  # Standardwert

# Button zum Bestätigen
button = ttk.Button(root, text="Bestätigen", command=aktualisiere_auswahl)
button.pack(pady=5)

# Label für Ergebnis
label_ergebnis = ttk.Label(root, text="")
label_ergebnis.pack(pady=10)

# Hauptloop starten
root.mainloop()
