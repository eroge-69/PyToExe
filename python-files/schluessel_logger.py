
import csv
import os
from datetime import datetime

LOG_FILE = 'schluessel_log.csv'
offene_schluessel = {}

# Bestehende Einträge laden
if os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'r') as f:
        reader = csv.reader(f, delimiter=';')
        for row in reader:
            key, action, timestamp = row
            if action == "Ausgabe":
                offene_schluessel[key] = timestamp
            elif action == "Rückgabe" and key in offene_schluessel:
                del offene_schluessel[key]

def log_schluessel(scan):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    action = ""
    if scan in offene_schluessel:
        action = "Rückgabe"
        del offene_schluessel[scan]
    else:
        action = "Ausgabe"
        offene_schluessel[scan] = now

    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow([scan, action, now])
    print(f"[Erfasst] {scan} - {action} - {now}")

print("Scanner bereit. Bitte Schlüssel scannen (Strg+C zum Beenden):")

while True:
    try:
        scan_input = input().strip()
        if scan_input:
            log_schluessel(scan_input)
    except KeyboardInterrupt:
        print("\nBeendet.")
        break
