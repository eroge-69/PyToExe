import threading
import requests
import tkinter as tk
from tkinter import simpledialog, messagebox
from flask import Flask, request
import subprocess
import time
import os
import json
import imaplib
import email
from email.header import decode_header
import sys
from tkinter import filedialog
import zipfile
def install_dependencies():
    required = [
        "requests",
        "flask",
        "tk",
        "pyinstaller"
    ]
    for pkg in required:
        try:
            __import__(pkg if pkg != "tk" else "tkinter")
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

install_dependencies()
# === Flask App ===
app = Flask(__name__)

# === Static PiShock Configuration ===
PISHOCK_USERNAME = "RascleFire"
PISHOCK_APIKEY = "24007cac-4dfc-4841-a0c3-19500a1e6851"
PISHOCK_SHARECODE = "2E66874B2E1"

# === Configuration ===
CONFIG_FILE = "config.json"
EMAIL_CONFIG_FILE = "email_config.json"
EMAIL_ADDRESS = "lucaspi.shock@gmail.com"
EMAIL_PASSWORD = "mccbcgkrqsycypzq"
EMAIL_SERVER = "imap.gmail.com"
EMAIL_PORT = 993

# === Global Variables ===
status_label = None
ngrok_url_label = None
ngrok_path = ""

# === PiShock Shock Function ===
def send_pishock_shock(duration=2, intensity=50, name="ShockTriggerApp"):
    url = "https://do.pishock.com/api/apioperate/"
    payload = {
        "Username": "RascleFire",
        "Name": "Venmo 5 Dollar Donation",
        "Code": "2E66874B2E1",
        "Apikey": "24007cac-4dfc-4841-a0c3-19500a1e6851",
        "Op": 0,               # 0 = Shock, 1 = Vibrate, 2 = Beep
        "Duration": "1",  # Duration in seconds (1–15)
        "Intensity": "20" # Intensity 1–100
    }
    response = requests.post(url, json=payload)
    return response.status_code == 200

# === Email Monitoring ===
def load_email_config():
    global EMAIL_ADDRESS, EMAIL_PASSWORD
    if os.path.exists(EMAIL_CONFIG_FILE):
        with open(EMAIL_CONFIG_FILE, "r") as f:
            config = json.load(f)
            EMAIL_ADDRESS = config.get("email", "")
            EMAIL_PASSWORD = config.get("password", "")
    else:
        root_prompt = tk.Tk()
        root_prompt.withdraw()
        EMAIL_ADDRESS = simpledialog.askstring("Email Setup", "Enter Gmail address to monitor for Venmo payments:")
        EMAIL_PASSWORD = simpledialog.askstring("Email Setup", "Enter Gmail app password:", show='*')
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            messagebox.showerror("Error", "Email and password are required.")
            return
        with open(EMAIL_CONFIG_FILE, "w") as f:
            json.dump({"email": EMAIL_ADDRESS, "password": EMAIL_PASSWORD}, f)

def monitor_email_for_venmo():
    last_seen_uids = set()
    while True:
        try:
            mail = imaplib.IMAP4_SSL(EMAIL_SERVER, EMAIL_PORT)
            mail.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            mail.select("inbox")

            status, messages = mail.search(None, '(UNSEEN)')
            uids = set(messages[0].split())

            new_uids = uids - last_seen_uids
            if new_uids:
                print(f"🔍 Found {len(new_uids)} new unread payment emails.")
            for num in new_uids:
                res, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject = decode_header(msg["Subject"])[0][0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(errors="ignore")

                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors="ignore")
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors="ignore")

                        print("----- New Email -----")
                        print("Subject:", subject)
                        print("Body:", body)
                        print("----------------------")

                        if "$5.00" in subject or any(f"${amount:.2f}" in subject for amount in range(6, 10000)):
                            success = send_pishock_shock()
                            if status_label:
                                status_label.config(
                                    text="💥 $5 Venmo email received! Shock Triggered!" if success else "⚠️ Shock Failed"
                                )
            last_seen_uids.update(new_uids)
            mail.logout()
        except Exception as e:
            print("❌ Email monitor error:", e)
        time.sleep(10)

# === Flask Placeholder ===
@app.route("/venmo-payment", methods=["POST"])
def venmo_payment():
    try:
        data = request.json or request.form.to_dict()
        note = data.get("note", "")
        amount = float(data.get("amount", "0"))
        if amount == 5.00 and "shock" in note.lower():
            success = send_pishock_shock()
            if status_label:
                status_label.config(text="💥 $5 Venmo payment received! Shock Triggered!" if success else "⚠️ Shock Failed")
    except Exception as e:
        print("Venmo payment error:", e)
    return "OK"

# === Flask Starter ===
def start_flask():
    app.run(port=5000)

# === Ngrok Starter ===
def start_ngrok():
    global ngrok_path
    try:
        subprocess.Popen([ngrok_path, "http", "5000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(3)
        tunnels = requests.get("http://localhost:4040/api/tunnels").json()["tunnels"]
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                return tunnel["public_url"]
    except Exception as e:
        print("Ngrok start error:", e)
    return None

# === GUI Application ===
def start_gui():
    global status_label, ngrok_url_label, ngrok_path


    # Load ngrok path
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            ngrok_path = config.get("ngrok_path", "")

    if not ngrok_path or not os.path.exists(ngrok_path):
        root_prompt = tk.Tk()
        root_prompt.withdraw()
        messagebox.showinfo("ngrok Setup", "Select a folder to install ngrok.exe.")
        folder = filedialog.askdirectory(title="Select Folder for ngrok.exe")
        if not folder:
            messagebox.showerror("Error", "No folder selected for ngrok.exe.")
            return

        ngrok_exe = os.path.join(folder, "ngrok.exe")
        if not os.path.exists(ngrok_exe):
            # Download ngrok.exe
            try:
                import urllib.request
                ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-windows-amd64.zip"
                zip_path = os.path.join(folder, "ngrok.zip")
                urllib.request.urlretrieve(ngrok_url, zip_path)
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(folder)
                os.remove(zip_path)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to download/extract ngrok.exe: {e}")
                return

        ngrok_path = ngrok_exe
        with open(CONFIG_FILE, "w") as f:
            json.dump({"ngrok_path": ngrok_path}, f)

    # Load email credentials and start monitor
    load_email_config()
    threading.Thread(target=monitor_email_for_venmo, daemon=True).start()

    # Build GUI
    root = tk.Tk()
    root.title("PiShock Venmo Trigger")

    tk.Label(root, text="Start the server to monitor $5 Venmo emails with 'shock' in the message.", font=("Arial", 14)).pack(pady=10)

    def on_start():
        status_label.config(text="🔄 Starting Flask server...")
        threading.Thread(target=start_flask, daemon=True).start()
        time.sleep(2)

        status_label.config(text="🚀 Starting ngrok tunnel...")
        public_url = start_ngrok()
        if public_url:
            payment_url = f"{public_url}/venmo-payment"
            ngrok_url_label.config(text=f"Webhook URL \n{payment_url}")
            status_label.config(text="✅ Server ready! Also monitoring email inbox.")
        else:
            status_label.config(text="❌ ngrok failed to start or return a tunnel.")

    # Track server state and process
    server_running = [False]
    ngrok_process = [None]

    def stop_ngrok():
        if ngrok_process[0] and ngrok_process[0].poll() is None:
            ngrok_process[0].terminate()
            try:
                ngrok_process[0].wait(timeout=5)
            except Exception:
                ngrok_process[0].kill()
        ngrok_process[0] = None

    def on_start_stop():
        if not server_running[0]:
            status_label.config(text="🔄 Starting Flask server...")
            threading.Thread(target=start_flask, daemon=True).start()
            time.sleep(2)

            status_label.config(text="🚀 Starting ngrok tunnel...")
            try:
                ngrok_process[0] = subprocess.Popen([ngrok_path, "http", "5000"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(3)
                tunnels = requests.get("http://localhost:4040/api/tunnels").json()["tunnels"]
                public_url = None
                for tunnel in tunnels:
                    if tunnel["proto"] == "https":
                        public_url = tunnel["public_url"]
                        break
                if public_url:
                    payment_url = f"{public_url}/venmo-payment"
                    ngrok_url_label.config(text=f"Webhook URL \n{payment_url}")
                    status_label.config(text="✅ Server ready! Also monitoring email inbox.")
                    server_running[0] = True
                    start_stop_btn.config(text="Stop Server", bg="#dc3545")
                else:
                    status_label.config(text="❌ ngrok failed to start or return a tunnel.")
            except Exception as e:
                status_label.config(text=f"❌ ngrok error: {e}")
        else:
            status_label.config(text="🛑 Stopping ngrok server...")
            stop_ngrok()
            ngrok_url_label.config(text="")
            status_label.config(text="Server stopped. Email monitor still running.")
            server_running[0] = False
            start_stop_btn.config(text="Start Server", bg="#28a745")

    start_stop_btn = tk.Button(root, text="Start Server", command=on_start_stop, bg="#28a745", fg="white", padx=20, pady=5)
    start_stop_btn.pack(pady=10)

    def test_shock():
        success = send_pishock_shock()
        status_label.config(text="⚡ Shock sent manually!" if success else "⚠️ Shock failed.")

    tk.Button(root, text="Test Shock", command=test_shock, bg="#007bff", fg="white", padx=20, pady=5).pack(pady=5)

    ngrok_url_label = tk.Label(root, text="", font=("Arial", 10), fg="blue")
    ngrok_url_label.pack(pady=5)

    status_label = tk.Label(root, text="Idle", font=("Arial", 12))
    status_label.pack(pady=20)

    root.mainloop()

# === Start Application ===
if __name__ == "__main__":
    start_gui()
