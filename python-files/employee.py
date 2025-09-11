import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import os
from datetime import datetime

# اسم ملف الإكسل
EXCEL_FILE = "employees_data.xlsx"

# التحقق من وجود الملف أو إنشاؤه
def init_excel():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["الاسم", "الوظيفة", "القسم", "رقم الهاتف", "الراتب", "تاريخ التعيين"])
        df.to_excel(EXCEL_FILE, index=False)

# قراءة البيانات
def load_data():
    return pd.read_excel(EXCEL_FILE)

# حفظ موظف جديد
def save_employee(emp_data):
    df = load_data()
    new_df = pd.DataFrame([emp_data])
    df = pd.concat([df, new_df], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

# إضافة موظف من خلال النموذج
def add_employee():
    name = entry_name.get().strip()
    job = entry_job.get().strip()
    department = entry_dept.get().strip()
    phone = entry_phone.get().strip()
    salary = entry_salary.get().strip()
    hire_date = entry_date.get().strip()

    if not all([name, job, department, phone, salary, hire_date]):
        messagebox.showerror("خطأ", "يرجى تعبئة جميع الحقول!")
        return

    try:
        float(salary)
    except ValueError:
        messagebox.showerror("خطأ", "الرجاء إدخال قيمة رقمية للراتب.")
        return

    try:
        datetime.strptime(hire_date, "%d/%m/%Y")
    except ValueError:
        messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح. استخدم: يوم/شهر/سنة")
        return

    emp_data = {
        "الاسم": name,
        "الوظيفة": job,
        "القسم": department,
        "رقم الهاتف": phone,
        "الراتب": float(salary),
        "تاريخ التعيين": hire_date
    }

    save_employee(emp_data)
    refresh_table()
    clear_form()
    messagebox.showinfo("نجاح", f"تم حفظ الموظف '{name}' بنجاح!")

# تحديث الجدول
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    df = load_data()
    for _, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# مسح الحقول بعد الإدخال
def clear_form():
    entry_name.delete(0, tk.END)
    entry_job.delete(0, tk.END)
    entry_dept.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_salary.delete(0, tk.END)
    entry_date.delete(0, tk.END)

# حذف الموظف المحدد
def delete_employee():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("تحذير", "اختر موظفًا من القائمة أولًا.")
        return

    item = tree.item(selected[0])
    employee_name = item['values'][0]

    confirm = messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف الموظف {employee_name}؟")
    if confirm:
        df = load_data()
        df = df[df["الاسم"] != employee_name]
        df.to_excel(EXCEL_FILE, index=False)
        refresh_table()
        messagebox.showinfo("تم الحذف", f"تم حذف الموظف {employee_name}.")

# تعديل الموظف (سيُملأ النموذج بالبيانات)
def edit_employee():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("تحذير", "اختر موظفًا من القائمة أولًا.")
        return

    item = tree.item(selected[0])
    values = item['values']

    # ملء الحقول
    entry_name.delete(0, tk.END)
    entry_name.insert(0, values[0])
    entry_job.delete(0, tk.END)
    entry_job.insert(0, values[1])
    entry_dept.delete(0, tk.END)
    entry_dept.insert(0, values[2])
    entry_phone.delete(0, tk.END)
    entry_phone.insert(0, values[3])
    entry_salary.delete(0, tk.END)
    entry_salary.insert(0, values[4])
    entry_date.delete(0, tk.END)
    entry_date.insert(0, values[5])

    # تغيير زر الإضافة إلى "تحديث"
    button_add.config(text="تحديث", command=lambda: update_employee(values[0]))
    button_cancel.grid(row=6, column=1, padx=5, pady=10)

def update_employee(old_name):
    name = entry_name.get().strip()
    job = entry_job.get().strip()
    department = entry_dept.get().strip()
    phone = entry_phone.get().strip()
    salary = entry_salary.get().strip()
    hire_date = entry_date.get().strip()

    try:
        float(salary)
    except ValueError:
        messagebox.showerror("خطأ", "الرجاء إدخال قيمة رقمية للراتب.")
        return

    try:
        datetime.strptime(hire_date, "%d/%m/%Y")
    except ValueError:
        messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح.")
        return

    df = load_data()
    df.loc[df["الاسم"] == old_name, :] = [name, job, department, phone, float(salary), hire_date]
    df.to_excel(EXCEL_FILE, index=False)

    refresh_table()
    clear_form()
    button_add.config(text="إضافة موظف", command=add_employee)
    button_cancel.grid_remove()
    messagebox.showinfo("نجاح", "تم تحديث بيانات الموظف بنجاح!")

def cancel_edit():
    clear_form()
    button_add.config(text="إضافة موظف", command=add_employee)
    button_cancel.grid_remove()

# واجهة المستخدم الرئيسية
init_excel()

root = tk.Tk()
root.title("👥 برنامج إدارة الموظفين")
root.geometry("900x600")
root.resizable(False, False)
root.configure(bg="#f0f0f0")

# --- إطار الإدخال ---
frame_form = tk.LabelFrame(root, text="إدخال بيانات الموظف", padx=10, pady=10, bg="#f7f7f7")
frame_form.pack(padx=20, pady=10, fill="x")

tk.Label(frame_form, text="الاسم:", bg="#f7f7f7").grid(row=0, column=0, sticky="e")
entry_name = tk.Entry(frame_form, width=30)
entry_name.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_form, text="الوظيفة:", bg="#f7f7f7").grid(row=1, column=0, sticky="e")
entry_job = tk.Entry(frame_form, width=30)
entry_job.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_form, text="القسم:", bg="#f7f7f7").grid(row=2, column=0, sticky="e")
entry_dept = tk.Entry(frame_form, width=30)
entry_dept.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_form, text="رقم الهاتف:", bg="#f7f7f7").grid(row=0, column=2, sticky="e")
entry_phone = tk.Entry(frame_form, width=20)
entry_phone.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_form, text="الراتب:", bg="#f7f7f7").grid(row=1, column=2, sticky="e")
entry_salary = tk.Entry(frame_form, width=20)
entry_salary.grid(row=1, column=3, padx=5, pady=5)

tk.Label(frame_form, text="تاريخ التعيين (يوم/شهر/سنة):", bg="#f7f7f7").grid(row=2, column=2, sticky="e")
entry_date = tk.Entry(frame_form, width=20)
entry_date.grid(row=2, column=3, padx=5, pady=5)

button_add = tk.Button(frame_form, text="إضافة موظف", command=add_employee, bg="#4CAF50", fg="white")
button_add.grid(row=6, column=0, padx=5, pady=10)

button_cancel = tk.Button(frame_form, text="إلغاء", command=cancel_edit, bg="#ff9800", fg="white")

# --- جدول العرض ---
frame_table = tk.Frame(root)
frame_table.pack(padx=20, pady=10, fill="both", expand=True)

columns = ["الاسم", "الوظيفة", "القسم", "رقم الهاتف", "الراتب", "تاريخ التعيين"]
tree = ttk.Treeview(frame_table, columns=columns, show="headings", height=10)

# تحديد عناوين الأعمدة
for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=120, anchor="center")

tree.pack(side="left", fill="both", expand=True)

# شريط التمرير
scrollbar = ttk.Scrollbar(frame_table, orient="vertical", command=tree.yview)
scrollbar.pack(side="right", fill="y")
tree.configure(yscrollcommand=scrollbar.set)

# --- أزرار التحكم ---
frame_buttons = tk.Frame(root, bg="#f0f0f0")
frame_buttons.pack(pady=5)

tk.Button(frame_buttons, text="🗑️ حذف", command=delete_employee, bg="#f44336", fg="white", width=10).pack(side="left", padx=5)
tk.Button(frame_buttons, text="✏️ تعديل", command=edit_employee, bg="#2196F3", fg="white", width=10).pack(side="left", padx=5)
tk.Button(frame_buttons, text="🔄 تحديث القائمة", command=refresh_table, bg="#9C27B0", fg="white", width=15).pack(side="left", padx=5)

# تحميل البيانات عند التشغيل
refresh_table()

# تشغيل البرنامج
root.mainloop()