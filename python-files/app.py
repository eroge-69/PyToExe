import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import threading
import tkinter as tk
from tkinter import messagebox
import urllib.request
import json

# Configuration
THRESHOLD_TEMP = 5.0  # 5°C, température critique de froid
CHECK_INTERVAL = 10  # chaque 10 sec , 60 = 1 min
API_URL = 'http://localhost:8085/data.json'

EMAIL_SENDER = 'votre-email@example.com'
EMAIL_RECEIVER = 'receveur@example.com'
EMAIL_SUBJECT = 'Alerte de Température'
EMAIL_BODY = 'La température du laptop est descendue en dessous du seuil critique.'
SMTP_SERVER = 'smtp.example.com'
SMTP_PORT = 587
SMTP_USER = 'votre-email@example.com'
SMTP_PASSWORD = 'votre-mot-de-passe'

running = False  # État du monitoring

def send_alert_email():
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = EMAIL_SUBJECT
    msg.attach(MIMEText(EMAIL_BODY, 'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            print('Alerte envoyée par email.')
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")

def extract_temperature(data):
    temperatures = []

    def extract_from_children(children):
        for child in children:
            if 'Children' in child:
                extract_from_children(child['Children'])
            if 'Text' in child and 'Value' in child:
                if '°C' in child['Value']:
                    try:
                        temp = float(child['Value'].replace('°C', '').replace(',', '.'))
                        temperatures.append(temp)
                    except ValueError:
                        pass

    extract_from_children(data['Children'])
    return temperatures

def check_temperature():
    try:
        with urllib.request.urlopen(API_URL) as response:
            data = json.load(response)
        temperatures = extract_temperature(data)
        if temperatures:
            return min(temperatures)
        else:
            return None
    except Exception as e:
        print(f'Erreur lecture température : {e}')
        return None

def monitor_temperature(label):
    global running
    while running:
        temp = check_temperature()
        if temp is not None:
            label.config(text=f"Température actuelle : {temp}°C")
            if temp < THRESHOLD_TEMP:
                print("Alerte : température basse !")
                messagebox.showwarning("Alerte", f"Attention, température basse : {temp}°C")
                send_alert_email()
        else:
            label.config(text="Température non disponible.")
        time.sleep(CHECK_INTERVAL)

def start_monitoring(label):
    global running
    if not running:
        running = True
        threading.Thread(target=monitor_temperature, args=(label,), daemon=True).start()

def stop_monitoring():
    global running
    running = False

def main_interface():
    root = tk.Tk()
    root.title("Surveillance Température Laptop")

    label = tk.Label(root, text="Température non mesurée", font=("Arial", 14))
    label.pack(pady=10)

    start_btn = tk.Button(root, text="Démarrer Surveillance", command=lambda: start_monitoring(label))
    start_btn.pack(pady=5)

    stop_btn = tk.Button(root, text="Arrêter Surveillance", command=stop_monitoring)
    stop_btn.pack(pady=5)

    quit_btn = tk.Button(root, text="Quitter", command=lambda: (stop_monitoring(), root.quit()))
    quit_btn.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_interface()
