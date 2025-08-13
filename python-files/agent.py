# agent.py
import time
import random
import string
import requests
import urllib3

# غیرفعال کردن هشدار SSL چون آدرس شما https ولی بدون امضا است
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

SERVER_URL = "https://192.168.3.100"

def generate_uid():
    """تولید UID تصادفی شبیه RFID"""
    return ''.join(random.choices(string.hexdigits.upper(), k=8))

def send_uid(uid):
    try:
        response = requests.post(
            SERVER_URL,
            json={"uid": uid, "username": "DOMAIN\\TestUser"},
            verify=False
        )
        print(f"[SERVER RESPONSE] {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    print("Agent started (test mode). Press Ctrl+C to exit.")
    try:
        while True:
            uid = generate_uid()
            print(f"[UID] {uid}")
            send_uid(uid)
            time.sleep(5)
    except KeyboardInterrupt:
        print("\nAgent stopped.")
