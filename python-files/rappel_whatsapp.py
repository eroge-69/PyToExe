import ezodf
from datetime import datetime, timedelta
from dateutil.parser import parse
import pywhatkit
import time

# Charger le fichier ODS
doc = ezodf.opendoc("rappels.ods")
sheet = doc.sheets[0]

# Date cible = aujourd'hui + 7 jours
date_cible = datetime.now().date() + timedelta(days=7)

# Lecture des lignes
for i, row in enumerate(sheet.rows()):
    if i == 0:
        continue  # ignorer l'en-tête

    date_cell = row[0].value
    nom = row[1].value
    immatriculation = row[2].value
    telephone = row[3].value

    if not all([date_cell, nom, immatriculation, telephone]):
        continue  # ignorer les lignes incomplètes

    try:
        date_rappel = parse(str(date_cell)).date()
    except:
        continue

    if date_rappel == date_cible:
        # Format numéro WhatsApp (avec indicatif)
        numero = str(telephone)
        if numero.startswith("0"):
            numero = "+212" + numero[1:]
        elif not numero.startswith("+"):
            numero = "+212" + numero

        # Message
        message = f"Bonjour {nom}, ceci est un rappel pour votre véhicule immatriculé {immatriculation}. Merci."

        # Heure d'envoi (1 minute après l’heure actuelle)
        heure = datetime.now() + timedelta(minutes=1)
        h = heure.hour
        m = heure.minute

        print(f"Envoi à {numero} à {h}:{m:02d} → {message}")
        pywhatkit.sendwhatmsg(numero, message, h, m, wait_time=10)
        time.sleep(5)
