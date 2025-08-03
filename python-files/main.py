import aiohttp
import asyncio
import json
import tkinter as tk
from tkinter import messagebox, scrolledtext
import threading
import uuid
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

# ---------------------- Playfab Backend Functions ----------------------

async def loginPlayfabAccount(session, url, payload, accountType, deviceId):
    async with session.post(url, json=payload) as response:
        print(f"Sent {accountType}: {deviceId}")
        return response.status

async def verifyTitleId(titleId):
    async with aiohttp.ClientSession() as session:
        custom_id = str(uuid.uuid4())
        payload = {
            "TitleId": titleId,
            "CustomId": custom_id,
            "CreateAccount": True,
            "InfoRequestParameters": {
                "GetUserAccountInfo": True
            }
        }
        url = f"https://{titleId}.playfabapi.com/Client/LoginWithCustomID"
        async with session.post(url, json=payload) as response:
            return response.status == 200

def getAccountTypeInfo(titleId, deviceId):
    return [
        ("android", f"https://{titleId}.playfabapi.com/Client/LoginWithAndroidDeviceID", {
            "TitleId": titleId,
            "AndroidDeviceId": deviceId,
            "CreateAccount": True,
            "InfoRequestParameters": {"GetUserAccountInfo": True}
        }),
        ("nintendo", f"https://{titleId}.playfabapi.com/Client/LoginWithNintendoSwitchDeviceID", {
            "TitleId": titleId,
            "NintendoSwitchDeviceId": deviceId,
            "CreateAccount": True,
            "InfoRequestParameters": {"GetUserAccountInfo": True}
        }),
        ("ios", f"https://{titleId}.playfabapi.com/Client/LoginWithIOSDeviceID", {
            "TitleId": titleId,
            "DeviceId": deviceId,
            "CreateAccount": True,
            "InfoRequestParameters": {"GetUserAccountInfo": True}
        })
    ]

async def create_accounts(titleId, num_accounts, device_id, log_callback=None):
    if await verifyTitleId(titleId):
        async with aiohttp.ClientSession() as session:
            for i in range(num_accounts):
                tasks = [
                    loginPlayfabAccount(session, url, payload, accountType, device_id)
                    for accountType, url, payload in getAccountTypeInfo(titleId, device_id)
                ]
                results = await asyncio.gather(*tasks)
                if log_callback:
                    log_callback(f"Created account {i+1}/{num_accounts} with statuses: {results}")
    else:
        if log_callback:
            log_callback("Invalid Title ID.")

# ---------------------- DLC Pulling Logic ----------------------

async def fetch_dlc(titleid, log_callback):
    login_payload = {
        "TitleId": titleid,
        "CustomId": "2837107398472340",
        "CreateAccount": True
    }
    login_url = f"https://{titleid}.playfabapi.com/Client/LoginWithCustomID"

    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_payload) as login_response:
            login_data = await login_response.json()
            session_ticket = login_data.get("data", {}).get("SessionTicket", None)
            if not session_ticket:
                log_callback("❌ Failed to get session ticket.")
                return

        dlc_url = f"https://{titleid}.playfabapi.com/Client/GetCatalogItems"
        headers = {
            "X-Authorization": session_ticket,
            "Content-Type": "application/json"
        }

        async with session.post(dlc_url, headers=headers, json={"X-PlayfabSDK": "PlayfabSDK/2.94.210118"}) as dlc_response:
            dlc_data = await dlc_response.json()
            with open("dlc_output.json", "w") as f:
                json.dump(dlc_data, f, indent=4)
            log_callback("✅ DLC saved to dlc_output.json")

# ---------------------- Webhook Spammer Logic ----------------------

async def spam_webhook(url, message, count, log_callback):
    async with aiohttp.ClientSession() as session:
        for i in range(count):
            json_data = {"content": message}
            try:
                async with session.post(url, json=json_data) as resp:
                    if resp.status in (200, 204):
                        log_callback(f"✅ Sent message {i+1}/{count}")
                    else:
                        log_callback(f"❌ Failed to send message {i+1}/{count} (Status: {resp.status})")
            except Exception as e:
                log_callback(f"❌ Exception on message {i+1}/{count}: {e}")
            await asyncio.sleep(0.5)  # slight delay

# ---------------------- Player Data Manager Logic ----------------------

async def fetch_player_data(titleId, log_callback):
    login_payload = {
        "TitleId": titleId,
        "CustomId": str(uuid.uuid4()),
        "CreateAccount": True
    }
    login_url = f"https://{titleId}.playfabapi.com/Client/LoginWithCustomID"

    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_payload) as login_response:
            login_data = await login_response.json()
            session_ticket = login_data.get("data", {}).get("SessionTicket", None)
            if not session_ticket:
                log_callback("❌ Failed to get session ticket.")
                return

        get_data_url = f"https://{titleId}.playfabapi.com/Client/GetUserData"
        headers = {
            "X-Authorization": session_ticket,
            "Content-Type": "application/json"
        }
        payload = {}
        async with session.post(get_data_url, headers=headers, json=payload) as data_response:
            data = await data_response.json()
            log_callback(json.dumps(data, indent=4))

# ---------------------- Item Granting Logic ----------------------

async def grant_item_to_user(titleId, playfab_id, item_id, amount, log_callback):
    login_payload = {
        "TitleId": titleId,
        "CustomId": str(uuid.uuid4()),
        "CreateAccount": True
    }
    login_url = f"https://{titleId}.playfabapi.com/Client/LoginWithCustomID"
    
    async with aiohttp.ClientSession() as session:
        async with session.post(login_url, json=login_payload) as login_response:
            login_data = await login_response.json()
            session_ticket = login_data.get("data", {}).get("SessionTicket", None)
            if not session_ticket:
                log_callback("❌ Failed to get session ticket.")
                return
        
        grant_url = f"https://{titleId}.playfabapi.com/Client/GrantItemsToUser"
        headers = {
            "X-Authorization": session_ticket,
            "Content-Type": "application/json"
        }

        for i in range(amount):
            try:
                async with session.post(grant_url, headers=headers, json={
                    "PlayFabId": playfab_id,
                    "ItemIds": [item_id],
                    "Annotation": "Granted by PlayFab Multi-Tool"
                }) as grant_response:
                    resp_data = await grant_response.json()
                    if grant_response.status == 200:
                        log_callback(f"✅ Granted {item_id} ({i+1}/{amount}) to {playfab_id}")
                    else:
                        log_callback(f"❌ Failed to grant item ({i+1}/{amount}): {resp_data.get('errorMessage', 'Unknown error')}")
            except Exception as e:
                log_callback(f"❌ Exception on granting item ({i+1}/{amount}): {e}")

# ---------------------- GUI Classes ----------------------

class PlayfabAccountsGUI(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=20)
        self.root = root
        root.title("Cisntsharp's Playfab Multi-Tool")
        root.geometry("620x580")
        root.resizable(False, False)
        self.grid(sticky="NSEW")
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Playfab Multi-Tool", font=("Poppins", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(0,15))

        ttk.Label(self, text="Title ID:", font=("Segoe UI", 11)).grid(row=1, column=0, sticky="W", pady=8)
        self.title_id_entry = ttk.Entry(self, width=30, bootstyle="dark")
        self.title_id_entry.grid(row=1, column=1, pady=8, sticky="EW")

        ttk.Label(self, text="Number of Accounts:", font=("Segoe UI", 11)).grid(row=2, column=0, sticky="W", pady=8)
        self.num_accounts_entry = ttk.Entry(self, width=30, bootstyle="dark")
        self.num_accounts_entry.grid(row=2, column=1, pady=8, sticky="EW")

        ttk.Button(self, text="Create Accounts", bootstyle="success outline",
                   command=self.create_accounts_on_click).grid(row=3, column=0, columnspan=2, pady=(15, 10), sticky="EW")

        ttk.Button(self, text="Open DLC Puller", bootstyle="info outline",
                   command=self.open_dlc_puller).grid(row=4, column=0, columnspan=2, pady=(0,10), sticky="EW")

        ttk.Button(self, text="Webhook Spammer", bootstyle="danger outline",
                   command=self.open_webhook_spammer).grid(row=5, column=0, columnspan=2, pady=(0,10), sticky="EW")

        ttk.Button(self, text="Player Data Manager", bootstyle="warning outline",
                   command=self.open_player_data_manager).grid(row=6, column=0, columnspan=2, pady=(0,10), sticky="EW")

        ttk.Button(self, text="Item Granting Tool", bootstyle="primary outline",
                   command=self.open_item_granting_tool).grid(row=7, column=0, columnspan=2, pady=(0,10), sticky="EW")

        self.log_box = scrolledtext.ScrolledText(self, height=10, state='disabled')
        self.log_box.grid(row=8, column=0, columnspan=2, sticky="NSEW", pady=10)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.config(state='disabled')
        self.log_box.see(tk.END)

    def create_accounts_on_click(self):
        title_id = self.title_id_entry.get()
        try:
            num_accounts = int(self.num_accounts_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Number of accounts must be an integer.")
            return

        if not title_id:
            messagebox.showerror("Invalid Input", "Title ID cannot be empty.")
            return

        device_id = "1234567890abcdef"

        self.log(f"Creating {num_accounts} accounts for Title ID: {title_id}")
        threading.Thread(target=self.run_async_create_accounts, args=(title_id, num_accounts, device_id), daemon=True).start()

    def run_async_create_accounts(self, titleId, num_accounts, device_id):
        asyncio.run(create_accounts(titleId, num_accounts, device_id, self.log))
        self.log(f"✅ Finished creating accounts for {titleId}")

    def open_dlc_puller(self):
        DLCWindow(self)

    def open_webhook_spammer(self):
        WebhookSpammerGUI(self)

    def open_player_data_manager(self):
        PlayerDataGUI(self)

    def open_item_granting_tool(self):
        ItemGrantingGUI(self)

class DLCWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("DLC Puller")
        self.geometry("600x400")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Enter Title ID for DLC Pulling", font=("Segoe UI", 12, "bold")).pack(pady=10)

        self.title_id_entry = ttk.Entry(self, width=40, bootstyle="dark")
        self.title_id_entry.pack(pady=5)

        self.output_text = scrolledtext.ScrolledText(self, height=12, state="disabled")
        self.output_text.pack(pady=10, fill="both", expand=True)

        ttk.Button(self, text="Pull DLC", bootstyle="success outline", command=self.start_dlc_pull).pack(pady=5)

    def log(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.config(state='disabled')
        self.output_text.see(tk.END)

    def start_dlc_pull(self):
        titleId = self.title_id_entry.get()
        if not titleId:
            messagebox.showerror("Input Error", "Please enter a Title ID.")
            return
        self.log(f"Starting DLC pull for Title ID: {titleId}")
        threading.Thread(target=self.run_async_dlc, args=(titleId,), daemon=True).start()

    def run_async_dlc(self, titleId):
        asyncio.run(fetch_dlc(titleId, self.log))

class WebhookSpammerGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Webhook Spammer")
        self.geometry("520x400")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Webhook URL:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.webhook_url_entry = ttk.Entry(self, width=60, bootstyle="dark")
        self.webhook_url_entry.pack(padx=10, pady=5)

        ttk.Label(self, text="Message:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.message_entry = ttk.Entry(self, width=60, bootstyle="dark")
        self.message_entry.pack(padx=10, pady=5)

        ttk.Label(self, text="Number of Messages:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.num_messages_entry = ttk.Entry(self, width=20, bootstyle="dark")
        self.num_messages_entry.pack(padx=10, pady=5)

        ttk.Button(self, text="Start Spamming", bootstyle="danger outline", command=self.start_spam).pack(pady=10)

        self.log_box = scrolledtext.ScrolledText(self, height=10, state='disabled')
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.config(state='disabled')
        self.log_box.see(tk.END)

    def start_spam(self):
        url = self.webhook_url_entry.get()
        message = self.message_entry.get()
        try:
            count = int(self.num_messages_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Number of messages must be an integer.")
            return

        if not url or not message:
            messagebox.showerror("Invalid Input", "URL and message cannot be empty.")
            return

        self.log(f"Starting spam: {count} messages to {url}")
        threading.Thread(target=self.run_async_spam, args=(url, message, count), daemon=True).start()

    def run_async_spam(self, url, message, count):
        asyncio.run(spam_webhook(url, message, count, self.log))
        self.log("✅ Finished spamming webhook.")

class PlayerDataGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Player Data Manager")
        self.geometry("520x400")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Title ID:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.title_id_entry = ttk.Entry(self, width=40, bootstyle="dark")
        self.title_id_entry.pack(padx=10, pady=5)

        ttk.Button(self, text="Fetch Player Data", bootstyle="warning outline", command=self.start_fetch_data).pack(pady=10)

        self.log_box = scrolledtext.ScrolledText(self, height=15, state='disabled')
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.config(state='disabled')
        self.log_box.see(tk.END)

    def start_fetch_data(self):
        titleId = self.title_id_entry.get()
        if not titleId:
            messagebox.showerror("Input Error", "Please enter a Title ID.")
            return
        self.log(f"Fetching player data for Title ID: {titleId}")
        threading.Thread(target=self.run_async_fetch, args=(titleId,), daemon=True).start()

    def run_async_fetch(self, titleId):
        asyncio.run(fetch_player_data(titleId, self.log))

class ItemGrantingGUI(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Item Granting Tool")
        self.geometry("520x420")
        self.resizable(False, False)
        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Title ID:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.title_id_entry = ttk.Entry(self, width=40, bootstyle="dark")
        self.title_id_entry.pack(padx=10, pady=5)

        ttk.Label(self, text="PlayFab ID:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.playfab_id_entry = ttk.Entry(self, width=40, bootstyle="dark")
        self.playfab_id_entry.pack(padx=10, pady=5)

        ttk.Label(self, text="Item ID:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.item_id_entry = ttk.Entry(self, width=40, bootstyle="dark")
        self.item_id_entry.pack(padx=10, pady=5)

        ttk.Label(self, text="Amount:", font=("Segoe UI", 11)).pack(anchor="w", padx=10, pady=5)
        self.amount_entry = ttk.Entry(self, width=20, bootstyle="dark")
        self.amount_entry.pack(padx=10, pady=5)

        ttk.Button(self, text="Grant Item(s)", bootstyle="primary outline", command=self.start_grant_item).pack(pady=10)

        self.log_box = scrolledtext.ScrolledText(self, height=12, state='disabled')
        self.log_box.pack(padx=10, pady=10, fill="both", expand=True)

    def log(self, message):
        self.log_box.config(state='normal')
        self.log_box.insert(tk.END, message + "\n")
        self.log_box.config(state='disabled')
        self.log_box.see(tk.END)

    def start_grant_item(self):
        titleId = self.title_id_entry.get()
        playfab_id = self.playfab_id_entry.get()
        item_id = self.item_id_entry.get()
        try:
            amount = int(self.amount_entry.get())
        except ValueError:
            messagebox.showerror("Invalid Input", "Amount must be an integer.")
            return

        if not titleId or not playfab_id or not item_id:
            messagebox.showerror("Invalid Input", "Title ID, PlayFab ID, and Item ID cannot be empty.")
            return

        self.log(f"Granting {amount}x {item_id} to {playfab_id} on Title {titleId}")
        threading.Thread(target=self.run_async_grant, args=(titleId, playfab_id, item_id, amount), daemon=True).start()

    def run_async_grant(self, titleId, playfab_id, item_id, amount):
        asyncio.run(grant_item_to_user(titleId, playfab_id, item_id, amount, self.log))
        self.log("✅ Finished granting items.")
        

# ---------------------- Main Application Entry ----------------------

def main():
    root = ttk.Window(themename="darkly")
    app = PlayfabAccountsGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
