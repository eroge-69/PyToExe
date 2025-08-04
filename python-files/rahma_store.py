import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

# ========== إعدادات ==========
PASSWORD = "2591969"
DATA_FILE = "products.json"

# ========== تحميل البيانات ==========
def load_products():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ========== حفظ البيانات ==========
def save_products():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

# ========== شاشة الدخول ==========
def show_login():
    login_window = tk.Toplevel()
    login_window.title("تسجيل الدخول")
    login_window.geometry("300x150")
    login_window.configure(bg="#1e1e1e")
    login_window.resizable(False, False)

    tk.Label(login_window, text="ادخل كلمة السر:", bg="#1e1e1e", fg="white", font=("Cairo", 14)).pack(pady=20)
    pwd_entry = tk.Entry(login_window, show="*", font=("Cairo", 12))
    pwd_entry.pack()

    def check_password():
        if pwd_entry.get() == PASSWORD:
            login_window.destroy()
            show_main_window()
        else:
            messagebox.showerror("خطأ", "كلمة السر غير صحيحة")

    tk.Button(login_window, text="دخول", font=("Cairo", 12), command=check_password).pack(pady=10)

# ========== واجهة البرنامج الأساسية ==========
def show_main_window():
    global root, name_entry, category_entry, size_entry, quantity_entry, table, search_entry
    root = tk.Tk()
    root.title("🧥 برنامج الرحمة لإدارة المخزون")
    root.geometry("1000x700")
    root.configure(bg="#121212")

    # ========== الستايل ==========
    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview", 
                    background="#1e1e1e", 
                    foreground="#fff", 
                    rowheight=30, 
                    fieldbackground="#1e1e1e", 
                    font=("Cairo", 14))
    style.map("Treeview", background=[('selected', '#2a9d8f')])
    style.configure("Treeview.Heading", font=("Cairo", 16, "bold"), background="#264653", foreground="#fff")
    style.configure("TButton", font=("Cairo", 14), padding=10, background="#2a9d8f", foreground="#fff")

    # ========== العنوان ==========
    header = tk.Label(root, text="👕 نظام إدارة مخزون - محل الرحمة للملابس الجاهزة 👚", 
                      font=("Cairo", 24, "bold"), bg="#121212", fg="#e9c46a")
    header.pack(pady=20)

    # ========== نموذج الإدخال ==========
    form_frame = tk.Frame(root, bg="#121212")
    form_frame.pack(pady=10)

    tk.Label(form_frame, text="اسم المنتج:", font=("Cairo", 16), bg="#121212", fg="white").grid(row=0, column=0, sticky="e", padx=10, pady=10)
    tk.Label(form_frame, text="النوع:", font=("Cairo", 16), bg="#121212", fg="white").grid(row=1, column=0, sticky="e", padx=10, pady=10)
    tk.Label(form_frame, text="المقاس:", font=("Cairo", 16), bg="#121212", fg="white").grid(row=2, column=0, sticky="e", padx=10, pady=10)
    tk.Label(form_frame, text="الكمية:", font=("Cairo", 16), bg="#121212", fg="white").grid(row=3, column=0, sticky="e", padx=10, pady=10)

    name_entry = tk.Entry(form_frame, font=("Cairo", 14))
    category_entry = tk.Entry(form_frame, font=("Cairo", 14))
    size_entry = tk.Entry(form_frame, font=("Cairo", 14))
    quantity_entry = tk.Entry(form_frame, font=("Cairo", 14))

    name_entry.grid(row=0, column=1, pady=10)
    category_entry.grid(row=1, column=1, pady=10)
    size_entry.grid(row=2, column=1, pady=10)
    quantity_entry.grid(row=3, column=1, pady=10)

    # ========== أزرار ==========
    button_frame = tk.Frame(root, bg="#121212")
    button_frame.pack(pady=10)

    def add_product():
        name = name_entry.get()
        category = category_entry.get()
        size = size_entry.get()
        quantity = quantity_entry.get()

        if not name or not category or not size or not quantity:
            messagebox.showwarning("تنبيه", "املأ جميع الحقول من فضلك.")
            return

        try:
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror("خطأ", "الكمية يجب أن تكون رقمًا.")
            return

        products.append([name, category, size, quantity])
        save_products()
        update_table()
        clear_fields()

    def delete_selected():
        selected = table.selection()
        if not selected:
            messagebox.showwarning("تنبيه", "اختر عنصرًا للحذف.")
            return

        for item in selected:
            val = table.item(item, 'values')
            for i, prod in enumerate(products):
                if tuple(prod) == val:
                    del products[i]
                    break
            table.delete(item)
        save_products()

    def search_products():
        term = search_entry.get().lower()
        table.delete(*table.get_children())
        for product in products:
            if term in product[0].lower() or term in product[1].lower():
                tag = 'low' if int(product[3]) < 5 else ''
                table.insert('', 'end', values=product, tags=(tag,))

    def clear_fields():
        name_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        size_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)

    def update_table():
        table.delete(*table.get_children())
        for product in products:
            tag = 'low' if int(product[3]) < 5 else ''
            table.insert('', 'end', values=product, tags=(tag,))

    search_entry = tk.Entry(button_frame, font=("Cairo", 14), width=30)
    search_entry.grid(row=0, column=0, padx=5)

    tk.Button(button_frame, text="🔍 بحث", command=search_products).grid(row=0, column=1, padx=5)
    tk.Button(button_frame, text="➕ إضافة", command=add_product).grid(row=0, column=2, padx=5)
    tk.Button(button_frame, text="🗑 حذف", command=delete_selected).grid(row=0, column=3, padx=5)
    tk.Button(button_frame, text="🚪 خروج", command=root.destroy).grid(row=0, column=4, padx=5)

    # ========== الجدول ==========
    table = ttk.Treeview(root, columns=("اسم", "نوع", "مقاس", "كمية"), show="headings", height=10)
    for col in ("اسم", "نوع", "مقاس", "كمية"):
        table.heading(col, text=col)
        table.column(col, anchor="center")

    table.tag_configure('low', background='#ff6961')  # تنبيه الكميات القليلة
    table.pack(pady=20, fill="x", padx=20)

    update_table()
    root.mainloop()

# ========== تحميل البيانات وبدء البرنامج ==========
products = load_products()
show_login()
