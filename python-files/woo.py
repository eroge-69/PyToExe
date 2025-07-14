import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import sqlite3
import os
from datetime import datetime
import jdatetime
import threading
import time
import html
import sys
import platform
import subprocess
import tempfile
import shutil
import webbrowser
import winsound

# تنظیمات پایگاه داده
DB_NAME = "woocommerce_orders.db"
CURRENT_VERSION = "0.7"  # نسخه جدید برنامه
GITHUB_REPO = "https://github.com/intellsoft/woocoomerce-easy-orders-manage"
VERSION_FILE_URL = f"{GITHUB_REPO}/raw/main/VERSION.TXT"
LAST_CHECK_FILE = "last_update_check.txt"

# مسیر فایل صدا
AUDIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "audio")
NEW_ORDER_SOUND = os.path.join(AUDIO_DIR, "neworder.wav")

def init_db(conn=None):
    """ایجاد جداول پایگاه داده با ساختار صحیح در صورت عدم وجود"""
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_NAME)
        close_conn = True
    
    c = conn.cursor()
    
    # جدول سفارشات با ستون‌های مرتب
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY,
        site_id INTEGER,
        date_created TEXT,
        status TEXT,
        total REAL,
        currency TEXT,
        payment_method TEXT,
        customer_name TEXT,
        customer_email TEXT,
        customer_phone TEXT,
        shipping_address TEXT,
        shipping_postcode TEXT,
        shipping_method TEXT,
        shipping_total REAL,
        seen INTEGER DEFAULT 0,
        FOREIGN KEY (site_id) REFERENCES sites(id)
    )''')
    
    # جدول اقلام سفارش
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_name TEXT,
        quantity INTEGER,
        price REAL,
        total REAL,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )''')
    
    # جدول توضیحات سفارش (اصلاح شده)
    c.execute('''CREATE TABLE IF NOT EXISTS order_notes (
        id INTEGER PRIMARY KEY,
        order_id INTEGER,
        author TEXT,
        date_created TEXT,
        note TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (id)
    )''')
    
    # جدول برای ذخیره زمان آخرین بررسی آپدیت
    c.execute('''CREATE TABLE IF NOT EXISTS app_settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    # جدول سایت‌ها
    c.execute('''CREATE TABLE IF NOT EXISTS sites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL UNIQUE,
        consumer_key TEXT NOT NULL,
        consumer_secret TEXT NOT NULL,
        enabled INTEGER DEFAULT 1,
        refresh_interval INTEGER DEFAULT 10,
        shop_address TEXT DEFAULT '',
        shop_postcode TEXT DEFAULT '',
        shop_phone TEXT DEFAULT ''
    )''')
    
    if close_conn:
        conn.commit()
        conn.close()

def migrate_db():
    """
    در صورت قدیمی بودن شمای پایگاه داده، جدول را بازسازی می‌کند
    """
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        # بررسی وجود ستون site_id در جدول سفارشات
        c.execute("PRAGMA table_info(orders)")
        columns = [info[1] for info in c.fetchall()]
        
        if 'site_id' not in columns:
            print("Adding site_id column to orders table...")
            c.execute("ALTER TABLE orders ADD COLUMN site_id INTEGER")
        
        # بررسی وجود جدول سایت‌ها
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='sites'")
        if not c.fetchone():
            print("Creating sites table...")
            c.execute('''CREATE TABLE sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                domain TEXT NOT NULL UNIQUE,
                consumer_key TEXT NOT NULL,
                consumer_secret TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                refresh_interval INTEGER DEFAULT 10,
                shop_address TEXT DEFAULT '',
                shop_postcode TEXT DEFAULT '',
                shop_phone TEXT DEFAULT ''
            )''')
        
        # بررسی وجود ستون‌های جدید فروشگاه
        c.execute("PRAGMA table_info(sites)")
        columns = [info[1] for info in c.fetchall()]
        new_columns = [
            ('shop_address', 'TEXT DEFAULT ""'),
            ('shop_postcode', 'TEXT DEFAULT ""'),
            ('shop_phone', 'TEXT DEFAULT ""')
        ]
        
        for col_name, col_type in new_columns:
            if col_name not in columns:
                print(f"Adding {col_name} column to sites table...")
                c.execute(f"ALTER TABLE sites ADD COLUMN {col_name} {col_type}")
        
        # بررسی وجود جدول توضیحات سفارش (اصلاح شده)
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='order_notes'")
        if not c.fetchone():
            print("Creating order_notes table...")
            c.execute('''CREATE TABLE order_notes (
                id INTEGER PRIMARY KEY,
                order_id INTEGER,
                author TEXT,
                date_created TEXT,
                note TEXT,
                FOREIGN KEY (order_id) REFERENCES orders (id)
            )''')
        
        conn.commit()
        print("Database migration complete.")
    except sqlite3.OperationalError as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

# اجرای به‌روزرسانی و مقداردهی اولیه دیتابیس
migrate_db()
init_db()

class WooCommerceOrdersApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدیریت سفارشات ووکامرس")
        self.root.geometry("1200x800")
        self.root.state('zoomed')
        
        # تنظیم فونت بزرگتر برای همه ویجت‌ها
        self.set_larger_fonts()
        
        # ذخیره سایت‌ها
        self.sites = []  # لیستی از دیکشنری‌های تنظیمات سایت
        self.load_sites()  # بارگیری سایت‌ها از دیتابیس
        
        # ذخیره سفارش‌ها
        self.orders = []
        self.new_order_ids = set()
        self.first_run = True
        self.refresh_in_progress = False
        self.current_order_id = None  # ذخیره شماره سفارش فعلی
        
        # نگاشت وضعیت‌های سفارش به فارسی
        self.status_translation = {
            "pending": "در انتظار پرداخت",
            "pending payment": "منتظر پرداخت مشتری",
            "on-hold": "در انتظار بررسی",
            "processing": "در حال انجام",
            "completed": "تکمیل شده",
            "failed": "ناموفق",
            "draft": "پیش‌نویس",
            "cancelled": "لغو شده",
            "refunded": "مسترد شده",
            "trash": "حذف شده", # WooCommerce might return 'trash' for deleted orders
        }
        
        # ایجاد منوها
        self.create_menus()
        
        # ایجاد رابط کاربری
        self.create_widgets()
        
        # بارگیری اولیه سفارش‌ها از دیتابیس
        self.load_orders_from_db()
        
        if self.first_run:
            self.check_new_orders(initial_load=True)
        else:
            self.show_floating_message(f"{len(self.orders)} سفارش از دیتابیس بارگیری شد")
            self.status_var.set("آماده")

        # شروع تایمر برای به‌روزرسانی خودکار
        self.setup_auto_refresh()
        
        # بررسی آپدیت بعد از 5 ثانیه (اجرا در پس‌زمینه)
        self.root.after(5000, self.check_for_updates_in_thread)
    
    def set_larger_fonts(self):
        """تنظیم فونت‌های بزرگتر برای همه عناصر رابط کاربری"""
        default_font = ("Tahoma", 12)
        self.root.option_add("*Font", default_font)
        
        # تنظیم فونت مخصوص Treeview
        style = ttk.Style()
        style.configure("Treeview", font=("Tahoma", 11))
        style.configure("Treeview.Heading", font=("Tahoma", 11, "bold"))
        
        # تنظیم فونت برای دکمه‌ها و سایر ویجت‌ها
        style.configure("TButton", font=default_font)
        style.configure("TLabel", font=default_font)
        style.configure("TLabelframe.Label", font=("Tahoma", 11, "bold"))
        
        # تعریف رنگ‌های متناوب برای ردیف‌ها
        style.configure("Treeview", background="#ffffff")
        style.map("Treeview", background=[("selected", "#4a6984")])
    
    def create_menus(self):
        """ایجاد منوهای برنامه"""
        menubar = tk.Menu(self.root)
        
        # منوی فایل
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="خروج", command=self.root.quit)
        menubar.add_cascade(label="فایل", menu=file_menu)
        
        # منوی تنظیمات جدید
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="مدیریت سایت‌ها", command=self.open_settings)
        menubar.add_cascade(label="تنظیمات", menu=settings_menu)
        
        # منوی راهنما
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="درباره برنامه", command=self.show_about)
        menubar.add_cascade(label="راهنما", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def load_sites(self):
        """بارگیری سایت‌ها از دیتابیس"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM sites")
        self.sites = []
        for row in c.fetchall():
            site = {
                'id': row[0],
                'domain': row[1],
                'consumer_key': row[2],
                'consumer_secret': row[3],
                'enabled': bool(row[4]),
                'refresh_interval': row[5],
                'shop_address': row[6] if len(row) > 6 else '',
                'shop_postcode': row[7] if len(row) > 7 else '',
                'shop_phone': row[8] if len(row) > 8 else ''
            }
            self.sites.append(site)
        conn.close()
    
    def open_settings(self):
        """باز کردن پنجره تنظیمات سایت‌ها"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("تنظیمات سایت‌ها")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # تنظیم اندازه پنجره
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        settings_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # فریم اصلی
        main_frame = ttk.Frame(settings_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # عنوان
        ttk.Label(main_frame, text="مدیریت سایت‌های ووکامرس", font=("Tahoma", 14, "bold")).pack(pady=10)
        
        # لیست سایت‌ها
        list_frame = ttk.LabelFrame(main_frame, text="سایت‌های ثبت شده", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("domain", "enabled", "interval")
        self.sites_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        # تنظیمات ستون‌ها
        self.sites_tree.heading("domain", text="دامنه سایت", anchor=tk.CENTER)
        self.sites_tree.heading("enabled", text="وضعیت", anchor=tk.CENTER)
        self.sites_tree.heading("interval", text="فاصله بررسی (دقیقه)", anchor=tk.CENTER)
        
        self.sites_tree.column("domain", width=250, anchor=tk.CENTER)
        self.sites_tree.column("enabled", width=100, anchor=tk.CENTER)
        self.sites_tree.column("interval", width=150, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.sites_tree.yview)
        self.sites_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.sites_tree.pack(fill=tk.BOTH, expand=True)
        
        # دکمه‌های مدیریت
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="افزودن سایت جدید", 
                  command=lambda: self.open_site_dialog(settings_window)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="ویرایش", 
                  command=lambda: self.edit_site(settings_window)).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="حذف", 
                  command=self.delete_site).pack(side=tk.RIGHT, padx=5)
        
        # بارگیری سایت‌ها در Treeview
        self.load_sites_to_treeview()
        
        # دکمه بستن
        ttk.Button(main_frame, text="ذخیره و بستن", command=settings_window.destroy).pack(pady=20)
    
    def load_sites_to_treeview(self):
        """بارگیری سایت‌ها در Treeview تنظیمات"""
        for item in self.sites_tree.get_children():
            self.sites_tree.delete(item)
        
        for site in self.sites:
            self.sites_tree.insert("", "end", values=(
                site['domain'],
                "فعال" if site['enabled'] else "غیرفعال",
                site['refresh_interval']
            ), tags=(site['id'],))
    
    def open_site_dialog(self, parent, site=None):
        """باز کردن دیالوگ افزودن/ویرایش سایت"""
        dialog = tk.Toplevel(parent)
        dialog.title("افزودن سایت جدید" if not site else "ویرایش سایت")
        dialog.transient(parent)
        dialog.grab_set()
        
        # تنظیم اندازه پنجره
        dialog.geometry("600x550")
        
        # فریم اصلی
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # متغیرهای فرم
        domain_var = tk.StringVar(value=site['domain'] if site else "")
        key_var = tk.StringVar(value=site['consumer_key'] if site else "")
        secret_var = tk.StringVar(value=site['consumer_secret'] if site else "")
        enabled_var = tk.BooleanVar(value=site['enabled'] if site else True)
        interval_var = tk.IntVar(value=site['refresh_interval'] if site else 10)
        shop_address_var = tk.StringVar(value=site['shop_address'] if site else "")
        shop_postcode_var = tk.StringVar(value=site['shop_postcode'] if site else "")
        shop_phone_var = tk.StringVar(value=site['shop_phone'] if site else "")
        
        # اعتبارسنجی ورودی‌ها
        def validate_domain(P):
            return all(c.isalnum() or c in ['.', '-'] for c in P) and len(P) <= 100
        
        def validate_key(P):
            return len(P) <= 100
        
        def validate_secret(P):
            return len(P) <= 100
        
        def validate_interval(P):
            if P == "": return True
            if P.isdigit():
                num = int(P)
                return 1 <= num <= 1440  # بین 1 دقیقه تا 24 ساعت
            return False
        
        vcmd_domain = (dialog.register(validate_domain), '%P')
        vcmd_key = (dialog.register(validate_key), '%P')
        vcmd_secret = (dialog.register(validate_secret), '%P')
        vcmd_interval = (dialog.register(validate_interval), '%P')
        
        # فرم
        ttk.Label(main_frame, text="دامنه سایت (بدون http:// و www):").grid(row=0, column=0, sticky=tk.W, pady=5)
        domain_entry = ttk.Entry(main_frame, textvariable=domain_var, validate="key", validatecommand=vcmd_domain)
        domain_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(main_frame, text="کلید مصرف‌کننده (Consumer Key):").grid(row=1, column=0, sticky=tk.W, pady=5)
        key_entry = ttk.Entry(main_frame, textvariable=key_var, validate="key", validatecommand=vcmd_key)
        key_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(main_frame, text="رمز مصرف‌کننده (Consumer Secret):").grid(row=2, column=0, sticky=tk.W, pady=5)
        secret_entry = ttk.Entry(main_frame, textvariable=secret_var, validate="key", validatecommand=vcmd_secret)
        secret_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(main_frame, text="فاصله بررسی خودکار (دقیقه):").grid(row=3, column=0, sticky=tk.W, pady=5)
        interval_entry = ttk.Entry(main_frame, textvariable=interval_var, validate="key", validatecommand=vcmd_interval)
        interval_entry.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Checkbutton(main_frame, text="فعال", variable=enabled_var).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # جداکننده
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).grid(row=5, column=0, columnspan=2, pady=15, sticky=tk.EW)
        
        # اطلاعات فروشگاه
        ttk.Label(main_frame, text="اطلاعات فروشگاه", font=("Tahoma", 11, "bold")).grid(row=6, column=0, columnspan=2, pady=5)
        
        ttk.Label(main_frame, text="آدرس فروشگاه:").grid(row=7, column=0, sticky=tk.W, pady=5)
        shop_address_entry = ttk.Entry(main_frame, textvariable=shop_address_var)
        shop_address_entry.grid(row=7, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(main_frame, text="کد پستی فروشگاه:").grid(row=8, column=0, sticky=tk.W, pady=5)
        shop_postcode_entry = ttk.Entry(main_frame, textvariable=shop_postcode_var)
        shop_postcode_entry.grid(row=8, column=1, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(main_frame, text="شماره تماس فروشگاه:").grid(row=9, column=0, sticky=tk.W, pady=5)
        shop_phone_entry = ttk.Entry(main_frame, textvariable=shop_phone_var)
        shop_phone_entry.grid(row=9, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # دکمه دریافت اطلاعات از ووکامرس (تعریف قبل از تابع)
        fetch_btn = ttk.Button(main_frame, text="دریافت اطلاعات فروشگاه از ووکامرس")
        fetch_btn.grid(row=10, column=0, columnspan=2, pady=10)

        def fetch_shop_info():
            domain = domain_var.get().strip().lower()
            consumer_key = key_var.get().strip()
            consumer_secret = secret_var.get().strip()

            if not domain or not consumer_key or not consumer_secret:
                messagebox.showerror("خطا", "لطفاً دامنه، کلید و رمز مصرف‌کننده را وارد کنید.")
                return

            # غیرفعال کردن دکمه و نمایش پیام "در حال دریافت"
            fetch_btn.config(state=tk.DISABLED)
            original_text = fetch_btn.cget("text")
            fetch_btn.config(text="در حال دریافت...")

            def do_fetch():
                try:
                    auth = (consumer_key, consumer_secret)
                    headers = {"User-Agent": "WooCommerce-Python-App/1.0"}

                    # 1. دریافت تنظیمات عمومی
                    settings_api_url = f"https://{domain}/wp-json/wc/v3/settings/general"
                    response = requests.get(settings_api_url, auth=auth, headers=headers, timeout=20, verify=False)
                    response.raise_for_status()
                    
                    settings_list = response.json()
                    settings = {setting['id']: setting['value'] for setting in settings_list}
                    
                    country_state_code = settings.get('woocommerce_default_country', '') # e.g., 'IR:TE'
                    city = settings.get('woocommerce_store_city', '')
                    address1 = settings.get('woocommerce_store_address', '')
                    address2 = settings.get('woocommerce_store_address_2', '')
                    postcode = settings.get('woocommerce_store_postcode', '')
                    phone = settings.get('woocommerce_store_phone', '')

                    country_name = ""
                    state_name = ""

                    # 2. دریافت نام کامل کشور و استان
                    if country_state_code and ':' in country_state_code:
                        country_code, state_code = country_state_code.split(':', 1)
                        
                        # 2a. فراخوانی API برای دریافت اطلاعات کشور
                        country_api_url = f"https://{domain}/wp-json/wc/v3/data/countries/{country_code}"
                        country_response = requests.get(country_api_url, auth=auth, headers=headers, timeout=10, verify=False)
                        
                        if country_response.status_code == 200:
                            country_data = country_response.json()
                            country_name = country_data.get('name', country_code)  # استفاده از کد در صورت نبود نام
                            
                            # 2b. جستجو برای نام استان در لیست استان‌های کشور
                            states = country_data.get('states', [])
                            state_found = next((s for s in states if s['code'] == state_code), None)
                            if state_found:
                                state_name = state_found.get('name', state_code) # استفاده از کد در صورت نبود نام
                            else:
                                state_name = state_code # اگر استان پیدا نشد
                        else:
                            # اگر دریافت اطلاعات کشور ناموفق بود، از کدها استفاده کن
                            country_name = country_code
                            state_name = state_code
                    
                    # 3. ترکیب آدرس نهایی
                    address_parts = []
                    if country_name: address_parts.append(country_name)
                    if state_name: address_parts.append(state_name)
                    if city: address_parts.append(city)
                    
                    main_address = ' '.join(filter(None, [address1, address2])).strip()
                    if main_address:
                        address_parts.append(main_address)

                    full_address = " - ".join(address_parts)

                    # 4. به‌روزرسانی رابط کاربری در نخ اصلی
                    dialog.after(0, lambda: shop_address_var.set(full_address))
                    dialog.after(0, lambda: shop_postcode_var.set(postcode))
                    dialog.after(0, lambda: shop_phone_var.set(phone))

                    if not full_address and not postcode and not phone:
                         dialog.after(0, lambda: messagebox.showwarning("توجه", "ارتباط موفق بود، اما فیلدهای اطلاعات فروشگاه در ووکامرس شما خالی است."))
                    else:
                         dialog.after(0, lambda: messagebox.showinfo("موفقیت", "اطلاعات فروشگاه با موفقیت دریافت شد."))

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 403:
                        error_message = (
                            "خطای 403: دسترسی ممنوع.\n\n"
                            "دلایل احتمالی:\n"
                            "1. کلید/رمز مصرف‌کننده (Consumer Key/Secret) اشتباه است.\n"
                            "2. کلید API دسترسی لازم (Read/Write) را ندارد.\n"
                            "3. فایروال یا افزونه امنیتی روی سرور، دسترسی را مسدود کرده است."
                        )
                        dialog.after(0, lambda: messagebox.showerror("خطا در دسترسی", error_message))
                    else:
                        error_message = f"خطا در دریافت اطلاعات: {e.response.status_code}\n\n{e.response.text}"
                        dialog.after(0, lambda: messagebox.showerror("خطا", error_message))
                except requests.exceptions.RequestException as e:
                    error_message = f"خطای شبکه یا اتصال:\n\n{str(e)}\n\n"
                    error_message += "لطفاً اتصال اینترنت و درستی دامنه سایت را بررسی کنید."
                    dialog.after(0, lambda: messagebox.showerror("خطای اتصال", error_message))
                except Exception as e:
                    error_message = f"یک خطای پیش‌بینی نشده رخ داد:\n{str(e)}"
                    dialog.after(0, lambda: messagebox.showerror("خطای ناشناخته", error_message))
                finally:
                    # فعال کردن مجدد دکمه در نخ اصلی
                    dialog.after(0, lambda: fetch_btn.config(state=tk.NORMAL, text=original_text))

            # اجرای درخواست شبکه در یک نخ جداگانه
            threading.Thread(target=do_fetch, daemon=True).start()
        
        # اختصاص دستور به دکمه
        fetch_btn.config(command=fetch_shop_info)
        
        # دکمه‌ها
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=11, column=0, columnspan=2, pady=20)
        
        def save_site():
            if not domain_var.get().strip():
                messagebox.showerror("خطا", "لطفاً دامنه سایت را وارد کنید")
                return
            
            if not key_var.get().strip() or not secret_var.get().strip():
                messagebox.showerror("خطا", "لطفاً کلید و رمز مصرف‌کننده را وارد کنید")
                return
            
            if not interval_var.get() or interval_var.get() < 1:
                messagebox.showerror("خطا", "فاصله بررسی باید حداقل 1 دقیقه باشد")
                return
            
            site_data = {
                'domain': domain_var.get().strip().lower(),
                'consumer_key': key_var.get().strip(),
                'consumer_secret': secret_var.get().strip(),
                'enabled': enabled_var.get(),
                'refresh_interval': interval_var.get(),
                'shop_address': shop_address_var.get().strip(),
                'shop_postcode': shop_postcode_var.get().strip(),
                'shop_phone': shop_phone_var.get().strip()
            }
            
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            
            if site:
                # ویرایش سایت موجود
                c.execute('''UPDATE sites SET 
                            domain=?, consumer_key=?, consumer_secret=?, 
                            enabled=?, refresh_interval=?,
                            shop_address=?, shop_postcode=?, shop_phone=?
                            WHERE id=?''',
                         (site_data['domain'], site_data['consumer_key'], 
                          site_data['consumer_secret'], int(site_data['enabled']),
                          site_data['refresh_interval'],
                          site_data['shop_address'], site_data['shop_postcode'], site_data['shop_phone'],
                          site['id']))
            else:
                # افزودن سایت جدید
                c.execute('''INSERT INTO sites 
                            (domain, consumer_key, consumer_secret, enabled, refresh_interval,
                            shop_address, shop_postcode, shop_phone)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                         (site_data['domain'], site_data['consumer_key'], 
                          site_data['consumer_secret'], int(site_data['enabled']),
                          site_data['refresh_interval'],
                          site_data['shop_address'], site_data['shop_postcode'], site_data['shop_phone']))
            
            conn.commit()
            conn.close()
            
            # بارگیری مجدد سایت‌ها و به‌روزرسانی رابط کاربری
            self.load_sites()
            self.load_sites_to_treeview()
            self.setup_auto_refresh()  # تنظیم مجدد تایمرها
            
            dialog.destroy()
        
        ttk.Button(btn_frame, text="ذخیره", command=save_site).pack(side=tk.RIGHT, padx=10)
        ttk.Button(btn_frame, text="لغو", command=dialog.destroy).pack(side=tk.RIGHT)
        
        # تنظیم وزن ستون‌ها برای گسترش
        main_frame.columnconfigure(1, weight=1)
    
    def edit_site(self, parent):
        """ویرایش سایت انتخاب شده"""
        selected = self.sites_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک سایت را انتخاب کنید")
            return
        
        site_id = self.sites_tree.item(selected[0], "tags")[0]
        site = next((s for s in self.sites if s['id'] == int(site_id)), None)
        
        if site:
            self.open_site_dialog(parent, site)
    
    def delete_site(self):
        """حذف سایت انتخاب شده"""
        selected = self.sites_tree.selection()
        if not selected:
            messagebox.showwarning("هشدار", "لطفاً یک سایت را انتخاب کنید")
            return
        
        site_id = self.sites_tree.item(selected[0], "tags")[0]
        site = next((s for s in self.sites if s['id'] == int(site_id)), None)
        
        if site and messagebox.askyesno("تأیید حذف", f"آیا از حذف سایت {site['domain']} مطمئن هستید؟"):
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("DELETE FROM sites WHERE id=?", (site['id'],))
            conn.commit()
            conn.close()
            
            # بارگیری مجدد سایت‌ها و به‌روزرسانی رابط کاربری
            self.load_sites()
            self.load_sites_to_treeview()
            self.setup_auto_refresh()  # تنظیم مجدد تایمرها
    
    def show_about(self):
        """نمایش پنجره درباره برنامه"""
        about_text = "برنامه مدیریت سفارشات ووکامرس\n\nبرنامه نویس: محمدعلی عباسپور\n\nنسخه: " + CURRENT_VERSION
        messagebox.showinfo("درباره برنامه", about_text)
    
    def create_widgets(self):
        # فریم اصلی
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # فریم بالایی
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # دکمه‌ها
        button_frame = ttk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT)
        
        self.refresh_btn = ttk.Button(button_frame, text="بروزرسانی سفارش‌ها", command=self.manual_refresh)
        self.refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        # نوار وضعیت
        self.status_var = tk.StringVar(value="در حال بارگیری...")
        status_bar = ttk.Label(top_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # لیست سفارش‌ها
        orders_frame = ttk.LabelFrame(main_frame, text="سفارش‌ها", padding=10)
        orders_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # اضافه کردن ستون جدید برای سایت
        columns = ("site", "id", "date", "customer", "status", "total")
        self.orders_tree = ttk.Treeview(orders_frame, columns=columns, show="headings", selectmode="browse", height=15)
        
        # تنظیمات ستون‌ها با وسط چین و تغییر نام‌ها
        self.orders_tree.heading("site", text="سایت", anchor=tk.CENTER)
        self.orders_tree.heading("id", text="شماره فاکتور", anchor=tk.CENTER)
        self.orders_tree.heading("date", text="تاریخ ثبت سفارش", anchor=tk.CENTER)
        self.orders_tree.heading("customer", text="نام مشتری", anchor=tk.CENTER)
        self.orders_tree.heading("status", text="وضعیت سفارش", anchor=tk.CENTER)
        self.orders_tree.heading("total", text="مبلغ کل (تومان)", anchor=tk.CENTER)
        
        # تنظیم عرض ستون‌ها با توجه به نام‌های جدید
        self.orders_tree.column("site", width=150, anchor=tk.CENTER)
        self.orders_tree.column("id", width=100, anchor=tk.CENTER)
        self.orders_tree.column("date", width=150, anchor=tk.CENTER)
        self.orders_tree.column("customer", width=200, anchor=tk.CENTER)
        self.orders_tree.column("status", width=120, anchor=tk.CENTER)
        self.orders_tree.column("total", width=150, anchor=tk.CENTER)
        
        self.orders_tree.tag_configure('new_order', background='#ffcccc')
        
        scrollbar = ttk.Scrollbar(orders_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.orders_tree.pack(fill=tk.BOTH, expand=True)
        
        # فریم جزئیات سفارش
        self.details_frame = ttk.LabelFrame(main_frame, text="جزئیات سفارش", padding=10)
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notebook = ttk.Notebook(self.details_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # تب‌های اطلاعات
        self.create_customer_tab(self.notebook)
        self.create_shipping_tab(self.notebook)
        self.create_items_tab(self.notebook)
        self.create_label_print_tab(self.notebook)  # تب جدید برای پرینت برچسب پستی
        
        # تب توضیحات سفارش (به صورت پویا اضافه می‌شود)
        self.notes_tab_frame = None
        self.notes_text = None
        
        self.orders_tree.bind("<<TreeviewSelect>>", self.on_order_select)
        
        # پیام شناور
        self.floating_message_var = tk.StringVar()
        self.floating_message = ttk.Label(self.root, textvariable=self.floating_message_var, 
                                         background="#d4edda", foreground="#155724", 
                                         padding=(15, 5), borderwidth=1, relief="solid",
                                         font=("Tahoma", 11))
        self.floating_message.place_forget()

    def create_customer_tab(self, notebook):
        customer_frame = ttk.Frame(notebook, padding=10)
        notebook.add(customer_frame, text="اطلاعات مشتری")
        columns = ("title", "value")
        self.customer_tree = ttk.Treeview(customer_frame, columns=columns, show="headings", height=6)
        
        # تنظیمات ستون‌ها با وسط چین
        self.customer_tree.heading("title", text="عنوان", anchor=tk.CENTER)
        self.customer_tree.heading("value", text="مقدار", anchor=tk.CENTER)
        
        self.customer_tree.column("title", width=150, anchor=tk.CENTER)
        self.customer_tree.column("value", width=300, anchor=tk.CENTER)
        
        # تعریف تگ‌ها برای رنگ‌آمیزی متناوب
        self.customer_tree.tag_configure('even_row', background='#ffffff')
        self.customer_tree.tag_configure('odd_row', background='#f0f0f0')
        
        self.customer_tree.bind("<Button-1>", lambda event: "break")
        self.customer_tree.pack(fill=tk.BOTH, expand=True)

    def create_shipping_tab(self, notebook):
        shipping_frame = ttk.Frame(notebook, padding=10)
        notebook.add(shipping_frame, text="اطلاعات حمل و نقل")
        columns = ("title", "value")
        self.shipping_tree = ttk.Treeview(shipping_frame, columns=columns, show="headings", height=6)
        
        # تنظیمات ستون‌ها با وسط چین
        self.shipping_tree.heading("title", text="عنوان", anchor=tk.CENTER)
        self.shipping_tree.heading("value", text="مقدار", anchor=tk.CENTER)
        
        self.shipping_tree.column("title", width=150, anchor=tk.CENTER)
        self.shipping_tree.column("value", width=300, anchor=tk.CENTER)
        
        # تعریف تگ‌ها برای رنگ‌آمیزی متناوب
        self.shipping_tree.tag_configure('even_row', background='#ffffff')
        self.shipping_tree.tag_configure('odd_row', background='#f0f0f0')
        
        self.shipping_tree.bind("<Button-1>", lambda event: "break")
        self.shipping_tree.pack(fill=tk.BOTH, expand=True)

    def create_items_tab(self, notebook):
        items_frame = ttk.Frame(notebook, padding=10)
        notebook.add(items_frame, text="فاکتور سفارش")
        columns = ("product", "quantity", "price", "total")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings", height=8)
        
        # تنظیمات ستون‌ها با وسط چین
        self.items_tree.heading("product", text="محصول", anchor=tk.CENTER)
        self.items_tree.heading("quantity", text="تعداد", anchor=tk.CENTER)
        self.items_tree.heading("price", text="قیمت واحد (تومان)", anchor=tk.CENTER)
        self.items_tree.heading("total", text="مجموع (تومان)", anchor=tk.CENTER)
        
        self.items_tree.column("product", width=300, anchor=tk.CENTER)
        self.items_tree.column("quantity", width=80, anchor=tk.CENTER)
        self.items_tree.column("price", width=120, anchor=tk.CENTER)
        self.items_tree.column("total", width=150, anchor=tk.CENTER)
        
        # تعریف تگ‌ها برای رنگ‌آمیزی متناوب
        self.items_tree.tag_configure('even_row', background='#ffffff')
        self.items_tree.tag_configure('odd_row', background='#f0f0f0')
        
        self.items_tree.bind("<Button-1>", lambda event: "break")
        self.items_tree.pack(fill=tk.BOTH, expand=True)
        
        invoice_frame = ttk.Frame(items_frame)
        invoice_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.subtotal_var = tk.StringVar(value="0")
        self.shipping_var = tk.StringVar(value="0")
        self.total_var = tk.StringVar(value="0")
        
        ttk.Label(invoice_frame, text="جمع کل محصولات (تومان):", font=('Tahoma', 11)).pack(side=tk.RIGHT, padx=10)
        ttk.Label(invoice_frame, textvariable=self.subtotal_var, font=('Tahoma', 11, 'bold')).pack(side=tk.RIGHT)
        ttk.Label(invoice_frame, text="هزینه ارسال (تومان):", font=('Tahoma', 11)).pack(side=tk.RIGHT, padx=10)
        ttk.Label(invoice_frame, textvariable=self.shipping_var, font=('Tahoma', 11, 'bold')).pack(side=tk.RIGHT)
        ttk.Label(invoice_frame, text="جمع فاکتور (تومان):", font=('Tahoma', 11)).pack(side=tk.RIGHT, padx=10)
        ttk.Label(invoice_frame, textvariable=self.total_var, font=('Tahoma', 11, 'bold')).pack(side=tk.RIGHT)

    def create_label_print_tab(self, notebook):
        """ایجاد تب جدید برای پرینت برچسب پستی"""
        label_frame = ttk.Frame(notebook, padding=10)
        notebook.add(label_frame, text="پرینت برچسب پستی")
        
        # فریم برای پیش‌نمایش و دکمه
        preview_frame = ttk.LabelFrame(label_frame, text="راهنمای پرینت برچسب پستی", padding=10)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # تغییر متن preview_text برای نمایش راهنما
        self.label_preview_text = tk.Text(preview_frame, wrap=tk.WORD, font=("Tahoma", 10), height=15, width=60, 
                                        state=tk.DISABLED, relief=tk.FLAT, background=self.root.cget('bg'))
        self.label_preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # دکمه پرینت
        self.print_label_btn = ttk.Button(label_frame, text="پرینت برچسب", command=self.print_label)
        self.print_label_btn.pack(pady=10)
        self.print_label_btn.config(state=tk.DISABLED) # ابتدا غیرفعال باشد
        
        # نمایش متن راهنما در ابتدا
        self.label_preview_text.config(state=tk.NORMAL)
        self.label_preview_text.delete(1.0, tk.END)
        self.label_preview_text.insert(tk.END, "برای مشاهده پیش‌نمایش و پرینت برچسب پستی، لطفاً یک سفارش را از لیست سفارش‌ها انتخاب کرده و سپس روی دکمه 'پرینت برچسب' کلیک کنید.\n\nپس از کلیک، برچسب در مرورگر پیش‌فرض شما باز خواهد شد. از آنجا می‌توانید با فشردن کلیدهای Ctrl+P (یا Command+P در مک) پنجره پرینت را باز کرده و برچسب را پرینت نمایید.")
        self.label_preview_text.config(state=tk.DISABLED)

    def create_order_notes_tab(self):
        """ایجاد تب توضیحات سفارش"""
        if self.notes_tab_frame is not None:
            return
            
        self.notes_tab_frame = ttk.Frame(self.notebook, padding=10)
        
        # فریم برای توضیحات
        notes_frame = ttk.LabelFrame(self.notes_tab_frame, text="توضیحات سفارش", padding=10)
        notes_frame.pack(fill=tk.BOTH, expand=True)
        
        # ویجت متن برای نمایش توضیحات
        self.notes_text = tk.Text(notes_frame, wrap=tk.WORD, font=("Tahoma", 10), height=10, 
                                 state=tk.DISABLED, relief=tk.FLAT, background=self.root.cget('bg'))
        scrollbar = ttk.Scrollbar(notes_frame, orient=tk.VERTICAL, command=self.notes_text.yview)
        self.notes_text.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def show_floating_message(self, message, duration=3000):
        self.floating_message_var.set(message)
        self.floating_message.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-20)
        self.root.after(duration, self.hide_floating_message)
    
    def hide_floating_message(self):
        self.floating_message.place_forget()
    
    def setup_auto_refresh(self):
        """تنظیم تایمر برای به‌روزرسانی خودکار بر اساس سایت‌های فعال"""
        # حذف تایمرهای قبلی
        if hasattr(self, 'auto_refresh_id'):
            self.root.after_cancel(self.auto_refresh_id)
        
        # یافتن کوچکترین فاصله زمانی در بین سایت‌های فعال
        min_interval = 10  # مقدار پیش‌فرض
        active_sites = [s for s in self.sites if s['enabled']]
        if active_sites:
            min_interval = min(site['refresh_interval'] for site in active_sites)
        
        # تنظیم تایمر جدید
        self.auto_refresh_id = self.root.after(min_interval * 60000, self.auto_refresh)
    
    def auto_refresh(self):
        if not self.refresh_in_progress:
            self.refresh_in_progress = True
            self.refresh_btn.config(state=tk.DISABLED)
            self.show_floating_message("در حال بررسی خودکار سفارش‌های جدید و به‌روزرسانی وضعیت‌ها...")
            threading.Thread(target=self.check_new_orders_thread, daemon=True).start()
        self.setup_auto_refresh()  # تنظیم مجدد تایمر
    
    def manual_refresh(self):
        if not self.refresh_in_progress:
            self.refresh_in_progress = True
            self.refresh_btn.config(state=tk.DISABLED)
            self.show_floating_message("در حال دریافت سفارش‌های جدید و به‌روزرسانی وضعیت‌ها...")
            threading.Thread(target=self.check_new_orders_thread, daemon=True).start()

    def check_new_orders_thread(self):
        """بررسی سفارش‌های جدید و به‌روزرسانی وضعیت‌ها برای همه سایت‌های فعال"""
        total_new_orders = 0
        total_updated_orders = 0
        
        for site in self.sites:
            if site['enabled']:
                new, updated = self.fetch_and_update_orders_for_site(site)
                total_new_orders += new
                total_updated_orders += updated
        
        self.refresh_in_progress = False
        self.root.after(0, lambda: self.refresh_btn.config(state=tk.NORMAL))
        self.root.after(0, self.load_orders_from_db) # بارگذاری مجدد Treeview پس از اتمام همه سایت‌ها
        
        if total_new_orders > 0 or total_updated_orders > 0:
            self.root.after(0, lambda: self.show_floating_message(f"{total_new_orders} سفارش جدید و {total_updated_orders} سفارش به‌روزرسانی شد"))
        else:
            self.root.after(0, lambda: self.show_floating_message("هیچ سفارش جدید یا به‌روزرسانی شده‌ای یافت نشد"))
        
        now = datetime.now().strftime('%H:%M:%S')
        self.root.after(0, lambda: self.status_var.set(f"آخرین بررسی: {now} | آماده"))


    def fetch_and_update_orders_for_site(self, site, initial_load=False):
        """دریافت و بروزرسانی سفارش‌ها برای یک سایت خاص"""
        new_orders_count = 0
        updated_orders_count = 0
        try:
            api_url = f"https://{site['domain']}/wp-json/wc/v3/orders"
            params = {
                "consumer_key": site['consumer_key'],
                "consumer_secret": site['consumer_secret'],
                "per_page": 100, # افزایش تعداد برای بررسی بیشتر سفارشات قدیمی
                "orderby": "date",
                "order": "desc"
            }
            headers = {"User-Agent": "WooCommerce-Python-App/1.0", "Accept": "application/json"}
            response = requests.get(api_url, params=params, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                remote_orders = response.json()
                
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                
                for order_data in remote_orders:
                    order_id = order_data['id']
                    
                    c.execute("SELECT status FROM orders WHERE id=? AND site_id=?", (order_id, site['id']))
                    local_order_status = c.fetchone()

                    shipping_info = order_data.get('shipping', {})
                    address_parts = [shipping_info.get('address_1', ''), shipping_info.get('city', '')]
                    shipping_address = ", ".join(filter(None, address_parts))
                    shipping_postcode = shipping_info.get('postcode', '')

                    # Prepare order data for upsert
                    order_values = (
                        order_id,
                        site['id'],
                        order_data['date_created'],
                        order_data['status'],
                        float(order_data['total']),
                        order_data['currency'],
                        order_data['payment_method_title'],
                        f"{order_data['billing']['first_name']} {order_data['billing']['last_name']}",
                        order_data['billing'].get('email', ''),
                        order_data['billing'].get('phone', ''),
                        shipping_address,
                        shipping_postcode,
                        order_data['shipping_lines'][0]['method_title'] if order_data.get('shipping_lines') else '',
                        float(order_data['shipping_total']),
                    )
                    
                    if local_order_status:
                        # Order exists, check for status change and other updates
                        if local_order_status[0] != order_data['status']:
                            updated_orders_count += 1
                        
                        c.execute('''UPDATE orders SET 
                                    date_created=?, status=?, total=?, currency=?, payment_method=?,
                                    customer_name=?, customer_email=?, customer_phone=?,
                                    shipping_address=?, shipping_postcode=?, shipping_method=?, shipping_total=?
                                    WHERE id=? AND site_id=?''',
                                (order_values[2], order_values[3], order_values[4], order_values[5], order_values[6],
                                 order_values[7], order_values[8], order_values[9], order_values[10],
                                 order_values[11], order_values[12], order_values[13],
                                 order_values[0], order_values[1]))
                        
                        # Update order items (clear and re-insert for simplicity)
                        c.execute("DELETE FROM order_items WHERE order_id=?", (order_id,))
                        for item in order_data['line_items']:
                            product_name = html.unescape(item['name'])
                            quantity = item.get('quantity', 0)
                            price = float(item.get('price', 0.0))
                            item_total = float(item.get('total', 0.0))
                            if price == 0.0 and item_total > 0.0 and quantity > 0:
                                price = item_total / quantity
                            c.execute('''INSERT INTO order_items (order_id, product_name, quantity, price, total) 
                                        VALUES (?, ?, ?, ?, ?)''', (order_id, product_name, quantity, price, item_total))

                    else:
                        # New order, insert it
                        c.execute('''INSERT INTO orders (
                            id, site_id, date_created, status, total, currency, payment_method,
                            customer_name, customer_email, customer_phone,
                            shipping_address, shipping_postcode, shipping_method, shipping_total, seen
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', order_values + (0,)) # seen = 0 for new orders
                        
                        for item in order_data['line_items']:
                            product_name = html.unescape(item['name'])
                            quantity = item.get('quantity', 0)
                            price = float(item.get('price', 0.0))
                            item_total = float(item.get('total', 0.0))
                            if price == 0.0 and item_total > 0.0 and quantity > 0:
                                price = item_total / quantity
                            c.execute('''INSERT INTO order_items (order_id, product_name, quantity, price, total) 
                                        VALUES (?, ?, ?, ?, ?)''', (order_id, product_name, quantity, price, item_total))
                        
                        new_orders_count += 1
                        if not initial_load:
                            self.play_new_order_sound()
                    
                    # دریافت و ذخیره توضیحات سفارش
                    self.fetch_and_save_order_notes(site, order_id, conn)
                
                conn.commit()

            else:
                self.root.after(0, lambda: self.show_floating_message(f"خطا در دریافت اطلاعات از سایت {site['domain']}: {response.status_code}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_floating_message(f"خطای شبکه برای سایت {site['domain']}: {e}"))
        finally:
            if 'conn' in locals() and conn:
                conn.close()
            return new_orders_count, updated_orders_count

    def fetch_and_save_order_notes(self, site, order_id, conn):
        """دریافت و ذخیره توضیحات سفارش از ووکامرس"""
        try:
            api_url = f"https://{site['domain']}/wp-json/wc/v3/orders/{order_id}/notes"
            params = {
                "consumer_key": site['consumer_key'],
                "consumer_secret": site['consumer_secret'],
            }
            headers = {"User-Agent": "WooCommerce-Python-App/1.0", "Accept": "application/json"}
            response = requests.get(api_url, params=params, headers=headers, timeout=15, verify=False)
            
            if response.status_code == 200:
                notes = response.json()
                c = conn.cursor()
                
                # حذف توضیحات قبلی
                c.execute("DELETE FROM order_notes WHERE order_id=?", (order_id,))
                
                # ذخیره توضیحات جدید
                for note in notes:
                    c.execute('''INSERT INTO order_notes (id, order_id, author, date_created, note)
                                VALUES (?, ?, ?, ?, ?)''',
                             (note['id'], order_id, note['author'], note['date_created'], note['note']))
                
                conn.commit()
        except Exception as e:
            print(f"خطا در دریافت توضیحات سفارش {order_id}: {e}")

    def play_new_order_sound(self):
        """پخش صدای سفارش جدید"""
        if os.path.exists(NEW_ORDER_SOUND):
            try:
                winsound.PlaySound(NEW_ORDER_SOUND, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"خطا در پخش صدا: {e}")
        else:
            print(f"فایل صدا یافت نشد: {NEW_ORDER_SOUND}")

    def format_currency(self, amount):
        """فرمت‌دهی مبلغ به صورت عددی بدون واحد"""
        try:
            num = float(amount)
            return f"{num:,.0f}"
        except (ValueError, TypeError):
            return "0"

    def convert_to_jalali(self, date_str):
        try:
            dt = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
            return jdatetime.datetime.fromgregorian(datetime=dt).strftime('%Y/%m/%d %H:%M')
        except:
            return date_str

    def save_order_to_db(self, order, site_id):
        # این تابع دیگر استفاده نمی‌شود و منطق آن به fetch_and_update_orders_for_site منتقل شده است
        pass

    def load_orders_from_db(self):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        # دریافت سفارش‌ها به همراه نام سایت
        c.execute('''SELECT orders.*, sites.domain 
                     FROM orders 
                     LEFT JOIN sites ON orders.site_id = sites.id 
                     ORDER BY orders.date_created DESC''')
        self.orders = c.fetchall()
        conn.close()
        
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        current_selection_id = None
        if self.orders_tree.selection():
            current_selection_id = self.orders_tree.item(self.orders_tree.selection()[0])['values'][1]

        for order in self.orders:
            # استخراج اطلاعات سفارش
            order_id = order[0]
            site_domain = order[-1]  # آخرین ستون که نام سایت است
            date_created = order[2]
            status_english = order[3]
            total = order[4]
            customer_name = order[7]
            seen = order[14]
            
            # ترجمه وضعیت سفارش
            status_persian = self.status_translation.get(status_english.lower(), status_english)
            
            tags = ('new_order',) if seen == 0 else ()
            if seen == 0: self.new_order_ids.add(order_id)
            
            inserted_item_id = self.orders_tree.insert("", "end", values=(
                site_domain,
                order_id, 
                self.convert_to_jalali(date_created), 
                customer_name, 
                status_persian,  # استفاده از وضعیت ترجمه شده
                self.format_currency(total)
            ), tags=tags)
            
            # اگر این آیتم همان آیتم انتخاب شده قبلی است، دوباره آن را انتخاب کن
            if current_selection_id == order_id:
                self.orders_tree.selection_set(inserted_item_id)
                self.orders_tree.focus(inserted_item_id)
            
        if not self.orders: self.first_run = True
        else: self.first_run = False

    def on_order_select(self, event):
        selected = self.orders_tree.selection()
        if not selected: return
        
        order_id = self.orders_tree.item(selected[0])['values'][1]  # شماره سفارش در ستون دوم
        self.current_order_id = order_id
        
        # به‌روزرسانی عنوان بخش جزئیات
        site_name = self.orders_tree.item(selected[0])['values'][0]  # نام سایت در ستون اول
        self.details_frame.configure(text=f"جزئیات سفارش شماره {order_id} از سایت {site_name}")
        
        self.mark_order_as_seen(order_id)
        if order_id in self.new_order_ids:
            # remove the 'new_order' tag
            for item_id in self.orders_tree.get_children():
                if self.orders_tree.item(item_id, 'values')[1] == order_id:
                    self.orders_tree.item(item_id, tags=())
                    break
            self.new_order_ids.discard(order_id)
        
        self.show_order_details(order_id)
        self.update_label_preview(order_id) # فراخوانی تابع برای به‌روزرسانی پیش‌نمایش برچسب
        self.print_label_btn.config(state=tk.NORMAL) # فعال کردن دکمه پرینت پس از انتخاب سفارش

    def mark_order_as_seen(self, order_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE orders SET seen=1 WHERE id=?", (order_id,))
        conn.commit()
        conn.close()

    def show_order_details(self, order_id):
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT * FROM orders WHERE id=?", (order_id,))
        order = c.fetchone()
        
        if order:
            self.show_customer_info(order)
            self.show_shipping_info(order)
            c.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,))
            items = c.fetchall()
            self.show_order_items(items, order)
            
            # نمایش توضیحات سفارش (اگر وجود داشته باشد)
            c.execute("SELECT * FROM order_notes WHERE order_id=?", (order_id,))
            notes = c.fetchall()
            self.show_order_notes(notes)
        
        conn.close()

    def show_customer_info(self, order):
        for item in self.customer_tree.get_children(): 
            self.customer_tree.delete(item)
        
        # اندیس‌ها بر اساس ساختار صحیح جدول
        customer_info = [("نام کامل", order[7]), ("ایمیل", order[8]), ("تلفن", order[9])]
        
        for i, (title, value) in enumerate(customer_info):
            tag = 'even_row' if i % 2 == 0 else 'odd_row'
            if value: 
                self.customer_tree.insert("", "end", values=(title, value), tags=(tag,))

    def show_shipping_info(self, order):
        for item in self.shipping_tree.get_children(): 
            self.shipping_tree.delete(item)
        
        # اندیس‌ها بر اساس ساختار صحیح و تضمین‌شده جدول
        shipping_info = [
            ("آدرس", order[10]),
            ("کد پستی", order[11]),
            ("روش ارسال", order[12]),
            ("هزینه ارسال", self.format_currency(order[13]))
        ]
        
        for i, (title, value) in enumerate(shipping_info):
            tag = 'even_row' if i % 2 == 0 else 'odd_row'
            if value: 
                self.shipping_tree.insert("", "end", values=(title, value), tags=(tag,))

    def show_order_items(self, items, order):
        for item in self.items_tree.get_children(): 
            self.items_tree.delete(item)
        
        subtotal = sum(item[5] for item in items)
        
        for i, item in enumerate(items):
            tag = 'even_row' if i % 2 == 0 else 'odd_row'
            self.items_tree.insert("", "end", values=(
                item[2], item[3], self.format_currency(item[4]), self.format_currency(item[5])
            ), tags=(tag,))
        
        self.subtotal_var.set(self.format_currency(subtotal))
        self.shipping_var.set(self.format_currency(order[13])) # هزینه ارسال
        self.total_var.set(self.format_currency(order[4])) # جمع کل

    def show_order_notes(self, notes):
        """نمایش توضیحات سفارش در تب مربوطه"""
        # حذف تب توضیحات اگر قبلاً وجود داشت
        if self.notes_tab_frame and self.notes_tab_frame in self.notebook.tabs():
            self.notebook.forget(self.notes_tab_frame)
        
        # اگر توضیحاتی وجود دارد
        if notes:
            # ایجاد تب توضیحات اگر قبلاً ساخته نشده
            if self.notes_tab_frame is None:
                self.create_order_notes_tab()
            
            # افزودن تب به نوت‌بوک
            self.notebook.add(self.notes_tab_frame, text="توضیحات سفارش")
            
            # نمایش توضیحات
            self.notes_text.config(state=tk.NORMAL)
            self.notes_text.delete(1.0, tk.END)
            
            for note in notes:
                note_date = self.convert_to_jalali(note[3])  # تاریخ ایجاد
                author = "سیستم" if note[2] == "system" else "مشتری"  # نویسنده
                note_content = note[4]  # متن توضیح
                
                self.notes_text.insert(tk.END, f"{note_date} - {author}:\n")
                self.notes_text.insert(tk.END, f"{note_content}\n\n")
                self.notes_text.insert(tk.END, "-" * 50 + "\n\n")
            
            self.notes_text.config(state=tk.DISABLED)

    def update_label_preview(self, order_id):
        """تنظیم متن راهنما برای تب پرینت برچسب پستی"""
        self.label_preview_text.config(state=tk.NORMAL)
        self.label_preview_text.delete(1.0, tk.END)
        self.label_preview_text.insert(tk.END, "سفارش انتخاب شد. برای مشاهده و پرینت برچسب، روی دکمه 'پرینت برچسب' کلیک کنید.\n\nپس از کلیک، برچسب در مرورگر پیش‌فرض شما باز خواهد شد. از آنجا می‌توانید با فشردن کلیدهای Ctrl+P (یا Command+P در مک) پنجره پرینت را باز کرده و برچسب را پرینت نمایید.")
        self.label_preview_text.config(state=tk.DISABLED)
        self.print_label_btn.config(state=tk.NORMAL) # فعال کردن دکمه پرینت

    def print_label(self):
        """باز کردن برچسب پستی در مرورگر برای پرینت"""
        if not self.current_order_id:
            messagebox.showwarning("هشدار", "لطفاً یک سفارش را برای پرینت برچسب انتخاب کنید.")
            return

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute('''SELECT orders.*, sites.shop_address, sites.shop_postcode, sites.shop_phone 
                     FROM orders 
                     JOIN sites ON orders.site_id = sites.id 
                     WHERE orders.id=?''', (self.current_order_id,))
        order = c.fetchone()
        conn.close()

        if order:
            sender_address = order[15] if order[15] else "نامشخص"
            sender_postcode = order[16] if order[16] else "نامشخص"
            sender_phone = order[17] if order[17] else "نامشخص"
            
            customer_name = order[7]
            receiver_address = order[10] if order[10] else "نامشخص"
            receiver_postcode = order[11] if order[11] else "نامشخص"
            receiver_phone = order[9] if order[9] else "نامشخص"

            # محتوای HTML برای برچسب
            html_content = f"""
            <!DOCTYPE html>
            <html dir="rtl" lang="fa">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>برچسب پستی سفارش #{self.current_order_id}</title>
                <style>
                    @page {{
                        size: A5 portrait;
                        margin: 0;
                    }}
                    body {{
                        font-family: Tahoma, sans-serif;
                        margin: 0;
                        padding: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh; /* For browser view, not strictly for print */
                    }}
                    .label-container {{
                        width: 148mm; /* A5 width */
                        height: 210mm; /* A5 height */
                        padding: 10mm; /* Overall padding inside A5 */
                        box-sizing: border-box;
                        position: relative;
                        text-align: right;
                    }}
                    .sender-box, .receiver-box {{
                        border: 2px solid #333;
                        border-radius: 15px;
                        padding: 15px;
                        margin: 5mm; /* Reduced margin for more content space */
                        width: 100mm; /* Fixed width for consistent size, roughly 2/3 of A5 width */
                        box-sizing: border-box; /* Include padding and border in the width */
                    }}
                    .sender-box {{
                        position: absolute;
                        top: 10mm; /* From top edge of A5 page */
                        right: 10mm; /* From right edge for RTL */
                    }}
                    .receiver-box {{
                        position: absolute;
                        bottom: 10mm; /* From bottom edge of A5 page */
                        left: 10mm; /* From left edge for RTL */
                    }}
                    b {{ font-weight: bold; }}
                    /* Spacing between lines */
                    .info-line {{
                        margin-bottom: 5px; /* Adjust as needed for spacing */
                    }}
                    .info-line:last-child {{
                        margin-bottom: 0;
                    }}

                    @media print {{
                        body {{
                            min-height: auto;
                        }}
                        .label-container {{
                            border: none; /* No border for the overall A5 on print */
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="label-container">
                    <div class="sender-box">
                        <div class="info-line"><b>آدرس فرستنده:</b></div>
                        <div class="info-line">{sender_address}</div>
                        <div class="info-line"><b>کد پستی:</b> {sender_postcode}</div>
                        <div class="info-line"><b>تلفن:</b> {sender_phone}</div>
                    </div>
                    <div class="receiver-box">
                        <div class="info-line"><b>آدرس گیرنده:</b></div> 
                        <div class="info-line">{receiver_address}</div>
                        <div class="info-line"><b>کد پستی:</b> {receiver_postcode}</div>
                        <div class="info-line"><b>تلفن:</b> {receiver_phone}</div>
                        <div class="info-line"><b>نام گیرنده:</b> {customer_name}</div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # ذخیره محتوای HTML در یک فایل موقت
            temp_file_path = os.path.join(tempfile.gettempdir(), f"shipping_label_order_{self.current_order_id}.html")
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            # باز کردن فایل HTML در مرورگر پیش‌فرض
            webbrowser.open(f"file:///{temp_file_path}")
            
            # پیام موفقیت و راهنمای پرینت
            messagebox.showinfo("پرینت برچسب", "برچسب پستی در مرورگر پیش‌فرض شما باز شد.\n\nلطفاً از آنجا با فشردن کلیدهای Ctrl+P (یا Command+P در مک) پنجره پرینت را باز کرده و برچسب را پرینت نمایید.")
        else:
            messagebox.showerror("خطا", "اطلاعات سفارش برای ایجاد برچسب یافت نشد.")

    def check_for_updates_in_thread(self):
        """بررسی آپدیت در یک نخ جداگانه"""
        threading.Thread(target=self.check_for_updates, daemon=True).start()

    def check_for_updates(self):
        """بررسی وجود نسخه جدید برنامه در گیت‌هاب"""
        try:
            # بررسی زمان آخرین بررسی
            last_check = self.get_last_check_time()
            now = datetime.now().timestamp()
            
            # اگر کمتر از یک هفته از آخرین بررسی گذشته، از چک کردن صرف‌نظر کن
            if last_check and (now - last_check) < 7 * 24 * 3600:
                return
                
            # دریافت نسخه از گیت‌هاب
            response = requests.get(VERSION_FILE_URL, timeout=10)
            response.raise_for_status()
            
            # استخراج نسخه از محتوای فایل
            latest_version = response.text.strip()
            
            # مقایسه نسخه‌ها
            if self.compare_versions(latest_version, CURRENT_VERSION) > 0:
                # نمایش پیام به کاربر در نخ رابط کاربری
                self.root.after(0, lambda: self.prompt_update(latest_version))
            
            # ذخیره زمان آخرین بررسی
            self.save_last_check_time(now)
            
        except Exception as e:
            print(f"خطا در بررسی آپدیت: {e}")

    def prompt_update(self, latest_version):
        """نمایش پیام برای آپدیت و اقدام"""
        if messagebox.askyesno("نسخه جدید", 
                              f"نسخه جدید {latest_version} موجود است!\nآیا می‌خواهید اکنون دانلود و نصب کنید؟"):
            threading.Thread(target=self.download_and_install_update, args=(latest_version,), daemon=True).start()

    def get_last_check_time(self):
        """دریافت زمان آخرین بررسی از دیتابیس"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("SELECT value FROM app_settings WHERE key='last_update_check'")
            result = c.fetchone()
            if result:
                return float(result[0])
        except:
            pass
        return None

    def save_last_check_time(self, timestamp):
        """ذخیره زمان آخرین بررسی در دیتابیس"""
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        try:
            c.execute("REPLACE INTO app_settings (key, value) VALUES (?, ?)", 
                     ('last_update_check', str(timestamp)))
            conn.commit()
        except Exception as e:
            print(f"خطا در ذخیره زمان بررسی آپدیت: {e}")
        finally:
            conn.close()

    def compare_versions(self, v1, v2):
        """مقایسه دو نسخه به صورت عددی"""
        def parse_version(v):
            return [int(x) for x in v.split('.')]
        
        try:
            v1_parts = parse_version(v1)
            v2_parts = parse_version(v2)
            
            # مقایسه بخش‌های نسخه
            for i in range(max(len(v1_parts), len(v2_parts))):
                v1_part = v1_parts[i] if i < len(v1_parts) else 0
                v2_part = v2_parts[i] if i < len(v2_parts) else 0
                
                if v1_part > v2_part:
                    return 1
                elif v1_part < v2_part:
                    return -1
            return 0
        except:
            return 0

    def download_and_install_update(self, version):
        """دانلود و نصب نسخه جدید برنامه"""
        try:
            # ساخت URL دانلود بر اساس نسخه
            download_url = f"{GITHUB_REPO}/releases/download/v{version}/woocommerce-orders.exe"
            
            # دانلود فایل
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # ذخیره موقت فایل دانلود شده
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, "woocommerce_orders_update.exe")
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # پیدا کردن مسیر اجرای برنامه فعلی
            current_exe = sys.executable
            current_dir = os.path.dirname(current_exe)
            
            # ایجاد اسکریپت برای جایگزینی
            if platform.system() == 'Windows':
                script = f"""
                @echo off
                TIMEOUT /T 3 /NOBREAK >NUL
                TASKKILL /F /IM "{os.path.basename(current_exe)}"
                DEL "{current_exe}"
                MOVE "{temp_file}" "{current_exe}"
                START "" "{current_exe}"
                DEL "%~f0"
                """
                script_file = os.path.join(current_dir, "update_script.bat")
                with open(script_file, 'w') as f:
                    f.write(script)
                
                # اجرای اسکریپت و خروج از برنامه
                subprocess.Popen([script_file], shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                sys.exit(0)
                
            else:  # سیستم‌عامل غیر ویندوز
                # در سیستم‌های غیر ویندوزی، به کاربر اطلاع می‌دهیم که باید دستی جایگزینی کند
                messagebox.showinfo("دانلود کامل", 
                                   "فایل آپدیت با موفقیت دانلود شد.\nلطفاً برنامه فعلی را ببندید و فایل جدید را جایگزین کنید.")
                # باز کردن پوشه حاوی فایل دانلود شده
                webbrowser.open(temp_dir)
                
        except Exception as e:
            messagebox.showerror("خطا در آپدیت", f"خطا در دانلود یا نصب آپدیت:\n{str(e)}")

if __name__ == "__main__":
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    root = tk.Tk()
    app = WooCommerceOrdersApp(root)
    root.mainloop()