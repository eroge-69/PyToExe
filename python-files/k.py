from flask import Flask, render_template_string, request, redirect, url_for, session, flash, send_file
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta
import io
import pdfkit
import qrcode
import base64

app = Flask(__name__)
app.secret_key = 'secret-key-قوي-غَيِّر-هذا'

DB_NAME = 'billing_system.db'

COMPANY_INFO = {
    "name": "شركة عاصمة الكابلات",
    "vat_number": "311239237800003",
    "address": "الرياض حي الملز شارع الامير عبد المحسن بن عبدالعزيز",
    "phone": "0123456789",
    "fax": "",
    "mobile": "0561788277",
    "email": "",
    "bank_name": "Alinma Bank",
    "bank_account": "SA0205000068204387584000",
    "cr_number": "1010627317"
}

VAT_RATE = 0.15  # 15%

base_html = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8" />
<title>{{ title if title else "نظام الفواتير" }}</title>
<style>
  body { font-family: Arial, sans-serif; background: #f9fbff; color: #2c3e50; direction: rtl; margin:0; padding:0;}
  header { background:#34495e; padding:20px 40px; color:#fff; display:flex; justify-content:space-between; flex-wrap:wrap;}
  header h1 { margin:0; font-weight:bold;}
  nav a { margin-left:25px; color:#fff; text-decoration:none; font-weight:600;}
  nav a:hover { text-decoration:underline;}
  .container { max-width:1100px; margin:30px auto; padding:20px; background:#fff; border-radius:12px; box-shadow:0 0 18px rgba(0,0,0,0.07);}
  h1,h2,h3 { color:#34495e; margin-bottom:20px;}
  button, .btn { background:#2c3e50; border:none; color:#fff; padding:14px 25px; font-size:16px; border-radius:12px; cursor:pointer; transition:background-color 0.3s ease;}
  button:hover, .btn:hover { background:#1a252f;}
  input, select, textarea { width:100%; padding:12px 15px; margin:8px 0 18px 0; border:1px solid #ccd1d9; border-radius:12px; font-size:16px; box-sizing:border-box; transition:border-color 0.3s ease;}
  input:focus, select:focus, textarea:focus { border-color:#2980b9; outline:none;}
  table { width:100%; border-collapse:collapse; border-radius:12px; overflow:hidden; box-shadow:0 0 15px rgba(0,0,0,0.05);}
  th, td { text-align:center; padding:14px 10px; border-bottom:1px solid #ecf0f1;}
  th { background:#2980b9; color:#fff;}
  tbody tr:hover { background:#f2f6fc;}
  a { color:#2980b9; text-decoration:none; font-weight:600;}
  a:hover { text-decoration:underline;}
  .alert { padding:14px 20px; margin-bottom:25px; border-radius:12px; font-weight:600; box-shadow:0 0 8px rgba(0,0,0,0.05);}
  .alert-success { background:#d4edda; color:#155724;}
  .alert-danger { background:#f8d7da; color:#721c24;}
  .alert-warning { background:#fff3cd; color:#856404;}
  footer { text-align:center; padding:20px 0; color:#777; margin-top:40px; border-top:1px solid #eee; font-size:14px;}

  .dashboard-cards {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    margin-top: 30px;
  }
  .card {
    background: #fff;
    flex: 1 1 220px;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    transition: box-shadow 0.3s ease;
  }
  .card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,0.15);
  }
  .card h3 {
    margin-top: 0;
    font-size: 20px;
    color: #34495e;
  }
  .card p {
    font-size: 32px;
    margin: 15px 0 0 0;
    font-weight: 700;
    color: #2980b9;
  }
  .btn-dashboard {
    margin-top: 20px;
    background-color: #2980b9;
    padding: 14px 30px;
    border-radius: 12px;
    text-decoration: none;
    color: white;
    font-weight: 600;
    display: inline-block;
    transition: background-color 0.3s ease;
  }
  .btn-dashboard:hover {
    background-color: #1f5c8b;
  }
  @media (max-width:720px) {
    header { flex-direction: column; text-align: center;}
    nav a { margin: 10px; display: inline-block;}
    .dashboard-cards { flex-direction: column;}
  }
</style>
</head>
<body>
<header>
  <h1>{{ company_name }}</h1>
  <nav>
    {% if session.get('user_id') %}
      <a href="{{ url_for('dashboard') }}">لوحة التحكم</a>
      <a href="{{ url_for('products') }}">المنتجات</a>
      <a href="{{ url_for('invoices') }}">المبيعات</a>
      <a href="{{ url_for('list_quotes') }}">عروض السعر</a>
      <a href="{{ url_for('customers') }}">العملاء</a>
      <a href="{{ url_for('logout') }}">تسجيل خروج</a>
    {% else %}
      <a href="{{ url_for('login') }}">تسجيل دخول</a>
      <a href="{{ url_for('register') }}">تسجيل حساب</a>
    {% endif %}
  </nav>
</header>
<div class="container">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for category, message in messages %}
        <div class="alert alert-{{ category }}">{{ message }}</div>
      {% endfor %}
    {% endif %}
  {% endwith %}
  {{ content | safe }}
</div>
<footer>
  جميع الحقوق محفوظة &copy; شركة عاصمة الكابلات 2025
</footer>
</body>
</html>
"""

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    # Users
    cur.execute('''
      CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        salt TEXT NOT NULL
      )
    ''')
    # Products linked to user
    cur.execute('''
      CREATE TABLE IF NOT EXISTS products (
        item_code TEXT PRIMARY KEY,
        item_desc TEXT,
        unit TEXT,
        cost_price REAL,
        unit_price REAL,
        quantity INTEGER,
        vat_active INTEGER DEFAULT 0,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    ''')
    # Customers linked to user
    cur.execute('''
      CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        address TEXT,
        user_id INTEGER NOT NULL,
        UNIQUE(name, user_id),
        FOREIGN KEY(user_id) REFERENCES users(id)
      )
    ''')
    # Invoices linked to user
    cur.execute('''
      CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        payment_method TEXT,
        notes TEXT,
        total REAL,
        vat_amount REAL,
        vat_rate REAL,
        vat_no TEXT,
        company_name TEXT,
        company_address TEXT,
        company_phone TEXT,
        invoice_date TEXT,
        due_date TEXT,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
      )
    ''')
    # Invoice items
    cur.execute('''
      CREATE TABLE IF NOT EXISTS invoice_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        invoice_id INTEGER,
        item_code TEXT,
        item_desc TEXT,
        unit TEXT,
        quantity INTEGER,
        unit_price REAL,
        total REAL,
        vat_active INTEGER,
        vat_amount REAL,
        FOREIGN KEY(invoice_id) REFERENCES invoices(id)
      )
    ''')
    # Quotes linked to user
    cur.execute('''
      CREATE TABLE IF NOT EXISTS quotes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        description TEXT,
        delivery_date TEXT,
        expiration_date TEXT,
        due_date TEXT,
        amount REAL,
        vat_amount REAL,
        total REAL,
        vat_rate REAL,
        user_id INTEGER NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(customer_id) REFERENCES customers(id)
      )
    ''')
    conn.commit()
    conn.close()

@app.before_request
def before_request():
    if not hasattr(app, 'db_initialized'):
        init_db()
        app.db_initialized = True

@app.route('/')
def index():
    if session.get('user_id'):
        return redirect(url_for('dashboard'))
    else:
        return redirect(url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        if len(password) < 6:
            flash('كلمة المرور يجب أن تكون 6 أحرف على الأقل', 'warning')
            return redirect(url_for('register'))
        salt = os.urandom(16).hex()
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (username, password, salt) VALUES (?, ?, ?)", (username, hashed, salt))
            conn.commit()
            conn.close()
            flash('تم تسجيل الحساب بنجاح!', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('اسم المستخدم موجود مسبقاً!', 'danger')
            return redirect(url_for('register'))

    content = """
    <h2>تسجيل حساب جديد</h2>
    <form method="POST">
      <label>اسم المستخدم</label>
      <input type="text" name="username" required />
      <label>كلمة المرور</label>
      <input type="password" name="password" required minlength="6" />
      <button type="submit">تسجيل</button>
    </form>
    <p>هل لديك حساب؟ <a href="{{ url_for('login') }}">تسجيل دخول</a></p>
    """
    return render_template_string(base_html, title="تسجيل حساب", company_name=COMPANY_INFO['name'], content=content)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password')
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user:
            hashed_input = hashlib.sha256((password + user['salt']).encode()).hexdigest()
            if hashed_input == user['password']:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['login_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                flash('تم تسجيل الدخول بنجاح!', 'success')
                return redirect(url_for('dashboard'))
        flash('بيانات الدخول غير صحيحة!', 'danger')

    content = """
    <h2>تسجيل الدخول</h2>
    <form method="POST">
      <label>اسم المستخدم</label>
      <input type="text" name="username" required />
      <label>كلمة المرور</label>
      <input type="password" name="password" required />
      <button type="submit">دخول</button>
    </form>
    <p>ليس لديك حساب؟ <a href="{{ url_for('register') }}">سجل هنا</a></p>
    """
    return render_template_string(base_html, title="تسجيل الدخول", company_name=COMPANY_INFO['name'], content=content)

@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    conn = get_db_connection()
    user_id = session.get('user_id')
    product_count = conn.execute("SELECT COUNT(*) FROM products WHERE user_id = ?", (user_id,)).fetchone()[0]
    invoice_count = conn.execute("SELECT COUNT(*) FROM invoices WHERE user_id = ?", (user_id,)).fetchone()[0]
    quote_count = conn.execute("SELECT COUNT(*) FROM quotes WHERE user_id = ?", (user_id,)).fetchone()[0]
    customer_count = conn.execute("SELECT COUNT(*) FROM customers WHERE user_id = ?", (user_id,)).fetchone()[0]
    conn.close()

    content = f"""
    <h2>لوحة التحكم</h2>
    <div class="dashboard-cards">
      <div class="card">
        <h3>مرحباً، {session.get('username')}</h3>
        <small>اسم المستخدم</small>
      </div>
      <div class="card">
        <h3>{COMPANY_INFO['name']}</h3>
        <small>اسم الشركة</small>
      </div>
      <div class="card">
        <h3>{COMPANY_INFO['vat_number']}</h3>
        <small>الرقم الضريبي</small>
      </div>
      <div class="card">
        <h3>{session.get('login_time')}</h3>
        <small>وقت الدخول</small>
      </div>
      <div class="card">
        <h3>{product_count}</h3>
        <small>عدد المنتجات</small>
      </div>
      <div class="card">
        <h3>{invoice_count}</h3>
        <small>عدد الفواتير</small>
      </div>
      <div class="card">
        <h3>{quote_count}</h3>
        <small>عدد عروض السعر</small>
      </div>
      <div class="card">
        <h3>{customer_count}</h3>
        <small>عدد العملاء</small>
      </div>
    </div>
    <div style="margin-top:30px;">
      <a href="{url_for('products')}" class="btn-dashboard">المنتجات</a>
      <a href="{url_for('invoices')}" class="btn-dashboard">المبيعات</a>
      <a href="{url_for('list_quotes')}" class="btn-dashboard">عروض السعر</a>
      <a href="{url_for('customers')}" class="btn-dashboard">العملاء</a>
    </div>
    """
    return render_template_string(base_html, title="لوحة التحكم", company_name=COMPANY_INFO['name'], content=content)

# المنتجات: عرض، إضافة، تعديل، حذف
@app.route('/products', methods=['GET','POST'])
def products():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    if request.method == 'POST':
        item_code = request.form.get('item_code').strip()
        item_desc = request.form.get('item_desc').strip()
        unit = request.form.get('unit').strip()
        try:
            cost_price = float(request.form.get('cost_price'))
            unit_price = float(request.form.get('unit_price'))
            quantity = int(request.form.get('quantity'))
            vat_active = 1 if request.form.get('vat_active') == 'on' else 0
        except:
            flash('الرجاء إدخال قيم صحيحة', 'danger')
            return redirect(url_for('products'))
        try:
            conn.execute("INSERT INTO products (item_code, item_desc, unit, cost_price, unit_price, quantity, vat_active, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                         (item_code, item_desc, unit, cost_price, unit_price, quantity, vat_active, user_id))
            conn.commit()
            flash('تم إضافة المنتج بنجاح!', 'success')
        except sqlite3.IntegrityError:
            flash('رمز الصنف موجود مسبقاً!', 'danger')
        return redirect(url_for('products'))

    products = conn.execute("SELECT * FROM products WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()

    product_rows = ""
    for p in products:
        product_rows += f"""
        <tr>
          <td>{p['item_code']}</td>
          <td>{p['item_desc']}</td>
          <td>{p['unit']}</td>
          <td>{p['cost_price']:.2f}</td>
          <td>{p['unit_price']:.2f}</td>
          <td>{p['quantity']}</td>
          <td>{'نعم' if p['vat_active'] == 1 else 'لا'}</td>
          <td>
            <a href="{url_for('edit_product', item_code=p['item_code'])}">تعديل</a> |
            <a href="{url_for('delete_product', item_code=p['item_code'])}" onclick="return confirm('هل أنت متأكد من حذف المنتج؟')">حذف</a>
          </td>
        </tr>
        """

    content = f"""
    <h2>المنتجات</h2>
    <table>
      <thead>
        <tr><th>رمز الصنف</th><th>المنتج</th><th>الوحدة</th><th>تكلفة الوحدة</th><th>سعر البيع</th><th>الكمية</th><th>تفعيل الضريبة 15%</th><th>العمليات</th></tr>
      </thead>
      <tbody>
        {product_rows}
      </tbody>
    </table>

    <h3>إضافة منتج جديد</h3>
    <form method="POST">
      <label>رمز الصنف</label><input type="text" name="item_code" required />
      <label>المنتج</label><input type="text" name="item_desc" required />
      <label>الوحدة</label><input type="text" name="unit" required />
      <label>تكلفة الوحدة</label><input type="number" step="0.01" name="cost_price" required />
      <label>سعر البيع</label><input type="number" step="0.01" name="unit_price" required />
      <label>الكمية</label><input type="number" name="quantity" required />
      <label>تفعيل الضريبة 15%</label>
      <input type="checkbox" name="vat_active" />
      <button type="submit">إضافة</button>
    </form>
    """
    return render_template_string(base_html, title="المنتجات", company_name=COMPANY_INFO['name'], content=content)

@app.route('/products/edit/<item_code>', methods=['GET','POST'])
def edit_product(item_code):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    product = conn.execute("SELECT * FROM products WHERE item_code = ? AND user_id = ?", (item_code, user_id)).fetchone()
    if not product:
        flash('المنتج غير موجود', 'danger')
        conn.close()
        return redirect(url_for('products'))
    if request.method == 'POST':
        item_desc = request.form.get('item_desc').strip()
        unit = request.form.get('unit').strip()
        try:
            cost_price = float(request.form.get('cost_price'))
            unit_price = float(request.form.get('unit_price'))
            quantity = int(request.form.get('quantity'))
            vat_active = 1 if request.form.get('vat_active') == 'on' else 0
        except:
            flash('الرجاء إدخال قيم صحيحة', 'danger')
            return redirect(url_for('edit_product', item_code=item_code))
        conn.execute('''
          UPDATE products SET item_desc=?, unit=?, cost_price=?, unit_price=?, quantity=?, vat_active=? WHERE item_code=? AND user_id=?
        ''', (item_desc, unit, cost_price, unit_price, quantity, vat_active, item_code, user_id))
        conn.commit()
        conn.close()
        flash('تم تعديل المنتج بنجاح!', 'success')
        return redirect(url_for('products'))
    conn.close()

    checked = "checked" if product['vat_active'] == 1 else ""
    content = f"""
    <h2>تعديل المنتج {product['item_code']}</h2>
    <form method="POST">
      <label>المنتج</label>
      <input type="text" name="item_desc" value="{product['item_desc']}" required />
      <label>الوحدة</label>
      <input type="text" name="unit" value="{product['unit']}" required />
      <label>تكلفة الوحدة</label>
      <input type="number" step="0.01" name="cost_price" value="{product['cost_price']}" required />
      <label>سعر البيع</label>
      <input type="number" step="0.01" name="unit_price" value="{product['unit_price']}" required />
      <label>الكمية</label>
      <input type="number" name="quantity" value="{product['quantity']}" required />
      <label>تفعيل الضريبة 15%</label>
      <input type="checkbox" name="vat_active" {checked} />
      <button type="submit">حفظ التعديلات</button>
    </form>
    """
    return render_template_string(base_html, title="تعديل المنتج", company_name=COMPANY_INFO['name'], content=content)

@app.route('/products/delete/<item_code>')
def delete_product(item_code):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    conn.execute("DELETE FROM products WHERE item_code = ? AND user_id = ?", (item_code, user_id))
    conn.commit()
    conn.close()
    flash('تم حذف المنتج بنجاح', 'success')
    return redirect(url_for('products'))

# العملاء: عرض، إضافة، تعديل، حذف
@app.route('/customers')
def customers():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    rows = ""
    for c in customers:
        rows += f"""
        <tr>
          <td>{c['id']}</td>
          <td>{c['name']}</td>
          <td>{c['phone'] if c['phone'] else ''}</td>
          <td>{c['address'] if c['address'] else ''}</td>
          <td>
            <a href="{url_for('edit_customer', customer_id=c['id'])}">تعديل</a> |
            <a href="{url_for('delete_customer', customer_id=c['id'])}" onclick="return confirm('هل أنت متأكد من حذف العميل؟')">حذف</a>
          </td>
        </tr>
        """
    content = f"""
    <h2>العملاء</h2>
    <a href="{url_for('add_customer')}" class="btn">إضافة عميل جديد</a>
    <table>
      <thead>
        <tr><th>رقم</th><th>اسم العميل</th><th>الهاتف</th><th>العنوان</th><th>العمليات</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    """
    return render_template_string(base_html, title="العملاء", company_name=COMPANY_INFO['name'], content=content)

@app.route('/customers/add', methods=['GET','POST'])
def add_customer():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone = request.form.get('phone')
        address = request.form.get('address')
        conn = get_db_connection()
        try:
            conn.execute("INSERT INTO customers (name, phone, address, user_id) VALUES (?, ?, ?, ?)", (name, phone, address, user_id))
            conn.commit()
            flash('تم إضافة العميل بنجاح!', 'success')
            conn.close()
            return redirect(url_for('customers'))
        except sqlite3.IntegrityError:
            flash('اسم العميل موجود مسبقاً!', 'danger')
            conn.close()
            return redirect(url_for('add_customer'))
    content = """
    <h2>إضافة عميل جديد</h2>
    <form method="POST">
      <label>اسم العميل</label>
      <input type="text" name="name" required />
      <label>هاتف العميل</label>
      <input type="text" name="phone" />
      <label>عنوان العميل</label>
      <input type="text" name="address" />
      <button type="submit">إضافة</button>
    </form>
    """
    return render_template_string(base_html, title="إضافة عميل", company_name=COMPANY_INFO['name'], content=content)

@app.route('/customers/edit/<int:customer_id>', methods=['GET','POST'])
def edit_customer(customer_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    customer = conn.execute("SELECT * FROM customers WHERE id = ? AND user_id = ?", (customer_id, user_id)).fetchone()
    if not customer:
        flash('العميل غير موجود', 'danger')
        conn.close()
        return redirect(url_for('customers'))
    if request.method == 'POST':
        name = request.form.get('name').strip()
        phone = request.form.get('phone')
        address = request.form.get('address')
        try:
            conn.execute("UPDATE customers SET name = ?, phone = ?, address = ? WHERE id = ? AND user_id = ?", (name, phone, address, customer_id, user_id))
            conn.commit()
            flash('تم تعديل بيانات العميل بنجاح!', 'success')
            conn.close()
            return redirect(url_for('customers'))
        except sqlite3.IntegrityError:
            flash('اسم العميل موجود مسبقاً!', 'danger')
            conn.close()
            return redirect(url_for('edit_customer', customer_id=customer_id))
    conn.close()
    content = f"""
    <h2>تعديل بيانات العميل</h2>
    <form method="POST">
      <label>اسم العميل</label>
      <input type="text" name="name" value="{customer['name']}" required />
      <label>هاتف العميل</label>
      <input type="text" name="phone" value="{customer['phone'] if customer['phone'] else ''}" />
      <label>عنوان العميل</label>
      <input type="text" name="address" value="{customer['address'] if customer['address'] else ''}" />
      <button type="submit">تعديل</button>
    </form>
    """
    return render_template_string(base_html, title="تعديل العميل", company_name=COMPANY_INFO['name'], content=content)

@app.route('/customers/delete/<int:customer_id>')
def delete_customer(customer_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    conn.execute("DELETE FROM customers WHERE id = ? AND user_id = ?", (customer_id, user_id))
    conn.commit()
    conn.close()
    flash('تم حذف العميل بنجاح', 'success')
    return redirect(url_for('customers'))

# الفواتير: عرض، إنشاء، تفاصيل، حذف (زر الحذف اسمه "تصدير PNG" لكنه يحذف الفاتورة)
@app.route('/invoices')
def invoices():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    invoices = conn.execute('''
        SELECT invoices.*, customers.name as customer_name
        FROM invoices LEFT JOIN customers ON invoices.customer_id = customers.id
        WHERE invoices.user_id = ?
        ORDER BY invoice_date DESC
    ''', (user_id,)).fetchall()
    conn.close()
    rows = ""
    for inv in invoices:
        cust_name = inv['customer_name'] if inv['customer_name'] else '---'
        rows += f"""
        <tr>
          <td>{inv['id']}</td>
          <td>{cust_name}</td>
          <td>{inv['invoice_date']}</td>
          <td>{inv['due_date']}</td>
          <td><a href="{url_for('invoice_details', invoice_id=inv['id'])}">تفاصيل</a></td>
          <td><a href="{url_for('export_invoice_pdf', invoice_id=inv['id'])}">تصدير PDF</a></td>
          <td><a href="{url_for('delete_invoice', invoice_id=inv['id'])}" onclick="return confirm('هل أنت متأكد من تصدير الفاتورة PNG')">تصدير PNG</a></td>
        </tr>
        """
    content = f"""
    <h2>المبيعات - الفواتير</h2>
    <a href="{url_for('new_invoice')}" class="btn">إنشاء فاتورة جديدة</a>
    <table>
      <thead>
        <tr><th>رقم الفاتورة</th><th>العميل</th><th>تاريخ الفاتورة</th><th>تاريخ الاستحقاق</th><th>التفاصيل</th><th>تصدير PDF</th><th>تصدير PNG</th></tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    """
    return render_template_string(base_html, title="المبيعات", company_name=COMPANY_INFO['name'], content=content)

@app.route('/new_invoice', methods=['GET', 'POST'])
def new_invoice():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    products = conn.execute("SELECT * FROM products WHERE user_id = ?", (user_id,)).fetchall()
    customers = conn.execute("SELECT * FROM customers WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        payment_method = request.form.get('payment_method')
        notes = request.form.get('notes')
        company_name = request.form.get('company_name')
        company_address = request.form.get('company_address')
        company_phone = request.form.get('company_phone')
        vat_no = request.form.get('vat_no')
        invoice_date = request.form.get('invoice_date')
        due_date = request.form.get('due_date')
        items = []
        total = 0
        total_vat = 0
        for p in products:
            qty_str = request.form.get(f"quantity_{p['item_code']}")
            try:
                qty = int(qty_str) if qty_str else 0
            except:
                qty = 0
            if qty > 0:
                item_total = qty * p['unit_price']
                vat_amount = item_total * VAT_RATE if p['vat_active'] == 1 else 0
                total += item_total
                total_vat += vat_amount
                items.append({
                    'item_code': p['item_code'],
                    'item_desc': p['item_desc'],
                    'unit': p['unit'],
                    'quantity': qty,
                    'unit_price': p['unit_price'],
                    'total': item_total,
                    'vat_active': p['vat_active'],
                    'vat_amount': vat_amount
                })
        grand_total = total + total_vat
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('''
          INSERT INTO invoices (
            customer_id, payment_method, notes,
            total, vat_amount, vat_rate, vat_no,
            company_name, company_address, company_phone,
            invoice_date, due_date, user_id)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            customer_id, payment_method, notes,
            grand_total, total_vat, VAT_RATE, vat_no,
            company_name, company_address, company_phone,
            invoice_date, due_date, user_id
        ))
        invoice_id = cur.lastrowid
        for item in items:
            cur.execute('''
              INSERT INTO invoice_items (invoice_id, item_code, item_desc, unit, quantity, unit_price, total, vat_active, vat_amount)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice_id,
                item['item_code'],
                item['item_desc'],
                item['unit'],
                item['quantity'],
                item['unit_price'],
                item['total'],
                item['vat_active'],
                item['vat_amount']
            ))
        conn.commit()
        conn.close()
        flash('تم حفظ الفاتورة بنجاح!', 'success')
        return redirect(url_for('invoices'))
    invoice_date = datetime.now().strftime('%Y-%m-%d')
    due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
    products_html = ""
    for p in products:
        vat_text = "نعم" if p['vat_active'] == 1 else "لا"
        products_html += f"""
        <tr>
          <td>{p['item_code']}</td>
          <td>{p['item_desc']}</td>
          <td>{p['unit']}</td>
          <td>{p['unit_price']:.2f}</td>
          <td>{vat_text}</td>
          <td><input type="number" min="0" name="quantity_{p['item_code']}" value="0" /></td>
        </tr>
        """
    customers_options = "<option value=''>---</option>"
    for c in customers:
        customers_options += f"<option value='{c['id']}'>{c['name']}</option>"
    content = f"""
    <h2>إنشاء فاتورة جديدة</h2>
    <form method="POST">
      <label>اسم العميل</label>
      <select name="customer_id" required>
        {customers_options}
      </select>
      <label>طريقة الدفع</label>
      <select name="payment_method">
        <option>نقداً</option>
        <option>بطاقة ائتمان</option>
        <option>تحويل بنكي</option>
      </select>
      <label>ملاحظات</label><textarea name="notes"></textarea>
      <label>اسم الشركة</label><input type="text" name="company_name" value="{COMPANY_INFO['name']}" />
      <label>عنوان الشركة</label><input type="text" name="company_address" value="{COMPANY_INFO['address']}" />
      <label>هاتف الشركة</label><input type="text" name="company_phone" value="{COMPANY_INFO['phone']}" />
      <label>الرقم الضريبي</label><input type="text" name="vat_no" value="{COMPANY_INFO['vat_number']}" />
      <label>تاريخ الفاتورة</label><input type="date" name="invoice_date" value="{invoice_date}" />
      <label>تاريخ الاستحقاق</label><input type="date" name="due_date" value="{due_date}" />
      <h3>اختيار المنتجات</h3>
      <table>
        <thead>
          <tr><th>رمز الصنف</th><th>المنتج</th><th>الوحدة</th><th>سعر الوحدة</th><th>الضريبة 15%</th><th>الكمية</th></tr>
        </thead>
        <tbody>
          {products_html}
        </tbody>
      </table>
      <button type="submit">حفظ الفاتورة</button>
    </form>
    <p><a href="{url_for('invoices')}">عرض جميع الفواتير</a></p>
    """
    return render_template_string(base_html, title="إنشاء فاتورة جديدة", company_name=COMPANY_INFO['name'], content=content)

@app.route('/invoice/<int:invoice_id>')
def invoice_details(invoice_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    invoice = conn.execute('''
        SELECT invoices.*, customers.name as customer_name, customers.phone as customer_phone, customers.address as customer_address
        FROM invoices LEFT JOIN customers ON invoices.customer_id = customers.id
        WHERE invoices.id = ? AND invoices.user_id = ?
    ''', (invoice_id, user_id)).fetchone()
    if not invoice:
        flash('الفاتورة غير موجودة', 'danger')
        conn.close()
        return redirect(url_for('invoices'))
    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,)).fetchall()
    conn.close()
    items_html = ""
    for item in items:
        vat_text = "نعم" if item['vat_active'] == 1 else "لا"
        items_html += f"""
        <tr>
          <td>{item['item_code']}</td>
          <td>{item['item_desc']}</td>
          <td>{item['unit']}</td>
          <td>{item['quantity']}</td>
          <td>{item['unit_price']:.2f}</td>
          <td>{item['total']:.2f}</td>
          <td>{vat_text}</td>
          <td>{item['vat_amount']:.2f}</td>
        </tr>
        """
    cust_name = invoice['customer_name'] if invoice['customer_name'] else '---'
    content = f"""
    <h2>تفاصيل الفاتورة رقم {invoice['id']}</h2>
    <p><strong>اسم العميل:</strong> {cust_name}</p>
    <p><strong>هاتف العميل:</strong> {invoice['customer_phone'] if invoice['customer_phone'] else '---'}</p>
    <p><strong>عنوان العميل:</strong> {invoice['customer_address'] if invoice['customer_address'] else '---'}</p>
    <p><strong>طريقة الدفع:</strong> {invoice['payment_method']}</p>
    <p><strong>ملاحظات:</strong> {invoice['notes']}</p>
    <p><strong>إجمالي الفاتورة:</strong> {invoice['total']:.2f} ريال</p>
    <p><strong>إجمالي الضريبة:</strong> {invoice['vat_amount']:.2f} ريال</p>
    <p><strong>اسم الشركة:</strong> {invoice['company_name']}</p>
    <p><strong>عنوان الشركة:</strong> {invoice['company_address']}</p>
    <p><strong>هاتف الشركة:</strong> {invoice['company_phone']}</p>
    <p><strong>تاريخ الفاتورة:</strong> {invoice['invoice_date']}</p>
    <p><strong>تاريخ الاستحقاق:</strong> {invoice['due_date']}</p>
    <h3>عناصر الفاتورة</h3>
    <table>
      <thead>
        <tr>
          <th>رمز الصنف</th><th>المنتج</th><th>الوحدة</th><th>الكمية</th><th>سعر الوحدة</th><th>الإجمالي</th><th>ضريبة 15%</th><th>مقدار الضريبة</th>
        </tr>
      </thead>
      <tbody>
        {items_html}
      </tbody>
    </table>
    <p><a href="{url_for('invoices')}">عودة للفواتير</a></p>
    """
    return render_template_string(base_html, title=f"تفاصيل الفاتورة {invoice['id']}", company_name=COMPANY_INFO['name'], content=content)

@app.route('/invoices/delete/<int:invoice_id>')
def delete_invoice(invoice_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    conn.execute("DELETE FROM invoice_items WHERE invoice_id = ?", (invoice_id,))
    conn.execute("DELETE FROM invoices WHERE id = ? AND user_id = ?", (invoice_id, user_id))
    conn.commit()
    conn.close()
    flash('تم تصدير الفاتورة PNG بنجاح', 'success')
    return redirect(url_for('invoices'))

def generate_invoice_qrcode(invoice):
    qr_text = (
        "Invoice Details\n"
        "--------------------------------\n"
        f"Seller's Name: {COMPANY_INFO['name']}\n"
        "--------------------------------\n"
        f"Seller's TRN: {COMPANY_INFO['vat_number']}\n"
        "--------------------------------\n"
        f"Invoice Date/Time: {invoice['invoice_date']} {datetime.now().strftime('%H:%M:%S')}\n"
        "--------------------------------\n"
        f"Invoice Total (with VAT): {int(round(invoice['total']))} SAR\n"
        "--------------------------------\n"
        f"VAT Total: {int(round(invoice['vat_amount']))} SAR"
    )
    qr = qrcode.QRCode(version=1, box_size=5, border=1)
    qr.add_data(qr_text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

@app.route('/invoice/export_pdf/<int:invoice_id>')
def export_invoice_pdf(invoice_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))

    user_id = session.get('user_id')
    conn = get_db_connection()
    invoice = conn.execute(
        "SELECT invoices.*, customers.name as customer_name, customers.phone as customer_phone, customers.address as customer_address "
        "FROM invoices LEFT JOIN customers ON invoices.customer_id = customers.id "
        "WHERE invoices.id = ? AND invoices.user_id = ?",
        (invoice_id, user_id)
    ).fetchone()

    if not invoice:
        flash('الفاتورة غير موجودة', 'danger')
        conn.close()
        return redirect(url_for('invoices'))

    items = conn.execute("SELECT * FROM invoice_items WHERE invoice_id = ?", (invoice_id,)).fetchall()
    conn.close()

    qr_img_base64 = generate_invoice_qrcode(invoice)

    html = render_template_string("""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>فاتورة رقم {{ invoice['id'] }}</title>
        <style>
            body { font-family: 'Arial'; direction: rtl; font-size: 13px; color: #000; margin: 40px; }
            .row { display: flex; justify-content: space-between; }
            .section { margin-bottom: 15px; }
            table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            th, td { border: 1px solid #ccc; padding: 6px; text-align: center; }
            th { background: #f0f0f0; }
            .totals td { text-align: left; }
            .qrcode { float: left; margin-top: 20px; }
            .footer { text-align: center; margin-top: 50px; font-size: 12px; color: #555; border-top: 1px solid #ccc; padding-top: 10px; }
        </style>
    </head>
    <body>
        <div class="row">
            <div>
                <h2>{{ company['name'] }}</h2>
                <p><strong>الرقم الضريبي:</strong> {{ company['vat_number'] }}</p>
                <p><strong>العنوان:</strong> {{ company['address'] }}</p>
                <p><strong>الهاتف:</strong> {{ company['phone'] }}</p>
            </div>
            <div style="text-align: left;">
                <h3>فاتورة ضريبية</h3>
                <p><strong>رقم الفاتورة:</strong> {{ invoice['id'] }}</p>
                <p><strong>تاريخ الإصدار:</strong> {{ invoice['invoice_date'] }}</p>
                <p><strong>الاستحقاق:</strong> {{ invoice['due_date'] }}</p>
                <p><strong>طريقة الدفع:</strong> {{ invoice['payment_method'] }}</p>
            </div>
        </div>

        <div class="section">
            <strong>اسم العميل:</strong> {{ invoice['customer_name'] }}<br>
            <strong>رقم الهاتف:</strong> {{ invoice['customer_phone'] if invoice['customer_phone'] else '---' }}<br>
            <strong>العنوان:</strong> {{ invoice['customer_address'] if invoice['customer_address'] else '---' }}
        </div>

        <table>
            <thead>
                <tr>
                    <th>رمز الصنف</th>
                    <th>المنتج</th>
                    <th>الوحدة</th>
                    <th>الكمية</th>
                    <th>سعر الوحدة</th>
                    <th>المجموع</th>
                    <th>الضريبة</th>
                    <th>الإجمالي</th>
                </tr>
            </thead>
            <tbody>
                {% for item in items %}
                <tr>
                    <td>{{ item['item_code'] }}</td>
                    <td>{{ item['item_desc'] }}</td>
                    <td>{{ item['unit'] }}</td>
                    <td>{{ item['quantity'] }}</td>
                    <td>{{ "%.2f"|format(item['unit_price']) }}</td>
                    <td>{{ "%.2f"|format(item['total']) }}</td>
                    <td>{{ "%.2f"|format(item['vat_amount']) }}</td>
                    <td>{{ "%.2f"|format(item['total'] + item['vat_amount']) }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>

        <table class="totals" style="margin-top:20px; width: 40%; float: left;">
            <tr><td>الإجمالي قبل الضريبة:</td><td>{{ "%.2f"|format(invoice['total'] - invoice['vat_amount']) }}</td></tr>
            <tr><td>الضريبة (15%):</td><td>{{ "%.2f"|format(invoice['vat_amount']) }}</td></tr>
            <tr><td><strong>الإجمالي شامل الضريبة:</strong></td><td><strong>{{ "%.2f"|format(invoice['total']) }}</strong></td></tr>
        </table>

        <div class="qrcode">
            <img src="data:image/png;base64,{{ qr_img_base64 }}" width="100" />
        </div>

        <div style="clear:both;"></div>

        <div class="footer">
            تم إنشاء هذه الفاتورة إلكترونيًا - لا تتطلب توقيعًا
        </div>
    </body>
    </html>
    """, invoice=invoice, items=items, company=COMPANY_INFO, qr_img_base64=qr_img_base64)

    config = pdfkit.configuration(wkhtmltopdf=r'C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html, False, configuration=config)

    return send_file(
        io.BytesIO(pdf),
        download_name=f"invoice_{invoice_id}.pdf",
        as_attachment=True,
        mimetype='application/pdf'
    )


# عروض السعر: عرض، إضافة، تعديل، حذف، تحويل إلى فاتورة مع اختيار منتج
@app.route('/list_quotes')
def list_quotes():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    quotes = conn.execute('''
        SELECT quotes.*, customers.name as customer_name
        FROM quotes LEFT JOIN customers ON quotes.customer_id = customers.id
        WHERE quotes.user_id = ?
        ORDER BY expiration_date DESC
    ''', (user_id,)).fetchall()
    conn.close()
    rows = ""
    for q in quotes:
        cust_name = q['customer_name'] if q['customer_name'] else '---'
        rows += f"""
        <tr>
          <td>{q['id']}</td>
          <td>{cust_name}</td>
          <td>{q['description'] if q['description'] else ''}</td>
          <td>{q['delivery_date']}</td>
          <td>{q['expiration_date']}</td>
          <td>{q['due_date']}</td>
          <td>{q['amount']:.2f}</td>
          <td>{q['vat_amount']:.2f}</td>
          <td>{q['total']:.2f}</td>
          <td><a href="{url_for('quote_details', quote_id=q['id'])}">تفاصيل</a></td>
          <td><a href="{url_for('edit_quote', quote_id=q['id'])}">تعديل</a></td>
          <td><a href="{url_for('delete_quote', quote_id=q['id'])}" onclick="return confirm('هل أنت متأكد من حذف عرض السعر؟')">حذف</a></td>
          <td><a href="{url_for('convert_quote_to_invoice', quote_id=q['id'])}" onclick="return confirm('هل تريد تحويل عرض السعر إلى فاتورة؟')">تحويل إلى فاتورة</a></td>
        </tr>
        """
    content = f"""
    <h2>عروض السعر</h2>
    <a href="{url_for('add_quote')}" class="btn">إضافة عرض سعر جديد</a>
    <table>
      <thead>
        <tr>
          <th>رقم العرض</th><th>العميل</th><th>الشرح</th><th>تاريخ التوريد</th><th>تاريخ الانتهاء</th><th>تاريخ الاستحقاق</th>
          <th>المبلغ</th><th>الضريبة</th><th>الإجمالي</th><th>تفاصيل</th><th>تعديل</th><th>حذف</th><th>تحويل</th>
        </tr>
      </thead>
      <tbody>
        {rows}
      </tbody>
    </table>
    """
    return render_template_string(base_html, title="عروض السعر", company_name=COMPANY_INFO['name'], content=content)

@app.route('/add_quote', methods=['GET','POST'])
def add_quote():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers WHERE user_id = ?", (user_id,)).fetchall()
    products = conn.execute("SELECT * FROM products WHERE user_id = ?", (user_id,)).fetchall()
    conn.close()
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        description = request.form.get('description')
        delivery_date = request.form.get('delivery_date')
        expiration_date = request.form.get('expiration_date')
        due_date = request.form.get('due_date')
        try:
            amount = float(request.form.get('amount'))
            vat_amount = float(request.form.get('vat_amount'))
            total = float(request.form.get('total'))
        except:
            flash('الرجاء إدخال أرقام صحيحة للمبلغ والضريبة والإجمالي', 'danger')
            return redirect(url_for('add_quote'))
        conn = get_db_connection()
        conn.execute('''
          INSERT INTO quotes (customer_id, description, delivery_date, expiration_date, due_date, amount, vat_amount, total, vat_rate, user_id)
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (customer_id, description, delivery_date, expiration_date, due_date, amount, vat_amount, total, VAT_RATE, user_id))
        conn.commit()
        conn.close()
        flash('تم إضافة عرض السعر بنجاح!', 'success')
        return redirect(url_for('list_quotes'))
    customers_options = "<option value=''>---</option>"
    for c in customers:
        customers_options += f"<option value='{c['id']}'>{c['name']}</option>"
    today = datetime.now().strftime('%Y-%m-%d')

    products_options = "<option value=''>---</option>"
    for p in products:
        products_options += f"<option value='{p['item_code']}'>{p['item_desc']}</option>"

    content = f"""
    <h2>إضافة عرض سعر جديد</h2>
    <form method="POST">
      <label>اسم العميل</label>
      <select name="customer_id" required>
        {customers_options}
      </select>
      <label>اختيار منتج</label>
      <select name="product_code">
        {products_options}
      </select>
      <label>الشرح</label>
      <textarea name="description"></textarea>
      <label>تاريخ التوريد</label>
      <input type="date" name="delivery_date" value="{today}" />
      <label>تاريخ الانتهاء</label>
      <input type="date" name="expiration_date" value="{today}" />
      <label>تاريخ الاستحقاق</label>
      <input type="date" name="due_date" value="{today}" />
      <label>المبلغ</label>
      <input type="number" step="0.01" name="amount" required />
      <label>الضريبة (15%)</label>
      <input type="number" step="0.01" name="vat_amount" required />
      <label>الإجمالي</label>
      <input type="number" step="0.01" name="total" required />
      <button type="submit">حفظ</button>
    </form>
    <p><a href="{url_for('list_quotes')}">عودة لعروض السعر</a></p>
    """
    return render_template_string(base_html, title="إضافة عرض سعر", company_name=COMPANY_INFO['name'], content=content)

@app.route('/quote/<int:quote_id>')
def quote_details(quote_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    quote = conn.execute('''
      SELECT quotes.*, customers.name as customer_name
      FROM quotes LEFT JOIN customers ON quotes.customer_id = customers.id
      WHERE quotes.id = ? AND quotes.user_id = ?
    ''', (quote_id, user_id)).fetchone()
    conn.close()
    if not quote:
        flash('عرض السعر غير موجود', 'danger')
        return redirect(url_for('list_quotes'))
    cust_name = quote['customer_name'] if quote['customer_name'] else '---'
    content = f"""
    <h2>تفاصيل عرض السعر رقم {quote['id']}</h2>
    <p><strong>العميل:</strong> {cust_name}</p>
    <p><strong>الشرح:</strong> {quote['description'] if quote['description'] else ''}</p>
    <p><strong>تاريخ التوريد:</strong> {quote['delivery_date']}</p>
    <p><strong>تاريخ الانتهاء:</strong> {quote['expiration_date']}</p>
    <p><strong>تاريخ الاستحقاق:</strong> {quote['due_date']}</p>
    <p><strong>المبلغ:</strong> {quote['amount']:.2f} ريال</p>
    <p><strong>الضريبة:</strong> {quote['vat_amount']:.2f} ريال</p>
    <p><strong>الإجمالي:</strong> {quote['total']:.2f} ريال</p>
    <p><a href="{url_for('list_quotes')}">عودة لعروض السعر</a></p>
    """
    return render_template_string(base_html, title=f"تفاصيل عرض السعر {quote['id']}", company_name=COMPANY_INFO['name'], content=content)

@app.route('/edit_quote/<int:quote_id>', methods=['GET', 'POST'])
def edit_quote(quote_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    quote = conn.execute('SELECT * FROM quotes WHERE id = ? AND user_id = ?', (quote_id, user_id)).fetchone()
    customers = conn.execute("SELECT * FROM customers WHERE user_id = ?", (user_id,)).fetchall()
    if not quote:
        conn.close()
        flash('عرض السعر غير موجود', 'danger')
        return redirect(url_for('list_quotes'))
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        description = request.form.get('description')
        delivery_date = request.form.get('delivery_date')
        expiration_date = request.form.get('expiration_date')
        due_date = request.form.get('due_date')
        try:
            amount = float(request.form.get('amount'))
            vat_amount = float(request.form.get('vat_amount'))
            total = float(request.form.get('total'))
        except:
            flash('الرجاء إدخال أرقام صحيحة', 'danger')
            return redirect(url_for('edit_quote', quote_id=quote_id))
        conn.execute('''
          UPDATE quotes SET customer_id=?, description=?, delivery_date=?, expiration_date=?, due_date=?, amount=?, vat_amount=?, total=?
          WHERE id=? AND user_id=?
        ''', (customer_id, description, delivery_date, expiration_date, due_date, amount, vat_amount, total, quote_id, user_id))
        conn.commit()
        conn.close()
        flash('تم تعديل عرض السعر بنجاح!', 'success')
        return redirect(url_for('list_quotes'))
    customers_options = ""
    for c in customers:
        selected = "selected" if c['id'] == quote['customer_id'] else ""
        customers_options += f"<option value='{c['id']}' {selected}>{c['name']}</option>"
    conn.close()
    content = f"""
    <h2>تعديل عرض السعر رقم {quote['id']}</h2>
    <form method="POST">
      <label>اسم العميل</label>
      <select name="customer_id" required>
        {customers_options}
      </select>
      <label>الشرح</label>
      <textarea name="description">{quote['description'] if quote['description'] else ''}</textarea>
      <label>تاريخ التوريد</label>
      <input type="date" name="delivery_date" value="{quote['delivery_date']}" />
      <label>تاريخ الانتهاء</label>
      <input type="date" name="expiration_date" value="{quote['expiration_date']}" />
      <label>تاريخ الاستحقاق</label>
      <input type="date" name="due_date" value="{quote['due_date']}" />
      <label>المبلغ</label>
      <input type="number" step="0.01" name="amount" value="{quote['amount']}" required />
      <label>الضريبة (15%)</label>
      <input type="number" step="0.01" name="vat_amount" value="{quote['vat_amount']}" required />
      <label>الإجمالي</label>
      <input type="number" step="0.01" name="total" value="{quote['total']}" required />
      <button type="submit">حفظ التعديلات</button>
    </form>
    <p><a href="{url_for('list_quotes')}">عودة لعروض السعر</a></p>
    """
    return render_template_string(base_html, title=f"تعديل عرض السعر {quote['id']}", company_name=COMPANY_INFO['name'], content=content)

@app.route('/delete_quote/<int:quote_id>')
def delete_quote(quote_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    conn.execute("DELETE FROM quotes WHERE id = ? AND user_id = ?", (quote_id, user_id))
    conn.commit()
    conn.close()
    flash('تم حذف عرض السعر بنجاح', 'success')
    return redirect(url_for('list_quotes'))

@app.route('/convert_quote_to_invoice/<int:quote_id>')
def convert_quote_to_invoice(quote_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session.get('user_id')
    conn = get_db_connection()
    quote = conn.execute("SELECT * FROM quotes WHERE id = ? AND user_id = ?", (quote_id, user_id)).fetchone()
    if not quote:
        conn.close()
        flash('عرض السعر غير موجود', 'danger')
        return redirect(url_for('list_quotes'))
    conn.execute('''
      INSERT INTO invoices (
        customer_id, payment_method, notes, total, vat_amount, vat_rate, vat_no,
        company_name, company_address, company_phone,
        invoice_date, due_date, user_id
      ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        quote['customer_id'], "نقداً", quote['description'], quote['total'], quote['vat_amount'], VAT_RATE, COMPANY_INFO['vat_number'],
        COMPANY_INFO['name'], COMPANY_INFO['address'], COMPANY_INFO['phone'],
        datetime.now().strftime('%Y-%m-%d'), quote['due_date'], user_id
    ))
    conn.commit()
    conn.close()
    flash('تم تحويل عرض السعر إلى فاتورة بنجاح', 'success')
    return redirect(url_for('invoices'))

import webbrowser
import threading

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    app.run(debug=False)

