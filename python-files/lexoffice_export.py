import csv
import os
import logging

INPUT_FILE = "nf-subs-1.csv"
OUTPUT_FILE = "neue-kunden.csv"

# Spaltenpositionen nach Datenstruktur
IDX_VORNAME = 3
IDX_NACHNAME = 4
IDX_STRASSE = 5
IDX_PLZ = 6
IDX_ORT = 7
IDX_TELEFON = 8
IDX_EMAIL = 9

# Einfache Konfiguration für Logging
logging.basicConfig(level=logging.INFO, format="%(message)s")


def lade_daten(pfad):
    if not os.path.exists(pfad):
        logging.error(f"Datei nicht gefunden: {pfad}")
        return []

    with open(pfad, newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        return list(reader)


def verarbeite_daten(rohdaten):
    if not rohdaten or len(rohdaten) < 2:
        logging.warning("Keine Daten oder nur Header vorhanden.")
        return []

    header, datensaetze = rohdaten[0], rohdaten[1:]
    gesehen = set()
    ausgabe = []

    for zeile in datensaetze:
        if len(zeile) <= IDX_EMAIL:
            continue

        vorname = zeile[IDX_VORNAME].strip()
        nachname = zeile[IDX_NACHNAME].strip()
        name_key = (vorname.lower(), nachname.lower())
        if name_key in gesehen:
            continue
        gesehen.add(name_key)

        strasse = zeile[IDX_STRASSE].strip()
        plz = zeile[IDX_PLZ].strip()
        ort = zeile[IDX_ORT].strip()
        telefon = zeile[IDX_TELEFON].strip()
        email = zeile[IDX_EMAIL].strip()

        ausgabe.append([
            vorname,
            nachname,
            strasse,
            ort,
            plz,
            telefon,
            email
        ])

    logging.info(f"{len(ausgabe)} eindeutige Adressen verarbeitet.")
    return ausgabe


def speichere_daten(pfad, datensaetze):
    with open(pfad, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(["Vorname", "Nachname", "Straße", "Ort", "PLZ", "Telefon", "E-Mail"])
        writer.writerows(datensaetze)
    logging.info(f"Datei geschrieben: {pfad}")


def main():
    daten = lade_daten(INPUT_FILE)
    bereinigt = verarbeite_daten(daten)
    if bereinigt:
        speichere_daten(OUTPUT_FILE, bereinigt)


if __name__ == "__main__":
    main()
