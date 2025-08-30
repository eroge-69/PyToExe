import time
import os
import random
import subprocess
import sys

# Funktion für zufällige Wartezeit
def wait_random(min_sec, max_sec):
    time.sleep(random.uniform(min_sec, max_sec))

# Hauptanzeige
def main_loader():
    print("=== ADVANTAGE LOADER BY KRIS ===\n")
    wait_random(1, 3)
    print("Systemkomponente wird gesucht...")
    wait_random(1, 3)
    print("Verbindungs-ID wird ermittelt...")
    wait_random(1, 3)
    print("Sicherheitsmodul wird geprüft...")
    wait_random(1, 3)
    print("done! ✅")
    wait_random(1, 2)

    # Neues CMD-Fenster öffnen
    subprocess.Popen([sys.executable, __file__, "keymode"], creationflags=subprocess.CREATE_NEW_CONSOLE)

# Eingabemodus für Key (wird in neuem Fenster aufgerufen)
def key_check():
    print("Key:", end=" ")
    user_key = input().strip()

    correct_key = "ARK-7F9X-LQ2P"

    if user_key == correct_key:
        print("Key ist noch nicht aktiviert. Bitte kontaktiere Kris zur Freischaltung.")
    else:
        print("Falscher Key.")

    wait_random(5, 10)
    print("closing...")
    time.sleep(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "keymode":
        key_check()
    else:
        main_loader()
