# main.py - برنامج كامل لإدارة محل تليفونات
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

# إنشاء وتوصيل قاعدة البيانات
def create_db():
    conn = sqlite3.connect('phone_shop.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS products (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 price REAL NOT NULL,
                 quantity INTEGER NOT NULL,
                 category TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 phone TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 product_id INTEGER,
                 customer_id INTEGER,
                 quantity INTEGER,
                 total REAL,
                 date TEXT,
                 payment_method TEXT)''')
    
    conn.commit()
    conn.close()

# واجهة المستخدم الرئيسية
class PhoneShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة محل تليفونات - الإصدار 1.0")
        self.root.geometry("1000x650")
        create_db()
        self.setup_ui()

    def setup_ui(self):
        # النافذة الرئيسية مع تبويبات
        notebook = ttk.Notebook(self.root)
        
        # تبويب المنتجات
        products_frame = ttk.Frame(notebook)
        self.setup_products_tab(products_frame)
        
        # تبويب العملاء
        customers_frame = ttk.Frame(notebook)
        self.setup_customers_tab(customers_frame)
        
        # تبويب المبيعات
        sales_frame = ttk.Frame(notebook)
        self.setup_sales_tab(sales_frame)
        
        # إضافة التبويبات
        notebook.add(products_frame, text="المنتجات")
        notebook.add(customers_frame, text="العملاء")
        notebook.add(sales_frame, text="المبيعات")
        notebook.pack(expand=True, fill='both')

    # تبويب المنتجات
    def setup_products_tab(self, frame):
        # حقول الإدخال
        tk.Label(frame, text="اسم المنتج:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.product_name = tk.Entry(frame, width=30)
        self.product_name.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(frame, text="السعر:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.product_price = tk.Entry(frame, width=30)
        self.product_price.grid(row=1, column=1, padx=10, pady=5)
        
        tk.Label(frame, text="الكمية:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.product_quantity = tk.Entry(frame, width=30)
        self.product_quantity.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(frame, text="الصنف:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.product_category = ttk.Combobox(frame, values=['موبايل', 'شاحن', 'سماعات', 'إكسسوارات'], width=27)
        self.product_category.grid(row=3, column=1, padx=10, pady=5)
        
        # أزرار التحكم
        tk.Button(frame, text="إضافة منتج", command=self.add_product, bg='#4CAF50', fg='white').grid(row=4, column=0, columnspan=2, pady=10)
        
        # جدول عرض المنتجات
        columns = ("id", "name", "price", "quantity", "category")
        self.products_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        self.products_tree.grid(row=5, column=0, columnspan=2, padx=10)
        
        # عناوين الأعمدة
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="الاسم")
        self.products_tree.heading("price", text="السعر")
        self.products_tree.heading("quantity", text="الكمية")
        self.products_tree.heading("category", text="الصنف")
        
        # عرض البيانات
        self.load_products()

    # دوال المنتجات
    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        quantity = self.product_quantity.get()
        category = self.product_category.get()
        
        if not all([name, price, quantity, category]):
            messagebox.showerror("خطأ", "جميع الحقول مطلوبة!")
            return
            
        try:
            conn = sqlite3.connect('phone_shop.db')
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, quantity, category) VALUES (?, ?, ?, ?)",
                     (name, float(price), int(quantity), category))
            conn.commit()
            messagebox.showinfo("نجاح", "تم إضافة المنتج بنجاح!")
            self.load_products()
            # مسح الحقول بعد الإضافة
            self.product_name.delete(0, tk.END)
            self.product_price.delete(0, tk.END)
            self.product_quantity.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("خطأ", "تأكد من صحة البيانات المدخلة!")
        finally:
            conn.close()

    def load_products(self):
        # مسح البيانات القديمة
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # جلب البيانات من قاعدة البيانات
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        products = c.fetchall()
        conn.close()
        
        # إضافة البيانات للجدول
        for product in products:
            self.products_tree.insert('', tk.END, values=product)

    # باقي التبويبات (العملاء والمبيعات)
    def setup_customers_tab(self, frame):
        # حقول إدخال بيانات العميل
        tk.Label(frame, text="اسم العميل:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.customer_name = tk.Entry(frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=10, pady=5)
        
        tk.Label(frame, text="رقم الهاتف:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.customer_phone = tk.Entry(frame, width=30)
        self.customer_phone.grid(row=1, column=1, padx=10, pady=5)
        
        # أزرار التحكم
        tk.Button(frame, text="إضافة عميل", command=self.add_customer, bg='#2196F3', fg='white').grid(row=2, column=0, columnspan=2, pady=10)
        
        # جدول عرض العملاء
        columns = ("id", "name", "phone")
        self.customers_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        self.customers_tree.grid(row=3, column=0, columnspan=2, padx=10)
        
        # عناوين الأعمدة
        self.customers_tree.heading("id", text="ID")
        self.customers_tree.heading("name", text="الاسم")
        self.customers_tree.heading("phone", text="الهاتف")
        
        # عرض البيانات
        self.load_customers()

    def add_customer(self):
        name = self.customer_name.get()
        phone = self.customer_phone.get()
        
        if not name:
            messagebox.showerror("خطأ", "اسم العميل مطلوب!")
            return
            
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("INSERT INTO customers (name, phone) VALUES (?, ?)", (name, phone))
        conn.commit()
        messagebox.showinfo("نجاح", "تم إضافة العميل بنجاح!")
        self.load_customers()
        # مسح الحقول بعد الإضافة
        self.customer_name.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
        conn.close()

    def load_customers(self):
        # مسح البيانات القديمة
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # جلب البيانات من قاعدة البيانات
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM customers")
        customers = c.fetchall()
        conn.close()
        
        # إضافة البيانات للجدول
        for customer in customers:
            self.customers_tree.insert('', tk.END, values=customer)

    def setup_sales_tab(self, frame):
        # حقول إدخال بيانات البيع
        tk.Label(frame, text="المنتج:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.sale_product = ttk.Combobox(frame, width=27)
        self.sale_product.grid(row=0, column=1, padx=10, pady=5)
        self.update_products_combobox()
        
        tk.Label(frame, text="العميل:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.sale_customer = ttk.Combobox(frame, width=27)
        self.sale_customer.grid(row=1, column=1, padx=10, pady=5)
        self.update_customers_combobox()
        
        tk.Label(frame, text="الكمية:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.sale_quantity = tk.Entry(frame, width=30)
        self.sale_quantity.grid(row=2, column=1, padx=10, pady=5)
        
        tk.Label(frame, text="طريقة الدفع:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.payment_method = ttk.Combobox(frame, values=['نقدي', 'آجل'], width=27)
        self.payment_method.grid(row=3, column=1, padx=10, pady=5)
        self.payment_method.current(0)
        
        # أزرار التحكم
        tk.Button(frame, text="تسجيل بيع", command=self.add_sale, bg='#FF5722', fg='white').grid(row=4, column=0, columnspan=2, pady=10)
        
        # جدول عرض المبيعات
        columns = ("id", "product", "customer", "quantity", "total", "date", "payment")
        self.sales_tree = ttk.Treeview(frame, columns=columns, show='headings', height=15)
        self.sales_tree.grid(row=5, column=0, columnspan=2, padx=10)
        
        # عناوين الأعمدة
        self.sales_tree.heading("id", text="ID")
        self.sales_tree.heading("product", text="المنتج")
        self.sales_tree.heading("customer", text="العميل")
        self.sales_tree.heading("quantity", text="الكمية")
        self.sales_tree.heading("total", text="الإجمالي")
        self.sales_tree.heading("date", text="التاريخ")
        self.sales_tree.heading("payment", text="طريقة الدفع")
        
        # عرض البيانات
        self.load_sales()

    def update_products_combobox(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM products")
        products = c.fetchall()
        conn.close()
        self.sale_product['values'] = [f"{p[0]} - {p[1]}" for p in products]

    def update_customers_combobox(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM customers")
        customers = c.fetchall()
        conn.close()
        self.sale_customer['values'] = [f"{c[0]} - {c[1]}" for c in customers]

    def add_sale(self):
        try:
            product_id = int(self.sale_product.get().split(' - ')[0])
            customer_id = int(self.sale_customer.get().split(' - ')[0])
            quantity = int(self.sale_quantity.get())
            payment = self.payment_method.get()
            date = datetime.now().strftime("%Y-%m-%d")
            
            # جلب سعر المنتج
            conn = sqlite3.connect('phone_shop.db')
            c = conn.cursor()
            c.execute("SELECT price, quantity FROM products WHERE id=?", (product_id,))
            product = c.fetchone()
            
            if not product:
                messagebox.showerror("خطأ", "المنتج غير موجود!")
                return
                
            price, available_quantity = product
            total = price * quantity
            
            if quantity > available_quantity:
                messagebox.showerror("خطأ", "الكمية غير متوفرة في المخزن!")
                return
                
            # تسجيل البيع
            c.execute("INSERT INTO sales (product_id, customer_id, quantity, total, date, payment_method) VALUES (?, ?, ?, ?, ?, ?)",
                     (product_id, customer_id, quantity, total, date, payment))
            
            # تحديث كمية المنتج
            new_quantity = available_quantity - quantity
            c.execute("UPDATE products SET quantity=? WHERE id=?", (new_quantity, product_id))
            
            conn.commit()
            messagebox.showinfo("نجاح", f"تم تسجيل البيع بنجاح! الإجمالي: {total} ج.م")
            self.load_sales()
            self.update_products_combobox()
            self.sale_quantity.delete(0, tk.END)
        except (ValueError, IndexError):
            messagebox.showerror("خطأ", "تأكد من صحة البيانات المدخلة!")
        finally:
            conn.close()

    def load_sales(self):
        # مسح البيانات القديمة
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
        
        # جلب البيانات من قاعدة البيانات
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute('''SELECT s.id, p.name, c.name, s.quantity, s.total, s.date, s.payment_method
                     FROM sales s
                     JOIN products p ON s.product_id = p.id
                     JOIN customers c ON s.customer_id = c.id''')
        sales = c.fetchall()
        conn.close()
        
        # إضافة البيانات للجدول
        for sale in sales:
            self.sales_tree.insert('', tk.END, values=sale)

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneShopApp(root)
    root.mainloop()
