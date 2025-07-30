import requests
import re

# --- Load settings from config.txt ---
config = {}
with open("config.txt") as f:
    for line in f:
        if "=" in line:
            key, value = line.strip().split("=", 1)
            config[key] = value

router_ip = config.get("ip", "http://192.168.0.1")
password = config.get("password", "")

session = requests.Session()

# Step 1: Login (MW305R uses only a password field)
# According to Mercury/Tenda firmware, login is typically a POST to / with password in 'password' or 'Pwd' field
login_url = f"{router_ip}/"
login_data = {
    "password": password
}

print("🔹 Logging in to router...")
session.post(login_url, data=login_data)

# Step 2: Fetch main page to extract current session 'id'
print("🔹 Fetching session ID...")
main_page = session.get(router_ip).text

# Try to find an ID that matches your previous reboot request
token_match = re.search(r'id=([A-Za-z0-9%]+)', main_page)
if not token_match:
    print("❌ Could not find session ID. Please verify login flow.")
    input("Press Enter to exit...")
    exit()

session_id = token_match.group(1)
print(f"✅ Session ID found: {session_id}")

# Step 3: Send reboot POST request
reboot_url = f"{router_ip}/?code=6&asyn=1&id={session_id}"
headers = {
    "Content-Type": "text/plain;charset=UTF-8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{router_ip}/",
    "Origin": router_ip,
    "User-Agent": "Mozilla/5.0"
}

print("🔹 Sending reboot command...")
response = session.post(reboot_url, headers=headers)

if response.status_code == 200:
    print("✅ Reboot command sent successfully!")
else:
    print(f"❌ Failed with status code {response.status_code}")

input("Press Enter to exit...")
