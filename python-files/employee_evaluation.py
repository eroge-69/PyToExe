
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import pandas as pd
import os

DATA_FILE = "employees.xlsx"

# تحميل البيانات أو إنشاء ملف جديد
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=["اسم الموظف"])

# دالة تحديث الجدول
def refresh_table():
    for row in tree.get_children():
        tree.delete(row)
    for i, row in df.iterrows():
        tree.insert("", "end", values=list(row))

# إضافة موظف جديد
def add_employee():
    name = simpledialog.askstring("إضافة موظف", "أدخل اسم الموظف:")
    if name:
        global df
        df.loc[len(df)] = [name] + [0]*(len(df.columns)-1)
        refresh_table()
        save_data()

# إضافة عمود تقييم جديد
def add_column():
    col_name = simpledialog.askstring("إضافة تقييم", "أدخل اسم العمود الجديد:")
    if col_name:
        global df
        if col_name in df.columns:
            messagebox.showwarning("تحذير", "هذا العمود موجود مسبقًا!")
            return
        df[col_name] = 0
        tree["columns"] = list(df.columns)
        for col in df.columns:
            tree.heading(col, text=col)
        refresh_table()
        save_data()

# تعديل تقييم موظف
def edit_score():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("تنبيه", "اختر موظفًا لتعديل تقييمه")
        return
    col = simpledialog.askstring("تعديل التقييم", f"اختر اسم العمود لتعديل القيمة: {', '.join(df.columns[1:])}")
    if col not in df.columns:
        messagebox.showerror("خطأ", "اسم العمود غير موجود")
        return
    value = simpledialog.askstring("تعديل التقييم", "أدخل القيمة الجديدة:")
    try:
        value = float(value)
    except:
        messagebox.showerror("خطأ", "يجب إدخال رقم صالح")
        return
    idx = tree.index(selected[0])
    df.at[idx, col] = value
    refresh_table()
    save_data()

# حذف موظف
def delete_employee():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("تنبيه", "اختر موظفًا للحذف")
        return
    idx = tree.index(selected[0])
    df.drop(df.index[idx], inplace=True)
    df.reset_index(drop=True, inplace=True)
    refresh_table()
    save_data()

# حفظ البيانات
def save_data():
    df.to_excel(DATA_FILE, index=False)

# إنشاء واجهة Tkinter
root = tk.Tk()
root.title("برنامج تقييم ومتابعة الموظفين")
root.geometry("800x500")

# الجدول
tree = ttk.Treeview(root, columns=list(df.columns), show="headings")
for col in df.columns:
    tree.heading(col, text=col)
tree.pack(fill=tk.BOTH, expand=True)

# أزرار
frame = tk.Frame(root)
frame.pack(pady=10)
tk.Button(frame, text="إضافة موظف", command=add_employee).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="إضافة تقييم جديد", command=add_column).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="تعديل تقييم", command=edit_score).pack(side=tk.LEFT, padx=5)
tk.Button(frame, text="حذف موظف", command=delete_employee).pack(side=tk.LEFT, padx=5)

refresh_table()
root.mainloop()
