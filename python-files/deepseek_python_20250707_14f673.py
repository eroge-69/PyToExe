import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import sqlite3
from datetime import datetime

class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة المخازن")
        self.root.geometry("1000x700")
        
        # إنشاء قاعدة بيانات SQLite
        self.conn = sqlite3.connect('inventory.db')
        self.create_tables()
        
        # إنشاء واجهة المستخدم
        self.create_widgets()
        
        # تحميل البيانات عند التشغيل
        self.load_data()
    
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                last_updated TEXT NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                type TEXT NOT NULL,  # 'in' or 'out'
                quantity INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        self.conn.commit()
    
    def create_widgets(self):
        # إطار للأزرار الرئيسية
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # أزرار الأصناف
        categories = ["قهوة ولوازمها", "أدوات مكتبية", "مواد التجميل", "حلويات", "مشروبات"]
        for i, category in enumerate(categories):
            btn = ttk.Button(main_frame, text=category, 
                            command=lambda c=category: self.filter_by_category(c))
            btn.grid(row=0, column=i, padx=5, pady=5, sticky='ew')
        
        # أزرار التحكم
        control_buttons = [
            ("إضافة", self.add_product),
            ("تعديل", self.edit_product),
            ("حذف", self.delete_product),
            ("الباقي في المخزن", self.show_inventory),
            ("دخل السلع", self.stock_in),
            ("خروج السلع", self.stock_out),
            ("تصدير إلى Excel", self.export_to_excel)
        ]
        
        for i, (text, command) in enumerate(control_buttons):
            btn = ttk.Button(main_frame, text=text, command=command)
            btn.grid(row=1, column=i, padx=5, pady=5, sticky='ew')
        
        # شجرة لعرض البيانات
        self.tree = ttk.Treeview(main_frame, columns=('ID', 'Name', 'Category', 'Quantity', 'Price'), show='headings')
        self.tree.grid(row=2, column=0, columnspan=7, pady=10, sticky='nsew')
        
        # عناوين الأعمدة
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='الاسم')
        self.tree.heading('Category', text='الفئة')
        self.tree.heading('Quantity', text='الكمية')
        self.tree.heading('Price', text='السعر')
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=2, column=7, sticky='ns')
        
        # جعل العناصر قابلة للتوسيع
        for i in range(8):
            main_frame.columnconfigure(i, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
    def load_data(self, category=None):
        cursor = self.conn.cursor()
        
        if category:
            cursor.execute("SELECT * FROM products WHERE category=?", (category,))
        else:
            cursor.execute("SELECT * FROM products")
        
        rows = cursor.fetchall()
        
        # مسح البيانات الحالية
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # إضافة البيانات الجديدة
        for row in rows:
            self.tree.insert('', tk.END, values=row)
    
    def filter_by_category(self, category):
        self.load_data(category)
    
    def add_product(self):
        self.product_dialog("إضافة منتج جديد", self.save_product)
    
    def edit_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "يرجى اختيار منتج للتعديل")
            return
        
        item = self.tree.item(selected_item[0])
        product_id = item['values'][0]
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = cursor.fetchone()
        
        self.product_dialog("تعديل المنتج", self.update_product, product)
    
    def delete_product(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "يرجى اختيار منتج للحذف")
            return
        
        if messagebox.askyesno("تأكيد", "هل أنت متأكد من حذف هذا المنتج؟"):
            item = self.tree.item(selected_item[0])
            product_id = item['values'][0]
            
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
            cursor.execute("DELETE FROM transactions WHERE product_id=?", (product_id,))
            self.conn.commit()
            
            self.load_data()
            messagebox.showinfo("نجاح", "تم حذف المنتج بنجاح")
    
    def show_inventory(self):
        # يمكن إضافة ميزات إضافية لعرض تقارير المخزون
        messagebox.showinfo("الباقي في المخزن", "عرض تقرير بالكميات المتبقية في المخزن")
    
    def stock_in(self):
        self.transaction_dialog("إدخال سلع", "in")
    
    def stock_out(self):
        self.transaction_dialog("إخراج سلع", "out")
    
    def export_to_excel(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products")
        rows = cursor.fetchall()
        
        df = pd.DataFrame(rows, columns=['ID', 'Name', 'Category', 'Quantity', 'Price', 'Last Updated'])
        df.to_excel("inventory_report.xlsx", index=False)
        messagebox.showinfo("نجاح", "تم تصدير البيانات إلى ملف Excel")
    
    def product_dialog(self, title, command, product=None):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="اسم المنتج:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        name_entry = tk.Entry(dialog)
        name_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(dialog, text="الفئة:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
        category_combobox = ttk.Combobox(dialog, values=["قهوة ولوازمها", "أدوات مكتبية", "مواد التجميل", "حلويات", "مشروبات"])
        category_combobox.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(dialog, text="الكمية:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        quantity_entry = tk.Entry(dialog)
        quantity_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        
        tk.Label(dialog, text="السعر:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        price_entry = tk.Entry(dialog)
        price_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')
        
        if product:
            name_entry.insert(0, product[1])
            category_combobox.set(product[2])
            quantity_entry.insert(0, product[3])
            price_entry.insert(0, product[4])
        
        def execute_command():
            name = name_entry.get()
            category = category_combobox.get()
            quantity = quantity_entry.get()
            price = price_entry.get()
            
            if not all([name, category, quantity, price]):
                messagebox.showwarning("تحذير", "جميع الحقول مطلوبة")
                return
            
            try:
                quantity = int(quantity)
                price = float(price)
            except ValueError:
                messagebox.showwarning("تحذير", "الكمية والسعر يجب أن يكونا أرقامًا")
                return
            
            if product:
                command(product[0], name, category, quantity, price)
            else:
                command(name, category, quantity, price)
            
            dialog.destroy()
        
        save_btn = ttk.Button(dialog, text="حفظ", command=execute_command)
        save_btn.grid(row=4, column=0, columnspan=2, pady=10)
    
    def transaction_dialog(self, title, transaction_type):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("تحذير", "يرجى اختيار منتج")
            return
        
        item = self.tree.item(selected_item[0])
        product_id = item['values'][0]
        product_name = item['values'][1]
        current_quantity = item['values'][3]
        
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("300x200")
        
        tk.Label(dialog, text=f"المنتج: {product_name}").pack(pady=5)
        tk.Label(dialog, text=f"الكمية الحالية: {current_quantity}").pack(pady=5)
        tk.Label(dialog, text="الكمية:").pack(pady=5)
        
        quantity_entry = tk.Entry(dialog)
        quantity_entry.pack(pady=5)
        
        def execute_transaction():
            try:
                quantity = int(quantity_entry.get())
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning("تحذير", "يرجى إدخال كمية صحيحة")
                return
            
            cursor = self.conn.cursor()
            
            if transaction_type == "in":
                new_quantity = current_quantity + quantity
            else:
                if quantity > current_quantity:
                    messagebox.showwarning("تحذير", "الكمية المطلوبة غير متوفرة")
                    return
                new_quantity = current_quantity - quantity
            
            # تحديث كمية المنتج
            cursor.execute("UPDATE products SET quantity=?, last_updated=? WHERE id=?", 
                           (new_quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))
            
            # تسجيل العملية
            cursor.execute("INSERT INTO transactions (product_id, type, quantity, date) VALUES (?, ?, ?, ?)",
                         (product_id, transaction_type, quantity, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            
            self.conn.commit()
            self.load_data()
            dialog.destroy()
            messagebox.showinfo("نجاح", "تمت العملية بنجاح")
        
        save_btn = ttk.Button(dialog, text="حفظ", command=execute_transaction)
        save_btn.pack(pady=10)
    
    def save_product(self, name, category, quantity, price):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO products (name, category, quantity, price, last_updated) VALUES (?, ?, ?, ?, ?)",
                      (name, category, quantity, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        self.conn.commit()
        self.load_data()
        messagebox.showinfo("نجاح", "تم إضافة المنتج بنجاح")
    
    def update_product(self, product_id, name, category, quantity, price):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE products SET name=?, category=?, quantity=?, price=?, last_updated=? WHERE id=?",
                      (name, category, quantity, price, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))
        self.conn.commit()
        self.load_data()
        messagebox.showinfo("نجاح", "تم تحديث المنتج بنجاح")

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()