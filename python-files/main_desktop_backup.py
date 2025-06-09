
import tkinter as tk
from tkinter import messagebox
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# بيانات البريد
SENDER_EMAIL = "Boukersiwalid08@gmail.com"
SENDER_PASSWORD = "yqyd jhah shkh qpwe"

# بيانات السيارات
cars = [
    {
        "name": "سيارة مرسيدس",
        "insurance_date": "2025-06-11",
        "tax_date": "2025-06-13",
        "recipient": "YAHIABEN03@gmail.com"
    },
    {
        "name": "سيارة تويوتا",
        "insurance_date": "2025-06-15",
        "tax_date": "2025-06-18",
        "recipient": "test@example.com"
    }
]

def send_email(to_email, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("فشل في الإرسال:", e)
        return False

def notify_expiring():
    today = datetime.date.today()
    count = 0
    for car in cars:
        insurance_date = datetime.datetime.strptime(car["insurance_date"], "%Y-%m-%d").date()
        tax_date = datetime.datetime.strptime(car["tax_date"], "%Y-%m-%d").date()

        send_alert = False
        body = f"🚗 السيارة: {car['name']}

"

        if (insurance_date - today).days <= 3:
            body += f"📅 تنبيه: التأمين ينتهي بتاريخ {car['insurance_date']}
"
            send_alert = True
        if (tax_date - today).days <= 3:
            body += f"📅 تنبيه: الضريبة تنتهي بتاريخ {car['tax_date']}
"
            send_alert = True

        if send_alert:
            subject = f"تنبيه بخصوص {car['name']}"
            if send_email(car["recipient"], subject, body):
                count += 1

    messagebox.showinfo("نتيجة الإرسال", f"📬 تم إرسال {count} تنبيه/تنبيهات.")

root = tk.Tk()
root.title("تنبيهات السيارات")
root.geometry("500x300")
root.configure(bg="#f9f9f9")

tk.Label(root, text="نظام تنبيه نهاية التأمين والضريبة", font=("Arial", 14, "bold"), bg="#f9f9f9").pack(pady=20)

tk.Button(root, text="📢 إرسال التنبيهات التلقائية", command=notify_expiring, bg="green", fg="white", width=40, height=2).pack(pady=30)

root.mainloop()
