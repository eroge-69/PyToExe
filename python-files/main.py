
# Merged Loader Main
# Includes: login, register, license check, webhook, IP ban, HWID, keygen, Discord bots

import tkinter as tk
from tkinter import messagebox, ttk
import json, os, uuid, socket, requests
from datetime import datetime
from pathlib import Path

# === Config ===
WEBHOOK_URL = "https://discord.com/api/webhooks/1399063886283407603/P1xe1-rhlXC0K-u3kM9yeXKTeqZ0SEp15mTpWhGtQsrQ2z1zjOguCDN38ZugBua17yoh"

# === HWID & IP ===
def get_hwid():
    return str(uuid.getnode())

def get_ip_and_location():
    try:
        ip_data = requests.get("https://ipinfo.io/json").json()
        return ip_data["ip"], ip_data.get("country", "Unknown")
    except:
        return "0.0.0.0", "Unknown"

def is_ip_banned(ip):
    try:
        with open("banned_ips.json", "r") as f:
            banned = json.load(f)
        return ip in banned
    except:
        return False

# === License & Ban ===
def is_license_expired(key):
    try:
        with open("keys.json", "r") as f:
            keys = json.load(f)
        if key in keys:
            expiry_str = keys[key].get("expires")
            if not expiry_str or expiry_str == "lifetime":
                return False
            expiry = datetime.strptime(expiry_str, "%Y-%m-%d")
            return datetime.now() > expiry
    except:
        return True
    return True

def validate_login(username, password, key):
    try:
        with open("banned_keys.json", "r") as f:
            banned = json.load(f)
        if key in banned:
            return False, "Key is banned."
    except:
        pass

    try:
        with open("keys.json", "r") as f:
            keys = json.load(f)
        info = keys.get(key)
        if info and info.get("user") == username and info.get("password") == password:
            ip, _ = get_ip_and_location()
            if is_ip_banned(ip):
                return False, "IP is banned."
            if is_license_expired(key):
                return False, "License expired."
            hwid = get_hwid()
            if info.get("hwid") not in ["", "NULL", None, hwid]:
                return False, "HWID mismatch."
            return True, info
    except:
        pass
    return False, "Invalid credentials."

def send_webhook(username, key, result="Login Success"):
    hwid = get_hwid()
    ip, _ = get_ip_and_location()
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    content = (
        f"🟢 Login Attempt\n"
        f"📋 Result: {result}\n"
        f"👤 User: {username}\n"
        f"🔑 Key: {key}\n"
        f"🖥️ HWID: {hwid}\n"
        f"🌐 IP: {ip}\n"
        f"🕒 Time: {timestamp}"
    )
    try:
        requests.post(WEBHOOK_URL, json={"content": content})
    except:
        pass

# === UI Functions ===
def login_action():
    username = username_entry.get()
    password = password_entry.get()
    key = license_entry.get()
    success, info = validate_login(username, password, key)
    if success:
        if remember_var.get():
            with open("remember_me.txt", "w") as f:
                f.write(f"{username}\n{password}\n{key}")
        send_webhook(username, key, "Login Success")
        root.destroy()
        MainLoaderUI(username)
    else:
        send_webhook(username, key, info)
        messagebox.showerror("Login Failed", info)

def register_action():
    username = username_entry.get()
    password = password_entry.get()
    key = license_entry.get()
    if not all([username, password, key]):
        messagebox.showerror("Missing Info", "Fill in all fields.")
        return
    try:
        with open("keys.json", "r") as f:
            keys = json.load(f)
        if key not in keys:
            messagebox.showerror("Error", "Key not found.")
            return
        if keys[key].get("user"):
            messagebox.showerror("Used", "Key already registered.")
            return
        keys[key]["user"] = username
        keys[key]["password"] = password
        keys[key]["hwid"] = get_hwid()
        with open("keys.json", "w") as f:
            json.dump(keys, f, indent=2)
        if remember_var.get():
            with open("remember_me.txt", "w") as f:
                f.write(f"{username}\n{password}\n{key}")
        messagebox.showinfo("Registered", "Account registered.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

def build_login_window():
    global root, username_entry, password_entry, license_entry, remember_var
    root = tk.Tk()
    root.title("Loader 311")
    root.geometry("320x320")
    root.configure(bg="black")

    tk.Label(root, text="Username", bg="black", fg="white").pack()
    username_entry = tk.Entry(root)
    username_entry.pack()

    tk.Label(root, text="Password", bg="black", fg="white").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack()

    tk.Label(root, text="License Key", bg="black", fg="white").pack()
    license_entry = tk.Entry(root)
    license_entry.pack()

    remember_var = tk.BooleanVar()
    tk.Checkbutton(root, text="Remember me", variable=remember_var, bg="black", fg="white").pack()

    tk.Button(root, text="OK", command=login_action).pack(pady=5)
    tk.Button(root, text="Cancel", command=root.quit).pack()
    tk.Button(root, text="Register", command=register_action).pack(pady=5)

    try:
        with open("remember_me.txt", "r") as f:
            u, p, k = f.read().splitlines()
            username_entry.insert(0, u)
            password_entry.insert(0, p)
            license_entry.insert(0, k)
            login_action()
    except:
        pass

    root.mainloop()

class MainLoaderUI:
    def __init__(self, username):
        self.root = tk.Tk()
        self.root.title("Loader UI")
        self.root.geometry("600x400")
        tk.Label(self.root, text=f"Welcome {username}", anchor="w").pack(fill="x", padx=10, pady=5)
        self.root.mainloop()

if __name__ == "__main__":
    build_login_window()
