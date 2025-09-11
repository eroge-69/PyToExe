
import os
from dotenv import load_dotenv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

load_dotenv()

fecha_hoy = '2025-09-11'
disposiciones = [
    {'numero': '6675/2025', 'titulo': 'Prohibición de productos UP! MY HAIR', 'link': 'https://www.boletinoficial.gob.ar/#!DetalleNorma/331162/20250911'},
    {'numero': '6676/2025', 'titulo': 'Prohibición de productos VIELESS', 'link': 'https://www.boletinoficial.gob.ar/#!DetalleNorma/331163/20250911'},
    {'numero': '6677/2025', 'titulo': 'Prohibición de aceite de oliva Campos de Arauco', 'link': 'https://www.boletinoficial.gob.ar/#!DetalleNorma/331164/20250911'},
    {'numero': '6678/2025', 'titulo': 'Prohibición de aceite de oliva Arauco Artesanal', 'link': 'https://www.boletinoficial.gob.ar/#!DetalleNorma/331165/20250911'},
    {'numero': '6696/2025', 'titulo': 'Prohibición de ventiladores ResMed robados', 'link': 'https://www.boletinoficial.gob.ar/#!DetalleNorma/331166/20250911'}
]

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
DESTINATARIO = os.getenv('DESTINATARIO')

mensaje = MIMEMultipart()
mensaje['From'] = EMAIL_ADDRESS
mensaje['To'] = DESTINATARIO
mensaje['Subject'] = f"Disposiciones ANMAT - Boletín Oficial {fecha_hoy}"

cuerpo = "Disposiciones ANMAT publicadas hoy en el Boletín Oficial:

"
for dispo in disposiciones:
    cuerpo += f"Disposición Nº {dispo['numero']} - {dispo['titulo']}
Link: {dispo['link']}

"

mensaje.attach(MIMEText(cuerpo, 'plain'))

# with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#     server.starttls()
#     server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
#     server.send_message(mensaje)
# print("Correo enviado exitosamente.")
