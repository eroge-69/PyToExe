import requests
import smtplib
from email.mime.text import MIMEText
import time

# OpenWeatherMap সেটিংস
API_KEY = "abc50629fa0a9ce40f890fad3c64b242"  # এখানে আপনার কপি করা API key দিন
CITY = "Naogaon"  # আপনার শহরের নাম
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}"

# Gmail সেটিংস
GMAIL_USER = "amitrayar19784@gmail.com"
GMAIL_PASS = "qqbl zgxn bqzr jphk"  # Gmail App Password দিন
TO_EMAIL = "amitrayar19784@gmail.com"

def check_rain():
    response = requests.get(URL)
    data = response.json()
    weather = data['weather'][0]['main'].lower()
    print("আবহাওয়া:", weather)
    return "rain" in weather or "drizzle" in weather

def send_email():
    msg = MIMEText("বৃষ্টি শুরু হয়েছে! দয়া করে কাপড় উঠিয়ে ফেলুন।")
    msg["Subject"] = "⚠️ বৃষ্টি পড়ছে!"
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(GMAIL_USER, GMAIL_PASS)
    server.send_message(msg)
    server.quit()
    print("✅ ইমেইল পাঠানো হয়েছে!")

# মেইন লুপ
while True:
    try:
        if check_rain():
            send_email()
            time.sleep(3600)  # ১ ঘণ্টা অপেক্ষা করবে
        else:
            print("❌ এখনো বৃষ্টি হচ্ছে না।")
            time.sleep(600)  # প্রতি ১০ মিনিট পর চেক করবে
    except Exception as e:
        print("⚠️ ভুল:", e)
        time.sleep(600)
