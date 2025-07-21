import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import socket
import json
import threading
import datetime
import os
import xml.etree.ElementTree as ET
import requests
import hashlib
import time
from pathlib import Path

# Import pyzk for ZKTeco devices
try:
    from zk import ZK, const
    PYZK_AVAILABLE = True
except ImportError:
    PYZK_AVAILABLE = False

class AttendanceApp:
    def __init__(self):
        self.root = tk.Tk()
        self.setup_ui()
        
        # تنظیمات اصلی
        self.UDP_IP = "192.168.88.200"
        self.UDP_PORT = 5005
        self.SERVER_URL = "https://hozor.neyrizpooyesh.ir/api.php"
        self.SECRET_KEY = "kArA_f500_sTrOnG_kEy_2025_nEyRiZ_pOoYeSh"
        
        # فایل JSON
        self.data_file = "attendance_data.json"
        self.ensure_data_file()
        
        # وضعیت اتصال UDP (کارا 200)
        self.socket = None
        self.listening = False
        self.pending_sync = []
        self.connected_devices = set()
        
        # ⭐ دستگاه‌های ZKTeco
        self.zkteco_devices = {}
        self.zkteco_threads = {}
        self.zkteco_status = {}
        self.load_zkteco_config()
        
        # متغیرهای کنترل اتصال خودکار به سرور
        self.server_connection_active = False
        self.server_connection_timer = None
        self.server_connection_interval = 5
        self.last_connection_error = ""
        
        # شمارنده‌های آماری
        self.entry_count = 0
        self.exit_count = 0
        self.ignored_count = 0
        
        # ⭐ کش رویدادهای اخیر برای تشخیص تکرار (جداگانه برای هر نوع دستگاه)
        self.recent_events_cache_kara = []  # برای دستگاه‌های کارا
        self.recent_events_cache_zkteco = []  # برای دستگاه‌های ZKTeco
        self.cache_size = 50
        
        # ⭐ کش رویدادهای روزانه برای تشخیص Duty On/Off
        self.daily_events_cache = {}
        
        # شروع سرویس UDP (کارا 200)
        self.start_udp_listener()
        
        # ⭐ شروع مانیتورینگ دستگاه‌های ZKTeco
        self.start_zkteco_monitoring()
        
        # ⭐ شروع Time Sync هر 2 دقیقه
        self.start_time_sync()
        
        # شروع بررسی خودکار اتصال به سرور
        self.start_auto_server_connection()

    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        self.root.title("سیستم حضور و غیاب - پشتیبانی از کارا F500 و ZKTeco")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # تنظیم فونت فارسی
        self.setup_fonts()
        
        # منو بار
        self.create_menu()
        
        # فریم اصلی
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # ⭐ فریم بالا - وضعیت دستگاه‌ها
        self.create_device_status_frame(main_frame)
        
        # فریم میانی - نمایش داده‌ها
        data_frame = ttk.LabelFrame(main_frame, text="رویدادهای حضور و غیاب (فیلتر شده)", padding=10)
        data_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # جدول نمایش داده‌ها
        columns = ("زمان", "نوع", "کاربر", "وضعیت", "روش تایید", "دستگاه", "نوع دستگاه")
        self.tree = ttk.Treeview(data_frame, columns=columns, show="headings", height=12)
        
        # تنظیم ستون‌ها
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "نوع دستگاه":
                self.tree.column(col, width=100, anchor="center")
            else:
                self.tree.column(col, width=130, anchor="center")
        
        # اسکرول بار
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="right", fill="both", expand=True)
        scrollbar.pack(side="left", fill="y")
        
        # فریم آمار
        stats_frame = ttk.LabelFrame(main_frame, text="آمار رویدادها (بدون تکرار)", padding=10)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # شمارنده‌های آماری
        stats_container = ttk.Frame(stats_frame)
        stats_container.pack(fill=tk.X)
        
        ttk.Label(stats_container, text="تعداد ورودها:", font=self.persian_font).pack(side=tk.RIGHT)
        self.entry_count_label = ttk.Label(stats_container, text="0", font=self.persian_font_bold, foreground="green")
        self.entry_count_label.pack(side=tk.RIGHT, padx=(10, 20))
        
        ttk.Label(stats_container, text="تعداد خروجها:", font=self.persian_font).pack(side=tk.RIGHT)
        self.exit_count_label = ttk.Label(stats_container, text="0", font=self.persian_font_bold, foreground="red")
        self.exit_count_label.pack(side=tk.RIGHT, padx=(10, 20))
        
        ttk.Label(stats_container, text="رویدادهای نادیده:", font=self.persian_font).pack(side=tk.RIGHT)
        self.ignored_count_label = ttk.Label(stats_container, text="0", font=self.persian_font_bold, foreground="orange")
        self.ignored_count_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # فریم پایین - لاگ خام
        log_frame = ttk.LabelFrame(main_frame, text="لاگ سیستم", padding=10)
        log_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, 
                                                font=("Consolas", 9))
        self.log_text.pack(fill=tk.X)
        
        # فریم پایین - اطلاعات برنامه‌نویس
        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X)
        
        credit_label = ttk.Label(info_frame, text="طراح و برنامه‌نویس: علی مطلقیان - پشتیبانی از دستگاه‌های کارا F500 و ZKTeco", 
                               font=self.persian_font, foreground="#666")
        credit_label.pack(pady=5)

    def create_device_status_frame(self, parent):
        """⭐ ایجاد فریم وضعیت دستگاه‌ها"""
        device_frame = ttk.LabelFrame(parent, text="وضعیت دستگاه‌ها", padding=10)
        device_frame.pack(fill=tk.X, pady=(0, 10))
        
        # فریم کارا 200
        kara_frame = ttk.LabelFrame(device_frame, text="دستگاه‌های کارا F500 (UDP)", padding=5)
        kara_frame.pack(fill=tk.X, pady=(0, 10))
        
        kara_content = ttk.Frame(kara_frame)
        kara_content.pack(fill=tk.X)
        
        ttk.Label(kara_content, text="وضعیت:", font=self.persian_font).pack(side=tk.RIGHT)
        self.status_label = ttk.Label(kara_content, text="غیرفعال", 
                                    foreground="gray", font=self.persian_font)
        self.status_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(kara_content, text="تعداد:", font=self.persian_font).pack(side=tk.RIGHT, padx=(20, 0))
        self.device_count_label = ttk.Label(kara_content, text="0", 
                                          foreground="blue", font=self.persian_font_bold)
        self.device_count_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # فریم ZKTeco
        zk_frame = ttk.LabelFrame(device_frame, text="دستگاه‌های ZKTeco", padding=5)
        zk_frame.pack(fill=tk.X, pady=(0, 10))
        
        zk_content = ttk.Frame(zk_frame)
        zk_content.pack(fill=tk.X)
        
        # دکمه مدیریت دستگاه‌های ZKTeco
        ttk.Button(zk_content, text="🔧 مدیریت دستگاه‌های ZKTeco", 
                  command=self.open_zkteco_manager).pack(side=tk.LEFT)
        
        # نمایش تعداد دستگاه‌های ZKTeco
        ttk.Label(zk_content, text="تعداد تعریف شده:", font=self.persian_font).pack(side=tk.RIGHT, padx=(20, 0))
        self.zkteco_count_label = ttk.Label(zk_content, text="0", 
                                           foreground="blue", font=self.persian_font_bold)
        self.zkteco_count_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # فریم وضعیت سرور و سینک
        server_frame = ttk.Frame(device_frame)
        server_frame.pack(fill=tk.X)
        
        self.sync_button = ttk.Button(server_frame, text="سینک با سرور", 
                                    command=self.sync_data, state="normal")
        self.sync_button.pack(side=tk.LEFT)
        
        ttk.Label(server_frame, text="وضعیت سرور:", font=self.persian_font).pack(side=tk.LEFT, padx=(20, 0))
        self.server_status = ttk.Label(server_frame, text="غیرفعال", 
                                     foreground="red", font=self.persian_font)
        self.server_status.pack(side=tk.LEFT, padx=(10, 0))

    def setup_fonts(self):
        """تنظیم فونت‌های فارسی"""
        try:
            self.persian_font = ("Tahoma", 10)
            self.persian_font_bold = ("Tahoma", 10, "bold")
        except:
            self.persian_font = ("Arial", 10)
            self.persian_font_bold = ("Arial", 10, "bold")

    def create_menu(self):
        """ایجاد منو"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # منو فایل
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="فایل", menu=file_menu)
        file_menu.add_command(label="نمایش داده‌های ذخیره شده", command=self.show_saved_data)
        file_menu.add_command(label="پاک کردن داده‌ها", command=self.clear_data)
        file_menu.add_separator()
        file_menu.add_command(label="خروج", command=self.root.quit)
        
        # ⭐ منو دستگاه‌ها
        device_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="دستگاه‌ها", menu=device_menu)
        device_menu.add_command(label="🔧 مدیریت دستگاه‌های ZKTeco", command=self.open_zkteco_manager)
        device_menu.add_command(label="📊 وضعیت دستگاه‌های ZKTeco", command=self.show_zkteco_status)
        device_menu.add_separator()
        device_menu.add_command(label="🟢 فعال کردن UDP (کارا)", command=self.enable_udp_listener)
        device_menu.add_command(label="🔴 غیرفعال کردن UDP (کارا)", command=self.disable_udp_listener)
        device_menu.add_command(label="🔄 بازراه‌اندازی UDP (کارا)", command=self.restart_udp_listener)
        device_menu.add_command(label="🔄 بازراه‌اندازی ZKTeco", command=self.restart_zkteco_monitoring)
        
        # منو ابزار
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ابزار", menu=tools_menu)
        tools_menu.add_command(label="تست اتصال سرور", command=self.test_server_connection)
        tools_menu.add_command(label="مشاهده مشکل اتصال", command=self.show_connection_error)
        tools_menu.add_command(label="تلاش مجدد برای اتصال", command=self.manual_connection_retry)
        tools_menu.add_command(label="تست ارسال نمونه", command=self.test_sample_data)
        tools_menu.add_command(label="نمایش کش رویدادها", command=self.show_events_cache)
        tools_menu.add_command(label="نمایش XML کامل", command=self.debug_xml_data)

    def ensure_data_file(self):
        """اطمینان از وجود فایل JSON"""
        if not os.path.exists(self.data_file):
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "events": [], 
                    "last_sync": None, 
                    "device_uid": None,
                    "zkteco_devices": []
                }, f, ensure_ascii=False, indent=2)

    def load_zkteco_config(self):
        """⭐ بارگذاری تنظیمات دستگاه‌های ZKTeco"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            zkteco_list = data.get("zkteco_devices", [])
            self.zkteco_devices = {}
            
            for device in zkteco_list:
                device_id = device.get("device_id")
                if device_id:
                    self.zkteco_devices[device_id] = device
                    self.zkteco_status[device_id] = "غیرفعال"
            
            self.safe_update_zkteco_count()
            self.safe_log_message(f"📱 {len(self.zkteco_devices)} دستگاه ZKTeco بارگذاری شد")
            
        except Exception as e:
            self.safe_log_message(f"❌ خطا در بارگذاری تنظیمات ZKTeco: {e}")

    def save_zkteco_config(self):
        """⭐ ذخیره تنظیمات دستگاه‌های ZKTeco"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"events": [], "last_sync": None, "device_uid": None}
        
        data["zkteco_devices"] = list(self.zkteco_devices.values())
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def open_zkteco_manager(self):
        """⭐ باز کردن پنجره مدیریت دستگاه‌های ZKTeco"""
        if not PYZK_AVAILABLE:
            messagebox.showerror("خطا", "کتابخانه pyzk نصب نیست!\nلطفاً با دستور زیر نصب کنید:\npip install pyzk")
            return
            
        manager_window = tk.Toplevel(self.root)
        manager_window.title("مدیریت دستگاه‌های ZKTeco")
        manager_window.geometry("800x600")
        manager_window.resizable(True, True)
        
        main_frame = ttk.Frame(manager_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # فریم دکمه‌ها
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(button_frame, text="➕ افزودن دستگاه جدید", 
                  command=lambda: self.add_zkteco_device(manager_window)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="🔄 بروزرسانی وضعیت", 
                  command=self.refresh_zkteco_status).pack(side=tk.LEFT, padx=(10, 0))
        
        # جدول دستگاه‌ها
        columns = ("شناسه", "IP", "Port", "وضعیت", "آخرین اتصال", "تعداد رکورد")
        self.zkteco_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.zkteco_tree.heading(col, text=col)
            self.zkteco_tree.column(col, width=120, anchor="center")
        
        # اسکرول بار برای جدول
        zk_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.zkteco_tree.yview)
        self.zkteco_tree.configure(yscrollcommand=zk_scrollbar.set)
        
        self.zkteco_tree.pack(side="left", fill="both", expand=True)
        zk_scrollbar.pack(side="right", fill="y")
        
        # فریم دکمه‌های عملیات
        action_frame = ttk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(action_frame, text="✏️ ویرایش", 
                  command=lambda: self.edit_zkteco_device(manager_window)).pack(side=tk.LEFT)
        ttk.Button(action_frame, text="🗑️ حذف", 
                  command=lambda: self.delete_zkteco_device(manager_window)).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(action_frame, text="🔌 تست اتصال", 
                  command=self.test_zkteco_connection).pack(side=tk.LEFT, padx=(10, 0))
        ttk.Button(action_frame, text="❌ بستن", 
                  command=manager_window.destroy).pack(side=tk.RIGHT)
        
        # بارگذاری داده‌ها
        self.refresh_zkteco_list()

    def add_zkteco_device(self, parent_window):
        """⭐ افزودن دستگاه ZKTeco جدید"""
        def save_device():
            device_id = device_id_var.get().strip()
            ip = ip_var.get().strip()
            port = port_var.get().strip()
            password = password_var.get().strip()
            
            if not all([device_id, ip, port]):
                messagebox.showerror("خطا", "لطفاً همه فیلدهای اجباری را پر کنید!")
                return
            
            try:
                port = int(port)
                if password:
                    password = int(password)
                else:
                    password = 0
            except ValueError:
                messagebox.showerror("خطا", "پورت و رمز عبور باید عدد باشند!")
                return
            
            if device_id in self.zkteco_devices:
                messagebox.showerror("خطا", "دستگاه با این شناسه قبلاً تعریف شده!")
                return
            
            device_config = {
                "device_id": device_id,
                "ip": ip,
                "port": port,
                "password": password,
                "created_at": datetime.datetime.now().isoformat(),
                "last_connection": None,
                "record_count": 0
            }
            
            self.zkteco_devices[device_id] = device_config
            self.zkteco_status[device_id] = "در انتظار اتصال"
            self.save_zkteco_config()
            self.safe_update_zkteco_count()
            
            messagebox.showinfo("موفق", f"دستگاه {device_id} اضافه شد!")
            add_window.destroy()
            self.refresh_zkteco_list()
            
            # شروع مانیتورینگ دستگاه جدید
            self.start_single_zkteco_monitor(device_id)
        
        add_window = tk.Toplevel(parent_window)
        add_window.title("افزودن دستگاه ZKTeco")
        add_window.geometry("400x300")
        add_window.resizable(False, False)
        
        main_frame = ttk.Frame(add_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # متغیرها
        device_id_var = tk.StringVar()
        ip_var = tk.StringVar()
        port_var = tk.StringVar(value="4370")
        password_var = tk.StringVar(value="0")
        
        # فیلدها
        ttk.Label(main_frame, text="شناسه دستگاه: *", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=device_id_var, font=self.persian_font).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="آدرس IP: *", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=ip_var, font=self.persian_font).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="پورت: *", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=port_var, font=self.persian_font).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="رمز عبور:", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=password_var, font=self.persian_font, show="*").pack(fill=tk.X, pady=(0, 20))
        
        # دکمه‌ها
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 ذخیره", command=save_device).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="❌ انصراف", command=add_window.destroy).pack(side=tk.RIGHT)

    def edit_zkteco_device(self, parent_window):
        """⭐ ویرایش دستگاه ZKTeco"""
        selection = self.zkteco_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک دستگاه را انتخاب کنید!")
            return
        
        item = self.zkteco_tree.item(selection[0])
        device_id = item['values'][0]
        device = self.zkteco_devices.get(device_id)
        
        if not device:
            messagebox.showerror("خطا", "دستگاه یافت نشد!")
            return
        
        def save_changes():
            ip = ip_var.get().strip()
            port = port_var.get().strip()
            password = password_var.get().strip()
            
            if not all([ip, port]):
                messagebox.showerror("خطا", "لطفاً همه فیلدهای اجباری را پر کنید!")
                return
            
            try:
                port = int(port)
                if password:
                    password = int(password)
                else:
                    password = 0
            except ValueError:
                messagebox.showerror("خطا", "پورت و رمز عبور باید عدد باشند!")
                return
            
            device["ip"] = ip
            device["port"] = port
            device["password"] = password
            device["updated_at"] = datetime.datetime.now().isoformat()
            
            self.save_zkteco_config()
            messagebox.showinfo("موفق", f"دستگاه {device_id} بروزرسانی شد!")
            edit_window.destroy()
            self.refresh_zkteco_list()
            
            # بازراه‌اندازی مانیتورینگ
            self.restart_single_zkteco_monitor(device_id)
        
        edit_window = tk.Toplevel(parent_window)
        edit_window.title(f"ویرایش دستگاه {device_id}")
        edit_window.geometry("400x250")
        edit_window.resizable(False, False)
        
        main_frame = ttk.Frame(edit_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # متغیرها
        ip_var = tk.StringVar(value=device.get("ip", ""))
        port_var = tk.StringVar(value=str(device.get("port", 4370)))
        password_var = tk.StringVar(value=str(device.get("password", 0)))
        
        # فیلدها
        ttk.Label(main_frame, text=f"شناسه دستگاه: {device_id}", font=self.persian_font_bold).pack(anchor="w", pady=(0, 15))
        
        ttk.Label(main_frame, text="آدرس IP: *", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=ip_var, font=self.persian_font).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="پورت: *", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=port_var, font=self.persian_font).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(main_frame, text="رمز عبور:", font=self.persian_font).pack(anchor="w", pady=(0, 5))
        ttk.Entry(main_frame, textvariable=password_var, font=self.persian_font, show="*").pack(fill=tk.X, pady=(0, 20))
        
        # دکمه‌ها
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="💾 ذخیره تغییرات", command=save_changes).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="❌ انصراف", command=edit_window.destroy).pack(side=tk.RIGHT)

    def delete_zkteco_device(self, parent_window):
        """⭐ حذف دستگاه ZKTeco"""
        selection = self.zkteco_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک دستگاه را انتخاب کنید!")
            return
        
        item = self.zkteco_tree.item(selection[0])
        device_id = item['values'][0]
        
        if messagebox.askyesno("تایید حذف", f"آیا از حذف دستگاه {device_id} اطمینان دارید؟"):
            # متوقف کردن مانیتورینگ
            if device_id in self.zkteco_threads:
                # thread رو متوقف نمی‌کنیم چون daemon هست
                del self.zkteco_threads[device_id]
            
            if device_id in self.zkteco_status:
                del self.zkteco_status[device_id]
            
            if device_id in self.zkteco_devices:
                del self.zkteco_devices[device_id]
            
            self.save_zkteco_config()
            self.safe_update_zkteco_count()
            self.refresh_zkteco_list()
            
            messagebox.showinfo("موفق", f"دستگاه {device_id} حذف شد!")

    def test_zkteco_connection(self):
        """⭐ تست اتصال دستگاه ZKTeco انتخاب شده"""
        selection = self.zkteco_tree.selection()
        if not selection:
            messagebox.showwarning("هشدار", "لطفاً یک دستگاه را انتخاب کنید!")
            return
        
        item = self.zkteco_tree.item(selection[0])
        device_id = item['values'][0]
        device = self.zkteco_devices.get(device_id)
        
        if not device:
            messagebox.showerror("خطا", "دستگاه یافت نشد!")
            return
        
        def test_connection():
            try:
                zk = ZK(device["ip"], port=device["port"], timeout=5, password=device["password"])
                conn = zk.connect()
                
                if conn:
                    # دریافت اطلاعات دستگاه
                    firmware = conn.get_firmware_version()
                    platform = conn.get_platform()
                    device_name = conn.get_device_name()
                    device_time = conn.get_time()
                    
                    conn.disconnect()
                    
                    info = f"اتصال موفق!\n\n"
                    info += f"نام دستگاه: {device_name}\n"
                    info += f"پلتفرم: {platform}\n"
                    info += f"نسخه firmware: {firmware}\n"
                    info += f"زمان دستگاه: {device_time}"
                    
                    self.root.after(0, lambda: messagebox.showinfo("تست اتصال موفق", info))
                else:
                    self.root.after(0, lambda: messagebox.showerror("تست اتصال", "اتصال ناموفق!"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("خطای اتصال", f"خطا: {str(e)}"))
        
        threading.Thread(target=test_connection, daemon=True).start()

    def refresh_zkteco_list(self):
        """⭐ بروزرسانی لیست دستگاه‌های ZKTeco"""
        if not hasattr(self, 'zkteco_tree'):
            return
            
        # پاک کردن جدول
        for item in self.zkteco_tree.get_children():
            self.zkteco_tree.delete(item)
        
        # اضافه کردن دستگاه‌ها
        for device_id, device in self.zkteco_devices.items():
            status = self.zkteco_status.get(device_id, "نامشخص")
            last_connection = device.get("last_connection", "هرگز")
            if last_connection and last_connection != "هرگز":
                try:
                    dt = datetime.datetime.fromisoformat(last_connection)
                    last_connection = dt.strftime("%Y/%m/%d %H:%M")
                except:
                    pass
            
            values = (
                device_id,
                device.get("ip", ""),
                device.get("port", ""),
                status,
                last_connection,
                device.get("record_count", 0)
            )
            
            self.zkteco_tree.insert("", tk.END, values=values)

    def refresh_zkteco_status(self):
        """⭐ بروزرسانی وضعیت دستگاه‌های ZKTeco"""
        self.refresh_zkteco_list()
        messagebox.showinfo("بروزرسانی", "وضعیت دستگاه‌ها بروزرسانی شد!")

    def show_zkteco_status(self):
        """⭐ نمایش وضعیت تفصیلی دستگاه‌های ZKTeco"""
        status_window = tk.Toplevel(self.root)
        status_window.title("وضعیت دستگاه‌های ZKTeco")
        status_window.geometry("600x400")
        
        main_frame = ttk.Frame(status_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        status_text = scrolledtext.ScrolledText(main_frame, width=60, height=20, 
                                              font=("Consolas", 10))
        status_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        status_content = "=== وضعیت دستگاه‌های ZKTeco ===\n\n"
        
        if not self.zkteco_devices:
            status_content += "هیچ دستگاه ZKTeco تعریف نشده است.\n"
        else:
            for device_id, device in self.zkteco_devices.items():
                status_content += f"🔷 دستگاه: {device_id}\n"
                status_content += f"   IP: {device.get('ip')}\n"
                status_content += f"   Port: {device.get('port')}\n"
                status_content += f"   وضعیت: {self.zkteco_status.get(device_id, 'نامشخص')}\n"
                status_content += f"   تعداد رکورد: {device.get('record_count', 0)}\n"
                
                last_conn = device.get("last_connection")
                if last_conn:
                    try:
                        dt = datetime.datetime.fromisoformat(last_conn)
                        status_content += f"   آخرین اتصال: {dt.strftime('%Y/%m/%d %H:%M:%S')}\n"
                    except:
                        status_content += f"   آخرین اتصال: {last_conn}\n"
                else:
                    status_content += f"   آخرین اتصال: هرگز\n"
                
                status_content += "\n"
        
        status_text.insert(tk.END, status_content)
        status_text.config(state="disabled")
        
        ttk.Button(main_frame, text="بستن", command=status_window.destroy).pack(pady=10)

    def start_zkteco_monitoring(self):
        """⭐ شروع مانیتورینگ همه دستگاه‌های ZKTeco"""
        if not PYZK_AVAILABLE:
            self.safe_log_message("⚠️ کتابخانه pyzk در دسترس نیست - دستگاه‌های ZKTeco غیرفعال")
            return
        
        for device_id in self.zkteco_devices.keys():
            self.start_single_zkteco_monitor(device_id)

    def start_single_zkteco_monitor(self, device_id):
        """⭐ شروع مانیتورینگ یک دستگاه ZKTeco"""
        if device_id in self.zkteco_threads:
            return  # قبلاً در حال اجرا
        
        device = self.zkteco_devices.get(device_id)
        if not device:
            return
        
        def monitor_device():
            self.safe_log_message(f"🔄 شروع مانیتورینگ دستگاه ZKTeco {device_id}")
            last_record_count = None  # ⭐ تغییر: None تا تعداد اولیه را بگیریم
            last_sync_time = 0
            initial_setup_done = False
            
            while device_id in self.zkteco_devices:  # تا زمانی که دستگاه تعریف شده باشد
                try:
                    # ⭐ اتصال به دستگاه
                    zk = ZK(device["ip"], port=device["port"], timeout=10, password=device["password"], 
                           force_udp=False, ommit_ping=False)
                    conn = zk.connect()
                    
                    if conn:
                        self.zkteco_status[device_id] = "متصل"
                        device["last_connection"] = datetime.datetime.now().isoformat()
                        
                        # ⭐ تنظیم اولیه - گرفتن تعداد فعلی رکوردها (فقط یک بار)
                        if not initial_setup_done:
                            try:
                                self.safe_log_message(f"📊 دریافت تعداد اولیه رکوردهای دستگاه {device_id}...")
                                initial_records = conn.get_attendance()
                                last_record_count = len(initial_records) if initial_records else 0
                                device["record_count"] = last_record_count
                                self.safe_log_message(f"✅ دستگاه {device_id} آماده - رکوردهای فعلی: {last_record_count} (فقط رکوردهای جدید نمایش داده می‌شود)")
                                initial_setup_done = True
                            except Exception as init_error:
                                self.safe_log_message(f"⚠️ خطا در تنظیم اولیه {device_id}: {init_error}")
                                last_record_count = 0
                                initial_setup_done = True
                        
                        # ⭐ Time Sync هر 2 دقیقه
                        current_time = time.time()
                        if current_time - last_sync_time > 120:  # 2 دقیقه
                            try:
                                system_time = datetime.datetime.now()
                                conn.set_time(system_time)
                                self.safe_log_message(f"🕐 زمان دستگاه {device_id} همگام سازی شد")
                                last_sync_time = current_time
                            except Exception as sync_error:
                                self.safe_log_message(f"⚠️ خطا در همگام سازی زمان {device_id}: {sync_error}")
                        
                        # ⭐ بررسی رکوردهای جدید (فقط پس از تنظیم اولیه)
                        if initial_setup_done and last_record_count is not None:
                            try:
                                current_records = conn.get_attendance()
                                current_count = len(current_records) if current_records else 0
                                device["record_count"] = current_count
                                
                                # ⭐ فقط اگر رکورد جدید وجود داشته باشد
                                if current_count > last_record_count:
                                    new_records_count = current_count - last_record_count
                                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                                    self.safe_log_message(f"🔔 [{timestamp}] {new_records_count} رکورد جدید در دستگاه {device_id}")
                                    
                                    # ⭐ پردازش فقط رکوردهای جدید
                                    new_records = current_records[last_record_count:]
                                    for record in new_records:
                                        self.safe_log_message(f"🎯 پردازش رکورد جدید: کاربر {record.user_id} - زمان {record.timestamp}")
                                        self.process_zkteco_record(record, device_id, device)
                                    
                                    # ⭐ بروزرسانی شمارنده
                                    last_record_count = current_count
                                    
                            except Exception as record_error:
                                self.safe_log_message(f"❌ خطا در دریافت رکوردها از {device_id}: {record_error}")
                        
                        conn.disconnect()
                        
                    else:
                        self.zkteco_status[device_id] = "خطا در اتصال"
                        self.safe_log_message(f"❌ اتصال به دستگاه {device_id} ناموفق")
                        # در صورت مشکل اتصال، تنظیم اولیه را ریست نکنیم
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    if "timeout" in error_msg or "tcp" in error_msg or "connection" in error_msg:
                        self.zkteco_status[device_id] = "قطعی اتصال"
                        self.safe_log_message(f"⚠️ مشکل اتصال به {device_id}: {e}")
                    else:
                        self.zkteco_status[device_id] = f"خطا: {str(e)[:20]}"
                        self.safe_log_message(f"❌ خطا در مانیتورینگ {device_id}: {e}")
                
                # انتظار 5 ثانیه قبل از چک بعدی
                time.sleep(5)
            
            # تمیز کردن thread از لیست
            if device_id in self.zkteco_threads:
                del self.zkteco_threads[device_id]
        
        # شروع thread
        thread = threading.Thread(target=monitor_device, daemon=True)
        thread.start()
        self.zkteco_threads[device_id] = thread

    def restart_single_zkteco_monitor(self, device_id):
        """⭐ بازراه‌اندازی مانیتورینگ یک دستگاه ZKTeco"""
        if device_id in self.zkteco_threads:
            del self.zkteco_threads[device_id]
        
        time.sleep(1)
        self.start_single_zkteco_monitor(device_id)

    def restart_zkteco_monitoring(self):
        """⭐ بازراه‌اندازی مانیتورینگ همه دستگاه‌های ZKTeco"""
        self.safe_log_message("🔄 بازراه‌اندازی مانیتورینگ دستگاه‌های ZKTeco...")
        
        # متوقف کردن همه thread ها
        self.zkteco_threads.clear()
        
        # شروع مجدد
        time.sleep(2)
        self.start_zkteco_monitoring()

    def process_zkteco_record(self, record, device_id, device_config):
        """⭐ پردازش رکورد ZKTeco و تبدیل به فرمت استاندارد"""
        try:
            # استخراج اطلاعات از record
            user_id = str(record.user_id)
            timestamp = record.timestamp
            
            # ⭐ تشخیص AttendanceStatus بر اساس زمان روز
            attendance_status = self.determine_attendance_status(user_id, timestamp)
            
            # ⭐ VerificationMode بر اساس punch type
            verification_mode = "FP"  # همه Fingerprint طبق درخواست
            
            # تبدیل به فرمت استاندارد (مشابه کارا 200)
            event_data = {
                "DeviceUID": device_id,
                "UserID": user_id,
                "EventType": "Time Log",
                "AttendanceStatus": attendance_status,
                "VerificationMode": verification_mode,
                "Year": str(timestamp.year),
                "Month": str(timestamp.month).zfill(2),
                "Day": str(timestamp.day).zfill(2),
                "Hour": str(timestamp.hour).zfill(2),
                "Minute": str(timestamp.minute).zfill(2),
                "Second": str(timestamp.second).zfill(2),
                "device_ip": device_config.get("ip", "unknown"),
                "raw_xml": f"<ZKTeco><UserID>{user_id}</UserID><Timestamp>{timestamp}</Timestamp><Status>{record.status}</Status><Punch>{record.punch}</Punch></ZKTeco>",
                "timestamp": datetime.datetime.now().isoformat(),
                "device_type": "ZKTeco"
            }
            
            # ⭐ بررسی تکراری بودن (همان منطق کارا 200)
            if self.is_duplicate_event(event_data):
                self.ignored_count += 1
                self.safe_update_stats()
                self.safe_log_message(f"🔄 رویداد تکراری ZKTeco نادیده گرفته شد: کاربر {user_id} - {attendance_status}")
                return
            
            # ⭐ اضافه کردن به کش رویدادهای اخیر
            self.add_to_events_cache(event_data)
            
            # آپدیت شمارنده‌های آماری
            self.update_event_counters(event_data)
            
            # ذخیره در فایل JSON
            self.save_to_json(event_data)
            
            # نمایش در جدول
            self.add_to_table(event_data)
            
            # ارسال به سرور (همان تابع کارا 200)
            self.send_to_server(event_data)
            
            self.safe_log_message(f"✅ رکورد ZKTeco ثبت شد: کاربر {user_id} - {attendance_status} - دستگاه {device_id}")
            
        except Exception as e:
            self.safe_log_message(f"❌ خطا در پردازش رکورد ZKTeco: {e}")

    def determine_attendance_status(self, user_id, timestamp):
        """⭐ تشخیص وضعیت حضور بر اساس رکوردهای روزانه"""
        today = timestamp.date()
        cache_key = f"{user_id}_{today}"
        
        # بررسی کش روزانه
        if cache_key not in self.daily_events_cache:
            self.daily_events_cache[cache_key] = 0
        
        self.daily_events_cache[cache_key] += 1
        event_number = self.daily_events_cache[cache_key]
        
        # اولین رویداد = Duty On، دومین = Duty Off، سومین = Duty On و ...
        if event_number % 2 == 1:
            return "Duty On"
        else:
            return "Duty Off"

    def start_time_sync(self):
        """⭐ شروع همگام سازی زمان هر 2 دقیقه"""
        def sync_time():
            if PYZK_AVAILABLE and self.zkteco_devices:
                self.safe_log_message("🕐 شروع همگام سازی زمان دستگاه‌های ZKTeco...")
                # Time sync در هر thread دستگاه انجام می‌شود
            
            # برنامه‌ریزی برای 2 دقیقه بعد
            self.root.after(120000, sync_time)  # 120000 ms = 2 دقیقه
        
        # شروع اولین sync بعد از 10 ثانیه
        self.root.after(10000, sync_time)

    def safe_update_zkteco_count(self):
        """⭐ آپدیت تعداد دستگاه‌های ZKTeco Thread-Safe"""
        def update():
            if hasattr(self, 'zkteco_count_label'):
                count = len(self.zkteco_devices)
                self.zkteco_count_label.config(text=str(count))
        
        try:
            self.root.after(0, update)
        except:
            pass

    # ================================================
    # باقی کدها (کارا 200) - بدون تغییر
    # ================================================

    def start_udp_listener(self):
        """شروع گوش دادن به پورت UDP"""
        def listen():
            while True:
                try:
                    if self.socket:
                        self.socket.close()
                    
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    self.socket.bind((self.UDP_IP, self.UDP_PORT))
                    self.listening = True
                    
                    self.safe_log_message(f"🎧 UDP Listener راه‌اندازی شد - IP: {self.UDP_IP}:{self.UDP_PORT}")
                    self.safe_update_status("متصل - در انتظار داده", "green")
                    
                    while self.listening:
                        try:
                            self.socket.settimeout(5.0)
                            data, addr = self.socket.recvfrom(4096)
                            
                            # اضافه کردن IP دستگاه به لیست متصلین
                            if addr[0] not in self.connected_devices:
                                self.connected_devices.add(addr[0])
                                self.safe_update_device_count()
                                self.safe_log_message(f"🔗 دستگاه کارا جدید متصل شد: {addr[0]}")
                            
                            self.process_received_data(data, addr)
                            
                        except socket.timeout:
                            continue
                        except Exception as e:
                            if self.listening:
                                self.safe_log_message(f"❌ خطا در دریافت داده UDP: {e}")
                                break
                                
                except Exception as e:
                    self.safe_log_message(f"❌ خطا در راه‌اندازی UDP: {e}")
                    self.safe_update_status("خطا در اتصال UDP", "red")
                    
                finally:
                    if self.socket:
                        self.socket.close()
                    self.listening = False
                    
                    if not hasattr(self, '_stop_udp_listener'):
                        self.safe_log_message("⏳ تلاش مجدد اتصال UDP در 5 ثانیه...")
                        time.sleep(5)

        self.udp_thread = threading.Thread(target=listen, daemon=True)
        self.udp_thread.start()

    def safe_log_message(self, message):
        """⭐ لاگ Thread-Safe"""
        def log():
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_line = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, log_line)
            self.log_text.see(tk.END)
            
            # محدود کردن تعداد خطوط لاگ
            lines = self.log_text.get("1.0", tk.END).split('\n')
            if len(lines) > 500:
                self.log_text.delete("1.0", f"{len(lines)-500}.0")
        
        try:
            self.root.after(0, log)
        except:
            # اگر main loop هنوز شروع نشده، صبر کن
            pass

    def safe_update_status(self, status, color):
        """⭐ آپدیت وضعیت Thread-Safe"""
        def update():
            self.status_label.config(text=status, foreground=color)
        
        try:
            self.root.after(0, update)
        except:
            pass

    def safe_update_device_count(self):
        """⭐ آپدیت تعداد دستگاه Thread-Safe"""
        def update():
            count = len(self.connected_devices)
            self.device_count_label.config(text=str(count))
        
        try:
            self.root.after(0, update)
        except:
            pass

    def safe_update_stats(self):
        """⭐ آپدیت آمار Thread-Safe"""
        def update():
            self.entry_count_label.config(text=str(self.entry_count))
            self.exit_count_label.config(text=str(self.exit_count))
            self.ignored_count_label.config(text=str(self.ignored_count))
        
        try:
            self.root.after(0, update)
        except:
            pass

    def process_received_data(self, data, addr):
        """پردازش داده‌های دریافتی از کارا 200"""
        try:
            raw_data = data.decode('utf-8', errors='ignore')
            
            # لاگ داده خام (فقط 200 کاراکتر اول)
            preview = raw_data[:200] + "..." if len(raw_data) > 200 else raw_data
            self.safe_log_message(f"📨 دریافت از کارا {addr[0]}: {preview}")
            
            # پیدا کردن XML
            xml_start = raw_data.find('<')
            if xml_start != -1:
                xml_data = raw_data[xml_start:]
                self.parse_xml_data(xml_data, addr[0])
            else:
                self.safe_log_message(f"⚠️ داده XML معتبر یافت نشد از {addr[0]}")
                
        except Exception as e:
            self.safe_log_message(f"❌ خطا در پردازش داده از {addr[0]}: {e}")

    def parse_xml_data(self, xml_data, device_ip):
        """⭐ تجزیه داده‌های XML با فیلتر تکرار بهبود یافته"""
        try:
            event_data = {
                "timestamp": datetime.datetime.now().isoformat(),
                "device_ip": device_ip,
                "raw_xml": xml_data,
                "device_type": "Kara"
            }
            
            # استخراج فیلدها
            fields = {
                "MachineType": "نوع دستگاه",
                "MachineID": "شناسه دستگاه", 
                "DeviceUID": "UID دستگاه",
                "Year": "سال", "Month": "ماه", "Day": "روز",
                "Hour": "ساعت", "Minute": "دقیقه", "Second": "ثانیه",
                "EventType": "نوع رویداد",
                "UserID": "شناسه کاربر",
                "AttendanceStatus": "وضعیت حضور",
                "VerificationMode": "روش تایید",
                "ReasonOfFailure": "علت شکست"
            }
            
            for field, persian_name in fields.items():
                start_tag = f"<{field}>"
                end_tag = f"</{field}>"
                start_idx = xml_data.find(start_tag)
                end_idx = xml_data.find(end_tag)
                
                if start_idx != -1 and end_idx != -1:
                    value = xml_data[start_idx + len(start_tag):end_idx]
                    event_data[field] = value
            
            # ⭐ برای کارا F500: استفاده از تاریخ سیستم بجای تاریخ دستگاه
            current_time = datetime.datetime.now()
            event_data["Year"] = str(current_time.year)
            event_data["Month"] = str(current_time.month).zfill(2)
            event_data["Day"] = str(current_time.day).zfill(2)
            event_data["Hour"] = str(current_time.hour).zfill(2)
            event_data["Minute"] = str(current_time.minute).zfill(2)
            event_data["Second"] = str(current_time.second).zfill(2)

            # نرمال‌سازی و اصلاح رویداد
            self.normalize_event_data(event_data)

            # فیلتر کردن رویدادهای غیرمعتبر
            if not self.is_valid_attendance_event(event_data):
                self.ignored_count += 1
                self.safe_update_stats()
                event_type = event_data.get('EventType', 'نامشخص')
                user_id = event_data.get('UserID', 'نامشخص')
                reason = self.get_ignore_reason(event_data)
                self.safe_log_message(f"❌ رویداد کارا نادیده گرفته شد: {event_type} - کاربر: {user_id} - دلیل: {reason}")
                return

            # ⭐ بررسی تکراری بودن (این مهم‌ترین بخش است)
            if self.is_duplicate_event(event_data):
                self.ignored_count += 1
                self.safe_update_stats()
                user_id = event_data.get('UserID', 'نامشخص')
                attendance_status = self.translate_attendance_status(event_data.get('AttendanceStatus', 'نامشخص'))
                self.safe_log_message(f"🔄 رویداد تکراری کارا نادیده گرفته شد: کاربر {user_id} - {attendance_status}")
                return

            # ⭐ اضافه کردن به کش رویدادهای اخیر
            self.add_to_events_cache(event_data)

            # آپدیت شمارنده‌های آماری
            self.update_event_counters(event_data)

            # ذخیره در فایل JSON
            self.save_to_json(event_data)
            
            # نمایش در جدول
            self.add_to_table(event_data)
            
            # ارسال به سرور
            self.send_to_server(event_data)
            
            self.safe_update_status("فعال - در حال دریافت", "green")
            
        except Exception as e:
            self.safe_log_message(f"❌ خطا در تجزیه XML کارا: {e}")

    def normalize_event_data(self, event_data):
        """نرمال‌سازی و اصلاح داده‌های رویداد"""
        event_type = event_data.get("EventType", "")
        user_id = event_data.get("UserID", "")
        
        # تبدیل Verification Success به Time Log با Duty On
        if event_type == "Verification Success" and user_id and user_id != "0":
            event_data["EventType"] = "Time Log" 
            event_data["AttendanceStatus"] = "Duty On"
            self.safe_log_message(f"🔄 تبدیل Verification Success به Time Log - کاربر: {user_id}")

    def is_valid_attendance_event(self, event_data):
        """بررسی معتبر بودن رویداد حضور و غیاب"""
        event_type = event_data.get("EventType", "")
        user_id = event_data.get("UserID", "")
        attendance_status = event_data.get("AttendanceStatus", "")
        
        # نادیده گرفتن رویدادهای فیزیکی و ناموفق
        if event_type in ["Press FP", "Press Card", "Press Password", "Verification Failure"]:
            return False
            
        # بررسی UserID معتبر
        if not user_id or user_id == "0":
            return False
        
        # قبول Time Log با انواع AttendanceStatus
        if event_type == "Time Log":
            valid_statuses = [
                "Duty On", "Duty Off", "Overtime On", "Overtime Off",
                "Break Out", "Break In", "Mission Out", "Mission In"
            ]
            return attendance_status in valid_statuses
        
        # قبول Verification Success (که به Time Log تبدیل شده)
        if event_type == "Verification Success":
            return True
            
        return False

    def is_duplicate_event(self, new_event):
        """⭐ بررسی تکراری بودن رویداد - نسخه کاملاً بهبود یافته"""
        try:
            user_id = new_event.get("UserID")
            device_uid = new_event.get("DeviceUID")
            attendance_status = new_event.get("AttendanceStatus")
            device_type = new_event.get("device_type", "Kara")
            
            if not user_id or user_id == "0":
                return False
            
            # ساخت زمان رویداد جدید
            try:
                new_time = datetime.datetime(
                    int(new_event.get('Year', 0)),
                    int(new_event.get('Month', 1)),
                    int(new_event.get('Day', 1)),
                    int(new_event.get('Hour', 0)),
                    int(new_event.get('Minute', 0)),
                    int(new_event.get('Second', 0))
                )
            except:
                return False
            
            # ⭐ انتخاب کش مناسب بر اساس نوع دستگاه
            if device_type == "ZKTeco":
                cache_to_check = self.recent_events_cache_zkteco
            else:
                cache_to_check = self.recent_events_cache_kara
            
            # بررسی کش رویدادهای اخیر (سریع‌تر از خواندن فایل)
            for cached_event in reversed(cache_to_check):
                if (cached_event.get("UserID") == user_id and 
                    cached_event.get("DeviceUID") == device_uid and
                    cached_event.get("AttendanceStatus") == attendance_status):
                    
                    try:
                        cached_time = datetime.datetime(
                            int(cached_event.get('Year', 0)),
                            int(cached_event.get('Month', 1)),
                            int(cached_event.get('Day', 1)),
                            int(cached_event.get('Hour', 0)),
                            int(cached_event.get('Minute', 0)),
                            int(cached_event.get('Second', 0))
                        )
                        
                        time_diff = abs((new_time - cached_time).total_seconds())
                        
                        # ⭐ اگر در کمتر از 15 ثانیه رویداد مشابه وجود داشته باشد = تکراری
                        if time_diff < 15:
                            return True
                            
                    except:
                        continue
            
            return False
            
        except Exception as e:
            self.safe_log_message(f"❌ خطا در بررسی تکراری: {e}")
            return False

    def add_to_events_cache(self, event_data):
        """⭐ اضافه کردن رویداد به کش رویدادهای اخیر"""
        device_type = event_data.get("device_type", "Kara")
        
        # ⭐ اضافه کردن به کش مناسب بر اساس نوع دستگاه
        if device_type == "ZKTeco":
            self.recent_events_cache_zkteco.append(event_data.copy())
            # نگهداری آخرین 50 رویداد در کش ZKTeco
            if len(self.recent_events_cache_zkteco) > self.cache_size:
                self.recent_events_cache_zkteco = self.recent_events_cache_zkteco[-self.cache_size:]
        else:
            self.recent_events_cache_kara.append(event_data.copy())
            # نگهداری آخرین 50 رویداد در کش کارا
            if len(self.recent_events_cache_kara) > self.cache_size:
                self.recent_events_cache_kara = self.recent_events_cache_kara[-self.cache_size:]

    def get_ignore_reason(self, event_data):
        """تشخیص دلیل نادیده گرفتن رویداد"""
        event_type = event_data.get("EventType", "")
        user_id = event_data.get("UserID", "")
        
        if event_type == "Press FP":
            return "رویداد فیزیکی (فشار انگشت)"
        elif event_type == "Verification Failure":
            return "شناسایی ناموفق"
        elif user_id == "0" or not user_id:
            return "شناسه کاربر نامعتبر"
        elif event_type not in ["Time Log", "Verification Success"]:
            return f"نوع رویداد غیرقابل پذیرش ({event_type})"
        else:
            return "دلیل نامشخص"

    def update_event_counters(self, event_data):
        """به‌روزرسانی شمارنده‌های رویداد"""
        attendance_status = event_data.get("AttendanceStatus", "")
        
        # انواع ورودها
        if attendance_status in ["Duty On", "Overtime On"]:
            self.entry_count += 1
        # انواع خروجها
        elif attendance_status in ["Duty Off", "Overtime Off"]:
            self.exit_count += 1
            
        self.safe_update_stats()

    def save_to_json(self, event_data):
        """ذخیره داده در فایل JSON - بدون چک تکرار اضافی"""
        try:
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                data = {"events": [], "last_sync": None, "device_uid": None, "zkteco_devices": []}
            
            if not isinstance(data, dict):
                data = {"events": [], "last_sync": None, "device_uid": None, "zkteco_devices": []}
            
            if "events" not in data:
                data["events"] = []
            
            if not isinstance(data["events"], list):
                data["events"] = []
            
            # اضافه کردن زمان دقیق پردازش
            event_data['processed_time'] = datetime.datetime.now().isoformat()
            
            data["events"].append(event_data)
            
            # نگهداری آخرین 1000 رکورد
            if len(data["events"]) > 1000:
                data["events"] = data["events"][-1000:]
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.safe_log_message(f"❌ خطا در ذخیره JSON: {e}")

    def add_to_table(self, event_data):
        """افزودن رکورد به جدول"""
        def add():
            try:
                # تشکیل زمان فارسی
                if all(k in event_data for k in ["Year", "Month", "Day", "Hour", "Minute", "Second"]):
                    time_str = f"{event_data['Year']}/{event_data['Month']:0>2}/{event_data['Day']:0>2} {event_data['Hour']:0>2}:{event_data['Minute']:0>2}:{event_data['Second']:0>2}"
                else:
                    time_str = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                
                # تبدیل انواع وضعیت حضور به فارسی
                attendance = event_data.get("AttendanceStatus", "نامشخص")
                attendance_persian = self.translate_attendance_status(attendance)
                    
                # تبدیل روش تایید
                verification = event_data.get("VerificationMode", "نامشخص")
                verification_persian = self.translate_verification_mode(verification)
                
                # نوع دستگاه
                device_type = event_data.get("device_type", "نامشخص")
                device_type_persian = "کارا F500" if device_type == "Kara" else "ZKTeco"
                
                # افزودن به جدول
                values = (
                    time_str,
                    "ثبت حضور",
                    event_data.get("UserID", "نامشخص"),
                    attendance_persian,
                    verification_persian,
                    event_data.get("DeviceUID", "نامشخص"),
                    device_type_persian
                )
                
                self.tree.insert("", 0, values=values)
                
                # نگهداری آخرین 100 رکورد در جدول
                items = self.tree.get_children()
                if len(items) > 100:
                    self.tree.delete(items[-1])
                    
                # لاگ مفصل برای رویداد معتبر
                self.safe_log_message(f"✅ رویداد معتبر ثبت شد: کاربر {event_data.get('UserID')} - {attendance_persian} - {time_str} - {device_type_persian}")
                    
            except Exception as e:
                self.safe_log_message(f"❌ خطا در افزودن به جدول: {e}")
        
        try:
            self.root.after(0, add)
        except:
            pass

    def translate_attendance_status(self, status):
        """ترجمه انواع وضعیت حضور به فارسی"""
        translations = {
            "Duty On": "ورود",
            "Duty Off": "خروج", 
            "Overtime On": "شروع اضافه‌کاری",
            "Overtime Off": "پایان اضافه‌کاری",
            "Break Out": "شروع استراحت",
            "Break In": "پایان استراحت", 
            "Mission Out": "شروع ماموریت",
            "Mission In": "پایان ماموریت"
        }
        return translations.get(status, status)

    def translate_verification_mode(self, mode):
        """ترجمه روش تایید"""
        translations = {
            "FP": "اثر انگشت",
            "Face": "چهره",
            "Card": "کارت",
            "Password": "رمز عبور", 
            "Any": "هر روش"
        }
        return translations.get(mode, mode)

    def create_super_simple_signature(self, data):
        """امضای خیلی ساده - فقط 3 فیلد مهم"""
        try:
            user_id = str(data.get('UserID', ''))
            device_uid = str(data.get('DeviceUID', ''))
            attendance_status = str(data.get('AttendanceStatus', ''))
            
            signature_string = user_id + device_uid + attendance_status + self.SECRET_KEY
            signature = hashlib.sha256(signature_string.encode('utf-8')).hexdigest()
            
            return signature
            
        except Exception as e:
            self.safe_log_message(f"❌ خطا در تولید امضا: {e}")
            return ""

    def send_to_server(self, event_data):
        """ارسال داده به سرور"""
        def send():
            try:
                server_data = {
                    "DeviceUID": event_data.get("DeviceUID", "unknown"),
                    "UserID": event_data.get("UserID", "unknown"),
                    "EventType": event_data.get("EventType", "Time Log"),
                    "AttendanceStatus": event_data.get("AttendanceStatus", "unknown"),
                    "VerificationMode": event_data.get("VerificationMode", "unknown"),
                    "Year": event_data.get("Year", ""),
                    "Month": event_data.get("Month", ""),
                    "Day": event_data.get("Day", ""),
                    "Hour": event_data.get("Hour", ""),
                    "Minute": event_data.get("Minute", ""),
                    "Second": event_data.get("Second", ""),
                    "device_ip": event_data.get("device_ip", ""),
                    "raw_xml": event_data.get("raw_xml", "")
                }
                
                signature = self.create_super_simple_signature(server_data)
                
                payload = {
                    "action": "add_event",
                    "data": server_data,
                    "signature": signature
                }
                
                attendance_persian = self.translate_attendance_status(server_data['AttendanceStatus'])
                device_type = event_data.get("device_type", "نامشخص")
                device_type_persian = "کارا" if device_type == "Kara" else "ZKTeco"
                
                self.safe_log_message(f"📤 ارسال به سرور: کاربر {server_data['UserID']} - {attendance_persian} - {device_type_persian}")
                
                response = requests.post(self.SERVER_URL, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.root.after(0, lambda: self.server_status.config(text="متصل", foreground="green"))
                        self.last_connection_error = ""
                        self.safe_log_message(f"✅ ارسال موفق به سرور: کاربر {server_data['UserID']} - {device_type_persian}")
                    else:
                        error_msg = f"خطای سرور: {result.get('message', 'خطای نامشخص')}"  
                        self.last_connection_error = error_msg
                        self.add_to_pending_sync(server_data)
                        self.root.after(0, lambda: self.server_status.config(text="خطا", foreground="red"))
                        self.safe_log_message(f"❌ {error_msg}")
                else:
                    error_msg = f"خطای HTTP {response.status_code}"
                    self.last_connection_error = error_msg
                    self.add_to_pending_sync(server_data)
                    self.root.after(0, lambda: self.server_status.config(text="خطا", foreground="red"))
                    self.safe_log_message(f"❌ {error_msg}")
                    
            except requests.exceptions.ConnectionError as e:
                error_msg = f"خطای اتصال به سرور"
                self.last_connection_error = error_msg
                self.add_to_pending_sync(server_data)
                self.root.after(0, lambda: self.server_status.config(text="قطع", foreground="red"))
                self.safe_log_message(f"❌ {error_msg}")
            except Exception as e:
                error_msg = f"خطای غیرمنتظره: {str(e)}"
                self.last_connection_error = error_msg
                self.add_to_pending_sync(server_data)
                self.root.after(0, lambda: self.server_status.config(text="قطع", foreground="red"))
                self.safe_log_message(f"❌ {error_msg}")

        threading.Thread(target=send, daemon=True).start()

    def add_to_pending_sync(self, event_data):
        """افزودن به لیست انتظار سینک"""
        self.pending_sync.append(event_data)
        def update_button():
            self.sync_button.config(text=f"سینک ({len(self.pending_sync)})")
        try:
            self.root.after(0, update_button)
        except:
            pass

    def enable_udp_listener(self):
        """⭐ فعال کردن UDP Listener"""
        if not self.listening:
            self.safe_log_message("🟢 فعال کردن UDP Listener برای دستگاه‌های کارا...")
            self.start_udp_listener()
        else:
            self.safe_log_message("ℹ️ UDP Listener قبلاً فعال است")

    def disable_udp_listener(self):
        """⭐ غیرفعال کردن UDP Listener"""
        if self.listening:
            self.safe_log_message("🔴 غیرفعال کردن UDP Listener...")
            self.listening = False
            self._stop_udp_listener = True
            if self.socket:
                self.socket.close()
            self.connected_devices.clear()
            self.safe_update_device_count()
            self.safe_update_status("غیرفعال", "gray")
        else:
            self.safe_log_message("ℹ️ UDP Listener قبلاً غیرفعال است")

    def restart_udp_listener(self):
        """بازراه‌اندازی UDP Listener"""
        self.safe_log_message("🔄 بازراه‌اندازی UDP Listener...")
        self.listening = False
        if self.socket:
            self.socket.close()
        self.connected_devices.clear()
        self.safe_update_device_count()
        time.sleep(1)
        self.start_udp_listener()

    def sync_data(self):
        """سینک کردن داده‌های عقب‌افتاده"""
        if not self.pending_sync:
            messagebox.showinfo("سینک", "همه داده‌ها به‌روز هستند!")
            return
            
        def sync():
            success_count = 0
            total_count = len(self.pending_sync)
            self.safe_log_message(f"🔄 شروع سینک {total_count} رکورد با سرور...")
            
            for event_data in self.pending_sync[:]:
                try:
                    signature = self.create_super_simple_signature(event_data)
                    
                    payload = {
                        "action": "add_event",
                        "data": event_data,
                        "signature": signature
                    }
                    
                    response = requests.post(self.SERVER_URL, json=payload, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("success"):
                            self.pending_sync.remove(event_data)
                            success_count += 1
                            
                except Exception:
                    continue
            
            def update_ui():
                self.sync_button.config(text=f"سینک ({len(self.pending_sync)})")
                messagebox.showinfo("سینک", f"{success_count} از {total_count} رکورد موفق")
            
            self.root.after(0, update_ui)

        threading.Thread(target=sync, daemon=True).start()

    def test_sample_data(self):
        """تست ارسال داده نمونه"""
        def test():
            try:
                sample_data = {
                    "DeviceUID": "TEST_DEVICE_001",
                    "UserID": "123",
                    "EventType": "Time Log",
                    "AttendanceStatus": "Duty On",
                    "VerificationMode": "FP",
                    "Year": "2025",
                    "Month": "06",
                    "Day": "30",
                    "Hour": "18",
                    "Minute": "45",
                    "Second": "30",
                    "device_ip": "192.168.1.100",
                    "raw_xml": "<test>sample data</test>"
                }
                
                signature = self.create_super_simple_signature(sample_data)
                
                payload = {
                    "action": "add_event",
                    "data": sample_data,
                    "signature": signature
                }
                
                response = requests.post(self.SERVER_URL, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        self.root.after(0, lambda: messagebox.showinfo("تست موفق", "داده نمونه ارسال شد!"))
                    else:
                        self.root.after(0, lambda: messagebox.showerror("تست ناموفق", f"خطا: {result.get('message')}"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("تست ناموفق", f"HTTP Error: {response.status_code}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("خطا در تست", f"خطا: {str(e)}"))
        
        threading.Thread(target=test, daemon=True).start()

    def start_auto_server_connection(self):
        """شروع بررسی خودکار اتصال به سرور"""
        def check_connection():
            if not self.server_connection_active:
                self.server_connection_active = True
                try:
                    test_url = self.SERVER_URL.replace("api.php", "test.php")
                    response = requests.get(test_url, timeout=5)
                    if response.status_code == 200:
                        def update_status():
                            if self.server_status.cget("text") != "متصل":
                                self.server_status.config(text="متصل", foreground="green")
                        self.root.after(0, update_status)
                        self.last_connection_error = ""
                except Exception as e:
                    def update_status():
                        self.server_status.config(text="قطع", foreground="red")
                    self.root.after(0, update_status)
                    self.last_connection_error = str(e)
                finally:
                    self.server_connection_active = False
                    self.server_connection_timer = self.root.after(self.server_connection_interval * 1000, check_connection)
        
        check_connection()

    def test_server_connection(self):
        """تست اتصال سرور"""
        def test():
            try:
                test_url = self.SERVER_URL.replace("api.php", "test.php")
                response = requests.get(test_url, timeout=5)
                if response.status_code == 200:
                    self.root.after(0, lambda: messagebox.showinfo("تست اتصال", "اتصال موفق!"))
                    self.root.after(0, lambda: self.server_status.config(text="متصل", foreground="green"))
                else:
                    self.root.after(0, lambda: messagebox.showerror("تست اتصال", f"خطا: {response.status_code}"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("تست اتصال", f"خطا: {str(e)}"))

        threading.Thread(target=test, daemon=True).start()

    def show_saved_data(self):
        """نمایش داده‌های ذخیره شده"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            count = len(data.get("events", []))
            zkteco_count = len(data.get("zkteco_devices", []))
            messagebox.showinfo("داده‌های ذخیره شده", f"تعداد رکوردها: {count}\nتعداد دستگاه‌های ZKTeco: {zkteco_count}")
            
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در خواندن فایل: {e}")

    def clear_data(self):
        """پاک کردن داده‌ها"""
        if messagebox.askyesno("تایید", "آیا از پاک کردن همه داده‌ها اطمینان دارید؟"):
            try:
                with open(self.data_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "events": [], 
                        "last_sync": None, 
                        "device_uid": None,
                        "zkteco_devices": list(self.zkteco_devices.values())  # حفظ تنظیمات دستگاه‌ها
                    }, f, ensure_ascii=False, indent=2)
                
                # پاک کردن جدول
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                # ریست آمارها و کش
                self.entry_count = 0
                self.exit_count = 0
                self.ignored_count = 0
                self.recent_events_cache_kara.clear()
                self.recent_events_cache_zkteco.clear()
                self.daily_events_cache.clear()
                self.safe_update_stats()
                
                messagebox.showinfo("موفق", "داده‌ها پاک شدند! (تنظیمات دستگاه‌ها حفظ شد)")
                self.safe_log_message("🗑️ همه داده‌ها و کش پاک شدند.")
                
            except Exception as e:
                messagebox.showerror("خطا", f"خطا در پاک کردن: {e}")

    def show_connection_error(self):
        """نمایش جزئیات خطای اتصال"""
        error_content = self.last_connection_error if self.last_connection_error else "هیچ خطایی ثبت نشده است."
        messagebox.showinfo("خطای اتصال", error_content)

    def manual_connection_retry(self):
        """تلاش مجدد دستی برای اتصال"""
        self.safe_log_message("🔄 تلاش مجدد اتصال...")
        self.test_server_connection()

    def show_events_cache(self):
        """⭐ نمایش کش رویدادهای اخیر برای دیباگ"""
        cache_window = tk.Toplevel(self.root)
        cache_window.title("کش رویدادهای اخیر")
        cache_window.geometry("800x600")
        
        main_frame = ttk.Frame(cache_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        total_events = len(self.recent_events_cache_kara) + len(self.recent_events_cache_zkteco)
        ttk.Label(main_frame, text=f"کش رویدادهای اخیر ({total_events} رویداد - کارا: {len(self.recent_events_cache_kara)}, ZKTeco: {len(self.recent_events_cache_zkteco)}):", 
                 font=self.persian_font).pack(pady=(0, 10))
        
        cache_text = scrolledtext.ScrolledText(main_frame, width=80, height=25, 
                                             wrap=tk.WORD, font=("Consolas", 9))
        cache_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        cache_content = "=== کش رویدادهای اخیر ===\n\n"
        
        # نمایش رویدادهای کارا
        cache_content += f"🔷 دستگاه‌های کارا F500 ({len(self.recent_events_cache_kara)} رویداد):\n"
        for i, event in enumerate(reversed(self.recent_events_cache_kara), 1):
            cache_content += f"--- رویداد کارا #{i} ---\n"
            cache_content += f"کاربر: {event.get('UserID', 'نامشخص')}\n"
            cache_content += f"دستگاه: {event.get('DeviceUID', 'نامشخص')}\n"
            cache_content += f"وضعیت: {self.translate_attendance_status(event.get('AttendanceStatus', 'نامشخص'))}\n"
            cache_content += f"زمان: {event.get('Year')}/{event.get('Month'):0>2}/{event.get('Day'):0>2} {event.get('Hour'):0>2}:{event.get('Minute'):0>2}:{event.get('Second'):0>2}\n\n"
        
        # نمایش رویدادهای ZKTeco
        cache_content += f"\n🔷 دستگاه‌های ZKTeco ({len(self.recent_events_cache_zkteco)} رویداد):\n"
        for i, event in enumerate(reversed(self.recent_events_cache_zkteco), 1):
            cache_content += f"--- رویداد ZKTeco #{i} ---\n"
            cache_content += f"کاربر: {event.get('UserID', 'نامشخص')}\n"
            cache_content += f"دستگاه: {event.get('DeviceUID', 'نامشخص')}\n"
            cache_content += f"وضعیت: {self.translate_attendance_status(event.get('AttendanceStatus', 'نامشخص'))}\n"
            cache_content += f"زمان: {event.get('Year')}/{event.get('Month'):0>2}/{event.get('Day'):0>2} {event.get('Hour'):0>2}:{event.get('Minute'):0>2}:{event.get('Second'):0>2}\n\n"
                
        cache_text.insert(tk.END, cache_content)
        cache_text.config(state="disabled")
        
        ttk.Button(main_frame, text="بستن", command=cache_window.destroy).pack(pady=10)

    def debug_xml_data(self):
        """نمایش آخرین داده‌های XML"""
        debug_window = tk.Toplevel(self.root)
        debug_window.title("آخرین داده‌های XML")
        debug_window.geometry("800x600")
        
        main_frame = ttk.Frame(debug_window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        xml_text = scrolledtext.ScrolledText(main_frame, width=80, height=25, font=("Consolas", 9))
        xml_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            recent_events = data.get("events", [])[-5:]
            
            xml_content = "=== آخرین 5 رویداد XML ===\n\n"
            for i, event in enumerate(reversed(recent_events), 1):
                device_type = event.get("device_type", "نامشخص")
                device_type_persian = "کارا F500" if device_type == "Kara" else "ZKTeco"
                
                xml_content += f"--- رویداد {i} ({device_type_persian}) ---\n"
                xml_content += f"زمان: {event.get('timestamp', 'نامشخص')}\n"
                xml_content += f"IP: {event.get('device_ip', 'نامشخص')}\n"
                xml_content += f"XML: {event.get('raw_xml', 'موجود نیست')}\n\n"
                
            xml_text.insert(tk.END, xml_content)
            
        except Exception as e:
            xml_text.insert(tk.END, f"خطا در خواندن فایل: {e}")
            
        xml_text.config(state="disabled")
        ttk.Button(main_frame, text="بستن", command=debug_window.destroy).pack(pady=10)

    def on_closing(self):
        """رویداد بستن برنامه"""
        self.safe_log_message("🔴 در حال بستن برنامه...")
        
        # متوقف کردن UDP listener
        self.listening = False
        self._stop_udp_listener = True
        
        if self.socket:
            self.socket.close()
        
        # متوقف کردن ZKTeco monitoring
        self.zkteco_threads.clear()
        
        # متوقف کردن server connection timer
        if self.server_connection_timer:
            self.root.after_cancel(self.server_connection_timer)
            
        self.root.destroy()

    def run(self):
        """اجرای برنامه"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # پیام‌های شروع
        self.safe_log_message("🚀 سیستم حضور و غیاب - نسخه پیشرفته")
        self.safe_log_message("📡 پشتیبانی از دستگاه‌های کارا F500 و ZKTeco")
        self.safe_log_message(f"🟢 UDP Listener (کارا): {self.UDP_IP}:{self.UDP_PORT} - فعال")
        
        if PYZK_AVAILABLE:
            self.safe_log_message(f"🔌 ZKTeco: {len(self.zkteco_devices)} دستگاه تعریف شده")
            if len(self.zkteco_devices) > 0:
                self.safe_log_message("✅ مانیتورینگ ZKTeco شروع شد - فقط رکوردهای جدید نمایش داده می‌شوند")
        else:
            self.safe_log_message("⚠️ کتابخانه pyzk در دسترس نیست - دستگاه‌های ZKTeco غیرفعال")
        
        self.safe_log_message("⭐ فیلتر تکرار فعال - رویدادهای مشابه در 15 ثانیه نادیده گرفته می‌شوند")
        
        self.root.mainloop()

if __name__ == "__main__":
    app = AttendanceApp()
    app.run()