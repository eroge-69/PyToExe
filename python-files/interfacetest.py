import tkinter as tk
from tkinter import simpledialog, messagebox

max_punkte = 0
anzahl_teilnehmer = 0
punktzahl_liste = []
noten_liste = []


def setze_max_punkte():
    global max_punkte
    punkte = simpledialog.askinteger("Maximale Punktzahl", "Maximal mögliche Punktzahl eingeben:")
    if punkte is not None:
        max_punkte = punkte
        messagebox.showinfo("Erfasst", f"Maximale Punktzahl: {max_punkte}")
    else:
        messagebox.showwarning("Abgebrochen", "Keine Punktzahl eingegeben.")


def setze_anzahl_teilnehmer():
    global anzahl_teilnehmer
    teilnehmer = simpledialog.askinteger("Anzahl Teilnehmer", "Anzahl der Teilnehmer eingeben:")
    if teilnehmer is not None:
        anzahl_teilnehmer = teilnehmer
        messagebox.showinfo("Erfasst", f"Teilnehmeranzahl: {anzahl_teilnehmer}")
    else:
        messagebox.showwarning("Abgebrochen", "Keine Teilnehmerzahl eingegeben.")


def erfasse_punkte():
    global punktzahl_liste
    if anzahl_teilnehmer == 0 or max_punkte == 0:
        messagebox.showerror("Fehler", "Bitte zuerst maximale Punktzahl und Teilnehmerzahl eingeben.")
        return

    punktzahl_liste.clear()
    for i in range(anzahl_teilnehmer):
        punkte = simpledialog.askfloat("Punkteingabe", f"Punkte für Teilnehmer {i + 1} eingeben:")
        if punkte is not None:
            punktzahl_liste.append(punkte)
        else:
            messagebox.showwarning("Abgebrochen", "Eingabe abgebrochen.")
            return

    messagebox.showinfo("Fertig", f"Alle Punkte erfasst: {punktzahl_liste}")


def berechne_noten():
    if not punktzahl_liste or max_punkte == 0:
        messagebox.showerror("Fehler", "Bitte erst Punkte und maximale Punktzahl erfassen.")
        return

    ergebnisse = ""
    noten_liste.clear()

    for index, punkte in enumerate(punktzahl_liste):
        prozent = (punkte / max_punkte) * 100

        # Note bestimmen
        if prozent >= 90:
            note = 1
        elif prozent >= 80:
            note = 2
        elif prozent >= 65:
            note = 3
        elif prozent >= 50:
            note = 4
        elif prozent >= 30:
            note = 5
        else:
            note = 6

        noten_liste.append(note)

        ergebnisse += (
            f"Teilnehmer {index + 1}:\n"
            f"  Punkte: {punkte} von {max_punkte}\n"
            f"  Prozent: {prozent:.2f} %\n"
            f"  Note: {note}\n\n"
        )

    durchschnitt = sum(noten_liste) / len(noten_liste)
    ergebnisse += f"Durchschnittsnote der Klasse: {durchschnitt:.2f}"

    # Ergebnisse im Dialog anzeigen (großes Textfenster)
    ergebnis_fenster = tk.Toplevel()
    ergebnis_fenster.title("Notenübersicht")
    textfeld = tk.Text(ergebnis_fenster, width=50, height=25)
    textfeld.pack()
    textfeld.insert(tk.END, ergebnisse)
    textfeld.config(state='disabled')


def starte_gui():
    root = tk.Tk()
    root.title("Notenrechner")
    root.geometry("400x400")
    root.configure(bg="lightblue")  # Hintergrundfarbe setzen

    tk.Button(root, text="Maximale Punktzahl eingeben", command=setze_max_punkte, bg="white").pack(pady=5)
    tk.Button(root, text="Anzahl Teilnehmer eingeben", command=setze_anzahl_teilnehmer, bg="white").pack(pady=5)
    tk.Button(root, text="Punkte der Teilnehmer erfassen", command=erfasse_punkte, bg="white").pack(pady=5)
    tk.Button(root, text="Noten berechnen & anzeigen", command=berechne_noten, bg="white").pack(pady=10)

    root.mainloop()



if __name__ == "__main__":
    starte_gui()
