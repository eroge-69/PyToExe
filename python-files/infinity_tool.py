import requests
import uuid
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    print(r"""
  _____       _        _ _         _______          _
 |_   _|     (_)      (_) |       |__   __|        | |
   | |  _ __  _ ___ ___ _| |_ ___    | |_ __ __ ___| |
   | | | '_ \| / __/ __| | __/ _ \   | | '__/ _` / __|
  _| |_| | | | \__ \__ \ | ||  __/   | | | | (_| \__ \
 |_____|_| |_|_|___/___/_|\__\___|   |_|_|  \__,_|___/
    """)

def ip_lookup():
    ip = input("Enter IP address: ")
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}")
        data = res.json()
        if data['status'] == 'success':
            for key, value in data.items():
                print(f"{key.title()}: {value}")
        else:
            print("Lookup failed.")
    except Exception as e:
        print(f"Error: {e}")

def webhook_sender():
    url = input("Enter Webhook URL: ")
    message = input("Enter message: ")
    data = {"content": message}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 204:
            print("Message sent successfully.")
        else:
            print(f"Failed to send: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def show_hwid():
    hwid = str(uuid.uuid1())
    print(f"Your HWID: {hwid}")

def main():
    while True:
        clear()
        banner()
        print("Infinitive Tool")
        print("[1] IP Lookup")
        print("[2] WebHook Sender")
        print("[3] Show HWID")
        print("[4] Exit")
        choice = input("Option: ")

        if choice == '1':
            ip_lookup()
        elif choice == '2':
            webhook_sender()
        elif choice == '3':
            show_hwid()
        elif choice == '4':
            break
        else:
            print("Invalid choice!")

        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
