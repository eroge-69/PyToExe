import tkinter as tk  # Importiert das Modul für grafische Oberflächen
import random          # Importiert das Modul für Zufallsfunktionen

# Liste von Begriffen, aus denen zufällig gewählt wird
spezaufnahmen = ["Greenspan", "Radiusköpfchen", "Outlet", "Inlet", "Calcaneus axial"]

# Funktion, die beim Buttonklick ausgeführt wird
def begriff_anzeigen():
    # Wählt einen zufälligen Begriff aus der Liste aus
    zufallsbegriff = random.choice(spezaufnahmen)
    # Setzt den Text des Labels auf den zufällig gewählten Begriff
    ausgabe_label.config(text=zufallsbegriff)

# Hauptfenster der Anwendung erstellen
fenster = tk.Tk()  # Erstellt das Hauptfenster
fenster.title("Spezialaufnahmen Zufallsgenerator")  # Setzt den Fenstertitel
fenster.minsize(width=300, height=200)

main_frame = tk.Frame(fenster)
main_frame.pack(expand=True)

# Label zur Ausgabe des Begriffs
ausgabe_label = tk.Label(fenster, text="", font=("Arial", 24))  # Erstellt ein Label mit großer Schrift
ausgabe_label.pack(pady=(20, 10))  # Fügt das Label ins Fenster ein und sorgt für etwas Abstand (padding) 1. Abstand oben, 2. Abstand unten

# Button, der bei Klick die Funktion ausführt
button = tk.Button(fenster, text="Spezialaufnahme", command=begriff_anzeigen, font=("Arial", 14))
button.pack(pady=(0, 20))  # Fügt den Button ins Fenster ein

#automatische Fenstergröße
fenster.update_idletasks()
fenster.geometry(f"{fenster.winfo_reqwidth()}x{fenster.winfo_reqheight()}")

# Startet die Haupt-Schleife des Fensters, damit es angezeigt wird
fenster.mainloop()
