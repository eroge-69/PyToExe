import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# ========== إعدادات ==========
PASSWORD = "2591969"
products = []

# ========== الدوال ========== #
def check_password():
    entered = password_entry.get()
    if entered == PASSWORD:
        login_window.destroy()
        show_main_window()
    else:
        messagebox.showerror("خطأ", "كلمة السر غير صحيحة!")

def add_product():
    name = name_entry.get()
    category = category_entry.get()
    size = size_entry.get()
    quantity = quantity_entry.get()

    if not name or not category or not size or not quantity:
        messagebox.showwarning("تحذير", "يرجى ملء جميع الحقول.")
        return

    try:
        quantity = int(quantity)
    except ValueError:
        messagebox.showerror("خطأ", "الكمية يجب أن تكون رقم.")
        return

    products.append([name, category, size, quantity])
    update_table()
    clear_fields()

def clear_fields():
    name_entry.delete(0, tk.END)
    category_entry.delete(0, tk.END)
    size_entry.delete(0, tk.END)
    quantity_entry.delete(0, tk.END)

def update_table():
    for row in table.get_children():
        table.delete(row)

    for product in products:
        tag = 'low' if int(product[3]) < 5 else ''
        table.insert('', tk.END, values=product, tags=(tag,))

def search_products():
    term = search_entry.get().lower()
    table.delete(*table.get_children())

    for product in products:
        if term in product[0].lower() or term in product[1].lower():
            tag = 'low' if int(product[3]) < 5 else ''
            table.insert('', tk.END, values=product, tags=(tag,))

def save_backup():
    filename = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['الاسم', 'النوع', 'المقاس', 'الكمية'])
        writer.writerows(products)
    messagebox.showinfo("تم الحفظ", f"تم حفظ النسخة الاحتياطية في:\n{filename}")

def delete_selected():
    selected = table.selection()
    if not selected:
        messagebox.showwarning("تنبيه", "اختر منتجًا للحذف.")
        return
    for item in selected:
        values = table.item(item, 'values')
        products.remove(list(values))
        table.delete(item)

def exit_app():
    if messagebox.askyesno("خروج", "هل تريد الخروج؟"):
        root.destroy()

# ========== شاشة الدخول ========== #
login_window = tk.Tk()
login_window.title("تسجيل الدخول")
login_window.geometry("400x200")
login_window.configure(bg="#1e1e1e")

tk.Label(login_window, text="نظام إدارة مخزون - محل الرحمة", font=("Cairo", 16, "bold"), bg="#1e1e1e", fg="white").pack(pady=20)
tk.Label(login_window, text="أدخل كلمة السر:", font=("Cairo", 12), bg="#1e1e1e", fg="white").pack()

password_entry = tk.Entry(login_window, show="*", font=("Cairo", 12), justify='center')
password_entry.pack(pady=10)

tk.Button(login_window, text="دخول", font=("Cairo", 12, "bold"), command=check_password, bg="#457b9d", fg="white").pack(pady=5)

def show_main_window():
    global root, name_entry, category_entry, size_entry, quantity_entry, search_entry, table

    root = tk.Tk()
    root.title("🧥 محل الرحمة للملابس الجاهزة - نظام المخزون")
    root.geometry("1000x700")
    root.configure(bg="#2c2c2c")

    # ستايلات
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", background="#1e1e1e", foreground="#fff", rowheight=30, fieldbackground="#1e1e1e", font=("Cairo", 12))
    style.map("Treeview", background=[('selected', '#3e638b')])
    style.configure("Treeview.Heading", font=("Cairo", 13, "bold"), background="#457b9d", foreground="#fff")
    style.configure("TButton", font=("Cairo", 11, "bold"), padding=6)

    # رأس
    tk.Label(root, text="🧵 محل الرحمة للملابس الجاهزة 🧥", font=("Cairo", 24, "bold"), bg="#2c2c2c", fg="#ffcc00").pack(pady=10)
    tk.Label(root, text="نظام إدارة المخزون", font=("Cairo", 14), bg="#2c2c2c", fg="white").pack()

    # نموذج الإدخال
    form_frame = tk.Frame(root, bg="#2c2c2c")
    form_frame.pack(pady=10)

    labels = ["اسم المنتج", "نوع المنتج", "المقاس", "الكمية"]
    for i, text in enumerate(labels):
        tk.Label(form_frame, text=text, font=("Cairo", 13), bg="#2c2c2c", fg="white").grid(row=i, column=0, padx=10, pady=8, sticky="e")

    name_entry = tk.Entry(form_frame, font=("Cairo", 12))
    category_entry = tk.Entry(form_frame, font=("Cairo", 12))
    size_entry = tk.Entry(form_frame, font=("Cairo", 12))
    quantity_entry = tk.Entry(form_frame, font=("Cairo", 12))

    name_entry.grid(row=0, column=1, pady=8)
    category_entry.grid(row=1, column=1, pady=8)
    size_entry.grid(row=2, column=1, pady=8)
    quantity_entry.grid(row=3, column=1, pady=8)

    # أزرار
    btn_frame = tk.Frame(root, bg="#2c2c2c")
    btn_frame.pack(pady=10)

    add_btn = ttk.Button(btn_frame, text="➕ إضافة", command=add_product)
    search_entry = tk.Entry(btn_frame, font=("Cairo", 12), width=30)
    search_btn = ttk.Button(btn_frame, text="🔍 بحث", command=search_products)
    save_btn = ttk.Button(btn_frame, text="💾 حفظ نسخة احتياطية", command=save_backup)
    delete_btn = ttk.Button(btn_frame, text="🗑 حذف", command=delete_selected)
    exit_btn = ttk.Button(btn_frame, text="🚪 خروج", command=exit_app)

    add_btn.grid(row=0, column=0, padx=5, pady=5)
    search_entry.grid(row=0, column=1, padx=5, pady=5)
    search_btn.grid(row=0, column=2, padx=5, pady=5)
    save_btn.grid(row=1, column=0, padx=5, pady=5)
    delete_btn.grid(row=1, column=1, padx=5, pady=5)
    exit_btn.grid(row=1, column=2, padx=5, pady=5)

    # جدول البيانات
    table = ttk.Treeview(root, columns=("الاسم", "النوع", "المقاس", "الكمية"), show="headings", height=10)
    for col in ("الاسم", "النوع", "المقاس", "الكمية"):
        table.heading(col, text=col)
        table.column(col, anchor="center", width=200)

    table.tag_configure('low', background='#aa4444')

    table.pack(pady=20)
    root.mainloop()

login_window.mainloop()
