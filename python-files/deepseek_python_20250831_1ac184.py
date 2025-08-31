import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import json

class FuelStationManager:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة محطة الوقود")
        self.root.geometry("1000x700")
        
        # إنشاء قاعدة البيانات
        self.setup_database()
        
        # واجهة المستخدم
        self.setup_ui()
        
        # تحميل البيانات
        self.load_data()

    def setup_database(self):
        self.conn = sqlite3.connect('fuel_station.db')
        self.cursor = self.conn.cursor()
        
        # إنشاء الجداول إذا لم تكن موجودة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS pumps (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pump_number INTEGER,
                fuel_type TEXT,
                opening_reading REAL,
                closing_reading REAL,
                date TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fuel_type TEXT,
                received REAL,
                sold REAL,
                balance REAL,
                date TEXT
            )
        ''')
        
        self.conn.commit()

    def setup_ui(self):
        # إنشاء دفتر التبويبات
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # تبويب المضخات
        self.pumps_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.pumps_frame, text="إدارة المضخات")
        
        # تبويب الجرد
        self.inventory_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.inventory_frame, text="الجرد والمخزون")
        
        # تبويب التقارير
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="التقارير")
        
        # إعداد واجهة المضخات
        self.setup_pumps_ui()
        
        # إعداد واجهة الجرد
        self.setup_inventory_ui()
        
        # إعداد واجهة التقارير
        self.setup_reports_ui()

    def setup_pumps_ui(self):
        # إطارات المضخات لأنواع الوقود المختلفة
        fuel_types = ["بنزين 95", "بنزين 92", "سولار"]
        
        for i, fuel_type in enumerate(fuel_types):
            frame = ttk.LabelFrame(self.pumps_frame, text=fuel_type)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            # عناوين الأعمدة
            ttk.Label(frame, text="رقم المضخة").grid(row=0, column=0, padx=5, pady=5)
            ttk.Label(frame, text="قراءة البداية").grid(row=0, column=1, padx=5, pady=5)
            ttk.Label(frame, text="قراءة النهاية").grid(row=0, column=2, padx=5, pady=5)
            ttk.Label(frame, text="الكمية المباعة").grid(row=0, column=3, padx=5, pady=5)
            
            # حقول الإدخال للمضخات
            for j in range(1, 7):  # 6 مضخات لكل نوع
                ttk.Label(frame, text=str(j)).grid(row=j, column=0, padx=5, pady=2)
                
                opening_var = tk.DoubleVar()
                ttk.Entry(frame, textvariable=opening_var, width=10).grid(row=j, column=1, padx=5, pady=2)
                
                closing_var = tk.DoubleVar()
                ttk.Entry(frame, textvariable=closing_var, width=10).grid(row=j, column=2, padx=5, pady=2)
                
                sold_var = tk.DoubleVar()
                ttk.Label(frame, textvariable=sold_var, width=10).grid(row=j, column=3, padx=5, pady=2)
                
                # ربط حدث لحساب الكمية المباعة تلقائياً
                def calculate_sold(op=opening_var, cl=closing_var, sold=sold_var, *args):
                    try:
                        sold.set(round(cl.get() - op.get(), 2))
                    except:
                        sold.set(0)
                
                opening_var.trace('w', calculate_sold)
                closing_var.trace('w', calculate_sold)
                
                # حفظ المرجع للمتغيرات
                if not hasattr(self, 'pump_vars'):
                    self.pump_vars = {}
                
                self.pump_vars[(fuel_type, j, 'opening')] = opening_var
                self.pump_vars[(fuel_type, j, 'closing')] = closing_var
                self.pump_vars[(fuel_type, j, 'sold')] = sold_var
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.pumps_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="حفظ البيانات", command=self.save_pump_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="جديد", command=self.clear_pump_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="استيراد من Excel", command=self.import_from_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تصدير إلى Excel", command=self.export_to_excel).pack(side=tk.LEFT, padx=5)

    def setup_inventory_ui(self):
        # إطارات الجرد لأنواع الوقود المختلفة
        fuel_types = ["بنزين 95", "بنزين 92", "سولار"]
        
        for i, fuel_type in enumerate(fuel_types):
            frame = ttk.LabelFrame(self.inventory_frame, text=fuel_type)
            frame.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            
            # حقول الإدخال
            ttk.Label(frame, text="الرصيد الافتتاحي").grid(row=0, column=0, padx=5, pady=5)
            opening_var = tk.DoubleVar()
            ttk.Entry(frame, textvariable=opening_var, width=15).grid(row=0, column=1, padx=5, pady=5)
            
            ttk.Label(frame, text="الوارد").grid(row=1, column=0, padx=5, pady=5)
            received_var = tk.DoubleVar()
            ttk.Entry(frame, textvariable=received_var, width=15).grid(row=1, column=1, padx=5, pady=5)
            
            ttk.Label(frame, text="المبيعات").grid(row=2, column=0, padx=5, pady=5)
            sales_var = tk.DoubleVar()
            ttk.Label(frame, textvariable=sales_var, width=15).grid(row=2, column=1, padx=5, pady=5)
            
            ttk.Label(frame, text="الرصيد الختامي").grid(row=3, column=0, padx=5, pady=5)
            closing_var = tk.DoubleVar()
            ttk.Label(frame, textvariable=closing_var, width=15).grid(row=3, column=1, padx=5, pady=5)
            
            ttk.Label(frame, text="الفرق").grid(row=4, column=0, padx=5, pady=5)
            difference_var = tk.DoubleVar()
            ttk.Label(frame, textvariable=difference_var, width=15).grid(row=4, column=1, padx=5, pady=5)
            
            # حفظ المرجع للمتغيرات
            if not hasattr(self, 'inventory_vars'):
                self.inventory_vars = {}
            
            self.inventory_vars[(fuel_type, 'opening')] = opening_var
            self.inventory_vars[(fuel_type, 'received')] = received_var
            self.inventory_vars[(fuel_type, 'sales')] = sales_var
            self.inventory_vars[(fuel_type, 'closing')] = closing_var
            self.inventory_vars[(fuel_type, 'difference')] = difference_var
            
            # ربط الأحداث للحساب التلقائي
            def calculate_inventory(op=opening_var, rec=received_var, sal=sales_var, 
                                   cl=closing_var, diff=difference_var, *args):
                try:
                    total = op.get() + rec.get() - sal.get()
                    cl.set(round(total, 2))
                    diff.set(round(total - sal.get(), 2))
                except:
                    cl.set(0)
                    diff.set(0)
            
            opening_var.trace('w', calculate_inventory)
            received_var.trace('w', calculate_inventory)
            sales_var.trace('w', calculate_inventory)
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.inventory_frame)
        button_frame.grid(row=1, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="حفظ الجرد", command=self.save_inventory).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تحديث المبيعات من المضخات", command=self.update_sales_from_pumps).pack(side=tk.LEFT, padx=5)

    def setup_reports_ui(self):
        # إطار عرض التقارير
        report_frame = ttk.LabelFrame(self.reports_frame, text="تقارير المبيعات")
        report_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # شجرة لعرض البيانات
        columns = ("النوع", "الكمية", "السعر", "الإجمالي")
        self.report_tree = ttk.Treeview(report_frame, columns=columns, show='headings')
        
        for col in columns:
            self.report_tree.heading(col, text=col)
            self.report_tree.column(col, width=100)
        
        self.report_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # أزرار التحكم
        button_frame = ttk.Frame(self.reports_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="عرض تقرير اليوم", command=self.generate_daily_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="عرض تقرير شهري", command=self.generate_monthly_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="تصدير التقرير", command=self.export_report).pack(side=tk.LEFT, padx=5)

    def load_data(self):
        # تحميل البيانات من قاعدة البيانات
        try:
            self.cursor.execute("SELECT * FROM pumps WHERE date=?", (datetime.now().strftime("%Y-%m-%d"),))
            pumps_data = self.cursor.fetchall()
            
            for data in pumps_data:
                fuel_type = data[2]
                pump_num = data[1]
                opening = data[3]
                closing = data[4]
                
                key_open = (fuel_type, pump_num, 'opening')
                key_close = (fuel_type, pump_num, 'closing')
                
                if key_open in self.pump_vars:
                    self.pump_vars[key_open].set(opening)
                if key_close in self.pump_vars:
                    self.pump_vars[key_close].set(closing)
        except Exception as e:
            print(f"Error loading pump data: {e}")

    def save_pump_data(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # حذف البيانات القديمة لهذا التاريخ
            self.cursor.execute("DELETE FROM pumps WHERE date=?", (current_date,))
            
            # حفظ البيانات الجديدة
            for key, var in self.pump_vars.items():
                if key[2] == 'opening' or key[2] == 'closing':
                    fuel_type, pump_num, reading_type = key
                    value = var.get()
                    
                    self.cursor.execute(
                        "INSERT INTO pumps (pump_number, fuel_type, opening_reading, closing_reading, date) VALUES (?, ?, ?, ?, ?)",
                        (pump_num, fuel_type, 
                         value if reading_type == 'opening' else 0,
                         value if reading_type == 'closing' else 0,
                         current_date)
                    )
            
            self.conn.commit()
            messagebox.showinfo("نجاح", "تم حفظ بيانات المضخات بنجاح")
            
            # تحديث بيانات المبيعات في الجرد
            self.update_sales_from_pumps()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}")

    def update_sales_from_pumps(self):
        try:
            # جمع إجمالي المبيعات من جميع المضخات لكل نوع وقود
            sales = {"بنزين 95": 0, "بنزين 92": 0, "سولار": 0}
            
            for key, var in self.pump_vars.items():
                if key[2] == 'sold':
                    fuel_type = key[0]
                    sales[fuel_type] += var.get()
            
            # تحديث قيم المبيعات في واجهة الجرد
            for fuel_type, total_sales in sales.items():
                if (fuel_type, 'sales') in self.inventory_vars:
                    self.inventory_vars[(fuel_type, 'sales')].set(round(total_sales, 2))
            
        except Exception as e:
            print(f"Error updating sales: {e}")

    def save_inventory(self):
        try:
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            # حذف البيانات القديمة لهذا التاريخ
            self.cursor.execute("DELETE FROM inventory WHERE date=?", (current_date,))
            
            # حفظ البيانات الجديدة
            for fuel_type in ["بنزين 95", "بنزين 92", "سولار"]:
                opening = self.inventory_vars[(fuel_type, 'opening')].get()
                received = self.inventory_vars[(fuel_type, 'received')].get()
                sales = self.inventory_vars[(fuel_type, 'sales')].get()
                closing = self.inventory_vars[(fuel_type, 'closing')].get()
                difference = self.inventory_vars[(fuel_type, 'difference')].get()
                
                self.cursor.execute(
                    "INSERT INTO inventory (fuel_type, received, sold, balance, date) VALUES (?, ?, ?, ?, ?)",
                    (fuel_type, received, sales, closing, current_date)
                )
            
            self.conn.commit()
            messagebox.showinfo("نجاح", "تم حفظ بيانات الجرد بنجاح")
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء الحفظ: {e}")

    def clear_pump_data(self):
        # مسح جميع حقول الإدخال
        for var in self.pump_vars.values():
            if isinstance(var, tk.DoubleVar):
                var.set(0.0)

    def generate_daily_report(self):
        # مسح البيانات القديمة في الشجرة
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # إضافة بيانات اليوم
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        try:
            # بيانات المضخات
            self.cursor.execute("SELECT fuel_type, SUM(closing_reading - opening_reading) FROM pumps WHERE date=? GROUP BY fuel_type", (current_date,))
            pump_results = self.cursor.fetchall()
            
            # بيانات الجرد
            self.cursor.execute("SELECT fuel_type, sold FROM inventory WHERE date=?", (current_date,))
            inventory_results = self.cursor.fetchall()
            
            # أسعار الوقود
            prices = {"بنزين 95": 19, "بنزين 92": 17.25, "سولار": 15.5}
            
            # إضافة البيانات إلى الشجرة
            total_revenue = 0
            
            for fuel_type, amount in pump_results:
                price = prices.get(fuel_type, 0)
                total = amount * price
                total_revenue += total
                
                self.report_tree.insert("", "end", values=(fuel_type, f"{amount:.2f}", f"{price:.2f}", f"{total:.2f}"))
            
            # إضافة الإجمالي
            self.report_tree.insert("", "end", values=("الإجمالي", "", "", f"{total_revenue:.2f}"))
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إنشاء التقرير: {e}")

    def generate_monthly_report(self):
        # مسح البيانات القديمة في الشجرة
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        # إضافة بيانات الشهر
        current_month = datetime.now().strftime("%Y-%m")
        
        try:
            # بيانات المضخات
            self.cursor.execute("SELECT fuel_type, SUM(closing_reading - opening_reading) FROM pumps WHERE date LIKE ? GROUP BY fuel_type", (f"{current_month}%",))
            pump_results = self.cursor.fetchall()
            
            # أسعار الوقود
            prices = {"بنزين 95": 19, "بنزين 92": 17.25, "سولار": 15.5}
            
            # إضافة البيانات إلى الشجرة
            total_revenue = 0
            
            for fuel_type, amount in pump_results:
                price = prices.get(fuel_type, 0)
                total = amount * price
                total_revenue += total
                
                self.report_tree.insert("", "end", values=(fuel_type, f"{amount:.2f}", f"{price:.2f}", f"{total:.2f}"))
            
            # إضافة الإجمالي
            self.report_tree.insert("", "end", values=("الإجمالي", "", "", f"{total_revenue:.2f}"))
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ أثناء إنشاء التقرير: {e}")

    def import_from_excel(self):
        # دالة لاستيراد البيانات من Excel
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            try:
                # هنا سيتم تنفيذ كود استيراد البيانات من Excel
                messagebox.showinfo("استيراد", "سيتم تنفيذ استيراد البيانات من Excel في النسخة الكاملة")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء الاستيراد: {e}")

    def export_to_excel(self):
        # دالة لتصدير البيانات إلى Excel
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            try:
                # هنا سيتم تنفيذ كود تصدير البيانات إلى Excel
                messagebox.showinfo("تصدير", "سيتم تنفيذ تصدير البيانات إلى Excel في النسخة الكاملة")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير: {e}")

    def export_report(self):
        # دلة لتصدير التقرير
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            try:
                # هنا سيتم تنفيذ كود تصدير التقرير
                messagebox.showinfo("تصدير", "سيتم تنفيذ تصدير التقرير في النسخة الكاملة")
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ أثناء التصدير: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FuelStationManager(root)
    root.mainloop()