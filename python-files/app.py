from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, make_response
from flask_cors import CORS
import sqlite3
import json
import pandas as pd
import io
from datetime import datetime, timedelta
from database_setup import Database

app = Flask(__name__)
CORS(app)

# إنشاء قاعدة البيانات
db = Database()

def get_db_connection():
    """الحصول على اتصال بقاعدة البيانات"""
    conn = sqlite3.connect('database/alkhabeer.db')
    conn.row_factory = sqlite3.Row
    return conn

# الصفحة الرئيسية
@app.route('/')
def index():
    return render_template('index.html')

# صفحة إدارة المنتجات
@app.route('/products')
def products():
    return render_template('products.html')

# صفحة التقارير
@app.route('/reports')
def reports():
    return render_template('reports.html')

# API endpoints
@app.route('/api/products', methods=['GET'])
def get_products():
    """الحصول على جميع المنتجات"""
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
    conn.close()
    
    products_list = []
    for product in products:
        products_list.append({
            'id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': product['quantity'],
            'description': product['description'],
            'category': product['category'],
            'created_at': product['created_at'],
            'updated_at': product['updated_at']
        })
    
    return jsonify(products_list)

@app.route('/api/products', methods=['POST'])
def add_product():
    """إضافة منتج جديد"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (name, price, quantity, description, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (data['name'], data['price'], data['quantity'], 
          data.get('description', ''), data.get('category', '')))
    
    product_id = cursor.lastrowid
    
    # إضافة سجل في تاريخ الأسعار
    cursor.execute('''
        INSERT INTO price_history (product_id, old_price, new_price, change_reason)
        VALUES (?, ?, ?, ?)
    ''', (product_id, 0, data['price'], 'إضافة منتج جديد'))
    
    # إضافة سجل في حركة المخزون
    if data['quantity'] > 0:
        cursor.execute('''
            INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
            VALUES (?, ?, ?, ?)
        ''', (product_id, 'IN', data['quantity'], 'رصيد ابتدائي'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم إضافة المنتج بنجاح'})

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """تحديث منتج موجود"""
    data = request.get_json()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # الحصول على البيانات الحالية
    current_product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if not current_product:
        conn.close()
        return jsonify({'success': False, 'message': 'المنتج غير موجود'})
    
    # تحديث البيانات
    cursor.execute('''
        UPDATE products 
        SET name = ?, price = ?, quantity = ?, description = ?, category = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (data['name'], data['price'], data['quantity'], 
          data.get('description', ''), data.get('category', ''), product_id))
    
    # إضافة سجل في تاريخ الأسعار إذا تغير السعر
    if float(current_product['price']) != float(data['price']):
        cursor.execute('''
            INSERT INTO price_history (product_id, old_price, new_price, change_reason)
            VALUES (?, ?, ?, ?)
        ''', (product_id, current_product['price'], data['price'], 
              data.get('price_change_reason', 'تحديث السعر')))
    
    # إضافة سجل في حركة المخزون إذا تغيرت الكمية
    quantity_diff = int(data['quantity']) - int(current_product['quantity'])
    if quantity_diff != 0:
        movement_type = 'IN' if quantity_diff > 0 else 'OUT'
        cursor.execute('''
            INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
            VALUES (?, ?, ?, ?)
        ''', (product_id, movement_type, abs(quantity_diff), 
              data.get('quantity_change_reason', 'تحديث الكمية')))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم تحديث المنتج بنجاح'})

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """حذف منتج"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # التحقق من وجود المنتج
    product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'المنتج غير موجود'})
    
    # حذف المنتج
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})

@app.route('/api/price-history/<int:product_id>')
def get_price_history(product_id):
    """الحصول على تاريخ تغييرات أسعار منتج"""
    conn = get_db_connection()
    history = conn.execute('''
        SELECT ph.*, p.name as product_name
        FROM price_history ph
        JOIN products p ON ph.product_id = p.id
        WHERE ph.product_id = ?
        ORDER BY ph.changed_at DESC
    ''', (product_id,)).fetchall()
    conn.close()
    
    history_list = []
    for record in history:
        history_list.append({
            'id': record['id'],
            'product_name': record['product_name'],
            'old_price': record['old_price'],
            'new_price': record['new_price'],
            'change_reason': record['change_reason'],
            'changed_at': record['changed_at']
        })
    
    return jsonify(history_list)

@app.route('/api/sales', methods=['POST'])
def add_sale():
    """إضافة مبيعة جديدة"""
    data = request.get_json()
    
    # تحويل البيانات للأنواع الصحيحة
    try:
        product_id = int(data['product_id'])
        quantity_sold = int(data['quantity_sold'])
        unit_price = float(data['unit_price'])
    except (ValueError, KeyError) as e:
        return jsonify({'success': False, 'message': 'بيانات غير صحيحة'})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # التحقق من توفر الكمية
    product = cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,)).fetchone()
    
    if not product:
        conn.close()
        return jsonify({'success': False, 'message': 'المنتج غير موجود'})
    
    if product['quantity'] < quantity_sold:
        conn.close()
        return jsonify({'success': False, 'message': 'الكمية المتاحة غير كافية'})
    
    # إضافة المبيعة
    total_amount = quantity_sold * unit_price
    cursor.execute('''
        INSERT INTO sales (product_id, quantity_sold, unit_price, total_amount, customer_name, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (product_id, quantity_sold, unit_price, 
          total_amount, data.get('customer_name', ''), data.get('notes', '')))
    
    # تحديث كمية المنتج
    new_quantity = product['quantity'] - quantity_sold
    cursor.execute('UPDATE products SET quantity = ? WHERE id = ?', (new_quantity, product_id))
    
    # إضافة سجل حركة المخزون
    cursor.execute('''
        INSERT INTO inventory_movements (product_id, movement_type, quantity, reason)
        VALUES (?, ?, ?, ?)
    ''', (product_id, 'OUT', quantity_sold, 'مبيعة'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'تم تسجيل المبيعة بنجاح'})

@app.route('/api/reports/monthly-sales')
def monthly_sales_report():
    """تقرير المبيعات الشهرية"""
    month = request.args.get('month', datetime.now().strftime('%Y-%m'))
    
    conn = get_db_connection()
    sales = conn.execute('''
        SELECT s.*, p.name as product_name, p.category
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE strftime('%Y-%m', s.sale_date) = ?
        ORDER BY s.sale_date DESC
    ''', (month,)).fetchall()
    
    # إحصائيات شاملة
    stats = conn.execute('''
        SELECT 
            COUNT(*) as total_sales,
            SUM(total_amount) as total_revenue,
            SUM(quantity_sold) as total_quantity
        FROM sales
        WHERE strftime('%Y-%m', sale_date) = ?
    ''', (month,)).fetchone()
    
    conn.close()
    
    sales_list = []
    for sale in sales:
        sales_list.append({
            'id': sale['id'],
            'product_name': sale['product_name'],
            'category': sale['category'],
            'quantity_sold': sale['quantity_sold'],
            'unit_price': sale['unit_price'],
            'total_amount': sale['total_amount'],
            'customer_name': sale['customer_name'],
            'sale_date': sale['sale_date']
        })
    
    return jsonify({
        'sales': sales_list,
        'stats': {
            'total_sales': stats['total_sales'] or 0,
            'total_revenue': stats['total_revenue'] or 0,
            'total_quantity': stats['total_quantity'] or 0
        }
    })

@app.route('/api/reports/price-comparison')
def price_comparison_report():
    """تقرير مقارنة الأسعار"""
    conn = get_db_connection()
    
    # الحصول على آخر تغييرات الأسعار لكل منتج
    price_changes = conn.execute('''
        SELECT 
            p.id,
            p.name,
            p.price as current_price,
            ph.old_price,
            ph.new_price,
            ph.changed_at,
            ph.change_reason
        FROM products p
        LEFT JOIN price_history ph ON p.id = ph.product_id
        WHERE ph.id IN (
            SELECT MAX(id) FROM price_history WHERE product_id = p.id
        ) OR ph.id IS NULL
        ORDER BY p.name
    ''').fetchall()
    
    conn.close()
    
    comparison_list = []
    for record in price_changes:
        comparison_list.append({
            'product_id': record['id'],
            'product_name': record['name'],
            'current_price': record['current_price'],
            'old_price': record['old_price'],
            'new_price': record['new_price'],
            'price_change': (record['new_price'] - record['old_price']) if record['old_price'] else 0,
            'change_percentage': ((record['new_price'] - record['old_price']) / record['old_price'] * 100) if record['old_price'] and record['old_price'] > 0 else 0,
            'last_changed': record['changed_at'],
            'change_reason': record['change_reason']
        })
    
    return jsonify(comparison_list)

@app.route('/api/reports/monthly-breakdown')
def monthly_breakdown_report():
    """تقرير شامل للمبيعات شهر بشهر"""
    try:
        conn = get_db_connection()
        
        # الحصول على بيانات شهرية لآخر 12 شهر
        monthly_data = conn.execute('''
            SELECT 
                strftime('%Y-%m', sale_date) as month,
                COUNT(*) as total_sales,
                SUM(total_amount) as total_revenue,
                SUM(quantity_sold) as total_quantity,
                AVG(total_amount) as avg_sale_amount,
                COUNT(DISTINCT customer_name) as unique_customers
            FROM sales
            WHERE sale_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY month DESC
        ''').fetchall()
        
        # الحصول على أفضل المنتجات مبيعاً لكل شهر
        top_products_by_month = conn.execute('''
            SELECT 
                strftime('%Y-%m', s.sale_date) as month,
                p.name as product_name,
                SUM(s.quantity_sold) as total_quantity,
                SUM(s.total_amount) as total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE s.sale_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', s.sale_date), s.product_id
            ORDER BY month DESC, total_revenue DESC
        ''').fetchall()
        
        conn.close()
        
        # تحويل أسماء الأشهر للعربية
        month_names = {
            '01': 'يناير', '02': 'فبراير', '03': 'مارس', '04': 'أبريل',
            '05': 'مايو', '06': 'يونيو', '07': 'يوليو', '08': 'أغسطس',
            '09': 'سبتمبر', '10': 'أكتوبر', '11': 'نوفمبر', '12': 'ديسمبر'
        }
        
        # تنظيم بيانات الأشهر
        monthly_stats = []
        for row in monthly_data:
            year, month = row['month'].split('-')
            month_name = month_names.get(month, month)
            
            monthly_stats.append({
                'month_code': row['month'],
                'month_name': f"{month_name} {year}",
                'total_sales': row['total_sales'] or 0,
                'total_revenue': float(row['total_revenue'] or 0),
                'total_quantity': row['total_quantity'] or 0,
                'avg_sale_amount': float(row['avg_sale_amount'] or 0),
                'unique_customers': row['unique_customers'] or 0
            })
        
        # تنظيم بيانات أفضل المنتجات لكل شهر
        monthly_top_products = {}
        for row in top_products_by_month:
            month = row['month']
            if month not in monthly_top_products:
                monthly_top_products[month] = []
            
            if len(monthly_top_products[month]) < 3:  # أفضل 3 منتجات فقط
                monthly_top_products[month].append({
                    'product_name': row['product_name'],
                    'quantity_sold': row['total_quantity'],
                    'revenue': float(row['total_revenue'])
                })
        
        return jsonify({
            'monthly_stats': monthly_stats,
            'top_products_by_month': monthly_top_products
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/sales-chart')
def sales_chart_data():
    """بيانات الرسم البياني للمبيعات لآخر 6 أشهر"""
    try:
        conn = get_db_connection()
        
        # الحصول على آخر 6 أشهر
        sales_data = conn.execute('''
            SELECT 
                strftime('%Y-%m', sale_date) as month,
                SUM(total_amount) as total_sales
            FROM sales
            WHERE sale_date >= date('now', '-6 months')
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY month
        ''').fetchall()
        
        conn.close()
        
        # تحويل أسماء الأشهر للعربية
        month_names = {
            '01': 'يناير', '02': 'فبراير', '03': 'مارس', '04': 'أبريل',
            '05': 'مايو', '06': 'يونيو', '07': 'يوليو', '08': 'أغسطس',
            '09': 'سبتمبر', '10': 'أكتوبر', '11': 'نوفمبر', '12': 'ديسمبر'
        }
        
        labels = []
        data = []
        
        for row in sales_data:
            year, month = row['month'].split('-')
            month_name = month_names.get(month, month)
            labels.append(f"{month_name} {year}")
            data.append(float(row['total_sales'] or 0))
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reports/category-chart')
def category_chart_data():
    """بيانات الرسم البياني لتوزيع المنتجات بالفئات"""
    try:
        conn = get_db_connection()
        
        category_data = conn.execute('''
            SELECT 
                CASE 
                    WHEN category IS NULL OR category = '' THEN 'غير محدد'
                    ELSE category
                END as category_name,
                COUNT(*) as product_count
            FROM products
            GROUP BY category_name
            ORDER BY product_count DESC
        ''').fetchall()
        
        conn.close()
        
        labels = []
        data = []
        
        for row in category_data:
            labels.append(row['category_name'])
            data.append(row['product_count'])
        
        return jsonify({
            'labels': labels,
            'data': data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/products')
def export_products_csv():
    """تصدير المنتجات إلى ملف CSV"""
    try:
        conn = get_db_connection()
        products = conn.execute('SELECT * FROM products ORDER BY name').fetchall()
        conn.close()
        
        # تحويل البيانات إلى DataFrame
        products_data = []
        for product in products:
            products_data.append({
                'الرقم': product['id'],
                'اسم المنتج': product['name'],
                'السعر': product['price'],
                'الكمية': product['quantity'],
                'الفئة': product['category'] or '',
                'الوصف': product['description'] or '',
                'تاريخ الإضافة': product['created_at'],
                'آخر تحديث': product['updated_at']
            })
        
        df = pd.DataFrame(products_data)
        
        # إنشاء ملف CSV في الذاكرة
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')  # BOM لدعم العربية
        
        # إنشاء استجابة مع الملف
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename=products_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ في التصدير: {str(e)}'}), 500

@app.route('/api/export/sales')
def export_sales_csv():
    """تصدير المبيعات إلى ملف CSV"""
    try:
        month = request.args.get('month', datetime.now().strftime('%Y-%m'))
        
        conn = get_db_connection()
        sales = conn.execute('''
            SELECT s.*, p.name as product_name, p.category
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE strftime('%Y-%m', s.sale_date) = ?
            ORDER BY s.sale_date DESC
        ''', (month,)).fetchall()
        conn.close()
        
        # تحويل البيانات إلى DataFrame
        sales_data = []
        for sale in sales:
            sales_data.append({
                'الرقم': sale['id'],
                'المنتج': sale['product_name'],
                'الفئة': sale['category'],
                'الكمية المباعة': sale['quantity_sold'],
                'سعر الوحدة': sale['unit_price'],
                'إجمالي المبلغ': sale['total_amount'],
                'العميل': sale['customer_name'] or '',
                'تاريخ البيع': sale['sale_date'],
                'ملاحظات': sale['notes'] or ''
            })
        
        df = pd.DataFrame(sales_data)
        
        # إنشاء ملف CSV في الذاكرة
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')  # BOM لدعم العربية
        
        # إنشاء استجابة مع الملف
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename=sales_{month}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ في التصدير: {str(e)}'}), 500

@app.route('/api/export/monthly-breakdown')
def export_monthly_breakdown_csv():
    """تصدير التقرير الشهري الشامل إلى ملف CSV"""
    try:
        conn = get_db_connection()
        
        # الحصول على بيانات شهرية لآخر 12 شهر
        monthly_data = conn.execute('''
            SELECT 
                strftime('%Y-%m', sale_date) as month,
                COUNT(*) as total_sales,
                SUM(total_amount) as total_revenue,
                SUM(quantity_sold) as total_quantity,
                AVG(total_amount) as avg_sale_amount,
                COUNT(DISTINCT customer_name) as unique_customers
            FROM sales
            WHERE sale_date >= date('now', '-12 months')
            GROUP BY strftime('%Y-%m', sale_date)
            ORDER BY month DESC
        ''').fetchall()
        
        conn.close()
        
        # تحويل أسماء الأشهر للعربية
        month_names = {
            '01': 'يناير', '02': 'فبراير', '03': 'مارس', '04': 'أبريل',
            '05': 'مايو', '06': 'يونيو', '07': 'يوليو', '08': 'أغسطس',
            '09': 'سبتمبر', '10': 'أكتوبر', '11': 'نوفمبر', '12': 'ديسمبر'
        }
        
        # تحويل البيانات إلى DataFrame
        breakdown_data = []
        for row in monthly_data:
            year, month = row['month'].split('-')
            month_name = month_names.get(month, month)
            
            breakdown_data.append({
                'الشهر': f"{month_name} {year}",
                'عدد المبيعات': row['total_sales'] or 0,
                'إجمالي الإيرادات': float(row['total_revenue'] or 0),
                'متوسط قيمة المبيعة': float(row['avg_sale_amount'] or 0),
                'عدد العملاء': row['unique_customers'] or 0
            })
        
        df = pd.DataFrame(breakdown_data)
        
        # إنشاء ملف CSV في الذاكرة
        output = io.StringIO()
        df.to_csv(output, index=False, encoding='utf-8-sig')
        
        # إنشاء استجابة مع الملف
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv; charset=utf-8-sig'
        response.headers['Content-Disposition'] = f'attachment; filename=monthly_breakdown_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        
        return response
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'خطأ في التصدير: {str(e)}'}), 500

if __name__ == '__main__':
    print("بدء تشغيل برنامج إدارة المنتجات - شركة الخبير")
    print("يمكنك الوصول للبرنامج عبر: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)