import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import os

class InventoryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة المخازن - الأصناف")
        self.root.geometry("1000x700")
        
        # قوائم البيانات
        self.categories = ["مواد التجميل", "قهوة ولوازمها", "أدوات مكتبية", "مشروبات", "حلويات"]
        self.products = []
        self.transactions = []
        
        # إنشاء ملفات البيانات إذا لم تكن موجودة
        self.create_data_files()
        
        # تحميل البيانات
        self.load_data()
        
        # واجهة المستخدم
        self.create_ui()
        
        # جدول المنتجات
        self.create_products_table()
        
        # جدول الحركات
        self.create_transactions_table()
        
        # تنبيهات نفاذ السلع
        self.check_low_stock()
    
    def create_data_files(self):
        if not os.path.exists("products.csv"):
            df = pd.DataFrame(columns=["ID", "Name", "Category", "Price", "Quantity", "Min_Stock"])
            df.to_csv("products.csv", index=False, encoding='utf-8')
        
        if not os.path.exists("transactions.csv"):
            df = pd.DataFrame(columns=["ID", "Product_ID", "Type", "Quantity", "Date", "Notes"])
            df.to_csv("transactions.csv", index=False, encoding='utf-8')
    
    def load_data(self):
        try:
            self.products = pd.read_csv("products.csv", encoding='utf-8').to_dict('records')
            self.transactions = pd.read_csv("transactions.csv", encoding='utf-8').to_dict('records')
        except:
            self.products = []
            self.transactions = []
    
    def save_data(self):
        pd.DataFrame(self.products).to_csv("products.csv", index=False, encoding='utf-8')
        pd.DataFrame(self.transactions).to_csv("transactions.csv", index=False, encoding='utf-8')
    
    def create_ui(self):
        # إطار التحكم
        control_frame = ttk.LabelFrame(self.root, text="التحكم بالأصناف")
        control_frame.pack(pady=10, padx=10, fill="x")
        
        # أزرار التحكم
        ttk.Button(control_frame, text="إضافة صنف", command=self.add_product).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="تعديل صنف", command=self.edit_product).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="حذف صنف", command=self.delete_product).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="الباقي في المخزن", command=self.show_stock).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="تصدير إلى Excel", command=self.export_to_excel).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="دخول السلع", command=self.product_in).pack(side=tk.RIGHT, padx=5)
        ttk.Button(control_frame, text="خروج السلع", command=self.product_out).pack(side=tk.RIGHT, padx=5)
    
    def create_products_table(self):
        # إطار جدول المنتجات
        table_frame = ttk.LabelFrame(self.root, text="قائمة الأصناف")
        table_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # شريط التمرير
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        scroll_y.pack(side=tk.RIGHT, fill="y")
        
        # الجدول
        self.products_table = ttk.Treeview(table_frame, columns=("ID", "Name", "Category", "Price", "Quantity", "Min_Stock"), 
                                          yscrollcommand=scroll_y.set)
        self.products_table.pack(fill="both", expand=True)
        
        # عناوين الأعمدة
        self.products_table.heading("ID", text="رقم الصنف")
        self.products_table.heading("Name", text="اسم الصنف")
        self.products_table.heading("Category", text="الفئة")
        self.products_table.heading("Price", text="السعر")
        self.products_table.heading("Quantity", text="الكمية")
        self.products_table.heading("Min_Stock", text="حد النفاذ")
        
        # إخفاء العمود الأول (فارغ)
        self.products_table.column("#0", width=0, stretch=tk.NO)
        
        # تكبير حجم الأعمدة
        self.products_table.column("ID", width=80)
        self.products_table.column("Name", width=200)
        self.products_table.column("Category", width=150)
        self.products_table.column("Price", width=100)
        self.products_table.column("Quantity", width=80)
        self.products_table.column("Min_Stock", width=80)
        
        scroll_y.config(command=self.products_table.yview)
        
        # تعبئة الجدول بالبيانات
        self.refresh_products_table()
    
    def create_transactions_table(self):
        # إطار جدول الحركات
        trans_frame = ttk.LabelFrame(self.root, text="سجل الحركات")
        trans_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # شريط التمرير
        scroll_y = ttk.Scrollbar(trans_frame, orient="vertical")
        scroll_y.pack(side=tk.RIGHT, fill="y")
        
        # الجدول
        self.trans_table = ttk.Treeview(trans_frame, columns=("ID", "Product_ID", "Product_Name", "Type", "Quantity", "Date", "Notes"), 
                                      yscrollcommand=scroll_y.set)
        self.trans_table.pack(fill="both", expand=True)
        
        # عناوين الأعمدة
        self.trans_table.heading("ID", text="رقم العملية")
        self.trans_table.heading("Product_ID", text="رقم الصنف")
        self.trans_table.heading("Product_Name", text="اسم الصنف")
        self.trans_table.heading("Type", text="نوع العملية")
        self.trans_table.heading("Quantity", text="الكمية")
        self.trans_table.heading("Date", text="التاريخ")
        self.trans_table.heading("Notes", text="ملاحظات")
        
        # إخفاء العمود الأول (فارغ)
        self.trans_table.column("#0", width=0, stretch=tk.NO)
        
        # تكبير حجم الأعمدة
        self.trans_table.column("ID", width=80)
        self.trans_table.column("Product_ID", width=80)
        self.trans_table.column("Product_Name", width=150)
        self.trans_table.column("Type", width=100)
        self.trans_table.column("Quantity", width=80)
        self.trans_table.column("Date", width=120)
        self.trans_table.column("Notes", width=200)
        
        scroll_y.config(command=self.trans_table.yview)
        
        # تعبئة الجدول بالبيانات
        self.refresh_transactions_table()
    
    def refresh_products_table(self):
        # مسح البيانات القديمة
        for item in self.products_table.get_children():
            self.products_table.delete(item)
        
        # إضافة البيانات الجديدة
        for product in self.products:
            self.products_table.insert("", tk.END, values=(
                product["ID"],
                product["Name"],
                product["Category"],
                f"{product['Price']:.2f}",
                product["Quantity"],
                product["Min_Stock"]
            ))
    
    def refresh_transactions_table(self):
        # مسح البيانات القديمة
        for item in self.trans_table.get_children():
            self.trans_table.delete(item)
        
        # إضافة البيانات الجديدة
        for trans in self.transactions[-50:]:  # عرض آخر 50 حركة فقط
            product_name = next((p["Name"] for p in self.products if p["ID"] == trans["Product_ID"]), "غير معروف")
            self.trans_table.insert("", tk.END, values=(
                trans["ID"],
                trans["Product_ID"],
                product_name,
                "دخول" if trans["Type"] == "in" else "خروج",
                trans["Quantity"],
                trans["Date"],
                trans["Notes"]
            ))
    
    def add_product(self):
        # نافذة إضافة منتج
        add_window = tk.Toplevel(self.root)
        add_window.title("إضافة صنف جديد")
        add_window.geometry("400x300")
        
        # حقول الإدخال
        ttk.Label(add_window, text="اسم الصنف:").pack(pady=5)
        name_entry = ttk.Entry(add_window, width=30)
        name_entry.pack(pady=5)
        
        ttk.Label(add_window, text="الفئة:").pack(pady=5)
        category_combo = ttk.Combobox(add_window, values=self.categories, width=27)
        category_combo.pack(pady=5)
        
        ttk.Label(add_window, text="السعر:").pack(pady=5)
        price_entry = ttk.Entry(add_window, width=30)
        price_entry.pack(pady=5)
        
        ttk.Label(add_window, text="الكمية الأولية:").pack(pady=5)
        qty_entry = ttk.Entry(add_window, width=30)
        qty_entry.pack(pady=5)
        
        ttk.Label(add_window, text="حد النفاذ:").pack(pady=5)
        min_stock_entry = ttk.Entry(add_window, width=30)
        min_stock_entry.pack(pady=5)
        
        # زر الحفظ
        def save_product():
            try:
                new_id = max([p["ID"] for p in self.products]) + 1 if self.products else 1
                new_product = {
                    "ID": new_id,
                    "Name": name_entry.get(),
                    "Category": category_combo.get(),
                    "Price": float(price_entry.get()),
                    "Quantity": int(qty_entry.get()),
                    "Min_Stock": int(min_stock_entry.get())
                }
                self.products.append(new_product)
                self.save_data()
                self.refresh_products_table()
                add_window.destroy()
                
                # تسجيل حركة الدخول
                self.record_transaction(new_id, "in", int(qty_entry.get()), "إضافة صنف جديد")
                
                messagebox.showinfo("نجاح", "تمت إضافة الصنف بنجاح")
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال قيم صحيحة")
        
        ttk.Button(add_window, text="حفظ", command=save_product).pack(pady=10)
    
    def edit_product(self):
        selected = self.products_table.focus()
        if not selected:
            messagebox.showerror("خطأ", "الرجاء تحديد صنف للتعديل")
            return
        
        item = self.products_table.item(selected)
        product_id = item["values"][0]
        product = next((p for p in self.products if p["ID"] == product_id), None)
        
        if not product:
            messagebox.showerror("خطأ", "الصنف المحدد غير موجود")
            return
        
        # نافذة تعديل المنتج
        edit_window = tk.Toplevel(self.root)
        edit_window.title("تعديل صنف")
        edit_window.geometry("400x300")
        
        # حقول الإدخال
        ttk.Label(edit_window, text="اسم الصنف:").pack(pady=5)
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.insert(0, product["Name"])
        name_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="الفئة:").pack(pady=5)
        category_combo = ttk.Combobox(edit_window, values=self.categories, width=27)
        category_combo.set(product["Category"])
        category_combo.pack(pady=5)
        
        ttk.Label(edit_window, text="السعر:").pack(pady=5)
        price_entry = ttk.Entry(edit_window, width=30)
        price_entry.insert(0, str(product["Price"]))
        price_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="الكمية:").pack(pady=5)
        qty_entry = ttk.Entry(edit_window, width=30)
        qty_entry.insert(0, str(product["Quantity"]))
        qty_entry.pack(pady=5)
        
        ttk.Label(edit_window, text="حد النفاذ:").pack(pady=5)
        min_stock_entry = ttk.Entry(edit_window, width=30)
        min_stock_entry.insert(0, str(product["Min_Stock"]))
        min_stock_entry.pack(pady=5)
        
        # زر الحفظ
        def save_edit():
            try:
                product["Name"] = name_entry.get()
                product["Category"] = category_combo.get()
                product["Price"] = float(price_entry.get())
                product["Quantity"] = int(qty_entry.get())
                product["Min_Stock"] = int(min_stock_entry.get())
                
                self.save_data()
                self.refresh_products_table()
                edit_window.destroy()
                messagebox.showinfo("نجاح", "تم تعديل الصنف بنجاح")
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال قيم صحيحة")
        
        ttk.Button(edit_window, text="حفظ التعديلات", command=save_edit).pack(pady=10)
    
    def delete_product(self):
        selected = self.products_table.focus()
        if not selected:
            messagebox.showerror("خطأ", "الرجاء تحديد صنف للحذف")
            return
        
        item = self.products_table.item(selected)
        product_id = item["values"][0]
        product_name = item["values"][1]
        
        if messagebox.askyesno("تأكيد", f"هل أنت متأكد من حذف الصنف '{product_name}'؟"):
            self.products = [p for p in self.products if p["ID"] != product_id]
            self.save_data()
            self.refresh_products_table()
            messagebox.showinfo("نجاح", "تم حذف الصنف بنجاح")
    
    def show_stock(self):
        # نافذة عرض المخزون
        stock_window = tk.Toplevel(self.root)
        stock_window.title("الباقي في المخزن")
        stock_window.geometry("600x400")
        
        # جدول المخزون
        tree = ttk.Treeview(stock_window, columns=("ID", "Name", "Category", "Quantity", "Status"), show="headings")
        tree.heading("ID", text="رقم الصنف")
        tree.heading("Name", text="اسم الصنف")
        tree.heading("Category", text="الفئة")
        tree.heading("Quantity", text="الكمية")
        tree.heading("Status", text="الحالة")
        
        tree.column("ID", width=80)
        tree.column("Name", width=150)
        tree.column("Category", width=120)
        tree.column("Quantity", width=80)
        tree.column("Status", width=100)
        
        # تعبئة الجدول
        for product in self.products:
            status = "ناقص" if product["Quantity"] < product["Min_Stock"] else "جيد"
            tree.insert("", tk.END, values=(
                product["ID"],
                product["Name"],
                product["Category"],
                product["Quantity"],
                status
            ))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def export_to_excel(self):
        try:
            # تصدير المنتجات
            products_df = pd.DataFrame(self.products)
            products_df.to_excel("منتجات_المخزن.xlsx", index=False, encoding='utf-8')
            
            # تصدير الحركات
            transactions_df = pd.DataFrame(self.transactions)
            
            # إضافة أسماء المنتجات للحركات
            product_names = {p["ID"]: p["Name"] for p in self.products}
            transactions_df["Product_Name"] = transactions_df["Product_ID"].map(product_names)
            
            transactions_df.to_excel("حركات_المخزن.xlsx", index=False, encoding='utf-8')
            
            messagebox.showinfo("نجاح", "تم التصدير إلى Excel بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير: {str(e)}")
    
    def product_in(self):
        selected = self.products_table.focus()
        if not selected:
            messagebox.showerror("خطأ", "الرجاء تحديد صنف لدخول الكمية")
            return
        
        item = self.products_table.item(selected)
        product_id = item["values"][0]
        product_name = item["values"][1]
        
        # نافذة دخول الكمية
        in_window = tk.Toplevel(self.root)
        in_window.title(f"دخول كمية للصنف: {product_name}")
        in_window.geometry("300x200")
        
        ttk.Label(in_window, text="الكمية الداخلة:").pack(pady=10)
        qty_entry = ttk.Entry(in_window, width=20)
        qty_entry.pack(pady=5)
        
        ttk.Label(in_window, text="ملاحظات:").pack(pady=5)
        notes_entry = ttk.Entry(in_window, width=30)
        notes_entry.pack(pady=5)
        
        def save_in():
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showerror("خطأ", "الكمية يجب أن تكون أكبر من الصفر")
                    return
                
                product = next((p for p in self.products if p["ID"] == product_id), None)
                if product:
                    product["Quantity"] += qty
                    self.save_data()
                    self.refresh_products_table()
                    
                    # تسجيل الحركة
                    self.record_transaction(product_id, "in", qty, notes_entry.get())
                    
                    in_window.destroy()
                    messagebox.showinfo("نجاح", "تم تسجيل دخول الكمية بنجاح")
                else:
                    messagebox.showerror("خطأ", "الصنف غير موجود")
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال كمية صحيحة")
        
        ttk.Button(in_window, text="حفظ", command=save_in).pack(pady=10)
    
    def product_out(self):
        selected = self.products_table.focus()
        if not selected:
            messagebox.showerror("خطأ", "الرجاء تحديد صنف لخروج الكمية")
            return
        
        item = self.products_table.item(selected)
        product_id = item["values"][0]
        product_name = item["values"][1]
        current_qty = item["values"][4]
        
        # نافذة خروج الكمية
        out_window = tk.Toplevel(self.root)
        out_window.title(f"خروج كمية من الصنف: {product_name}")
        out_window.geometry("300x200")
        
        ttk.Label(out_window, text=f"الكمية المتاحة: {current_qty}").pack(pady=5)
        
        ttk.Label(out_window, text="الكمية الخارجة:").pack(pady=5)
        qty_entry = ttk.Entry(out_window, width=20)
        qty_entry.pack(pady=5)
        
        ttk.Label(out_window, text="ملاحظات:").pack(pady=5)
        notes_entry = ttk.Entry(out_window, width=30)
        notes_entry.pack(pady=5)
        
        def save_out():
            try:
                qty = int(qty_entry.get())
                if qty <= 0:
                    messagebox.showerror("خطأ", "الكمية يجب أن تكون أكبر من الصفر")
                    return
                
                product = next((p for p in self.products if p["ID"] == product_id), None)
                if product:
                    if product["Quantity"] < qty:
                        messagebox.showerror("خطأ", "الكمية المطلوبة غير متوفرة في المخزن")
                        return
                    
                    product["Quantity"] -= qty
                    self.save_data()
                    self.refresh_products_table()
                    
                    # تسجيل الحركة
                    self.record_transaction(product_id, "out", qty, notes_entry.get())
                    
                    out_window.destroy()
                    messagebox.showinfo("نجاح", "تم تسجيل خروج الكمية بنجاح")
                    
                    # التحقق من حد النفاذ بعد الخروج
                    if product["Quantity"] <= product["Min_Stock"]:
                        messagebox.showwarning("تنبيه", f"تنبيه: الكمية المتبقية من {product['Name']} وصلت أو قاربت حد النفاذ!")
                else:
                    messagebox.showerror("خطأ", "الصنف غير موجود")
            except ValueError:
                messagebox.showerror("خطأ", "الرجاء إدخال كمية صحيحة")
        
        ttk.Button(out_window, text="حفظ", command=save_out).pack(pady=10)
    
    def record_transaction(self, product_id, trans_type, quantity, notes=""):
        new_id = max([t["ID"] for t in self.transactions]) + 1 if self.transactions else 1
        new_trans = {
            "ID": new_id,
            "Product_ID": product_id,
            "Type": trans_type,
            "Quantity": quantity,
            "Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Notes": notes
        }
        self.transactions.append(new_trans)
        self.save_data()
        self.refresh_transactions_table()
    
    def check_low_stock(self):
        low_stock_products = [p for p in self.products if p["Quantity"] <= p["Min_Stock"]]
        
        if low_stock_products:
            message = "تنبيه: الأصناف التالية وصلت أو قاربت حد النفاذ:\n"
            for product in low_stock_products:
                message += f"- {product['Name']} (المتبقي: {product['Quantity']}, حد النفاذ: {product['Min_Stock']})\n"
            
            messagebox.showwarning("تنبيه نفاذ السلع", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryManagementSystem(root)
    root.mainloop()