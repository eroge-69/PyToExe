
import json
import requests
import tkinter as tk
from tkinter import ttk, messagebox

# Load config
with open("config.json", "r") as f:
    config = json.load(f)

API_URL = config.get("server_url", "")
TOKEN = config.get("auth_token", "")

def fetch_friends():
    headers = {"Authorization": f"Bearer {TOKEN}"}
    try:
        response = requests.get(f"{API_URL}/friends", headers=headers, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load friends list:\n{e}")
        return []

def on_gift():
    selected_friend = friend_var.get()
    if not selected_friend:
        messagebox.showwarning("Select Friend", "Please select a friend to gift.")
        return
    messagebox.showinfo("Gifting", f"Sending gift to {selected_friend}...")

root = tk.Tk()
root.title("Sirius Gifting Launcher")
friend_var = tk.StringVar()

friends = fetch_friends()
friend_names = [f["name"] for f in friends]

ttk.Label(root, text="Select Friend to Gift:").pack(padx=10, pady=5)
friend_combo = ttk.Combobox(root, textvariable=friend_var, values=friend_names, state="readonly")
friend_combo.pack(padx=10, pady=5)
friend_combo.current(0 if friend_names else -1)

gift_btn = ttk.Button(root, text="Send Gift", command=on_gift)
gift_btn.pack(padx=10, pady=10)

root.mainloop()
