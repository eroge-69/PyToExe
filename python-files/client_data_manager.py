import tkinter as tk
from tkinter import messagebox
import sqlite3

# كلمة المرور
PASSWORD = "2011993"

# نافذة تسجيل الدخول
def validate_password():
    entered_password = password_entry.get()
    if entered_password == PASSWORD:
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")

# نافذة تسجيل الدخول
login_window = tk.Tk()
login_window.title("تسجيل الدخول")
login_window.geometry("300x200")

label = tk.Label(login_window, text="أدخل كلمة المرور", font=("Arial", 14))
label.pack(pady=20)

password_entry = tk.Entry(login_window, show="*", font=("Arial", 14))
password_entry.pack(pady=10)

login_button = tk.Button(login_window, text="دخول", font=("Arial", 14), command=validate_password)
login_button.pack(pady=10)

# فتح النافذة الرئيسية بعد التحقق من كلمة المرور
def open_main_window():
    main_window = tk.Tk()
    main_window.title("إدارة بيانات العملاء")
    main_window.geometry("800x600")

    # زر إضافة بيانات جديدة
    add_button = tk.Button(main_window, text="إضافة بيانات جديدة", font=("Arial", 14), command=open_add_window)
    add_button.pack(pady=20)

    # زر تعديل البيانات
    modify_button = tk.Button(main_window, text="تعديل البيانات", font=("Arial", 14), command=open_modify_window)
    modify_button.pack(pady=20)

    # زر حذف البيانات
    delete_button = tk.Button(main_window, text="حذف البيانات", font=("Arial", 14), command=open_delete_window)
    delete_button.pack(pady=20)

    # زر البحث
    search_button = tk.Button(main_window, text="البحث عن عميل", font=("Arial", 14), command=open_search_window)
    search_button.pack(pady=20)

    # زر طباعة التقارير
    report_button = tk.Button(main_window, text="طباعة التقارير", font=("Arial", 14), command=open_report_window)
    report_button.pack(pady=20)

    main_window.mainloop()

# نافذة إضافة بيانات جديدة
def open_add_window():
    add_window = tk.Tk()
    add_window.title("إضافة بيانات جديدة")
    add_window.geometry("400x500")

    labels = [
        "رقم التسلسل", "الرقم الوطني", "الاسم رباعي", "اسم الأم", 
        "تاريخ الميلاد", "رقم الهاتف", "المؤهل العلمي", "تاريخ الحصول عليه",
        "اسم المصرف", "رقم الحساب", "تاريخ المباشرة", "مكان العمل", "ملاحظة"
    ]
    
    entries = {}
    for label in labels:
        row = tk.Frame(add_window)
        label_widget = tk.Label(row, text=label, width=15, anchor="w")
        entry_widget = tk.Entry(row, width=30)
        row.pack(pady=5)
        label_widget.pack(side="left")
        entry_widget.pack(side="right")
        entries[label] = entry_widget

    def save_data():
        # حفظ البيانات في قاعدة البيانات أو Excel
        data = {label: entry.get() for label, entry in entries.items()}
        save_to_database(data)
        add_window.destroy()

    save_button = tk.Button(add_window, text="حفظ", font=("Arial", 14), command=save_data)
    save_button.pack(pady=20)

    add_window.mainloop()

def save_to_database(data):
    conn = sqlite3.connect("clients.db")
    cursor = conn.cursor()
    
    # إنشاء الجدول في حال لم يكن موجودًا
    cursor.execute('''CREATE TABLE IF NOT EXISTS clients (
        serial_no TEXT, national_id TEXT, full_name TEXT, mother_name TEXT,
        birth_date TEXT, phone_number TEXT, qualification TEXT, qualification_date TEXT,
        bank_name TEXT, account_number TEXT, start_date TEXT, work_place TEXT, notes TEXT)''')
    
    # إدخال البيانات
    cursor.execute('''INSERT INTO clients (serial_no, national_id, full_name, mother_name, birth_date, 
                      phone_number, qualification, qualification_date, bank_name, account_number, 
                      start_date, work_place, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                   (data["رقم التسلسل"], data["الرقم الوطني"], data["الاسم رباعي"], data["اسم الأم"],
                    data["تاريخ الميلاد"], data["رقم الهاتف"], data["المؤهل العلمي"], data["تاريخ الحصول عليه"],
                    data["اسم المصرف"], data["رقم الحساب"], data["تاريخ المباشرة"], data["مكان العمل"], data["ملاحظة"]))
    
    conn.commit()
    conn.close()

# تشغيل نافذة تسجيل الدخول
login_window.mainloop()
