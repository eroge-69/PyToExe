import smtplib
from email.message import EmailMessage

def check_for_word(file_path, word="dupl"):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            return word in content
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

def send_email_notification(subject, body, to_email):
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = "spinimport@leoni.com"
    msg['To'] = to_email

    try:
        with smtplib.SMTP('outlook.leoni.com', 25) as server:
            server.send_message(msg)
        print("Email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")

file_path = r'D:\ANeT\Log\Spinimport.log'

if check_for_word(file_path):
    send_email_notification(
        subject="Upozornenie: Nájdené slovo 'dupl'",
        body=f"Slovo 'dupl' bolo nájdené v súbore: {file_path}",
        to_email="wsktr-it-admins@internal.leoni.com"
    )
else:
    print("Slovo 'dupl' nebolo nájdené.")
