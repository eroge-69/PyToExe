import os
import time
import platform
from itertools import cycle

# قائمة ألوان ANSI لتغيير الألوان في terminal
colors = [
    "\033[91m", "\033[92m", "\033[93m", "\033[94m",
    "\033[95m", "\033[96m", "\033[97m"
]

# شعار LETD
logo = """
L     EEEEE TTTTT DDDD
L     E       T   D   D
L     EEEE    T   D   D
L     E       T   D   D
LLLL  EEEEE   T   DDDD
"""

# طباعة الشعار بلون ثابت في البداية
print("\033[95m" + logo)

# إدخال IP من المستخدم
IP = input("Enter The IP: ")

# تحديد الخيار الصحيح لأمر ping حسب نظام التشغيل
param = "-n" if platform.system().lower() == "windows" else "-c"

# عمل حلقة لتغيير الألوان بشكل دائري
color_cycle = cycle(colors)

try:
    while True:
        color = next(color_cycle)
        # مسح الشاشة في كل مرة
        os.system('cls' if platform.system().lower() == 'windows' else 'clear')
        # طباعة الشعار
        print(color + logo)
        # تنفيذ ping والتحقق من النتيجة
        response = os.system(f"ping {param} 1 {IP} >nul 2>&1")
        if response == 0:
            print(color + f"{IP} is online")
        else:
            print(color + f"{IP} is offline...")
        # تأخير لمدة ثانية
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")

# تمنع نافذة التيرمنال من الإغلاق عند التشغيل بالنقر المزدوج
input("Press Enter to exit...")

