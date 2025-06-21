import tkinter as tk
from tkinter import messagebox
import random
import string
import tempfile
import os

def generate_strong_password_from_username(numeric_username):
    if len(numeric_username) < 4:
        return None

    suffix = numeric_username[-4:]  # 4 رقم آخر عدد

    # کاراکترهای پیشوند: یکی از هر نوع
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    symbol = random.choice("!@#$%^&*")

    # ترکیب اولیه (4 کاراکتر)
    prefix_chars = [upper, lower, digit, symbol]
    random.shuffle(prefix_chars)

    prefix = ''.join(prefix_chars)
    return prefix + suffix


def generate():
    numeric_username = entry.get()
    if not numeric_username.isdigit():
        messagebox.showerror("❌ خطا", "فقط عدد وارد کن.")
        return
    if len(numeric_username) < 4:
        messagebox.showerror("❌ خطا", "حداقل 4 رقم لازم است.")
        return

    new_username = "usr_" + numeric_username
    new_password = generate_strong_password_from_username(numeric_username)

    username_var.set(new_username)
    password_var.set(new_password)
    messagebox.showinfo("✅ موفق", "اطلاعات ساخته شد.")

def copy_to_clipboard(text):
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("📋 کپی شد", "در کلیپ‌بورد ذخیره شد.")

def print_credentials():
    uname = username_var.get()
    pword = password_var.get()

    if not uname or not pword:
        messagebox.showwarning("⚠️ هشدار", "اطلاعات کامل نیست.")
        return

    content = "نام کاربری: {}\nپسورد: {}".format(uname, pword)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as f:
        f.write(content)
        try:
            os.startfile(f.name, "print")
        except Exception as e:
            messagebox.showerror("❌ خطا", "چاپ انجام نشد:\n{}".format(e))

# رابط گرافیکی
root = tk.Tk()
root.title("🧩 تولید نام کاربری و پسورد همراه بانک")
root.geometry("400x450")
root.configure(bg="#f2f2f2")
root.resizable(False, False)

font_label = ("Arial", 11)
font_entry = ("Consolas", 12)
button_style = {"font": ("Arial", 11, "bold"), "bg": "#3A7FF6", "fg": "white",
                "activebackground": "#2a5fd0", "relief": "flat", "bd": 0}

# عنوان
tk.Label(root, text="نام کاربری عددی:", font=font_label, bg="#f2f2f2").pack(pady=(20, 5))

# فیلد ورودی
entry = tk.Entry(root, font=font_entry, justify='center', width=25, bg="white", bd=0,
                 relief="flat", highlightthickness=1, highlightbackground="#ccc",
                 highlightcolor="#3A7FF6")
entry.pack(pady=5, ipady=6)

# دکمه تولید
btn = tk.Button(root, text=" تولید", command=generate, **button_style)
btn.pack(pady=15, ipadx=10, ipady=5)

# خروجی نام کاربری
username_var = tk.StringVar()
tk.Label(root, text="نام کاربری جدید:", font=font_label, bg="#f2f2f2").pack()
tk.Entry(root, textvariable=username_var, font=font_entry, state='readonly',
         justify='center', width=30, bg="#e6f0ff", bd=0, relief="flat").pack(ipady=5)

tk.Button(root, text=" کپی نام کاربری",
          command=lambda: copy_to_clipboard(username_var.get()),
          bg="#007ACC", fg="white", bd=0, relief="flat", font=("Arial", 10)).pack(pady=5, ipadx=6, ipady=4)

# خروجی پسورد
password_var = tk.StringVar()
tk.Label(root, text="پسورد جدید:", font=font_label, bg="#f2f2f2").pack()
tk.Entry(root, textvariable=password_var, font=font_entry, state='readonly',
         justify='center', width=30, bg="#e6ffe6", bd=0, relief="flat").pack(ipady=5)

tk.Button(root, text=" کپی پسورد",
          command=lambda: copy_to_clipboard(password_var.get()),
          bg="#28A745", fg="white", bd=0, relief="flat", font=("Arial", 10)).pack(pady=5, ipadx=6, ipady=4)

# دکمه پرینت
tk.Button(root, text="🖨️ چاپ اطلاعات", command=print_credentials,
          bg="#FF9800", fg="white", font=("Arial", 11, "bold"),
          bd=0, relief="flat").pack(pady=15, ipadx=8, ipady=5)

root.mainloop()
