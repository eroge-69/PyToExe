import os
from PIL import Image, ExifTags

# ⚜️ Einstellungen
QUALITAET = 13  # Sehr starke Kompression
SUBSAMPLING = 2  # 4:2:0 – wie "High (Smaller File Size)"
UNTERSTUETZTE_FORMATE = ('.jpg', '.jpeg', '.png')

def aktueller_ordner():
    return os.path.dirname(os.path.abspath(__file__))

def komprimiere_bild(pfad, dateiname):
    vollpfad = os.path.join(pfad, dateiname)

    try:
        with Image.open(vollpfad) as img:
            # Konvertiere PNGs zu JPEGs für bessere Kompression
            if img.format == 'PNG':
                print(f'🌀 Konvertiere PNG → JPEG: {dateiname}')
                dateiname = os.path.splitext(dateiname)[0] + '.jpg'
                vollpfad = os.path.join(pfad, dateiname)

            # Entferne alle Metadaten (EXIF)
            img = img.convert('RGB')

            img.save(
                vollpfad,
                format='JPEG',
                quality=QUALITAET,
                optimize=True,
                subsampling=SUBSAMPLING
            )
            print(f'⚜️ Komprimiert & gespeichert: {dateiname}')

    except Exception as e:
        print(f'⚠️ Fehler bei {dateiname}: {e}')

def bilder_komprimieren():
    ordner = aktueller_ordner()
    print(f'🏰 Arbeitsverzeichnis: {ordner}')

    for datei in os.listdir(ordner):
        if datei.lower().endswith(UNTERSTUETZTE_FORMATE):
            komprimiere_bild(ordner, datei)

if __name__ == '__main__':
    bilder_komprimieren()
