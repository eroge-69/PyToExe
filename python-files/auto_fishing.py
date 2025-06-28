import time
import pytesseract
import pyautogui
import keyboard
from PIL import ImageGrab

# Configuration – à ajuster selon la position de la touche affichée à l'écran
# Format : (left, top, right, bottom)
capture_zone = (860, 500, 1060, 600)  # Modifier en fonction de ton écran

print("Auto-pêche lancé.")
print("Appuie sur F7 pour arrêter le programme.")

# Boucle principale
while True:
    if keyboard.is_pressed("F7"):
        print("Arrêt demandé par l'utilisateur. Fermeture.")
        break

    # Capture une portion de l'écran
    img = ImageGrab.grab(bbox=capture_zone)

    # Reconnaissance de texte OCR
    text = pytesseract.image_to_string(img).strip().upper()

    # Recherche de la première touche valide
    for char in text:
        if char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890":
            pyautogui.press(char.lower())  # Appuie sur la touche détectée
            print(f"Touche pressée : {char}")
            time.sleep(0.8)  # Temps pour éviter de spam
            break

    time.sleep(0.2)
