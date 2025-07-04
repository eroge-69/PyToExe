
import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
import subprocess

def login():
    token = entry.get().strip()
    if not token:
        messagebox.showerror("Błąd", "Wklej token!")
        return

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        profile = requests.get("https://api.minecraftservices.com/minecraft/profile", headers=headers)
        if profile.status_code != 200:
            messagebox.showerror("Błąd", "Nieprawidłowy token lub brak internetu.")
            return
        data = profile.json()
        uuid = data.get("id", "")
        username = data.get("name", "")

        if not uuid or not username:
            messagebox.showerror("Błąd", "Nie udało się pobrać danych konta.")
            return

        feather_path = os.path.join(os.getenv("APPDATA"), ".feather")
        os.makedirs(feather_path, exist_ok=True)
        acc_path = os.path.join(feather_path, "accounts.json")

        acc_data = {
            "accounts": [
                {
                    "type": "msa",
                    "access_token": token,
                    "uuid": uuid,
                    "username": username
                }
            ]
        }

        with open(acc_path, "w") as f:
            json.dump(acc_data, f, indent=2)

        feather_exe = os.path.join("C:\\Program Files\\FeatherClient\\FeatherClient.exe")
        if os.path.exists(feather_exe):
            subprocess.Popen([feather_exe])
        else:
            messagebox.showinfo("Uwaga", "Nie znaleziono FeatherClient.exe. Uruchom go ręcznie.")

        messagebox.showinfo("Sukces", f"Zalogowano jako {username}!")

    except Exception as e:
        messagebox.showerror("Błąd", f"Wystąpił problem: {str(e)}")

root = tk.Tk()
root.title("Feather Token Login")
root.geometry("400x150")
root.resizable(False, False)

label = tk.Label(root, text="Wklej Microsoft Token:")
label.pack(pady=10)

entry = tk.Entry(root, width=50)
entry.pack()

button = tk.Button(root, text="Zaloguj", command=login)
button.pack(pady=10)

root.mainloop()
