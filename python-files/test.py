import keyboard
import time

def envoyer_message():
    print("Commande envoyée : /pay iDrxkzz 1M")

print("Appuie sur 'Y' pour envoyer la commande. Appuie sur 'ESC' pour quitter.")

keyboard.add_hotkey('y', envoyer_message)

# Boucle infinie pour garder le programme actif
keyboard.wait('esc')
