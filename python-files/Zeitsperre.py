import customtkinter as ctk
import os
import json
import datetime
import time
import threading
import psutil
import ctypes
from cryptography.fernet import Fernet
from tkinter import messagebox

# === SETTINGS ===
CONFIG_FILE = "config.lock"
KEY_FILE = "key.key"

# === DEFAULTS ===
DEFAULT_PIN = "1234"
DEFAULT_LIMIT = 120  # Minuten

# === ENCRYPTION ===
def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(KEY_FILE):
        generate_key()
    with open(KEY_FILE, "rb") as f:
        return f.read()

fernet = Fernet(load_key())

def encrypt_data(data):
    return fernet.encrypt(json.dumps(data).encode())

def decrypt_data(data):
    return json.loads(fernet.decrypt(data).decode())

# === KONFIG SPEICHERN / LADEN ===
def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_PIN, DEFAULT_LIMIT, 0, str(datetime.date.today()))
    with open(CONFIG_FILE, "rb") as f:
        return decrypt_data(f.read())

def save_config(pin, limit, usage, datum):
    data = {"pin": pin, "limit": limit, "usage": usage, "date": datum}
    with open(CONFIG_FILE, "wb") as f:
        f.write(encrypt_data(data))

def sperre_pc():
    ctypes.windll.user32.LockWorkStation()

# === ZEITÜBERWACHUNG ===
def zeit_überwachung():
    while True:
        time.sleep(60)  # jede Minute
        config = load_config()
        heute = str(datetime.date.today())
        if config["date"] != heute:
            config["usage"] = 0
            config["date"] = heute
        config["usage"] += 1
        save_config(config["pin"], config["limit"], config["usage"], config["date"])
        print(f"[INFO] Nutzung: {config['usage']} / {config['limit']} Minuten")
        if config["usage"] >= config["limit"]:
            sperre_pc()
            break

# === GUI ===
class ZeitSperreApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Zeit-Sperre")
        self.geometry("400x300")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.config_data = load_config()

        self.login_frame = ctk.CTkFrame(self)
        self.menu_frame = ctk.CTkFrame(self)
        self.pin_frame = ctk.CTkFrame(self)

        self.build_login()
        self.build_menu()
        self.build_pin_change()

        self.login_frame.pack(expand=True)

        # Hintergrundthread starten
        threading.Thread(target=zeit_überwachung, daemon=True).start()

    def build_login(self):
        ctk.CTkLabel(self.login_frame, text="Admin-PIN eingeben:").pack(pady=10)
        self.pin_entry = ctk.CTkEntry(self.login_frame, show="*")
        self.pin_entry.pack(pady=10)
        ctk.CTkButton(self.login_frame, text="Login", command=self.check_login).pack(pady=10)

    def build_menu(self):
        ctk.CTkLabel(self.menu_frame, text="Tägliches Zeitlimit (Minuten):").pack(pady=10)
        self.limit_entry = ctk.CTkEntry(self.menu_frame)
        self.limit_entry.insert(0, str(self.config_data["limit"]))
        self.limit_entry.pack(pady=10)

        ctk.CTkButton(self.menu_frame, text="Speichern", command=self.speichern).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="PIN ändern", command=self.show_pin_change).pack(pady=5)
        ctk.CTkButton(self.menu_frame, text="Beenden", command=self.safe_exit).pack(pady=5)

    def build_pin_change(self):
        ctk.CTkLabel(self.pin_frame, text="Neuer PIN:").pack(pady=10)
        self.new_pin = ctk.CTkEntry(self.pin_frame, show="*")
        self.new_pin.pack(pady=5)
        ctk.CTkLabel(self.pin_frame, text="Bestätigen:").pack(pady=10)
        self.new_pin_confirm = ctk.CTkEntry(self.pin_frame, show="*")
        self.new_pin_confirm.pack(pady=5)
        ctk.CTkButton(self.pin_frame, text="PIN speichern", command=self.save_new_pin).pack(pady=10)
        ctk.CTkButton(self.pin_frame, text="Zurück", command=self.show_menu).pack()

    def check_login(self):
        entered = self.pin_entry.get()
        if entered == self.config_data["pin"]:
            self.login_frame.pack_forget()
            self.menu_frame.pack(expand=True)
        else:
            messagebox.showerror("Fehler", "Falscher PIN!")

    def speichern(self):
        try:
            limit = int(self.limit_entry.get())
            self.config_data["limit"] = limit
            self.config_data["usage"] = 0
            self.config_data["date"] = str(datetime.date.today())
            save_config(self.config_data["pin"], limit, 0, self.config_data["date"])
            messagebox.showinfo("Gespeichert", "Zeitlimit gespeichert!")
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige Zahl eingeben!")

    def show_pin_change(self):
        self.menu_frame.pack_forget()
        self.pin_frame.pack(expand=True)

    def show_menu(self):
        self.pin_frame.pack_forget()
        self.menu_frame.pack(expand=True)

    def save_new_pin(self):
        new = self.new_pin.get()
        confirm = self.new_pin_confirm.get()
        if new == confirm and new.strip() != "":
            self.config_data["pin"] = new
            save_config(new, self.config_data["limit"], self.config_data["usage"], self.config_data["date"])
            messagebox.showinfo("PIN geändert", "Neuer PIN gespeichert.")
            self.show_menu()
        else:
            messagebox.showerror("Fehler", "PINs stimmen nicht überein oder sind leer.")

    def safe_exit(self):
        # Schutz gegen Beenden kann hier erweitert werden
        self.destroy()

if __name__ == "__main__":
    app = ZeitSperreApp()
    app.protocol("WM_DELETE_WINDOW", lambda: None)  # Deaktiviert das Schließen-Kreuz
    app.mainloop() 
