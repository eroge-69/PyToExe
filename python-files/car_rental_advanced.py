import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import smtplib
from email.mime.text import MIMEText
import schedule
import time
import threading
from PIL import Image, ImageTk
import os
import shutil
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle

# إنشاء قاعدة البيانات
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('car_rental_advanced.db')
        self.cursor = self.conn.cursor()
        self.create_tables()
        
    def create_tables(self):
        # جدول السيارات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                car_id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL,
                model TEXT NOT NULL,
                year INTEGER,
                plate_number TEXT UNIQUE NOT NULL,
                daily_rate REAL NOT NULL,
                status TEXT DEFAULT 'available',
                last_maintenance DATE,
                next_maintenance DATE,
                mileage INTEGER
            )
        ''')
        
        # جدول العملاء
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                id_number TEXT UNIQUE,
                loyalty_points INTEGER DEFAULT 0
            )
        ''')
        
        # جدول التأجيرات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS rentals (
                rental_id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                customer_id INTEGER NOT NULL,
                start_date DATE NOT NULL,
                end_date DATE NOT NULL,
                actual_return_date DATE,
                total_cost REAL,
                deposit REAL,
                payment_status TEXT DEFAULT 'unpaid',
                FOREIGN KEY (car_id) REFERENCES cars (car_id),
                FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
            )
        ''')
        
        # جدول المدفوعات
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rental_id INTEGER NOT NULL,
                payment_date DATE NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                FOREIGN KEY (rental_id) REFERENCES rentals (rental_id)
            )
        ''')
        
        # جدول الصيانة
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS maintenance (
                maintenance_id INTEGER PRIMARY KEY AUTOINCREMENT,
                car_id INTEGER NOT NULL,
                maintenance_type TEXT NOT NULL,
                maintenance_date DATE NOT NULL,
                next_maintenance_date DATE NOT NULL,
                cost REAL NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'completed',
                FOREIGN KEY (car_id) REFERENCES cars (car_id)
        ''')
        
        # جدول الفواتير
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                invoice_id INTEGER PRIMARY KEY AUTOINCREMENT,
                rental_id INTEGER NOT NULL,
                invoice_date DATE NOT NULL,
                total_amount REAL NOT NULL,
                tax_amount REAL NOT NULL,
                discount_amount REAL DEFAULT 0,
                final_amount REAL NOT NULL,
                status TEXT DEFAULT 'unpaid',
                FOREIGN KEY (rental_id) REFERENCES rentals (rental_id)
        ''')
        
        self.conn.commit()

# نظام الإشعارات
class NotificationSystem:
    def __init__(self, db):
        self.db = db
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.email = "your_email@gmail.com"
        self.password = "your_password"
        
    def send_email(self, to_email, subject, body):
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.email
            msg['To'] = to_email
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def send_sms(self, phone, message):
        # يمكن استبدال هذا بواجهة برمجة تطبيقات SMS حقيقية
        print(f"SMS to {phone}: {message}")
        return True
    
    def check_due_returns(self):
        self.db.cursor.execute('''
            SELECT r.rental_id, c.name, c.email, c.phone, 
                   car.make, car.model, r.end_date
            FROM rentals r
            JOIN customers c ON r.customer_id = c.customer_id
            JOIN cars car ON r.car_id = car.car_id
            WHERE r.actual_return_date IS NULL 
            AND r.end_date BETWEEN date('now') AND date('now', '+2 days')
        ''')
        rentals = self.db.cursor.fetchall()
        
        for rental in rentals:
            rental_id, name, email, phone, make, model, end_date = rental
            days_left = (datetime.strptime(end_date, '%Y-%m-%d') - datetime.now()).days
            
            message = f"عزيزي {name}، "
            if days_left == 0:
                message += f"اليوم هو موعد إرجاع السيارة {make} {model}. يرجى الإرجاع في الوقت المحدد لتجنب رسوم التأخير."
            else:
                message += f"يتبقى {days_left} يوم حتى موعد إرجاع السيارة {make} {model}."
            
            # إرسال البريد الإلكتروني
            if email:
                self.send_email(email, "تذكير إرجاع السيارة", message)
            
            # إرسال SMS
            if phone:
                self.send_sms(phone, message)
    
    def check_maintenance(self):
        self.db.cursor.execute('''
            SELECT c.car_id, c.make, c.model, c.plate_number, 
                   c.next_maintenance_date, e.email
            FROM cars c
            LEFT JOIN employees e ON 1=1  # في الواقع، يجب ربطها بالموظف المسؤول
            WHERE c.next_maintenance_date BETWEEN date('now') AND date('now', '+7 days')
        ''')
        cars = self.db.cursor.fetchall()
        
        for car in cars:
            car_id, make, model, plate, next_date, email = car
            days_left = (datetime.strptime(next_date, '%Y-%m-%d') - datetime.now()).days
            
            message = f"تنبيه: السيارة {make} {model} ({plate}) تحتاج صيانة خلال {days_left} يوم. تاريخ الصيانة: {next_date}"
            
            # إرسال إشعار للموظف المسؤول
            if email:
                self.send_email(email, "تذكير صيانة السيارة", message)

# نظام النسخ الاحتياطي
class BackupSystem:
    @staticmethod
    def create_backup():
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"car_rental_backup_{timestamp}.db")
        
        try:
            shutil.copy2('car_rental_advanced.db', backup_file)
            return True, backup_file
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def restore_backup(backup_file):
        try:
            shutil.copy2(backup_file, 'car_rental_advanced.db')
            return True
        except Exception as e:
            return False, str(e)

# نظام الفواتير
class InvoiceSystem:
    def __init__(self, db):
        self.db = db
    
    def generate_invoice(self, rental_id):
        # الحصول على بيانات التأجير
        self.db.cursor.execute('''
            SELECT r.rental_id, r.start_date, r.end_date, r.total_cost, r.deposit,
                   c.name, c.phone, c.email,
                   car.make, car.model, car.plate_number
            FROM rentals r
            JOIN customers c ON r.customer_id = c.customer_id
            JOIN cars car ON r.car_id = car.car_id
            WHERE r.rental_id = ?
        ''', (rental_id,))
        rental = self.db.cursor.fetchone()
        
        if not rental:
            return False, "التأجير غير موجود"
        
        # حساب الضريبة والخصومات
        tax_rate = 0.15  # 15% ضريبة
        tax_amount = rental[3] * tax_rate
        discount = 0  # يمكن حساب الخصم بناء على نقاط الولاء أو العروض
        
        # المبلغ النهائي
        final_amount = rental[3] + tax_amount - discount - rental[4]
        
        # إدخال الفاتورة في قاعدة البيانات
        invoice_date = datetime.now().strftime('%Y-%m-%d')
        self.db.cursor.execute('''
            INSERT INTO invoices (rental_id, invoice_date, total_amount, 
                                tax_amount, discount_amount, final_amount)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (rental_id, invoice_date, rental[3], tax_amount, discount, final_amount))
        
        invoice_id = self.db.cursor.lastrowid
        self.db.conn.commit()
        
        # إنشاء ملف PDF للفاتورة
        self.generate_invoice_pdf(invoice_id, rental, tax_amount, discount, final_amount)
        
        return True, invoice_id
    
    def generate_invoice_pdf(self, invoice_id, rental_data, tax_amount, discount, final_amount):
        filename = f"Invoice_{invoice_id}.pdf"
        c = canvas.Canvas(filename, pagesize=letter)
        
        # عنوان الفاتورة
        c.setFont("Helvetica-Bold", 16)
        c.drawString(250, 750, "فاتورة تأجير سيارة")
        
        # معلومات الشركة
        c.setFont("Helvetica", 10)
        c.drawString(50, 730, "شركة تأجير السيارات المتميزة")
        c.drawString(50, 715, "العنوان: الرياض، المملكة العربية السعودية")
        c.drawString(50, 700, "الهاتف: 0112345678")
        
        # معلومات العميل
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 670, "معلومات العميل:")
        c.setFont("Helvetica", 10)
        c.drawString(50, 655, f"الاسم: {rental_data[5]}")
        c.drawString(50, 640, f"الهاتف: {rental_data[6]}")
        
        # معلومات الفاتورة
        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, 670, "معلومات الفاتورة:")
        c.setFont("Helvetica", 10)
        c.drawString(350, 655, f"رقم الفاتورة: {invoice_id}")
        c.drawString(350, 640, f"تاريخ الفاتورة: {datetime.now().strftime('%Y-%m-%d')}")
        
        # معلومات التأجير
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, 610, "معلومات التأجير:")
        c.setFont("Helvetica", 10)
        c.drawString(50, 595, f"السيارة: {rental_data[8]} {rental_data[9]} ({rental_data[10]})")
        c.drawString(50, 580, f"فترة التأجير: من {rental_data[1]} إلى {rental_data[2]}")
        
        # جدول تفاصيل الفاتورة
        data = [
            ["الوصف", "المبلغ"],
            ["إيجار السيارة", f"{rental_data[3]:.2f}"],
            ["الضريبة (15%)", f"{tax_amount:.2f}"],
            ["الخصم", f"-{discount:.2f}"],
            ["العربون", f"-{rental_data[4]:.2f}"],
            ["المبلغ المستحق", f"{final_amount:.2f}"]
        ]
        
        table = Table(data, colWidths=[300, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
        ]))
        
        table.wrapOn(c, 50, 500)
        table.drawOn(c, 50, 500)
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        c.drawString(50, 50, "شكراً لاختياركم شركتنا. نرجو معاودة الاتصال بنا لاحتياجاتكم المستقبلية.")
        
        c.save()
        return filename

# الواجهة الرسومية
class RentalApp(tk.Tk):
    def __init__(self, db, notification_system, invoice_system):
        super().__init__()
        self.db = db
        self.notification_system = notification_system
        self.invoice_system = invoice_system
        
        self.title("نظام إدارة تأجير السيارات المتكامل")
        self.geometry("1200x800")
        self.configure(bg="#f0f0f0")
        
        self.create_widgets()
        self.setup_scheduler()
    
    def create_widgets(self):
        # شريط القوائم
        menubar = tk.Menu(self)
        
        # قوائم النظام
        system_menu = tk.Menu(menubar, tearoff=0)
        system_menu.add_command(label="إنشاء نسخة احتياطية", command=self.create_backup)
        system_menu.add_command(label="استعادة نسخة احتياطية", command=self.restore_backup)
        system_menu.add_separator()
        system_menu.add_command(label="خروج", command=self.quit)
        menubar.add_cascade(label="النظام", menu=system_menu)
        
        # قوائم التقارير
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="تقرير الإيرادات", command=self.show_revenue_report)
        reports_menu.add_command(label="تقرير السيارات", command=self.show_cars_report)
        reports_menu.add_command(label="تقرير العملاء", command=self.show_customers_report)
        menubar.add_cascade(label="التقارير", menu=reports_menu)
        
        self.config(menu=menubar)
        
        # دفتر الملاحظات (Notebook)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # إنشاء تبويبات النظام
        self.create_dashboard_tab()
        self.create_cars_tab()
        self.create_customers_tab()
        self.create_rentals_tab()
        self.create_maintenance_tab()
        self.create_invoices_tab()
    
    def create_dashboard_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="اللوحة الرئيسية")
        
        # إحصائيات سريعة
        stats_frame = ttk.LabelFrame(tab, text="إحصائيات سريعة")
        stats_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # الحصول على البيانات للإحصائيات
        available_cars = self.db.cursor.execute("SELECT COUNT(*) FROM cars WHERE status='available'").fetchone()[0]
        rented_cars = self.db.cursor.execute("SELECT COUNT(*) FROM cars WHERE status='rented'").fetchone()[0]
        maintenance_cars = self.db.cursor.execute("SELECT COUNT(*) FROM cars WHERE status='maintenance'").fetchone()[0]
        active_rentals = self.db.cursor.execute("SELECT COUNT(*) FROM rentals WHERE actual_return_date IS NULL").fetchone()[0]
        
        ttk.Label(stats_frame, text=f"السيارات المتاحة: {available_cars}").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, text=f"السيارات المؤجرة: {rented_cars}").grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, text=f"السيارات في الصيانة: {maintenance_cars}").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        ttk.Label(stats_frame, text=f"التأجيرات النشطة: {active_rentals}").grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)
        
        # رسم بياني للإيرادات
        self.plot_revenue_chart(tab)
    
    def plot_revenue_chart(self, parent):
        # الحصول على بيانات الإيرادات الشهرية
        self.db.cursor.execute('''
            SELECT strftime('%Y-%m', payment_date) AS month, 
                   SUM(amount) AS total
            FROM payments
            GROUP BY strftime('%Y-%m', payment_date)
            ORDER BY month DESC
            LIMIT 6
        ''')
        revenue_data = self.db.cursor.fetchall()
        
        if revenue_data:
            months = [row[0] for row in revenue_data]
            amounts = [row[1] for row in revenue_data]
            
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(months, amounts, color='skyblue')
            ax.set_title('الإيرادات الشهرية')
            ax.set_ylabel('المبلغ')
            
            chart_frame = ttk.Frame(parent)
            chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            canvas = FigureCanvasTkAgg(fig, master=chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def create_cars_tab(self):
        # ... (كود إدارة السيارات)
        pass
    
    def create_customers_tab(self):
        # ... (كود إدارة العملاء)
        pass
    
    def create_rentals_tab(self):
        # ... (كود إدارة التأجيرات)
        pass
    
    def create_maintenance_tab(self):
        # ... (كود إدارة الصيانة)
        pass
    
    def create_invoices_tab(self):
        # ... (كود إدارة الفواتير)
        pass
    
    def setup_scheduler(self):
        # جدولة المهام الخلفية
        schedule.every().day.at("09:00").do(self.notification_system.check_due_returns)
        schedule.every().day.at("09:00").do(self.notification_system.check_maintenance)
        schedule.every().sunday.at("10:00").do(BackupSystem.create_backup)
        
        # تشغيل المجدول في خيط منفصل
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def create_backup(self):
        success, result = BackupSystem.create_backup()
        if success:
            messagebox.showinfo("نجاح", f"تم إنشاء نسخة احتياطية بنجاح في: {result}")
        else:
            messagebox.showerror("خطأ", f"فشل في إنشاء النسخة الاحتياطية: {result}")
    
    def restore_backup(self):
        backup_file = filedialog.askopenfilename(title="اختر ملف النسخة الاحتياطية", 
                                              filetypes=[("Database files", "*.db")])
        if backup_file:
            success, result = BackupSystem.restore_backup(backup_file)
            if success:
                messagebox.showinfo("نجاح", "تم استعادة النسخة الاحتياطية بنجاح")
                # إعادة تحميل البيانات
                self.refresh_all_tabs()
            else:
                messagebox.showerror("خطأ", f"فشل في استعادة النسخة الاحتياطية: {result}")
    
    def show_revenue_report(self):
        # ... (كود تقرير الإيرادات)
        pass
    
    def show_cars_report(self):
        # ... (كود تقرير السيارات)
        pass
    
    def show_customers_report(self):
        # ... (كود تقرير العملاء)
        pass
    
    def refresh_all_tabs(self):
        # ... (كود تحديث جميع التبويبات)
        pass

# تشغيل التطبيق
if __name__ == "__main__":
    db = Database()
    notification_system = NotificationSystem(db)
    invoice_system = InvoiceSystem(db)
    
    app = RentalApp(db, notification_system, invoice_system)
    app.mainloop()