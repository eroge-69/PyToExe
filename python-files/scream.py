import time
import random
import os
import subprocess

# Pfad zur Datei auf dem Desktop
filename = os.path.expanduser("~\\Desktop\\warning.txt")

# Gruselige Nachrichtenliste
messages = [
    "Ich sehe dich.",
    "Warum hast du mich nicht gelöscht?",
    "Ich finde dich.",
    "Du kannst nicht entkommen.",
    "Ich weiß, wo du wohnst.",
    "Was war das hinter dir?",
    "Schau hinter dich. Jetzt.",
    "Wir sind nicht allein.",
    "Es ist zu spät.",
    "Du hast einen Fehler gemacht.",
    "Denkst du, das ist nur ein Zufall?",
    "Ich bin näher als du denkst.",
    "Dein Ende beginnt jetzt.",
    "Wir beobachten dich.",
    "Du bist nicht allein in diesem Raum.",
    "Du hättest die Datei nicht öffnen sollen.",
    "Ich bin im System.",
    "Ich kontrolliere die Maus...",
    "Tick... Tack...",
    "Warum rennst du nicht?"
]

# Warte 5 Minuten vor der ersten Nachricht
print("Starte in 5 Minuten...")
time.sleep(300)

while True:
    # Zufällige Nachricht auswählen
    message = random.choice(messages)

    # Nachricht an Datei anhängen
    with open(filename, "a", encoding="utf-8") as f:
        f.write(message + "\n")

    # Datei mit Notepad öffnen
    subprocess.Popen(["notepad.exe", filename])

    # Zufällige Pause vor der nächsten Nachricht (10–60 Sekunden)
    wait_time = random.randint(10, 60)
    time.sleep(wait_time)
