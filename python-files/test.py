import tkinter as tk
import subprocess
import webbrowser

# ---------- توابع دکمه‌ها ----------
def clear_ipv4():
    try:
        subprocess.run("ipconfig /release", shell=True)
        subprocess.run("ipconfig /renew", shell=True)
        tk.messagebox.showinfo("موفق", "IPv4 با موفقیت ریست شد ✅")
    except Exception as e:
        tk.messagebox.showerror("خطا", str(e))

def open_link():
    url = "https://panel.sheltertm.com/ip/72c8a5cb5f469da"
    webbrowser.open(url)

def set_dns():
    try:
        adapter = "Wi-Fi"  # اگر کارت شبکه‌ات اسم دیگه‌ای داره تغییر بده (Ethernet و ...)
        subprocess.run(f'netsh interface ip set dns name="{adapter}" static 78.157.34.244', shell=True)
        subprocess.run(f'netsh interface ip add dns name="{adapter}" 10.30.72.39 index=2', shell=True)
        tk.messagebox.showinfo("موفق", "DNS با موفقیت تنظیم شد ✅")
    except Exception as e:
        tk.messagebox.showerror("خطا", str(e))


# ---------- رابط گرافیکی ----------
root = tk.Tk()
root.title("IP Tool")
root.geometry("300x200")

from tkinter import messagebox

btn1 = tk.Button(root, text="Clear IPv4", command=clear_ipv4, width=20, height=2)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="Open Link", command=open_link, width=20, height=2)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="Set DNS", command=set_dns, width=20, height=2)
btn3.pack(pady=10)

root.mainloop()
