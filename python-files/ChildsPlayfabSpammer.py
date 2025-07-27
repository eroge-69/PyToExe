import subprocess
import sys
import threading

def install_if_missing(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Package '{package}' not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_if_missing('aiohttp')
install_if_missing('colorama')

import aiohttp
import asyncio
import tkinter as tk
import uuid
import random
import string
from colorama import Fore, init

init(autoreset=True)

def random_suffix(length=3):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

async def login_and_set_display_name(session, title_id, base_device_id, base_display_name):
    suffix = " " + random_suffix(3)
    max_display_length = 25
    max_device_id_length = 128

    allowed_display_base_len = max_display_length - len(suffix)
    truncated_display_name = base_display_name[:allowed_display_base_len]
    full_display_name = truncated_display_name + suffix

    device_suffix = " " + random_suffix(3)
    allowed_device_base_len = max_device_id_length - len(device_suffix)
    truncated_device_id = base_device_id[:allowed_device_base_len]
    full_device_id = truncated_device_id + device_suffix

    login_url = f"https://{title_id}.playfabapi.com/Client/LoginWithAndroidDeviceID"
    payload = {
        "TitleId": title_id,
        "AndroidDeviceId": full_device_id,
        "CreateAccount": True,
        "InfoRequestParameters": {"GetUserAccountInfo": True}
    }

    async with session.post(login_url, json=payload) as response:
        if response.status == 200:
            result = await response.json()
            session_ticket = result.get("data", {}).get("SessionTicket")

            if session_ticket:
                update_url = f"https://{title_id}.playfabapi.com/Client/UpdateUserTitleDisplayName"
                update_payload = {"DisplayName": full_display_name}
                headers = {"X-Authorization": session_ticket}

                async with session.post(update_url, json=update_payload, headers=headers) as update_response:
                    if update_response.status == 200:
                        print(f"{Fore.GREEN}Set display name to: '{full_display_name}' for device: {full_device_id}")
                    else:
                        text = await update_response.text()
                        print(f"{Fore.RED}Failed to set display name for device: {full_device_id}, Response: {update_response.status} {text}")
            else:
                print(f"{Fore.YELLOW}No session ticket for device: {full_device_id}")
        else:
            text = await response.text()
            print(f"{Fore.RED}Login failed for device: {full_device_id}, Response: {response.status} {text}")

async def verify_title_id(title_id):
    async with aiohttp.ClientSession() as session:
        test_id = str(uuid.uuid4())
        payload = {
            "TitleId": title_id,
            "CustomId": test_id,
            "CreateAccount": True,
            "InfoRequestParameters": {"GetUserAccountInfo": True}
        }
        url = f"https://{title_id}.playfabapi.com/Client/LoginWithCustomID"
        async with session.post(url, json=payload) as response:
            return response.status == 200

async def create_accounts(title_id, num_accounts, base_device_id, pause_time, base_display_name):
    is_valid = await verify_title_id(title_id)
    if not is_valid:
        print(Fore.RED + "Invalid Title ID.")
        return

    async with aiohttp.ClientSession() as session:
        for i in range(num_accounts):
            print(Fore.CYAN + f"Creating account {i + 1} of {num_accounts}...")

            await login_and_set_display_name(session, title_id, base_device_id, base_display_name)

            if i < num_accounts - 1:
                print(Fore.YELLOW + f"Waiting {pause_time} seconds before next account...\n")
                await asyncio.sleep(pause_time)

        print(Fore.GREEN + "All accounts created.")

def start_account_creation():
    title_id = titleIdEntry.get().strip()
    if not (3 <= len(title_id) <= 6):
        print(Fore.RED + "Title ID must be 5 to 6 characters long.")
        return

    try:
        num = int(numAccountsEntry.get())
        pause = int(pauseTimeEntry.get())
    except ValueError:
        print(Fore.RED + "Invalid number or pause time.")
        return

    base_device_id = accountIDEntry.get().strip() or str(uuid.uuid4())[:8]
    base_display_name = displayNameEntry.get().strip()

    if not base_display_name:
        print(Fore.RED + "Display name cannot be empty.")
        return

    threading.Thread(target=lambda: asyncio.run(create_accounts(title_id, num, base_device_id, pause, base_display_name)), daemon=True).start()

# GUI
root = tk.Tk()
root.title("PlayFab Spammer By Child")

def make_label_entry(row, label, default=""):
    tk.Label(root, text=label).grid(row=row, column=0, padx=5, pady=5, sticky="w")
    entry = tk.Entry(root, width=40)
    entry.insert(0, default)
    entry.grid(row=row, column=1, padx=5, pady=5)
    return entry

titleIdEntry = make_label_entry(0, "Title ID:")
numAccountsEntry = make_label_entry(1, "Number of Accounts:", "5")
pauseTimeEntry = make_label_entry(2, "Pause Time (sec):", "3")
displayNameEntry = make_label_entry(3, "Display Name:")
accountIDEntry = make_label_entry(4, "Device ID Base:")

tk.Button(root, text="Start", command=start_account_creation).grid(row=5, columnspan=2, pady=15)

root.mainloop()
