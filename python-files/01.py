Python 3.13.6 (tags/v3.13.6:4e66535, Aug  6 2025, 14:36:00) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
import hashlib
import json
import os
import shutil
import sqlite3
import barcode
import qrcode
from barcode.writer import ImageWriter
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as ReportLabImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pandas as pd
from PIL import Image as PILImage
from typing import Dict, Optional, List, Tuple, Union
import unicodedata
from getpass import getpass
import bcrypt
import re

# --------------------------
# Configuration
# --------------------------

class Config:
    """Centralized configuration"""
    FONT_NAME = 'Persian'
    FONT_FILE = 'arial.ttf'
    DATABASE_FILE = "products.db"
    USER_DB = "users.db"
    BACKUP_FOLDER = "backups"
    REPORTS_FOLDER = "reports"
    BARCODES_FOLDER = "barcodes"
    EXPORTS_FOLDER = "exports"
    IMAGES_FOLDER = "product_images"
   
    PRODUCT_TYPES = [
        "مبل", "میز نهارخوری", "کنسول", "میز tv",
        "صندلی ناهارخوری", "مبل تک", "میز وسط",
        "گل میز", "پاف", "آینه", "تخت خواب", "گل میز پاتختی"
    ]
   
    TYPE_PREFIXES = {
        'مبل': 'S', 'میز نهارخوری': 'D', 'کنسول': 'C',
        'میز tv': 'T', 'صندلی ناهارخوری': 'H', 'مبل تک': 'P',
        'میز وسط': 'M', 'گل میز': 'F', 'پاف': 'O',
        'آینه': 'R', 'تخت خواب': 'B', 'گل میز پاتختی': 'G'
    }
   
    ROLES = {
        'admin': ['create', 'read', 'update', 'delete', 'export'],
        'editor': ['create', 'read', 'update'],
        'viewer': ['read']
    }

# --------------------------
# Database Layer
# --------------------------

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_FILE)
        self._init_db()
   
    def _init_db(self):
        """Initialize database tables"""
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            name TEXT,
            type TEXT,
            images TEXT,
            specs TEXT,
            created TEXT,
            modified TEXT
        )
        """)
        self.conn.commit()
   
    def save_product(self, code: str, data: dict):
        """Save product to database"""
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO products VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            code,
            data['product_name'],
            data['product_type'],
            json.dumps(data.get('images', [])),
            json.dumps({k:v for k,v in data.items()
                      if k not in ['product_name', 'product_type', 'images',
                                 'creation_date', 'last_modified']}),
            data.get('creation_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            data.get('last_modified', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        ))
        self.conn.commit()
   
    def load_products(self) -> Dict[str, dict]:
        """Load all products from database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products")
        products = {}
        for row in cursor.fetchall():
            products[row[0]] = {
                'product_name': row[1],
                'product_type': row[2],
                'images': json.loads(row[3]),
                **json.loads(row[4]),
                'creation_date': row[5],
                'last_modified': row[6]
            }
        return products
   
    def delete_product(self, code: str):
        """Delete a product by code"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM products WHERE code = ?", (code,))
        self.conn.commit()

# --------------------------
# Authentication
# --------------------------

class AuthManager:
    def __init__(self):
        self.conn = sqlite3.connect(Config.USER_DB)
        self._init_db()
   
    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT,
            role TEXT
        )
        """)
        self.conn.commit()
   
    def register(self, username: str, password: str, role: str = "editor"):
        """Register a new user"""
        if not re.match("^[a-zA-Z0-9_]{3,20}$", username):
            raise ValueError("نام کاربری باید 3-20 حرف و فقط شامل حروف و اعداد باشد")
       
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
       
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users VALUES (?, ?, ?)",
                (username, hashed.decode(), role)
            )
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
   
    def login(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT password_hash, role FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
       
        if result and bcrypt.checkpw(password.encode(), result[0].encode()):
            return {'username': username, 'role': result[1]}
        return None

# --------------------------
# Core Functionality
# --------------------------

class ProductManager:
    def __init__(self):
        self.db = Database()
        self.auth = AuthManager()
        self.current_user = None
   
    # ----- Authentication -----
    def authenticate(self):
        while not self.current_user:
            print("\n" + "="*50)
            print("سیستم مدیریت محصولات".center(50))
            print("="*50)
            print("1. ورود\n2. ثبت نام\n3. خروج")
            choice = input("انتخاب کنید: ")
           
            if choice == "1":
                self._handle_login()
            elif choice == "2":
                self._handle_register()
            elif choice == "3":
                exit()
   
    def _handle_login(self):
        username = input("نام کاربری: ")
        password = getpass("رمز عبور: ")
        user = self.auth.login(username, password)
        if user:
            self.current_user = user
            print(f"\n✅ ورود موفقیت آمیز. نقش: {user['role']}")
        else:
            print("❌ نام کاربری یا رمز عبور نامعتبر")
   
    def _handle_register(self):
        username = input("نام کاربری جدید (3-20 حرف): ")
        password = getpass("رمز عبور جدید: ")
        if self.auth.register(username, password):
            print("✅ ثبت نام موفقیت آمیز. اکنون وارد شوید")
        else:
            print("❌ نام کاربری قبلاً استفاده شده است")
   
    # ----- Product Operations -----
    def create_product(self):
        if 'create' not in Config.ROLES.get(self.current_user['role'], []):
            print("❌ دسترسی غیرمجاز")
            return
       
        data = self._get_product_data()
        raw_code = self._generate_code(data)
        final_code = self._ensure_unique_code(raw_code)
       
        # Handle images
        if data['images']:
            data['images'] = self._save_images(data['images'], final_code)
       
        self.db.save_product(final_code, data)
        print(f"\n✅ محصول جدید با کد {final_code} ایجاد شد")
        self._generate_reports(final_code, data)
   
    def edit_product(self, code: str):
        products = self.db.load_products()
        if code not in products:
            print("❌ کد محصول نامعتبر")
            return
       
        print(f"\nویرایش محصول {code}")
        updated_data = self._get_product_data(products[code])
       
        # Handle images
        if updated_data['images'] != products[code].get('images', []):
            self._delete_images(products[code].get('images', []))
            updated_data['images'] = self._save_images(updated_data['images'], code)
       
        # Handle code change if product type changed
        if updated_data['product_type'] != products[code]['product_type']:
            new_code = self._generate_code(updated_data)
            new_code = self._ensure_unique_code(new_code)
            self.db.delete_product(code)
            code = new_code
       
        updated_data['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.save_product(code, updated_data)
        print(f"\n✅ محصول با کد {code} به‌روزرسانی شد")
        self._generate_reports(code, updated_data)
        return code
   
    # ----- Helper Methods -----
    def _generate_code(self, data: dict) -> str:
        """Generate product code from data"""
        filtered = {k:v for k,v in data.items()
                   if v and not k.startswith(('extra_info', 'images'))}
        data_str = "|".join(f"{k}:{v}" for k,v in sorted(filtered.items()))
        hash_hex = hashlib.md5(data_str.encode()).hexdigest()
       
        prefix = Config.TYPE_PREFIXES.get(data['product_type'], 'X')
        letters = prefix + "".join([c for c in hash_hex if c.isalpha()][:2]).upper()
        numbers = "".join([c for c in hash_hex if c.isdigit()][:5])
        return f"{letters.ljust(3,'X')[:3]}{numbers.ljust(5,'0')[:5]}"
   
    def _ensure_unique_code(self, code: str) -> str:
        """Ensure code uniqueness"""
        products = self.db.load_products()
        if code not in products:
            return code
       
        counter = 1
        while f"{code}_{counter}" in products:
            counter += 1
        return f"{code}_{counter}"
   
    def _save_images(self, image_paths: List[str], product_code: str) -> List[str]:
        """Save images to storage and return new paths"""
        ensure_dir(Config.IMAGES_FOLDER)
        saved_paths = []
       
        for i, path in enumerate(image_paths):
            if not os.path.exists(path):
                continue
               
            ext = os.path.splitext(path)[1].lower()
            new_path = os.path.join(Config.IMAGES_FOLDER, f"{product_code}_{i}{ext}")
           
            try:
                shutil.copy2(path, new_path)
                saved_paths.append(new_path)
            except Exception as e:
                print(f"⚠ خطا در ذخیره تصویر: {e}")
       
        return saved_paths
   
    def _delete_images(self, image_paths: List[str]):
        """Delete product images"""
        for path in image_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"⚠ خطا در حذف تصویر: {e}")

    # ----- UI Components -----
    def _get_product_data(self, existing: dict = None) -> dict:
        """Get product data through forms"""
        data = {
            'creation_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'images': []
        } if not existing else existing.copy()
       
        print("\n" + "="*50)
        print("فرم اطلاعات محصول".center(50))
        print("="*50)
       
        # Product name
        data['product_name'] = input("\n1. نام محصول: " if not existing else
                                    f"1. نام محصول (فعلی: {existing['product_name']}): ") \
                              or existing.get('product_name', '')
       
        # Product type (checkbox style)
        data['product_type'] = self._checkbox_select(
            "2. نوع محصول",
            Config.PRODUCT_TYPES,
            existing.get('product_type') if existing else None
        )
       
        # Images
        print("\n3. تصاویر محصول")
        data['images'] = self._manage_images(
            existing.get('images', []) if existing else [])
       
        # ... (other fields follow same pattern) ...
       
        if existing:
            data['last_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
       
        return data
   
    def _checkbox_select(self, title: str, options: List[str], current: str = None) -> str:
        """Checkbox-style single selection menu"""
        print(f"\n{title} (فقط یک گزینه قابل انتخاب است)")
        print("┌" + "─" * 50 + "┐")
       
        for i, option in enumerate(options, 1):
            prefix = "[✓]" if option == current else "[ ]"
            print(f"│ {prefix} {i}. {option.ljust(40)} │")
       
        print("└" + "─" * 50 + "┘")
       
        while True:
            choice = input("شماره گزینه مورد نظر را وارد کنید: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(options):
                return options[int(choice)-1]
            print("⚠ لطفاً عدد مربوط به گزینه صحیح را وارد کنید")
   
    def _manage_images(self, existing: List[str]) -> List[str]:
        """Image management interface"""
        print("\nمدیریت تصاویر محصول:")
        if existing:
            print("تصاویر فعلی:")
            for i, img in enumerate(existing, 1):
                print(f"{i}. {img}")
       
        while True:
            print("\n1. افزودن تصویر\n2. حذف تصویر\n3. اتمام")
            choice = input("انتخاب کنید: ")
           
            if choice == "3":
                break
            elif choice == "1":
                path = input("مسیر تصویر را وارد کنید: ").strip()
                if path and os.path.exists(path):
                    existing.append(path)
                else:
                    print("❌ فایل وجود ندارد")
            elif choice == "2" and existing:
                try:
                    idx = int(input("شماره تصویر برای حذف: ")) - 1
                    if 0 <= idx < len(existing):
                        existing.pop(idx)
                except ValueError:
                    print("❌ شماره نامعتبر")
       
        return existing

    # ----- Report Generation -----
    def _generate_reports(self, code: str, data: dict):
        """Generate all reports for a product"""
        ensure_dir(Config.REPORTS_FOLDER)
        ensure_dir(Config.BARCODES_FOLDER)
       
        # Generate barcode
        try:
            barcode_path = os.path.join(Config.BARCODES_FOLDER, f"barcode_{code}.png")
            barcode.get('code128', code, writer=ImageWriter()).save(barcode_path)
        except Exception as e:
            print(f"⚠ خطا در ایجاد بارکد: {e}")
       
        # Generate QR code
        try:
            qr_path = os.path.join(Config.BARCODES_FOLDER, f"qrcode_{code}.png")
            qrcode.make(code).save(qr_path)
        except Exception as e:
            print(f"⚠ خطا در ایجاد QR کد: {e}")
       
        # Generate PDF report
        try:
            self._generate_pdf_report(code, data)
        except Exception as e:
            print(f"⚠ خطا در ایجاد گزارش PDF: {e}")

    def _generate_pdf_report(self, code: str, data: dict):
        """Generate PDF report for product"""
        filename = os.path.join(Config.REPORTS_FOLDER, f"product_{code}.pdf")
       
        # Register font
        try:
            pdfmetrics.registerFont(TTFont(Config.FONT_NAME, Config.FONT_FILE))
        except:
            print("⚠ فونت فارسی یافت نشد. از فونت پیش‌فرض استفاده می‌شود")
       
        doc = SimpleDocTemplate(filename, pagesize=A4)
        story = []
       
        # Title
        title_style = ParagraphStyle(
            'Title',
            fontName=Config.FONT_NAME,
            fontSize=18,
            alignment=1
        )
        story.append(Paragraph(f"گزارش محصول - {code}", title_style))
        story.append(Spacer(1, 24))
       
        # Images
        if data.get('images'):
            for img_path in data['images']:
                if os.path.exists(img_path):
                    try:
                        img = PILImage.open(img_path)
                        width, height = img.size
                        aspect = width / height
                       
                        # Scale to fit
                        max_width = 15 * cm
                        max_height = 10 * cm
                       
                        if aspect > 1:  # Landscape
                            width = min(width, max_width)
                            height = width / aspect
                        else:  # Portrait
                            height = min(height, max_height)
                            width = height * aspect
                       
                        story.append(ReportLabImage(img_path, width=width, height=height))
                        story.append(Spacer(1, 10))
                    except Exception as e:
                        print(f"⚠ خطا در اضافه کردن تصویر: {e}")
       
        # Product details table
        table_data = []
        for key, value in data.items():
            if key in ['images', 'creation_date', 'last_modified']:
                continue
            if isinstance(value, (list, dict)):
                continue
            if not value:
                continue
               
            persian_name = {
                'product_name': 'نام محصول',
                'product_type': 'نوع محصول',
                # ... other field names ...
            }.get(key, key)
           
            table_data.append([persian_name, str(value)])
       
        table = Table(table_data, colWidths=[6*cm, 10*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4F81BD')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
            ('FONTNAME', (0,0), (-1,0), Config.FONT_NAME),
            ('FONTSIZE', (0,0), (-1,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#DBE5F1')),
            ('GRID', (0,0), (-1,-1), 1, colors.black),
        ]))
       
        story.append(table)
        doc.build(story)
        print(f"✅ گزارش PDF ایجاد شد: {filename}")
... 
... # --------------------------
... # Utilities
... # --------------------------
... 
... def ensure_dir(directory: str):
...     """Ensure directory exists"""
...     if not os.path.exists(directory):
...         os.makedirs(directory)
... 
... # --------------------------
... # Main Application
... # --------------------------
... 
... def main():
...     app = ProductManager()
...     app.authenticate()
...    
...     while app.current_user:
...         print("\n" + "="*50)
...         print("منوی اصلی".center(50))
...         print("="*50)
...         print("1. محصول جدید\n2. جستجو\n3. ویرایش\n4. حذف\n5. خروج")
...         choice = input("انتخاب کنید: ")
...        
...         if choice == "1":
...             app.create_product()
...         elif choice == "2":
...             pass  # Implement search
...         elif choice == "3":
...             code = input("کد محصول برای ویرایش: ").strip()
...             app.edit_product(code)
...         elif choice == "4":
...             pass  # Implement delete
...         elif choice == "5":
...             app.current_user = None
...             app.authenticate()
... 
... if __name__ == "__main__":
