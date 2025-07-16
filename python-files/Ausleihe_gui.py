import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

DB_NAME = 'Messmittelausleihe.db'

def erstelle_datenbank():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Haupttabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teile (
            nummer TEXT PRIMARY KEY,
            name TEXT,
            beschreibung TEXT,
            aktueller_standort TEXT,
            kalibrierdatum TEXT,
            entnommen_am TEXT,
            zurueckgebracht_am TEXT
        )
    ''')
    # Historientabelle
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historie (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nummer TEXT,
            aktion TEXT,
            benutzer TEXT,
            zeitpunkt TEXT,
            details TEXT
        )
    ''')
    conn.commit()
    conn.close()

def ist_datum_gueltig(datum):
    if not datum:
        return True
    try:
        datetime.strptime(datum, "%Y-%m-%d")
        return True
    except ValueError:
        return False

def log_historie(nummer, aktion, details, benutzer="System"):
    zeitpunkt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historie (nummer, aktion, benutzer, zeitpunkt, details) VALUES (?, ?, ?, ?, ?)",
        (nummer, aktion, benutzer, zeitpunkt, details)
    )
    conn.commit()
    conn.close()

def suche_teil():
    nummer = eingabe_nummer.get()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, beschreibung, aktueller_standort, kalibrierdatum, entnommen_am, zurueckgebracht_am FROM teile WHERE nummer = ?", (nummer,))
    result = cursor.fetchone()
    conn.close()

    if result:
        name_var.set(result[0])
        beschreibung_var.set(result[1])
        standort_var.set(result[2])
        kalibrierdatum_var.set(result[3] or "")
        entnommen_var.set(result[4] or "")
        zurueck_var.set(result[5] or "")
        dropdown.set(result[2])
    else:
        messagebox.showinfo("Nicht gefunden", f"Messmittel mit Nummer '{nummer}' wurde nicht gefunden.")
        name_var.set("")
        beschreibung_var.set("")
        standort_var.set("")
        kalibrierdatum_var.set("")
        entnommen_var.set("")
        zurueck_var.set("")
        dropdown.set("")

def aktualisiere_standort():
    nummer = eingabe_nummer.get()
    neuer_standort = dropdown.get()
    if not nummer:
        messagebox.showwarning("Fehler", "Bitte zuerst eine Messmittelnummer eingeben und suchen.")
        return
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE teile SET aktueller_standort = ? WHERE nummer = ?", (neuer_standort, nummer))
    conn.commit()
    conn.close()
    standort_var.set(neuer_standort)
    messagebox.showinfo("Erfolgreich", f"Standort für Messmittel '{nummer}' wurde aktualisiert.")
    log_historie(nummer, "Standort geändert", f"Neuer Standort: {neuer_standort}")
    lade_alle_messmittel()

def aktualisiere_stammdaten():
    nummer = eingabe_nummer.get()
    neuer_name = name_var.get()
    neue_beschreibung = beschreibung_var.get()
    neues_kalibrierdatum = kalibrierdatum_var.get()
    entnommen_am = entnommen_var.get()
    zurueckgebracht_am = zurueck_var.get()

    if not nummer:
        messagebox.showwarning("Fehler", "Bitte zuerst eine Messmittelnummer eingeben und suchen.")
        return

    if not ist_datum_gueltig(neues_kalibrierdatum) or not ist_datum_gueltig(entnommen_am) or not ist_datum_gueltig(zurueckgebracht_am):
        messagebox.showerror("Ungültiges Datum", "Bitte gib die Daten im Format JJJJ-MM-TT ein.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE teile 
        SET name = ?, beschreibung = ?, kalibrierdatum = ?, entnommen_am = ?, zurueckgebracht_am = ?
        WHERE nummer = ?
    """, (neuer_name, neue_beschreibung, neues_kalibrierdatum, entnommen_am, zurueckgebracht_am, nummer))
    conn.commit()
    conn.close()
    messagebox.showinfo("Erfolgreich", f"Stammdaten für Messmittel '{nummer}' wurden aktualisiert.")
    details = f"Name: {neuer_name}, Beschreibung: {neue_beschreibung}, Kalibrierdatum: {neues_kalibrierdatum}, Entnommen: {entnommen_am}, Zurückgebracht: {zurueckgebracht_am}"
    log_historie(nummer, "Stammdaten aktualisiert", details)
    lade_alle_messmittel()

def neues_teil_hinzufuegen():
    nummer = neuer_nummer_entry.get()
    name = neuer_name_entry.get()
    beschreibung = neue_beschreibung_entry.get()
    standort = neuer_standort_dropdown.get()
    kalibrierdatum = neues_kalibrierdatum_entry.get()

    if not nummer or not name:
        messagebox.showwarning("Fehlende Eingabe", "Messmittelnr. und Name sind erforderlich.")
        return

    if not ist_datum_gueltig(kalibrierdatum):
        messagebox.showerror("Ungültiges Datum", "Kalibrierdatum ist nicht korrekt (JJJJ-MM-TT).")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO teile (nummer, name, beschreibung, aktueller_standort, kalibrierdatum) VALUES (?, ?, ?, ?, ?)",
                       (nummer, name, beschreibung, standort, kalibrierdatum))
        conn.commit()
        messagebox.showinfo("Erfolgreich", f"Neues Messmittel '{nummer}' wurde hinzugefügt.")
        log_historie(nummer, "Neues Messmittel", f"Name: {name}, Standort: {standort}")
        neuer_nummer_entry.delete(0, tk.END)
        neuer_name_entry.delete(0, tk.END)
        neue_beschreibung_entry.delete(0, tk.END)
        neuer_standort_dropdown.set("")
        neues_kalibrierdatum_entry.delete(0, tk.END)
        lade_alle_messmittel()
    except sqlite3.IntegrityError:
        messagebox.showerror("Fehler", f"Messmittel mit Nummer '{nummer}' existiert bereits.")
    conn.close()

def lade_alle_messmittel():
    for row in tree.get_children():
        tree.delete(row)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT nummer, name, aktueller_standort, kalibrierdatum, entnommen_am, zurueckgebracht_am FROM teile")
    daten = cursor.fetchall()
    conn.close()

    for eintrag in daten:
        tree.insert("", tk.END, values=eintrag)

# ---------------- GUI-Setup ---------------- #

erstelle_datenbank()

root = tk.Tk()
root.title("Messmittel-Ausleihe")

# Suche
tk.Label(root, text="🔍 Messmittelnr. eingeben:").pack()
eingabe_nummer = tk.Entry(root)
eingabe_nummer.pack()
tk.Button(root, text="Suchen", command=suche_teil).pack()

name_var = tk.StringVar()
beschreibung_var = tk.StringVar()
standort_var = tk.StringVar()
kalibrierdatum_var = tk.StringVar()
entnommen_var = tk.StringVar()
zurueck_var = tk.StringVar()

tk.Label(root, text="🧾 Name:").pack()
tk.Entry(root, textvariable=name_var).pack()

tk.Label(root, text="📄 Beschreibung:").pack()
tk.Entry(root, textvariable=beschreibung_var).pack()

tk.Label(root, text="📍 Aktueller Standort:").pack()
tk.Label(root, textvariable=standort_var).pack()

tk.Label(root, text="📅 Kalibrierdatum (JJJJ-MM-TT):").pack()
tk.Entry(root, textvariable=kalibrierdatum_var).pack()

tk.Label(root, text="📤 Entnommen am (JJJJ-MM-TT):").pack()
tk.Entry(root, textvariable=entnommen_var).pack()

tk.Label(root, text="📥 Zurückgebracht am (JJJJ-MM-TT):").pack()
tk.Entry(root, textvariable=zurueck_var).pack()

standorte = ["221K01", "221K02", "221K03", "270C01", "270C02", "270S01", "320C01", "470S01", "QS", "WZB", "Kalibrierung", "Messmittel fehlt"]
dropdown = tk.StringVar()
tk.Label(root, text="📍 Neuer Standort:").pack()
tk.OptionMenu(root, dropdown, *standorte).pack()

tk.Button(root, text="✅ Standort aktualisieren", command=aktualisiere_standort).pack()
tk.Button(root, text="📝 Stammdaten speichern", command=aktualisiere_stammdaten).pack()

# Neues Messmittel
tk.Label(root, text="——————————————").pack()
tk.Label(root, text="➕ Neues Messmittel hinzufügen").pack()

tk.Label(root, text="🔢 Messmittelnr.:").pack()
neuer_nummer_entry = tk.Entry(root)
neuer_nummer_entry.pack()

tk.Label(root, text="🧾 Name:").pack()
neuer_name_entry = tk.Entry(root)
neuer_name_entry.pack()

tk.Label(root, text="📄 Beschreibung:").pack()
neue_beschreibung_entry = tk.Entry(root)
neue_beschreibung_entry.pack()

tk.Label(root, text="📍 Standort:").pack()
neuer_standort_dropdown = tk.StringVar()
tk.OptionMenu(root, neuer_standort_dropdown, *standorte).pack()

tk.Label(root, text="📅 Kalibrierdatum (JJJJ-MM-TT):").pack()
neues_kalibrierdatum_entry = tk.Entry(root)
neues_kalibrierdatum_entry.pack()

tk.Button(root, text="➕ Messmittel hinzufügen", command=neues_teil_hinzufuegen).pack()

# Übersicht
tk.Label(root, text="——————————————").pack()
tk.Label(root, text="📋 Übersicht aller Messmittel").pack()

spalten = ("nummer", "name", "standort", "kalibrierdatum", "entnommen_am", "zurueckgebracht_am")
tree = ttk.Treeview(root, columns=spalten, show="headings")
for spalte in spalten:
    tree.heading(spalte, text=spalte.replace("_", " ").title())
    tree.column(spalte, width=130)
tree.pack()

tk.Button(root, text="🔄 Tabelle aktualisieren", command=lade_alle_messmittel).pack()

# Initiale Tabelle laden
lade_alle_messmittel()

root.mainloop()
