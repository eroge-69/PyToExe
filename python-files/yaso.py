import os
import time
import datetime
import ctypes

def show_message(message):
    ctypes.windll.user32.MessageBoxW(0, message, "تنبيه", 1)

while True:
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute

    # لو الساعة 1:00 بالظبط
    if hour == 1 and minute == 0:
        show_message("الساعة 1 صباحًا! سيتم إيقاف الجهاز بعد 10 دقائق.")
        time.sleep(600)  # 10 دقائق

        os.system("shutdown /s /f /t 1")  # إيقاف الجهاز

    # لو الجهاز فتح قبل 6 الصبح
    if hour < 6:
        show_message("ممنوع استخدام الجهاز قبل 6 صباحًا. سيتم الإغلاق الآن.")
        os.system("shutdown /s /f /t 1")

    time.sleep(30)  # يشيك كل نص دقيقة
