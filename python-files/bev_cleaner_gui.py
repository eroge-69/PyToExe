import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import ctypes

# كلمة المرور
PASSWORD = "BEV-FREE"

# تنظيف شامل لبصمات فورتنايت (بشكل غير مدمر)
def start_cleaning():
    msg_label.config(text="Cleaning in progress...", fg="orange")
    root.update()

    try:
        # حذف Temp
        subprocess.call("del /s /f /q %temp%\\*", shell=True)

        # حذف Prefetch
        subprocess.call("del /s /f /q C:\\Windows\\Prefetch\\*", shell=True)

        # حذف Epic/Fortnite AppData/ProgramData Logs
        paths = [
            os.getenv("LOCALAPPDATA") + r"\\FortniteGame",
            os.getenv("LOCALAPPDATA") + r"\\EpicGamesLauncher",
            os.getenv("APPDATA") + r"\\Epic",
            r"C:\\ProgramData\\Epic",
        ]
        for path in paths:
            subprocess.call(f"rmdir /s /q \"{path}\"", shell=True)

        # تعطيل خدمة DiagTrack
        subprocess.call("sc stop DiagTrack", shell=True)
        subprocess.call("sc config DiagTrack start= disabled", shell=True)

        # تنظيف WMI Cache
        subprocess.call("winmgmt /verifyrepository", shell=True)
        subprocess.call("winmgmt /salvagerepository", shell=True)

        # حذف سجلات Event Viewer (اختياري)
        subprocess.call("wevtutil cl System", shell=True)
        subprocess.call("wevtutil cl Application", shell=True)

        msg_label.config(text="Cleaning completed! Restarting your PC...", fg="green")
        root.update()
        ctypes.windll.user32.MessageBoxW(0, "Thanks for using Bev Cleaner\nYour PC will restart now", "Goodbye!", 0)
        os.system("shutdown /r /t 5")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# التحقق من كلمة المرور
def check_password():
    if password_entry.get() == PASSWORD:
        password_frame.pack_forget()
        main_frame.pack(pady=40)
    else:
        messagebox.showerror("Access Denied", "Incorrect password!")

# نافذة GUI
root = tk.Tk()
root.title("Bev Cleaner PRO")
root.geometry("400x250")
root.configure(bg="#1a1a1a")
root.resizable(False, False)

# ستايل
font = ("Segoe UI", 11)
root.option_add("*Font", font)

# كلمة المرور
password_frame = tk.Frame(root, bg="#1a1a1a")
tk.Label(password_frame, text="Enter Password:", bg="#1a1a1a", fg="white").pack(pady=10)
password_entry = tk.Entry(password_frame, show="*", width=25)
password_entry.pack()
tk.Button(password_frame, text="Unlock", command=check_password).pack(pady=10)
password_frame.pack(pady=50)

# محتوى الواجهة الرئيسية
main_frame = tk.Frame(root, bg="#1a1a1a")
tk.Label(main_frame, text="Bev Cleaner PRO", font=("Segoe UI", 16), bg="#1a1a1a", fg="#a66cff").pack(pady=10)
tk.Button(main_frame, text="Start Cleaning", command=start_cleaning, bg="#a66cff", fg="white", width=20).pack(pady=10)
msg_label = tk.Label(main_frame, text="", bg="#1a1a1a", fg="white")
msg_label.pack()

root.mainloop()
