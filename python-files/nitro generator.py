import random
import string
import time
import requests

WEBHOOK_URL = "https://canary.discord.com/api/webhooks/1408512615625396385/UDKO1GzZbp1PaUGYVKLLXKu8alOYaPzdVwLVh9Wd3D3OH0JrZbMulSrIGZDSr73BPPnB"

def generate_code(length=24):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def send_to_webhook(url):
    data = {
        "content": url
    }
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"Failed to send to webhook: {e}")

def start_generating():
    count = 1
    while True:
        code = generate_code()
        url = f"https://discord.gift/{code}"
        print(f"[{count}] Sent: {url}")
        send_to_webhook(url)
        count += 1
        time.sleep(1)

start_generating()
