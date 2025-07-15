from flask import Flask, request, redirect, session, render_template, url_for, send_from_directory, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'ваш_очень_сложный_секретный_ключ'  # Замените на случайную строку!
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls'}
app.config['PRICE_FILE'] = 'price.xlsx'

# Создаем папки, если их нет
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Пользователи (логин: admin, пароль: admin123)
users = {
    "admin": generate_password_hash("admin123")
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_price_update_time():
    price_path = os.path.join(app.config['UPLOAD_FOLDER'], app.config['PRICE_FILE'])
    if os.path.exists(price_path):
        return datetime.fromtimestamp(os.path.getmtime(price_path))
    return None

@app.route('/')
def home():
    update_time = get_price_update_time()
    return render_template('index.html', price_update_time=update_time)

@app.route('/admin')
def admin_panel():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    return render_template('admin_panel.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and check_password_hash(users[username], password):
            session['admin_logged_in'] = True
            session['username'] = username
            return redirect(url_for('admin_panel'))
        error = "Неверный логин или пароль"
    return render_template('login.html', error=error)

@app.route('/admin/logout')
def logout():
    session.pop('admin_logged_in', None)
    session.pop('username', None)
    return redirect('/')

@app.route('/admin/edit-prices', methods=['GET', 'POST'])
def edit_prices():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        if 'price_file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        file = request.files['price_file']
        
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(app.config['PRICE_FILE'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            flash('Прайс успешно обновлен!', 'success')
            return redirect(url_for('admin_panel'))
        else:
            flash('Допустимы только файлы Excel (.xlsx, .xls)', 'error')
    
    return render_template('edit_prices.html')

@app.route('/download-price')
def download_price():
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        app.config['PRICE_FILE'],
        as_attachment=True
    )

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)