import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from datetime import datetime, timedelta

def berechne_zeit():
    try:
        stunde = int(stunden_combobox.get())
        minute = int(minuten_combobox.get())
        arbeitsbeginn = datetime.strptime(f"{stunde}:{minute}", "%H:%M")

        # 7,6 Stunden in Stunden und Minuten umwandeln
        arbeitszeit = timedelta(hours=7, minutes=36)

        # Zusätzliche Zeiten hinzufügen, wenn die Checkbox aktiviert sind
        if zusatz_checkbox.var.get():  # Wenn der Haken gesetzt ist
            arbeitszeit += timedelta(minutes=30)  # Mittagspause hinzufügen
        if fruehstueck_checkbox.var.get():  # Wenn der Haken gesetzt ist
            arbeitszeit += timedelta(minutes=15)  # Frühstück hinzufügen

        endzeit = arbeitsbeginn + arbeitszeit

        # Ergebnis anzeigen
        ergebnis_var.set(f"Arbeitsende: {endzeit.strftime('%H:%M')}")
    except ValueError:
        messagebox.showerror("Fehler", "Bitte wählen Sie gültige Uhrzeiten aus.")

# Erstellt das Hauptfenster
root = tk.Tk()
root.title("Arbeitszeitrechner")

# Setze die Fenstergröße (Breite x Höhe)
fenster_breite = 250
fenster_hoehe = 280
root.geometry(f"{fenster_breite}x{fenster_hoehe}")

# Berechne die Position für das Öffnen des Fensters in der unteren rechten Ecke
root.update_idletasks()  # Berechne die Fenstergröße
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x_position = screen_width - fenster_breite - 13
y_position = screen_height - fenster_hoehe - 85

# Setze die Fensterposition
root.geometry(f"{fenster_breite}x{fenster_hoehe}+{x_position}+{y_position}")

# Eingabefelder für Arbeitsbeginn
tk.Label(root, text="Arbeitsbeginn:").grid(row=0, column=0, columnspan=4, padx=5, pady=5)

# Stunden Combobox
stunden = [f"{i:02}" for i in range(24)]  # Stunden von 00 bis 23
stunden_combobox = ttk.Combobox(root, values=stunden, width=3)
stunden_combobox.set("07")

# Minuten Combobox
minuten = [f"{i:02}" for i in range(60)]  # Minuten von 00 bis 59
minuten_combobox = ttk.Combobox(root, values=minuten, width=3)
minuten_combobox.set("30")

# Positioniere die Comboboxen und das Label "Uhr" nebeneinander
stunden_combobox.grid(row=1, column=0, padx=2, pady=5)
tk.Label(root, text=":").grid(row=1, column=1, padx=2, pady=5)  # ":" zwischen Stunden und Minuten
minuten_combobox.grid(row=1, column=2, padx=2, pady=5)
tk.Label(root, text="Uhr").grid(row=1, column=3, padx=2, pady=5)  # Abstand von 5 Pixeln für "Uhr"

# Checkbox für Frühstückspause
fruehstueck_checkbox = tk.Checkbutton(root, text="Frühstück (+15min)")
fruehstueck_checkbox.var = tk.BooleanVar(value=True)  # Standardwert ist True
fruehstueck_checkbox['variable'] = fruehstueck_checkbox.var
fruehstueck_checkbox.grid(row=2, column=0, columnspan=4, pady=5)

# Checkbox für Mittagspause
zusatz_checkbox = tk.Checkbutton(root, text="Mittagspause (+30min)")
zusatz_checkbox.var = tk.BooleanVar(value=True)  # Standardwert ist True
zusatz_checkbox['variable'] = zusatz_checkbox.var
zusatz_checkbox.grid(row=3, column=0, columnspan=4, pady=5)

# Variable zur Anzeige des Ergebnisses
ergebnis_var = tk.StringVar(value="")

# Label zur Anzeige der berechneten Uhrzeit
ergebnis_label = tk.Label(root, textvariable=ergebnis_var, font=("Arial", 12, "bold"))
ergebnis_label.grid(row=4, column=0, columnspan=4, pady=5)

# Berechnen-Button
berechnen_button = tk.Button(root, text="Berechnen", command=berechne_zeit)
berechnen_button.grid(row=5, column=0, columnspan=4, pady=20)

# Zentrale Ausrichtung durch Konfiguration der Zeilen und Spalten
for i in range(6):
    root.grid_rowconfigure(i, weight=1)  # Jede Zeile hat das gleiche Gewicht
for i in range(4):
    root.grid_columnconfigure(i, weight=1)  # Jede Spalte hat das gleiche Gewicht

# Hauptloop der GUI
root.mainloop()