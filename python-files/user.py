import requests
import random
import string

def generate_usernames(length, count=10):
    chars = string.ascii_lowercase + string.digits
    usernames = set()
    while len(usernames) < count:
        usernames.add(''.join(random.choice(chars) for _ in range(length)))
    return list(usernames)

def check_tiktok(username):
    url = f"https://www.tiktok.com/@{username}"
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 404   # 404 يعني متاح
    except:
        return False

def check_discord(username):
    url = f"https://discord.com/users/{username}"
    try:
        r = requests.get(url, timeout=5)
        return r.status_code == 404   # 404 يعني متاح
    except:
        return False

# تجربة
usernames = generate_usernames(3, 10)

for u in usernames:
    tiktok_status = "✅ متاح" if check_tiktok(u) else "❌ محجوز"
    discord_status = "✅ متاح" if check_discord(u) else "❌ محجوز"
    print(f"{u} | TikTok: {tiktok_status} | Discord: {discord_status}")
