import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

def umbenennen(ordner, datum, initialen, titel):
    erlaubte_formate = (".jpg", ".jpeg", ".png")
    dateien = [f for f in os.listdir(ordner) if f.lower().endswith(erlaubte_formate)]

    if not dateien:
        messagebox.showinfo("Info", "Keine JPG- oder PNG-Dateien im Ordner gefunden.")
        return

    dateien.sort()
    for i, datei in enumerate(dateien, start=1):
        dateiendung = os.path.splitext(datei)[1]
        neue_datei = f"{datum}_{initialen}_{titel}_{i}{dateiendung}"
        alter_pfad = os.path.join(ordner, datei)
        neuer_pfad = os.path.join(ordner, neue_datei)
        os.rename(alter_pfad, neuer_pfad)

    messagebox.showinfo("Fertig", f"{len(dateien)} Dateien wurden erfolgreich umbenannt!")

def main():
    # Prüfen ob Drag & Drop Ordner übergeben wurde
    if len(sys.argv) > 1:
        ordner = sys.argv[1]
        if not os.path.isdir(ordner):
            tk.Tk().withdraw()
            messagebox.showerror("Fehler", "Der übergebene Pfad ist kein gültiger Ordner.")
            return
    else:
        # Kein Drag & Drop: Ordner manuell auswählen
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Info", "Ziehe bitte einen Ordner auf die EXE, oder öffne sie erneut und übergebe einen Ordner.")
        return

    # Eingabefenster für Datum, Initialen, Titel
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster

    datum = simpledialog.askstring("Eingabe", "Gib das Datum ein (yyyy-MM-dd):")
    if not datum:
        return
    initialen = simpledialog.askstring("Eingabe", "Gib die Initialen ein:")
    if not initialen:
        return
    titel = simpledialog.askstring("Eingabe", "Gib den Titel ein:")
    if not titel:
        return

    umbenennen(ordner, datum, initialen, titel)

if __name__ == "__main__":
    main()import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

def umbenennen(ordner, datum, initialen, titel):
    erlaubte_formate = (".jpg", ".jpeg", ".png")
    dateien = [f for f in os.listdir(ordner) if f.lower().endswith(erlaubte_formate)]

    if not dateien:
        messagebox.showinfo("Info", "Keine JPG- oder PNG-Dateien im Ordner gefunden.")
        return

    dateien.sort()
    for i, datei in enumerate(dateien, start=1):
        dateiendung = os.path.splitext(datei)[1]
        neue_datei = f"{datum}_{initialen}_{titel}_{i}{dateiendung}"
        alter_pfad = os.path.join(ordner, datei)
        neuer_pfad = os.path.join(ordner, neue_datei)
        os.rename(alter_pfad, neuer_pfad)

    messagebox.showinfo("Fertig", f"{len(dateien)} Dateien wurden erfolgreich umbenannt!")

def main():
    # Prüfen ob Drag & Drop Ordner übergeben wurde
    if len(sys.argv) > 1:
        ordner = sys.argv[1]
        if not os.path.isdir(ordner):
            tk.Tk().withdraw()
            messagebox.showerror("Fehler", "Der übergebene Pfad ist kein gültiger Ordner.")
            return
    else:
        # Kein Drag & Drop: Ordner manuell auswählen
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Info", "Ziehe bitte einen Ordner auf die EXE, oder öffne sie erneut und übergebe einen Ordner.")
        return

    # Eingabefenster für Datum, Initialen, Titel
    root = tk.Tk()
    root.withdraw()  # Versteckt das Hauptfenster

    datum = simpledialog.askstring("Eingabe", "Gib das Datum ein (yyyy-MM-dd):")
    if not datum:
        return
    initialen = simpledialog.askstring("Eingabe", "Gib die Initialen ein:")
    if not initialen:
        return
    titel = simpledialog.askstring("Eingabe", "Gib den Titel ein:")
    if not titel:
        return

    umbenennen(ordner, datum, initialen, titel)

if __name__ == "__main__":
    main()