
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

DB_FILE = 'cars.db'
SETTINGS_FILE = 'settings.txt'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        type TEXT,
        insurance_end TEXT,
        tax_end TEXT,
        email TEXT
    )''')
    conn.commit()
    conn.close()

def load_settings():
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            lines = f.read().splitlines()
            return {
                'sender_email': lines[0],
                'sender_password': lines[1],
                'smtp_server': lines[2],
                'smtp_port': int(lines[3])
            }
    except:
        return {'sender_email': '', 'sender_password': '', 'smtp_server': '', 'smtp_port': 587}

def save_settings(s):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        f.write(f"{s['sender_email']}\n{s['sender_password']}\n{s['smtp_server']}\n{s['smtp_port']}")

def send_notification(car, settings, subject, msg):
    try:
        message = MIMEText(msg)
        message['Subject'] = subject
        message['From'] = settings['sender_email']
        message['To'] = car['email']

        with smtplib.SMTP(settings['smtp_server'], settings['smtp_port']) as server:
            server.starttls()
            server.login(settings['sender_email'], settings['sender_password'])
            server.sendmail(settings['sender_email'], [car['email']], message.as_string())
    except Exception as e:
        print(f"فشل في إرسال الإيميل إلى {car['email']}: {e}")

def check_and_notify():
    settings = load_settings()
    if not settings['sender_email']:
        messagebox.showerror("خطأ", "يرجى ضبط إعدادات البريد أولاً")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    today = datetime.today().date()
    c.execute("SELECT * FROM cars")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        car = {
            'id': row[0],
            'number': row[1],
            'type': row[2],
            'insurance_end': datetime.strptime(row[3], "%Y-%m-%d").date(),
            'tax_end': datetime.strptime(row[4], "%Y-%m-%d").date(),
            'email': row[5]
        }

        if (car['insurance_end'] - today).days == 3:
            msg = f"تنبيه: تأمين السيارة رقم {car['number']} ينتهي بتاريخ {car['insurance_end']}."
            send_notification(car, settings, "تنبيه بانتهاء تأمين", msg)

        if (car['tax_end'] - today).days == 3:
            msg = f"تنبيه: ضريبة السيارة رقم {car['number']} تنتهي بتاريخ {car['tax_end']}."
            send_notification(car, settings, "تنبيه بانتهاء الضريبة", msg)

def open_settings_window():
    win = tk.Toplevel()
    win.title("إعدادات البريد")

    tk.Label(win, text="بريد المرسل:").grid(row=0, column=0, sticky="e")
    tk.Label(win, text="كلمة المرور:").grid(row=1, column=0, sticky="e")
    tk.Label(win, text="SMTP Server:").grid(row=2, column=0, sticky="e")
    tk.Label(win, text="SMTP Port:").grid(row=3, column=0, sticky="e")

    sender_email = tk.Entry(win, width=30)
    sender_password = tk.Entry(win, show="*", width=30)
    smtp_server = tk.Entry(win, width=30)
    smtp_port = tk.Entry(win, width=30)

    settings = load_settings()
    sender_email.insert(0, settings['sender_email'])
    sender_password.insert(0, settings['sender_password'])
    smtp_server.insert(0, settings['smtp_server'])
    smtp_port.insert(0, str(settings['smtp_port']))

    sender_email.grid(row=0, column=1)
    sender_password.grid(row=1, column=1)
    smtp_server.grid(row=2, column=1)
    smtp_port.grid(row=3, column=1)

    def save():
        save_settings({
            'sender_email': sender_email.get(),
            'sender_password': sender_password.get(),
            'smtp_server': smtp_server.get(),
            'smtp_port': int(smtp_port.get())
        })
        win.destroy()

    tk.Button(win, text="حفظ", command=save).grid(row=4, column=0, columnspan=2, pady=10)

def main():
    init_db()

    root = tk.Tk()
    root.title("متابعة وثائق سيارات الشركة")
    root.geometry("800x400")

    tree = ttk.Treeview(root, columns=("رقم", "نوع", "نهاية التأمين", "نهاية الضريبة", "البريد"), show="headings")
    for col in tree["columns"]:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.pack(fill="both", expand=True)

    def refresh():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT number, type, insurance_end, tax_end, email FROM cars")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def add_car():
        def save():
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO cars (number, type, insurance_end, tax_end, email) VALUES (?, ?, ?, ?, ?)",
                      (e1.get(), e2.get(), e3.get(), e4.get(), e5.get()))
            conn.commit()
            conn.close()
            win.destroy()
            refresh()

        win = tk.Toplevel()
        win.title("إضافة سيارة")
        labels = ["رقم السيارة", "نوع السيارة", "تاريخ نهاية التأمين (yyyy-mm-dd)", "تاريخ نهاية الضريبة (yyyy-mm-dd)", "بريد المستلم"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0)
            entry = tk.Entry(win, width=30)
            entry.grid(row=i, column=1)
            entries.append(entry)

        e1, e2, e3, e4, e5 = entries
        tk.Button(win, text="حفظ", command=save).grid(row=5, column=0, columnspan=2, pady=10)

    tk.Button(root, text="إضافة سيارة", command=add_car).pack(side="left", padx=5, pady=5)
    tk.Button(root, text="إعدادات البريد", command=open_settings_window).pack(side="left", padx=5)
    tk.Button(root, text="إرسال التنبيهات", command=check_and_notify).pack(side="left", padx=5)
    tk.Button(root, text="تحديث القائمة", command=refresh).pack(side="left", padx=5)

    refresh()
    root.mainloop()

if __name__ == "__main__":
    main()
