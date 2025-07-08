
import requests
import time

USER_ID = 99060139
WEBHOOK_URL = "https://discord.com/api/webhooks/1392148080349941893/voWT2DDQ9NpJp5OTnVxwCnrr2ND6ElJXmPUFWNzhhjgeArT1bKFm2Aug05WMpxfoXsiH"
CHECK_INTERVAL = 30

def is_online(uid):
    url = "https://presence.roblox.com/v1/presence/users"
    data = {"userIds": [uid]}
    resp = requests.post(url, json=data).json()
    status = resp["userPresences"][0]["userPresenceType"]
    game = resp["userPresences"][0].get("lastLocation", "")
    return status != 0, game

last_state = None

print("Running... Waiting for Juliaminegirl to come online.")

while True:
    try:
        online, game = is_online(USER_ID)
        if online and last_state == False:
            msg = {"content": f"🔔 **Juliaminegirl** is now online!\nPlaying: `{game}`"}
            requests.post(WEBHOOK_URL, json=msg)
            print("Notification sent to Discord.")
        last_state = online
    except Exception as e:
        print("Error:", e)
    time.sleep(CHECK_INTERVAL)
