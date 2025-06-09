
import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

DB_FILE = 'cars.db'

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
    return {
        'sender_email': 'Boukersiwalid08@gmail.com',
        'sender_password': 'WALID2025',
        'smtp_server': 'smtp.gmail.com',
        'smtp_port': 587
    }

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

def main():
    init_db()

    root = tk.Tk()
    root.title("متابعة وثائق سيارات الشركة")
    root.geometry("900x400")

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

    def delete_car():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سيارة أولاً")
            return
        item = tree.item(selected[0])
        number = item['values'][0]
        if messagebox.askyesno("تأكيد", f"هل تريد حذف السيارة رقم {number}؟"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM cars WHERE number=?", (number,))
            conn.commit()
            conn.close()
            refresh()

    def edit_car():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "يرجى اختيار سيارة أولاً")
            return
        item = tree.item(selected[0])
        old_values = item['values']

        def save_changes():
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE cars SET number=?, type=?, insurance_end=?, tax_end=?, email=? WHERE number=?",
                      (e1.get(), e2.get(), e3.get(), e4.get(), e5.get(), old_values[0]))
            conn.commit()
            conn.close()
            win.destroy()
            refresh()

        win = tk.Toplevel()
        win.title("تعديل سيارة")
        labels = ["رقم السيارة", "نوع السيارة", "تاريخ نهاية التأمين (yyyy-mm-dd)", "تاريخ نهاية الضريبة (yyyy-mm-dd)", "بريد المستلم"]
        entries = []
        for i, label in enumerate(labels):
            tk.Label(win, text=label).grid(row=i, column=0)
            entry = tk.Entry(win, width=30)
            entry.grid(row=i, column=1)
            entry.insert(0, old_values[i])
            entries.append(entry)

        e1, e2, e3, e4, e5 = entries
        tk.Button(win, text="حفظ التعديلات", command=save_changes).grid(row=5, column=0, columnspan=2, pady=10)

    tk.Button(root, text="إضافة سيارة", command=add_car).pack(side="left", padx=5, pady=5)
    tk.Button(root, text="تعديل سيارة", command=edit_car).pack(side="left", padx=5)
    tk.Button(root, text="حذف سيارة", command=delete_car).pack(side="left", padx=5)
    tk.Button(root, text="إرسال التنبيهات", command=check_and_notify).pack(side="left", padx=5)
    tk.Button(root, text="تحديث القائمة", command=refresh).pack(side="left", padx=5)

    refresh()
    root.mainloop()

if __name__ == "__main__":
    main()
