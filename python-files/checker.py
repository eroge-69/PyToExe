import requests
import random
import string

# دالة لتوليد يوزرات رباعية عشوائية
def generate_usernames(count=50):
    usernames = []
    chars = string.ascii_lowercase + string.digits
    for _ in range(count):
        usernames.append(''.join(random.choice(chars) for _ in range(4)))
    return usernames

print("=== Discord Username Checker ===")
token = input("[?] أدخل التوكن: ").strip()
password = input("[?] أدخل الباسورد: ").strip()

usernames_to_check = generate_usernames(50)

url = "https://discord.com/api/v9/users/@me"
headers = {
    "Authorization": token,
    "Content-Type": "application/json"
}

available = []

for username in usernames_to_check:
    payload = {
        "username": username,
        "password": password
    }
    r = requests.patch(url, headers=headers, json=payload)
    if r.status_code == 200:
        print(f"[✔] متاح: {username}")
        available.append(username)
    elif r.status_code == 400:
        print(f"[✘] غير متاح: {username}")
    else:
        print(f"[!] خطأ: {username} - كود {r.status_code}")

# حفظ النتائج
with open("available.txt", "w", encoding="utf-8") as f:
    for name in available:
        f.write(name + "\n")

print("\n✅ تم الحفظ في available.txt")
