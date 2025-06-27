import os
import json
import base64
import shutil
import sqlite3
import win32crypt
from Crypto.Cipher import AES
import datetime
import tkinter as tk
from tkinter import ttk

BROWSERS = {
    "Chrome": r"AppData\Local\Google\Chrome\User Data\Default",
    "Edge": r"AppData\Local\Microsoft\Edge\User Data\Default",
    "Brave": r"AppData\Local\BraveSoftware\Brave-Browser\User Data\Default",
    "Vivaldi": r"AppData\Local\Vivaldi\User Data\Default",
    "Opera": r"AppData\Roaming\Opera Software\Opera Stable",
    "Opera GX": r"AppData\Roaming\Opera Software\Opera GX Stable"
}

def get_path(*parts):
    return os.path.join(os.environ['USERPROFILE'], *parts)

def get_local_state_path(browser_path):
    return os.path.join(os.path.dirname(browser_path), "Local State")

def get_master_key(local_state_path):
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except Exception:
        return None

def decrypt_value(buff, master_key):
    try:
        if buff[:3] != b'v10':
            return buff.decode(errors='ignore')
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except Exception:
        return ""

def copy_db(src):
    tmp_db = "temp_db.db"
    try:
        shutil.copy2(src, tmp_db)
        return tmp_db
    except Exception:
        return None

def chrome_time_to_datetime(chrome_time):
    try:
        if chrome_time == 0:
            return "Nie"
        epoch_start = datetime.datetime(1601, 1, 1)
        delta = datetime.timedelta(microseconds=chrome_time)
        dt = epoch_start + delta
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Ungültig"

class BrowserDataApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Browser Daten Ausleser")
        self.geometry("1100x700")

        # Links: Browserliste
        self.browser_tree = ttk.Treeview(self)
        self.browser_tree.heading("#0", text="Browser")
        self.browser_tree.pack(side=tk.LEFT, fill=tk.Y)
        for browser in BROWSERS:
            self.browser_tree.insert('', 'end', text=browser)
        self.browser_tree.bind("<<TreeviewSelect>>", self.on_browser_select)

        # Rechts: Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Tabs & Tabellen vorbereiten
        self.tabs = {}
        self.tables = {}

        for section in ['Passwörter', 'Cookies', 'Verlauf']:
            tab = ttk.Frame(self.notebook)
            self.notebook.add(tab, text=section)
            self.tabs[section] = tab

            table = ttk.Treeview(tab, columns=("1", "2", "3"), show="headings")
            table.pack(fill=tk.BOTH, expand=True)
            self.tables[section] = table

            if section == 'Passwörter':
                table.heading("1", text="URL")
                table.heading("2", text="Benutzername")
                table.heading("3", text="Passwort")
            elif section == 'Cookies':
                table.heading("1", text="Host")
                table.heading("2", text="Name")
                table.heading("3", text="Wert")
            elif section == 'Verlauf':
                table.heading("1", text="Zeit")
                table.heading("2", text="Titel")
                table.heading("3", text="URL")

    def on_browser_select(self, event):
        selected = self.browser_tree.selection()
        if not selected:
            return
        browser_name = self.browser_tree.item(selected[0])['text']
        self.load_browser_data(browser_name)

    def clear_tables(self):
        for table in self.tables.values():
            for row in table.get_children():
                table.delete(row)

    def load_browser_data(self, name):
        self.clear_tables()

        path = BROWSERS[name]
        browser_path = get_path(*path.split('\\'))
        local_state_path = get_local_state_path(browser_path)
        master_key = get_master_key(local_state_path)
        if not master_key:
            self.tables['Passwörter'].insert("", "end", values=("Master Key konnte nicht geladen werden", "", ""))
            return

        self.load_passwords(name, browser_path, master_key)
        self.load_cookies(name, browser_path, master_key)
        self.load_history(name, browser_path)

    def load_passwords(self, name, browser_path, master_key):
        db_path = os.path.join(browser_path, "Login Data")
        if not os.path.exists(db_path):
            self.tables['Passwörter'].insert("", "end", values=("Keine Login-Daten gefunden", "", ""))
            return
        tmp_db = copy_db(db_path)
        if not tmp_db:
            self.tables['Passwörter'].insert("", "end", values=("Konnte Datenbank nicht kopieren", "", ""))
            return
        try:
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            rows = cursor.fetchall()
            if not rows:
                self.tables['Passwörter'].insert("", "end", values=("Keine Passwörter gefunden", "", ""))
            else:
                for url, user, pwd_encrypted in rows:
                    if name.lower() == "chrome":
                        pwd = "Bitte Website aufrufen und ChromePW Revealer nutzen"
                    else:
                        pwd = decrypt_value(pwd_encrypted, master_key)
                    self.tables['Passwörter'].insert("", "end", values=(url, user, pwd))
            cursor.close()
            conn.close()
        finally:
            os.remove(tmp_db)

    def load_cookies(self, name, browser_path, master_key):
        db_path = os.path.join(browser_path, "Cookies")
        if not os.path.exists(db_path):
            self.tables['Cookies'].insert("", "end", values=("Keine Cookies gefunden", "", ""))
            return
        tmp_db = copy_db(db_path)
        if not tmp_db:
            self.tables['Cookies'].insert("", "end", values=("Konnte Datenbank nicht kopieren", "", ""))
            return
        try:
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            rows = cursor.fetchall()
            if not rows:
                self.tables['Cookies'].insert("", "end", values=("Keine Cookies gefunden", "", ""))
            else:
                for host, name_c, enc_val in rows:
                    val = decrypt_value(enc_val, master_key)
                    self.tables['Cookies'].insert("", "end", values=(host, name_c, val))
            cursor.close()
            conn.close()
        finally:
            os.remove(tmp_db)

    def load_history(self, name, browser_path):
        db_path = os.path.join(browser_path, "History")
        if not os.path.exists(db_path):
            self.tables['Verlauf'].insert("", "end", values=("Kein Verlauf gefunden", "", ""))
            return
        tmp_db = copy_db(db_path)
        if not tmp_db:
            self.tables['Verlauf'].insert("", "end", values=("Konnte Verlauf nicht kopieren", "", ""))
            return
        try:
            conn = sqlite3.connect(tmp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 20")
            rows = cursor.fetchall()
            if not rows:
                self.tables['Verlauf'].insert("", "end", values=("Kein Verlauf vorhanden", "", ""))
            else:
                for url, title, time in rows:
                    visit = chrome_time_to_datetime(time)
                    self.tables['Verlauf'].insert("", "end", values=(visit, title, url))
            cursor.close()
            conn.close()
        finally:
            os.remove(tmp_db)

if __name__ == "__main__":
    app = BrowserDataApp()
    app.mainloop()
