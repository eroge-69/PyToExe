
import os
import shutil
from pathlib import Path
from datetime import datetime

# =============================
# EINSTELLUNGEN
# =============================
quellordner = [
    r"\\NAS-SUR\Fotos",
    r"\\NAS-SUR\Videos",
    r"\\NAS-SUR\extern3Tb",
    r"\\NAS-SUR\extern6Tb"
]

zielordner = Path(r"\\NAS-SUR\extern6Tb\gesammeltPython")
zielordner.mkdir(parents=True, exist_ok=True)

dateiendung = ".mts"
neue_endung = ".mp4"

# =============================
# FUNKTIONEN
# =============================

def finde_videos(quellordner, dateiendung):
    dateien = []
    for ordner in quellordner:
        for root, _, files in os.walk(ordner):
            for name in files:
                if name.lower().endswith(dateiendung.lower()):
                    dateien.append(Path(root) / name)
    return dateien

def erstellungsdatum(pfad):
    t = os.path.getmtime(pfad)
    return datetime.fromtimestamp(t)

# =============================
# MAIN
# =============================

print("Starte Verarbeitung...")
alle_videos = finde_videos(quellordner, dateiendung)

laufnummer = 1
übersprungen = 0
kopiert = 0

for video in sorted(alle_videos, key=os.path.getmtime):
    try:
        datum = erstellungsdatum(video)
        basisname = datum.strftime("%Y-%m-%d_%H-%M-%S")
        nummer = f"{laufnummer:04}"
        neuer_name = f"{basisname}_{nummer}{neue_endung}"
        zielpfad = zielordner / neuer_name

        # Wenn Datei schon existiert: überspringen
        if zielpfad.exists():
            print(f"Überspringe (bereits vorhanden): {zielpfad.name}")
            übersprungen += 1
            continue

        shutil.copy2(video, zielpfad)
        print(f"Kopiert: {zielpfad.name}")
        laufnummer += 1
        kopiert += 1

    except Exception as e:
        print(f"Fehler bei {video}: {e}")

print("\n✅ Fertig!")
print(f"Gesamt gefunden: {len(alle_videos)}")
print(f"--> Kopiert: {kopiert}")
print(f"--> Übersprungen (bereits vorhanden): {übersprungen}")
