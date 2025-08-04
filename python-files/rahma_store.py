import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import pandas as pd
from datetime import datetime

# الاتصال بقاعدة البيانات
def connect_db():
    return sqlite3.connect("rahma_store.db")

# إضافة منتج
def add_product():
    if not (entry_name.get() and entry_category.get() and entry_size.get() and entry_color.get() and entry_price.get() and entry_quantity.get()):
        messagebox.showwarning("تحذير", "يرجى ملء جميع الخانات")
        return
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO products (name, category, size, color, price, quantity)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entry_name.get(), entry_category.get(), entry_size.get(),
            entry_color.get(), float(entry_price.get()), int(entry_quantity.get())
        ))
        conn.commit()
        conn.close()
        messagebox.showinfo("تم", "تمت إضافة المنتج بنجاح")
        clear_entries()
        refresh_table()
    except Exception as e:
        messagebox.showerror("خطأ", str(e))

# تحديث الجدول
def refresh_table():
    for row in table.get_children():
        table.delete(row)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    rows = cursor.fetchall()
    for row in rows:
        table.insert("", "end", values=row, tags=("low" if row[6] < 5 else "normal"))
    conn.close()

# مسح الخانات
def clear_entries():
    entry_name.delete(0, tk.END)
    entry_category.delete(0, tk.END)
    entry_size.delete(0, tk.END)
    entry_color.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    entry_quantity.delete(0, tk.END)

# بحث
def search_products():
    keyword = entry_search.get()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE name LIKE ? OR category LIKE ?", ('%' + keyword + '%', '%' + keyword + '%'))
    rows = cursor.fetchall()
    conn.close()
    for row in table.get_children():
        table.delete(row)
    for row in rows:
        table.insert("", "end", values=row, tags=("low" if row[6] < 5 else "normal"))

# تصدير نسخة احتياطية
def export_backup():
    df = pd.read_sql_query("SELECT * FROM products", connect_db())
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_csv(f"rahma_backup_{now}.csv", index=False, encoding="utf-8-sig")
    messagebox.showinfo("تم", "تم حفظ النسخة الاحتياطية")

# إنشاء قاعدة البيانات إذا لم تكن موجودة
conn = connect_db()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    size TEXT NOT NULL,
    color TEXT NOT NULL,
    price REAL NOT NULL,
    quantity INTEGER NOT NULL
)
""")
conn.commit()
conn.close()

# بناء الواجهة
root = tk.Tk()
root.title("الرحمه للملابس الجاهزه")
root.geometry("900x600")

# الحقول
tk.Label(root, text="الاسم").grid(row=0, column=0)
entry_name = tk.Entry(root)
entry_name.grid(row=0, column=1)

tk.Label(root, text="النوع").grid(row=1, column=0)
entry_category = tk.Entry(root)
entry_category.grid(row=1, column=1)

tk.Label(root, text="المقاس").grid(row=2, column=0)
entry_size = tk.Entry(root)
entry_size.grid(row=2, column=1)

tk.Label(root, text="اللون").grid(row=3, column=0)
entry_color = tk.Entry(root)
entry_color.grid(row=3, column=1)

tk.Label(root, text="السعر").grid(row=4, column=0)
entry_price = tk.Entry(root)
entry_price.grid(row=4, column=1)

tk.Label(root, text="الكمية").grid(row=5, column=0)
entry_quantity = tk.Entry(root)
entry_quantity.grid(row=5, column=1)

tk.Button(root, text="إضافة المنتج", command=add_product).grid(row=6, column=1)

# البحث
tk.Label(root, text="بحث بالاسم أو النوع").grid(row=7, column=0)
entry_search = tk.Entry(root)
entry_search.grid(row=7, column=1)
tk.Button(root, text="بحث", command=search_products).grid(row=7, column=2)

# جدول عرض المنتجات
cols = ("ID", "الاسم", "النوع", "المقاس", "اللون", "السعر", "الكمية")
table = ttk.Treeview(root, columns=cols, show="headings")
for col in cols:
    table.heading(col, text=col)
table.grid(row=8, column=0, columnspan=4)
table.tag_configure("low", background="red")

# زر النسخ الاحتياطي
tk.Button(root, text="تصدير نسخة احتياطية", command=export_backup).grid(row=9, column=1)

refresh_table()
root.mainloop()
