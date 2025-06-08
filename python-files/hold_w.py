import pyautogui
import time
import threading
import sys
import ctypes

# Functie om de 'W' toets ingedrukt te houden
def hold_w():
    while True:
        pyautogui.keyDown('w')
        time.sleep(0.1)
        pyautogui.keyUp('w')
        time.sleep(0.1)

# Functie om het script te stoppen
def stop_script():
    print("Programma gestopt.")
    sys.exit()

# Maak een thread voor de hold_w functie
thread = threading.Thread(target=hold_w)
thread.daemon = True
thread.start()

# Zorg ervoor dat het script blijft draaien
ctypes.windll.user32.MessageBoxW(0, "Druk op OK om het script te stoppen.", "Informatie", 1)
stop_script()
