
import os
import time
import ctypes
import sys

def full_screen_effect():
    os.system('mode con: cols=700 lines=60')
    os.system('color 0C')
    for _ in range(5):
        os.system('cls')
        print("█" * 200)
        print("🔥 SYSTEM BREACH DETECTED 🔥".center(200))
        print("█" * 200)
        time.sleep(0.4)
        os.system('cls')
        time.sleep(0.2)

def message_loop():
    for i in range(10):
        ctypes.windll.user32.MessageBoxW(0,
            "🔴 لا تحاول إيقاف الفايروس... لقد فات الأوان!\nملفاتك تُحذف الآن!",
            "🔥 SYSTEM HACKED 🔥", 0)
        time.sleep(0.3)

def fake_delete_screen():
    os.system("cls")
    os.system("color 04")
    print("\n" * 5)
    print("🧨 جاري حذف ملفات النظام ... الرجاء عدم الإغلاق ...")
    for i in range(100):
        sys.stdout.write(f"حذف الملف رقم: {i + 1}/100\r")
        sys.stdout.flush()
        time.sleep(0.05)
    time.sleep(1.5)

def reveal_joke():
    os.system("cls")
    os.system("color 0A")
    print("\n" * 5)
    print("💀💀💀")
    time.sleep(1.5)
    print("\n" * 2 + "لكن....".center(80))
    time.sleep(1.5)
    print("\n" * 2 + "🤣 Rahim خدعك يا وحش، جهازك بخير ❤️".center(80))
    ctypes.windll.user32.MessageBoxW(0,
        "🤣 Rahim خدعك! لا يوجد فايروس، فقط مقلب نظيف 😎",
        "مفاجأة!", 0)

def main():
    full_screen_effect()
    message_loop()
    fake_delete_screen()
    reveal_joke()

main()
