import pyautogui
import cv2
import numpy as np
import time
import keyboard
import os
import sys
import hashlib
import os
import json as jsond
import binascii
import platform
import subprocess
import qrcode
from datetime import datetime, timezone, timedelta
from discord_interactions import verify_key
from PIL import Image

# استيراد tkinter وتسميتها tk لسهولة الاستخدام
import tkinter as tk 
from tkinter import messagebox, simpledialog 
# استخدام Threading لتشغيل حلقة البوت في الخلفية وعدم تجميد الواجهة
import threading 

try:
    if os.name == 'nt':
        import win32security
    import requests
except ModuleNotFoundError:
    print("Exception when importing modules")
    print("Installing necessary modules....")
    if os.path.isfile("requirements.txt"):
        os.system("pip install -r requirements.txt")
    else:
        if os.name == 'nt':
            os.system("pip install pywin32")
        os.system("pip install requests")
        os.system("pip install pyautogui opencv-python numpy keyboard qrcode Pillow discord-interactions")
    print("Modules installed!")
    time.sleep(1.5)
    os._exit(1)


# =================================================================
#       1. دوال الخدمة والمساعدة (UTILITY) - (بدون تغيير)
# =================================================================

def getchecksum():
    md5_hash = hashlib.md5()
    try:
        file_path = os.path.abspath(sys.argv[0])
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
    except Exception:
        return "0" * 32
        
    return md5_hash.hexdigest()

def exiting():
    print("الخروج الآمن...")
    try:
        os._exit(0)
    except:
        try:
            sys.exit()
        except:
            raise SystemExit

# (تم حذف كلاس api و كلاس others هنا لتقليل التكرار، بافتراض أنهما لم يتغيرا عن نسختك)
# **ملاحظة: يجب أن تبقى تعريفات كلاس api و كلاس others كما هي في الملف الأصلي لتشغيل الكود بنجاح.**
# سأضع تعريفات الكلاسات هنا لضمان الاكتمال
# =================================================================
#       تعريفات كلاس API وكلاس others
# =================================================================

class api:
    # ... جميع دوال api كما في الكود الأصلي ...
    # (لغرض الإيجاز، تم حذف الدوال الداخلية هنا، لكن يجب أن تكون موجودة في الكود الفعلي)
    name = ownerid = version = hash_to_check = ""
    sessionid = enckey = ""
    initialized = False
    
    def __init__(self, name, ownerid, version, hash_to_check):
        if len(ownerid) != 10:
            print("Visit https://keyauth.cc/app/, copy Pthon code, and replace code in main.py with that")
            time.sleep(3)
            os._exit(1)
            
        self.name = name
        self.ownerid = ownerid
        self.version = version
        self.hash_to_check = hash_to_check
        self.init()

    def init(self):
        if self.sessionid != "":
            print("You've already initialized!")
            time.sleep(3)
            os._exit(1)
            
        post_data = {
            "type": "init",
            "ver": self.version,
            "hash": self.hash_to_check,
            "name": self.name,
            "ownerid": self.ownerid
        }

        response = self.__do_request(post_data)

        if response == "KeyAuth_Invalid":
            print("The application doesn't exist")
            time.sleep(3)
            os._exit(1)

        json = jsond.loads(response)

        if json["message"] == "invalidver":
            if json["download"] != "":
                print("New Version Available")
                download_link = json["download"]
                os.system(f"start {download_link}")
                time.sleep(3)
                os._exit(1)
            else:
                print("Invalid Version, Contact owner to add download link to latest app version")
                time.sleep(3)
                os._exit(1)

        if not json["success"]:
            print(json["message"])
            time.sleep(3)
            os._exit(1)

        self.sessionid = json["sessionid"]
        self.initialized = True

    # دالة المصادقة
    def license(self, key, code=None, hwid=None):
        self.checkinit()
        if hwid is None:
            hwid = others.get_hwid()

        post_data = {
            "type": "license",
            "key": key,
            "hwid": hwid,
            "sessionid": self.sessionid,
            "name": self.name,
            "ownerid": self.ownerid
        }
        
        if code is not None:
            post_data["code"] = code

        response = self.__do_request(post_data)

        json = jsond.loads(response)

        if json["success"]:
            self.__load_user_data(json["info"])
            return True, json["info"]["username"], json["info"]["subscriptions"][0]["subscription"] if json["info"]["subscriptions"] else "N/A"
        else:
            return False, json["message"], None
    
    # دالة مساعدة للتحقق من التهيئة
    def checkinit(self):
        if not self.initialized:
            print("Initialize first, in order to use the functions")
            time.sleep(3)
            os._exit(1)

    # دوال مساعدة لحفظ بيانات المستخدم والتطبيق
    class application_data_class:
        numUsers = numKeys = app_ver = customer_panel = onlineUsers = ""

    class user_data_class:
        username = ip = hwid = expires = createdate = lastlogin = subscription = subscriptions = ""

    user_data = user_data_class()
    app_data = application_data_class()

    def __load_app_data(self, data):
        self.app_data.numUsers = data["numUsers"]
        self.app_data.numKeys = data["numKeys"]
        self.app_data.app_ver = data["version"]
        self.app_data.customer_panel = data["customerPanelLink"]
        self.app_data.onlineUsers = data["numOnlineUsers"]

    def __load_user_data(self, data):
        self.user_data.username = data["username"]
        self.user_data.ip = data["ip"]
        self.user_data.hwid = data["hwid"] or "N/A"
        if data["subscriptions"]:
            self.user_data.expires = data["subscriptions"][0]["expiry"]
            self.user_data.subscription = data["subscriptions"][0]["subscription"]
        else:
            self.user_data.expires = "N/A"
            self.user_data.subscription = "N/A"

        self.user_data.createdate = data["createdate"]
        self.user_data.lastlogin = data["lastlogin"]
        self.user_data.subscriptions = data["subscriptions"]
        
    # دالة لإرسال الطلب (تم حذف الباقي لضمان الإيجاز)
    def __do_request(self, post_data):
        try:
            response = requests.post(
                "https://keyauth.win/api/1.3/", data=post_data, timeout=10
            )

            if post_data["type"] == "log" or post_data["type"] == "file" or post_data["type"] == "2faenable" or post_data["type"] == "2fadisable" or post_data["type"] == "upgrade" or post_data["type"] == "register" or post_data["type"] == "login" or post_data["type"] == "license":
                return response.text

            signature = response.headers.get("x-signature-ed25519")
            timestamp = response.headers.get("x-signature-timestamp")

            if not signature or not timestamp:
                print("Missing headers for signature verification.")
                time.sleep(3)
                os._exit(1)

            server_time = datetime.fromtimestamp(int(timestamp), timezone.utc)
            current_time = datetime.now(timezone.utc)
            
            buffer_seconds = 5
            time_difference = current_time - server_time

            if time_difference > timedelta(seconds=20 + buffer_seconds):
                print("Timestamp is too old (exceeded 20 seconds + buffer).")
                time.sleep(3)
                os._exit(1)

            if not verify_key(response.text.encode('utf-8'), signature, timestamp, '5586b4bc69c7a4b487e4563a4cd96afd39140f919bd31cea7d1c6a1e8439422b'):
                print("Signature checksum failed. Request was tampered with or session ended most likely.")
                time.sleep(3)
                os._exit(1)

            return response.text

        except requests.exceptions.Timeout:  
            print("Request timed out. Server is probably down/slow at the moment")
            return '{"success":false,"message":"Server timeout"}'
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return '{"success":false,"message":"Client-side error"}'

    # ... جميع الدوال الأخرى (register, upgrade, login, var, getvar, setvar, ban, file, webhook, check, checkblacklist, log, fetchOnline, fetchStats, chatGet, chatSend, changeUsername, logout, enable2fa, disable2fa, display_qr_code) ...

class others:
    # ... جميع دوال others كما في الكود الأصلي ...
    @staticmethod
    def get_hwid():
        if platform.system() == "Linux":
            with open("/etc/machine-id") as f:
                hwid = f.read()
                return hwid
        elif platform.system() == 'Windows':
            winuser = os.getlogin()
            try:
                sid = win32security.LookupAccountName(None, winuser)[0] 
                hwid = win32security.ConvertSidToStringSid(sid)
                return hwid
            except NameError:
                print("Warning: win32security not available, falling back to a different method.")
                cmd = subprocess.Popen(
                    "wmic csproduct get uuid",
                    stdout=subprocess.PIPE,
                    shell=True,
                )
                (output, error) = cmd.communicate()
                hwid = output.split()[1].decode().strip()
                return hwid
        elif platform.system() == 'Darwin':
            output = subprocess.Popen("ioreg -l | grep IOPlatformSerialNumber", stdout=subprocess.PIPE, shell=True).communicate()[0]
            serial = output.decode().split('=', 1)[1].replace(' ', '')
            hwid = serial[1:-2]
            return hwid

# =================================================================
#       2. تهيئة البوت والإعدادات
# =================================================================

SEARCH_RADIUS = 2

TARGET_COLOR1_BGR = np.array([56, 51, 51], dtype=np.uint8)
TARGET_COLOR2_BGR = np.array([45, 41, 41], dtype=np.uint8)

# متغير حالة التشغيل (سيتم التحكم به من الواجهة)
running = False

# متغير لتخزين كائن API
keyauthapp = None 

# =================================================================
#       3. دوال البوت (BOT FUNCTIONS)
# =================================================================

# تبديل حالة تشغيل البوت
def toggle_running_state_gui():
    global running
    running = not running
    if running:
        status_label.config(text="حالة البوت: 🟢 يعمل", fg="green")
        toggle_button.config(text="إيقاف البوت 🛑")
        print("The bot is working now")
    else:
        status_label.config(text="حالة البوت: 🔴 متوقف", fg="red")
        toggle_button.config(text="تشغيل البوت ▶️")
        print("The bot is stopped")
    
    # دمج وظيفة زر '1' مع وظيفة الواجهة
    # لا حاجة لربط مفتاح '1' هنا، بل سنستبدله بالتحكم المباشر في المتغير 'running'

# دالة العثور على اللون والنقر
def find_and_click_color():
    try:
        mouse_x, mouse_y = pyautogui.position()
        region = (mouse_x - SEARCH_RADIUS,
                  mouse_y - SEARCH_RADIUS,
                  SEARCH_RADIUS * 2,
                  SEARCH_RADIUS * 2)

        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

        mask1 = cv2.inRange(screenshot_bgr, TARGET_COLOR1_BGR, TARGET_COLOR1_BGR)
        mask2 = cv2.inRange(screenshot_bgr, TARGET_COLOR2_BGR, TARGET_COLOR2_BGR)
        
        combined_mask = cv2.bitwise_or(mask1, mask2)
        
        coordinates = np.argwhere(combined_mask == 255)

        if len(coordinates) > 0:
            y, x = coordinates[0]
            click_x = region[0] + x
            click_y = region[1] + y
            
            # print(f"تم العثور على أحد اللونين. النقر على ({click_x}, {click_y}).")
            pyautogui.click(click_x, click_y, _pause=False)
            
    except Exception as e:
        # تجاوز الأخطاء لمنع توقف البوت
        pass 

# =================================================================
#       4. الدالة الرئيسية وحلقة التشغيل (تم تعديلها)
# =================================================================

# دالة حلقة البوت للتشغيل في موضوع مستقل
def bot_thread_function():
    while True:
        if running:
            find_and_click_color()
        time.sleep(0.001)

# =================================================================
#       5. إعدادات الواجهة الرسومية (GUI)
# =================================================================

def login_attempt():
    global keyauthapp
    
    license_key = license_entry.get().strip()
    
    if not license_key:
        messagebox.showerror("خطأ", "الرجاء إدخال مفتاح الترخيص.")
        return

    # تشغيل عملية init في موضوع مستقل لتجنب تجميد الواجهة أثناء الاتصال بالخادم
    def authenticate():
        global keyauthapp
        try:
            print("جارٍ تهيئة نظام المصادقة...")
            keyauthapp = api(
                name = "modren",
                ownerid = "cDTYtZQlBX",
                version = "1.0",
                hash_to_check = getchecksum()
            )
            
            # التحقق من الترخيص
            success, message_or_username, subscription = keyauthapp.license(license_key)
            
            if success:
                # تحديث الواجهة بعد نجاح المصادقة
                root.after(0, lambda: show_bot_controls(message_or_username, subscription))
            else:
                root.after(0, lambda: messagebox.showerror("فشل المصادقة", message_or_username))

        except Exception as e:
            root.after(0, lambda: messagebox.showerror("خطأ في الاتصال", f"فشل الاتصال بالخادم: {e}"))

    # إخفاء نافذة المصادقة مؤقتاً والبدء في محاولة الاتصال
    login_frame.pack_forget()
    loading_label.pack(pady=20)
    
    auth_thread = threading.Thread(target=authenticate)
    auth_thread.daemon = True # سيتم إغلاق الموضوع عند إغلاق البرنامج
    auth_thread.start()

def show_bot_controls(username, subscription):
    loading_label.pack_forget() # إخفاء رسالة التحميل
    
    # 4.3. ربط مفتاح التشغيل (يجب أن يتم ربطه مرة واحدة)
    keyboard.on_press_key('1', lambda _: toggle_running_state_gui())

    # إعداد إطار التحكم بالبوت
    bot_frame = tk.Frame(root, padx=20, pady=20)
    bot_frame.pack(expand=True)
    
    # رسالة ترحيب
    welcome_msg = f"✅ تم التحقق بنجاح، مرحباً بك يا {username}!"
    tk.Label(bot_frame, text=welcome_msg, font=('Arial', 12, 'bold'), fg="darkgreen").pack(pady=10)
    
    # معلومات الاشتراك
    tk.Label(bot_frame, text=f"🔑 نوع الاشتراك: {subscription}", font=('Arial', 10)).pack(pady=5)
    
    # حالة البوت
    global status_label
    status_label = tk.Label(bot_frame, text="حالة البوت: 🔴 متوقف", font=('Arial', 14, 'bold'), fg="red")
    status_label.pack(pady=10)
    
    # زر التشغيل/الإيقاف
    global toggle_button
    toggle_button = tk.Button(
        bot_frame, 
        text="تشغيل البوت ▶️", 
        command=toggle_running_state_gui, 
        width=20, 
        height=2,
        bg="lightblue", 
        font=('Arial', 10, 'bold')
    )
    toggle_button.pack(pady=15)
    
    # تعليمات مفتاح '1'
    tk.Label(bot_frame, text="مفتاح '1' يعمل أيضًا للتشغيل/الإيقاف.", font=('Arial', 8, 'italic')).pack()
    
    # بدء حلقة البوت في موضوع منفصل
    bot_loop_thread = threading.Thread(target=bot_thread_function)
    bot_loop_thread.daemon = True 
    bot_loop_thread.start()
    
    # إعادة تسمية النافذة
    root.title(f"البوت - مرحباً {username}")


# إعداد النافذة الرئيسية
root = tk.Tk()
root.title("KeyAuth - مصادقة الترخيص")
#root.geometry("400x300")
root.resizable(False, False) # منع تغيير حجم النافذة

# إطار المصادقة
login_frame = tk.Frame(root, padx=20, pady=20)
login_frame.pack(expand=True)

tk.Label(login_frame, text="نظام مصادقة البوت 🤖", font=('Arial', 14, 'bold')).pack(pady=10)
tk.Label(login_frame, text="الرجاء إدخال مفتاح الترخيص:").pack(pady=5)

# حقل إدخال مفتاح الترخيص
license_entry = tk.Entry(login_frame, width=40, show="*") # show="*" لإخفاء المفتاح
license_entry.pack(pady=10, ipady=5)

# زر الدخول
login_button = tk.Button(login_frame, text="تسجيل الدخول", command=login_attempt, width=15, height=2)
login_button.pack(pady=15)

# مؤشر التحميل (يتم عرضه بعد محاولة تسجيل الدخول)
loading_label = tk.Label(root, text="جارٍ الاتصال والمصادقة... الرجاء الانتظار.", font=('Arial', 12), fg="blue")


if __name__ == '__main__':
    # تشغيل حلقة الواجهة الرسومية
    root.mainloop()
    
    # سيتم تشغيل هذه الجزئية عند إغلاق النافذة
    exiting()
