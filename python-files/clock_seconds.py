import customtkinter as ctk
import subprocess

def enable_seconds():
    subprocess.run(r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowSecondsInSystemClock /t REG_DWORD /d 1 /f', shell=True)
    restart_explorer()

def disable_seconds():
    subprocess.run(r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v ShowSecondsInSystemClock /t REG_DWORD /d 0 /f', shell=True)
    restart_explorer()

def restart_explorer():
    subprocess.run("taskkill /f /im explorer.exe", shell=True)
    subprocess.run("start explorer.exe", shell=True)

# إعداد الواجهة
ctk.set_appearance_mode("dark")   # "dark" أو "light"
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("إدارة الثواني في ساعة ويندوز 10")
root.geometry("400x300")

label = ctk.CTkLabel(root, text="اختر العملية:", font=("Arial", 16))
label.pack(pady=20)

btn1 = ctk.CTkButton(root, text="✅ تفعيل إظهار الثواني", command=enable_seconds, width=250, height=40, fg_color="green")
btn1.pack(pady=10)

btn2 = ctk.CTkButton(root, text="❌ إلغاء إظهار الثواني", command=disable_seconds, width=250, height=40, fg_color="red")
btn2.pack(pady=10)

btn3 = ctk.CTkButton(root, text="🚪 خروج", command=root.quit, width=250, height=40)
btn3.pack(pady=10)

root.mainloop()
