import keyboard
import pyautogui
import time

def envoyer_message():
    pyautogui.press('t')
    time.sleep(0.1)
    pyautogui.typewrite("/pay iDrxkzz 1M")
    pyautogui.press('enter')

print("Le programme est lancé. Appuie sur Maj + M pour exécuter l'action.")
keyboard.add_hotkey('shift+m', envoyer_message)
keyboard.wait('esc')
