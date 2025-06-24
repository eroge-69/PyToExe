
import pyautogui
import time

INTERVALLO = 30  # secondi

print("Mouse mover in esecuzione. Premi CTRL+C per uscire.")

try:
    while True:
        pyautogui.moveRel(5, 0, duration=0.1)
        pyautogui.moveRel(-5, 0, duration=0.1)
        time.sleep(INTERVALLO)
except KeyboardInterrupt:
    print("Terminato.")
