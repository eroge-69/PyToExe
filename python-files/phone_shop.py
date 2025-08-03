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

class PhoneShopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة محل تليفونات")
        self.root.geometry("1000x700")
        create_db()
        self.setup_ui()
    
    def setup_ui(self):
        self.notebook = ttk.Notebook(self.root)
        
        # تبويب المنتجات
        self.products_frame = ttk.Frame(self.notebook)
        self.setup_products_tab()
        
        # تبويب العملاء
        self.customers_frame = ttk.Frame(self.notebook)
        self.setup_customers_tab()
        
        # تبويب المبيعات
        self.sales_frame = ttk.Frame(self.notebook)
        self.setup_sales_tab()
        
        # تبويب التقارير
        self.reports_frame = ttk.Frame(self.notebook)
        self.setup_reports_tab()
        
        self.notebook.add(self.products_frame, text="المنتجات")
        self.notebook.add(self.customers_frame, text="العملاء")
        self.notebook.add(self.sales_frame, text="المبيعات")
        self.notebook.add(self.reports_frame, text="التقارير")
        self.notebook.pack(expand=True, fill='both')
    
    def setup_products_tab(self):
        # حقول الإدخال
        tk.Label(self.products_frame, text="اسم المنتج:").grid(row=0, column=0, padx=5, pady=5)
        self.product_name = tk.Entry(self.products_frame, width=30)
        self.product_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.products_frame, text="السعر:").grid(row=1, column=0, padx=5, pady=5)
        self.product_price = tk.Entry(self.products_frame, width=30)
        self.product_price.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(self.products_frame, text="الكمية:").grid(row=2, column=0, padx=5, pady=5)
        self.product_quantity = tk.Entry(self.products_frame, width=30)
        self.product_quantity.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self.products_frame, text="الصنف:").grid(row=3, column=0, padx=5, pady=5)
        self.product_category = ttk.Combobox(self.products_frame, 
                                           values=['موبايل', 'شاحن', 'سماعات', 'إكسسوارات'])
        self.product_category.grid(row=3, column=1, padx=5, pady=5)
        self.product_category.current(0)
        
        # أزرار التحكم
        tk.Button(self.products_frame, text="إضافة منتج", command=self.add_product, 
                 bg='green', fg='white').grid(row=4, column=0, columnspan=2, pady=10)
        
        # جدول المنتجات
        columns = ("id", "name", "price", "quantity", "category")
        self.products_tree = ttk.Treeview(self.products_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.products_tree.heading(col, text=col)
        self.products_tree.grid(row=5, column=0, columnspan=2)
        
        self.load_products()
    
    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        quantity = self.product_quantity.get()
        category = self.product_category.get()
        
        if not all([name, price, quantity]):
            messagebox.showerror("خطأ", "الرجاء ملء جميع الحقول")
            return
            
        try:
            conn = sqlite3.connect('phone_shop.db')
            c = conn.cursor()
            c.execute("INSERT INTO products (name, price, quantity, category) VALUES (?, ?, ?, ?)",
                     (name, float(price), int(quantity), category))
            conn.commit()
            messagebox.showinfo("نجاح", "تم إضافة المنتج بنجاح!")
            self.load_products()
            self.clear_product_fields()
        except ValueError:
            messagebox.showerror("خطأ", "رقم غير صالح في السعر أو الكمية")
        finally:
            conn.close()
    
    def clear_product_fields(self):
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_quantity.delete(0, tk.END)
    
    def load_products(self):
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
            
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM products")
        rows = c.fetchall()
        
        for row in rows:
            self.products_tree.insert('', tk.END, values=row)
        
        conn.close()
    
    def setup_customers_tab(self):
        # حقول الإدخال للعملاء
        tk.Label(self.customers_frame, text="اسم العميل:").grid(row=0, column=0, padx=5, pady=5)
        self.customer_name = tk.Entry(self.customers_frame, width=30)
        self.customer_name.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(self.customers_frame, text="رقم الهاتف:").grid(row=1, column=0, padx=5, pady=5)
        self.customer_phone = tk.Entry(self.customers_frame, width=30)
        self.customer_phone.grid(row=1, column=1, padx=5, pady=5)
        
        # أزرار التحكم
        tk.Button(self.customers_frame, text="إضافة عميل", command=self.add_customer,
                 bg='blue', fg='white').grid(row=2, column=0, columnspan=2, pady=10)
        
        # جدول العملاء
        columns = ("id", "name", "phone")
        self.customers_tree = ttk.Treeview(self.customers_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.customers_tree.heading(col, text=col)
        self.customers_tree.grid(row=3, column=0, columnspan=2)
        
        self.load_customers()
    
    def add_customer(self):
        name = self.customer_name.get()
        phone = self.customer_phone.get()
        
        if not name:
            messagebox.showerror("خطأ", "اسم العميل مطلوب")
            return
            
        try:
            conn = sqlite3.connect('phone_shop.db')
            c = conn.cursor()
            c.execute("INSERT INTO customers (name, phone) VALUES (?, ?)",
                     (name, phone))
            conn.commit()
            messagebox.showinfo("نجاح", "تم إضافة العميل بنجاح!")
            self.load_customers()
            self.clear_customer_fields()
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
        finally:
            conn.close()
    
    def clear_customer_fields(self):
        self.customer_name.delete(0, tk.END)
        self.customer_phone.delete(0, tk.END)
    
    def load_customers(self):
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
            
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT * FROM customers")
        rows = c.fetchall()
        
        for row in rows:
            self.customers_tree.insert('', tk.END, values=row)
        
        conn.close()
    
    def setup_sales_tab(self):
        # حقول الإدخال للمبيعات
        tk.Label(self.sales_frame, text="المنتج:").grid(row=0, column=0, padx=5, pady=5)
        self.sale_product = ttk.Combobox(self.sales_frame)
        self.sale_product.grid(row=0, column=1, padx=5, pady=5)
        self.update_product_combobox()
        
        tk.Label(self.sales_frame, text="العميل:").grid(row=1, column=0, padx=5, pady=5)
        self.sale_customer = ttk.Combobox(self.sales_frame)
        self.sale_customer.grid(row=1, column=1, padx=5, pady=5)
        self.update_customer_combobox()
        
        tk.Label(self.sales_frame, text="الكمية:").grid(row=2, column=0, padx=5, pady=5)
        self.sale_quantity = tk.Entry(self.sales_frame)
        self.sale_quantity.grid(row=2, column=1, padx=5, pady=5)
        
        tk.Label(self.sales_frame, text="طريقة الدفع:").grid(row=3, column=0, padx=5, pady=5)
        self.payment_method = ttk.Combobox(self.sales_frame, values=['نقدي', 'آجل'])
        self.payment_method.grid(row=3, column=1, padx=5, pady=5)
        self.payment_method.current(0)
        
        # أزرار التحكم
        tk.Button(self.sales_frame, text="تسجيل عملية بيع", command=self.add_sale,
                 bg='darkorange', fg='white').grid(row=4, column=0, columnspan=2, pady=10)
        
        # جدول المبيعات
        columns = ("id", "product", "customer", "quantity", "total", "date", "payment")
        self.sales_tree = ttk.Treeview(self.sales_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.sales_tree.heading(col, text=col)
        self.sales_tree.grid(row=5, column=0, columnspan=2)
        
        self.load_sales()
    
    def update_product_combobox(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM products WHERE quantity > 0")
        products = c.fetchall()
        self.sale_product['values'] = [f"{p[0]} - {p[1]}" for p in products]
        conn.close()
    
    def update_customer_combobox(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT id, name FROM customers")
        customers = c.fetchall()
        self.sale_customer['values'] = [f"{c[0]} - {c[1]}" for c in customers]
        conn.close()
    
    def add_sale(self):
        if not all([self.sale_product.get(), self.sale_customer.get(), self.sale_quantity.get()]):
            messagebox.showerror("خطأ", "جميع الحقول مطلوبة")
            return
            
        try:
            product_id = int(self.sale_product.get().split(' - ')[0])
            customer_id = int(self.sale_customer.get().split(' - ')[0])
            quantity = int(self.sale_quantity.get())
            payment = self.payment_method.get()
            
            conn = sqlite3.connect('phone_shop.db')
            c = conn.cursor()
            
            # الحصول على سعر المنتج والكمية المتاحة
            c.execute("SELECT price, quantity FROM products WHERE id = ?", (product_id,))
            product = c.fetchone()
            
            if product:
                price, available_quantity = product
                
                if quantity > available_quantity:
                    messagebox.showerror("خطأ", "الكمية المطلوبة غير متوفرة في المخزن")
                    return
                    
                total = price * quantity
                date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # تسجيل عملية البيع
                c.execute("""INSERT INTO sales (product_id, customer_id, quantity, total, date, payment_method)
                          VALUES (?, ?, ?, ?, ?, ?)""",
                          (product_id, customer_id, quantity, total, date, payment))
                
                # تحديث كمية المنتج
                new_quantity = available_quantity - quantity
                c.execute("UPDATE products SET quantity = ? WHERE id = ?", (new_quantity, product_id))
                
                conn.commit()
                messagebox.showinfo("نجاح", f"تمت عملية البيع بنجاح!\nالإجمالي: {total} جنيه")
                self.load_sales()
                self.update_product_combobox()
                self.sale_quantity.delete(0, tk.END)
            else:
                messagebox.showerror("خطأ", "المنتج غير موجود")
                
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال قيم صحيحة")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
        finally:
            conn.close()
    
    def load_sales(self):
        for item in self.sales_tree.get_children():
            self.sales_tree.delete(item)
            
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("""SELECT s.id, p.name, c.name, s.quantity, s.total, s.date, s.payment_method
                     FROM sales s
                     JOIN products p ON s.product_id = p.id
                     JOIN customers c ON s.customer_id = c.id""")
        rows = c.fetchall()
        
        for row in rows:
            self.sales_tree.insert('', tk.END, values=row)
        
        conn.close()
    
    def setup_reports_tab(self):
        # عناصر تبويب التقارير
        tk.Label(self.reports_frame, text="التقارير والأحصاءات", font=('Arial', 14)).pack(pady=10)
        
        tk.Button(self.reports_frame, text="عرض إجمالي المبيعات", command=self.show_total_sales,
                 width=20).pack(pady=5)
        
        tk.Button(self.reports_frame, text="عرض المنتجات المتاحة", command=self.show_available_products,
                 width=20).pack(pady=5)
        
        tk.Button(self.reports_frame, text="عرض العملاء", command=self.show_customers_list,
                 width=20).pack(pady=5)
        
        self.report_text = tk.Text(self.reports_frame, height=15)
        self.report_text.pack(fill='both', expand=True)
    
    def show_total_sales(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT SUM(total) FROM sales")
        total = c.fetchone()[0] or 0
        conn.close()
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, f"إجمالي المبيعات: {total} جنيهاً\n")
    
    def show_available_products(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT name, quantity FROM products WHERE quantity > 0 ORDER BY quantity DESC")
        products = c.fetchall()
        conn.close()
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "المنتجات المتاحة في المخزن:\n\n")
        for product in products:
            self.report_text.insert(tk.END, f"{product[0]}: {product[1]} قطعة\n")
    
    def show_customers_list(self):
        conn = sqlite3.connect('phone_shop.db')
        c = conn.cursor()
        c.execute("SELECT name, phone FROM customers ORDER BY name")
        customers = c.fetchall()
        conn.close()
        
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, "قائمة العملاء:\n\n")
        for customer in customers:
            phone = customer[1] if customer[1] else "غير مسجل"
            self.report_text.insert(tk.END, f"{customer[0]} - الهاتف: {phone}\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhoneShopApp(root)
    root.mainloop()
