import csv
import os

EINGABE_DATEI = "nf-subs-1.csv"
AUSGABE_DATEI = "neue-kunden.csv"

def lade_csv():
    with open(EINGABE_DATEI, newline='', encoding='utf-8') as f:
        return list(csv.reader(f, delimiter=','))

def speichere_csv(daten):
    with open(AUSGABE_DATEI, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Vorname", "Nachname", "Straße", "Ort", "PLZ", "Telefon", "E-Mail"])
        writer.writerows(daten)

def verarbeite_daten():
    daten = lade_csv()
    header, zeilen = daten[0], daten[1:]
    seen = set()
    result = []

    for z in zeilen:
        if len(z) < 10:
            continue
        vorname = z[3].strip()
        nachname = z[4].strip()
        key = (vorname.lower(), nachname.lower())
        if key in seen:
            continue
        seen.add(key)

        strasse = z[5].strip()
        ort = z[7].strip()
        plz = z[6].strip()
        telefon = z[8].strip()
        email = z[9].strip()

        result.append([vorname, nachname, strasse, o]()
