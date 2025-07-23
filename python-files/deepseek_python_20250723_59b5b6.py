# WoTechAccounting.py - Fixed Accounting Application
import os
import sys
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///accounting.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'webmail.wotech.co.zw'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'hi@wotech.co.zw'
app.config['MAIL_PASSWORD'] = 'Tino*125#'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.config['IFRS_VERSION'] = '2023'

# Initialize extensions
db = SQLAlchemy(app)
mail = Mail(app)

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text)
    logo = db.Column(db.String(100))
    vat_number = db.Column(db.String(50))

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(50), unique=True)
    date = db.Column(db.Date, default=datetime.utcnow)
    due_date = db.Column(db.Date)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='unpaid')

# Helper Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def send_email(to, subject, body):
    try:
        msg = Message(subject,
                     recipients=[to],
                     sender=app.config['MAIL_DEFAULT_SENDER'])
        msg.body = body
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Email error: {str(e)}", file=sys.stderr)
        return False

# Routes
@app.route('/')
def dashboard():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>Accounting Dashboard</h1>
            <nav>
                <a href="/company">Company Profile</a> |
                <a href="/clients">Clients</a> |
                <a href="/invoices">Invoices</a>
            </nav>
        </body>
        </html>
    ''')

@app.route('/company', methods=['GET', 'POST'])
def company_profile():
    company = Company.query.first()
    if not company:
        company = Company()
        
    if request.method == 'POST':
        company.name = request.form.get('name', company.name)
        company.address = request.form.get('address', company.address)
        company.vat_number = request.form.get('vat_number', company.vat_number)
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                company.logo = filename
        
        db.session.add(company)
        db.session.commit()
        return redirect(url_for('company_profile'))
    
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>Company Profile</title></head>
        <body>
            <h1>Company Profile</h1>
            <form method="post" enctype="multipart/form-data">
                Name: <input type="text" name="name" value="{{ company.name }}"><br>
                Address: <textarea name="address">{{ company.address }}</textarea><br>
                VAT Number: <input type="text" name="vat_number" value="{{ company.vat_number }}"><br>
                Logo: <input type="file" name="logo"><br>
                <button type="submit">Save</button>
            </form>
        </body>
        </html>
    ''', company=company)

@app.route('/invoices')
def invoice_list():
    invoices = Invoice.query.all()
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head><title>Invoices</title></head>
        <body>
            <h1>Invoice List</h1>
            <table border="1">
                <tr>
                    <th>Number</th>
                    <th>Date</th>
                    <th>Due Date</th>
                    <th>Amount</th>
                    <th>Status</th>
                </tr>
                {% for invoice in invoices %}
                <tr>
                    <td>{{ invoice.number }}</td>
                    <td>{{ invoice.date }}</td>
                    <td>{{ invoice.due_date }}</td>
                    <td>{{ invoice.amount }}</td>
                    <td>{{ invoice.status }}</td>
                </tr>
                {% endfor %}
            </table>
        </body>
        </html>
    ''', invoices=invoices)

@app.route('/send_reminders')
def send_reminders():
    overdue_invoices = Invoice.query.filter(Invoice.due_date < datetime.now()).all()
    for invoice in overdue_invoices:
        client = Client.query.get(invoice.client_id)
        if client and client.email:
            subject = f"Payment Reminder: Invoice #{invoice.number}"
            body = f"Dear {client.name},\n\nThis is a reminder that Invoice #{invoice.number} is overdue."
            send_email(client.email, subject, body)
    
    return "Reminders sent successfully"

# Initialize the application
def initialize_app():
    with app.app_context():
        db.create_all()
        if not Company.query.first():
            company = Company(
                name="WoTech Accounting",
                address="123 Business Ave, Harare",
                vat_number="ZW123456789"
            )
            db.session.add(company)
            db.session.commit()

if __name__ == '__main__':
    initialize_app()
    print("Starting WoTech Accounting Application...")
    print(f"Access at: http://localhost:5000")
    app.run(debug=True)