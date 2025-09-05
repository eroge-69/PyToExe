import os
import shutil

ordner = r"C:\Klassenarbeiten"

def leere_ordner(pfad):
    if not os.path.exists(pfad):
        return  # wenn Ordner nicht existiert → nichts tun

    for element in os.listdir(pfad):
        element_pfad = os.path.join(pfad, element)
        try:
            if os.path.isfile(element_pfad) or os.path.islink(element_pfad):
                os.remove(element_pfad)  # Datei oder Verknüpfung löschen
            elif os.path.isdir(element_pfad):
                shutil.rmtree(element_pfad)  # Unterordner löschen
        except Exception:
            pass  # Fehler ignorieren (z. B. gesperrte Datei)

if __name__ == "__main__":
    leere_ordner(ordner)
