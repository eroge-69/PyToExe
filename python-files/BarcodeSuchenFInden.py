import os
import re
import glob
import pandas as pd
from pathlib import Path

def clean_filename(s):
    return re.sub(r'[^\w\\-_. ]', '_', str(s).strip())

# === Schritt 1: Excel-Pfad eingeben ===
excel_path = input("🔍 Bitte Pfad zur Excel-Datei (.xlsx) eingeben:\n> ").strip()

if not os.path.isfile(excel_path):
    print(f"❌ Datei nicht gefunden: {excel_path}")
    input("\nDrücke Enter zum Beenden...")
    exit(1)

# Excel laden
df = pd.read_excel(excel_path, engine="openpyxl")
base_path = Path(excel_path).parent

# === Schritt 2: Spalten anzeigen ===
print("\n📄 Gefundene Spalten:")
for i, col in enumerate(df.columns):
    print(f"  [{i}] {col}")

# === Schritt 3: Barcode-Spalte wählen ===
barcode_index = input("\n🧬 Gib die Nummer der Barcode-Spalte ein: ").strip()
try:
    barcode_col = df.columns[int(barcode_index)]
except:
    print("❌ Ungültige Eingabe.")
    exit(1)

# === Schritt 4: Spalten für neuen Namen wählen ===
print("\n✏️ Du kannst mehrere Spalten für den neuen Dateinamen angeben (z.B. 1,3,5)")
name_indices = input("Gib die Nummern der Spalten ein, die zusätzlich zum Barcode im neuen Dateinamen stehen sollen: ").split(",")
try:
    name_cols = [df.columns[int(i.strip())] for i in name_indices]
except:
    print("❌ Ungültige Eingabe.")
    exit(1)

# === Dateitypen, die gesucht werden ===
extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tif']

# === Hauptlogik ===
for idx, row in df.iterrows():
    barcode = str(row.get(barcode_col)).strip()
    if not barcode or barcode.lower() == 'nan':
        print(f"⚠️ Zeile {idx + 2}: Kein Barcode – übersprungen.")
        continue

    # Datei mit Barcode am Anfang suchen (z. B. "123456*.pdf")
    matched_file = None
    for ext in extensions:
        pattern = str(base_path / f"{barcode}*{ext}")
        matches = glob.glob(pattern)
        if matches:
            matched_file = Path(matches[0])  # Nimmt die erste gefundene Datei
            break

    if not matched_file:
        print(f"❌ Datei für Barcode {barcode} nicht gefunden.")
        continue

    # Teile für neuen Dateinamen sammeln
    parts = [clean_filename(row.get(col)) for col in name_cols if pd.notna(row.get(col))]
    if not parts:
        print(f"⚠️ Zeile {idx + 2}: Keine gültigen Namensbestandteile für Barcode {barcode}.")
        continue

    new_name = f"{barcode}_" + "_".join(parts) + matched_file.suffix
    new_file_path = base_path / new_name

    try:
        matched_file.rename(new_file_path)
        print(f"✅ Umbenannt: {matched_file.name} → {new_file_path.name}")
    except Exception as e:
        print(f"❌ Fehler bei {matched_file.name}: {e}")

print("\n✅ Vorgang abgeschlossen. Drücke Enter zum Beenden...")
input()
