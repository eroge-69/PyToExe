import pyautogui
import time
import threading
from collections import deque
import tkinter as tk


# إعدادات قابلة للتغيير من المستخدم
عدم_الحركة_بالثواني = 5       # ثواني عدم حركة الماوس قبل النقل للمنتصف
مدة_التوهج_بالثواني = 2       # مدة ظهور التوهج بعد تحريك الماوس


# لتخزين مواقع الماوس لتحليل المسارات
المسارات = deque(maxlen=100)
آخر_موقع = pyautogui.position()
توهج_نشط = False


def نقل_للمنتصف():
    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(screen_width // 2, screen_height // 2)


def توهج():
    global توهج_نشط
    if توهج_نشط:
        return
    توهج_نشط = True


    root = tk.Tk()
    root.overrideredirect(True)
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.6)
    root.config(bg='yellow')


    w, h = 150, 150
    x, y = pyautogui.position()
    root.geometry(f"{w}x{h}+{x - w//2}+{y - h//2}")


    def اغلاق():
        global توهج_نشط
        توهج_نشط = False
        root.destroy()


    root.after(int(مدة_التوهج_بالثواني * 1000), اغلاق)
    root.mainloop()


def احفظ_المسار():
    while True:
        x, y = pyautogui.position()
        المسارات.append((x, y))
        time.sleep(0.1)


def احسب_الاتجاه_الغالب():
    dx_total = 0
    dy_total = 0
    for i in range(1, len(المسارات)):
        dx_total += المسارات[i][0] - المسارات[i - 1][0]
        dy_total += المسارات[i][1] - المسارات[i - 1][1]


    return dx_total / max(len(المسارات),1), dy_total / max(len(المسارات),1)


def تحريك_ذكي():
    while True:
        dx, dy = احسب_الاتجاه_الغالب()
        لو_الاتجاه_واضح = abs(dx) > 5 or abs(dy) > 5
        if لو_الاتجاه_واضح:
            x, y = pyautogui.position()
            pyautogui.moveTo(x + dx * 0.2, y + dy * 0.2, duration=0.1)
        time.sleep(0.5)


def راقب_الماوس():
    global آخر_موقع
    while True:
        الموقع_الحالي = pyautogui.position()
        if الموقع_الحالي == آخر_موقع:
            time.sleep(عدم_الحركة_بالثواني)
            لو_ما_تحركش = pyautogui.position() == آخر_موقع
            if لو_ما_تحركش:
                نقل_للمنتصف()
        else:
            آخر_موقع = الموقع_الحالي
            threading.Thread(target=توهج).start()
        time.sleep(0.5)


# تشغيل الوظائف في الخلفية
threading.Thread(target=احفظ_المسار, daemon=True).start()
threading.Thread(target=تحريك_ذكي, daemon=True).start()
threading.Thread(target=راقب_الماوس, daemon=True).start()


# إبقاء البرنامج شغال
while True:
    time.sleep(1)