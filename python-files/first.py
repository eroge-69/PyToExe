# --- المكتبات الأساسية ---
import pyodbc # للاتصال بقاعدة بيانات SQL Server
from tkinter import * # لإنشاء واجهة المستخدم الرسومية
from tkinter import messagebox # لعرض مربعات الرسائل
import os # للتعامل مع مسارات الملفات
import configparser # لقراءة وكتابة ملفات الإعدادات
import sys # لاستخدام sys._MEIPASS لدعم PyInstaller
from collections import OrderedDict

# تعريف الخط الافتراضي للقائمة (تم نقله إلى الأعلى لسهولة التعديل)
menu_font = ("Segoe UI", 11, "bold") 

# قائمة أنواع الأسعار المتاحة
PRICE_TYPES = OrderedDict([
    ("whole", "سعر الجملة"),
    ("half", "نصف جملة"),
    ("retail", "سعر المفرق"),
    ("enduser", "سعر المستهلك"),
    ("export", "سعر التصدير"),
    ("vendor", "سعر المورد"),
    ("lastprice", "آخر سعر شراء"),
    ("lastsale", "آخر سعر بيع")
])

# --- 1. دالة مساعدة لمسارات الموارد (للتوافق مع PyInstaller) ---
def resource_path(relative_path):
    """
    الحصول على المسار المطلق للمورد، يعمل في وضع التطوير ومع PyInstaller.
    PyInstaller ينشئ مجلدًا مؤقتًا ويخزن المسار في _MEIPASS.
    """
    try:
        # المسار عند التشغيل كبرنامج مجمع
        base_path = sys._MEIPASS
    except Exception:
        # المسار عند التشغيل في وضع التطوير
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- 2. إعدادات تخزين / قراءة الاتصال بقاعدة البيانات ---
CONFIG_FILE = 'config.ini' # اسم ملف الإعدادات

def save_db_config(server, database, username, password):
    """حفظ إعدادات الاتصال بقاعدة البيانات في ملف config.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    config['DATABASE'] = {
        'server': server,
        'database': database,
        'username': username,
        'password': password
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        messagebox.showinfo("حفظ الإعدادات", "تم حفظ إعدادات قاعدة البيانات بنجاح.")
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل حفظ الإعدادات: {e}")

def save_pricing_config(currency_guid, price_type):
    """حفظ إعدادات العملة والسعر في ملف config.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
    config['PRICING'] = {
        'currency_guid': currency_guid,
        'price_type': price_type
    }
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        messagebox.showinfo("حفظ الإعدادات", "تم حفظ إعدادات العملة والأسعار بنجاح.")
    except Exception as e:
        messagebox.showerror("خطأ", f"فشل حفظ الإعدادات: {e}")

def load_db_config():
    """تحميل إعدادات الاتصال بقاعدة البيانات من ملف config.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
        if 'DATABASE' in config:
            return config['DATABASE']
    return None # إذا لم يتم العثور على الإعدادات

def load_pricing_config():
    """تحميل إعدادات العملة والسعر من ملف config.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE, encoding='utf-8')
        if 'PRICING' in config:
            return config['PRICING']
    return None

# --- 3. دالة الاتصال بقاعدة البيانات ---
def get_db_connection(config_data):
    """
    تحاول إنشاء اتصال بقاعدة البيانات باستخدام بيانات التكوين المقدمة.
    """
    if not config_data:
        # حالة عدم وجود بيانات اتصال
        return None

    server = config_data.get('server')
    database = config_data.get('database')
    username = config_data.get('username')
    password = config_data.get('password')

    # التحقق من أن جميع حقول الاتصال مملوءة
    if not all([server, database, username, password]):
        print("DEBUG: Connection data is incomplete.")
        return None

    # سلسلة الاتصال
    CONNECTION_STRING = (
        f'DRIVER={{ODBC Driver 18 for SQL Server}};' 
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        f'TrustServerCertificate=yes;' # للحماية من مشكلة شهادة SSL/TLS
    )
    try:
        conn = pyodbc.connect(CONNECTION_STRING)
        return conn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        # عرض رسالة خطأ أكثر وضوحًا للمستخدم
        print(f"DEBUG: SQL Connection Error: {ex}") 
        return None
        
def get_latest_exchange_rate(conn, currency_guid):
    """
    جلب أحدث سعر صرف لعملة معينة من جدول mh000.
    """
    if not currency_guid:
        return 1.0 # افتراض أن السعر هو 1 إذا لم يتم اختيار عملة
    try:
        cursor = conn.cursor()
        query = "SELECT TOP 1 CurrencyVal FROM mh000 WHERE CurrencyGUID = ? ORDER BY Date DESC"
        cursor.execute(query, currency_guid)
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return 1.0 # السعر الافتراضي إذا لم يتم العثور على سعر صرف
    except Exception as e:
        print(f"DEBUG: Error fetching exchange rate: {e}")
        return 1.0

# --- 4. شاشة إعدادات الاتصال ---
class SettingsWindow:
    def __init__(self, master, on_save_callback):
        self.master = master
        self.master.title("إعدادات قاعدة البيانات")
        self.master.geometry("600x450")
        self.master.resizable(False, False)
        self.master.configure(bg="#e0e0e0")

        main_frame = Frame(master, padx=15, pady=15, bg="#ffffff", relief="flat", bd=0)
        main_frame.pack(expand=True, fill=BOTH, padx=20, pady=20)

        self.server_var = StringVar()
        self.database_var = StringVar()
        self.username_var = StringVar()
        self.password_var = StringVar()
        self.status_message_var = StringVar()

        existing_config = load_db_config()
        if existing_config:
            self.server_var.set(existing_config.get('server', ''))
            self.database_var.set(existing_config.get('database', ''))
            self.username_var.set(existing_config.get('username', ''))
            self.password_var.set(existing_config.get('password', ''))

        labels_font = ("Segoe UI", 13, "bold")
        entry_font = ("Segoe UI", 13)
        button_font = ("Segoe UI", 12, "bold")

        Label(main_frame, text="الخادم", font=labels_font, bg="#ffffff", fg="#333").grid(row=0, column=1, sticky="e", pady=8, padx=40)
        Entry(main_frame, textvariable=self.server_var, width=35, font=entry_font, bd=1, relief="solid", highlightbackground="#cccccc", highlightthickness=1, justify='left').grid(row=0, column=0, pady=8, padx=10)

        Label(main_frame, text="قاعدة البيانات", font=labels_font, bg="#ffffff", fg="#333").grid(row=1, column=1, sticky="e", pady=8, padx=40)
        Entry(main_frame, textvariable=self.database_var, width=35, font=entry_font, bd=1, relief="solid", highlightbackground="#cccccc", highlightthickness=1, justify='left').grid(row=1, column=0, pady=8, padx=10)

        Label(main_frame, text="اسم المستخدم", font=labels_font, bg="#ffffff", fg="#333").grid(row=2, column=1, sticky="e", pady=8, padx=40)
        Entry(main_frame, textvariable=self.username_var, width=35, font=entry_font, bd=1, relief="solid", highlightbackground="#cccccc", highlightthickness=1, justify='left').grid(row=2, column=0, pady=8, padx=10)

        Label(main_frame, text="كلمة المرور", font=labels_font, bg="#ffffff", fg="#333").grid(row=3, column=1, sticky="e", pady=8, padx=40)
        Entry(main_frame, textvariable=self.password_var, show="*", width=35, font=entry_font, bd=1, relief="solid", highlightbackground="#cccccc", highlightthickness=1, justify='left').grid(row=3, column=0, pady=8, padx=10)

        status_label = Label(main_frame, textvariable=self.status_message_var, font=("Segoe UI", 11, "bold"), fg="#670707", bg="#FFFFFF")
        status_label.grid(row=4, column=0, columnspan=2, pady=5)

        button_frame = Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        Button(button_frame, text="اختبار الاتصال", command=self.test_connection, font=button_font, bg="#007bff", fg="white", relief="flat", bd=0, padx=15, pady=5, activebackground="#0056b3", activeforeground="white").pack(side=LEFT, padx=5)
        Button(button_frame, text="حفظ الإعدادات", command=self.save_settings, font=button_font, bg="#28a745", fg="white", relief="flat", bd=0, padx=15, pady=5, activebackground="#1e7e34", activeforeground="white").pack(side=LEFT, padx=5)

    def test_connection(self):
        """اختبار الاتصال بقاعدة البيانات وعرض النتيجة."""
        config_data = {
            'server': self.server_var.get().strip(),
            'database': self.database_var.get().strip(),
            'username': self.username_var.get().strip(),
            'password': self.password_var.get().strip()
        }
        if not all(config_data.values()):
            self.status_message_var.set("الرجاء تعبئة جميع حقول الاتصال للاختبار.")
            return

        self.status_message_var.set("جاري اختبار الاتصال...")
        self.master.update_idletasks()
        
        conn = get_db_connection(config_data)
        if conn:
            self.status_message_var.set("✅ تم الاتصال بنجاح!")
            conn.close()
        else:
            self.status_message_var.set("❌ فشل الاتصال. تحقق من البيانات أو Driver.")

    def save_settings(self):
        """حفظ إعدادات الاتصال المدخلة."""
        server = self.server_var.get().strip()
        database = self.database_var.get().strip()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not all([server, database, username, password]):
            messagebox.showwarning("إدخال ناقص", "الرجاء تعبئة جميع حقول الاتصال.")
            return
        save_db_config(server, database, username, password)
        if self.on_save_callback:
            self.on_save_callback()
        self.master.destroy()

# --- 5. شاشة إعدادات العملة والسعر ---
class CurrencyPriceSettingsWindow:
    def __init__(self, master, on_save_callback):
        self.master = master
        self.master.title("إعدادات العملة والأسعار")
        self.master.geometry("600x450")
        self.master.resizable(False, False)
        self.master.configure(bg="#e0e0e0")

        self.on_save_callback = on_save_callback
        
        # إطار رئيسي مع بعض التباعد لتحسين الشكل
        main_frame = Frame(master, padx=30, pady=30, bg="#ffffff", relief="flat", bd=0, highlightbackground="#d1d1d1", highlightthickness=1)
        main_frame.pack(expand=True, fill=BOTH, padx=40, pady=40)
        
        # متغيرات حقول الإدخال
        self.currency_var = StringVar()
        self.price_type_var = StringVar()
        self.currencies_map = {}
        
        # تحميل الإعدادات الموجودة
        existing_pricing_config = load_pricing_config()
        
        # جلب العملات من قاعدة البيانات
        self.load_currencies()

        # إنشاء عناصر الواجهة باستخدام Grid
        labels_font = ("Segoe UI", 14, "bold")
        dropdown_font = ("Segoe UI", 14)
        button_font = ("Segoe UI", 13, "bold")
        
        Label(main_frame, text="اختر العملة", font=labels_font, bg="#ffffff", fg="#333").grid(row=0, column=1, sticky="e", pady=15, padx=20)
        currency_options = list(self.currencies_map.keys())
        if not currency_options:
            currency_options.append("لا يوجد عملات")
        
        self.currency_dropdown = OptionMenu(main_frame, self.currency_var, *currency_options)
        self.currency_dropdown.config(width=25, font=dropdown_font, bg="#f0f0f0", activebackground="#e0e0e0", relief="groove")
        self.currency_dropdown.grid(row=0, column=0, pady=15, padx=20, sticky="w")
        if existing_pricing_config and existing_pricing_config.get('currency_guid', '') in self.currencies_map.values():
            for name, guid in self.currencies_map.items():
                if guid == existing_pricing_config['currency_guid']:
                    self.currency_var.set(name)
                    break
        else:
            self.currency_var.set(currency_options[0])

        Label(main_frame, text="اختر نوع السعر", font=labels_font, bg="#ffffff", fg="#333").grid(row=1, column=1, sticky="e", pady=15, padx=20)
        price_type_options = list(PRICE_TYPES.values())
        self.price_type_dropdown = OptionMenu(main_frame, self.price_type_var, *price_type_options)
        self.price_type_dropdown.config(width=25, font=dropdown_font, bg="#f0f0f0", activebackground="#e0e0e0", relief="groove")
        self.price_type_dropdown.grid(row=1, column=0, pady=15, padx=20, sticky="w")
        
        if existing_pricing_config and existing_pricing_config.get('price_type', '') in PRICE_TYPES:
            self.price_type_var.set(PRICE_TYPES[existing_pricing_config['price_type']])
        else:
            self.price_type_var.set(price_type_options[0])

        button_frame = Frame(main_frame, bg="#ffffff")
        button_frame.grid(row=2, column=0, columnspan=2, pady=30)
        
        Button(button_frame, text="حفظ الإعدادات", command=self.save_settings, font=button_font, bg="#28a745", fg="white", relief="flat", bd=0, padx=20, pady=8, activebackground="#1e7e34", activeforeground="white").pack(side=LEFT, padx=5)

    def load_currencies(self):
        """جلب العملات من قاعدة البيانات."""
        self.currencies_map = {}
        db_config = load_db_config()
        if not db_config:
            messagebox.showwarning("خطأ في الإعدادات", "الرجاء إعدادات الاتصال بقاعدة البيانات أولاً.")
            return

        conn = get_db_connection(db_config)
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT name, guid FROM my000")
                for row in cursor.fetchall():
                    self.currencies_map[row[0]] = str(row[1])
            except Exception as e:
                messagebox.showerror("خطأ في الاتصال", f"فشل جلب العملات: {e}")
            finally:
                conn.close()

    def save_settings(self):
        """حفظ إعدادات العملة والسعر المدخلة."""
        selected_currency_name = self.currency_var.get()
        selected_price_type_name = self.price_type_var.get()
        
        currency_guid = self.currencies_map.get(selected_currency_name)
        
        # الحصول على اسم العمود من قيمة الاختيار
        price_type = None
        for key, value in PRICE_TYPES.items():
            if value == selected_price_type_name:
                price_type = key
                break
        
        if currency_guid and price_type:
            save_pricing_config(currency_guid, price_type)
            self.master.destroy()
            if self.on_save_callback:
                self.on_save_callback()
        else:
            messagebox.showwarning("خطأ في الاختيار", "الرجاء اختيار العملة ونوع السعر.")


# --- 6. شاشة مدقق الأسعار الرئيسية ---
class PriceCheckerApp:
    def __init__(self, master):
        self.master = master
        master.title("Price Checker")
        master.geometry("1200x750")
        master.minsize(800, 600) 
        master.configure(bg="#f1f1f1")

        # متغيرات لعرض البيانات
        self.product_name_var = StringVar()
        self.product_price_var = StringVar()
        self.barcode_entry_var = StringVar()
        self.status_label_var = StringVar()
        self.currency_var = StringVar()
        # تمت إزالة self.last_sale_date_var

        self.db_config = None
        self.pricing_config = None

        # شريط القائمة
        menubar = Menu(master)
        master.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0, bg="#ffffff", fg="#333333", activebackground="#e0e0e0", activeforeground="#000000")
        menubar.add_cascade(label="ملف", menu=file_menu)
        file_menu.add_command(label="إعدادات قاعدة البيانات", command=self.open_db_settings, font=menu_font)
        file_menu.add_command(label="إعدادات العملة والأسعار", command=self.open_currency_price_settings, font=menu_font)
        file_menu.add_command(label="خروج", command=master.quit, font=menu_font)

        # إطار للباركود والإدخال (الجزء العلوي)
        barcode_frame = Frame(master, padx=20, pady=20, bg="#ffffff", relief="flat", bd=0)
        barcode_frame.pack(pady=20, fill=X, padx=20)

        Label(barcode_frame, text="ادخل الباركود أو امسح المنتج", font=("Segoe UI", 18, "bold"), bg="#ffffff", fg="#333").pack(side=RIGHT, padx=5)
        self.barcode_entry = Entry(barcode_frame, textvariable=self.barcode_entry_var, font=("Segoe UI", 24), width=30, bd=2, relief="solid", justify='right', highlightbackground="#007bff", highlightthickness=2)
        self.barcode_entry.pack(side=RIGHT, padx=15, ipady=8) 
        self.barcode_entry.bind("<Return>", self.check_price_on_enter)
        self.barcode_entry.focus_set()

        Button(barcode_frame, text="بحث", command=self.check_price, font=("Segoe UI", 16, "bold"), bg="#007bff", fg="white", relief="flat", bd=0, padx=20, pady=10, activebackground="#0056b3", activeforeground="white").pack(side=RIGHT, padx=10)
        Button(barcode_frame, text="مسح الشاشة", command=self.clear_product_info, font=("Segoe UI", 16, "bold"), bg="#dc3545", fg="white", relief="flat", bd=0, padx=20, pady=10, activebackground="#c82333", activeforeground="white").pack(side=RIGHT, padx=10)

        info_frame = Frame(master, padx=10, pady=10, bd=0, relief="flat", bg="#ffffff")
        info_frame.pack(pady=20, fill=BOTH, expand=True, padx=20)

        Label(info_frame, text=":اسم المنتج", font=("Segoe UI", 30, "bold"), fg="#000000", bg="#ffffff").pack(anchor='e', pady=(15, 0), padx=20)
        Label(info_frame, textvariable=self.product_name_var, font=("Segoe UI", 48, "bold"), fg="#0056b3", bg="#ffffff", wraplength=900, justify='right').pack(anchor='e', pady=(0, 15), padx=20)

        Label(info_frame, text=":سعر المنتج", font=("Segoe UI", 30, "bold"), fg="#000000", bg="#ffffff").pack(anchor='e', pady=(15, 0), padx=20)
        
        # إطار جديد لتجميع السعر والعملة
        price_currency_frame = Frame(info_frame, bg="#ffffff")
        price_currency_frame.pack(anchor='e', pady=(0, 15), padx=20)
        
        Label(price_currency_frame, textvariable=self.product_price_var, font=("Segoe UI", 72, "bold"), fg="#28a745", bg="#ffffff").pack(side=RIGHT, padx=(0, 10))
        Label(price_currency_frame, textvariable=self.currency_var, font=("Segoe UI", 28), fg="#333", bg="#ffffff").pack(side=RIGHT, pady=(0, 15))
        # تم حذف عرض تاريخ آخر بيع

        self.status_display_label = Label(master, textvariable=self.status_label_var, font=("Segoe UI", 18, "bold"), fg="red", bg="#f0f2f5")
        self.status_display_label.pack(pady=15)

        self.load_settings_and_check_connection()

    def load_settings_and_check_connection(self):
        """تحميل إعدادات قاعدة البيانات والتحقق من وجودها."""
        self.db_config = load_db_config()
        self.pricing_config = load_pricing_config()
        
        if not self.db_config:
            self.status_label_var.set("الرجاء إدخال إعدادات قاعدة البيانات من قائمة 'ملف'.")
            self.status_display_label.config(fg="red")
        else:
            conn = get_db_connection(self.db_config)
            if conn:
                self.status_label_var.set("✅ تم الاتصال بقاعدة البيانات بنجاح.")
                self.status_display_label.config(fg="green")
                conn.close()
                if not self.pricing_config:
                     self.status_label_var.set("⚠️ إعدادات العملة والأسعار مفقودة. يرجى إعدادها من قائمة 'ملف'.")
                     self.status_display_label.config(fg="orange")
            else:
                self.status_label_var.set("❌ فشل الاتصال بقاعدة البيانات. تحقق من الإعدادات.")
                self.status_display_label.config(fg="red")

    def open_db_settings(self):
        """فتح نافذة إعدادات قاعدة البيانات."""
        settings_root = Toplevel(self.master)
        SettingsWindow(settings_root, self.load_settings_and_check_connection)
        settings_root.transient(self.master)
        settings_root.grab_set()
        self.master.wait_window(settings_root)
        
    def open_currency_price_settings(self):
        """فتح نافذة إعدادات العملة والسعر."""
        settings_root = Toplevel(self.master)
        CurrencyPriceSettingsWindow(settings_root, self.load_settings_and_check_connection)
        settings_root.transient(self.master)
        settings_root.grab_set()
        self.master.wait_window(settings_root)


    def check_price_on_enter(self, event=None):
        """تُستدعى عند الضغط على مفتاح Enter في حقل الباركود."""
        self.check_price()

    def check_price(self, event=None):
        """جلب معلومات المنتج من قاعدة البيانات وعرضها."""
        barcode = self.barcode_entry_var.get().strip()
        self.barcode_entry_var.set("")
        self.barcode_entry.focus_set()

        self.clear_product_info_display_only()

        if not barcode:
            self.status_label_var.set("⚠️ الرجاء إدخال باركود للمسح.")
            self.status_display_label.config(fg="orange")
            return

        if not self.db_config or not self.pricing_config:
            self.status_label_var.set("❌ إعدادات التطبيق مفقودة. الرجاء إعدادها أولاً.")
            self.status_display_label.config(fg="red")
            return

        conn = get_db_connection(self.db_config)
        if conn is None:
            self.status_label_var.set("❌ فشل الاتصال بقاعدة البيانات. تحقق من الإعدادات.")
            self.status_display_label.config(fg="red")
            return

        try:
            cursor = conn.cursor()
            
            # جلب إعدادات السعر والعملة
            selected_price_type = self.pricing_config.get('price_type')
            selected_currency_guid = self.pricing_config.get('currency_guid')

            if not selected_price_type or not selected_currency_guid:
                self.status_label_var.set("⚠️ إعدادات العملة والأسعار غير مكتملة.")
                self.status_display_label.config(fg="orange")
                return

            # جلب سعر الصرف
            exchange_rate = get_latest_exchange_rate(conn, selected_currency_guid)
            
            # جلب اسم المنتج
            product_query = "SELECT Name FROM mt000 WHERE code = ?"
            cursor.execute(product_query, barcode)
            product_name_result = cursor.fetchone()

            if product_name_result:
                self.product_name_var.set(product_name_result[0])
            else:
                self.product_name_var.set("الاسم غير متوفر")

            # جلب السعر بناءً على النوع المختار
            price_query = f"SELECT {selected_price_type} FROM mt000 WHERE code = ?"
            cursor.execute(price_query, barcode)
            product_price_result = cursor.fetchone()

            if product_price_result:
                product_price = product_price_result[0]
                
                # حساب السعر النهائي بعد تطبيق سعر الصرف
                final_price = product_price / exchange_rate
                
                if final_price is not None:
                    formatted_price = f"{final_price:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
                    self.product_price_var.set(f"{formatted_price}")
                else:
                    self.product_price_var.set("---")
                
                # جلب معلومات العملة من الجدول my000
                currency_info_query = "SELECT Name FROM my000 WHERE guid = ?"
                cursor.execute(currency_info_query, selected_currency_guid)
                currency_name_result = cursor.fetchone()
                
                if currency_name_result:
                    self.currency_var.set(currency_name_result[0])
                else:
                    self.currency_var.set("---")

                # تم حذف self.last_sale_date_var.set()

                self.status_label_var.set(f"✅ تم العثور على المنتج وحساب السعر بناءً على '{PRICE_TYPES.get(selected_price_type)}'.")
                self.status_display_label.config(fg="green")
            else:
                self.product_price_var.set("---")
                self.currency_var.set("---")
                self.status_label_var.set(f"❌ لم يتم العثور على سعر من نوع '{PRICE_TYPES.get(selected_price_type)}' لهذا المنتج.")
                self.status_display_label.config(fg="red")
            
        except pyodbc.Error as ex:
            sqlstate = ex.args[0]
            self.status_label_var.set(f"❌ خطأ في الاستعلام: {sqlstate}")
            self.status_display_label.config(fg="red")
            self.clear_product_info_display_only()
        finally:
            if conn:
                conn.close()

    def clear_product_info_display_only(self):
        """مسح معلومات المنتج المعروضة فقط."""
        self.product_name_var.set("---")
        self.product_price_var.set("---")
        self.currency_var.set("---")
        # تم حذف self.last_sale_date_var.set()
        self.status_label_var.set("") 

    def clear_product_info(self):
        """مسح معلومات المنتج المعروضة وحقل الباركود والعودة للحالة الافتراضية."""
        self.product_name_var.set("---")
        self.product_price_var.set("---")
        self.barcode_entry_var.set("")
        self.currency_var.set("---")
        # تم حذف self.last_sale_date_var.set()
        self.status_label_var.set("")
        self.barcode_entry.focus_set()


if __name__ == '__main__':
    root = Tk()
    app = PriceCheckerApp(root)
    root.mainloop()
