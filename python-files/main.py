import random
import string
import requests
import threading
import time

# ========== CONFIGURATION ==========
WEBHOOK_URL = "https://discord.com/api/webhooks/your_webhook_here"
CHECK_URL = "https://discordapp.com/api/v9/entitlements/gift-codes/{}?with_application=false&with_subscription_plan=true"
CODE_LENGTH = 18
THREAD_COUNT = 10
USE_PROXIES = True
PROXY_FILE = "proxies.txt"
DELAY = 0.5  # Delay between attempts (per thread)

# ========== LOAD PROXIES ==========
proxies = []
if USE_PROXIES:
    try:
        with open(PROXY_FILE, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
        print(f"[+] Loaded {len(proxies)} proxies.")
    except FileNotFoundError:
        print("[!] Proxy file not found. Disabling proxy usage.")
        USE_PROXIES = False

proxy_index = 0
proxy_lock = threading.Lock()

# ========== CODE GENERATOR ==========
def generate_code(length=CODE_LENGTH):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# ========== CHECK CODE ==========
def check_code(code):
    global proxy_index
    url = CHECK_URL.format(code)
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*"
    }

    proxies_dict = None
    if USE_PROXIES and proxies:
        with proxy_lock:
            proxy = proxies[proxy_index % len(proxies)]
            proxy_index += 1
        proxies_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }

    try:
        response = requests.get(url, headers=headers, proxies=proxies_dict, timeout=10)
        print(f"[{response.status_code}] Checked: {code}")
        return response.status_code == 200
    except requests.RequestException as e:
        print(f"[!] Request failed for code {code} | {e}")
        return False

# ========== WEBHOOK ALERT ==========
def send_to_webhook(code):
    data = {
        "content": f"✅ Valid Code Found: `{code}`"
    }
    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code in [200, 204]:
            print(f"[+] Webhook sent: {code}")
        else:
            print(f"[!] Webhook failed: {response.status_code}")
    except requests.RequestException as e:
        print(f"[!] Webhook error: {e}")

# ========== SAVE VALID CODE ==========
def save_valid_code(code):
    with open("valid_codes.txt", "a") as f:
        f.write(code + "\n")

# ========== WORKER LOOP ==========
def worker():
    while True:
        code = generate_code()
        if check_code(code):
            send_to_webhook(code)
            save_valid_code(code)
        time.sleep(DELAY)

# ========== MAIN ==========
if __name__ == "__main__":
    print(f"[✓] Starting {THREAD_COUNT} threads...\n")
    for _ in range(THREAD_COUNT):
        threading.Thread(target=worker, daemon=True).start()

    while True:
        time.sleep(10)
