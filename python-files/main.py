import requests
import os
from datetime import datetime, timezone

# Green text
GREEN = "\033[92m"
RESET = "\033[0m"

BANNER = f"""{GREEN}
 ███    ██ ███████ ██    ██ ██    ██ ████████ 
 ████   ██ ██       ██  ██  ██    ██    ██    
 ██ ██  ██ █████     ████   ██    ██    ██    
 ██  ██ ██ ██         ██    ██    ██    ██    
 ██   ████ ███████    ██     ██████     ██    

        NEVUS.TOOLS - Token Checker
{RESET}"""

API_BASE = "https://discord.com/api/v9"

def check_token(token: str):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    result = {}

    # Check if token valid
    r = requests.get(f"{API_BASE}/users/@me", headers=headers)
    if r.status_code != 200:
        result["valid"] = False
        return result
    
    data = r.json()
    result["valid"] = True
    result["username"] = f'{data.get("username")}#{data.get("discriminator")}'
    result["email"] = data.get("email")

    # Nitro check
    nitro_type = data.get("premium_type", 0)
    if nitro_type == 1:
        result["nitro"] = "Nitro Classic"
    elif nitro_type == 2:
        result["nitro"] = "Nitro"
    else:
        result["nitro"] = "No Nitro"

    # Redeemable check (only if no Nitro active)
    if result["nitro"] == "No Nitro":
        r = requests.get(f"{API_BASE}/users/@me/entitlements/gifts", headers=headers)
        if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) == 0:
            result["redeemable"] = True
        else:
            result["redeemable"] = False
    else:
        result["redeemable"] = False

    # Boosts check
    free_count = 0
    cooldown_count = 0
    used_count = 0

    # Active boosts
    r = requests.get(f"{API_BASE}/users/@me/guilds/premium/subscriptions", headers=headers)
    subs = r.json() if r.status_code == 200 else []

    # Cooldowns
    r2 = requests.get(f"{API_BASE}/users/@me/guilds/premium/cooldowns", headers=headers)
    cooldowns = r2.json() if r2.status_code == 200 else []

    if subs:
        # All subs = used boosts
        used_count = len(subs)

    if cooldowns:
        for cd in cooldowns:
            cooldown = cd.get("cooldown_ends_at")
            if cooldown:
                cooldown_time = datetime.fromisoformat(cooldown.replace("Z", "+00:00"))
                if cooldown_time > datetime.now(timezone.utc):
                    cooldown_count += 1
                else:
                    free_count += 1
            else:
                free_count += 1

    if free_count == cooldown_count == used_count == 0:
        result["boosts"] = "No Boosts"
    else:
        result["boosts"] = f"{free_count} Free, {cooldown_count} Cooldown, {used_count} Used"

    return result


if __name__ == "__main__":
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)

    if not os.path.exists("tkn.txt"):
        print("⚠️ tkn.txt not found! Add tokens (one per line).")
        exit()

    with open("tkn.txt", "r") as f:
        tokens = [line.strip() for line in f if line.strip()]

    for token in tokens:
        info = check_token(token)
        if not info["valid"]:
            print(f"{GREEN}[INVALID] {token[:25]}...{RESET}")
        else:
            print(f"""{GREEN}
[VALID] {info['username']}
📧 Email: {info['email']}
🚀 Nitro: {info['nitro']}
🎁 Redeemable: {info['redeemable']}
💎 Boosts: {info['boosts']}
{RESET}""")
