import tkinter as tk
from tkinter import messagebox, filedialog
import os

# --- توابع ساخت پروژه‌ها ---
def build_telegram_bot():
    folder = filedialog.askdirectory(title="محل ذخیره ربات تلگرام")
    if folder:
        file_path = os.path.join(folder, "telegram_bot.py")
        code = '''# نمونه ربات تلگرام ساده
print("ربات تلگرام شما آماده است!")'''
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        messagebox.showinfo("نتیجه", f"✅ ربات تلگرام ساخته شد!\n{file_path}")

def build_android_app():
    folder = filedialog.askdirectory(title="محل ذخیره اپ اندروید")
    if folder:
        file_path = os.path.join(folder, "android_app.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("🚧 این قابلیت به زودی اضافه می‌شود")
        messagebox.showinfo("نتیجه", f"⚠️ اپلیکیشن اندروید نمونه ساخته شد\n{file_path}")

def build_desktop_app():
    folder = filedialog.askdirectory(title="محل ذخیره نرم افزار دسکتاپ")
    if folder:
        file_path = os.path.join(folder, "desktop_app.py")
        code = '''# نمونه نرم افزار دسکتاپ ساده
print("نرم افزار دسکتاپ شما آماده است!")'''
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)
        messagebox.showinfo("نتیجه", f"✅ نرم افزار دسکتاپ ساخته شد!\n{file_path}")

# --- رابط گرافیکی ---
root = tk.Tk()
root.title("BotBuilderX - نسخه حرفه‌ای")
root.geometry("450x350")
root.resizable(False, False)

label = tk.Label(root, text="یک گزینه برای ساخت انتخاب کنید:", font=("Tahoma", 13))
label.pack(pady=20)

btn1 = tk.Button(root, text="ساخت ربات تلگرام", command=build_telegram_bot, width=30)
btn1.pack(pady=10)

btn2 = tk.Button(root, text="ساخت اپلیکیشن اندروید", command=build_android_app, width=30)
btn2.pack(pady=10)

btn3 = tk.Button(root, text="ساخت نرم افزار دسکتاپ", command=build_desktop_app, width=30)
btn3.pack(pady=10)

root.mainloop()
