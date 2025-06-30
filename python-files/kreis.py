import pyautogui
import time

# Fail-Safe deaktivieren
pyautogui.FAILSAFE = False

def zickzack_bewegung(schritte=50, geschwindigkeit=0.001):
    breite, hoehe = pyautogui.size()
    dx = breite // schritte
    dy = hoehe // schritte
    richtung = 1

    for i in range(schritte):
        x = i * dx
        y = i * dy if richtung == 1 else hoehe - (i * dy)
        pyautogui.moveTo(x, y, duration=geschwindigkeit)
        richtung *= -1

try:
    while True:
        zickzack_bewegung()
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Beendet durch Benutzer.")
