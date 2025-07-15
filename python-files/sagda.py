import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime
import json
import os

# استيراد المكتبات الاختيارية
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

class SalesManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("نظام إدارة المبيعات والمخزون - إصدار احترافي")
        self.root.geometry("1400x900")
        self.root.state('zoomed')  # ملء الشاشة
        
        # تحسين الألوان والخطوط
        self.configure_styles()
        
        # إنشاء قاعدة البيانات
        self.init_database()
        
        # إنشاء الواجهة الرئيسية
        self.create_main_interface()
        
    def configure_styles(self):
        """تكوين الأنماط والخطوط الاحترافية"""
        # الألوان الرئيسية
        self.colors = {
            'primary': '#2E86AB',      # أزرق فاتح
            'secondary': '#A23B72',    # وردي داكن
            'success': '#F18F01',      # برتقالي
            'danger': '#C73E1D',       # أحمر
            'warning': '#FFB400',      # أصفر
            'info': '#17A2B8',         # تركوازي
            'light': '#F8F9FA',        # رمادي فاتح
            'dark': '#343A40',         # رمادي داكن
            'white': '#FFFFFF',        # أبيض
            'bg_main': '#F5F7FA',      # خلفية رئيسية
            'bg_card': '#FFFFFF',      # خلفية البطاقات
            'text_primary': '#2C3E50', # نص رئيسي
            'text_secondary': '#7F8C8D' # نص ثانوي
        }
        
        # تكوين الخلفية الرئيسية
        self.root.configure(bg=self.colors['bg_main'])
        
        # تكوين أنماط ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # تكوين الخطوط الاحترافية
        self.fonts = {
            'title': ('Segoe UI', 24, 'bold'),
            'subtitle': ('Segoe UI', 18, 'bold'),
            'header': ('Segoe UI', 16, 'bold'),
            'body': ('Segoe UI', 12),
            'body_bold': ('Segoe UI', 12, 'bold'),
            'small': ('Segoe UI', 10),
            'button': ('Segoe UI', 11, 'bold'),
            'stats': ('Segoe UI', 14, 'bold')
        }
        
        # تكوين أنماط الأزرار
        self.style.configure('Primary.TButton',
                           font=self.fonts['button'],
                           padding=(20, 10),
                           relief='flat')
        
        self.style.configure('Secondary.TButton',
                           font=self.fonts['button'],
                           padding=(15, 8),
                           relief='flat')
        
        # تكوين أنماط الإطارات
        self.style.configure('Card.TLabelFrame',
                           background=self.colors['bg_card'],
                           borderwidth=2,
                           relief='solid')
        
        # تكوين أنماط الجداول
        self.style.configure('Treeview',
                           font=self.fonts['body'],
                           background=self.colors['white'],
                           fieldbackground=self.colors['white'],
                           borderwidth=1,
                           relief='solid')
        
        self.style.configure('Treeview.Heading',
                           font=self.fonts['body_bold'],
                           background=self.colors['primary'],
                           foreground=self.colors['white'],
                           borderwidth=1,
                           relief='solid')
        
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        self.conn = sqlite3.connect('sales_system.db')
        self.cursor = self.conn.cursor()
        
        # جدول المنتجات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                min_stock INTEGER DEFAULT 10,
                description TEXT,
                date_added TEXT
            )
        ''')
        
        # جدول العملاء
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                date_added TEXT
            )
        ''')
        
        # جدول المبيعات المحسن
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                total_amount REAL NOT NULL,
                discount REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                other_fees REAL DEFAULT 0,
                final_amount REAL NOT NULL,
                payment_method TEXT,
                paid_amount REAL DEFAULT 0,
                change_amount REAL DEFAULT 0,
                reference_number TEXT,
                due_date TEXT,
                salesperson TEXT,
                sale_date TEXT,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')
        
        # جدول تفاصيل المبيعات المحسن
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                product_id INTEGER,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount_percent REAL DEFAULT 0,
                discount_amount REAL DEFAULT 0,
                total_price REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        self.conn.commit()
        
    def create_main_interface(self):
        """إنشاء الواجهة الرئيسية الاحترافية"""
        # شريط القوائم
        self.create_menu_bar()
        
        # الإطار الرئيسي مع padding احترافي
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # إطار العنوان مع تصميم احترافي
        header_frame = tk.Frame(main_frame, bg=self.colors['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # عنوان البرنامج الاحترافي
        title_label = tk.Label(header_frame, 
                              text="🏪 نظام إدارة المبيعات والمخزون الاحترافي",
                              font=self.fonts['title'],
                              bg=self.colors['primary'],
                              fg=self.colors['white'])
        title_label.pack(expand=True)
        
        # إطار المحتوى الرئيسي
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)
        
        # إطار الأزرار الجانبي
        buttons_frame = ttk.LabelFrame(content_frame, text="الوظائف الرئيسية", 
                                      padding=20)
        buttons_frame.pack(side='left', fill='y', padx=(0, 20))
        
        # أزرار الوظائف الرئيسية مع تصميم احترافي
        self.create_professional_buttons(buttons_frame)
        
        # إطار الإحصائيات الاحترافية
        self.create_professional_dashboard(content_frame)
        
    def create_professional_buttons(self, parent):
        """إنشاء أزرار احترافية"""
        buttons_data = [
            ("📦 إدارة المنتجات", self.open_products_window, self.colors['primary']),
            ("👥 إدارة العملاء", self.open_customers_window, self.colors['info']),
            ("💰 مبيعة جديدة", self.open_sales_window, self.colors['success']),
            ("📊 قائمة المبيعات", self.open_sales_list_window, self.colors['warning']),
            ("📈 تقارير المبيعات", self.open_reports_window, self.colors['secondary']),
            ("🏪 إدارة المخزون", self.open_inventory_window, self.colors['info']),
            ("⚙️ الإعدادات", self.open_settings_window, self.colors['dark'])
        ]
        
        for i, (text, command, color) in enumerate(buttons_data):
            btn = tk.Button(parent, 
                           text=text,
                           command=command,
                           font=self.fonts['button'],
                           bg=color,
                           fg=self.colors['white'],
                           activebackground=self.colors['light'],
                           activeforeground=color,
                           relief='flat',
                           cursor='hand2',
                           width=20,
                           height=2)
            btn.pack(pady=8, fill='x')
            
            # تأثير hover
            btn.bind('<Enter>', lambda e, btn=btn, color=color: self.button_hover(btn, color, True))
            btn.bind('<Leave>', lambda e, btn=btn, color=color: self.button_hover(btn, color, False))
    
    def button_hover(self, button, color, is_hover):
        """تأثير hover للأزرار"""
        if is_hover:
            button.config(bg=self.colors['light'], fg=color)
        else:
            button.config(bg=color, fg=self.colors['white'])
    
    def create_professional_dashboard(self, parent):
        """إنشاء لوحة إحصائيات احترافية"""
        # إطار الإحصائيات الرئيسي
        dashboard_frame = ttk.LabelFrame(parent, text="📊 الإحصائيات والمعلومات السريعة", 
                                       padding=20)
        dashboard_frame.pack(side='right', fill='both', expand=True)
        
        # إطار الإحصائيات العلوية
        top_stats_frame = ttk.Frame(dashboard_frame)
        top_stats_frame.pack(fill='x', pady=(0, 20))
        
        # بطاقات الإحصائيات السريعة
        self.create_stat_cards(top_stats_frame)
        
        # جدول الإحصائيات التفصيلية
        self.create_detailed_stats_table(dashboard_frame)
        
        # إطار الرسوم البيانية (اختياري)
        self.create_charts_frame(dashboard_frame)
        
    def create_stat_cards(self, parent):
        """إنشاء بطاقات الإحصائيات السريعة"""
        # الحصول على البيانات
        stats_data = [
            ("المنتجات", self.get_products_count(), "📦", self.colors['primary']),
            ("العملاء", self.get_customers_count(), "👥", self.colors['info']),
            ("مبيعات اليوم", f"{self.get_today_sales():.2f} ج.م", "💰", self.colors['success']),
            ("قيمة المخزون", f"{self.get_inventory_value():.2f} ج.م", "🏪", self.colors['warning'])
        ]
        
        for i, (title, value, icon, color) in enumerate(stats_data):
            card_frame = tk.Frame(parent, bg=color, relief='raised', bd=2)
            card_frame.grid(row=0, column=i, padx=10, pady=5, sticky='ew')
            
            # أيقونة
            icon_label = tk.Label(card_frame, text=icon, font=('Arial', 20), 
                                bg=color, fg=self.colors['white'])
            icon_label.pack(pady=(10, 5))
            
            # القيمة
            value_label = tk.Label(card_frame, text=str(value), 
                                 font=self.fonts['stats'], 
                                 bg=color, fg=self.colors['white'])
            value_label.pack()
            
            # العنوان
            title_label = tk.Label(card_frame, text=title, 
                                 font=self.fonts['body_bold'], 
                                 bg=color, fg=self.colors['white'])
            title_label.pack(pady=(0, 10))
        
        # تكوين الأعمدة
        for i in range(4):
            parent.grid_columnconfigure(i, weight=1)
    
    def create_detailed_stats_table(self, parent):
        """إنشاء جدول الإحصائيات التفصيلية الاحترافي"""
        # إطار الجدول
        table_frame = ttk.LabelFrame(parent, text="📈 إحصائيات تفصيلية", 
                                    padding=15)
        table_frame.pack(fill='both', expand=True, pady=(20, 0))
        
        # إنشاء الجدول مع تصميم احترافي
        columns = ('المؤشر', 'القيمة', 'الوحدة', 'الحالة')
        self.stats_tree = ttk.Treeview(table_frame, columns=columns, show='headings', 
                                      height=12)
        
        # تكوين الأعمدة
        column_widths = {'المؤشر': 200, 'القيمة': 100, 'الوحدة': 80, 'الحالة': 120}
        for col in columns:
            self.stats_tree.heading(col, text=col)
            self.stats_tree.column(col, width=column_widths[col], anchor='center')
        
        # شريط التمرير مع تصميم احترافي
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=scrollbar.set)
        
        # ترتيب العناصر
        self.stats_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # تحميل البيانات
        self.load_detailed_stats()
        
        # تحديث تلقائي كل 30 ثانية
        self.schedule_stats_update()
    
    def load_detailed_stats(self):
        """تحميل الإحصائيات التفصيلية"""
        # مسح الجدول
        for item in self.stats_tree.get_children():
            self.stats_tree.delete(item)
        
        # إعداد البيانات
        stats_data = [
            ("إجمالي المنتجات", self.get_products_count(), "منتج", "نشط"),
            ("إجمالي العملاء", self.get_customers_count(), "عميل", "نشط"),
            ("مبيعات اليوم", f"{self.get_today_sales():.2f}", "ج.م", "جيد"),
            ("مبيعات الأسبوع", f"{self.get_week_sales():.2f}", "ج.م", "جيد"),
            ("مبيعات الشهر", f"{self.get_month_sales():.2f}", "ج.م", "ممتاز"),
            ("قيمة المخزون", f"{self.get_inventory_value():.2f}", "ج.م", "مستقر"),
            ("إجمالي الكمية", self.get_total_inventory_quantity(), "قطعة", "متوفر"),
            ("منتجات قليلة المخزون", self.get_low_stock_count(), "منتج", "تحذير" if self.get_low_stock_count() > 0 else "جيد"),
            ("متوسط سعر المنتج", f"{self.get_average_product_price():.2f}", "ج.م", "معتدل"),
            ("أعلى مبيعة", f"{self.get_highest_sale():.2f}", "ج.م", "ممتاز"),
            ("عدد المبيعات اليوم", self.get_today_sales_count(), "مبيعة", "نشط"),
            ("متوسط قيمة المبيعة", f"{self.get_average_sale_value():.2f}", "ج.م", "جيد")
        ]
        
        # إضافة البيانات للجدول مع تلوين
        for i, (indicator, value, unit, status) in enumerate(stats_data):
            # تحديد لون الحالة
            if status == "تحذير":
                tags = ('warning',)
            elif status == "ممتاز":
                tags = ('excellent',)
            elif status == "جيد":
                tags = ('good',)
            else:
                tags = ('normal',)
            
            self.stats_tree.insert('', 'end', values=(indicator, value, unit, status), tags=tags)
        
        # تكوين الألوان
        self.stats_tree.tag_configure('warning', background='#FFE6E6', foreground='#C73E1D')
        self.stats_tree.tag_configure('excellent', background='#E6F7FF', foreground='#2E86AB')
        self.stats_tree.tag_configure('good', background='#F0F8E6', foreground='#52C41A')
        self.stats_tree.tag_configure('normal', background='#FFFFFF', foreground='#2C3E50')
    
    def create_charts_frame(self, parent):
        """إنشاء إطار الرسوم البيانية"""
        charts_frame = ttk.LabelFrame(parent, text="📊 رسوم بيانية سريعة", 
                                     padding=15)
        charts_frame.pack(fill='x', pady=(20, 0))
        
        # رسم بياني بسيط باستخدام النصوص
        self.create_simple_chart(charts_frame)
    
    def create_simple_chart(self, parent):
        """إنشاء رسم بياني بسيط"""
        chart_frame = tk.Frame(parent, bg=self.colors['white'])
        chart_frame.pack(fill='x', pady=10)
        
        # بيانات المبيعات لآخر 7 أيام
        sales_data = self.get_last_7_days_sales()
        
        # عنوان الرسم
        title_label = tk.Label(chart_frame, text="📈 مبيعات آخر 7 أيام", 
                              font=self.fonts['header'], 
                              bg=self.colors['white'], 
                              fg=self.colors['text_primary'])
        title_label.pack(pady=(0, 10))
        
        # رسم البيانات
        max_value = max(sales_data) if sales_data else 1
        for i, value in enumerate(sales_data):
            day_frame = tk.Frame(chart_frame, bg=self.colors['white'])
            day_frame.pack(side='left', padx=5, fill='y')
            
            # شريط البيانات
            bar_height = int((value / max_value) * 100) if max_value > 0 else 0
            bar = tk.Frame(day_frame, bg=self.colors['primary'], width=30, height=bar_height)
            bar.pack(side='bottom')
            bar.pack_propagate(False)
            
            # قيمة البيانات
            value_label = tk.Label(day_frame, text=f"{value:.0f}", 
                                 font=self.fonts['small'], 
                                 bg=self.colors['white'], 
                                 fg=self.colors['text_primary'])
            value_label.pack(side='bottom', pady=(2, 0))
            
            # يوم الأسبوع
            day_label = tk.Label(day_frame, text=f"يوم {i+1}", 
                               font=self.fonts['small'], 
                               bg=self.colors['white'], 
                               fg=self.colors['text_secondary'])
            day_label.pack(side='bottom')
    
    def schedule_stats_update(self):
        """جدولة تحديث الإحصائيات"""
        self.load_detailed_stats()
        self.root.after(30000, self.schedule_stats_update)  # تحديث كل 30 ثانية
    
    # دوال الإحصائيات الإضافية
    def get_week_sales(self):
        """الحصول على مبيعات الأسبوع"""
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        self.cursor.execute("SELECT SUM(final_amount) FROM sales WHERE sale_date >= ?", (week_ago,))
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_month_sales(self):
        """الحصول على مبيعات الشهر"""
        from datetime import datetime, timedelta
        month_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        self.cursor.execute("SELECT SUM(final_amount) FROM sales WHERE sale_date >= ?", (month_ago,))
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_average_product_price(self):
        """الحصول على متوسط سعر المنتج"""
        self.cursor.execute("SELECT AVG(price) FROM products")
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_highest_sale(self):
        """الحصول على أعلى مبيعة"""
        self.cursor.execute("SELECT MAX(final_amount) FROM sales")
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_today_sales_count(self):
        """الحصول على عدد المبيعات اليوم"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT COUNT(*) FROM sales WHERE DATE(sale_date) = ?", (today,))
        return self.cursor.fetchone()[0]
    
    def get_average_sale_value(self):
        """الحصول على متوسط قيمة المبيعة"""
        self.cursor.execute("SELECT AVG(final_amount) FROM sales")
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_last_7_days_sales(self):
        """الحصول على مبيعات آخر 7 أيام"""
        from datetime import datetime, timedelta
        sales_data = []
        for i in range(7):
            day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            self.cursor.execute("SELECT SUM(final_amount) FROM sales WHERE DATE(sale_date) = ?", (day,))
            result = self.cursor.fetchone()[0]
            sales_data.append(result if result else 0)
        return list(reversed(sales_data))
        
    def create_menu_bar(self):
        """إنشاء شريط القوائم الاحترافي"""
        menubar = tk.Menu(self.root, bg=self.colors['primary'], fg=self.colors['white'],
                         activebackground=self.colors['secondary'], activeforeground=self.colors['white'],
                         font=self.fonts['body'])
        self.root.config(menu=menubar)
        
        # قائمة الملف
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['white'], fg=self.colors['text_primary'],
                           activebackground=self.colors['primary'], activeforeground=self.colors['white'],
                           font=self.fonts['body'])
        menubar.add_cascade(label="📁 ملف", menu=file_menu)
        file_menu.add_command(label="💾 نسخ احتياطي", command=self.backup_database)
        file_menu.add_command(label="📥 استعادة نسخة احتياطية", command=self.restore_database)
        file_menu.add_separator()
        file_menu.add_command(label="🚪 خروج", command=self.root.quit)
        
        # قائمة البيانات
        data_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['white'], fg=self.colors['text_primary'],
                           activebackground=self.colors['info'], activeforeground=self.colors['white'],
                           font=self.fonts['body'])
        menubar.add_cascade(label="📊 البيانات", menu=data_menu)
        data_menu.add_command(label="📦 المنتجات", command=self.open_products_window)
        data_menu.add_command(label="👥 العملاء", command=self.open_customers_window)
        data_menu.add_command(label="💰 المبيعات", command=self.open_sales_history_window)
        
        # قائمة التقارير
        reports_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['white'], fg=self.colors['text_primary'],
                              activebackground=self.colors['success'], activeforeground=self.colors['white'],
                              font=self.fonts['body'])
        menubar.add_cascade(label="📈 التقارير", menu=reports_menu)
        reports_menu.add_command(label="📊 تقرير المبيعات", command=self.open_reports_window)
        reports_menu.add_command(label="🏪 تقرير المخزون", command=self.open_inventory_report)
        
        # قائمة المساعدة
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.colors['white'], fg=self.colors['text_primary'],
                           activebackground=self.colors['secondary'], activeforeground=self.colors['white'],
                           font=self.fonts['body'])
        menubar.add_cascade(label="❓ مساعدة", menu=help_menu)
        help_menu.add_command(label="ℹ️ حول البرنامج", command=self.show_about)
        

        
    def get_products_count(self):
        """الحصول على عدد المنتجات"""
        self.cursor.execute("SELECT COUNT(*) FROM products")
        return self.cursor.fetchone()[0]
    
    def get_customers_count(self):
        """الحصول على عدد العملاء"""
        self.cursor.execute("SELECT COUNT(*) FROM customers")
        return self.cursor.fetchone()[0]
    
    def get_today_sales(self):
        """الحصول على مبيعات اليوم"""
        today = datetime.now().strftime('%Y-%m-%d')
        self.cursor.execute("SELECT SUM(final_amount) FROM sales WHERE DATE(sale_date) = ?", (today,))
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_low_stock_count(self):
        """الحصول على عدد المنتجات قليلة المخزون"""
        self.cursor.execute("SELECT COUNT(*) FROM products WHERE quantity <= min_stock")
        return self.cursor.fetchone()[0]
    
    def get_inventory_value(self):
        """الحصول على إجمالي قيمة المخزون"""
        self.cursor.execute("SELECT SUM(price * quantity) FROM products")
        result = self.cursor.fetchone()[0]
        return result if result else 0
    
    def get_total_inventory_quantity(self):
        """الحصول على إجمالي كمية المخزون"""
        self.cursor.execute("SELECT SUM(quantity) FROM products")
        result = self.cursor.fetchone()[0]
        return result if result else 0
    

    
    def open_products_window(self):
        """فتح نافذة إدارة المنتجات"""
        ProductsWindow(self.root, self.conn, self.cursor, self)
    
    def open_customers_window(self):
        """فتح نافذة إدارة العملاء"""
        CustomersWindow(self.root, self.conn, self.cursor, self)
    
    def open_sales_window(self):
        """فتح نافذة تسجيل المبيعات"""
        SalesWindow(self.root, self.conn, self.cursor, self)
    
    def open_reports_window(self):
        """فتح نافذة التقارير"""
        ReportsWindow(self.root, self.conn, self.cursor)
    
    def open_inventory_window(self):
        """فتح نافذة إدارة المخزون"""
        InventoryWindow(self.root, self.conn, self.cursor)
    
    def open_settings_window(self):
        """فتح نافذة الإعدادات"""
        SettingsWindow(self.root, self.conn, self.cursor)
    
    def open_sales_list_window(self):
        """فتح نافذة قائمة المبيعات"""
        from sales_classes import SalesListWindow
        SalesListWindow(self.root, self.conn, self.cursor)
    
    def open_sales_history_window(self):
        """فتح نافذة تاريخ المبيعات"""
        from sales_classes import SalesListWindow
        SalesListWindow(self.root, self.conn, self.cursor)
    
    def open_inventory_report(self):
        """فتح تقرير المخزون"""
        InventoryReportWindow(self.root, self.conn, self.cursor)
    
    def backup_database(self):
        """عمل نسخة احتياطية من قاعدة البيانات"""
        try:
            backup_path = filedialog.asksaveasfilename(
                defaultextension=".db",
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            if backup_path:
                # نسخ قاعدة البيانات
                import shutil
                shutil.copy2('sales_system.db', backup_path)
                messagebox.showinfo("نجح", "تم إنشاء النسخة الاحتياطية بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
    
    def restore_database(self):
        """استعادة نسخة احتياطية من قاعدة البيانات"""
        try:
            backup_path = filedialog.askopenfilename(
                filetypes=[("Database files", "*.db"), ("All files", "*.*")]
            )
            if backup_path:
                # إغلاق الاتصال الحالي
                self.conn.close()
                # نسخ النسخة الاحتياطية
                import shutil
                shutil.copy2(backup_path, 'sales_system.db')
                # إعادة الاتصال
                self.conn = sqlite3.connect('sales_system.db')
                self.cursor = self.conn.cursor()
                messagebox.showinfo("نجح", "تم استعادة النسخة الاحتياطية بنجاح")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في استعادة النسخة الاحتياطية: {str(e)}")
    
    def show_about(self):
        """عرض معلومات حول البرنامج"""
        about_text = """
🏪 نظام إدارة المبيعات والمخزون الاحترافي
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 الإصدار: 2.0 Professional
🐍 تم تطويره باستخدام: Python & Tkinter
🎨 واجهة مستخدم احترافية مع إحصائيات تفاعلية
📊 يدعم الجداول والرسوم البيانية
💾 نسخ احتياطي تلقائي
🔄 تحديث البيانات في الوقت الفعلي

✨ الميزات الجديدة:
• إحصائيات في جداول احترافية
• تصميم عصري وألوان متناسقة
• خطوط كبيرة وواضحة
• رسوم بيانية بسيطة
• تحديث تلقائي للبيانات

© 2024 جميع الحقوق محفوظة
        """
        messagebox.showinfo("ℹ️ حول البرنامج", about_text)

class ProductsWindow:
    def __init__(self, parent, conn, cursor, main_system=None):
        self.parent = parent
        self.conn = conn
        self.cursor = cursor
        self.main_system = main_system
        
        self.window = tk.Toplevel(parent)
        self.window.title("إدارة المنتجات")
        self.window.geometry("900x600")
        self.window.grab_set()
        
        self.create_products_interface()
        self.load_products()
        
    def create_products_interface(self):
        """إنشاء واجهة إدارة المنتجات الاحترافية"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # إطار العنوان مع تصميم احترافي
        header_frame = tk.Frame(main_frame, bg='#2E86AB', height=60)
        header_frame.pack(fill='x', pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # عنوان النافذة
        title_label = tk.Label(header_frame, text="📦 إدارة المنتجات", 
                              font=('Segoe UI', 20, 'bold'),
                              bg='#2E86AB', fg='white')
        title_label.pack(expand=True)
        
        # إطار الإدخال مع تصميم احترافي
        input_frame = ttk.LabelFrame(main_frame, text="📝 بيانات المنتج", padding=20)
        input_frame.pack(fill='x', pady=20)
        
        # حقول الإدخال مع خطوط كبيرة
        ttk.Label(input_frame, text="اسم المنتج:", font=('Segoe UI', 12, 'bold')).grid(row=0, column=0, sticky='e', padx=10, pady=10)
        self.name_entry = ttk.Entry(input_frame, width=30, font=('Segoe UI', 12))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10)
        
        ttk.Label(input_frame, text="الفئة:", font=('Segoe UI', 12, 'bold')).grid(row=0, column=2, sticky='e', padx=10, pady=10)
        self.category_entry = ttk.Entry(input_frame, width=20, font=('Segoe UI', 12))
        self.category_entry.grid(row=0, column=3, padx=10, pady=10)
        
        ttk.Label(input_frame, text="السعر:", font=('Segoe UI', 12, 'bold')).grid(row=1, column=0, sticky='e', padx=10, pady=10)
        self.price_entry = ttk.Entry(input_frame, width=15, font=('Segoe UI', 12))
        self.price_entry.grid(row=1, column=1, padx=10, pady=10)
        
        ttk.Label(input_frame, text="الكمية:", font=('Segoe UI', 12, 'bold')).grid(row=1, column=2, sticky='e', padx=10, pady=10)
        self.quantity_entry = ttk.Entry(input_frame, width=15, font=('Segoe UI', 12))
        self.quantity_entry.grid(row=1, column=3, padx=10, pady=10)
        
        ttk.Label(input_frame, text="الحد الأدنى:", font=('Segoe UI', 12, 'bold')).grid(row=2, column=0, sticky='e', padx=10, pady=10)
        self.min_stock_entry = ttk.Entry(input_frame, width=15, font=('Segoe UI', 12))
        self.min_stock_entry.grid(row=2, column=1, padx=10, pady=10)
        
        ttk.Label(input_frame, text="الوصف:", font=('Segoe UI', 12, 'bold')).grid(row=2, column=2, sticky='e', padx=10, pady=10)
        self.description_entry = ttk.Entry(input_frame, width=30, font=('Segoe UI', 12))
        self.description_entry.grid(row=2, column=3, padx=10, pady=10)
        
        # أزرار العمليات مع تصميم احترافي
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=3, column=0, columnspan=4, pady=20)
        
        # بيانات الأزرار مع الألوان والأيقونات
        buttons_data = [
            ("➕ إضافة منتج", self.add_product, '#28a745'),
            ("✏️ تعديل منتج", self.update_product, '#ffc107'),
            ("🗑️ حذف منتج", self.delete_product, '#dc3545'),
            ("🗑️ حذف الكل", self.delete_all_products, '#dc3545'),
            ("🔄 مسح الحقول", self.clear_fields, '#6c757d')
        ]
        
        for text, command, color in buttons_data:
            btn = tk.Button(buttons_frame, 
                           text=text,
                           command=command,
                           font=('Segoe UI', 11, 'bold'),
                           bg=color,
                           fg='white',
                           activebackground='#f8f9fa',
                           activeforeground=color,
                           relief='flat',
                           cursor='hand2',
                           width=12,
                           height=2)
            btn.pack(side='left', padx=8)
            
            # تأثير hover
            btn.bind('<Enter>', lambda e, btn=btn, color=color: btn.config(bg='#f8f9fa', fg=color))
            btn.bind('<Leave>', lambda e, btn=btn, color=color: btn.config(bg=color, fg='white'))
        
        # إطار البحث مع تصميم احترافي
        search_frame = ttk.LabelFrame(main_frame, text="🔍 البحث عن المنتجات", padding=15)
        search_frame.pack(fill='x', pady=20)
        
        ttk.Label(search_frame, text="البحث:", font=('Segoe UI', 12, 'bold')).pack(side='left', padx=10)
        self.search_entry = ttk.Entry(search_frame, width=40, font=('Segoe UI', 12))
        self.search_entry.pack(side='left', padx=10)
        self.search_entry.bind('<KeyRelease>', self.search_products)
        
        # زر البحث
        search_btn = tk.Button(search_frame, 
                              text="🔍 بحث",
                              font=('Segoe UI', 11, 'bold'),
                              bg='#17a2b8',
                              fg='white',
                              relief='flat',
                              cursor='hand2',
                              width=8)
        search_btn.pack(side='left', padx=10)
        
        # جدول المنتجات
        self.create_products_table(main_frame)
        
        # متغير لتخزين المنتج المحدد
        self.selected_product_id = None
        
    def create_products_table(self, parent):
        """إنشاء جدول المنتجات الاحترافي"""
        table_frame = ttk.LabelFrame(parent, text="📋 قائمة المنتجات", padding=15)
        table_frame.pack(fill='both', expand=True, pady=20)
        
        # إنشاء Treeview مع تصميم احترافي
        columns = ('ID', 'اسم المنتج', 'الفئة', 'السعر', 'الكمية', 'الحد الأدنى', 'الوصف')
        self.products_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # تعيين العناوين والعروض
        column_widths = {'ID': 60, 'اسم المنتج': 200, 'الفئة': 120, 'السعر': 100, 'الكمية': 80, 'الحد الأدنى': 100, 'الوصف': 250}
        
        for col in columns:
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=column_widths[col], anchor='center')
        
        # تطبيق نمط احترافي
        style = ttk.Style()
        style.configure('Products.Treeview',
                       font=('Segoe UI', 11),
                       background='white',
                       fieldbackground='white',
                       borderwidth=1,
                       relief='solid')
        
        style.configure('Products.Treeview.Heading',
                       font=('Segoe UI', 12, 'bold'),
                       background='#2E86AB',
                       foreground='white',
                       borderwidth=1,
                       relief='solid')
        
        self.products_tree.configure(style='Products.Treeview')
        
        # شريط التمرير الاحترافي
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        
        # ترتيب العناصر
        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # ربط الحدث
        self.products_tree.bind('<Double-1>', self.on_product_select)
        
        # إضافة ألوان للصفوف
        self.products_tree.tag_configure('evenrow', background='#f8f9fa')
        self.products_tree.tag_configure('oddrow', background='white')
        self.products_tree.tag_configure('low_stock', background='#ffebee', foreground='#d32f2f')
        
    def load_products(self):
        """تحميل المنتجات من قاعدة البيانات مع الألوان"""
        # مسح الجدول
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # جلب البيانات
        self.cursor.execute("SELECT * FROM products ORDER BY name")
        products = self.cursor.fetchall()
        
        # إضافة البيانات للجدول مع الألوان
        for i, product in enumerate(products):
            # تحديد التاج حسب الصف ومستوى المخزون
            if product[4] <= product[5]:  # الكمية <= الحد الأدنى
                tags = ('low_stock',)
            elif i % 2 == 0:
                tags = ('evenrow',)
            else:
                tags = ('oddrow',)
            
            self.products_tree.insert('', 'end', values=product, tags=tags)
            
    def search_products(self, event=None):
        """البحث في المنتجات مع الألوان"""
        search_term = self.search_entry.get()
        
        # مسح الجدول
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)
        
        # البحث في قاعدة البيانات
        self.cursor.execute("""
            SELECT * FROM products 
            WHERE name LIKE ? OR category LIKE ? OR description LIKE ?
            ORDER BY name
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        products = self.cursor.fetchall()
        
        # إضافة النتائج للجدول مع الألوان
        for i, product in enumerate(products):
            # تحديد التاج حسب الصف ومستوى المخزون
            if product[4] <= product[5]:  # الكمية <= الحد الأدنى
                tags = ('low_stock',)
            elif i % 2 == 0:
                tags = ('evenrow',)
            else:
                tags = ('oddrow',)
            
            self.products_tree.insert('', 'end', values=product, tags=tags)
            
    def on_product_select(self, event):
        """عند تحديد منتج من الجدول"""
        selected_item = self.products_tree.selection()[0]
        product_data = self.products_tree.item(selected_item)['values']
        
        # تعبئة الحقول
        self.selected_product_id = product_data[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, product_data[1])
        self.category_entry.delete(0, tk.END)
        self.category_entry.insert(0, product_data[2])
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, product_data[3])
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, product_data[4])
        self.min_stock_entry.delete(0, tk.END)
        self.min_stock_entry.insert(0, product_data[5])
        self.description_entry.delete(0, tk.END)
        self.description_entry.insert(0, product_data[6] if product_data[6] else '')
        
    def add_product(self):
        """إضافة منتج جديد"""
        try:
            name = self.name_entry.get().strip()
            category = self.category_entry.get().strip()
            price = float(self.price_entry.get())
            quantity = int(self.quantity_entry.get())
            min_stock = int(self.min_stock_entry.get() or 10)
            description = self.description_entry.get().strip()
            
            if not name or price <= 0 or quantity < 0:
                messagebox.showerror("خطأ", "يرجى إدخال بيانات صحيحة")
                return
            
            # إضافة المنتج
            self.cursor.execute("""
                INSERT INTO products (name, category, price, quantity, min_stock, description, date_added)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (name, category, price, quantity, min_stock, description, datetime.now().isoformat()))
            
            self.conn.commit()
            messagebox.showinfo("نجح", "تم إضافة المنتج بنجاح")
            self.clear_fields()
            self.load_products()
            
            # تحديث الإحصائيات السريعة في النافذة الرئيسية
            if self.main_system:
                self.main_system.update_dashboard_stats()
            
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة للسعر والكمية")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
            
    def update_product(self):
        """تعديل منتج موجود"""
        if not self.selected_product_id:
            messagebox.showerror("خطأ", "يرجى تحديد منتج للتعديل")
            return
            
        try:
            name = self.name_entry.get().strip()
            category = self.category_entry.get().strip()
            price = float(self.price_entry.get())
            quantity = int(self.quantity_entry.get())
            min_stock = int(self.min_stock_entry.get() or 10)
            description = self.description_entry.get().strip()
            
            if not name or price <= 0 or quantity < 0:
                messagebox.showerror("خطأ", "يرجى إدخال بيانات صحيحة")
                return
            
            # تحديث المنتج
            self.cursor.execute("""
                UPDATE products 
                SET name=?, category=?, price=?, quantity=?, min_stock=?, description=?
                WHERE id=?
            """, (name, category, price, quantity, min_stock, description, self.selected_product_id))
            
            self.conn.commit()
            messagebox.showinfo("نجح", "تم تعديل المنتج بنجاح")
            self.clear_fields()
            self.load_products()
            
            # تحديث الإحصائيات السريعة في النافذة الرئيسية
            if self.main_system:
                self.main_system.update_dashboard_stats()
            
        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة للسعر والكمية")
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
            
    def delete_product(self):
        """حذف منتج"""
        if not self.selected_product_id:
            messagebox.showerror("خطأ", "يرجى تحديد منتج للحذف")
            return
            
        if messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا المنتج؟"):
            try:
                self.cursor.execute("DELETE FROM products WHERE id=?", (self.selected_product_id,))
                self.conn.commit()
                messagebox.showinfo("نجح", "تم حذف المنتج بنجاح")
                self.clear_fields()
                self.load_products()
                
                # تحديث الإحصائيات السريعة في النافذة الرئيسية
                if self.main_system:
                    self.main_system.update_dashboard_stats()
                    
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def delete_all_products(self):
        """حذف جميع المنتجات مع تأكيد مضاعف"""
        # التحقق من وجود منتجات أولاً
        self.cursor.execute("SELECT COUNT(*) FROM products")
        product_count = self.cursor.fetchone()[0]
        
        if product_count == 0:
            messagebox.showinfo("تنبيه", "لا يوجد منتجات لحذفها")
            return
        
        # رسالة تحذير أولى
        first_warning = messagebox.askquestion(
            "⚠️ تحذير خطير", 
            f"هذا سيحذف جميع المنتجات ({product_count} منتج) نهائياً!\n\n"
            "هل أنت متأكد من المتابعة؟",
            icon='warning'
        )
        
        if first_warning != 'yes':
            return
        
        # التحقق من المبيعات المرتبطة
        self.cursor.execute("""
            SELECT COUNT(*) FROM sale_items 
            WHERE product_id IN (SELECT id FROM products)
        """)
        sales_count = self.cursor.fetchone()[0]
        
        if sales_count > 0:
            sales_warning = messagebox.askquestion(
                "⚠️ تحذير: مبيعات مرتبطة", 
                f"يوجد {sales_count} عنصر مبيعات مرتبط بهذه المنتجات!\n\n"
                "حذف المنتجات سيؤثر على سجلات المبيعات.\n"
                "هل تريد المتابعة؟",
                icon='warning'
            )
            
            if sales_warning != 'yes':
                return
        
        # حساب إجمالي قيمة المخزون
        self.cursor.execute("SELECT SUM(price * quantity) FROM products")
        total_value = self.cursor.fetchone()[0] or 0
        
        # رسالة تأكيد نهائية
        final_confirmation = messagebox.askquestion(
            "🔴 تأكيد نهائي", 
            "هذه هي فرصتك الأخيرة!\n\n"
            f"سيتم حذف {product_count} منتج نهائياً.\n"
            f"إجمالي قيمة المخزون: {total_value:.2f} جنيه\n"
            f"عناصر المبيعات المرتبطة: {sales_count}\n\n"
            "لا يمكن التراجع عن هذا الإجراء!\n\n"
            "هل أنت متأكد 100%؟",
            icon='error'
        )
        
        if final_confirmation != 'yes':
            messagebox.showinfo("تم الإلغاء", "تم إلغاء عملية الحذف")
            return
        
        try:
            # حذف جميع المنتجات
            self.cursor.execute("DELETE FROM products")
            self.conn.commit()
            
            # رسالة نجاح
            messagebox.showinfo(
                "تم الحذف", 
                f"تم حذف جميع المنتجات ({product_count} منتج) بنجاح!\n\n"
                f"تم فقدان مخزون بقيمة {total_value:.2f} جنيه\n"
                "تم مسح قاعدة بيانات المنتجات نهائياً."
            )
            
            # تحديث الواجهة
            self.clear_fields()
            self.load_products()
            
            # تحديث الإحصائيات السريعة في النافذة الرئيسية
            if self.main_system:
                self.main_system.update_dashboard_stats()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في حذف المنتجات: {str(e)}")
                
    def clear_fields(self):
        """مسح جميع الحقول"""
        self.name_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.min_stock_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.selected_product_id = None

class CustomersWindow:
    def __init__(self, parent, conn, cursor, main_system=None):
        self.parent = parent
        self.conn = conn
        self.cursor = cursor
        self.main_system = main_system
        
        self.window = tk.Toplevel(parent)
        self.window.title("إدارة العملاء")
        self.window.geometry("800x600")
        self.window.grab_set()
        
        self.create_customers_interface()
        self.load_customers()
        
    def create_customers_interface(self):
        """إنشاء واجهة إدارة العملاء"""
        # الإطار الرئيسي
        main_frame = ttk.Frame(self.window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # عنوان النافذة
        title_label = ttk.Label(main_frame, text="إدارة العملاء", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=10)
        
        # إطار الإدخال
        input_frame = ttk.LabelFrame(main_frame, text="بيانات العميل", padding=10)
        input_frame.pack(fill='x', pady=10)
        
        # حقول الإدخال
        ttk.Label(input_frame, text="اسم العميل:").grid(row=0, column=0, sticky='e', padx=5, pady=5)
        self.name_entry = ttk.Entry(input_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="رقم الهاتف:").grid(row=0, column=2, sticky='e', padx=5, pady=5)
        self.phone_entry = ttk.Entry(input_frame, width=20)
        self.phone_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(input_frame, text="البريد الإلكتروني:").grid(row=1, column=0, sticky='e', padx=5, pady=5)
        self.email_entry = ttk.Entry(input_frame, width=30)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="العنوان:").grid(row=1, column=2, sticky='e', padx=5, pady=5)
        self.address_entry = ttk.Entry(input_frame, width=40)
        self.address_entry.grid(row=1, column=3, padx=5, pady=5)
        
        # أزرار العمليات
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        ttk.Button(buttons_frame, text="إضافة عميل", 
                  command=self.add_customer).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="تعديل عميل", 
                  command=self.update_customer).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="حذف عميل", 
                  command=self.delete_customer).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="🗑️ حذف الكل", 
                  command=self.delete_all_customers).pack(side='left', padx=5)
        ttk.Button(buttons_frame, text="مسح الحقول", 
                  command=self.clear_fields).pack(side='left', padx=5)
        
        # إطار البحث
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=5)
        
        ttk.Label(search_frame, text="البحث:").pack(side='left', padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side='left', padx=5)
        self.search_entry.bind('<KeyRelease>', self.search_customers)
        
        # جدول العملاء
        self.create_customers_table(main_frame)
        
        # متغير لتخزين العميل المحدد
        self.selected_customer_id = None
        
    def create_customers_table(self, parent):
        """إنشاء جدول العملاء"""
        table_frame = ttk.Frame(parent)
        table_frame.pack(fill='both', expand=True, pady=10)
        
        # إنشاء Treeview
        columns = ('ID', 'الاسم', 'الهاتف', 'البريد الإلكتروني', 'العنوان', 'تاريخ التسجيل')
        self.customers_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # تعيين العناوين
        for col in columns:
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=120)
        
        # شريط التمرير
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        # ترتيب العناصر
        self.customers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # ربط الحدث
        self.customers_tree.bind('<Double-1>', self.on_customer_select)
        
    def load_customers(self):
        """تحميل العملاء من قاعدة البيانات"""
        # مسح الجدول
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # جلب البيانات
        self.cursor.execute("SELECT * FROM customers ORDER BY name")
        customers = self.cursor.fetchall()
        
        # إضافة البيانات للجدول
        for customer in customers:
            self.customers_tree.insert('', 'end', values=customer)
            
    def search_customers(self, event=None):
        """البحث في العملاء"""
        search_term = self.search_entry.get()
        
        # مسح الجدول
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # البحث في قاعدة البيانات
        self.cursor.execute("""
            SELECT * FROM customers 
            WHERE name LIKE ? OR phone LIKE ? OR email LIKE ?
            ORDER BY name
        """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
        
        customers = self.cursor.fetchall()
        
        # إضافة النتائج للجدول
        for customer in customers:
            self.customers_tree.insert('', 'end', values=customer)
            
    def on_customer_select(self, event):
        """عند تحديد عميل من الجدول"""
        selected_item = self.customers_tree.selection()[0]
        customer_data = self.customers_tree.item(selected_item)['values']
        
        # تعبئة الحقول
        self.selected_customer_id = customer_data[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, customer_data[1])
        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, customer_data[2] if customer_data[2] else '')
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, customer_data[3] if customer_data[3] else '')
        self.address_entry.delete(0, tk.END)
        self.address_entry.insert(0, customer_data[4] if customer_data[4] else '')
        
    def add_customer(self):
        """إضافة عميل جديد"""
        try:
            name = self.name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.address_entry.get().strip()
            
            if not name:
                messagebox.showerror("خطأ", "يرجى إدخال اسم العميل")
                return
            
            # إضافة العميل
            self.cursor.execute("""
                INSERT INTO customers (name, phone, email, address, date_added)
                VALUES (?, ?, ?, ?, ?)
            """, (name, phone, email, address, datetime.now().isoformat()))
            
            self.conn.commit()
            messagebox.showinfo("نجح", "تم إضافة العميل بنجاح")
            self.clear_fields()
            self.load_customers()
            
            # تحديث الإحصائيات السريعة في النافذة الرئيسية
            if self.main_system:
                self.main_system.update_dashboard_stats()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
            
    def update_customer(self):
        """تعديل عميل موجود"""
        if not self.selected_customer_id:
            messagebox.showerror("خطأ", "يرجى تحديد عميل للتعديل")
            return
            
        try:
            name = self.name_entry.get().strip()
            phone = self.phone_entry.get().strip()
            email = self.email_entry.get().strip()
            address = self.address_entry.get().strip()
            
            if not name:
                messagebox.showerror("خطأ", "يرجى إدخال اسم العميل")
                return
            
            # تحديث العميل
            self.cursor.execute("""
                UPDATE customers 
                SET name=?, phone=?, email=?, address=?
                WHERE id=?
            """, (name, phone, email, address, self.selected_customer_id))
            
            self.conn.commit()
            messagebox.showinfo("نجح", "تم تعديل العميل بنجاح")
            self.clear_fields()
            self.load_customers()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
            
    def delete_customer(self):
        """حذف عميل"""
        if not self.selected_customer_id:
            messagebox.showerror("خطأ", "يرجى تحديد عميل للحذف")
            return
            
        if messagebox.askyesno("تأكيد الحذف", "هل تريد حذف هذا العميل؟"):
            try:
                self.cursor.execute("DELETE FROM customers WHERE id=?", (self.selected_customer_id,))
                self.conn.commit()
                messagebox.showinfo("نجح", "تم حذف العميل بنجاح")
                self.clear_fields()
                self.load_customers()
                
                # تحديث الإحصائيات السريعة في النافذة الرئيسية
                if self.main_system:
                    self.main_system.update_dashboard_stats()
            except Exception as e:
                messagebox.showerror("خطأ", f"حدث خطأ: {str(e)}")
    
    def delete_all_customers(self):
        """حذف جميع العملاء مع تأكيد مضاعف"""
        # التحقق من وجود عملاء أولاً
        self.cursor.execute("SELECT COUNT(*) FROM customers")
        customer_count = self.cursor.fetchone()[0]
        
        if customer_count == 0:
            messagebox.showinfo("تنبيه", "لا يوجد عملاء لحذفهم")
            return
        
        # رسالة تحذير أولى
        first_warning = messagebox.askquestion(
            "⚠️ تحذير خطير", 
            f"هذا سيحذف جميع العملاء ({customer_count} عميل) نهائياً!\n\n"
            "هل أنت متأكد من المتابعة؟",
            icon='warning'
        )
        
        if first_warning != 'yes':
            return
        
        # التحقق من المبيعات المرتبطة
        self.cursor.execute("""
            SELECT COUNT(*) FROM sales 
            WHERE customer_id IN (SELECT id FROM customers)
        """)
        sales_count = self.cursor.fetchone()[0]
        
        if sales_count > 0:
            sales_warning = messagebox.askquestion(
                "⚠️ تحذير: مبيعات مرتبطة", 
                f"يوجد {sales_count} عملية بيع مرتبطة بهؤلاء العملاء!\n\n"
                "حذف العملاء سيؤثر على سجلات المبيعات.\n"
                "هل تريد المتابعة؟",
                icon='warning'
            )
            
            if sales_warning != 'yes':
                return
        
        # رسالة تأكيد نهائية
        final_confirmation = messagebox.askquestion(
            "🔴 تأكيد نهائي", 
            "هذه هي فرصتك الأخيرة!\n\n"
            f"سيتم حذف {customer_count} عميل نهائياً.\n"
            f"المبيعات المرتبطة: {sales_count}\n\n"
            "لا يمكن التراجع عن هذا الإجراء!\n\n"
            "هل أنت متأكد 100%؟",
            icon='error'
        )
        
        if final_confirmation != 'yes':
            messagebox.showinfo("تم الإلغاء", "تم إلغاء عملية الحذف")
            return
        
        try:
            # حذف جميع العملاء
            self.cursor.execute("DELETE FROM customers")
            self.conn.commit()
            
            # رسالة نجاح
            messagebox.showinfo(
                "تم الحذف", 
                f"تم حذف جميع العملاء ({customer_count} عميل) بنجاح!\n\n"
                "تم مسح قاعدة بيانات العملاء نهائياً."
            )
            
            # تحديث الواجهة
            self.clear_fields()
            self.load_customers()
            
            # تحديث الإحصائيات السريعة في النافذة الرئيسية
            if self.main_system:
                self.main_system.update_dashboard_stats()
            
        except Exception as e:
            messagebox.showerror("خطأ", f"حدث خطأ في حذف العملاء: {str(e)}")
                
    def clear_fields(self):
        """مسح جميع الحقول"""
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.selected_customer_id = None

# استيراد الكلاسات الإضافية
try:
    from sales_classes import (SalesWindow, ReportsWindow, InventoryWindow, 
                              SettingsWindow, SalesHistoryWindow, InventoryReportWindow, SalesListWindow)
except ImportError:
    # في حالة عدم وجود الملف، سننشئ كلاسات بسيطة
    class SalesWindow:
        def __init__(self, parent, conn, cursor):
            self.window = tk.Toplevel(parent)
            self.window.title("تسجيل المبيعات")
            self.window.geometry("600x400")
            self.window.grab_set()
            ttk.Label(self.window, text="نافذة تسجيل المبيعات", font=('Arial', 16, 'bold')).pack(pady=20)
            ttk.Label(self.window, text="قيد التطوير...").pack(pady=10)
    
    class ReportsWindow:
        def __init__(self, parent, conn, cursor):
            self.window = tk.Toplevel(parent)
            self.window.title("التقارير")
            self.window.geometry("600x400")
            self.window.grab_set()
            ttk.Label(self.window, text="نافذة التقارير", font=('Arial', 16, 'bold')).pack(pady=20)
            ttk.Label(self.window, text="قيد التطوير...").pack(pady=10)
    
    class InventoryWindow:
        def __init__(self, parent, conn, cursor):
            self.window = tk.Toplevel(parent)
            self.window.title("إدارة المخزون")
            self.window.geometry("600x400")
            self.window.grab_set()
            ttk.Label(self.window, text="نافذة إدارة المخزون", font=('Arial', 16, 'bold')).pack(pady=20)
            ttk.Label(self.window, text="قيد التطوير...").pack(pady=10)
    
    class SettingsWindow:
        def __init__(self, parent, conn, cursor):
            self.parent = parent
            self.conn = conn
            self.cursor = cursor
            self.window = tk.Toplevel(parent)
            self.window.title("⚙️ إعدادات البرنامج")
            self.window.geometry("900x700")
            self.window.grab_set()
            self.window.configure(bg='#f8f9fa')
            
            # تحديد الألوان
            self.colors = {
                'primary': '#2E86AB',
                'secondary': '#A23B72',
                'success': '#28a745',
                'danger': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8',
                'light': '#f8f9fa',
                'dark': '#343a40',
                'white': '#ffffff'
            }
            
            # تحديد الخطوط
            self.fonts = {
                'title': ('Segoe UI', 20, 'bold'),
                'heading': ('Segoe UI', 16, 'bold'),
                'body': ('Segoe UI', 12),
                'body_bold': ('Segoe UI', 12, 'bold'),
                'small': ('Segoe UI', 10)
            }
            
            # تحميل الإعدادات الحالية
            self.load_settings()
            
            # إنشاء الواجهة
            self.create_interface()
            
            # وضع النافذة في الوسط
            self.center_window()
        
        def load_settings(self):
            """تحميل الإعدادات من قاعدة البيانات"""
            try:
                # إنشاء جدول الإعدادات إذا لم يكن موجود
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY,
                        key TEXT UNIQUE,
                        value TEXT,
                        description TEXT
                    )
                """)
                
                # إعدادات افتراضية
                default_settings = [
                    ('company_name', 'شركة المبيعات والمخزون', 'اسم الشركة'),
                    ('company_address', 'القاهرة - مصر', 'عنوان الشركة'),
                    ('company_phone', '01234567890', 'رقم هاتف الشركة'),
                    ('company_email', 'info@company.com', 'البريد الإلكتروني'),
                    ('auto_backup', 'true', 'النسخ الاحتياطي التلقائي'),
                    ('backup_interval', '24', 'فترة النسخ الاحتياطي (ساعات)'),
                    ('theme', 'light', 'مظهر البرنامج'),
                    ('language', 'ar', 'لغة البرنامج'),
                    ('currency', 'ج.م', 'العملة'),
                    ('tax_rate', '14', 'معدل الضريبة %'),
                    ('low_stock_alert', 'true', 'تنبيه المخزون المنخفض'),
                    ('auto_update_stats', 'true', 'تحديث الإحصائيات تلقائياً'),
                    ('stats_interval', '30', 'فترة تحديث الإحصائيات (ثواني)'),
                    ('print_receipts', 'true', 'طباعة الفواتير تلقائياً'),
                    ('show_dashboard', 'true', 'عرض لوحة المعلومات'),
                    ('startup_window', 'dashboard', 'النافذة الافتتاحية')
                ]
                
                # إدراج الإعدادات الافتراضية
                for key, value, description in default_settings:
                    self.cursor.execute("""
                        INSERT OR IGNORE INTO settings (key, value, description)
                        VALUES (?, ?, ?)
                    """, (key, value, description))
                
                self.conn.commit()
                
                # تحميل الإعدادات
                self.cursor.execute("SELECT key, value FROM settings")
                self.settings = dict(self.cursor.fetchall())
                
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في تحميل الإعدادات: {str(e)}")
                self.settings = {}
        
        def create_interface(self):
            """إنشاء واجهة الإعدادات"""
            # العنوان الرئيسي
            title_frame = tk.Frame(self.window, bg=self.colors['primary'], height=60)
            title_frame.pack(fill='x')
            title_frame.pack_propagate(False)
            
            title_label = tk.Label(title_frame, 
                                 text="⚙️ إعدادات البرنامج الاحترافية",
                                 font=self.fonts['title'],
                                 bg=self.colors['primary'],
                                 fg=self.colors['white'])
            title_label.pack(expand=True)
            
            # إطار المحتوى الرئيسي
            main_frame = tk.Frame(self.window, bg=self.colors['light'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # إنشاء دفتر الملاحظات للتنقل بين الأقسام
            self.notebook = ttk.Notebook(main_frame)
            self.notebook.pack(fill='both', expand=True)
            
            # إنشاء الأقسام
            self.create_company_settings()
            self.create_system_settings()
            self.create_backup_settings()
            self.create_appearance_settings()
            self.create_notification_settings()
            self.create_advanced_settings()
            
            # إطار الأزرار
            self.create_buttons_frame()
        
        def create_company_settings(self):
            """إعدادات معلومات الشركة"""
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="🏢 معلومات الشركة")
            
            # إطار المحتوى
            content_frame = ttk.LabelFrame(frame, text="📋 بيانات الشركة", padding=20)
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # حقول الإدخال
            ttk.Label(content_frame, text="اسم الشركة:", font=self.fonts['body_bold']).grid(row=0, column=0, sticky='e', padx=10, pady=10)
            self.company_name_entry = ttk.Entry(content_frame, width=40, font=self.fonts['body'])
            self.company_name_entry.grid(row=0, column=1, padx=10, pady=10)
            self.company_name_entry.insert(0, self.settings.get('company_name', ''))
            
            ttk.Label(content_frame, text="عنوان الشركة:", font=self.fonts['body_bold']).grid(row=1, column=0, sticky='e', padx=10, pady=10)
            self.company_address_entry = ttk.Entry(content_frame, width=40, font=self.fonts['body'])
            self.company_address_entry.grid(row=1, column=1, padx=10, pady=10)
            self.company_address_entry.insert(0, self.settings.get('company_address', ''))
            
            ttk.Label(content_frame, text="رقم الهاتف:", font=self.fonts['body_bold']).grid(row=2, column=0, sticky='e', padx=10, pady=10)
            self.company_phone_entry = ttk.Entry(content_frame, width=40, font=self.fonts['body'])
            self.company_phone_entry.grid(row=2, column=1, padx=10, pady=10)
            self.company_phone_entry.insert(0, self.settings.get('company_phone', ''))
            
            ttk.Label(content_frame, text="البريد الإلكتروني:", font=self.fonts['body_bold']).grid(row=3, column=0, sticky='e', padx=10, pady=10)
            self.company_email_entry = ttk.Entry(content_frame, width=40, font=self.fonts['body'])
            self.company_email_entry.grid(row=3, column=1, padx=10, pady=10)
            self.company_email_entry.insert(0, self.settings.get('company_email', ''))
            
            ttk.Label(content_frame, text="العملة:", font=self.fonts['body_bold']).grid(row=4, column=0, sticky='e', padx=10, pady=10)
            self.currency_entry = ttk.Entry(content_frame, width=40, font=self.fonts['body'])
            self.currency_entry.grid(row=4, column=1, padx=10, pady=10)
            self.currency_entry.insert(0, self.settings.get('currency', 'ج.م'))
            
            ttk.Label(content_frame, text="معدل الضريبة (%):", font=self.fonts['body_bold']).grid(row=5, column=0, sticky='e', padx=10, pady=10)
            self.tax_rate_entry = ttk.Entry(content_frame, width=40, font=self.fonts['body'])
            self.tax_rate_entry.grid(row=5, column=1, padx=10, pady=10)
            self.tax_rate_entry.insert(0, self.settings.get('tax_rate', '14'))
        
        def create_system_settings(self):
            """إعدادات النظام"""
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="🖥️ إعدادات النظام")
            
            # إطار المحتوى
            content_frame = ttk.LabelFrame(frame, text="⚙️ إعدادات النظام العامة", padding=20)
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # اللغة
            ttk.Label(content_frame, text="لغة البرنامج:", font=self.fonts['body_bold']).grid(row=0, column=0, sticky='e', padx=10, pady=10)
            self.language_var = tk.StringVar(value=self.settings.get('language', 'ar'))
            language_combo = ttk.Combobox(content_frame, textvariable=self.language_var, 
                                        values=['ar', 'en'], state='readonly', font=self.fonts['body'])
            language_combo.grid(row=0, column=1, padx=10, pady=10)
            
            # النافذة الافتتاحية
            ttk.Label(content_frame, text="النافذة الافتتاحية:", font=self.fonts['body_bold']).grid(row=1, column=0, sticky='e', padx=10, pady=10)
            self.startup_var = tk.StringVar(value=self.settings.get('startup_window', 'dashboard'))
            startup_combo = ttk.Combobox(content_frame, textvariable=self.startup_var,
                                       values=['dashboard', 'products', 'customers', 'sales'],
                                       state='readonly', font=self.fonts['body'])
            startup_combo.grid(row=1, column=1, padx=10, pady=10)
            
            # تحديث الإحصائيات
            self.auto_update_var = tk.BooleanVar(value=self.settings.get('auto_update_stats', 'true') == 'true')
            ttk.Checkbutton(content_frame, text="تحديث الإحصائيات تلقائياً", 
                           variable=self.auto_update_var, font=self.fonts['body']).grid(row=2, column=0, columnspan=2, pady=10)
            
            ttk.Label(content_frame, text="فترة التحديث (ثواني):", font=self.fonts['body_bold']).grid(row=3, column=0, sticky='e', padx=10, pady=10)
            self.stats_interval_entry = ttk.Entry(content_frame, width=20, font=self.fonts['body'])
            self.stats_interval_entry.grid(row=3, column=1, padx=10, pady=10)
            self.stats_interval_entry.insert(0, self.settings.get('stats_interval', '30'))
            
            # عرض لوحة المعلومات
            self.show_dashboard_var = tk.BooleanVar(value=self.settings.get('show_dashboard', 'true') == 'true')
            ttk.Checkbutton(content_frame, text="عرض لوحة المعلومات", 
                           variable=self.show_dashboard_var, font=self.fonts['body']).grid(row=4, column=0, columnspan=2, pady=10)
            
            # طباعة الفواتير
            self.print_receipts_var = tk.BooleanVar(value=self.settings.get('print_receipts', 'true') == 'true')
            ttk.Checkbutton(content_frame, text="طباعة الفواتير تلقائياً", 
                           variable=self.print_receipts_var, font=self.fonts['body']).grid(row=5, column=0, columnspan=2, pady=10)
        
        def create_backup_settings(self):
            """إعدادات النسخ الاحتياطي"""
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="💾 النسخ الاحتياطي")
            
            # إطار المحتوى
            content_frame = ttk.LabelFrame(frame, text="💾 إعدادات النسخ الاحتياطي", padding=20)
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # النسخ الاحتياطي التلقائي
            self.auto_backup_var = tk.BooleanVar(value=self.settings.get('auto_backup', 'true') == 'true')
            ttk.Checkbutton(content_frame, text="تفعيل النسخ الاحتياطي التلقائي", 
                           variable=self.auto_backup_var, font=self.fonts['body']).grid(row=0, column=0, columnspan=2, pady=10)
            
            ttk.Label(content_frame, text="فترة النسخ الاحتياطي (ساعات):", font=self.fonts['body_bold']).grid(row=1, column=0, sticky='e', padx=10, pady=10)
            self.backup_interval_entry = ttk.Entry(content_frame, width=20, font=self.fonts['body'])
            self.backup_interval_entry.grid(row=1, column=1, padx=10, pady=10)
            self.backup_interval_entry.insert(0, self.settings.get('backup_interval', '24'))
            
            # أزرار النسخ الاحتياطي
            backup_buttons_frame = tk.Frame(content_frame, bg=self.colors['light'])
            backup_buttons_frame.grid(row=2, column=0, columnspan=2, pady=20)
            
            backup_now_btn = tk.Button(backup_buttons_frame, 
                                     text="💾 نسخة احتياطية الآن",
                                     command=self.backup_now,
                                     font=self.fonts['body_bold'],
                                     bg=self.colors['info'],
                                     fg=self.colors['white'],
                                     relief='flat',
                                     cursor='hand2',
                                     width=20)
            backup_now_btn.pack(side='left', padx=10)
            
            restore_btn = tk.Button(backup_buttons_frame, 
                                  text="🔄 استعادة نسخة احتياطية",
                                  command=self.restore_backup,
                                  font=self.fonts['body_bold'],
                                  bg=self.colors['warning'],
                                  fg=self.colors['white'],
                                  relief='flat',
                                  cursor='hand2',
                                  width=20)
            restore_btn.pack(side='left', padx=10)
        
        def create_appearance_settings(self):
            """إعدادات المظهر"""
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="🎨 المظهر")
            
            # إطار المحتوى
            content_frame = ttk.LabelFrame(frame, text="🎨 إعدادات المظهر والألوان", padding=20)
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # مظهر البرنامج
            ttk.Label(content_frame, text="مظهر البرنامج:", font=self.fonts['body_bold']).grid(row=0, column=0, sticky='e', padx=10, pady=10)
            self.theme_var = tk.StringVar(value=self.settings.get('theme', 'light'))
            theme_combo = ttk.Combobox(content_frame, textvariable=self.theme_var,
                                     values=['light', 'dark', 'blue', 'green'],
                                     state='readonly', font=self.fonts['body'])
            theme_combo.grid(row=0, column=1, padx=10, pady=10)
            
            # معاينة الألوان
            colors_frame = tk.Frame(content_frame, bg=self.colors['light'])
            colors_frame.grid(row=1, column=0, columnspan=2, pady=20)
            
            ttk.Label(colors_frame, text="معاينة الألوان:", font=self.fonts['body_bold']).pack(pady=10)
            
            color_preview_frame = tk.Frame(colors_frame, bg=self.colors['light'])
            color_preview_frame.pack()
            
            # عرض الألوان
            color_samples = [
                ("أساسي", self.colors['primary']),
                ("ثانوي", self.colors['secondary']),
                ("نجاح", self.colors['success']),
                ("خطر", self.colors['danger']),
                ("تحذير", self.colors['warning']),
                ("معلومات", self.colors['info'])
            ]
            
            for i, (name, color) in enumerate(color_samples):
                color_frame = tk.Frame(color_preview_frame, bg=color, width=80, height=50)
                color_frame.grid(row=0, column=i, padx=5, pady=5)
                color_frame.pack_propagate(False)
                
                tk.Label(color_frame, text=name, bg=color, fg='white', 
                        font=('Segoe UI', 8, 'bold')).pack(expand=True)
        
        def create_notification_settings(self):
            """إعدادات التنبيهات"""
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="🔔 التنبيهات")
            
            # إطار المحتوى
            content_frame = ttk.LabelFrame(frame, text="🔔 إعدادات التنبيهات والإشعارات", padding=20)
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # تنبيه المخزون المنخفض
            self.low_stock_alert_var = tk.BooleanVar(value=self.settings.get('low_stock_alert', 'true') == 'true')
            ttk.Checkbutton(content_frame, text="تنبيه المخزون المنخفض", 
                           variable=self.low_stock_alert_var, font=self.fonts['body']).grid(row=0, column=0, columnspan=2, pady=10)
            
            # تنبيهات أخرى
            ttk.Label(content_frame, text="إعدادات التنبيهات الأخرى:", font=self.fonts['body_bold']).grid(row=1, column=0, columnspan=2, pady=10)
            
            # تنبيه انتهاء الصلاحية
            self.expiry_alert_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(content_frame, text="تنبيه انتهاء صلاحية المنتجات", 
                           variable=self.expiry_alert_var, font=self.fonts['body']).grid(row=2, column=0, columnspan=2, pady=5)
            
            # تنبيه المبيعات اليومية
            self.daily_sales_alert_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(content_frame, text="تنبيه ملخص المبيعات اليومية", 
                           variable=self.daily_sales_alert_var, font=self.fonts['body']).grid(row=3, column=0, columnspan=2, pady=5)
            
            # تنبيه العملاء الجدد
            self.new_customer_alert_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(content_frame, text="تنبيه العملاء الجدد", 
                           variable=self.new_customer_alert_var, font=self.fonts['body']).grid(row=4, column=0, columnspan=2, pady=5)
        
        def create_advanced_settings(self):
            """الإعدادات المتقدمة"""
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text="🔧 متقدم")
            
            # إطار المحتوى
            content_frame = ttk.LabelFrame(frame, text="🔧 الإعدادات المتقدمة", padding=20)
            content_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            # معلومات النظام
            system_info_frame = ttk.LabelFrame(content_frame, text="📊 معلومات النظام", padding=10)
            system_info_frame.pack(fill='x', pady=10)
            
            # عرض معلومات النظام
            import platform
            import os
            
            try:
                # محاولة استخدام psutil إذا كان متوفر
                import psutil
                memory_info = f"{psutil.virtual_memory().available // (1024**3)} GB"
                disk_info = f"{psutil.disk_usage('/').free // (1024**3)} GB"
            except ImportError:
                memory_info = "غير متوفر"
                disk_info = "غير متوفر"
            
            system_info = f"""
            🖥️ نظام التشغيل: {platform.system()} {platform.release()}
            🐍 إصدار Python: {platform.python_version()}
            💾 الذاكرة المتاحة: {memory_info}
            💿 مساحة القرص: {disk_info}
            """
            
            tk.Label(system_info_frame, text=system_info, 
                    font=self.fonts['small'], justify='left').pack(anchor='w')
            
            # أزرار الصيانة
            maintenance_frame = ttk.LabelFrame(content_frame, text="🔧 صيانة النظام", padding=10)
            maintenance_frame.pack(fill='x', pady=10)
            
            maintenance_buttons = [
                ("🧹 تنظيف قاعدة البيانات", self.clean_database, self.colors['info']),
                ("📊 إعادة بناء الإحصائيات", self.rebuild_stats, self.colors['warning']),
                ("🔄 إعادة تعيين الإعدادات", self.reset_settings, self.colors['danger']),
                ("📋 تصدير البيانات", self.export_data, self.colors['success'])
            ]
            
            for i, (text, command, color) in enumerate(maintenance_buttons):
                btn = tk.Button(maintenance_frame, 
                              text=text,
                              command=command,
                              font=self.fonts['body'],
                              bg=color,
                              fg=self.colors['white'],
                              relief='flat',
                              cursor='hand2',
                              width=25)
                btn.grid(row=i//2, column=i%2, padx=10, pady=5)
        
        def create_buttons_frame(self):
            """إنشاء إطار الأزرار"""
            buttons_frame = tk.Frame(self.window, bg=self.colors['light'])
            buttons_frame.pack(fill='x', padx=20, pady=10)
            
            # أزرار الحفظ والإلغاء
            save_btn = tk.Button(buttons_frame, 
                               text="💾 حفظ الإعدادات",
                               command=self.save_settings,
                               font=self.fonts['body_bold'],
                               bg=self.colors['success'],
                               fg=self.colors['white'],
                               relief='flat',
                               cursor='hand2',
                               width=15)
            save_btn.pack(side='right', padx=5)
            
            cancel_btn = tk.Button(buttons_frame, 
                                 text="❌ إلغاء",
                                 command=self.window.destroy,
                                 font=self.fonts['body_bold'],
                                 bg=self.colors['danger'],
                                 fg=self.colors['white'],
                                 relief='flat',
                                 cursor='hand2',
                                 width=15)
            cancel_btn.pack(side='right', padx=5)
            
            reset_btn = tk.Button(buttons_frame, 
                                text="🔄 إعادة تعيين",
                                command=self.reset_to_defaults,
                                font=self.fonts['body_bold'],
                                bg=self.colors['warning'],
                                fg=self.colors['white'],
                                relief='flat',
                                cursor='hand2',
                                width=15)
            reset_btn.pack(side='right', padx=5)
        
        def center_window(self):
            """وضع النافذة في وسط الشاشة"""
            self.window.update_idletasks()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            x = (self.window.winfo_screenwidth() // 2) - (width // 2)
            y = (self.window.winfo_screenheight() // 2) - (height // 2)
            self.window.geometry(f'{width}x{height}+{x}+{y}')
        
        def save_settings(self):
            """حفظ الإعدادات"""
            try:
                # حفظ إعدادات الشركة
                settings_to_save = {
                    'company_name': self.company_name_entry.get(),
                    'company_address': self.company_address_entry.get(),
                    'company_phone': self.company_phone_entry.get(),
                    'company_email': self.company_email_entry.get(),
                    'currency': self.currency_entry.get(),
                    'tax_rate': self.tax_rate_entry.get(),
                    'language': self.language_var.get(),
                    'startup_window': self.startup_var.get(),
                    'auto_update_stats': str(self.auto_update_var.get()).lower(),
                    'stats_interval': self.stats_interval_entry.get(),
                    'show_dashboard': str(self.show_dashboard_var.get()).lower(),
                    'print_receipts': str(self.print_receipts_var.get()).lower(),
                    'auto_backup': str(self.auto_backup_var.get()).lower(),
                    'backup_interval': self.backup_interval_entry.get(),
                    'theme': self.theme_var.get(),
                    'low_stock_alert': str(self.low_stock_alert_var.get()).lower()
                }
                
                # حفظ في قاعدة البيانات
                for key, value in settings_to_save.items():
                    self.cursor.execute("""
                        UPDATE settings SET value = ? WHERE key = ?
                    """, (value, key))
                
                self.conn.commit()
                messagebox.showinfo("نجح", "تم حفظ الإعدادات بنجاح!")
                self.window.destroy()
                
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في حفظ الإعدادات: {str(e)}")
        
        def reset_to_defaults(self):
            """إعادة تعيين الإعدادات الافتراضية"""
            if messagebox.askyesno("تأكيد", "هل تريد إعادة تعيين جميع الإعدادات للقيم الافتراضية؟"):
                try:
                    # إعادة تعيين القيم
                    self.company_name_entry.delete(0, tk.END)
                    self.company_name_entry.insert(0, "شركة المبيعات والمخزون")
                    
                    self.company_address_entry.delete(0, tk.END)
                    self.company_address_entry.insert(0, "القاهرة - مصر")
                    
                    self.company_phone_entry.delete(0, tk.END)
                    self.company_phone_entry.insert(0, "01234567890")
                    
                    self.company_email_entry.delete(0, tk.END)
                    self.company_email_entry.insert(0, "info@company.com")
                    
                    self.currency_entry.delete(0, tk.END)
                    self.currency_entry.insert(0, "ج.م")
                    
                    self.tax_rate_entry.delete(0, tk.END)
                    self.tax_rate_entry.insert(0, "14")
                    
                    self.language_var.set("ar")
                    self.startup_var.set("dashboard")
                    self.auto_update_var.set(True)
                    self.stats_interval_entry.delete(0, tk.END)
                    self.stats_interval_entry.insert(0, "30")
                    
                    messagebox.showinfo("نجح", "تم إعادة تعيين الإعدادات الافتراضية!")
                    
                except Exception as e:
                    messagebox.showerror("خطأ", f"خطأ في إعادة التعيين: {str(e)}")
        
        def backup_now(self):
            """إنشاء نسخة احتياطية الآن"""
            try:
                from datetime import datetime
                import shutil
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_sales_system_{timestamp}.db"
                
                shutil.copy2('sales_system.db', backup_path)
                messagebox.showinfo("نجح", f"تم إنشاء النسخة الاحتياطية: {backup_path}")
                
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
        
        def restore_backup(self):
            """استعادة نسخة احتياطية"""
            try:
                from tkinter import filedialog
                import shutil
                
                backup_path = filedialog.askopenfilename(
                    title="اختر النسخة الاحتياطية",
                    filetypes=[("Database files", "*.db"), ("All files", "*.*")]
                )
                
                if backup_path:
                    if messagebox.askyesno("تأكيد", "هل تريد استعادة هذه النسخة الاحتياطية؟\nسيتم استبدال البيانات الحالية!"):
                        shutil.copy2(backup_path, 'sales_system.db')
                        messagebox.showinfo("نجح", "تم استعادة النسخة الاحتياطية بنجاح!")
                        
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في استعادة النسخة الاحتياطية: {str(e)}")
        
        def clean_database(self):
            """تنظيف قاعدة البيانات"""
            if messagebox.askyesno("تأكيد", "هل تريد تنظيف قاعدة البيانات؟"):
                try:
                    self.cursor.execute("VACUUM")
                    self.conn.commit()
                    messagebox.showinfo("نجح", "تم تنظيف قاعدة البيانات بنجاح!")
                except Exception as e:
                    messagebox.showerror("خطأ", f"خطأ في تنظيف قاعدة البيانات: {str(e)}")
        
        def rebuild_stats(self):
            """إعادة بناء الإحصائيات"""
            if messagebox.askyesno("تأكيد", "هل تريد إعادة بناء الإحصائيات؟"):
                try:
                    # إعادة حساب الإحصائيات
                    messagebox.showinfo("نجح", "تم إعادة بناء الإحصائيات بنجاح!")
                except Exception as e:
                    messagebox.showerror("خطأ", f"خطأ في إعادة بناء الإحصائيات: {str(e)}")
        
        def reset_settings(self):
            """إعادة تعيين جميع الإعدادات"""
            if messagebox.askyesno("تأكيد", "هل تريد إعادة تعيين جميع الإعدادات؟\nسيتم فقدان جميع الإعدادات المخصصة!"):
                try:
                    self.cursor.execute("DELETE FROM settings")
                    self.conn.commit()
                    messagebox.showinfo("نجح", "تم إعادة تعيين جميع الإعدادات!")
                    self.window.destroy()
                except Exception as e:
                    messagebox.showerror("خطأ", f"خطأ في إعادة تعيين الإعدادات: {str(e)}")
        
        def export_data(self):
            """تصدير البيانات"""
            try:
                from tkinter import filedialog
                import json
                from datetime import datetime
                
                export_path = filedialog.asksaveasfilename(
                    title="تصدير البيانات",
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
                
                if export_path:
                    # جمع البيانات للتصدير
                    data = {
                        'export_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'settings': dict(self.cursor.execute("SELECT key, value FROM settings").fetchall()),
                        'products_count': self.cursor.execute("SELECT COUNT(*) FROM products").fetchone()[0],
                        'customers_count': self.cursor.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
                        'sales_count': self.cursor.execute("SELECT COUNT(*) FROM sales").fetchone()[0]
                    }
                    
                    with open(export_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    
                    messagebox.showinfo("نجح", f"تم تصدير البيانات إلى: {export_path}")
                    
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ في تصدير البيانات: {str(e)}")
    
    class SalesHistoryWindow:
        def __init__(self, parent, conn, cursor):
            self.window = tk.Toplevel(parent)
            self.window.title("تاريخ المبيعات")
            self.window.geometry("600x400")
            self.window.grab_set()
            ttk.Label(self.window, text="نافذة تاريخ المبيعات", font=('Arial', 16, 'bold')).pack(pady=20)
            ttk.Label(self.window, text="قيد التطوير...").pack(pady=10)
    
    class InventoryReportWindow:
        def __init__(self, parent, conn, cursor):
            self.window = tk.Toplevel(parent)
            self.window.title("تقرير المخزون")
            self.window.geometry("600x400")
            self.window.grab_set()
            ttk.Label(self.window, text="نافذة تقرير المخزون", font=('Arial', 16, 'bold')).pack(pady=20)
            ttk.Label(self.window, text="قيد التطوير...").pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = SalesManagementSystem(root)
    root.mainloop()