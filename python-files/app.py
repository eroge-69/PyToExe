from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel
from flask_mail import Mail
from config import Config
import os

# إنشاء مجلدات المشروع إذا لم تكن موجودة
for dir_name in ['instance', 'models', 'routes', 'static/css', 'static/js', 'static/img', 
                'templates/auth', 'templates/products', 'templates/warehouses', 
                'templates/transactions', 'templates/reports']:
    os.makedirs(os.path.join(os.path.dirname(__file__), dir_name), exist_ok=True)

# تهيئة التطبيق
app = Flask(__name__)
app.config.from_object(Config)

# تهيئة قاعدة البيانات
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# تهيئة نظام تسجيل الدخول
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'

# تهيئة نظام البريد الإلكتروني للتنبيهات
mail = Mail(app)

# تهيئة نظام الترجمة
babel = Babel(app)

# استيراد النماذج
from models.user import User
from models.product import Product, Category
from models.warehouse import Warehouse, WarehouseProduct
from models.transaction import Transaction

# استيراد المسارات
from routes.auth_routes import auth_bp
from routes.product_routes import product_bp
from routes.warehouse_routes import warehouse_bp
from routes.transaction_routes import transaction_bp
from routes.report_routes import report_bp

# تسجيل المسارات
app.register_blueprint(auth_bp)
app.register_blueprint(product_bp)
app.register_blueprint(warehouse_bp)
app.register_blueprint(transaction_bp)
app.register_blueprint(report_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # إنشاء جداول قاعدة البيانات
    app.run(debug=True)


    