import pyautogui
import time

# délai pour te laisser basculer dans l'application
time.sleep(3)

# chercher l'icône (image à utiliser : "icone.png")
location = pyautogui.locateOnScreen("icone.png", confidence=0.8)

if location:
    # récupérer le centre du bouton
    center = pyautogui.center(location)
    # cliquer dessus
    pyautogui.click(center)
    print("Bouton cliqué avec succès ✅")
else:
    print("Bouton non trouvé ❌")
