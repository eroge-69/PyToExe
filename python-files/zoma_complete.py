import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

# ================================
# إعدادات عامة
# ================================
ROOT_BG = "#f0f0f0"
HEADER_STYLE = {"font": ("Arial", 20, "bold"), "bg": ROOT_BG, "fg": "#333"}
LABEL_STYLE = {"font": ("Arial", 14), "bg": ROOT_BG, "fg": "#000"}
ENTRY_STYLE = {"font": ("Arial", 14)}
BUTTON_STYLE = {"font": ("Arial", 14, "bold"), "bg": "#4CAF50", "fg": "white", "width": 20, "height": 2}
SPECIAL_BUTTON_STYLE = {"font": ("Arial", 14, "bold"), "bg": "#2196F3", "fg": "white", "width": 22, "height": 2}
EDIT_BUTTON_STYLE = {"font": ("Arial", 14, "bold"), "bg": "#FF9800", "fg": "white", "width": 20, "height": 2}
DELETE_BUTTON_STYLE = {"font": ("Arial", 14, "bold"), "bg": "#f44336", "fg": "white", "width": 20, "height": 2}

# ================================
# بيانات مؤقتة
# ================================
users = [("admin", "123", ["Products","Suppliers","Customers","Sales","Purchases","Reports","Settings"])]
suppliers = [("Supplier A",), ("Supplier B",)]
customers = [("Customer A", 500), ("Customer B", 1000)]
products = [("Product 1", 100, 50, "Supplier A"), ("Product 2", 150, 30, "Supplier B")]
sales = []
purchases = []

sales_counter = 1
purchase_counter = 1

# ================================
# حفظ التقرير CSV
# ================================
def save_treeview_as_csv(tree, title):
    file_path = tk.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
    if not file_path:
        return
    with open(file_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        headers = [tree.heading(col)["text"] for col in tree["columns"]]
        writer.writerow(headers)
        for row_id in tree.get_children():
            values = tree.item(row_id)["values"]
            writer.writerow(values)
    messagebox.showinfo("تم", f"تم حفظ التقرير CSV: {file_path}")

# ================================
# تسجيل الدخول
# ================================
def login_screen(root):
    login_frame = tk.Frame(root, bg=ROOT_BG)
    login_frame.pack(expand=True, fill="both")
    tk.Label(login_frame, text="🔑 تسجيل الدخول", **HEADER_STYLE).pack(pady=20)
    tk.Label(login_frame, text="اسم المستخدم:", **LABEL_STYLE).pack(pady=5)
    username_entry = tk.Entry(login_frame, **ENTRY_STYLE)
    username_entry.pack(pady=5)
    tk.Label(login_frame, text="كلمة المرور:", **LABEL_STYLE).pack(pady=5)
    password_entry = tk.Entry(login_frame, show="*", **ENTRY_STYLE)
    password_entry.pack(pady=5)

    def check_login(event=None):
        username = username_entry.get().strip()
        password = password_entry.get().strip()
        for user in users:
            if user[0] == username and user[1] == password:
                login_frame.destroy()
                main_app(root, user[2])
                return
        messagebox.showerror("خطأ", "❌ اسم المستخدم أو كلمة المرور غير صحيحة")

    tk.Button(login_frame, text="دخول", command=check_login, **BUTTON_STYLE).pack(pady=20)
    root.bind("<Return>", check_login)

# ================================
# شاشة العملاء
# ================================
def customers_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text="👥 شاشة العملاء", **HEADER_STYLE).pack(pady=20)

    tree = ttk.Treeview(frame, columns=("name", "balance"), show="headings", height=12)
    tree.heading("name", text="اسم العميل")
    tree.heading("balance", text="الرصيد المسموح به")
    tree.pack(pady=10, fill="x")

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for c in customers:
            tree.insert("", "end", values=c)
    refresh_table()

    def add_customer():
        add_win = tk.Toplevel(root)
        add_win.title("إضافة عميل")
        add_win.geometry("400x300")
        add_win.config(bg=ROOT_BG)
        tk.Label(add_win, text="إضافة عميل", **HEADER_STYLE).pack(pady=10)
        tk.Label(add_win, text="اسم العميل:", **LABEL_STYLE).pack(pady=5)
        name_entry = tk.Entry(add_win, **ENTRY_STYLE)
        name_entry.pack(pady=5)
        tk.Label(add_win, text="الرصيد المسموح به:", **LABEL_STYLE).pack(pady=5)
        balance_entry = tk.Entry(add_win, **ENTRY_STYLE)
        balance_entry.pack(pady=5)
        def save_customer():
            name = name_entry.get().strip()
            balance = balance_entry.get().strip()
            if not name or not balance:
                messagebox.showerror("خطأ", "الرجاء إدخال جميع البيانات")
                return
            customers.append((name, balance))
            refresh_table()
            add_win.destroy()
        tk.Button(add_win, text="حفظ", command=save_customer, **BUTTON_STYLE).pack(pady=20)

    btn_frame = tk.Frame(frame, bg=ROOT_BG)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="➕ إضافة عميل", command=add_customer, **SPECIAL_BUTTON_STYLE).grid(row=0,column=0,padx=5)
    tk.Button(btn_frame, text="✏ تعديل عميل", command=lambda: messagebox.showinfo("Info","تعديل عميل"), **EDIT_BUTTON_STYLE).grid(row=0,column=1,padx=5)
    tk.Button(btn_frame, text="🗑 حذف عميل", command=lambda: messagebox.showinfo("Info","حذف عميل"), **DELETE_BUTTON_STYLE).grid(row=0,column=2,padx=5)
    tk.Button(btn_frame, text="🔍 بحث", command=lambda: messagebox.showinfo("Info","بحث عن عميل"), **BUTTON_STYLE).grid(row=0,column=3,padx=5)
    tk.Button(btn_frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).grid(row=0,column=4,padx=5)
    tk.Button(frame, text="حفظ التقرير CSV", command=lambda: save_treeview_as_csv(tree,"تقرير العملاء"), **BUTTON_STYLE).pack(pady=5)

# ================================
# شاشة الموردين
# ================================
def suppliers_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text="🏢 شاشة الموردين", **HEADER_STYLE).pack(pady=20)

    tree = ttk.Treeview(frame, columns=("name",), show="headings", height=12)
    tree.heading("name", text="اسم المورد")
    tree.pack(pady=10, fill="x")

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for s in suppliers:
            tree.insert("", "end", values=s)
    refresh_table()

    def add_supplier():
        add_win = tk.Toplevel(root)
        add_win.title("إضافة مورد")
        add_win.geometry("400x300")
        add_win.config(bg=ROOT_BG)
        tk.Label(add_win, text="إضافة مورد", **HEADER_STYLE).pack(pady=10)
        tk.Label(add_win, text="اسم المورد:", **LABEL_STYLE).pack(pady=5)
        name_entry = tk.Entry(add_win, **ENTRY_STYLE)
        name_entry.pack(pady=5)
        def save_supplier():
            name = name_entry.get().strip()
            if not name:
                messagebox.showerror("خطأ", "الرجاء إدخال اسم المورد")
                return
            suppliers.append((name,))
            refresh_table()
            add_win.destroy()
        tk.Button(add_win, text="حفظ", command=save_supplier, **BUTTON_STYLE).pack(pady=20)

    btn_frame = tk.Frame(frame, bg=ROOT_BG)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="➕ إضافة مورد", command=add_supplier, **SPECIAL_BUTTON_STYLE).grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="✏ تعديل مورد", command=lambda: messagebox.showinfo("Info","تعديل مورد"), **EDIT_BUTTON_STYLE).grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="🗑 حذف مورد", command=lambda: messagebox.showinfo("Info","حذف مورد"), **DELETE_BUTTON_STYLE).grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).grid(row=0, column=3, padx=5)
    tk.Button(frame, text="حفظ التقرير CSV", command=lambda: save_treeview_as_csv(tree,"تقرير الموردين"), **BUTTON_STYLE).pack(pady=5)

# ================================
# شاشة الأصناف
# ================================
def products_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text="📦 شاشة الأصناف", **HEADER_STYLE).pack(pady=20)

    tree = ttk.Treeview(frame, columns=("name","price","qty","supplier"), show="headings", height=12)
    tree.heading("name", text="اسم الصنف")
    tree.heading("price", text="السعر")
    tree.heading("qty", text="الكمية")
    tree.heading("supplier", text="المورد")
    tree.pack(pady=10, fill="x")

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for p in products:
            tree.insert("", "end", values=p)
    refresh_table()

    def add_product():
        add_win = tk.Toplevel(root)
        add_win.title("إضافة صنف")
        add_win.geometry("400x400")
        add_win.config(bg=ROOT_BG)
        tk.Label(add_win, text="إضافة صنف جديد", **HEADER_STYLE).pack(pady=10)
        tk.Label(add_win, text="اسم الصنف:", **LABEL_STYLE).pack(pady=5)
        name_entry = tk.Entry(add_win, **ENTRY_STYLE)
        name_entry.pack(pady=5)
        tk.Label(add_win, text="السعر:", **LABEL_STYLE).pack(pady=5)
        price_entry = tk.Entry(add_win, **ENTRY_STYLE)
        price_entry.pack(pady=5)
        tk.Label(add_win, text="الكمية:", **LABEL_STYLE).pack(pady=5)
        qty_entry = tk.Entry(add_win, **ENTRY_STYLE)
        qty_entry.pack(pady=5)
        tk.Label(add_win, text="المورد:", **LABEL_STYLE).pack(pady=5)
        supplier_var = tk.StringVar()
        supplier_dropdown = ttk.Combobox(add_win, textvariable=supplier_var, values=[s[0] for s in suppliers], font=("Arial",12))
        supplier_dropdown.pack(pady=5)
        def save_product():
            name = name_entry.get().strip()
            price = price_entry.get().strip()
            qty = qty_entry.get().strip()
            supplier_name = supplier_var.get().strip()
            if not name or not price or not qty or not supplier_name:
                messagebox.showerror("خطأ", "الرجاء إدخال جميع البيانات")
                return
            products.append((name, price, qty, supplier_name))
            refresh_table()
            add_win.destroy()
        tk.Button(add_win, text="حفظ", command=save_product, **BUTTON_STYLE).pack(pady=20)

    btn_frame = tk.Frame(frame, bg=ROOT_BG)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="➕ إضافة صنف", command=add_product, **SPECIAL_BUTTON_STYLE).grid(row=0,column=0,padx=5)
    tk.Button(btn_frame, text="✏ تعديل صنف", command=lambda: messagebox.showinfo("Info","تعديل صنف"), **EDIT_BUTTON_STYLE).grid(row=0,column=1,padx=5)
    tk.Button(btn_frame, text="🗑 حذف صنف", command=lambda: messagebox.showinfo("Info","حذف صنف"), **DELETE_BUTTON_STYLE).grid(row=0,column=2,padx=5)
    tk.Button(btn_frame, text="🔍 بحث", command=lambda: messagebox.showinfo("Info","بحث عن صنف"), **BUTTON_STYLE).grid(row=0,column=3,padx=5)
    tk.Button(btn_frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).grid(row=0,column=4,padx=5)
    tk.Button(frame, text="حفظ التقرير CSV", command=lambda: save_treeview_as_csv(tree,"تقرير الأصناف"), **BUTTON_STYLE).pack(pady=5)

# ================================
# فاتورة المبيعات
# ================================
def sales_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    global sales_counter
    tk.Label(frame, text="🧾 فاتورة المبيعات", **HEADER_STYLE).pack(pady=20)

    tk.Label(frame, text=f"رقم الفاتورة: {sales_counter}", **LABEL_STYLE).pack(pady=5)
    tk.Label(frame, text="الصنف:", **LABEL_STYLE).pack(pady=5)
    product_var = tk.StringVar()
    product_dropdown = ttk.Combobox(frame, textvariable=product_var, values=[p[0] for p in products], font=("Arial",12))
    product_dropdown.pack(pady=5)

    tk.Label(frame, text="الكمية:", **LABEL_STYLE).pack(pady=5)
    qty_entry = tk.Entry(frame, **ENTRY_STYLE)
    qty_entry.pack(pady=5)

    tk.Label(frame, text="السعر الإجمالي:", **LABEL_STYLE).pack(pady=5)
    total_label = tk.Label(frame, text="0", **LABEL_STYLE)
    total_label.pack(pady=5)

    def update_total(event=None):
        prod_name = product_var.get()
        qty = qty_entry.get()
        price = 0
        for p in products:
            if p[0]==prod_name:
                price = float(p[1])
        try:
            total = float(qty)*price
        except:
            total = 0
        total_label.config(text=str(total))

    qty_entry.bind("<KeyRelease>", update_total)
    product_dropdown.bind("<<ComboboxSelected>>", update_total)

    def save_sale():
        global sales_counter
        prod_name = product_var.get()
        qty = qty_entry.get()
        if not prod_name or not qty:
            messagebox.showerror("خطأ","الرجاء إدخال الصنف والكمية")
            return
        sales.append((sales_counter, prod_name, qty, total_label.cget("text")))
        sales_counter += 1
        messagebox.showinfo("تم","تم حفظ الفاتورة")
        sales_screen(root, frame)

    tk.Button(frame, text="💾 حفظ الفاتورة", command=save_sale, **BUTTON_STYLE).pack(pady=10)
    tk.Button(frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).pack(pady=10)

# ================================
# شاشة المشتريات
# ================================
def purchases_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    global purchase_counter
    tk.Label(frame, text="🛒 شاشة المشتريات", **HEADER_STYLE).pack(pady=20)

    tk.Label(frame, text=f"رقم الشراء: {purchase_counter}", **LABEL_STYLE).pack(pady=5)
    tk.Label(frame, text="الصنف:", **LABEL_STYLE).pack(pady=5)
    product_var = tk.StringVar()
    product_dropdown = ttk.Combobox(frame, textvariable=product_var, values=[p[0] for p in products], font=("Arial",12))
    product_dropdown.pack(pady=5)

    tk.Label(frame, text="الكمية:", **LABEL_STYLE).pack(pady=5)
    qty_entry = tk.Entry(frame, **ENTRY_STYLE)
    qty_entry.pack(pady=5)

    def save_purchase():
        global purchase_counter
        prod_name = product_var.get()
        qty = qty_entry.get()
        if not prod_name or not qty:
            messagebox.showerror("خطأ","الرجاء إدخال الصنف والكمية")
            return
        purchases.append((purchase_counter, prod_name, qty))
        purchase_counter +=1
        messagebox.showinfo("تم","تم حفظ عملية الشراء")
        purchases_screen(root, frame)

    tk.Button(frame, text="💾 حفظ الشراء", command=save_purchase, **BUTTON_STYLE).pack(pady=10)
    tk.Button(frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).pack(pady=10)

# ================================
# شاشة التقارير
# ================================
def reports_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text="📊 شاشة التقارير", **HEADER_STYLE).pack(pady=20)

    notebook = ttk.Notebook(frame)
    notebook.pack(expand=True, fill="both")

    def create_report_tab(title, data, columns):
        tab = tk.Frame(notebook, bg=ROOT_BG)
        notebook.add(tab, text=title)
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        for col in columns:
            tree.heading(col, text=col)
        tree.pack(pady=10, fill="both")
        for d in data:
            tree.insert("", "end", values=d)
        tk.Button(tab, text="حفظ CSV", command=lambda: save_treeview_as_csv(tree,title), **BUTTON_STYLE).pack(pady=5)

    create_report_tab("الأصناف", products, ["اسم الصنف","السعر","الكمية","المورد"])
    create_report_tab("الموردين", suppliers, ["اسم المورد"])
    create_report_tab("العملاء", customers, ["اسم العميل","الرصيد المسموح به"])
    create_report_tab("المبيعات", sales, ["رقم الفاتورة","الصنف","الكمية","الإجمالي"])
    create_report_tab("المشتريات", purchases, ["رقم الشراء","الصنف","الكمية"])
    tk.Button(frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).pack(pady=10)

# ================================
# شاشة الإعدادات
# ================================
def settings_screen(root, parent_frame):
    parent_frame.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text="⚙️ الإعدادات", **HEADER_STYLE).pack(pady=20)

    tree = ttk.Treeview(frame, columns=("username","permissions"), show="headings", height=12)
    tree.heading("username", text="اسم المستخدم")
    tree.heading("permissions", text="الصلاحيات")
    tree.pack(pady=10, fill="x")

    def refresh_table():
        for row in tree.get_children():
            tree.delete(row)
        for u in users:
            tree.insert("", "end", values=(u[0], ",".join(u[2])))
    refresh_table()

    def add_user():
        add_win = tk.Toplevel(root)
        add_win.title("إضافة مستخدم")
        add_win.geometry("400x500")
        add_win.config(bg=ROOT_BG)
        tk.Label(add_win, text="إضافة مستخدم", **HEADER_STYLE).pack(pady=10)
        tk.Label(add_win, text="اسم المستخدم:", **LABEL_STYLE).pack(pady=5)
        username_entry = tk.Entry(add_win, **ENTRY_STYLE)
        username_entry.pack(pady=5)
        tk.Label(add_win, text="كلمة المرور:", **LABEL_STYLE).pack(pady=5)
        password_entry = tk.Entry(add_win, **ENTRY_STYLE)
        password_entry.pack(pady=5)
        perms = ["Products","Suppliers","Customers","Sales","Purchases","Reports","Settings"]
        vars_chk = {}
        tk.Label(add_win, text="الصلاحيات:", **LABEL_STYLE).pack(pady=5)
        for p in perms:
            var = tk.IntVar()
            chk = tk.Checkbutton(add_win, text=p, variable=var, bg=ROOT_BG, font=("Arial",12))
            chk.pack(anchor="w")
            vars_chk[p] = var

        def save_user():
            username = username_entry.get().strip()
            password = password_entry.get().strip()
            selected_perms = [k for k,v in vars_chk.items() if v.get()==1]
            if not username or not password:
                messagebox.showerror("خطأ","الرجاء إدخال اسم المستخدم وكلمة المرور")
                return
            users.append((username,password,selected_perms))
            refresh_table()
            add_win.destroy()
        tk.Button(add_win, text="حفظ", command=save_user, **BUTTON_STYLE).pack(pady=20)

    btn_frame = tk.Frame(frame, bg=ROOT_BG)
    btn_frame.pack(pady=10)
    tk.Button(btn_frame, text="➕ إضافة مستخدم", command=add_user, **SPECIAL_BUTTON_STYLE).grid(row=0,column=0,padx=5)
    tk.Button(btn_frame, text="✏ تعديل", command=lambda: messagebox.showinfo("Info","تعديل مستخدم"), **EDIT_BUTTON_STYLE).grid(row=0,column=1,padx=5)
    tk.Button(btn_frame, text="🗑 حذف", command=lambda: messagebox.showinfo("Info","حذف مستخدم"), **DELETE_BUTTON_STYLE).grid(row=0,column=2,padx=5)
    tk.Button(btn_frame, text="⬅ رجوع", command=lambda: main_app(root, users[0][2]), **BUTTON_STYLE).grid(row=0,column=3,padx=5)
    tk.Button(frame, text="خروج من البرنامج", command=root.destroy, **DELETE_BUTTON_STYLE).pack(pady=10)

# ================================
# التطبيق الرئيسي
# ================================
def main_app(root, permissions):
    for widget in root.winfo_children():
        widget.destroy()
    frame = tk.Frame(root, bg=ROOT_BG)
    frame.pack(expand=True, fill="both")
    tk.Label(frame, text="🏠 القائمة الرئيسية", **HEADER_STYLE).pack(pady=20)

    btns = []
    if "Products" in permissions:
        btns.append(("📦 الأصناف", lambda: products_screen(root, frame)))
    if "Suppliers" in permissions:
        btns.append(("🏢 الموردين", lambda: suppliers_screen(root, frame)))
    if "Customers" in permissions:
        btns.append(("👥 العملاء", lambda: customers_screen(root, frame)))
    if "Sales" in permissions:
        btns.append(("🧾 المبيعات", lambda: sales_screen(root, frame)))
    if "Purchases" in permissions:
        btns.append(("🛒 المشتريات", lambda: purchases_screen(root, frame)))
    if "Reports" in permissions:
        btns.append(("📊 التقارير", lambda: reports_screen(root, frame)))
    if "Settings" in permissions:
        btns.append(("⚙️ الإعدادات", lambda: settings_screen(root, frame)))

    for i,(txt,cmd) in enumerate(btns):
        tk.Button(frame, text=txt, command=cmd, **SPECIAL_BUTTON_STYLE).pack(pady=5)

    tk.Button(frame, text="🚪 خروج", command=root.destroy, **DELETE_BUTTON_STYLE).pack(pady=20)

# ================================
# تشغيل البرنامج
# ================================
if __name__ == "__main__":
    root = tk.Tk()
    root.title("برنامج زوما للمبيعات")
    root.geometry("900x700")
    root.config(bg=ROOT_BG)
    login_screen(root)
    root.mainloop()
