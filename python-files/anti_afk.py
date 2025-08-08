import time
import pyautogui

def simulate_activity():
    # Simula un piccolo movimento del mouse
    current_position = pyautogui.position()
    pyautogui.moveRel(3, 0)  # Muove il mouse di 1 pixel a destra
    print("Mouse spostato di 3 pixel.")

    # Esegue 3-4 clic consecutivi
    for i in range(4):  # Cambia il numero in base al numero di clic desiderato
        pyautogui.click()
        print(f"Click {i+1} eseguito!")
        time.sleep(0.5)  # Pausa di 0.5 secondi tra un clic e l'altro

    # Riporta il mouse alla posizione originale
    pyautogui.moveTo(current_position)
    print("Mouse riportato alla posizione originale.")

def main():
    print("Programma avviato. Premere Ctrl+C per uscire.")
    while True:
        time.sleep(250)  # Aspetta 5 minuti (300 secondi)
        simulate_activity()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgramma terminato.")
