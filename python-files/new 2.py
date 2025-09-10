import os
import sys
import shutil
import subprocess

def zielpfad():
    appdata = os.getenv('APPDATA')
    zielordner = os.path.join(appdata, 'MeinProgramm')
    os.makedirs(zielordner, exist_ok=True)
    return os.path.join(zielordner, 'mein_programm.exe')

def main():
    eigene_datei = sys.executable
    ziel = zielpfad()

    if os.path.abspath(eigene_datei).lower() != os.path.abspath(ziel).lower():
        print("[INFO] Erste Ausführung – kopiere mich nach:")
        print("       " + ziel)
        shutil.copy2(eigene_datei, ziel)
        print("[INFO] Starte neue Instanz...")
        subprocess.Popen([ziel])
        sys.exit()

    else:
        print("[INFO] Ich wurde bereits kopiert.")
        print("[INFO] Starte normales Programm...")
        input("Drücke Enter zum Beenden.")

if __name__ == "__main__":
    main()
