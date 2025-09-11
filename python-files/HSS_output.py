import os
import re
import csv
import pandas as pd
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

# --- Hilfsfunktionen ---

def normalize(name: str) -> str:
    if name is None:
        return ""
    name = name.replace("\ufeff", "")  # BOM entfernen
    name = name.strip().lower()
    for ch in [" ", "-", "_", ":", ";", ",", "/", "\\", "\t"]:
        name = name.replace(ch, "")
    name = name.replace("serivce", "service")
    return name


def find_index(headers_norm, primary_names, fallback_after=None, offset=1):
    for i, h in enumerate(headers_norm):
        if h in primary_names:
            return i
    if fallback_after is not None:
        if isinstance(fallback_after, (list, tuple)):
            for near in fallback_after:
                if near in headers_norm:
                    idx = headers_norm.index(near) + offset
                    if 0 <= idx < len(headers_norm):
                        return idx
        else:
            if fallback_after in headers_norm:
                idx = headers_norm.index(fallback_after) + offset
                if 0 <= idx < len(headers_norm):
                    return idx
    return None

DATE_PATTERNS = [
    (re.compile(r"(20\d{2})[-_.]?(\d{2})[-_.]?(\d{2})"), "%Y%m%d"),
    (re.compile(r"(\d{2})[-_.]?(\d{2})[-_.]?(20\d{2})"), "%d%m%Y"),
]


def extract_date_from_filename(filename: str) -> str:
    base = os.path.basename(filename)
    for rx, fmt in DATE_PATTERNS:
        m = rx.search(base)
        if m:
            digits = "".join(m.groups())
            try:
                dt = datetime.strptime(digits, fmt)
                return dt.strftime("%d.%m.%Y")  # Ausgabeformat TT.MM.JJJJ
            except Exception:
                pass
    return "Unbekannt"


# --- Hauptlogik ---

root = tk.Tk()
root.withdraw()
INPUT_FOLDER = filedialog.askdirectory(title="Bitte Ordner mit TXT-Dateien auswählen")

if not INPUT_FOLDER:
    print(" Kein Ordner ausgewählt. Skript beendet.")
    raise SystemExit

OUTPUT_FILE = os.path.join(INPUT_FOLDER, "output.xlsx")

# Falls schon ein output.xlsx existiert → umbenennen nach **Erstelldatum**
if os.path.exists(OUTPUT_FILE):
    ctime = os.path.getctime(OUTPUT_FILE)
    dt = datetime.fromtimestamp(ctime).strftime("%d.%m.%Y")
    backup_name = os.path.join(INPUT_FOLDER, f"output_{dt}.xlsx")

    counter = 1
    while os.path.exists(backup_name):
        backup_name = os.path.join(INPUT_FOLDER, f"output_{dt}_{counter}.xlsx")
        counter += 1

    os.rename(OUTPUT_FILE, backup_name)
    print(f" Alte Datei wurde umbenannt in: {backup_name}")

records = []

for filename in sorted(os.listdir(INPUT_FOLDER)):
    if not filename.lower().endswith(".txt"):
        continue

    filepath = os.path.join(INPUT_FOLDER, filename)
    file_date = extract_date_from_filename(filename)

    try:
        with open(filepath, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)
    except UnicodeDecodeError:
        with open(filepath, "r", encoding="latin-1", newline="") as f:
            reader = csv.reader(f, delimiter="\t")
            rows = list(reader)

    if not rows:
        continue

    header_raw = rows[0]
    if header_raw and header_raw[0] == "":
        header_raw = header_raw[1:]
        rows = [r[1:] if r else r for r in rows]

    headers_norm = [normalize(h) for h in header_raw]

    ref1_aliases = {"referenz1", "ref1", "kundenreferenz1", "referenz01", "referenz_1", "referenz 1"}
    ref2_aliases = {"referenz2", "ref2", "kundenreferenz2", "referenz02", "referenz_2", "referenz 2"}

    neighbor_service = ["service"]
    neighbor_beschreibung = ["beschreibung"]

    idx_ref1 = find_index(headers_norm, ref1_aliases, fallback_after=neighbor_service, offset=1)
    if idx_ref1 is None:
        idx_ref1 = find_index(headers_norm, ref1_aliases, fallback_after=neighbor_beschreibung, offset=2)

    idx_ref2 = find_index(headers_norm, ref2_aliases, fallback_after=neighbor_service, offset=2)
    if idx_ref2 is None:
        idx_ref2 = find_index(headers_norm, ref2_aliases, fallback_after=neighbor_beschreibung, offset=3)

    if idx_ref1 is None or idx_ref2 is None:
        print(f" '{filename}': Konnte Referenz-Spalten nicht sicher erkennen. Überspringe Datei.")
        continue

    for r in rows[1:]:
        if len(r) <= max(idx_ref1, idx_ref2):
            r = r + [""] * (max(idx_ref1, idx_ref2) - len(r) + 1)

        referenz1_val = r[idx_ref1]
        referenz2_val = r[idx_ref2]

        records.append({
            "Datum": file_date,
            "Referenz1": referenz1_val,
            "Referenz2": referenz2_val,
            "Datei": filename,
        })

if records:
    out_df = pd.DataFrame(records)
    out_df.sort_values(by=["Datum", "Datei"], inplace=True)
    out_df.to_excel(OUTPUT_FILE, index=False)
    print(f" Fertig! Neue Datei gespeichert als '{OUTPUT_FILE}'")
else:
    print(" Keine verwertbaren Referenz-Daten gefunden.")
