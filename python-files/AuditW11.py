# audit_win11.py
import os
import platform
import subprocess
import webbrowser
import json
import psutil
from datetime import datetime

# Fonctions pour l'audit système
def get_computer_name():
    return platform.node()

def get_processor():
    return platform.processor()

def get_ram():
    ram = round(psutil.virtual_memory().total / (1024 ** 3))
    return f"{ram} Go"

def get_storage():
    storage = psutil.disk_usage('/')
    return f"{round(storage.total / (1024 ** 3))} Go"

def check_tpm():
    try:
        result = subprocess.run(["powershell", "Get-WmiObject -Namespace \"Root\\CIMv2\\Security\\MicrosoftTpm\" -Class Win32_Tpm"], capture_output=True, text=True)
        return "Présent" if "IsActivated_InitialValue" in result.stdout else "Absent"
    except:
        return "Inconnu"

def check_secure_boot():
    try:
        result = subprocess.run(["powershell", "Confirm-SecureBootUEFI"], capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return "Inconnu"

# Données collectées
info = {
    "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "computerName": get_computer_name(),
    "processor": get_processor(),
    "ram": get_ram(),
    "storage": get_storage(),
    "tpm": check_tpm(),
    "secureBoot": check_secure_boot(),
}

# Génération du HTML
html_template = f"""
<!DOCTYPE html>
<html lang=\"fr\">
<head>
    <meta charset=\"UTF-8\">
    <title>Audit Windows 11</title>
    <style>
        body {{ font-family: Arial; padding: 20px; }}
        .field {{ margin-bottom: 10px; }}
        .label {{ font-weight: bold; }}
        input {{ padding: 5px; width: 300px; }}
    </style>
</head>
<body>
    <h2>Rapport d'audit Windows 11</h2>
    <p><b>Date :</b> {info['date']}</p>
    <p><b>Nom de l'ordinateur :</b> {info['computerName']}</p>
    <p><b>Processeur :</b> {info['processor']}</p>
    <p><b>Mémoire RAM :</b> {info['ram']}</p>
    <p><b>Stockage :</b> {info['storage']}</p>
    <p><b>TPM :</b> {info['tpm']}</p>
    <p><b>Secure Boot :</b> {info['secureBoot']}</p>

    <h3>Envoyer une demande de soumission</h3>
    <div class=\"field\">
        <span class=\"label\">Nom :</span><br>
        <input type=\"text\" id=\"clientName\" required>
    </div>
    <div class=\"field\">
        <span class=\"label\">Téléphone :</span><br>
        <input type=\"text\" id=\"clientPhone\" placeholder=\"123-456-7890\" required>
    </div>
    <div class=\"field\">
        <span class=\"label\">Adresse courriel :</span><br>
        <input type=\"email\" id=\"clientEmail\" required>
    </div>
    <button onclick=\"sendAudit()\">Demande de soumission</button>

    <p id=\"response\"></p>

    <script>
    function sendAudit() {{
        const data = {{
            clientName: document.getElementById('clientName').value,
            clientPhone: document.getElementById('clientPhone').value,
            clientEmail: document.getElementById('clientEmail').value,
            computerName: '{info['computerName']}',
            processor: '{info['processor']}',
            ram: '{info['ram']}',
            storage: '{info['storage']}',
            tpm: '{info['tpm']}',
            secureBoot: '{info['secureBoot']}',
            date: '{info['date']}'
        }};

        fetch('https://www.samouraitek.ca/AuditW11/AuditW11.php', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/json' }},
            body: JSON.stringify(data)
        }})
        .then(response => response.json())
        .then(result => {{
            document.getElementById('response').innerText = result.message;
        }})
        .catch(error => {{
            document.getElementById('response').innerText = 'Erreur lors de l\'envoi';
        }});
    }}
    </script>
</body>
</html>
"""

# Sauvegarder le fichier HTML
filename = os.path.join(os.environ['TEMP'], "audit_windows11.html")
with open(filename, "w", encoding="utf-8") as file:
    file.write(html_template)

# Ouvrir dans Edge
webbrowser.get("windows-default").open(filename)