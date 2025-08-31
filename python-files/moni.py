import os
import time
import requests

# --- CONFIG ---
BOT_TOKEN = "7758683061:AAFapXOu-UAJBsf8Iokq65kp-C1CY9MyA8g"       # Replace with your bot token
CHAT_ID = "7660485006"           # Replace with your chat ID
FILE_PATH = "good.txt"        # Path to the file
CHECK_INTERVAL = 20 * 60           # 20 minutes in seconds
# ---------------

def send_file():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(FILE_PATH, "rb") as f:
        files = {"document": f}
        data = {"chat_id": CHAT_ID}
        response = requests.post(url, data=data, files=files)
    return response.status_code

def get_file_size_kb(path):
    return os.path.getsize(path) // 1024  # size in KB

def main():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return
    
    last_size = get_file_size_kb(FILE_PATH)
    print(f"Starting monitoring... initial size: {last_size} KB")

    while True:
        time.sleep(CHECK_INTERVAL)
        
        if os.path.exists(FILE_PATH):
            current_size = get_file_size_kb(FILE_PATH)
            if current_size != last_size:
                print(f"File changed! Sending to Telegram... (Size: {current_size} KB)")
                status = send_file()
                print(f"Sent with status: {status}")
                last_size = current_size
            else:
                print("No change detected, skipping.")
        else:
            print("File not found. Retrying...")

if __name__ == "__main__":
    main()
