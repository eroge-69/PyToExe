import os

ordner_pfad = input("Pfad zum Ordner eingeben: ").strip()
ziel_laenge = 15  # Gewünschte Länge des Dateinamens ohne Endung

if not os.path.isdir(ordner_pfad):
    print("❌ Ungültiger Pfad. Bitte überprüfe die Eingabe.")
    exit()

# 🔁 Durchlaufe alle Dateien im Ordner
for dateiname in os.listdir(ordner_pfad):
    alter_pfad = os.path.join(ordner_pfad, dateiname)

    if not os.path.isfile(alter_pfad):
        continue

    name, ext = os.path.splitext(dateiname)

    # Entferne IMG_- oder IMG- am Anfang
    if name.startswith('IMG_') or name.startswith('IMG-'):
        name = name[4:]

    # Bringe den Namen auf exakt 15 Zeichen
    if len(name) > ziel_laenge:
        basisname = name[:ziel_laenge]
    else:
        basisname = name.zfill(ziel_laenge)

    neuer_name = basisname + ext
    neuer_pfad = os.path.join(ordner_pfad, neuer_name)

    zaehler = 2
    while os.path.exists(neuer_pfad):
        neuer_name = f"{basisname}.{zaehler}{ext}"
        neuer_pfad = os.path.join(ordner_pfad, neuer_name)
        zaehler += 1

    try:
        os.rename(alter_pfad, neuer_pfad)
        print(f"✏️  {dateiname} → {neuer_name}")
    except Exception as e:
        print(f"❌ Fehler beim Umbenennen von {dateiname}: {e}")

print("✅ Alle Dateinamen wurden korrekt umbenannt.")
