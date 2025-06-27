import os
import logging
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///accounting.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models.user import User
    return User.query.get(int(user_id))

# Import and register blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from routes.modules import modules_bp

app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(modules_bp, url_prefix='/modules')

# Create tables
with app.app_context():
    # Import models to ensure they are registered
    from models.user import User
    from models.subscription import Subscription
    
    db.create_all()
    
    # Create default admin user if it doesn't exist
    admin = User.query.filter_by(username='mohamed').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin_user = User()
        admin_user.username = 'mohamed'
        admin_user.email = 'mohamed@system.com'
        admin_user.password_hash = generate_password_hash('sheko123')
        admin_user.is_admin = True
        admin_user.store_name = 'النظام الإداري'
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Default admin user created")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
