import os
import shutil
import time
import sys
from pathlib import Path

# Funktion, um alle Laufwerke zu ermitteln (nur lokale Festplatten, keine Netzlaufwerke)D:\Py\usb.py pyinstaller --onefile usb.py
def get_drives():
    drives = []
    for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        drive = f"{letter}:/"
        if os.path.exists(drive):
            drives.append(drive)
    return drives

# Optimierte Such- und Kopierfunktion: Nur Windows durchsucht "Dokumente"
def search_and_copy_files(usb_path, search_terms=["Test", "Klassenarbeit", "Hausaufgabe"]):
    if os.name != "nt":
        print("Dieses Programm unterstützt die Dateisuche nur unter Windows.")
        return

    # Nur den Dokumente-Ordner durchsuchen
    documents = os.path.join(os.path.expanduser("~"), "Documents")
    if not os.path.exists(documents):
        print("Der Dokumente-Ordner wurde nicht gefunden.")
        return

    print(f"Suche nach Dateien im Ordner: {documents}")
    print(f"USB-Stick gefunden: {usb_path}")
    time.sleep(2)
    print("Starte die Suche nach Dateien...")

    # Zielordner auf dem USB-Stick
    zielordner = os.path.join(usb_path, "Gefundene_Dateien")
    os.makedirs(zielordner, exist_ok=True)

    for root, dirs, files in os.walk(documents):
        try:
            for file in files:
                if any(term.lower() in file.lower() for term in search_terms):
                    file_path = os.path.join(root, file)
                    try:
                        shutil.copy(file_path, zielordner)
                        print(f"Datei {file} kopiert nach {zielordner}")
                    except Exception as e:
                        print(f"Fehler beim Kopieren von {file_path}: {e}")
        except Exception as e:
            print(f"Zugriff auf {root} nicht möglich: {e}")

# Funktion, um den USB-Stick zu finden (immer D:)
def find_usb_drive():
    usb_drive = "D:/"
    if os.path.exists(usb_drive):
        print(f"USB-Stick gefunden: {usb_drive}")
        return usb_drive
    else:
        print(f"USB-Stick (D:/) nicht gefunden.")
        return None

def main():
    print("Suche nach Dateien und kopiere sie auf den USB-Stick.")

    # USB-Stick finden
    usb_drive = find_usb_drive()
    if usb_drive is None:
        return

    # Suchen und Kopieren der Dateien
    search_and_copy_files(usb_drive)

if __name__ == "__main__":
    main()