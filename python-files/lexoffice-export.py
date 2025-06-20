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
        if len(z) < 11:
            continue
        vorname = z[4].strip()
        nachname = z[5].strip()
        key = (vorname.lower(), nachname.lower())
        if key in seen:
            continue
        seen.add(key)

        strasse = z[6].strip()  # enthält Straße und Hausnummer
        plz = z[7].strip()
        ort = z[8].strip()
        telefon = z[9].strip()
        email = z[10].strip()

        result.append([vorname, nachname, strasse, ort, plz, telefon, email])

    speichere_csv(result)
    print(f"{len(result)} Datensätze exportiert in '{AUSGABE_DATEI}'.")

if __name__ == "__main__":
    if not os.path.exists(EINGABE_DATEI):
        print(f"Datei '{EINGABE_DATEI}' nicht gefunden.")
    else:
        verarbeite_daten()
