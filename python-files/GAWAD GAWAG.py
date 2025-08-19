import os
import sys
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import datetime as dt
import csv
import shutil
import json
import subprocess
import hashlib
import tempfile
from pathlib import Path

# حل مشكلة Hack Configuration في VS Code
os.environ["PYDEVD_DISABLE_FILE_VALIDATION"] = "1"

# تحديد المسار الصحيح للموارد
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# تحسين الأداء للأجهزة الضعيفة - استخدام tkinter العادي
try:
    import tkinter.ttk as ttk
    THEME = None
except ImportError:
    import tkinter as tk
    ttk = tk
    THEME = None

# تحسين الأداء للأجهزة الضعيفة - إزالة المكتبات الثقيلة
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    REPORTLAB = True
except ImportError:
    REPORTLAB = False

# تحسين الأداء للأجهزة الضعيفة - استخدام معالجة بسيطة للنص العربي
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    # دالة بديلة بسيطة لمعالجة النص العربي
    def get_display(text):
        # معالجة بسيطة للنص العربي - عكس ترتيب الحروف
        if not text:
            return text
        # تقسيم النص إلى كلمات وعكس ترتيبها
        words = text.split()
        return ' '.join(reversed(words))

# مسار قاعدة البيانات
DB = os.path.join(BASE_DIR, "store.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(BACKUP_DIR, exist_ok=True)

APP_TITLE = "نظام المخزن والفواتير - للأجهزة الضعيفة"
DEFAULT_ADMIN_PASSWORD = hashlib.md5("1234".encode()).hexdigest()
DEFAULT_EDIT_PASSWORD = hashlib.md5("1234".encode()).hexdigest()

# تحسين الأداء للأجهزة الضعيفة - تقليل حجم النوافذ
WINDOW_WIDTH = 1000  # تقليل من 1200
WINDOW_HEIGHT = 600  # تقليل من 800
TREE_HEIGHT = 12     # تقليل من 18

def get_conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    # تحسين الأداء للأجهزة الضعيفة
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=NORMAL")
    c.execute("PRAGMA cache_size=1000")
    c.execute("PRAGMA temp_store=MEMORY")
    return c

def table_columns(table):
    c = get_conn(); cur = c.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    rows = cur.fetchall(); c.close()
    return [r["name"] for r in rows]

def ensure_tables_and_columns():
    c = get_conn(); cur = c.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        thickness TEXT,
        price REAL DEFAULT 0,
        quantity INTEGER DEFAULT 0
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        phone TEXT,
        balance REAL DEFAULT 0
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        created_at TEXT,
        subtotal REAL,
        paid REAL,
        invoice_number TEXT UNIQUE,
        notes TEXT,
        discount REAL DEFAULT 0  -- إضافة حقل الخصم
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        product_id INTEGER,
        product_code TEXT,
        thickness TEXT,
        qty REAL,
        unit_price REAL,
        cutting_price REAL,
        edge_price REAL,
        line_total REAL,
        cost_per_unit REAL,
        line_cost REAL,
        description TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        action TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_password TEXT,
        edit_password TEXT,
        login_required INTEGER DEFAULT 0,
        company_name TEXT,
        company_address TEXT,
        company_phone TEXT,
        default_cutting_price REAL DEFAULT 0,
        default_edge_price REAL DEFAULT 0,
        invoice_prefix TEXT DEFAULT 'INV'
    )""")
    # إضافة جدول الرسوم
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        amount REAL,
        category TEXT,
        description TEXT
    )""")
    # إضافة جدول الكاش
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cash (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        amount REAL,
        description TEXT
    )""")
    c.commit()
    # Ensure missing columns in settings for backward compatibility
    try:
        settings_cols = table_columns("settings")
        settings_extras = [
            ("company_name", "TEXT"),
            ("company_address", "TEXT"),
            ("company_phone", "TEXT"),
            ("default_cutting_price", "REAL DEFAULT 0"),
            ("default_edge_price", "REAL DEFAULT 0"),
            ("invoice_prefix", "TEXT DEFAULT 'INV'")
        ]
        for col, ddl in settings_extras:
            if col not in settings_cols:
                try:
                    cur.execute(f"ALTER TABLE settings ADD COLUMN {col} {ddl}")
                    c.commit()
                except Exception:
                    pass
    except Exception:
        pass
    # Initialize settings if not exists
    cur.execute("SELECT COUNT(*) as cnt FROM settings")
    if cur.fetchone()["cnt"] == 0:
        cur.execute("INSERT INTO settings (admin_password, edit_password, company_name, company_address, company_phone) VALUES (?, ?, ?, ?, ?)", 
                   (DEFAULT_ADMIN_PASSWORD, DEFAULT_EDIT_PASSWORD, "شركتي", "عنوان الشركة", "0123456789"))
        c.commit()
    prod_cols = table_columns("products")
    extras = [
        ("cost", "REAL DEFAULT 0"),
        ("type", "TEXT"),
        ("edge_length", "REAL"),
        ("low_stock_threshold", "INTEGER DEFAULT 1"),
        ("created_at", "TEXT"),
        ("description", "TEXT")
    ]
    for col, ddl in extras:
        if col not in prod_cols:
            try:
                cur.execute(f"ALTER TABLE products ADD COLUMN {col} {ddl}")
                c.commit()
            except Exception:
                pass
    inv_cols = table_columns("invoice_items")
    inv_extras = [("cost_per_unit", "REAL DEFAULT 0"), ("line_cost", "REAL DEFAULT 0"), ("description", "TEXT")]
    for col, ddl in inv_extras:
        if col not in inv_cols:
            try:
                cur.execute(f"ALTER TABLE invoice_items ADD COLUMN {col} {ddl}")
                c.commit()
            except Exception:
                pass
    # Add missing columns for invoices table
    invoices_cols = table_columns("invoices")
    invoices_extras = [
        ("invoice_number", "TEXT"),
        ("notes", "TEXT"),
        ("discount", "REAL DEFAULT 0")  # تأكيد إضافة حقل الخصم
    ]
    for col, ddl in invoices_extras:
        if col not in invoices_cols:
            try:
                cur.execute(f"ALTER TABLE invoices ADD COLUMN {col} {ddl}")
                c.commit()
            except Exception:
                pass
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_code_thickness ON products(code, thickness)")
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_invoice_number ON invoices(invoice_number)")
    c.commit(); c.close()

def log_action(action):
    c = get_conn(); cur = c.cursor()
    cur.execute("INSERT INTO activity_log (created_at, action) VALUES (?, ?)", (datetime.now(dt.UTC).isoformat(), action))
    c.commit(); c.close()

def add_product_db(code, thickness, price, cost, qty, ptype, edge_length, low_stock=1, description=""):
    c = get_conn(); cur = c.cursor()
    
    # التحقق من وجود المنتج بنفس الكود والسمك
    if thickness is None or str(thickness).strip() == "":
        cur.execute("SELECT id FROM products WHERE code=? AND (thickness IS NULL OR thickness='')", (code,))
    else:
        cur.execute("SELECT id FROM products WHERE code=? AND thickness=?", (code, thickness))
    
    existing = cur.fetchone()
    if existing:
        c.close()
        raise ValueError("هذا الكود مع السمك موجود بالفعل!")
    
    cur.execute("""
        INSERT INTO products (code, thickness, price, cost, quantity, type, edge_length, low_stock_threshold, created_at, description)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (code, thickness, price, cost, qty, ptype, edge_length, low_stock, datetime.now(dt.UTC).isoformat(), description))
    c.commit(); c.close()
    log_action(f"أضف منتج: {code}")

def update_product_db(pid, code, thickness, price, cost, qty, ptype, edge_length, low_stock, description=""):
    c = get_conn(); cur = c.cursor()
    
    # التحقق من وجود منتج آخر بنفس الكود والسمك
    cur.execute("SELECT code, thickness FROM products WHERE id=?", (pid,))
    current = cur.fetchone()
    current_code = current["code"]
    current_thickness = current["thickness"] or ""
    
    # إذا تغير الكود أو السمك، تحقق من وجود تكرار
    if code != current_code or thickness != current_thickness:
        if thickness is None or str(thickness).strip() == "":
            cur.execute("SELECT id FROM products WHERE code=? AND (thickness IS NULL OR thickness='') AND id!=?", (code, pid))
        else:
            cur.execute("SELECT id FROM products WHERE code=? AND thickness=? AND id!=?", (code, thickness, pid))
        
        if cur.fetchone():
            c.close()
            raise ValueError("هذا الكود مع السمك موجود بالفعل!")
    
    cur.execute("""
        UPDATE products SET code=?, thickness=?, price=?, cost=?, quantity=?, type=?, edge_length=?, low_stock_threshold=?, description=?
        WHERE id=?
    """, (code, thickness, price, cost, qty, ptype, edge_length, low_stock, description, pid))
    c.commit(); c.close()
    log_action(f"تعديل منتج ID={pid}")

def delete_product_db(pid):
    c = get_conn(); cur = c.cursor()
    cur.execute("DELETE FROM products WHERE id=?", (pid,))
    c.commit(); c.close()
    log_action(f"حذف منتج ID={pid}")

def search_products(keyword=None):
    c = get_conn(); cur = c.cursor()
    if keyword:
        q = f"%{keyword}%"
        cur.execute("SELECT * FROM products WHERE code LIKE ? OR thickness LIKE ? OR description LIKE ? ORDER BY code", (q, q, q))
    else:
        cur.execute("SELECT * FROM products ORDER BY code")
    rows = cur.fetchall(); c.close()
    return rows

def get_product_by_code_and_thickness(code, thickness):
    c = get_conn(); cur = c.cursor()
    # اعتبر السمك الفارغ مكافئًا لـ NULL في قاعدة البيانات
    if thickness is None or str(thickness).strip() == "":
        cur.execute(
            "SELECT * FROM products WHERE code=? AND (thickness IS NULL OR thickness='')",
            (code,)
        )
    else:
        cur.execute("SELECT * FROM products WHERE code=? AND thickness=?", (code, thickness))
    r = cur.fetchone(); c.close(); return r

def get_product_by_code(code):
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT * FROM products WHERE code=?", (code,))
    r = cur.fetchall(); c.close(); return r

def get_customer_by_name(name):
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT * FROM customers WHERE name=?", (name,))
    r = cur.fetchone(); c.close(); return r

def upsert_customer(name, phone):
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT id FROM customers WHERE name=?", (name,))
    r = cur.fetchone()
    if r:
        cur.execute("UPDATE customers SET phone=? WHERE id=?", (phone, r["id"]))
        cid = r["id"]
    else:
        cur.execute("INSERT INTO customers (name, phone, balance) VALUES (?, ?, ?)", (name, phone, 0.0))
        cid = cur.lastrowid
    c.commit(); c.close()
    log_action(f"إنشاء/تحديث عميل: {name}")
    return cid

def generate_invoice_number():
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT invoice_prefix FROM settings LIMIT 1")
    prefix = cur.fetchone()["invoice_prefix"] or "INV"
    cur.execute("SELECT MAX(CAST(substr(invoice_number, length(?) + 1) AS INTEGER)) FROM invoices WHERE invoice_number LIKE ? || '%'", 
               (prefix, prefix))
    last_num = cur.fetchone()[0] or 0
    c.close()
    return f"{prefix}{last_num + 1:04d}"

def create_invoice_db(customer_name, phone, items, paid, invoice_date, notes="", discount=0.0):
    cid = upsert_customer(customer_name, phone)
    subtotal = sum(it["line_total"] for it in items)
    # تطبيق الخصم على الإجمالي
    subtotal_after_discount = max(0, subtotal - discount)
    invoice_number = generate_invoice_number()
    
    c = get_conn(); cur = c.cursor()
    cur.execute("""
        INSERT INTO invoices (customer_id, created_at, subtotal, paid, invoice_number, notes, discount)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (cid, invoice_date, subtotal_after_discount, paid, invoice_number, notes, discount))
    inv_id = cur.lastrowid
    
    for it in items:
        # دعم المنتجات ذات السمك الفارغ (NULL/"")
        th_val = it.get("thickness")
        if th_val is None or str(th_val).strip() == "":
            cur.execute(
                "SELECT id, quantity, cost, type, edge_length FROM products WHERE code=? AND (thickness IS NULL OR thickness='')",
                (it["code"],)
            )
        else:
            cur.execute("SELECT id, quantity, cost, type, edge_length FROM products WHERE code=? AND thickness=?", (it["code"], it["thickness"]))
        prod = cur.fetchone()
        prod_id = prod["id"] if prod else None
        prod_cost = prod["cost"] if prod and prod["cost"] is not None else 0.0
        if prod:
            if (prod["type"] or "") == "شريط الحرف":
                # خصم الطول بالمتر من المخزون لشريط الحرف
                try:
                    length_sold = float(it.get("qty", 0) or 0)
                except Exception:
                    length_sold = 0.0
                current_len = float((prod["edge_length"] if "edge_length" in prod.keys() else 0.0) or 0.0)
                new_len = max(0.0, current_len - length_sold)
                cur.execute("UPDATE products SET edge_length=? WHERE id=?", (new_len, prod_id))
            else:
                # خصم عدد الوحدات للمنتجات العادية
                try:
                    qty_number = int(round(float(it.get("qty", 0))))
                    if qty_number < 0:
                        qty_number = 0
                except Exception:
                    qty_number = 0
                new_qty = max(0, int(prod["quantity"] or 0) - qty_number)
                cur.execute("UPDATE products SET quantity=? WHERE id=?", (new_qty, prod_id))
        line_cost = prod_cost * (it["qty"] if not it.get("is_edge_strip") else it.get("qty", 0))
        cur.execute("""INSERT INTO invoice_items
                       (invoice_id, product_id, product_code, thickness, qty, unit_price, cutting_price, edge_price, 
                       line_total, cost_per_unit, line_cost, description)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (inv_id, prod_id, it["code"], it["thickness"], it["qty"], it.get("unit_price",0.0), 
                     it.get("cutting_price",0.0), it.get("edge_price",0.0), it["line_total"], 
                     prod_cost, line_cost, it.get("description", "")))
    
    cur.execute("SELECT balance FROM customers WHERE id=?", (cid,))
    old_bal = cur.fetchone()["balance"]
    new_bal = old_bal + paid - subtotal_after_discount
    cur.execute("UPDATE customers SET balance=? WHERE id=?", (new_bal, cid))
    c.commit(); c.close()
    log_action(f"إنشاء فاتورة ID={inv_id} رقم {invoice_number} لعميل {customer_name} إجمالي={subtotal_after_discount} مدفوع={paid} خصم={discount}")
    return inv_id, old_bal, new_bal, invoice_number

def cancel_invoice_db(invoice_id):
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT customer_id, subtotal, paid, discount FROM invoices WHERE id=?", (invoice_id,))
    inv = cur.fetchone()
    if not inv:
        c.close()
        raise ValueError("الفاتورة غير موجودة!")
    cur.execute("SELECT product_id, qty, thickness FROM invoice_items WHERE invoice_id=?", (invoice_id,))
    items = cur.fetchall()
    for item in items:
        if item["product_id"]:
            cur.execute("SELECT quantity, type, edge_length FROM products WHERE id=?", (item["product_id"],))
            prod = cur.fetchone()
            if prod:
                if (prod["type"] or "") == "شريط الحرف":
                    # استرجاع الطول بالمتر
                    try:
                        length_return = float(item["qty"] or 0)
                    except Exception:
                        length_return = 0.0
                    current_len = float(prod["edge_length"] or 0.0)
                    cur.execute("UPDATE products SET edge_length=? WHERE id=?", (current_len + length_return, item["product_id"]))
                else:
                    new_qty = int(prod["quantity"] or 0) + int(float(item["qty"]))
                    cur.execute("UPDATE products SET quantity=? WHERE id=?", (new_qty, item["product_id"]))
    cur.execute("SELECT balance FROM customers WHERE id=?", (inv["customer_id"],))
    old_bal = cur.fetchone()["balance"]
    new_bal = old_bal + inv["subtotal"] - inv["paid"]
    cur.execute("UPDATE customers SET balance=? WHERE id=?", (new_bal, inv["customer_id"]))
    cur.execute("DELETE FROM invoice_items WHERE invoice_id=?", (invoice_id,))
    cur.execute("DELETE FROM invoices WHERE id=?", (invoice_id,))
    c.commit(); c.close()
    log_action(f"إلغاء فاتورة ID={invoice_id}")

def get_invoices(limit=50, start_date=None, end_date=None, invoice_number=None, customer_name=None):
    c = get_conn(); cur = c.cursor()
    query = """SELECT invoices.*, customers.name AS customer_name, customers.phone, customers.balance 
               FROM invoices LEFT JOIN customers ON invoices.customer_id=customers.id"""
    params = []
    
    conditions = []
    if start_date and end_date:
        conditions.append("invoices.created_at BETWEEN ? AND ?")
        params.extend([start_date, end_date])
    if invoice_number:
        conditions.append("invoices.invoice_number LIKE ?")
        params.append(f"%{invoice_number}%")
    if customer_name:
        conditions.append("customers.name LIKE ?")
        params.append(f"%{customer_name}%")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    cur.execute(query, params)
    r = cur.fetchall(); c.close(); return r

def get_invoice_items(invoice_id):
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT * FROM invoice_items WHERE invoice_id=?",(invoice_id,))
    r = cur.fetchall(); c.close(); return r

def get_invoice_by_number(invoice_number):
    c = get_conn(); cur = c.cursor()
    cur.execute("""SELECT invoices.*, customers.name AS customer_name, customers.phone, customers.balance 
                   FROM invoices LEFT JOIN customers ON invoices.customer_id=customers.id 
                   WHERE invoice_number=?""", (invoice_number,))
    r = cur.fetchone(); c.close(); return r

def get_activity(limit=200):
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT * FROM activity_log ORDER BY created_at DESC LIMIT ?", (limit,))
    r = cur.fetchall(); c.close(); return r

def backup_database():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(BACKUP_DIR, f"store_backup_{timestamp}.db")
    shutil.copy(DB, backup_path)
    log_action(f"نسخ احتياطي: {backup_path}")
    return backup_path

def compute_profit_loss(start_date=None, end_date=None):
    c = get_conn(); cur = c.cursor()
    if start_date and end_date:
        q = """SELECT SUM(line_total) as revenue, SUM(line_cost) as cost
               FROM invoice_items JOIN invoices ON invoice_items.invoice_id = invoices.id
               WHERE invoices.created_at BETWEEN ? AND ?"""
        cur.execute(q, (start_date, end_date))
    else:
        cur.execute("SELECT SUM(line_total) as revenue, SUM(line_cost) as cost FROM invoice_items")
    r = cur.fetchone()
    revenue = r["revenue"] or 0.0
    cost = r["cost"] or 0.0
    profit = revenue - cost
    c.close()
    return {"revenue": revenue, "cost": cost, "profit": profit}

def sales_by_product(start_date=None, end_date=None):
    c = get_conn(); cur = c.cursor()
    q = """SELECT p.code, p.thickness, SUM(i.qty) as total_qty, SUM(i.line_total) as total_revenue
           FROM invoice_items i JOIN products p ON i.product_id = p.id
           JOIN invoices inv ON i.invoice_id = inv.id"""
    if start_date and end_date:
        q += " WHERE inv.created_at BETWEEN ? AND ?"
        cur.execute(q + " GROUP BY p.id", (start_date, end_date))
    else:
        cur.execute(q + " GROUP BY p.id")
    rows = cur.fetchall(); c.close()
    return rows

def get_company_info():
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT company_name, company_address, company_phone, invoice_prefix FROM settings LIMIT 1")
    info = cur.fetchone(); c.close()
    return {
        "name": info["company_name"] if info and info["company_name"] else "شركتي",
        "address": info["company_address"] if info and info["company_address"] else "عنوان الشركة",
        "phone": info["company_phone"] if info and info["company_phone"] else "0123456789",
        "prefix": info["invoice_prefix"] if info and info["invoice_prefix"] else "INV"
    }

def get_settings_row():
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT * FROM settings LIMIT 1")
    r = cur.fetchone(); c.close(); return r

def hash_md5(text: str) -> str:
    try:
        return hashlib.md5(text.encode()).hexdigest()
    except Exception:
        return ""

def verify_password(kind: str, plain_text: str) -> bool:
    s = get_settings_row()
    if not s:
        return False
    if kind == "admin":
        expected = s["admin_password"] or DEFAULT_ADMIN_PASSWORD
    else:
        expected = s["edit_password"] or DEFAULT_EDIT_PASSWORD
    return hash_md5(plain_text) == expected

def ensure_font_for_pdf():
    # أولاً: حاول استخدام الخط المضمن
    font_path = os.path.join(BASE_DIR, "amiri-regular.ttf")
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("Amiri", font_path))
            return "Amiri"
        except Exception:
            pass

    # ثانياً: حاول استخدام خطوط النظام
    fonts_to_try = [("Arial", "arial.ttf"), ("Times", "times.ttf"), ("Courier", "cour.ttf")]
    for name, fname in fonts_to_try:
        possible = [
            fname,
            os.path.join(os.getcwd(), fname),
            os.path.join("C:\\Windows\\Fonts", fname),
            os.path.join(BASE_DIR, fname)
        ]
        for p in possible:
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(name, p))
                    return name
                except Exception:
                    continue
    # استخدام الخط الافتراضي إذا لم نجد خطوط أخرى
    return "Helvetica"

def generate_invoice_pdf(invoice_id, filename, customer_name, customer_phone, old_balance, new_balance, invoice_date, invoice_number, notes="", discount=0.0):
    if not REPORTLAB:
        # دعم Windows 7 32-bit - إنشاء ملف نصي بدلاً من PDF
        generate_invoice_text(invoice_id, filename, customer_name, customer_phone, old_balance, new_balance, invoice_date, invoice_number, notes, discount)
        return
    # لا نتحقق من ARABIC_SUPPORT لأننا نستخدم دالة بديلة
    
    try:
        dirpath = os.path.dirname(filename)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        
        items = get_invoice_items(invoice_id)
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        inv = cur.fetchone(); c.close()
        
        company = get_company_info()

        pdf = canvas.Canvas(filename, pagesize=A4)
        width, height = A4
        font = ensure_font_for_pdf()
        pdf.setFont(font, 12)

        # Header - دعم Windows 7 32-bit
        pdf.drawCentredString(width / 2, height - 30, get_display(company["name"]))
        pdf.setFont(font, 10)
        pdf.drawCentredString(width / 2, height - 45, get_display(company["address"]))
        pdf.drawCentredString(width / 2, height - 60, get_display(f"تليفون: {company['phone']}"))
        
        pdf.setFont(font, 14)
        pdf.drawCentredString(width / 2, height - 90, get_display("فاتورة مبيعات"))
        
        # Invoice details - دعم Windows 7 32-bit
        y = height - 120
        pdf.drawRightString(width - 50, y, get_display(f"رقم الفاتورة: {invoice_number}"))
        pdf.drawRightString(width - 300, y, get_display(f"التاريخ: {invoice_date}"))
        y -= 25
        pdf.drawRightString(width - 50, y, get_display(f"العميل: {customer_name or ''}"))
        pdf.drawRightString(width - 300, y, get_display(f"هاتف: {customer_phone or ''}"))
        y -= 25
        pdf.drawRightString(width - 50, y, get_display(f"الرصيد القديم: {old_balance:.2f}"))
        pdf.drawRightString(width - 300, y, get_display(f"الرصيد الجديد: {new_balance:.2f}"))
        
        if notes:
            y -= 25
            pdf.drawRightString(width - 50, y, get_display(f"ملاحظات: {notes}"))
        
        # Table headers - دعم Windows 7 32-bit
        y -= 40
        pdf.line(50, y, width - 50, y)
        y -= 20
        headers = ["الإجمالي", "شريط", "تقطيع", "سعر الوحدة", "كمية/طول", "سمك", "كود", "وصف"]  # Reversed
        x_positions = [width - 50, width - 120, width - 190, width - 260, width - 340, width - 410, width - 480, width - 550]  # Adjusted for right alignment
        for i, header in enumerate(headers):
            text = get_display(header)
            pdf.drawRightString(x_positions[i], y, text)
        y -= 10
        pdf.line(50, y, width - 50, y)
        y -= 20
        
        # Items - دعم Windows 7 32-bit
        for it in items:
            if y < 100:
                pdf.showPage()
                pdf.setFont(font, 12)
                y = height - 50
                pdf.line(50, y, width - 50, y)
                y -= 20
                for i, header in enumerate(headers):
                    text = get_display(header)
                    pdf.drawRightString(x_positions[i], y, text)
                y -= 10
                pdf.line(50, y, width - 50, y)
                y -= 20
            vals = [
                f"{float(it['line_total'] or 0):.2f}", 
                f"{float(it['edge_price'] or 0):.2f}", 
                f"{float(it['cutting_price'] or 0):.2f}", 
                f"{float(it['unit_price'] or 0):.2f}", 
                str(it["qty"]), 
                it["thickness"] or "", 
                it["product_code"] or "",
                it["description"] or ""
            ]  # Reversed
            for i, val in enumerate(vals):
                text = get_display(val)
                pdf.drawRightString(x_positions[i], y, text)
            y -= 20
        
        # Footer - دعم Windows 7 32-bit
        pdf.line(50, y, width - 50, y)
        y -= 20
        pdf.drawRightString(width - 50, y, get_display(f"المجموع الفرعي: {inv['subtotal'] + discount:.2f}"))
        if discount > 0:
            y -= 20
            pdf.drawRightString(width - 50, y, get_display(f"الخصم: {discount:.2f}"))
        y -= 20
        pdf.drawRightString(width - 50, y, get_display(f"المجموع بعد الخصم: {inv['subtotal']:.2f}"))
        y -= 20
        pdf.drawRightString(width - 50, y, get_display(f"المدفوع: {inv['paid']:.2f}"))
        pdf.drawRightString(width - 300, y, get_display(f"الإجمالي النهائي (مع الرصيد القديم): {inv['subtotal'] + old_balance:.2f}"))
        
        # Company stamp and signature
        y -= 40
        pdf.line(width/2 - 100, y, width/2 + 100, y)
        pdf.drawCentredString(width/2, y - 15, get_display("ختم وتوقيع الشركة"))
        
        pdf.save()
    except PermissionError:
        raise RuntimeError("خطأ في الوصول إلى الملف. تحقق من الأذونات أو أغلق الملف إذا كان مفتوحًا.")
    except Exception as e:
        raise RuntimeError(f"خطأ أثناء إنشاء PDF: {str(e)}")

def generate_invoice_text(invoice_id, filename, customer_name, customer_phone, old_balance, new_balance, invoice_date, invoice_number, notes="", discount=0.0):
    """دعم Windows 7 32-bit - إنشاء ملف نصي بدلاً من PDF"""
    try:
        # تغيير امتداد الملف إلى .txt
        if filename.endswith('.pdf'):
            filename = filename[:-4] + '.txt'
        
        items = get_invoice_items(invoice_id)
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
        inv = cur.fetchone(); c.close()
        
        company = get_company_info()
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"{company['name']}\n")
            f.write(f"{company['address']}\n")
            f.write(f"تليفون: {company['phone']}\n")
            f.write("=" * 60 + "\n")
            f.write("فاتورة مبيعات\n")
            f.write("=" * 60 + "\n")
            f.write(f"رقم الفاتورة: {invoice_number}\n")
            f.write(f"التاريخ: {invoice_date}\n")
            f.write(f"العميل: {customer_name or ''}\n")
            f.write(f"هاتف: {customer_phone or ''}\n")
            f.write(f"الرصيد القديم: {old_balance:.2f}\n")
            f.write(f"الرصيد الجديد: {new_balance:.2f}\n")
            if notes:
                f.write(f"ملاحظات: {notes}\n")
            if discount > 0:
                f.write(f"الخصم: {discount:.2f}\n")
            f.write("=" * 60 + "\n")
            f.write("المنتجات:\n")
            f.write("-" * 60 + "\n")
            
            for it in items:
                f.write(f"كود: {it['product_code']} | سمك: {it['thickness']} | كمية: {it['qty']} | ")
                f.write(f"سعر الوحدة: {float(it['unit_price'] or 0):.2f} | ")
                f.write(f"تقطيع: {float(it['cutting_price'] or 0):.2f} | ")
                f.write(f"شريط: {float(it['edge_price'] or 0):.2f} | ")
                f.write(f"الإجمالي: {float(it['line_total'] or 0):.2f}\n")
                if it.get('description'):
                    f.write(f"  وصف: {it['description']}\n")
            
            f.write("-" * 60 + "\n")
            f.write(f"المجموع الفرعي: {inv['subtotal'] + discount:.2f}\n")
            if discount > 0:
                f.write(f"الخصم: {discount:.2f}\n")
                f.write(f"المجموع بعد الخصم: {inv['subtotal']:.2f}\n")
            f.write(f"المدفوع: {inv['paid']:.2f}\n")
            f.write(f"الإجمالي النهائي (مع الرصيد القديم): {inv['subtotal'] + old_balance:.2f}\n")
            f.write("=" * 60 + "\n")
            f.write("ختم وتوقيع الشركة\n")
            f.write("=" * 60 + "\n")
        
    except Exception as e:
        raise RuntimeError(f"خطأ أثناء إنشاء الملف النصي: {str(e)}")

class PrintPreviewWindow(tk.Toplevel):
    def __init__(self, parent, invoice_id, customer_name, phone, old_balance, new_balance, items, invoice_date, invoice_number, notes="", discount=0.0):
        super().__init__(parent)
        self.title(f"معاينة طباعة الفاتورة رقم {invoice_number}")
        self.geometry("900x700")
        
        self.invoice_id = invoice_id
        self.customer_name = customer_name
        self.phone = phone
        self.old_balance = old_balance
        self.new_balance = new_balance
        self.items = items
        self.invoice_date = invoice_date
        self.invoice_number = invoice_number
        self.notes = notes
        self.discount = discount
        
        # Create a temporary PDF file
        self.temp_pdf = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
        self.temp_pdf.close()
        
        # Generate the PDF or Text file
        try:
            if REPORTLAB:
                generate_invoice_pdf(
                    invoice_id, 
                    self.temp_pdf.name, 
                    customer_name, 
                    phone, 
                    old_balance, 
                    new_balance, 
                    invoice_date, 
                    invoice_number,
                    notes,
                    discount
                )
            else:
                # دعم Windows 7 32-bit - إنشاء ملف نصي
                generate_invoice_text(
                    invoice_id, 
                    self.temp_pdf.name, 
                    customer_name, 
                    phone, 
                    old_balance, 
                    new_balance, 
                    invoice_date, 
                    invoice_number,
                    notes,
                    discount
                )
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إنشاء معاينة الطباعة: {str(e)}")
            self.destroy()
            return
        
        # Display PDF preview
        try:
            if os.name == 'nt':
                os.startfile(self.temp_pdf.name)
            elif os.name == 'posix':
                if os.system(f'xdg-open "{self.temp_pdf.name}"') != 0:
                    os.system(f'open "{self.temp_pdf.name}"')
        except Exception as e:
            messagebox.showwarning("تحذير", f"تم إنشاء الملف لكن فشل فتحه: {str(e)}")
        
        # Buttons frame
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(btn_frame, text="🖨️ طباعة مباشرة", command=self.print_directly, style="success.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="💾 حفظ كـ PDF", command=self.save_as_pdf, style="info.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="إغلاق", command=self.destroy, style="danger.TButton").pack(side=tk.RIGHT, padx=5)
    
    def print_directly(self):
        try:
            if REPORTLAB:
                # طباعة PDF
                if os.name == 'nt':
                    os.startfile(self.temp_pdf.name, "print")
                elif os.name == 'posix':
                    if os.system(f'lpr "{self.temp_pdf.name}"') != 0:
                        os.system(f'lp "{self.temp_pdf.name}"')
            else:
                # دعم Windows 7 32-bit - طباعة ملف نصي
                if os.name == 'nt':
                    # استخدام notepad لطباعة الملف النصي
                    os.system(f'notepad /p "{self.temp_pdf.name}"')
                elif os.name == 'posix':
                    os.system(f'lpr "{self.temp_pdf.name}"')
            messagebox.showinfo("تم", "تم إرسال الفاتورة إلى الطابعة")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إرسال الفاتورة للطباعة: {str(e)}")
    
    def save_as_pdf(self):
        if REPORTLAB:
            default_filename = f"فاتورة_{self.invoice_number}.pdf"
            filetypes = [("PDF", "*.pdf")]
            title = "حفظ الفاتورة كـ PDF"
        else:
            # دعم Windows 7 32-bit - حفظ كملف نصي
            default_filename = f"فاتورة_{self.invoice_number}.txt"
            filetypes = [("ملف نصي", "*.txt")]
            title = "حفظ الفاتورة كملف نصي"
        
        path = filedialog.asksaveasfilename(
            defaultextension=filetypes[0][1], 
            filetypes=filetypes, 
            initialfile=default_filename,
            title=title
        )
        if path:
            try:
                shutil.copy(self.temp_pdf.name, path)
                messagebox.showinfo("تم", f"تم حفظ الفاتورة في:\n{path}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حفظ الملف: {str(e)}")
    
    def destroy(self):
        try:
            os.remove(self.temp_pdf.name)
        except Exception:
            pass
        super().destroy()

class EditProductWindow(tk.Toplevel):
    def __init__(self, parent, pid, refresh):
        super().__init__(parent)
        self.title("تعديل منتج")
        self.geometry("400x400")
        # حماية شاشة التعديل الفردي
        pwd = tk.simpledialog.askstring("كلمة السر", "أدخل كلمة سر التعديل:", show="*")
        if not pwd or not verify_password("edit", pwd):
            messagebox.showerror("خطأ", "صلاحية التعديل مرفوضة."); self.destroy(); return
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT * FROM products WHERE id=?", (pid,))
        p = cur.fetchone(); c.close()
        frm = ttk.Frame(self, padding=10); frm.pack(fill=tk.BOTH, expand=True)
        ttk.Label(frm, text="نوع المنتج:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        type_var = tk.StringVar(value=p["type"] or "لوح")
        type_cb = ttk.Combobox(frm, textvariable=type_var, values=["لوح", "شريط الحرف", "آخر"], state="readonly", width=20)
        type_cb.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(frm, text="كود المنتج:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.E, padx=4, pady=4)
        code_ent = ttk.Entry(frm); code_ent.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4); code_ent.insert(0, p["code"])
        thickness_label = ttk.Label(frm, text="السمك:", font=("Arial", 10))
        thickness_entry = ttk.Entry(frm, width=20)
        length_label = ttk.Label(frm, text="طول شريط الحرف (متر):", font=("Arial", 10))
        length_entry = ttk.Entry(frm, width=20)
        price_label = ttk.Label(frm, text="سعر البيع (الوحدة):", font=("Arial", 10))
        price_entry = ttk.Entry(frm, width=16); price_entry.insert(0, p["price"] or 0)
        cost_label = ttk.Label(frm, text="تكلفة الوحدة (cost):", font=("Arial", 10))
        cost_entry = ttk.Entry(frm, width=16); cost_entry.insert(0, p["cost"] or 0)
        quantity_label = ttk.Label(frm, text="الكمية:", font=("Arial", 10))
        quantity_entry = ttk.Entry(frm, width=10); quantity_entry.insert(0, p["quantity"] or 0)
        low_label = ttk.Label(frm, text="تنبيه حد الكمية المنخفضة:", font=("Arial", 10))
        low_entry = ttk.Entry(frm, width=6); low_entry.insert(0, p["low_stock_threshold"] or 1)
        desc_label = ttk.Label(frm, text="وصف المنتج:", font=("Arial", 10))
        desc_entry = ttk.Entry(frm); desc_entry.insert(0, p["description"] or "")
        def update_fields(*args):
            for w in (thickness_label, thickness_entry, length_label, length_entry, price_label, price_entry, 
                      cost_label, cost_entry, quantity_label, quantity_entry, low_label, low_entry, desc_label, desc_entry):
                try:
                    w.grid_remove()
                except:
                    pass
            t = type_var.get()
            if t == "لوح":
                thickness_label.grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
                thickness_entry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
                thickness_entry.delete(0, tk.END); thickness_entry.insert(0, p["thickness"] or "")
                quantity_label.grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
                quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
                price_label.grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
                price_entry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
                cost_label.grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
                cost_entry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
                low_label.grid(row=6, column=0, sticky=tk.E, padx=4, pady=4)
                low_entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
                desc_label.grid(row=7, column=0, sticky=tk.E, padx=4, pady=4)
                desc_entry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)
            elif t == "شريط الحرف":
                length_label.grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
                length_entry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
                length_entry.delete(0, tk.END); length_entry.insert(0, p["edge_length"] or "")
                price_label.grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
                price_entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
                cost_label.grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
                cost_entry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
                low_label.grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
                low_entry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
                desc_label.grid(row=6, column=0, sticky=tk.E, padx=4, pady=4)
                desc_entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
            else:
                thickness_label.grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
                thickness_entry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
                thickness_entry.delete(0, tk.END); thickness_entry.insert(0, p["thickness"] or "")
                quantity_label.grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
                quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
                price_label.grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
                price_entry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
                cost_label.grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
                cost_entry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
                low_label.grid(row=6, column=0, sticky=tk.E, padx=4, pady=4)
                low_entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
                desc_label.grid(row=7, column=0, sticky=tk.E, padx=4, pady=4)
                desc_entry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)
        type_var.trace("w", update_fields)
        update_fields()
        def save():
            code = code_ent.get().strip()
            if not code:
                messagebox.showerror("خطأ", "كود المنتج مطلوب."); return
            ptype = type_var.get()
            thickness = thickness_entry.get().strip() if thickness_entry.winfo_ismapped() else ""
            try:
                price = float(price_entry.get()) if price_entry.winfo_ismapped() and price_entry.get().strip() else 0.0
            except:
                messagebox.showerror("خطأ", "أدخل سعرًا صحيحًا."); return
            try:
                costv = float(cost_entry.get()) if cost_entry.winfo_ismapped() and cost_entry.get().strip() else 0.0
            except:
                messagebox.showerror("خطأ", "أدخل تكلفة صحيحة."); return
            try:
                qty = int(quantity_entry.get()) if quantity_entry.winfo_ismapped() and quantity_entry.get().strip() else 0
            except:
                messagebox.showerror("خطأ", "أدخل كمية صحيحة."); return
            try:
                edge_len = float(length_entry.get()) if length_entry.winfo_ismapped() and length_entry.get().strip() else None
            except:
                messagebox.showerror("خطأ", "أدخل طول شريط صحيح."); return
            try:
                low = int(low_entry.get()) if low_entry.winfo_ismapped() else 1
            except:
                low = 1
            description = desc_entry.get().strip()
            try:
                update_product_db(pid, code, thickness, price, costv, qty, ptype, edge_len, low, description)
                messagebox.showinfo("تم", "تم تعديل المنتج.")
                refresh()
                self.destroy()
            except ValueError as e:
                messagebox.showerror("خطأ", str(e))
        ttk.Button(frm, text="حفظ التعديلات", command=save, style="success.TButton").grid(row=8, column=0, columnspan=2, pady=10)

class StoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(True, True)
        
        # تحسين الأداء للأجهزة الضعيفة - تقليل عدد الأزرار
        if THEME:
            self.style = ttk.Style(THEME)
        
        # شريط العنوان المبسط
        top = ttk.Frame(self, padding=4); top.pack(fill=tk.X)
        ttk.Label(top, text=APP_TITLE, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
        ttk.Button(top, text="نسخ احتياطي", command=self.backup_db).pack(side=tk.RIGHT, padx=2)
        ttk.Button(top, text="الإعدادات", command=self.show_settings).pack(side=tk.RIGHT, padx=2)
        
        # شريط التنقل المبسط للأجهزة الضعيفة
        nav = ttk.Frame(self, padding=4); nav.pack(fill=tk.X)
        ttk.Button(nav, text="إضافة منتج", command=self.show_add_product).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="المخزن", command=self.show_inventory).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="الفواتير", command=self.show_invoices).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="إنشاء فاتورة", command=self.show_create_invoice).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="المدين والدائن", command=self.show_customer_balances).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="الرسوم", command=self.show_fees_page).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="الكاش", command=self.show_cash_page).pack(side=tk.RIGHT, padx=2)
        ttk.Button(nav, text="تقارير", command=self.show_reports).pack(side=tk.RIGHT, padx=2)
        
        self.container = ttk.Frame(self, padding=6); self.container.pack(fill=tk.BOTH, expand=True)
        self.show_welcome()
        ensure_tables_and_columns()

    def clear(self):
        for w in self.container.winfo_children(): w.destroy()

    def show_welcome(self):
        self.clear()
        ttk.Label(self.container, text="مرحبًا! استخدم الأزرار أعلاه للعمل بالنظام.", font=("Arial", 12)).pack(pady=20)

    def backup_db(self):
        try:
            path = backup_database()
            messagebox.showinfo("تم", f"تم إنشاء نسخة احتياطية: {path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل النسخ الاحتياطي: {e}")

    def show_settings(self):
        w = tk.Toplevel(self)
        w.title("إعدادات النظام")
        w.geometry("500x400")
        
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT * FROM settings LIMIT 1")
        settings = cur.fetchone(); c.close()
        
        frm = ttk.Frame(w, padding=10); frm.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frm, text="اسم الشركة:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        company_name = ttk.Entry(frm); company_name.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        company_name.insert(0, settings["company_name"] or "")
        
        ttk.Label(frm, text="عنوان الشركة:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.E, padx=4, pady=4)
        company_address = ttk.Entry(frm); company_address.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        company_address.insert(0, settings["company_address"] or "")
        
        ttk.Label(frm, text="تليفون الشركة:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
        company_phone = ttk.Entry(frm); company_phone.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        company_phone.insert(0, settings["company_phone"] or "")
        
        ttk.Label(frm, text="بادئة رقم الفاتورة:", font=("Arial", 10)).grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
        invoice_prefix = ttk.Entry(frm); invoice_prefix.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
        invoice_prefix.insert(0, settings["invoice_prefix"] or "INV")
        
        ttk.Label(frm, text="سعر التقطيع الافتراضي:", font=("Arial", 10)).grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
        default_cutting = ttk.Entry(frm); default_cutting.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
        default_cutting.insert(0, settings["default_cutting_price"] or "0")
        
        ttk.Label(frm, text="سعر الشريط الافتراضي:", font=("Arial", 10)).grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
        default_edge = ttk.Entry(frm); default_edge.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
        default_edge.insert(0, settings["default_edge_price"] or "0")
        
        def save_settings():
            c = get_conn(); cur = c.cursor()
            cur.execute("""
                UPDATE settings SET 
                company_name=?, company_address=?, company_phone=?, 
                invoice_prefix=?, default_cutting_price=?, default_edge_price=?
            """, (
                company_name.get().strip(),
                company_address.get().strip(),
                company_phone.get().strip(),
                invoice_prefix.get().strip(),
                float(default_cutting.get() or 0),
                float(default_edge.get() or 0)
            ))
            c.commit(); c.close()
            messagebox.showinfo("تم", "تم حفظ الإعدادات بنجاح")
            w.destroy()
        
        ttk.Button(frm, text="حفظ الإعدادات", command=save_settings, style="success.TButton").grid(row=6, column=0, columnspan=2, pady=10)

        # تبويب الأمان
        sec = ttk.Labelframe(frm, text="الأمان", padding=10)
        sec.grid(row=7, column=0, columnspan=2, sticky=tk.EW, padx=4, pady=6)
        ttk.Label(sec, text="كلمة مرور الدخول (مشفر MD5):").grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        admin_pass = ttk.Entry(sec, show="*"); admin_pass.grid(row=0, column=1, sticky=tk.W)
        ttk.Label(sec, text="كلمة سر تعديل المنتجات (مشفر MD5):").grid(row=1, column=0, sticky=tk.E, padx=4, pady=4)
        edit_pass = ttk.Entry(sec, show="*"); edit_pass.grid(row=1, column=1, sticky=tk.W)
        login_required_var = tk.IntVar(value=settings["login_required"] or 0)
        ttk.Checkbutton(sec, text="تفعيل شاشة الدخول", variable=login_required_var).grid(row=2, column=0, columnspan=2, sticky=tk.W)

        def save_security():
            new_admin = admin_pass.get().strip()
            new_edit = edit_pass.get().strip()
            c = get_conn(); cur = c.cursor()
            if new_admin:
                cur.execute("UPDATE settings SET admin_password=?", (hash_md5(new_admin),))
            if new_edit:
                cur.execute("UPDATE settings SET edit_password=?", (hash_md5(new_edit),))
            cur.execute("UPDATE settings SET login_required=?", (1 if login_required_var.get() else 0,))
            c.commit(); c.close()
            messagebox.showinfo("تم", "تم حفظ إعدادات الأمان")
        ttk.Button(sec, text="حفظ الأمان", command=save_security, style="warning.TButton").grid(row=3, column=0, columnspan=2, pady=6)

    def show_add_product(self):
        self.clear()
        frm = ttk.Frame(self.container); frm.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(frm, text="نوع المنتج:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        type_var = tk.StringVar(value="لوح")
        type_cb = ttk.Combobox(frm, textvariable=type_var, values=["لوح", "شريط الحرف", "آخر"], state="readonly", width=20)
        type_cb.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(frm, text="كود المنتج:", font=("Arial", 10)).grid(row=1, column=0, sticky=tk.E, padx=4, pady=4)
        code_ent = ttk.Entry(frm); code_ent.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        thickness_label = ttk.Label(frm, text="السمك:", font=("Arial", 10))
        thickness_entry = ttk.Entry(frm, width=20)
        length_label = ttk.Label(frm, text="طول شريط الحرف (متر):", font=("Arial", 10))
        length_entry = ttk.Entry(frm, width=20)
        price_label = ttk.Label(frm, text="سعر البيع (الوحدة):", font=("Arial", 10))
        price_entry = ttk.Entry(frm, width=16)
        cost_label = ttk.Label(frm, text="تكلفة الوحدة (cost):", font=("Arial", 10))
        cost_entry = ttk.Entry(frm, width=16)
        quantity_label = ttk.Label(frm, text="الكمية:", font=("Arial", 10))
        quantity_entry = ttk.Entry(frm, width=10)
        low_label = ttk.Label(frm, text="تنبيه حد الكمية المنخفضة:", font=("Arial", 10))
        low_entry = ttk.Entry(frm, width=6); low_entry.insert(0, "1")
        desc_label = ttk.Label(frm, text="وصف المنتج:", font=("Arial", 10))
        desc_entry = ttk.Entry(frm)
        def update_fields(*args):
            for w in (thickness_label, thickness_entry, length_label, length_entry, price_label, price_entry, 
                      cost_label, cost_entry, quantity_label, quantity_entry, low_label, low_entry, desc_label, desc_entry):
                try:
                    w.grid_remove()
                except:
                    pass
            t = type_var.get()
            if t == "لوح":
                thickness_label.grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
                thickness_entry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
                quantity_label.grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
                quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
                price_label.grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
                price_entry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
                cost_label.grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
                cost_entry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
                low_label.grid(row=6, column=0, sticky=tk.E, padx=4, pady=4)
                low_entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
                desc_label.grid(row=7, column=0, sticky=tk.E, padx=4, pady=4)
                desc_entry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)
            elif t == "شريط الحرف":
                length_label.grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
                length_entry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
                price_label.grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
                price_entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
                cost_label.grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
                cost_entry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
                low_label.grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
                low_entry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
                desc_label.grid(row=6, column=0, sticky=tk.E, padx=4, pady=4)
                desc_entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
            else:
                thickness_label.grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
                thickness_entry.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
                quantity_label.grid(row=3, column=0, sticky=tk.E, padx=4, pady=4)
                quantity_entry.grid(row=3, column=1, sticky=tk.W, padx=4, pady=4)
                price_label.grid(row=4, column=0, sticky=tk.E, padx=4, pady=4)
                price_entry.grid(row=4, column=1, sticky=tk.W, padx=4, pady=4)
                cost_label.grid(row=5, column=0, sticky=tk.E, padx=4, pady=4)
                cost_entry.grid(row=5, column=1, sticky=tk.W, padx=4, pady=4)
                low_label.grid(row=6, column=0, sticky=tk.E, padx=4, pady=4)
                low_entry.grid(row=6, column=1, sticky=tk.W, padx=4, pady=4)
                desc_label.grid(row=7, column=0, sticky=tk.E, padx=4, pady=4)
                desc_entry.grid(row=7, column=1, sticky=tk.W, padx=4, pady=4)
        type_var.trace("w", update_fields)
        update_fields()
        def save_product():
            code = code_ent.get().strip()
            if not code:
                messagebox.showerror("خطأ", "كود المنتج مطلوب."); return
            ptype = type_var.get()
            thickness = thickness_entry.get().strip() if thickness_entry.winfo_ismapped() else ""
            try:
                price = float(price_entry.get()) if price_entry.winfo_ismapped() and price_entry.get().strip() else 0.0
            except:
                messagebox.showerror("خطأ", "أدخل سعرًا صحيحًا."); return
            try:
                costv = float(cost_entry.get()) if cost_entry.winfo_ismapped() and cost_entry.get().strip() else 0.0
            except:
                messagebox.showerror("خطأ", "أدخل تكلفة صحيحة."); return
            try:
                qty = int(quantity_entry.get()) if quantity_entry.winfo_ismapped() and quantity_entry.get().strip() else 0
            except:
                messagebox.showerror("خطأ", "أدخل كمية صحيحة."); return
            try:
                edge_len = float(length_entry.get()) if length_entry.winfo_ismapped() and length_entry.get().strip() else None
            except:
                messagebox.showerror("خطأ", "أدخل طول شريط صحيح."); return
            try:
                low = int(low_entry.get()) if low_entry.winfo_ismapped() else 1
            except:
                low = 1
            description = desc_entry.get().strip()
            try:
                add_product_db(code, thickness, price, costv, qty, ptype, edge_len, low, description)
                messagebox.showinfo("تم", "تمت إضافة المنتج.")
                code_ent.delete(0,tk.END)
                thickness_entry.delete(0,tk.END); price_entry.delete(0,tk.END); cost_entry.delete(0,tk.END)
                quantity_entry.delete(0,tk.END); length_entry.delete(0,tk.END); low_entry.delete(0,tk.END); low_entry.insert(0,"1")
                desc_entry.delete(0, tk.END)
            except ValueError as e:
                # إذا كان المنتج موجودًا، عرض خيار التعديل
                if "موجود بالفعل" in str(e):
                    # البحث عن المنتج الموجود بنفس الكود والسمك
                    existing = get_product_by_code_and_thickness(code, thickness)
                    if existing:
                        if messagebox.askyesno("تنبيه", f"{e}\nهل تريد تعديل المنتج الموجود؟"):
                            EditProductWindow(self, existing["id"], self.show_inventory)
                else:
                    messagebox.showerror("خطأ", str(e))
        ttk.Button(frm, text="حفظ المنتج", command=save_product, style="success.TButton").grid(row=8, column=0, columnspan=2, pady=10)

    def show_inventory(self):
        self.clear()
        # تحسين الأداء للأجهزة الضعيفة - واجهة مبسطة
        top = ttk.Frame(self.container); top.pack(fill=tk.X, padx=4, pady=4)
        ttk.Label(top, text="بحث:", font=("Arial", 9)).pack(side=tk.LEFT)
        q_ent = ttk.Entry(top, width=20); q_ent.pack(side=tk.LEFT, padx=4)
        def do_search():
            for r in tree.get_children(): tree.delete(r)
            rows = search_products(q_ent.get().strip())
            # تحسين الأداء للأجهزة الضعيفة - تقليل عدد الأعمدة
            for r in rows:
                tree.insert("", tk.END, values=(
                    r["code"], r["thickness"], r["price"], r["quantity"], r["type"], r["edge_length"] or 0
                ))
        ttk.Button(top, text="بحث", command=do_search).pack(side=tk.LEFT, padx=2)
        ttk.Button(top, text="تحديث", command=do_search).pack(side=tk.LEFT, padx=2)
        
        # تحسين الأداء للأجهزة الضعيفة - تقليل عدد الأعمدة
        cols = ("code","thickness","price","quantity","type","edge_length")
        tree = ttk.Treeview(self.container, columns=cols, show="headings", height=TREE_HEIGHT)
        headings = ["كود","سمك","سعر","كمية","نوع","طول الشريط"]
        for c,h in zip(cols,headings):
            tree.heading(c, text=h); tree.column(c, width=80, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)
        btns = ttk.Frame(self.container); btns.pack(fill=tk.X, padx=6, pady=6)
        def on_edit():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("تحذير", "اختر منتجًا للتعديل."); return
            # حماية تعديل فردي
            pwd = tk.simpledialog.askstring("كلمة السر", "أدخل كلمة سر التعديل:", show="*")
            if not pwd or not verify_password("edit", pwd):
                messagebox.showerror("خطأ", "صلاحية التعديل مرفوضة."); return
            pid = tree.item(sel[0])["values"][0]
            EditProductWindow(self, pid, do_search)
        def on_edit_all():
            password = tk.simpledialog.askstring("كلمة المرور", "أدخل الرقم السري لتعديل كل المنتجات:", show="*")
            if password == DEFAULT_EDIT_PASSWORD:
                self.edit_all_products(do_search)
            else:
                messagebox.showerror("خطأ", "الرقم السري خاطئ.")
        def on_delete():
            sel = tree.selection()
            if not sel:
                messagebox.showwarning("تحذير", "اختر منتجًا للحذف."); return
            if not messagebox.askyesno("تأكيد", "هل تريد حذف المنتج؟"): return
            pid = tree.item(sel[0])["values"][0]; delete_product_db(pid); do_search()
        def export_inventory():
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if not path: return
            rows = search_products()
            with open(path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f); writer.writerow(["id","code","thickness","price","cost","quantity","type","edge_length","description"])
                for r in rows:
                    writer.writerow([r["id"],r["code"],r["thickness"],r["price"],r["cost"],r["quantity"],r["type"],r["edge_length"],r["description"]])
            messagebox.showinfo("تم", f"تم تصدير المخزن إلى {path}")
        ttk.Button(btns, text="✏️ تعديل", command=on_edit, style="warning.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="✏️ تعديل الكل", command=on_edit_all, style="warning.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="🗑️ حذف", command=on_delete, style="danger.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="📤 تصدير CSV", command=export_inventory, style="primary.TButton").pack(side=tk.LEFT, padx=4)
        do_search()

    def edit_all_products(self, refresh):
        w = tk.Toplevel(self); w.title("تعديل كل المنتجات"); w.geometry("1000x600")
        cols = ("id","code","thickness","price","cost","quantity","type","edge_length","low_stock","description")
        tree = ttk.Treeview(w, columns=cols, show="headings", height=20)
        headings = ["ID","كود","سمك","سعر","تكلفة","كمية","نوع","طول شريط","تنبيه حد","وصف"]
        for c,h in zip(cols,headings):
            tree.heading(c, text=h); tree.column(c, width=100, anchor=tk.CENTER)
        tree.column("description", width=200)
        tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        rows = search_products()
        for r in rows:
            tree.insert("", tk.END, iid=r["id"], values=(r["id"], r["code"], r["thickness"], r["price"], r["cost"], r["quantity"], r["type"], r["edge_length"], r["low_stock_threshold"], r["description"]))
        def edit_cell(event):
            item = tree.identify_row(event.y)
            column = tree.identify_column(event.x)
            if item and column:
                bbox = tree.bbox(item, column)
                entry = ttk.Entry(w)
                entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                entry.insert(0, tree.item(item, "values")[int(column[1]) - 1])
                entry.focus()
                def finish_edit(e):
                    new_val = entry.get()
                    tree.set(item, column, new_val)
                    pid = item
                    col_name = cols[int(column[1]) - 1]
                    if col_name in ["price", "cost"]:
                        new_val = float(new_val)
                    elif col_name in ["quantity", "low_stock_threshold"]:
                        new_val = int(new_val)
                    elif col_name == "edge_length":
                        new_val = float(new_val) if new_val else None
                    c = get_conn(); cur = c.cursor()
                    cur.execute(f"UPDATE products SET {col_name}=? WHERE id=?", (new_val, pid))
                    c.commit(); c.close()
                    entry.destroy()
                    refresh()
                entry.bind("<Return>", finish_edit)
        tree.bind("<Double-1>", edit_cell)
        ttk.Button(w, text="إغلاق", command=w.destroy, style="danger.TButton").pack(pady=5)

    def show_invoices(self):
        self.clear()
        filter_frm = ttk.Frame(self.container); filter_frm.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(filter_frm, text="من (YYYY-MM-DD):", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        start_date_ent = ttk.Entry(filter_frm, width=12); start_date_ent.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter_frm, text="إلى (YYYY-MM-DD):", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        end_date_ent = ttk.Entry(filter_frm, width=12); end_date_ent.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter_frm, text="رقم الفاتورة:", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        invoice_num_ent = ttk.Entry(filter_frm, width=12); invoice_num_ent.pack(side=tk.LEFT, padx=2)
        ttk.Label(filter_frm, text="اسم العميل:", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        customer_name_ent = ttk.Entry(filter_frm, width=15); customer_name_ent.pack(side=tk.LEFT, padx=2)
        
        def load_invoices():
            for r in invoices_tree.get_children(): invoices_tree.delete(r)
            rows = get_invoices(100, 
                                start_date_ent.get() or None, 
                                end_date_ent.get() or None, 
                                invoice_num_ent.get() or None,
                                customer_name_ent.get() or None)
            for r in rows:
                invoices_tree.insert("", tk.END, values=(
                    r["invoice_number"], r["customer_name"], r["created_at"], 
                    f"{r['subtotal']:.2f}", f"{r['paid']:.2f}", 
                    f"{float(r['subtotal']) - float(r['paid']):.2f}"
                ))
            on_invoice_select()
        
        ttk.Button(filter_frm, text="📅 تصفية الفواتير", command=load_invoices, style="primary.TButton").pack(side=tk.LEFT, padx=4)
        invoices_frame = ttk.Frame(self.container); invoices_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        invoices_tree = ttk.Treeview(invoices_frame, columns=("number","customer","date","subtotal","paid","remaining"), show="headings", height=10)
        invoices_tree.heading("number", text="رقم الفاتورة"); invoices_tree.column("number", width=120)
        invoices_tree.heading("customer", text="العميل"); invoices_tree.column("customer", width=200)
        invoices_tree.heading("date", text="التاريخ"); invoices_tree.column("date", width=120)
        invoices_tree.heading("subtotal", text="المجموع"); invoices_tree.column("subtotal", width=100, anchor=tk.E)
        invoices_tree.heading("paid", text="المدفوع"); invoices_tree.column("paid", width=100, anchor=tk.E)
        invoices_tree.heading("remaining", text="المتبقي"); invoices_tree.column("remaining", width=100, anchor=tk.E)
        invoices_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scroll = ttk.Scrollbar(invoices_frame, orient=tk.VERTICAL, command=invoices_tree.yview)
        scroll.pack(fill=tk.Y, side=tk.RIGHT)
        invoices_tree.configure(yscrollcommand=scroll.set)
        # خزن المرجع لاستخدامه في الأزرار
        self.invoices_tree = invoices_tree

        # لوحة تفاصيل الفاتورة
        details_frame = ttk.Frame(self.container); details_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        detail_cols = ("code","thickness","qty","unit_price","cutting_price","edge_price","line_total","desc")
        details_tree = ttk.Treeview(details_frame, columns=detail_cols, show="headings", height=8)
        for c,h in zip(detail_cols, ["كود","سمك","كمية/طول","سعر الوحدة","تقطيع","شريط","الإجمالي","وصف"]):
            details_tree.heading(c, text=h); details_tree.column(c, width=120, anchor=tk.CENTER)
        details_tree.column("desc", width=200)
        details_tree.pack(fill=tk.BOTH, expand=True)
        self.details_tree = details_tree

        def on_invoice_select(event=None):
            for r in details_tree.get_children():
                details_tree.delete(r)
            sel = invoices_tree.selection()
            if not sel:
                return
            invoice_number = invoices_tree.item(sel[0])["values"][0]
            inv = get_invoice_by_number(invoice_number)
            if not inv:
                return
            items = get_invoice_items(inv["id"])
            for it in items:
                desc_val = it["description"] if ("description" in it.keys() and it["description"] is not None) else ""
                details_tree.insert("", tk.END, values=(
                    it["product_code"], it["thickness"], it["qty"],
                    f"{float(it['unit_price'] or 0):.2f}", f"{float(it['cutting_price'] or 0):.2f}",
                    f"{float(it['edge_price'] or 0):.2f}", f"{float(it['line_total'] or 0):.2f}",
                    desc_val
                ))
        invoices_tree.bind("<<TreeviewSelect>>", on_invoice_select)
        
        inv_actions = ttk.Frame(self.container); inv_actions.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(inv_actions, text="عرض الفاتورة المحددة", command=self.view_selected_invoice, style="info.TButton").pack(side=tk.LEFT, padx=4)
        # إظهار زر المعاينة دائمًا؛ سيتم التعامل مع الاعتماديات داخل الدالة
        ttk.Button(inv_actions, text="🖨️ معاينة طباعة الفاتورة المحددة", command=self.print_selected_invoice, style="success.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Button(inv_actions, text="💾 حفظ الفاتورة المحددة كـ PDF", command=self.save_selected_invoice_as_pdf, style="primary.TButton").pack(side=tk.LEFT, padx=4)
        load_invoices()

    def view_selected_invoice(self):
        sel = getattr(self, 'invoices_tree', None).selection() if hasattr(self, 'invoices_tree') else []
        if not sel:
            messagebox.showwarning("تحذير", "اختر فاتورة لعرضها")
            return
        invoice_number = self.invoices_tree.item(sel[0])["values"][0]
        inv = get_invoice_by_number(invoice_number)
        if not inv:
            messagebox.showerror("خطأ", "الفاتورة غير موجودة")
            return
        items = get_invoice_items(inv["id"])
        self.show_invoice_details(
            inv["id"], inv["customer_name"], inv["phone"], 
            inv["balance"] - inv["paid"] + inv["subtotal"], 
            inv["balance"], items, inv["created_at"], 
            inv["invoice_number"], inv["notes"] or "",
            inv["discount"] or 0.0
        )

    def print_selected_invoice(self):
        if not REPORTLAB:
            messagebox.showwarning("تحذير", "مكتبة reportlab غير مثبتة للطباعة/المعاينة.")
            return
        sel = getattr(self, 'invoices_tree', None).selection() if hasattr(self, 'invoices_tree') else []
        if not sel:
            messagebox.showwarning("تحذير", "اختر فاتورة لطباعتها")
            return
        invoice_number = self.invoices_tree.item(sel[0])["values"][0]
        inv = get_invoice_by_number(invoice_number)
        if not inv:
            messagebox.showerror("خطأ", "الفاتورة غير موجودة")
            return
        items = get_invoice_items(inv["id"])
        old_bal = inv["balance"] - inv["paid"] + inv["subtotal"]
        new_bal = inv["balance"]
        PrintPreviewWindow(
            self, inv["id"], inv["customer_name"], inv["phone"], old_bal, new_bal, 
            items, inv["created_at"], inv["invoice_number"], inv["notes"] or "",
            inv["discount"] or 0.0
        )

    def save_selected_invoice_as_pdf(self):
        if not REPORTLAB:
            messagebox.showwarning("تحذير", "مكتبة reportlab غير مثبتة.")
            return
        sel = getattr(self, 'invoices_tree', None).selection() if hasattr(self, 'invoices_tree') else []
        if not sel:
            messagebox.showwarning("تحذير", "اختر فاتورة للحفظ")
            return
        invoice_number = self.invoices_tree.item(sel[0])["values"][0]
        inv = get_invoice_by_number(invoice_number)
        if not inv:
            messagebox.showerror("خطأ", "الفاتورة غير موجودة")
            return
        default_filename = f"فاتورة_{invoice_number}.pdf"
        path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF","*.pdf")], initialfile=default_filename, title="حفظ فاتورة كـ PDF")
        if not path:
            return
        items = get_invoice_items(inv["id"])
        old_bal = inv["balance"] - inv["paid"] + inv["subtotal"]
        new_bal = inv["balance"]
        try:
            generate_invoice_pdf(inv["id"], path, inv["customer_name"], inv["phone"], old_bal, new_bal, inv["created_at"], invoice_number, inv["notes"] or "", inv["discount"] or 0.0)
            messagebox.showinfo("تم", f"تم حفظ الفاتورة في:\n{path}")
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل حفظ الفاتورة: {e}")

    def show_create_invoice(self):
        self.clear()
        top = ttk.Frame(self.container); top.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(top, text="اسم العميل:", font=("Arial", 10)).pack(side=tk.LEFT)
        cust_ent = ttk.Entry(top); cust_ent.pack(side=tk.LEFT, padx=6)
        ttk.Label(top, text="هاتف:", font=("Arial", 10)).pack(side=tk.LEFT); phone_ent = ttk.Entry(top, width=14); phone_ent.pack(side=tk.LEFT, padx=6)
        balance_label = ttk.Label(top, text="رصيد العميل: 0.00", font=("Arial", 10))
        balance_label.pack(side=tk.LEFT, padx=(10,6))
        ttk.Label(top, text="تاريخ الفاتورة:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(10,2))
        date_ent = ttk.Entry(top, width=12); date_ent.pack(side=tk.LEFT, padx=2)
        date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        def fetch_balance(ev=None):
            name = cust_ent.get().strip()
            if not name:
                balance_label.config(text="رصيد العميل: 0.00"); return
            c = get_customer_by_name(name)
            if c:
                balance_label.config(text=f"رصيد العميل: {c['balance']:.2f}"); phone_ent.delete(0,tk.END); phone_ent.insert(0, c["phone"] or "")
            else:
                balance_label.config(text="رصيد العميل: 0.00 (عميل جديد)")
        ttk.Button(top, text="🔍 جلب الرصيد", command=fetch_balance, style="primary.TButton").pack(side=tk.LEFT, padx=4)
        cust_ent.bind("<FocusOut>", fetch_balance)
        ttk.Label(top, text="سعر التقطيع:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20,2))
        cutting_price_ent = ttk.Entry(top, width=10); cutting_price_ent.pack(side=tk.LEFT, padx=2); cutting_price_ent.insert(0, "0")
        ttk.Label(top, text="طول شريط الحرف (متر):", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20,2))
        edge_length_ent = ttk.Entry(top, width=10); edge_length_ent.pack(side=tk.LEFT, padx=2); edge_length_ent.insert(0, "0")
        ttk.Label(top, text="كود شريط الحرف:", font=("Arial", 10)).pack(side=tk.LEFT, padx=(20,2))
        edge_code_ent = ttk.Entry(top, width=10); edge_code_ent.pack(side=tk.LEFT, padx=2)
        add_item_frm = ttk.Frame(self.container); add_item_frm.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(add_item_frm, text="كود المنتج:", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        code_ent = ttk.Entry(add_item_frm, width=15); code_ent.pack(side=tk.LEFT, padx=4)
        ttk.Label(add_item_frm, text="السمك:", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        thickness_cb = ttk.Combobox(add_item_frm, width=20, state="readonly"); thickness_cb.pack(side=tk.LEFT, padx=4)
        qty_ent = ttk.Entry(add_item_frm, width=10); qty_ent.pack(side=tk.LEFT, padx=4); qty_ent.insert(0, "1")
        ttk.Label(add_item_frm, text="كمية/طول", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Button(add_item_frm, text="1", command=lambda: qty_ent.delete(0, tk.END) or qty_ent.insert(0, "1"), style="info.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(add_item_frm, text="5", command=lambda: qty_ent.delete(0, tk.END) or qty_ent.insert(0, "5"), style="info.TButton").pack(side=tk.LEFT, padx=2)
        ttk.Button(add_item_frm, text="10", command=lambda: qty_ent.delete(0, tk.END) or qty_ent.insert(0, "10"), style="info.TButton").pack(side=tk.LEFT, padx=2)
        cut_ent = ttk.Entry(add_item_frm, width=10); cut_ent.pack(side=tk.LEFT, padx=4); cut_ent.insert(0, cutting_price_ent.get() or "0")
        ttk.Label(add_item_frm, text="سعر التقطيع", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        ttk.Label(add_item_frm, text="الوصف:", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        desc_ent = ttk.Entry(add_item_frm, width=20); desc_ent.pack(side=tk.LEFT, padx=4)
        ttk.Button(add_item_frm, text="➕ أضف بند", command=lambda: add_item_inline(), style="success.TButton").pack(side=tk.LEFT, padx=4)
        def update_thickness_options(*args):
            code = code_ent.get().strip()
            thickness_cb.set("")
            thickness_cb["values"] = []
            if code:
                products = get_product_by_code(code)
                # لا تستبعد السماكات الفارغة
                thickness_options = [(p["thickness"] or "") for p in products]
                thickness_cb["values"] = thickness_options
                if len(thickness_options) == 1:
                    thickness_cb.set(thickness_options[0])
        code_ent.bind("<KeyRelease>", update_thickness_options)
        def add_item_inline():
            code = code_ent.get().strip()
            thickness = thickness_cb.get().strip()
            if not code:
                messagebox.showerror("خطأ", "يرجى إدخال كود المنتج.")
                return
            product = get_product_by_code_and_thickness(code, thickness)
            if not product:
                messagebox.showerror("خطأ", "المنتج غير موجود بهذا الكود والسمك.")
                return
            unit_price = product["price"] or 0.0
            is_edge = (product["type"] == "شريط الحرف")
            try:
                q = float(qty_ent.get())
                if q <= 0:
                    messagebox.showerror("خطأ", "الكمية/الطول يجب أن تكون أكبر من 0.")
                    return
            except:
                messagebox.showerror("خطأ", "الكمية/الطول يجب أن يكون رقمًا.")
                return
            try:
                cutting_per_slab = float(cut_ent.get()) if cut_ent.get().strip() else 0.0
                # حساب إجمالي سعر التقطيع (سعر التقطيع للوح × الكمية)
                cutting_total = cutting_per_slab * q
            except:
                messagebox.showerror("خطأ", "سعر التقطيع خاطئ.")
                return
            edge_total = 0.0
            if is_edge:
                # بيع شريط الحرف بالمتر: نستخدم q كطول بالمتر، ولا نضيف تكلفة شريط إضافية
                edge_total = 0.0
            else:
                edge_code = edge_code_ent.get().strip()
                edge_price = 0.0
                edge_len = 0.0
                if edge_code:
                    edge_product = get_product_by_code(edge_code)
                    if edge_product and edge_product[0]["type"] == "شريط الحرف":
                        edge_price = edge_product[0]["price"] or 0.0
                        try:
                            edge_len = float(edge_length_ent.get()) if edge_length_ent.get().strip() else 0.0
                            if edge_len < 0:
                                messagebox.showerror("خطأ", "طول شريط الحرف يجب أن يكون رقمًا موجبًا.")
                                return
                        except:
                            messagebox.showerror("خطأ", "طول شريط الحرف يجب أن يكون رقمًا.")
                            return
                    else:
                        messagebox.showerror("خطأ", "كود شريط الحرف غير صحيح أو ليس شريط حرف.")
                        return
            product_total = unit_price * q
            if is_edge:
                line_total = product_total + cutting_total
            else:
                line_total = product_total + cutting_total
            qty_display = f"{q:.2f}" if is_edge else f"{int(q)}"
            # السطر الأساسي (لوح أو شريط)
            items_tree.insert("", tk.END, values=(
                code, thickness, qty_display, f"{unit_price:.2f}", 
                f"{cutting_per_slab:.2f}", f"{0.0:.2f}", f"{line_total:.2f}",
                desc_ent.get().strip(), "", ""
            ))
            # إذا تم اختيار شريط حرف مع اللوح: أضف بندًا منفصلًا لشريط الحرف ليتم خصم الطول من المخزن
            if (not is_edge) and edge_code and edge_len > 0:
                edge_line_total = edge_price * edge_len
                items_tree.insert("", tk.END, values=(
                    edge_code, "", f"{edge_len:.2f}", f"{edge_price:.2f}",
                    f"{0.0:.2f}", f"{0.0:.2f}", f"{edge_line_total:.2f}",
                    "شريط حرف", "", ""
                ))
            code_ent.delete(0, tk.END)
            thickness_cb.set("")
            qty_ent.delete(0, tk.END); qty_ent.insert(0, "1")
            cut_ent.delete(0, tk.END); cut_ent.insert(0, cutting_price_ent.get() or "0")
            edge_length_ent.delete(0, tk.END); edge_length_ent.insert(0, "0")
            edge_code_ent.delete(0, tk.END)
            desc_ent.delete(0, tk.END)
            update_totals_display()
        # أضف أعمدة خفية لتخزين كود وطول شريط الحرف المستخدم مع البنود غير الشريط
        cols = ("code","thickness","qty","unit_price","cutting_price","edge_price","line_total","desc","_edge_code","_edge_len")
        items_tree = ttk.Treeview(self.container, columns=cols, show="headings", height=12)
        headers = ["كود","سمك","كمية/طول(m)","سعر الوحدة","سعر التقطيع","سعر الشريط","الإجمالي","وصف","",""]
        for c,h in zip(cols,headers):
            items_tree.heading(c, text=h); items_tree.column(c, width=120, anchor=tk.CENTER)
        items_tree.column("desc", width=200)
        # إخفاء الأعمدة المساعدة
        items_tree.column("_edge_code", width=0, stretch=False)
        items_tree.column("_edge_len", width=0, stretch=False)
        items_tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        search_frm = ttk.Frame(self.container); search_frm.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(search_frm, text="بحث بالكود:", font=("Arial", 10)).pack(side=tk.LEFT)
        code_search_ent = ttk.Entry(search_frm); code_search_ent.pack(side=tk.LEFT, padx=6)
        ttk.Button(search_frm, text="🔍 بحث", command=lambda: search_by_code(), style="primary.TButton").pack(side=tk.LEFT, padx=4)
        def search_by_code():
            code = code_search_ent.get().strip()
            if not code:
                messagebox.showerror("خطأ", "أدخل الكود للبحث.")
                return
            rows = get_product_by_code(code)
            w = tk.Toplevel(self); w.title("المنتجات بالكود: " + code); w.geometry("800x600")
            cols = ("id","thickness","price","cost","quantity","type","edge_length","low_stock","description")
            tree = ttk.Treeview(w, columns=cols, show="headings", height=20)
            headings = ["ID","سمك","سعر","تكلفة","كمية","نوع","طول شريط","تنبيه حد","وصف"]
            for c,h in zip(cols,headings):
                tree.heading(c, text=h); tree.column(c, width=100, anchor=tk.CENTER)
            tree.column("description", width=200)
            tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
            for r in rows:
                tree.insert("", tk.END, values=(r["id"], r["thickness"], r["price"], r["cost"], r["quantity"], r["type"], r["edge_length"], r["low_stock_threshold"], r["description"]))
        btns = ttk.Frame(self.container); btns.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(btns, text="🗑️ حذف بند", command=lambda: [items_tree.delete(i) for i in items_tree.selection()] or update_totals_display(), style="danger.TButton").pack(side=tk.LEFT, padx=4)
        payfrm = ttk.Frame(self.container); payfrm.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(payfrm, text="مدفوع الآن:", font=("Arial", 10)).pack(side=tk.LEFT)
        paid_ent = ttk.Entry(payfrm, width=12); paid_ent.pack(side=tk.LEFT, padx=6); paid_ent.insert(0,"0")
        ttk.Label(payfrm, text="الخصم:", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        discount_ent = ttk.Entry(payfrm, width=10); discount_ent.pack(side=tk.LEFT, padx=2); discount_ent.insert(0, "0")
        subtotal_label = ttk.Label(payfrm, text="المجموع الفرعي: 0.00", font=("Arial", 10)); subtotal_label.pack(side=tk.LEFT, padx=10)
        discount_display_label = ttk.Label(payfrm, text="بعد الخصم: 0.00", font=("Arial", 10)); discount_display_label.pack(side=tk.LEFT, padx=10)
        remaining_label = ttk.Label(payfrm, text="المتبقي للدفع: 0.00", font=("Arial", 10)); remaining_label.pack(side=tk.LEFT, padx=10)
        final_display_label = ttk.Label(payfrm, text="الإجمالي النهائي (شامل الرصيد القديم): 0.00", font=("Arial", 10)); final_display_label.pack(side=tk.LEFT, padx=10)
        notes_label = ttk.Label(payfrm, text="ملاحظات:", font=("Arial", 10)); notes_label.pack(side=tk.LEFT, padx=2)
        notes_ent = ttk.Entry(payfrm, width=30); notes_ent.pack(side=tk.LEFT, padx=2)
        def update_totals_display():
            subtotal = 0.0
            for r in items_tree.get_children():
                try:
                    subtotal += float(items_tree.item(r)["values"][6])
                except:
                    pass
            subtotal_label.config(text=f"المجموع الفرعي: {subtotal:.2f}")
            try:
                discount = float(discount_ent.get()) if discount_ent.get().strip() else 0.0
                if discount < 0:
                    discount = 0.0
            except:
                discount = 0.0
            subtotal_after_discount = max(0, subtotal - discount)
            discount_display_label.config(text=f"بعد الخصم: {subtotal_after_discount:.2f}")
            try:
                paid = float(paid_ent.get()) if paid_ent.get().strip() else 0.0
            except:
                paid = 0.0
            remaining = subtotal_after_discount - paid
            remaining_label.config(text=f"المتبقي للدفع: {remaining:.2f}")
            name = cust_ent.get().strip()
            old_bal = 0.0
            if name:
                c = get_customer_by_name(name)
                if c:
                    old_bal = c["balance"]
            final_display = subtotal_after_discount + old_bal
            final_display_label.config(text=f"الإجمالي النهائي (شامل الرصيد القديم): {final_display:.2f}")
        items_tree.bind("<<TreeviewSelect>>", lambda e: update_totals_display())
        ttk.Button(payfrm, text="🧮 حساب الإجمالي", command=update_totals_display, style="primary.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(payfrm, text="حفظ الفاتورة", command=lambda: self.save_invoice(cust_ent, phone_ent, date_ent, notes_ent, items_tree, paid_ent, balance_label, update_totals_display, discount_ent), style="success.TButton").pack(side=tk.LEFT, padx=4)
        if REPORTLAB:
            # ميزات الطباعة داخل صفحة إنشاء الفاتورة
            ttk.Button(payfrm, text="💾 حفظ كـ PDF", command=lambda: self.save_invoice(cust_ent, phone_ent, date_ent, notes_ent, items_tree, paid_ent, balance_label, update_totals_display, discount_ent, True), style="info.TButton").pack(side=tk.LEFT, padx=4)
            ttk.Button(payfrm, text="🖨️ طباعة مباشرة", command=lambda: self.save_invoice(cust_ent, phone_ent, date_ent, notes_ent, items_tree, paid_ent, balance_label, update_totals_display, discount_ent, False, True), style="success.TButton").pack(side=tk.LEFT, padx=4)

    def save_invoice(self, cust_ent, phone_ent, date_ent, notes_ent, items_tree, paid_ent, balance_label, update_totals_display, discount_ent, ask_print=False, print_directly=False):
        customer = cust_ent.get().strip()
        phone = phone_ent.get().strip()
        invoice_date = date_ent.get().strip() or datetime.now().strftime("%Y-%m-%d")
        notes = notes_ent.get().strip()
        try:
            datetime.strptime(invoice_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح. استخدم YYYY-MM-DD (مثال: 2025-08-11)")
            return
        if not customer:
            messagebox.showerror("خطأ", "أدخل اسم العميل.")
            return
        items = []
        for r in items_tree.get_children():
            vals = items_tree.item(r)["values"]
            code = vals[0]
            thickness = vals[1]
            qty = float(vals[2])
            unit_price = float(vals[3])
            cutting_price = float(vals[4])
            edge_price = float(vals[5])
            line_total = float(vals[6])
            description = vals[7] if len(vals) > 7 else ""
            p = get_product_by_code_and_thickness(code, thickness)
            is_edge = (p and p["type"] == "شريط الحرف")
            items.append({
                "code": code,
                "thickness": thickness,
                "qty": qty,
                "unit_price": unit_price,
                "cutting_price": cutting_price,
                "edge_price": edge_price,
                "line_total": line_total,
                "is_edge_strip": is_edge,
                "description": description
            })
        if not items:
            messagebox.showerror("خطأ", "أضف بندًا واحدًا على الأقل.")
            return
        try:
            paid = float(paid_ent.get())
            if paid < 0:
                messagebox.showerror("خطأ", "المبلغ المدفوع لا يمكن أن يكون سالبًا.")
                return
        except:
            messagebox.showerror("خطأ", "أدخل مبلغًا صحيحًا للمدفوع.")
            return
        try:
            discount = float(discount_ent.get()) if discount_ent.get().strip() else 0.0
            if discount < 0:
                discount = 0.0
        except:
            discount = 0.0
        inv_id, old_bal, new_bal, inv_number = create_invoice_db(customer, phone, items, paid, invoice_date, notes, discount)
        c = get_customer_by_name(customer)
        if c:
            balance_label.config(text=f"رصيد العميل: {c['balance']:.2f}")
        self.show_invoice_details(inv_id, customer, phone, old_bal, new_bal, items, invoice_date, inv_number, notes, discount)
        if ask_print or print_directly:
            if not REPORTLAB:
                messagebox.showwarning("تنبيه", "مكتبة reportlab غير مثبتة. نفّذ: pip install reportlab")
                return
            if print_directly:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    temp_path = tmp.name
                try:
                    generate_invoice_pdf(
                        inv_id, temp_path, customer, phone, 
                        old_bal, new_bal, invoice_date, inv_number, notes, discount
                    )
                    try:
                        if os.name == 'nt':
                            os.startfile(temp_path, "print")
                        elif os.name == 'posix':
                            if os.system(f'lpr "{temp_path}"') != 0:
                                os.system(f'lp "{temp_path}"')
                        messagebox.showinfo("تم", f"تم إرسال الفاتورة إلى الطابعة")
                    except subprocess.CalledProcessError:
                        messagebox.showerror("خطأ", "فشل إرسال الفاتورة للطباعة. تحقق من توفر طابعة.")
                    except Exception as e:
                        messagebox.showerror("خطأ", f"خطأ أثناء الطباعة: {str(e)}")
                finally:
                    try:
                        os.remove(temp_path)
                    except Exception:
                        pass
            else:
                default_filename = f"فاتورة_{inv_number}.pdf"
                path = filedialog.asksaveasfilename(
                    defaultextension=".pdf", 
                    filetypes=[("PDF", "*.pdf")], 
                    initialfile=default_filename,
                    title="حفظ فاتورة كـ PDF"
                )
                if path:
                    generate_invoice_pdf(
                        inv_id, path, customer, phone, 
                        old_bal, new_bal, invoice_date, inv_number, notes, discount
                    )
                    messagebox.showinfo("تم", f"تم حفظ الفاتورة كـ PDF:\n{path}\nسيتم فتح الملف.")
                    try:
                        if os.name == 'nt':
                            os.startfile(path)
                        elif os.name == 'posix':
                            if os.system(f'xdg-open "{path}"') != 0:
                                os.system(f'open "{path}"')
                    except Exception as e:
                        messagebox.showwarning("تحذير", f"تم حفظ الملف لكن فشل فتحه: {str(e)}")
        else:
            messagebox.showinfo("تم", f"تم حفظ الفاتورة برقم {inv_number}")
        cust_ent.delete(0, tk.END)
        phone_ent.delete(0, tk.END)
        paid_ent.delete(0, tk.END)
        paid_ent.insert(0, "0")
        discount_ent.delete(0, tk.END)
        discount_ent.insert(0, "0")
        date_ent.delete(0, tk.END)
        date_ent.insert(0, datetime.now().strftime("%Y-%m-%d"))
        notes_ent.delete(0, tk.END)
        for r in items_tree.get_children():
            items_tree.delete(r)
        update_totals_display()
        self.show_invoices()  # التعديل ده عشان يرجعك لصفحة العرض ويحدثها فورًا
        self.alert_low_stock()

    def show_invoice_details(self, invoice_id, customer_name, phone, old_balance, new_balance, items, invoice_date, invoice_number, notes="", discount=0.0):
        w = tk.Toplevel(self); w.title(f"تفاصيل الفاتورة رقم {invoice_number}"); w.geometry("900x700")
        ttk.Label(w, text=f"رقم الفاتورة: {invoice_number}", font=("Arial", 12, "bold")).pack(pady=5)
        ttk.Label(w, text=f"العميل: {customer_name}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"الهاتف: {phone or ''}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"الرصيد القديم: {old_balance:.2f}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"الرصيد الجديد: {new_balance:.2f}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"التاريخ: {invoice_date}", font=("Arial", 10)).pack()
        if notes:
            ttk.Label(w, text=f"ملاحظات: {notes}", font=("Arial", 10)).pack()
        if discount > 0:
            ttk.Label(w, text=f"الخصم: {discount:.2f}", font=("Arial", 10)).pack()
        cols = ("code","thickness","qty","unit_price","cutting_price","edge_price","line_total","desc")
        tree = ttk.Treeview(w, columns=cols, show="headings", height=12)
        headers = ["كود","سمك","كمية/طول(m)","سعر الوحدة","سعر التقطيع","سعر الشريط","الإجمالي","وصف"]
        for c,h in zip(cols,headers):
            tree.heading(c, text=h); tree.column(c, width=120, anchor=tk.CENTER)
        tree.column("desc", width=200)
        tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for it in items:
            tree.insert("", tk.END, values=(
                it["code"], it["thickness"], it["qty"], 
                f"{it['unit_price']:.2f}", f"{it['cutting_price']:.2f}", 
                f"{it['edge_price']:.2f}", f"{it['line_total']:.2f}",
                it.get("description", "")
            ))
        subtotal = sum(it["line_total"] for it in items)
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT paid, subtotal FROM invoices WHERE id=?", (invoice_id,))
        inv_row = cur.fetchone()
        paid = inv_row["paid"]
        subtotal_after_discount = inv_row["subtotal"]
        c.close()
        ttk.Label(w, text=f"المجموع الفرعي: {subtotal:.2f}", font=("Arial", 10)).pack()
        if discount > 0:
            ttk.Label(w, text=f"الخصم: {discount:.2f}", font=("Arial", 10)).pack()
            ttk.Label(w, text=f"المجموع بعد الخصم: {subtotal_after_discount:.2f}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"المدفوع: {paid:.2f}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"المتبقي للدفع: {subtotal_after_discount - paid:.2f}", font=("Arial", 10)).pack()
        ttk.Label(w, text=f"الإجمالي النهائي (مع الرصيد القديم): {subtotal_after_discount + old_balance:.2f}", font=("Arial", 10)).pack()
        btn_frame = ttk.Frame(w); btn_frame.pack(fill=tk.X, padx=10, pady=10)
        if REPORTLAB:
            ttk.Button(btn_frame, text="🖨️ معاينة الطباعة", command=lambda: PrintPreviewWindow(
                self, invoice_id, customer_name, phone, old_balance, new_balance, 
                items, invoice_date, invoice_number, notes, discount
            ), style="success.TButton").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="💾 حفظ كـ PDF", command=lambda: self.save_as_pdf_invoice(
                invoice_id, customer_name, phone, old_balance, 
                new_balance, invoice_date, invoice_number, notes, discount
            ), style="info.TButton").pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="🖨️ طباعة مباشرة", command=lambda: self.print_direct_invoice(
                invoice_id, customer_name, phone, old_balance, 
                new_balance, invoice_date, invoice_number, notes, discount
            ), style="success.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="إلغاء الفاتورة", command=lambda: self.cancel_invoice(invoice_id), style="danger.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="إغلاق", command=w.destroy, style="primary.TButton").pack(side=tk.RIGHT, padx=5)

    def save_as_pdf_invoice(self, invoice_id, customer_name, phone, old_balance, new_balance, invoice_date, invoice_number, notes, discount):
        default_filename = f"فاتورة_{invoice_number}.pdf"
        path = filedialog.asksaveasfilename(
            defaultextension=".pdf", 
            filetypes=[("PDF", "*.pdf")], 
            initialfile=default_filename,
            title="حفظ فاتورة كـ PDF"
        )
        if path:
            try:
                generate_invoice_pdf(
                    invoice_id, path, customer_name, phone, 
                    old_balance, new_balance, invoice_date, invoice_number, notes, discount
                )
                messagebox.showinfo("تم", f"تم حفظ الفاتورة كـ PDF:\n{path}\nسيتم فتح الملف.")
                try:
                    if os.name == 'nt':
                        os.startfile(path)
                    elif os.name == 'posix':
                        if os.system(f'xdg-open "{path}"') != 0:
                            os.system(f'open "{path}"')
                except Exception as e:
                    messagebox.showwarning("تحذير", f"تم حفظ الملف لكن فشل فتحه: {str(e)}")
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل حفظ الملف: {str(e)}")

    def print_direct_invoice(self, invoice_id, customer_name, phone, old_balance, new_balance, invoice_date, invoice_number, notes, discount):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            temp_path = tmp.name
        try:
            generate_invoice_pdf(
                invoice_id, temp_path, customer_name, phone, 
                old_balance, new_balance, invoice_date, invoice_number, notes, discount
            )
            try:
                if os.name == 'nt':
                    os.startfile(temp_path, "print")
                elif os.name == 'posix':
                    if os.system(f'lpr "{temp_path}"') != 0:
                        os.system(f'lp "{temp_path}"')
                messagebox.showinfo("تم", f"تم إرسال الفاتورة إلى الطابعة")
            except Exception as e:
                messagebox.showerror("خطأ", f"خطأ أثناء الطباعة: {str(e)}")
        finally:
            try:
                os.remove(temp_path)
            except Exception:
                pass

    def cancel_invoice(self, invoice_id):
        if not messagebox.askyesno("تأكيد", "هل أنت متأكد من إلغاء هذه الفاتورة؟ لا يمكن التراجع عن هذه العملية."):
            return
        try:
            cancel_invoice_db(invoice_id)
            messagebox.showinfo("تم", "تم إلغاء الفاتورة بنجاح")
            self.show_invoices()
        except Exception as e:
            messagebox.showerror("خطأ", f"فشل إلغاء الفاتورة: {str(e)}")

    def alert_low_stock(self):
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT code, thickness, quantity, low_stock_threshold FROM products WHERE low_stock_threshold IS NOT NULL AND quantity <= low_stock_threshold")
        lows = cur.fetchall(); c.close()
        if lows:
            s = "\n".join([f"{r['code']} | {r['thickness']} => كمية {r['quantity']}" for r in lows])
            messagebox.showwarning("تنبيه مخزون منخفض", f"المنتجات التالية عندها كمية منخفضة:\n{s}")

    def show_customer_balances(self):
        self.clear()
        top = ttk.Frame(self.container); top.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(top, text="بحث:", font=("Arial", 10)).pack(side=tk.LEFT)
        search_ent = ttk.Entry(top, width=30); search_ent.pack(side=tk.LEFT, padx=6)
        
        def load_balances():
            for row in tree.get_children():
                tree.delete(row)
            c = get_conn(); cur = c.cursor()
            query = "SELECT * FROM customers"
            params = []
            if search_ent.get().strip():
                query += " WHERE name LIKE ?"
                params.append(f"%{search_ent.get().strip()}%")
            cur.execute(query, params)
            for r in cur.fetchall():
                balance = r['balance']
                status = "مدين" if balance > 0 else "دائن" if balance < 0 else "متوازن"
                tree.insert("", tk.END, values=(
                    r['name'], 
                    r['phone'] or "", 
                    f"{balance:.2f}", 
                    status
                ))
            c.close()
        
        ttk.Button(top, text="بحث", command=load_balances).pack(side=tk.LEFT, padx=2)
        
        tree = ttk.Treeview(self.container, columns=("name", "phone", "balance", "status"), show="headings", height=TREE_HEIGHT)
        tree.heading("name", text="اسم العميل")
        tree.heading("phone", text="الهاتف")
        tree.heading("balance", text="الرصيد")
        tree.heading("status", text="الحالة")
        
        tree.column("name", width=200)
        tree.column("phone", width=120)
        tree.column("balance", width=100)
        tree.column("status", width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        load_balances()

    def show_fees_page(self):
        self.clear()
        frm = ttk.Frame(self.container); frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        categories = ["عربية", "كهربة", "ماية", "إيجار", "أخرى"]
        
        ttk.Label(frm, text="نوع الرسوم:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        category_var = tk.StringVar()
        category_cb = ttk.Combobox(frm, textvariable=category_var, values=categories, state="readonly", width=20)
        category_cb.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frm, text="المبلغ:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5)
        amount_ent = ttk.Entry(frm); amount_ent.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(frm, text="الوصف:", font=("Arial", 10)).grid(row=2, column=0, padx=5, pady=5)
        desc_ent = ttk.Entry(frm); desc_ent.grid(row=2, column=1, padx=5, pady=5)
        
        def save_fee():
            category = category_var.get()
            try:
                amount = float(amount_ent.get())
            except:
                messagebox.showerror("خطأ", "أدخل مبلغًا صحيحًا")
                return
                
            description = desc_ent.get().strip()
            
            if not category:
                messagebox.showerror("خطأ", "اختر نوع الرسوم")
                return
                
            # حفظ الرسوم
            c = get_conn(); cur = c.cursor()
            cur.execute("INSERT INTO fees (created_at, amount, category, description) VALUES (?, ?, ?, ?)",
                       (datetime.now().isoformat(), amount, category, description))
            c.commit()
            
            # خصم المبلغ من الكاش
            cur.execute("INSERT INTO cash (created_at, amount, description) VALUES (?, ?, ?)",
                       (datetime.now().isoformat(), -amount, f"رسوم: {category} - {description}"))
            c.commit()
            c.close()
            
            messagebox.showinfo("تم", "تم حفظ الرسوم وخصمها من الكاش")
            amount_ent.delete(0, tk.END)
            desc_ent.delete(0, tk.END)
        
        ttk.Button(frm, text="حفظ الرسوم", command=save_fee, style="success.TButton").grid(row=3, column=0, columnspan=2, pady=10)

    def show_cash_page(self):
        self.clear()
        frm = ttk.Frame(self.container); frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # حساب إجمالي الكاش
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT SUM(amount) as total FROM cash")
        total_cash = cur.fetchone()["total"] or 0.0
        c.close()
        
        ttk.Label(frm, text=f"رصيد الكاش الحالي: {total_cash:.2f} جنيه", font=("Arial", 12, "bold")).pack(pady=10)
        
        # إضافة معاملات جديدة
        add_frm = ttk.LabelFrame(frm, text="إضافة معاملة كاش", padding=10)
        add_frm.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(add_frm, text="المبلغ:", font=("Arial", 10)).grid(row=0, column=0, padx=5, pady=5)
        amount_ent = ttk.Entry(add_frm); amount_ent.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(add_frm, text="الوصف:", font=("Arial", 10)).grid(row=1, column=0, padx=5, pady=5)
        desc_ent = ttk.Entry(add_frm); desc_ent.grid(row=1, column=1, padx=5, pady=5)
        
        def add_cash_transaction():
            try:
                amount = float(amount_ent.get())
            except:
                messagebox.showerror("خطأ", "أدخل مبلغًا صحيحًا")
                return
                
            description = desc_ent.get().strip()
            
            c = get_conn(); cur = c.cursor()
            cur.execute("INSERT INTO cash (created_at, amount, description) VALUES (?, ?, ?)",
                       (datetime.now().isoformat(), amount, description))
            c.commit()
            c.close()
            
            messagebox.showinfo("تم", "تمت إضافة المعاملة بنجاح")
            amount_ent.delete(0, tk.END)
            desc_ent.delete(0, tk.END)
            self.show_cash_page()  # تحديث الصفحة
        
        ttk.Button(add_frm, text="إضافة إيداع", command=lambda: [amount_ent.insert(0, "+"), add_cash_transaction()], 
                  style="success.TButton").grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(add_frm, text="إضافة سحب", command=lambda: [amount_ent.insert(0, "-"), add_cash_transaction()], 
                  style="danger.TButton").grid(row=2, column=1, padx=5, pady=5)
        
        # عرض حركات الكاش
        tree = ttk.Treeview(frm, columns=("date", "amount", "description"), show="headings", height=10)
        tree.heading("date", text="التاريخ")
        tree.heading("amount", text="المبلغ")
        tree.heading("description", text="الوصف")
        
        tree.column("date", width=150)
        tree.column("amount", width=100)
        tree.column("description", width=400)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        c = get_conn(); cur = c.cursor()
        cur.execute("SELECT * FROM cash ORDER BY created_at DESC")
        for r in cur.fetchall():
            tree.insert("", tk.END, values=(
                r['created_at'], 
                f"{r['amount']:.2f}", 
                r['description'] or ""
            ))
        c.close()

    def show_reports(self):
        self.clear()
        frm = ttk.Frame(self.container); frm.pack(fill=tk.X, padx=6, pady=6)
        ttk.Label(frm, text="تقرير أرباح وخسارة", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=6)
        ttk.Label(frm, text="من (YYYY-MM-DD):", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        start_date = ttk.Entry(frm, width=12); start_date.pack(side=tk.LEFT, padx=2)
        ttk.Label(frm, text="إلى (YYYY-MM-DD):", font=("Arial", 10)).pack(side=tk.LEFT, padx=2)
        end_date = ttk.Entry(frm, width=12); end_date.pack(side=tk.LEFT, padx=2)
        ttk.Button(frm, text="🧮 حساب الأرباح", command=lambda: self.do_profit_calc(start_date.get(), end_date.get()), style="primary.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(frm, text="📊 تقرير المبيعات حسب المنتج", command=lambda: self.show_sales_by_product(start_date.get(), end_date.get()), style="primary.TButton").pack(side=tk.LEFT, padx=6)
        ttk.Button(frm, text="📈 عرض الرسم البياني", command=lambda: self.show_profit_chart(start_date.get(), end_date.get()), style="primary.TButton").pack(side=tk.LEFT, padx=6)
        tree = ttk.Treeview(self.container, columns=("number","customer","created","subtotal","paid","remaining"), show="headings", height=12)
        for c,h in zip(("number","customer","created","subtotal","paid","remaining"), ("رقم","عميل","تاريخ","المجموع","مدفوع","متبقي")):
            tree.heading(c, text=h); tree.column(c, width=120, anchor=tk.CENTER)
        tree.column("customer", width=200)
        tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for r in get_invoices(100, start_date.get(), end_date.get()):
            tree.insert("", tk.END, values=(
                r["invoice_number"], r["customer_name"], r["created_at"], 
                f"{r['subtotal']:.2f}", f"{r['paid']:.2f}", 
                f"{float(r['subtotal']) - float(r['paid']):.2f}"
            ))

    def do_profit_calc(self, start_date=None, end_date=None):
        if start_date and end_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح. استخدم YYYY-MM-DD (مثال: 2025-08-11)")
                return
        res = compute_profit_loss(start_date, end_date)
        messagebox.showinfo("نتيجة", f"إجمالي المبيعات: {res['revenue']:.2f}\nإجمالي التكلفة: {res['cost']:.2f}\nالربح: {res['profit']:.2f}")

    def show_sales_by_product(self, start_date=None, end_date=None):
        if start_date and end_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح. استخدم YYYY-MM-DD (مثال: 2025-08-11)")
                return
        w = tk.Toplevel(self); w.title("تقرير المبيعات حسب المنتج"); w.geometry("800x600")
        cols = ("code","thickness","total_qty","total_revenue")
        tree = ttk.Treeview(w, columns=cols, show="headings", height=20)
        headers = ["كود","سمك","إجمالي الكمية","إجمالي المبيعات"]
        for c,h in zip(cols,headers):
            tree.heading(c, text=h); tree.column(c, width=150, anchor=tk.CENTER)
        tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for r in sales_by_product(start_date, end_date):
            tree.insert("", tk.END, values=(r["code"], r["thickness"], r["total_qty"], r["total_revenue"]))

    def show_profit_chart(self, start_date=None, end_date=None):
        if start_date and end_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("خطأ", "تنسيق التاريخ غير صحيح. استخدم YYYY-MM-DD (مثال: 2025-08-11)")
                return
        res = compute_profit_loss(start_date, end_date)
        chart_data = {
            "type": "bar",
            "data": {
                "labels": ["الإيرادات", "التكاليف", "الأرباح"],
                "datasets": [{
                    "label": "القيم",
                    "data": [res["revenue"], res["cost"], res["profit"]],
                    "backgroundColor": ["#36A2EB", "#FF6384", "#4BC0C0"],
                    "borderColor": ["#36A2EB", "#FF6384", "#4BC0C0"],
                    "borderWidth": 1
                }]
            },
            "options": {
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {"display": True, "text": "المبلغ (جنيه)"}
                    },
                    "x": {
                        "title": {"display": True, "text": "الفئة"}
                    }
                },
                "plugins": {
                    "title": {"display": True, "text": "تقرير الأرباح والخسائر"}
                }
            }
        }
        path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML","*.html")])
        if not path: return
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"""
<!DOCTYPE html>
<html>
<head>
    <title>تقرير الأرباح</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <canvas id="profitChart" width="800" height="400"></canvas>
    <script>
        const ctx = document.getElementById('profitChart').getContext('2d');
        new Chart(ctx, {json.dumps(chart_data)});
    </script>
</body>
</html>
""")
        messagebox.showinfo("تم", f"تم حفظ الرسم البياني في: {path}")
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                if os.system(f'xdg-open "{path}"') != 0:
                    os.system(f'open "{path}"')
        except Exception:
            pass

    def show_activity(self):
        self.clear()
        tree = ttk.Treeview(self.container, columns=("time","action"), show="headings", height=20)
        tree.heading("time", text="الوقت"); tree.heading("action", text="الإجراء")
        tree.column("time", width=220); tree.column("action", width=760)
        tree.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
        for r in get_activity(200):
            tree.insert("", tk.END, values=(r["created_at"], r["action"]))

    def show_receive_payment(self):
        self.clear()
        frm = ttk.Frame(self.container); frm.pack(fill=tk.X, padx=10, pady=10)
        ttk.Label(frm, text="اسم العميل:", font=("Arial", 10)).grid(row=0, column=0, sticky=tk.E, padx=4, pady=4)
        name_ent = ttk.Entry(frm, width=30); name_ent.grid(row=0, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(frm, text="الهاتف:", font=("Arial", 10)).grid(row=0, column=2, sticky=tk.E, padx=4, pady=4)
        phone_ent = ttk.Entry(frm, width=16); phone_ent.grid(row=0, column=3, sticky=tk.W, padx=4, pady=4)
        bal_lbl = ttk.Label(frm, text="رصيد: 0.00", font=("Arial", 10)); bal_lbl.grid(row=1, column=1, sticky=tk.W, padx=4, pady=4)
        def fetch():
            n = name_ent.get().strip()
            if not n:
                bal_lbl.config(text="رصيد: 0.00"); return
            c = get_customer_by_name(n)
            if c:
                bal_lbl.config(text=f"رصيد: {c['balance']:.2f}")
                phone_ent.delete(0,tk.END); phone_ent.insert(0, c["phone"] or "")
            else:
                bal_lbl.config(text="رصيد: 0.00 (عميل جديد)")
        ttk.Button(frm, text="🔍 جلب الرصيد", command=fetch, style="primary.TButton").pack(side=tk.LEFT, padx=4)
        ttk.Label(frm, text="مبلغ السداد:", font=("Arial", 10)).grid(row=2, column=0, sticky=tk.E, padx=4, pady=4)
        amt_ent = ttk.Entry(frm, width=12); amt_ent.grid(row=2, column=1, sticky=tk.W, padx=4, pady=4)
        ttk.Label(frm, text="ملاحظات:", font=("Arial", 10)).grid(row=2, column=2, sticky=tk.E, padx=4, pady=4)
        note_ent = ttk.Entry(frm, width=30); note_ent.grid(row=2, column=3, sticky=tk.W, padx=4, pady=4)
        def submit():
            name = name_ent.get().strip()
            phone = phone_ent.get().strip()
            if not name:
                messagebox.showerror("خطأ", "أدخل اسم العميل"); return
            try:
                amt = float(amt_ent.get())
                if amt <= 0:
                    raise ValueError()
            except:
                messagebox.showerror("خطأ", "أدخل مبلغ سداد صحيح (>0)"); return
            # استخدم منطق إنشاء الفاتورة لتحديث رصيد العميل بشكل صحيح
            today = datetime.now().strftime("%Y-%m-%d")
            try:
                inv_id, old_bal, new_bal, inv_num = create_invoice_db(
                    customer_name=name,
                    phone=phone,
                    items=[],
                    paid=amt,
                    invoice_date=today,
                    notes=f"سداد: {note_ent.get().strip()}"
                )
                log_action(f"سداد من العميل {name}: {amt:.2f} | الرصيد السابق={old_bal:.2f} الرصيد الجديد={new_bal:.2f}")
                messagebox.showinfo("تم", f"تم تسجيل السداد برقم {inv_num}.\nالرصيد السابق: {old_bal:.2f}\nالرصيد الجديد: {new_bal:.2f}")
                self.show_invoices()
            except Exception as e:
                messagebox.showerror("خطأ", f"فشل تسجيل السداد: {e}")
        ttk.Button(frm, text="💵 سداد", command=submit, style="success.TButton").pack(side=tk.LEFT, padx=4)

    def export_csv_menu(self):
        w = tk.Toplevel(self); w.title("تصدير CSV"); w.geometry("300x200")
        ttk.Label(w, text="اختر ما تريد تصديره:", font=("Arial", 12)).pack(padx=6, pady=6)
        def export_invoices():
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if not path: return
            rows = get_invoices(1000)
            with open(path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["invoice_number","customer","phone","created_at","subtotal","paid","balance"])
                for r in rows:
                    writer.writerow([r["invoice_number"], r["customer_name"], r["phone"] or "", r["created_at"], r["subtotal"], r["paid"], r["balance"]])
            messagebox.showinfo("تم", f"تم تصدير الفواتير إلى {path}")
            w.destroy()
        def export_products():
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV","*.csv")])
            if not path: return
            rows = search_products()
            with open(path, "w", newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["id","code","thickness","price","cost","quantity","type","edge_length","description"])
                for r in rows:
                    writer.writerow([r["id"],r["code"],r["thickness"],r["price"],r["cost"],r["quantity"],r["type"],r["edge_length"],r["description"]])
            messagebox.showinfo("تم", f"تم تصدير المخزن إلى {path}")
            w.destroy()
        ttk.Button(w, text="تصدير الفواتير", command=export_invoices, style="primary.TButton").pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(w, text="تصدير المخزن", command=export_products, style="primary.TButton").pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(w, text="إغلاق", command=w.destroy, style="danger.TButton").pack(pady=6)

def main():
    # شاشة تسجيل دخول اختيارية
    ensure_tables_and_columns()
    s = get_settings_row()
    if s and (s["login_required"] or 0):
        root = tk.Tk(); root.withdraw()
        for _ in range(3):
            pwd = simpledialog.askstring("تسجيل الدخول", "أدخل كلمة المرور:", show="*")
            if pwd is None:
                return
            if verify_password("admin", pwd):
                break
            messagebox.showerror("خطأ", "كلمة المرور غير صحيحة")
        else:
            return
        root.destroy()
    app = StoreApp()
    c = get_conn(); cur = c.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM products"); cnt = cur.fetchone()["cnt"]; c.close()
    if cnt == 0:
        messagebox.showinfo("جاهز", "قاعدة البيانات جاهزة. يمكنك الآن إضافة منتجات.")
    app.alert_low_stock()
    app.mainloop()

if __name__ == "__main__":
    main()