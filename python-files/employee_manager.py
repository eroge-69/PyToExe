
import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os
from datetime import datetime

excel_file = "employee_data.xlsx"

if not os.path.exists(excel_file):
    df = pd.DataFrame(columns=["الرقم", "الاسم", "الوظيفة", "الراتب", "تاريخ", "نوع التسجيل"])
    df.to_excel(excel_file, index=False)

def check_password():
    if password_entry.get() == "admin123":
        login_window.destroy()
        open_main_window()
    else:
        messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")

def save_data(emp_id, name, job, salary, record_type):
    df = pd.read_excel(excel_file)
    new_record = {
        "الرقم": emp_id,
        "الاسم": name,
        "الوظيفة": job,
        "الراتب": salary,
        "تاريخ": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "نوع التسجيل": record_type
    }
    df = pd.concat([df, pd.DataFrame([new_record])], ignore_index=True)
    df.to_excel(excel_file, index=False)
    messagebox.showinfo("تم", "تم حفظ البيانات بنجاح")

def open_main_window():
    main_window = tk.Tk()
    main_window.title("برنامج شؤون العاملين")

    tk.Label(main_window, text="رقم الموظف").grid(row=0, column=0)
    tk.Label(main_window, text="اسم الموظف").grid(row=1, column=0)
    tk.Label(main_window, text="الوظيفة").grid(row=2, column=0)
    tk.Label(main_window, text="الراتب").grid(row=3, column=0)

    id_entry = tk.Entry(main_window)
    name_entry = tk.Entry(main_window)
    job_entry = tk.Entry(main_window)
    salary_entry = tk.Entry(main_window)

    id_entry.grid(row=0, column=1)
    name_entry.grid(row=1, column=1)
    job_entry.grid(row=2, column=1)
    salary_entry.grid(row=3, column=1)

    def record_action(action_type):
        save_data(id_entry.get(), name_entry.get(), job_entry.get(), salary_entry.get(), action_type)

    tk.Button(main_window, text="تسجيل حضور", command=lambda: record_action("حضور")).grid(row=4, column=0)
    tk.Button(main_window, text="تسجيل انصراف", command=lambda: record_action("انصراف")).grid(row=4, column=1)
    tk.Button(main_window, text="تسجيل إجازة", command=lambda: record_action("إجازة")).grid(row=5, column=0)

    main_window.mainloop()

login_window = tk.Tk()
login_window.title("تسجيل الدخول")

tk.Label(login_window, text="أدخل كلمة المرور:").pack()
password_entry = tk.Entry(login_window, show="*")
password_entry.pack()
tk.Button(login_window, text="دخول", command=check_password).pack()

login_window.mainloop()
