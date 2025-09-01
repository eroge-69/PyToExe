import tkinter as tk
from tkinter import messagebox
import psutil
import platform
import threading
import time
import socket
import os
import subprocess

# ==================== توابع دکمه‌ها ====================
def بررسی_رم():
    ram = psutil.virtual_memory()
    messagebox.showinfo("اطلاعات رم", f"کل رم: {ram.total / (1024**3):.2f} گیگابایت\nرم آزاد: {ram.available / (1024**3):.2f} گیگابایت")

def بررسی_سی_پی_یو():
    cpu_percent = psutil.cpu_percent(interval=1)
    messagebox.showinfo("اطلاعات CPU", f"استفاده CPU: {cpu_percent}%\nتعداد هسته‌ها: {psutil.cpu_count(logical=False)}\nCPU مجازی: {psutil.cpu_count(logical=True)}")

def بررسی_هارد():
    disk = psutil.disk_usage('/')
    messagebox.showinfo("اطلاعات هارد", f"کل فضا: {disk.total / (1024**3):.2f} گیگابایت\nاستفاده شده: {disk.used / (1024**3):.2f} گیگابایت\nآزاد: {disk.free / (1024**3):.2f} گیگابایت")

def اطلاعات_سیستم():
    info = platform.uname()
    messagebox.showinfo("اطلاعات سیستم", f"سیستم عامل: {info.system}\nنام دستگاه: {info.node}\nنسخه: {info.release}\nنسخه کامل: {info.version}\nنوع دستگاه: {info.machine}\nپردازنده: {info.processor}")

def آی_پی_و_شبکه():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    net_io = psutil.net_io_counters()
    messagebox.showinfo("شبکه", f"نام دستگاه: {hostname}\nآی‌پی: {ip_address}\nارسال: {net_io.bytes_sent / (1024**2):.2f} MB\nدریافت: {net_io.bytes_recv / (1024**2):.2f} MB")

def باتری():
    battery = psutil.sensors_battery()
    if battery:
        messagebox.showinfo("باتری", f"درصد شارژ: {battery.percent}%\nشارژر متصل: {battery.power_plugged}")
    else:
        messagebox.showinfo("باتری", "باتری یافت نشد")

def دمای_سیستم():
    temps = psutil.sensors_temperatures()
    result = ""
    if temps:
        for name, entries in temps.items():
            for entry in entries:
                result += f"{name} - {entry.label}: {entry.current}°C\n"
    else:
        result = "اطلاعات دما در دسترس نیست"
    messagebox.showinfo("دمای سیستم", result)

def پردازه‌ها():
    procs = psutil.pids()[:10]
    result = ""
    for pid in procs:
        try:
            p = psutil.Process(pid)
            result += f"شناسه PID: {pid} | نام: {p.name()}\n"
        except:
            continue
    messagebox.showinfo("پردازه‌ها", result)

def آنتی_ویروس():
    try:
        if platform.system() == "Windows":
            output = subprocess.check_output("wmic /namespace:\\\\root\\SecurityCenter2 path AntivirusProduct get displayName", shell=True)
            result = output.decode()
        else:
            result = "اطلاعات آنتی‌ویروس در این سیستم عامل پشتیبانی نمی‌شود"
    except:
        result = "قابل دریافت نیست"
    messagebox.showinfo("آنتی‌ویروس", result)

# ==================== انیمیشن متن ====================
def انیمیشن_متن():
    text = "مدیریت سیستم - نسخه حرفه‌ای"
    while True:
        for i in range(len(text)+1):
            anim_label.config(text=text[:i])
            time.sleep(0.05)
        time.sleep(0.5)
        for i in range(len(text), -1, -1):
            anim_label.config(text=text[:i])
            time.sleep(0.03)

# ==================== پنجره اصلی ====================
root = tk.Tk()
root.title("مدیریت سیستم")
root.geometry("900x750")
root.configure(bg="#1c1c1c")

anim_label = tk.Label(root, text="", font=("B Nazanin", 18, "bold"), fg="lime", bg="#1c1c1c")
anim_label.pack(pady=20)
threading.Thread(target=انیمیشن_متن, daemon=True).start()

# فریم‌ها
frame_hardware = tk.LabelFrame(root, text="سخت‌افزار و سیستم", padx=10, pady=10, bg="#2c2c2c", fg="white", font=("B Nazanin", 12, "bold"))
frame_hardware.pack(padx=10, pady=10, fill="both")

frame_network = tk.LabelFrame(root, text="شبکه", padx=10, pady=10, bg="#2c2c2c", fg="white", font=("B Nazanin", 12, "bold"))
frame_network.pack(padx=10, pady=10, fill="both")

frame_tools = tk.LabelFrame(root, text="ابزارها", padx=10, pady=10, bg="#2c2c2c", fg="white", font=("B Nazanin", 12, "bold"))
frame_tools.pack(padx=10, pady=10, fill="both")

# ==================== لیست دکمه‌ها ====================
buttons = [
    (frame_hardware, "بررسی رم", بررسی_رم),
    (frame_hardware, "بررسی CPU", بررسی_سی_پی_یو),
    (frame_hardware, "بررسی هارد", بررسی_هارد),
    (frame_hardware, "اطلاعات سیستم", اطلاعات_سیستم),
    (frame_hardware, "دمای سیستم", دمای_سیستم),
    (frame_hardware, "باتری", باتری),
    (frame_network, "IP و شبکه", آی_پی_و_شبکه),
    (frame_tools, "پردازه‌ها", پردازه‌ها),
    (frame_tools, "آنتی‌ویروس", آنتی_ویروس),
]

# ساخت ۵۰ دکمه واقعی با عملکرد مشابه برای نمونه و فارسی
for i in range(50):
    frame, text, cmd = buttons[i % len(buttons)]
    tk.Button(frame, text=f"{text} {i+1}", command=cmd, width=22, height=2, bg="#4d4d4d", fg="white", font=("B Nazanin", 10)).pack(padx=5, pady=3, side="left")

root.mainloop()
