
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

DB_FILE = 'cars.db'
SETTINGS_FILE = 'settings.txt'

# الترجمة حسب اللغة
translations = {
    'ar': {
        'title': 'متابعة وثائق سيارات الشركة',
        'car_number': 'رقم السيارة',
        'car_type': 'نوع السيارة',
        'insurance_end': 'نهاية التأمين',
        'inspection_end': 'نهاية المراقبة التقنية',
        'email': 'البريد',
        'add_car': 'إضافة سيارة',
        'edit_car': 'تعديل سيارة',
        'delete_car': 'حذف سيارة',
        'send_notifications': 'إرسال التنبيهات',
        'update_list': 'تحديث القائمة',
        'settings': 'إعدادات البريد',
        'days_before': 'عدد الأيام قبل الإشعار',
        'language': 'اللغة',
        'save': 'حفظ الإعدادات',
        'smtp_server': 'خادم SMTP',
        'smtp_port': 'منفذ SMTP',
        'sender_email': 'بريد المرسل',
        'sender_password': 'كلمة مرور المرسل'
    },
    'en': {
        'title': 'Vehicle Document Tracker',
        'car_number': 'Car Number',
        'car_type': 'Car Type',
        'insurance_end': 'Insurance Expiry',
        'inspection_end': 'Inspection Expiry',
        'email': 'Email',
        'add_car': 'Add Car',
        'edit_car': 'Edit Car',
        'delete_car': 'Delete Car',
        'send_notifications': 'Send Notifications',
        'update_list': 'Refresh List',
        'settings': 'Email Settings',
        'days_before': 'Days Before Notification',
        'language': 'Language',
        'save': 'Save Settings',
        'smtp_server': 'SMTP Server',
        'smtp_port': 'SMTP Port',
        'sender_email': 'Sender Email',
        'sender_password': 'Sender Password'
    },
    'fr': {
        'title': 'Suivi des Documents Véhicule',
        'car_number': 'Numéro Véhicule',
        'car_type': 'Type',
        'insurance_end': 'Fin Assurance',
        'inspection_end': 'Fin Contrôle Technique',
        'email': 'Email',
        'add_car': 'Ajouter',
        'edit_car': 'Modifier',
        'delete_car': 'Supprimer',
        'send_notifications': 'Envoyer les alertes',
        'update_list': 'Rafraîchir',
        'settings': 'Paramètres Email',
        'days_before': 'Jours avant l'alerte',
        'language': 'Langue',
        'save': 'Sauvegarder',
        'smtp_server': 'Serveur SMTP',
        'smtp_port': 'Port SMTP',
        'sender_email': 'Email d'envoi',
        'sender_password': 'Mot de passe'
    }
}

language = 'ar'

def t(key):
    return translations[language].get(key, key)

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        type TEXT,
        insurance_end TEXT,
        inspection_end TEXT,
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
                'smtp_port': int(lines[3]),
                'days_before': int(lines[4])
            }
    except:
        return {
            'sender_email': 'chakergroupnotification@gmail.com',
            'sender_password': 'yqyd jhad shkh qpwe',
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'days_before': 3
        }

def save_settings(s):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        f.write(f"{s['sender_email']}\n{s['sender_password']}\n{s['smtp_server']}\n{s['smtp_port']}\n{s['days_before']}")

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
        print(f"Email failed to {car['email']}: {e}")


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
            'inspection_end': datetime.strptime(row[4], "%Y-%m-%d").date(),
            'email': row[5]
        }

        if (car['insurance_end'] - today).days == load_settings()['days_before']:
            msg = f"تنبيه: تأمين السيارة رقم {car['number']} ينتهي بتاريخ {car['insurance_end']}."
            send_notification(car, settings, "تنبيه بانتهاء التأمين", msg)

        if (car['inspection_end'] - today).days == load_settings()['days_before']:
            msg = f"تنبيه: المراقبة التقنية للسيارة رقم {car['number']} تنتهي بتاريخ {car['inspection_end']}."
            send_notification(car, settings, "تنبيه بانتهاء المراقبة التقنية", msg)

def open_settings_window(refresh_ui):
    s = load_settings()
    win = tk.Toplevel()
    win.title(t('settings'))
    labels = ['sender_email', 'sender_password', 'smtp_server', 'smtp_port', 'days_before']
    entries = {}
    for i, key in enumerate(labels):
        tk.Label(win, text=t(key)).grid(row=i, column=0, sticky='w')
        entry = tk.Entry(win, width=40)
        entry.insert(0, str(s[key]))
        entry.grid(row=i, column=1)
        entries[key] = entry

    def save():
        new_settings = {key: entries[key].get() for key in labels}
        new_settings['smtp_port'] = int(new_settings['smtp_port'])
        new_settings['days_before'] = int(new_settings['days_before'])
        save_settings(new_settings)
        messagebox.showinfo(t('settings'), t('save'))
        win.destroy()

    tk.Button(win, text=t('save'), command=save).grid(row=len(labels), column=0, columnspan=2, pady=10)

def main():
    init_db()
    root = tk.Tk()
    root.title(t('title'))
    root.geometry("950x500")

    # اختيار اللغة
    def switch_lang(l):
        global language
        language = l
        root.destroy()
        main()

    lang_frame = tk.Frame(root)
    lang_frame.pack()
    for code, label in [('ar', 'العربية'), ('en', 'English'), ('fr', 'Français')]:
        tk.Button(lang_frame, text=label, command=lambda c=code: switch_lang(c)).pack(side='left', padx=5)

    tree = ttk.Treeview(root, columns=("number", "type", "insurance", "inspection", "email"), show="headings")
    for col, key in zip(tree["columns"], ["car_number", "car_type", "insurance_end", "inspection_end", "email"]):
        tree.heading(col, text=t(key))
        tree.column(col, width=180)
    tree.pack(fill="both", expand=True)

    def refresh():
        for row in tree.get_children():
            tree.delete(row)
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT number, type, insurance_end, inspection_end, email FROM cars")
        for row in c.fetchall():
            tree.insert("", "end", values=row)
        conn.close()

    def add_car():
        win = tk.Toplevel()
        win.title(t('add_car'))
        labels = ["car_number", "car_type", "insurance_end", "inspection_end", "email"]
        entries = []
        for i, key in enumerate(labels):
            tk.Label(win, text=t(key)).grid(row=i, column=0)
            entry = tk.Entry(win, width=30)
            entry.grid(row=i, column=1)
            entries.append(entry)
        def save():
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("INSERT INTO cars (number, type, insurance_end, inspection_end, email) VALUES (?, ?, ?, ?, ?)",
                      tuple(e.get() for e in entries))
            conn.commit()
            conn.close()
            win.destroy()
            refresh()
        tk.Button(win, text=t('save'), command=save).grid(row=5, column=0, columnspan=2, pady=10)

    def edit_car():
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        old_values = item['values']
        win = tk.Toplevel()
        win.title(t('edit_car'))
        labels = ["car_number", "car_type", "insurance_end", "inspection_end", "email"]
        entries = []
        for i, key in enumerate(labels):
            tk.Label(win, text=t(key)).grid(row=i, column=0)
            entry = tk.Entry(win, width=30)
            entry.insert(0, old_values[i])
            entry.grid(row=i, column=1)
            entries.append(entry)
        def save_changes():
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("UPDATE cars SET number=?, type=?, insurance_end=?, inspection_end=?, email=? WHERE number=?",
                      (*[e.get() for e in entries], old_values[0]))
            conn.commit()
            conn.close()
            win.destroy()
            refresh()
        tk.Button(win, text=t('save'), command=save_changes).grid(row=5, column=0, columnspan=2, pady=10)

    def delete_car():
        selected = tree.selection()
        if not selected:
            return
        item = tree.item(selected[0])
        number = item['values'][0]
        if messagebox.askyesno(t('delete_car'), f"{t('delete_car')} {number}?"):
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM cars WHERE number=?", (number,))
            conn.commit()
            conn.close()
            refresh()

    frame = tk.Frame(root)
    frame.pack(pady=5)
    tk.Button(frame, text=t('add_car'), command=add_car).pack(side="left", padx=5)
    tk.Button(frame, text=t('edit_car'), command=edit_car).pack(side="left", padx=5)
    tk.Button(frame, text=t('delete_car'), command=delete_car).pack(side="left", padx=5)
    tk.Button(frame, text=t('send_notifications'), command=check_and_notify).pack(side="left", padx=5)
    tk.Button(frame, text=t('update_list'), command=refresh).pack(side="left", padx=5)
    tk.Button(frame, text=t('settings'), command=lambda: open_settings_window(refresh)).pack(side="left", padx=5)

    refresh()
    root.mainloop()

if __name__ == "__main__":
    main()
