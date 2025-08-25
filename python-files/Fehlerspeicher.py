import os
import re
from datetime import datetime, timedelta
from collections import defaultdict

# Hauptordner mit Fahrzeug-Unterordnern
hauptordner = os.path.dirname(os.path.abspath(__file__))


# Ergebnisse pro Datei
datei_ergebnisse = []

# Zusammenfassungen
klemmwechsel_pro_fahrzeug = defaultdict(int)
datei_counter_pro_fahrzeug = defaultdict(int)
zeit_pro_fahrzeug = defaultdict(timedelta)

# Funktion zur Datumsextraktion aus Dateinamen
def extract_datetime_from_filename(filename):
    match = re.search(r'_(\d{14})', filename)
    if match:
        dt_str = match.group(1)[:12]  # Nur bis Minute verwenden
        dt = datetime.strptime(dt_str, "%Y%m%d%H%M")
        return dt.strftime("%d.%m.%Y %H.%MUhr")
    return "Unbekannt"

# Funktion zur Extraktion aller Zeitstempel aus dem Text
def extract_timestamps(text):
    pattern = r'\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun), \d{2}\.\d{2}\.\d{4} \d{2}:\d{2}:\d{2}\.\d{2}'
    matches = re.findall(pattern, text)
    timestamps = []
    for match in matches:
        try:
            timestamps.append(datetime.strptime(match, "%a, %d.%m.%Y %H:%M:%S.%f"))
        except ValueError:
            continue
    return timestamps

# Alle Dateien rekursiv durchlaufen
for root, dirs, files in os.walk(hauptordner):
    for file in files:
        if file.endswith(".txt"):
            fahrzeugnummer = os.path.basename(root)
            dateipfad = os.path.join(root, file)
            datum_zeit = extract_datetime_from_filename(file)

            with open(dateipfad, 'r', encoding='utf-8') as f:
                inhalt = f.read()

            ignition_on = len(re.findall(r'Ignition ON', inhalt))
            ignition_off = len(re.findall(r'Ignition OFF', inhalt))
            klemmwechsel = min(ignition_on, ignition_off)

            timestamps = extract_timestamps(inhalt)
            gesamtzeit = timedelta()
            for i in range(1, len(timestamps)):
                diff = timestamps[i] - timestamps[i - 1]
                if timedelta(seconds=0) < diff <= timedelta(minutes=5):
                    gesamtzeit += diff

            datei_ergebnisse.append((fahrzeugnummer, datum_zeit, ignition_on, ignition_off, klemmwechsel, gesamtzeit))
            klemmwechsel_pro_fahrzeug[fahrzeugnummer] += klemmwechsel
            datei_counter_pro_fahrzeug[fahrzeugnummer] += 1
            zeit_pro_fahrzeug[fahrzeugnummer] += gesamtzeit

# Gesamtsummen berechnen
gesamt_klemmwechsel = sum(klemmwechsel_pro_fahrzeug.values())
gesamt_dateien = sum(datei_counter_pro_fahrzeug.values())
gesamt_zeit = sum(zeit_pro_fahrzeug.values(), timedelta())

# Ausgabe in Konsole
print(f"{'Fahrzeugnummer':<15} {'Datum/Uhrzeit':<22} {'Ignition ON':<12} {'Ignition OFF':<13} {'Klemmwechsel':<13} {'Gesamtzeit':<15}")
print("-" * 95)
for eintrag in datei_ergebnisse:
    print(f"{eintrag[0]:<15} {eintrag[1]:<22} {eintrag[2]:<12} {eintrag[3]:<13} {eintrag[4]:<13} {str(eintrag[5]):<15}")
print("-" * 95)

print("Gesamtübersicht pro Fahrzeug:")
print(f"{'Fahrzeugnummer':<15} {'Auslesungen':<15} {'Klemmwechsel':<15} {'Gesamtzeit':<15}")
for fahrzeug in klemmwechsel_pro_fahrzeug:
    print(f"{fahrzeug:<15} {datei_counter_pro_fahrzeug[fahrzeug]:<15} {klemmwechsel_pro_fahrzeug[fahrzeug]:<15} {str(zeit_pro_fahrzeug[fahrzeug]):<15}")
print("-" * 95)
print(f"{'Gesamtsumme':<15} {gesamt_dateien:<15} {gesamt_klemmwechsel:<15} {str(gesamt_zeit):<15}")

# Ausgabe in Textdatei
with open("auswertung_ergebnisse.txt", "w", encoding="utf-8") as file:
    file.write(f"{'Fahrzeugnummer':<15} {'Datum/Uhrzeit Auslesung':<30} {'Ignition ON':<12} {'Ignition OFF':<13} {'Klemmwechsel':<13} {'Gesamtzeit':<15}\n")
    file.write("-" * 95 + "\n")
    for eintrag in datei_ergebnisse:
        file.write(f"{eintrag[0]:<15} {eintrag[1]:<30} {eintrag[2]:<12} {eintrag[3]:<13} {eintrag[4]:<13} {str(eintrag[5]):<15}\n")
    file.write("-" * 95 + "\n\n")

    file.write("Gesamtübersicht pro Fahrzeug:\n")
    file.write(f"{'Fahrzeugnummer':<15} {'Auslesungen':<15} {'Klemmwechsel':<15} {'Gesamtzeit':<15}\n")
    for fahrzeug in klemmwechsel_pro_fahrzeug:
        file.write(f"{fahrzeug:<15} {datei_counter_pro_fahrzeug[fahrzeug]:<15} {klemmwechsel_pro_fahrzeug[fahrzeug]:<15} {str(zeit_pro_fahrzeug[fahrzeug]):<15}\n")
    file.write("-" * 95 + "\n")
    file.write(f"{'Gesamtsumme':<15} {gesamt_dateien:<10} {gesamt_klemmwechsel:<15} {str(gesamt_zeit):<15}\n")
