
import tkinter as tk
from tkinter import messagebox
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# بيانات البريد
SENDER_EMAIL = "Boukersiwalid08@gmail.com"
SENDER_PASSWORD = "yqyd jhah shkh qpwe"

# بيانات السيارات (يمكن تعديلها مستقبلاً لقراءة من قاعدة بيانات)
cars = [
    {
        "name": "سيارة تويوتا",
        "insurance_date": "2025-06-12",
        "tax_date": "2025-06-15",
        "recipient": "YAHIABEN03@gmail.com"
    },
    {
        "name": "سيارة هيونداي",
        "insurance_date": "2025-06-10",
        "tax_date": "2025-06-25",
        "recipient": "test@example.com"
    }
]

# إرسال البريد الإلكتروني
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
        print("فشل في إرسال البريد:", e)
        return False

# إرسال التنبيهات للسيارات التي تنتهي خلال 3 أيام
def notify_expiring():
    today = datetime.date.today()
    count = 0
    for car in cars:
        ins_date = datetime.datetime.strptime(car["insurance_date"], "%Y-%m-%d").date()
        tax_date = datetime.datetime.strptime(car["tax_date"], "%Y-%m-%d").date()

        send_flag = False
        msg = f"تنبيه بخصوص السيارة: {car['name']}

"
        if (ins_date - today).days <= 3:
            msg += f"- ينتهي التأمين في: {car['insurance_date']}
"
            send_flag = True
        if (tax_date - today).days <= 3:
            msg += f"- تنتهي الضريبة في: {car['tax_date']}
"
            send_flag = True

        if send_flag:
            subject = f"تنبيه بخصوص السيارة {car['name']}"
            if send_email(car["recipient"], subject, msg):
                count += 1

    messagebox.showinfo("النتيجة", f"تم إرسال {count} تنبيه/تنبيهات.")

# إرسال إشعار مخصص
def send_custom_notification():
    email = entry_email.get().strip()
    message = text_message.get("1.0", tk.END).strip()

    if not email or not message:
        messagebox.showwarning("تنبيه", "يرجى إدخال البريد والرسالة.")
        return

    if send_email(email, "إشعار مخصص", message):
        messagebox.showinfo("نجاح", "تم إرسال الإشعار بنجاح.")
    else:
        messagebox.showerror("خطأ", "فشل في إرسال الإشعار.")

# إنشاء واجهة المستخدم
root = tk.Tk()
root.title("متابعة تأمين وضريبة السيارات")
root.geometry("500x500")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

title = tk.Label(root, text="📋 نظام تنبيهات السيارات", font=("Arial", 16, "bold"), bg="#f0f0f0")
title.pack(pady=10)

btn_notify = tk.Button(root, text="🚗 إرسال التنبيهات التلقائية", command=notify_expiring, bg="#28a745", fg="white", width=40, height=2)
btn_notify.pack(pady=10)

separator = tk.Label(root, text="إرسال إشعار مخصص", font=("Arial", 14), bg="#f0f0f0")
separator.pack(pady=10)

lbl_email = tk.Label(root, text="📧 البريد الإلكتروني:", bg="#f0f0f0")
lbl_email.pack()
entry_email = tk.Entry(root, width=50)
entry_email.pack(pady=5)

lbl_msg = tk.Label(root, text="✉️ الرسالة:", bg="#f0f0f0")
lbl_msg.pack()
text_message = tk.Text(root, height=6, width=50)
text_message.pack(pady=5)

btn_custom = tk.Button(root, text="📨 إرسال الإشعار", command=send_custom_notification, bg="#007bff", fg="white", width=40, height=2)
btn_custom.pack(pady=10)

root.mainloop()
