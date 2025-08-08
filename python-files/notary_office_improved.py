
import sqlite3
from tkinter import *
from tkinter import messagebox, ttk

# اتصال به دیتابیس
conn = sqlite3.connect("notary_data.db")
cursor = conn.cursor()

# ساخت جدول
cursor.execute('''CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    plate_number TEXT,
    forbidden TEXT,
    duplicate_title TEXT,
    lost_title TEXT,
    extra1 TEXT,
    extra2 TEXT
)''')
conn.commit()

# توابع
def add_record():
    cursor.execute("INSERT INTO records (full_name, plate_number, forbidden, duplicate_title, lost_title, extra1, extra2) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (entry_name.get(), entry_plate.get(), var_forbidden.get(), var_duplicate.get(), var_lost.get(), entry_extra1.get(), entry_extra2.get()))
    conn.commit()
    show_records()
    clear_fields()

def show_records():
    for row in tree.get_children():
        tree.delete(row)
    for row in cursor.execute("SELECT * FROM records"):
        tree.insert("", END, values=row)

def delete_record():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("هشدار", "لطفاً یک ردیف را انتخاب کنید.")
        return
    item = tree.item(selected[0])
    record_id = item['values'][0]
    cursor.execute("DELETE FROM records WHERE id=?", (record_id,))
    conn.commit()
    show_records()

def search_records():
    query = entry_search.get()
    for row in tree.get_children():
        tree.delete(row)
    for row in cursor.execute("SELECT * FROM records WHERE full_name LIKE ?", ('%' + query + '%',)):
        tree.insert("", END, values=row)

def clear_fields():
    entry_name.delete(0, END)
    entry_plate.delete(0, END)
    var_forbidden.set("خیر")
    var_duplicate.set("خیر")
    var_lost.set("خیر")
    entry_extra1.delete(0, END)
    entry_extra2.delete(0, END)

# رابط گرافیکی
root = Tk()
root.title("نرم‌افزار مدیریت دفترخانه")
root.geometry("850x600")

font_main = ("B Nazanin", 12)

Label(root, text="نام و نام خانوادگی:", font=font_main).grid(row=0, column=0, sticky=W)
entry_name = Entry(root, font=font_main, width=30)
entry_name.grid(row=0, column=1)

Label(root, text="شماره پلاک ثبتی:", font=font_main).grid(row=1, column=0, sticky=W)
entry_plate = Entry(root, font=font_main, width=30)
entry_plate.grid(row=1, column=1)

var_forbidden = StringVar(value="خیر")
Checkbutton(root, text="ممنوع‌المعامله", variable=var_forbidden, onvalue="بله", offvalue="خیر", font=font_main).grid(row=2, column=1, sticky=W)

var_duplicate = StringVar(value="خیر")
Checkbutton(root, text="سند مالکیت المثنی", variable=var_duplicate, onvalue="بله", offvalue="خیر", font=font_main).grid(row=3, column=1, sticky=W)

var_lost = StringVar(value="خیر")
Checkbutton(root, text="مفقودی سند مالکیت", variable=var_lost, onvalue="بله", offvalue="خیر", font=font_main).grid(row=4, column=1, sticky=W)

Label(root, text="ستون اضافه ۱:", font=font_main).grid(row=5, column=0, sticky=W)
entry_extra1 = Entry(root, font=font_main, width=30)
entry_extra1.grid(row=5, column=1)

Label(root, text="ستون اضافه ۲:", font=font_main).grid(row=6, column=0, sticky=W)
entry_extra2 = Entry(root, font=font_main, width=30)
entry_extra2.grid(row=6, column=1)

Button(root, text="ثبت", command=add_record, font=font_main, width=15).grid(row=7, column=1, pady=10, sticky=W)
Button(root, text="حذف", command=delete_record, font=font_main, width=15).grid(row=7, column=1, pady=10, sticky=E)

Label(root, text="جستجو بر اساس نام:", font=font_main).grid(row=8, column=0, sticky=W)
entry_search = Entry(root, font=font_main, width=30)
entry_search.grid(row=8, column=1)
Button(root, text="جستجو", command=search_records, font=font_main).grid(row=8, column=2, padx=10)

# جدول نمایش اطلاعات
tree = ttk.Treeview(root, columns=("id", "full_name", "plate_number", "forbidden", "duplicate", "lost", "extra1", "extra2"), show="headings", height=10)
tree.grid(row=9, column=0, columnspan=3, padx=10, pady=10)
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=100)

show_records()
root.mainloop()
