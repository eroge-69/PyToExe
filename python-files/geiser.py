import requests
import random
import time
from datetime import datetime
import re

base_names = [
    "coolguy", "hotdog", "bananamike", "epicgamer", "robloxian", "builderman",
    "ninjaboy", "cutegirl", "legend", "shadow", "fireboy", "watergirl", "dragon",
    "wolfboy", "pikachu", "pokemon", "minecrafter", "steve", "creeper", "herobrine",
    "killer", "sniper", "crazybob", "sparkle", "awesomekid", "john", "alex", "jake",
    "nick", "max", "ethan", "dylan", "zack", "tyler", "ryan", "kevin", "jordan",
    "brandon", "ashley", "jessica", "sarah", "zoe", "emma", "bunnygirl", "kittycat",
    "puppylove", "baconhair", "guest", "racerx", "swordmaster", "skyfall", "blaster",
    "phantom", "doom", "zeus", "nyancat", "rainbowboy", "epicface", "milktoast",
    "toasterguy", "captain", "agent", "samurai", "wizard"
]

class KeySystem:
    def __init__(self):
        self.access_expiry = 0
        self.cooldown_start = 0

    def current_time(self):
        return int(time.time() * 1000)

    def use_key(self, input_key):
        now = self.current_time()

        if input_key != "geiser6172":
            return "❌ Invalid key."

        if now < self.access_expiry:
            remaining = self.access_expiry - now
            return f"⏳ You already have access for another {round(remaining / 60000)} minutes."

        if now < self.cooldown_start + 10 * 60 * 1000:
            remaining = (self.cooldown_start + 10 * 60 * 1000) - now
            return f"⏳ Access expired. Please wait {round(remaining / 60000)} minutes before requesting again."

        self.access_expiry = now + 2 * 60 * 60 * 1000
        self.cooldown_start = 0
        return "✅ Access granted for 2 hours!"

    def start_cooldown(self):
        self.cooldown_start = self.current_time()

    def has_access(self):
        return self.current_time() < self.access_expiry

def generate_random_username():
    base = random.choice(base_names)
    digits = random.randint(100, 99999)
    return f"{base}{digits}"

def generate_potential_passwords(username, creation_year):
    match = re.match(r"^([a-zA-Z]+)(\d*)$", username)
    if not match:
        return []

    name = match.group(1)
    fixed_digits = ["12", "123", "2020", "2021", "2022", "2023"]

    passwords = []

    for digits in fixed_digits:
        passwords.append(f"{name}{digits}")
        passwords.append(f"{digits}{name}")

    if creation_year and str(creation_year) not in fixed_digits:
        passwords.append(f"{name}{creation_year}")
        passwords.append(f"{creation_year}{name}")

    return list(set(passwords))

def check_username(username):
    try:
        res = requests.post("https://users.roblox.com/v1/usernames/users", json={"usernames": [username]})
        user_data = res.json()["data"][0]
        if not user_data:
            print(f"[❌] {username} not found.")
            return

        user_id = user_data["id"]
        info = requests.get(f"https://users.roblox.com/v1/users/{user_id}").json()
        created_str = info.get("created", "")
        created = datetime.fromisoformat(created_str.replace("Z", "")) if created_str else None

        if not created:
            print(f"[❌] {username} (ID: {user_id}) - Invalid or missing creation date.")
            return

        creation_year = created.year
        years_ago = datetime.now().year - creation_year
        date_str = created.strftime("%Y-%m-%d")

        msg = f"[✅] {username} (ID: {user_id}) - Created: {date_str}"
        show_passwords = False

        if 9 <= years_ago <= 11:
            msg += " 🔹 Possibly inactive 9–11 years"
            show_passwords = True
        elif years_ago > 11:
            msg += " 🕰️ Over 11 years old"
            show_passwords = True
        else:
            msg += " ⚠️ Likely newer or active"

        print(msg)

        if show_passwords:
            passwords = generate_potential_passwords(username, creation_year)
            if passwords:
                print("Potential Passwords:", ", ".join(passwords))

    except Exception as e:
        print(f"[❌] Error checking {username}: {str(e)}")

def main():
    key_system = KeySystem()

    while True:
        input_key = input("Enter your key: ").strip()
        result = key_system.use_key(input_key)
        print(result)
        if result.startswith("✅"):
            break

    print("Booting Up Geiser...\n")

    while True:
        if not key_system.has_access():
            print("Access expired! Starting cooldown...")
            key_system.start_cooldown()
            print("Waiting 10 minutes cooldown...")
            time.sleep(10 * 60)

            while True:
                input_key = input("Enter your key to regain access: ").strip()
                result = key_system.use_key(input_key)
                print(result)
                if result.startswith("✅"):
                    break

        username = generate_random_username()
        check_username(username)
        time.sleep(0.6)

if __name__ == "__main__":
    main()
