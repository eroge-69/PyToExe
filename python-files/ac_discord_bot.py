
import requests
import datetime
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1095784878483718246/LLnxqTonVDwmUulJanOPeDm5Y50TlLjTG9GWOji0N4kC0mrJaTWFhAUTPVdbX7OYk_As"
SERVER_API_URL = "http://26.188.78.161:8081/api/live"
UPDATE_INTERVAL_SECONDS = 60

def get_online_players():
    try:
        response = requests.get(SERVER_API_URL, timeout=5)
        data = response.json()
        return data.get("clients", [])
    except:
        return None

def send_to_discord(clients):
    embed = {
        "title": "🌐 Онлайн на сервере Assetto Corsa",
        "color": 3447003,
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "fields": []
    }

    if clients:
        for i, client in enumerate(clients, start=1):
            name = client.get("name", "Unknown")
            car = client.get("car", "Unknown Car")
            embed["fields"].append({
                "name": f"{i}. {name}",
                "value": f"🚗 Машина: `{car}`",
                "inline": False
            })
    else:
        embed["fields"].append({
            "name": "❌ Никто не подключён",
            "value": "Сервер пуст.",
            "inline": False
        })

    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]})
    except:
        pass

if __name__ == "__main__":
    print("🚦 Assetto Corsa Discord Bot запущен!")
    while True:
        clients = get_online_players()
        if clients is not None:
            send_to_discord(clients)
        time.sleep(UPDATE_INTERVAL_SECONDS)
