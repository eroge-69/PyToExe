# main.py

import requests
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox

# Replace these with your KeyAuth application credentials
KEYAUTH_APP_NAME = "Galaxeegt's Application"
KEYAUTH_OWNER_ID = "nOSHxhiVmn"
KEYAUTH_SECRET = "563399d1519cee4e9cc18cb57807d9c1f95451e34ba6b1a8e40967e89d550990"
KEYAUTH_VERSION = "1.0"

KEYAUTH_API_URL = "https://keyauth.win/api/1.2/"

def keyauth_login(key):
    payload = {
        "type": "login",
        "key": key,
        "name": KEYAUTH_APP_NAME,
        "ownerid": KEYAUTH_OWNER_ID,
        "ver": KEYAUTH_VERSION
    }
    try:
        response = requests.post(KEYAUTH_API_URL, data=payload)
        data = response.json()
        return data.get("success", False)
    except Exception:
        return False

def prompt_for_key():
    root = tk.Tk()
    root.withdraw()
    key = simpledialog.askstring("KeyAuth Login", "Enter your KeyAuth key:")
    root.destroy()
    return key

def main_screen():
    root = tk.Tk()
    root.title("Main Screen")
    label = tk.Label(root, text="Welcome to the main screen!", font=("Arial", 16))
    label.pack(padx=20, pady=20)
    root.mainloop()

def main():
    key = prompt_for_key()
    if not key:
        sys.exit()
    if keyauth_login(key):
        main_screen()
    else:
        messagebox.showerror("Error", "Invalid KeyAuth key.")
        sys.exit()

if __name__ == "__main__":
    main()