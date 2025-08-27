import tkinter as tk
from tkinter import messagebox
import sqlite3
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from twilio.rest import Client
import threading
import time

# ================== Twilio Config ==================
TWILIO_SID = "your_account_sid"
TWILIO_AUTH = "your_auth_token"
TWILIO_PHONE = "+123456789"

# ================== Database ==================
def init_db():
    conn = sqlite3.connect("cars.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS cars (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 car_name TEXT,
                 plate TEXT,
                 email TEXT,
                 phone TEXT,
                 start_date TEXT,
                 end_date TEXT
                 )""")
    conn.commit()
    conn.close()

def is_first_run():
    conn = sqlite3.connect("cars.db")
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cars")
    count = c.fetchone()[0]
    conn.close()
    return count == 0

# ================== Email ==================
def send_email(receiver_email, subject, body):
    sender_email = "yourmail@gmail.com"
    sender_pass = "yourpassword"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_pass)
            server.send_message(msg)
    except Exception as e:
        print("Email Error:", e)

# ================== SMS ==================
def send_sms(phone, body):
    try:
        client = Client(TWILIO_SID, TWILIO_AUTH)
        client.messages.create(
            body=body,
            from_=TWILIO_PHONE,
            to=phone
        )
    except Exception as e:
        print("SMS Error:", e)

# ================== Add Car ==================
def add_car():
    car_name = entry_name.get()
    plate = entry_plate.get()
    email = entry_email.get()
    phone = entry_phone.get()
    start_date = entry_start.get()
    end_date = entry_end.get()

    if not (car_name and plate and email and phone and start_date and end_date):
        messagebox.showwarning("خطأ", "من فضلك املأ جميع البيانات")
        return

    conn = sqlite3.connect("cars.db")
    c = conn.cursor()
    c.execute("INSERT INTO cars (car_name, plate, email, phone, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
              (car_name, plate, email, phone, start_date, end_date))
    conn.commit()
    conn.close()
    messagebox.showinfo("تم", "تم تسجيل البيانات بنجاح!")

# ================== Check Expiry ==================
def check_expiry():
    conn = sqlite3.connect("cars.db")
    c = conn.cursor()
    c.execute("SELECT * FROM cars")
    rows = c.fetchall()
    conn.close()

    today = datetime.now().date()

    for row in rows:
        car_id, car_name, plate, email, phone, start_date, end_date = row
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        days_left = (end_date_obj - today).days

        if days_left <= 10 and days_left >= 0:
            if days_left <= 2:
                alert = f"⚠️ الرخصة للعربية {car_name} ({plate}) هتنتهي بعد {days_left} يوم!"
                messagebox.showerror("تنبيه خطير!", alert)
            else:
                alert = f"تنبيه: الرخصة للعربية {car_name} ({plate}) هتنتهي بعد {days_left} يوم."
                messagebox.showwarning("تنبيه", alert)

            send_email(email, "تنبيه انتهاء رخصة", alert)
            send_sms(phone, alert)

        elif days_left < 0:
            alert = f"❌ الرخصة للعربية {car_name} ({plate}) انتهت يوم {end_date}"
            messagebox.showerror("انتهت الرخصة", alert)
            send_email(email, "انتهت الرخصة", alert)
            send_sms(phone, alert)

# ================== Renew License ==================
def renew_license():
    plate = entry_plate.get()
    new_end = entry_end.get()

    if not (plate and new_end):
        messagebox.showwarning("خطأ", "ادخل رقم اللوحة والتاريخ الجديد للتجديد")
        return

    conn = sqlite3.connect("cars.db")
    c = conn.cursor()
    c.execute("UPDATE cars SET end_date=? WHERE plate=?", (new_end, plate))
    conn.commit()
    conn.close()
    messagebox.showinfo("تم", f"تم تجديد رخصة العربية {plate} لغاية {new_end}")

# ================== Background Checker ==================
def background_checker():
    while True:
        today = datetime.now().date()
        sleep_time = 86400  # الافتراضي: يوم كامل

        conn = sqlite3.connect("cars.db")
        c = conn.cursor()
        c.execute("SELECT end_date FROM cars")
        rows = c.fetchall()
        conn.close()

        for row in rows:
            end_date = datetime.strptime(row[0], "%Y-%m-%d").date()
            days_left = (end_date - today).days

            if 0 <= days_left <= 2:
                sleep_time = 3600   # كل ساعة
            elif 3 <= days_left <= 10:
                sleep_time = 10800  # كل 3 ساعات

        check_expiry()
        time.sleep(sleep_time)

# ================== GUI ==================
root = tk.Tk()
root.title("برنامج متابعة رخص السيارات")

tk.Label(root, text="اسم العربية:").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="رقم اللوحة:").grid(row=1, column=0)
entry_plate = tk.Entry(root)
entry_plate.grid(row=1, column=1)

tk.Label(root, text="البريد الإلكتروني:").grid(row=2, column=0)
entry_email = tk.Entry(root)
entry_email.grid(row=2, column=1)

tk.Label(root, text="رقم التليفون:").grid(row=3, column=0)
entry_phone = tk.Entry(root)
entry_phone.grid(row=3, column=1)

tk.Label(root, text="تاريخ البداية (YYYY-MM-DD):").grid(row=4, column=0)
entry_start = tk.Entry(root)
entry_start.grid(row=4, column=1)

tk.Label(root, text="تاريخ النهاية (YYYY-MM-DD):").grid(row=5, column=0)
entry_end = tk.Entry(root)
entry_end.grid(row=5, column=1)

btn_add = tk.Button(root, text="حفظ البيانات", command=add_car)
btn_add.grid(row=6, column=0, pady=5)

btn_check = tk.Button(root, text="فحص الرخص", command=check_expiry)
btn_check.grid(row=6, column=1, pady=5)

btn_renew = tk.Button(root, text="تجديد الرخصة", command=renew_license)
btn_renew.grid(row=7, column=0, columnspan=2, pady=10)

init_db()

# شغل الثريد اللي بيشيك في الخلفية
thread = threading.Thread(target=background_checker, daemon=True)
thread.start()

root.mainloop()
