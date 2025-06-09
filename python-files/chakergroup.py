
import tkinter as tk
from tkinter import messagebox
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# بيانات البريد
SENDER_EMAIL = "Boukersiwalid08@gmail.com"
SENDER_PASSWORD = "yqyd jhah shkh qpwe"

# بيانات السيارات كمثال (يمكن لاحقاً ربطها بقاعدة بيانات أو ملف)
cars = [
    {"name": "سيارة 1", "insurance_date": "2025-06-12", "tax_date": "2025-06-14", "recipient": "YAHIABEN03@gmail.com"},
    {"name": "سيارة 2", "insurance_date": "2025-06-10", "tax_date": "2025-06-25", "recipient": "someone@example.com"},
]

# إرسال بريد إلكتروني
def send_email(recipient, subject, message):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print("خطأ في إرسال البريد:", e)
        return False

# زر إرسال التنبيهات التلقائية (للتأمين والضريبة)
def notify_expiring():
    today = datetime.date.today()
    notified = 0
    for car in cars:
        insurance_end = datetime.datetime.strptime(car["insurance_date"], "%Y-%m-%d").date()
        tax_end = datetime.datetime.strptime(car["tax_date"], "%Y-%m-%d").date()

        if (insurance_end - today).days <= 3 or (tax_end - today).days <= 3:
            subject = f"تنبيه بخصوص السيارة: {car['name']}"
            message = f"تنبيه: تقترب نهاية صلاحية:
"
            if (insurance_end - today).days <= 3:
                message += f"- التأمين: {car['insurance_date']}
"
            if (tax_end - today).days <= 3:
                message += f"- الضريبة: {car['tax_date']}
"
            if send_email(car['recipient'], subject, message):
                notified += 1

    messagebox.showinfo("تم", f"تم إرسال {notified} تنبيه/تنبيهات.")

# إرسال إشعار مخصص إلى إيميل معين
def send_custom_notification():
    recipient = entry_email.get().strip()
    msg = entry_message.get("1.0", tk.END).strip()
    if recipient and msg:
        success = send_email(recipient, "إشعار مخصص", msg)
        if success:
            messagebox.showinfo("تم", "تم إرسال الإشعار بنجاح.")
        else:
            messagebox.showerror("فشل", "فشل في إرسال الإيميل.")
    else:
        messagebox.showwarning("تنبيه", "يرجى إدخال البريد والرسالة.")

# واجهة المستخدم
root = tk.Tk()
root.title("متابعة تأمين وضريبة السيارات")
root.geometry("500x400")
root.configure(bg="#f2f2f2")

label_title = tk.Label(root, text="تنبيهات السيارات", font=("Arial", 16), bg="#f2f2f2")
label_title.pack(pady=10)

btn_notify = tk.Button(root, text="إرسال التنبيهات التلقائية", command=notify_expiring, bg="green", fg="white", width=40)
btn_notify.pack(pady=10)

# قسم الإشعار المخصص
label_email = tk.Label(root, text="أدخل البريد الإلكتروني:", bg="#f2f2f2")
label_email.pack()
entry_email = tk.Entry(root, width=50)
entry_email.pack(pady=5)

label_message = tk.Label(root, text="أدخل الرسالة:", bg="#f2f2f2")
label_message.pack()
entry_message = tk.Text(root, height=5, width=50)
entry_message.pack(pady=5)

btn_custom = tk.Button(root, text="إرسال إشعار مخصص", command=send_custom_notification, bg="#007acc", fg="white", width=40)
btn_custom.pack(pady=10)

root.mainloop()
