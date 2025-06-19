import tkinter as tk
from tkinter import messagebox
import requests
import threading
import time
import sys

# Login GUI
def show_login():
    def login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "trssty" and password == "trssty":
            login_window.destroy()
            show_main_menu()
        else:
            messagebox.showerror("Greška", "Pogrešan username ili lozinka.")

    login_window = tk.Tk()
    login_window.title("Login")
    login_window.geometry("300x150")
    login_window.resizable(False, False)

    tk.Label(login_window, text="Username").pack()
    username_entry = tk.Entry(login_window)
    username_entry.pack()

    tk.Label(login_window, text="Password").pack()
    password_entry = tk.Entry(login_window, show="*")
    password_entry.pack()

    tk.Button(login_window, text="Login", command=login).pack(pady=10)
    login_window.mainloop()

# Spammer funkcija
def spam_webhook(webhook_url):
    message = "Srecna nova godina svima!"
    headers = {
        "Content-Type": "application/json"
    }
    while True:
        try:
            payload = {
                "content": message
            }
            response = requests.post(webhook_url, json=payload, headers=headers)
            if response.status_code == 204 or response.status_code == 200:
                print("✅ Poruka poslata.")
            else:
                print("⚠️ Greška:", response.status_code)
            time.sleep(0.7)
        except Exception as e:
            print("❌ Došlo je do greške:", e)
            break

# Terminal meni
def show_main_menu():
    print("=== Ulogovan si kao trssty ===")
    print("1 | Spammer")
    opcija = input("Izaberi opciju: ")
    if opcija == "1":
        webhook = input("Unesi Webhook URL: ")
        t = threading.Thread(target=spam_webhook, args=(webhook,))
        t.daemon = True
        t.start()
        print("🔫 Spammer aktiviran. Pritisni Ctrl+C za prekid.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 Zaustavljeno.")
            sys.exit()
    else:
        print("Nepoznata opcija.")

# Pokreni
show_login()
