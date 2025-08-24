import requests
import threading
import time
from colorama import init, Fore
import fade

init(autoreset=True)

# 🎨 Fire Gradient Banner
def banner():
    art = """
⢀⡴⠑⡄⠀⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠸⡇⠀⠿⡀⠀⠀⠀⣀⡴⢿⣿⣿⣿⣿⣿⣿⣿⣷⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠑⢄⣠⠾⠁⣀⣄⡈⠙⣿⣿⣿⣿⣿⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⢀⡀⠁⠀⠀⠈⠙⠛⠂⠈⣿⣿⣿⣿⣿⠿⡿⢿⣆⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⢀⡾⣁⣀⠀⠴⠂⠙⣗⡀⠀⢻⣿⣿⠭⢤⣴⣦⣤⣹⠀⠀⠀⢀⢴⣶⣆ 
⠀⠀⢀⣾⣿⣿⣿⣷⣮⣽⣾⣿⣥⣴⣿⣿⡿⢂⠔⢚⡿⢿⣿⣦⣴⣾⠁⠸⣼⡿ 
⠀⢀⡞⠁⠙⠻⠿⠟⠉⠀⠛⢹⣿⣿⣿⣿⣿⣌⢤⣼⣿⣾⣿⡟⠉⠀⠀⠀⠀⠀ 
⠀⣾⣷⣶⠇⠀⠀⣤⣄⣀⡀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠉⠈⠉⠀⠀⢦⡈⢻⣿⣿⣿⣶⣶⣶⣶⣤⣽⡹⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠉⠲⣽⡻⢿⣿⣿⣿⣿⣿⣿⣷⣜⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣷⣶⣮⣭⣽⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⣀⣀⣈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠇⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀ 
⠀⠀⠀⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠟⠁⠀Shrekk X
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠻⠿⠿⠿⠿⠛⠉ Made by unseenvex

1: Webhook Nuker | 2: Webhook Deleter | 3: Webhook Tester | 4: Exit
"""
    print(fade.brazil(art))
    time.sleep(0.2)

# 🔒 Global Pause Flag
pause_all = threading.Event()

# 🔁 Message Sender Thread with Hard Global Pause
def send_loop(url, username, msg, loops, idx):
    for i in range(loops):
        if pause_all.is_set():
            print(Fore.RED + f"[{i+1}] RATE LIMIT DETECTED. Bypassing rate limitation.")
            time.sleep(5)
            continue

        try:
            payload = {
                "content": msg,
                "username": username
            }
            r = requests.post(url, json=payload)

            if r.status_code == 204:
                print(Fore.GREEN + f"[{i+1}] Sent to Webhook {idx+1}")
            elif r.status_code == 429:
                print(Fore.RED + f"[{i+1}] Rate limited on Webhook {idx+1}. Triggering global cooldown.")
                pause_all.set()
                time.sleep(5)
                pause_all.clear()
                continue
            else:
                print(Fore.RED + f"[{i+1}] Failed ({r.status_code}) on Webhook {idx+1}")
        except Exception as e:
            print(Fore.RED + f"[{i+1}] Error on Webhook {idx+1}: {e}")

        time.sleep(0.8)

# 🧊 Multi-Webhooks Sender
def send_messages():
    try:
        count = int(input(Fore.GREEN + "\nHow many webhooks do you want to use?\n>> "))
        webhooks = []
        for i in range(count):
            url = input(f"Webhook {i+1} URL: ").strip()
            webhooks.append(url)
    except ValueError:
        print(Fore.RED + "Invalid input. Try again.")
        return

    username = input(Fore.GREEN + "\nEnter a username to use for all webhooks:\n>> ")
    msg = input(Fore.GREEN + "\nInsert message to send:\n>> ")
    loops = int(input(Fore.GREEN + "How many messages per webhook?\n>> "))

    print(Fore.CYAN + f"\nLaunching {count} threads — fast sending with global cooldown...\n")
    threads = []
    for idx, url in enumerate(webhooks):
        t = threading.Thread(target=send_loop, args=(url, username, msg, loops, idx))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

# 🧹 Webhook Deleter
def delete_webhook():
    url = input(Fore.YELLOW + "\nInsert webhook URL to delete:\n>> ").strip()
    try:
        r = requests.delete(url)
        if r.status_code == 204:
            print(Fore.RED + "Webhook deleted successfully.")
        else:
            print(Fore.RED + f"Failed to delete webhook. Status: {r.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error deleting webhook: {e}")

# 🧪 Webhook Tester
def test_webhook():
    url = input(Fore.GREEN + "\nInsert webhook URL to test:\n>> ").strip()
    try:
        payload = {
            "content": "TEST.",
            "username": "APPLICATION"
        }
        r = requests.post(url, json=payload)
        if r.status_code == 204:
            print(Fore.GREEN + "Test message sent successfully.")
        else:
            print(Fore.RED + f"Failed to send test message. Status: {r.status_code}")
    except Exception as e:
        print(Fore.RED + f"Error testing webhook: {e}")

# 🧭 Main Menu
def main():
    banner()
    while True:
        choice = input(">> ").strip()

        if choice == "1":
            send_messages()
        elif choice == "2":
            delete_webhook()
        elif choice == "3":
            test_webhook()
        elif choice == "4":
            print(Fore.CYAN + "Exiting Discord Webhook Multitool.")
            break
        else:
            print(Fore.RED + "Invalid choice. Try again.")

main()
