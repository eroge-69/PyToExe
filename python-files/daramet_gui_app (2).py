import tkinter as tk
from tkinter import simpledialog, messagebox
import webbrowser
import requests
import threading
import random

# اطلاعات پلن‌ها
plans = {
    "گنگ پلن 1": 150000,
    "گنگ پلن 2": 250000,
    "گنگ پلن 3": 350000,
    "گنگ پلن 4": 450000,
    "گنگ پلن 5": 550000
}

API_TOKEN = "90c4d9e98276ce90a7cf3b9f0fd9f8df6d271b902ac1d444ca670ffd6dd5946f"
USERNAME = "Wither_Official"

# پیام‌ها و رمزهای مربوط به پلن
plan_passwords = {}

# تابع تولید کد سه رقمی با جمع ۱۳
def generate_code_with_sum_13():
    while True:
        code = random.randint(100, 999)
        if sum(map(int, str(code))) == 13:
            return code

# چک کردن پرداخت با API و رمز عبور
def check_payment(plan, password, btn, label):
    def _check():
        btn.config(state="disabled")
        label.config(text="در حال بررسی پرداخت...")
        message = f"{plan} | رمز: {password}"
        try:
            res = requests.post(
                "https://daramet.com/api/v2/Donates/Search",
                headers={"Authorization": API_TOKEN},
                json={"term": message}
            )
            res.raise_for_status()
            data = res.json()
            if data:
                code = generate_code_with_sum_13()
                label.config(
                    text=f"سفارش شما تایید شد\nکد پشتیبانی: {code}\nاین کد را فقط به پشتیبانی دهید"
                )
            else:
                label.config(text="پرداختی با این پیام یافت نشد. لطفا مجدد تلاش کنید.")
        except Exception:
            label.config(text="خطا در ارتباط با سرور. دوباره امتحان کنید.")
        finally:
            btn.config(state="normal")

    threading.Thread(target=_check).start()

# باز کردن لینک پرداخت در مرورگر با رمز
def open_payment(plan, label):
    password = simpledialog.askstring("رمز عبور", "لطفا یک رمز عبور وارد کنید (اگر آسان باشد ممکن است مشکل ایجاد شود):")
    if not password:
        return
    message = f"{plan} | رمز: {password}"
    plan_passwords[plan] = password
    amount = plans[plan]
    url = f"https://daramet.com/{USERNAME}?webintent&donate={amount}&message={message}"
    webbrowser.open(url)
    selected_plan.set(plan)
    label.config(text="پس از پرداخت، روی 'پرداخت کردم' کلیک کنید.")

# ساخت GUI
root = tk.Tk()
root.title("پرداخت دارمت - Wither")
root.geometry("500x500")
root.configure(bg="#1e1e1e")

font_title = ("B Nazanin", 16, "bold")
font_text = ("B Nazanin", 14)

tk.Label(root, text="انتخاب پلن پرداخت", bg="#1e1e1e", fg="white", font=font_title).pack(pady=10)

selected_plan = tk.StringVar()

for plan in plans:
    def make_cmd(p=plan):
        return lambda: open_payment(p, status_label)
    tk.Button(root, text=plan, font=font_text, bg="#3a3a3a", fg="white", width=30, command=make_cmd()).pack(pady=5)

status_label = tk.Label(root, text="", bg="#1e1e1e", fg="lightgreen", font=font_text)
status_label.pack(pady=20)

def on_payment():
    plan = selected_plan.get()
    if not plan:
        status_label.config(text="ابتدا یک پلن را انتخاب و پرداخت کنید.")
        return
    password = simpledialog.askstring("بررسی پرداخت", "رمز عبوری که هنگام پرداخت وارد کردید را مجددا وارد کنید:")
    if not password:
        return
    check_payment(plan, password, check_btn, status_label)

check_btn = tk.Button(root, text="پرداخت کردم ✅", font=font_text, bg="#007700", fg="white", width=20, command=on_payment)
check_btn.pack(pady=10)

root.mainloop()
