# WoTechAccounting.py - Complete Accounting Application
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import sqlite3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, Image
from reportlab.lib.styles import getSampleStyleSheet

# ==============================================
# CONFIGURATION
# ==============================================
class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///accounting.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'webmail.wotech.co.zw'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'hi@wotech.co.zw'
    MAIL_PASSWORD = 'Tino*125#'
    MAIL_DEFAULT_SENDER = 'hi@wotech.co.zw'
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    IFRS_VERSION = '2023'

# ==============================================
# APPLICATION SETUP
# ==============================================
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
mail = Mail(app)

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ==============================================
# DATABASE MODELS
# ==============================================
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
    tax = db.Column(db.Float)
    status = db.Column(db.String(20), default='unpaid')

# ==============================================
# HELPER FUNCTIONS
# ==============================================
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
        print(f"Email error: {str(e)}")
        return False

def generate_invoice_pdf(invoice_id):
    invoice = Invoice.query.get(invoice_id)
    client = Client.query.get(invoice.client_id)
    company = Company.query.first()
    
    filename = f"Invoice_{invoice.number}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    
    styles = getSampleStyleSheet()
    elements = []
    
    # Add company logo if exists
    if company and company.logo:
        logo_path = os.path.join(app.config['UPLOAD_FOLDER'], company.logo)
        elements.append(Image(logo_path, width=100, height=50))
    
    # Add invoice details
    elements.append(Paragraph(f"INVOICE #{invoice.number}", styles['Heading1']))
    elements.append(Paragraph(f"Date: {invoice.date.strftime('%Y-%m-%d')}", styles['Normal']))
    elements.append(Paragraph(f"Due Date: {invoice.due_date.strftime('%Y-%m-%d')}", styles['Normal']))
    
    # Add IFRS compliance note
    ifrs_note = f"Prepared in accordance with IFRS {app.config['IFRS_VERSION']}"
    elements.append(Paragraph(ifrs_note, styles['Italic']))
    
    # Build PDF
    doc.build(elements)
    return filename

# ==============================================
# ROUTES
# ==============================================
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/company', methods=['GET', 'POST'])
def company_profile():
    company = Company.query.first() or Company()
    
    if request.method == 'POST':
        company.name = request.form.get('name')
        company.address = request.form.get('address')
        company.vat_number = request.form.get('vat_number')
        
        if 'logo' in request.files:
            file = request.files['logo']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                company.logo = filename
        
        db.session.add(company)
        db.session.commit()
        return redirect(url_for('company_profile'))
    
    return render_template('company.html', company=company)

@app.route('/invoices')
def invoice_list():
    invoices = Invoice.query.all()
    return render_template('invoices.html', invoices=invoices)

@app.route('/send_reminders')
def send_reminders():
    overdue_invoices = Invoice.query.filter(Invoice.due_date < datetime.now()).all()
    for invoice in overdue_invoices:
        client = Client.query.get(invoice.client_id)
        subject = f"Payment Reminder: Invoice #{invoice.number}"
        body = f"Dear {client.name},\n\nThis is a reminder that Invoice #{invoice.number} is overdue."
        send_email(client.email, subject, body)
    
    return "Reminders sent successfully"

# ==============================================
# TEMPLATE RENDERING (Fallback for standalone)
# ==============================================
@app.route('/templates/<path:filename>')
def serve_template(filename):
    templates = {
        'dashboard.html': """
        <!DOCTYPE html>
        <html>
        <head><title>Dashboard</title></head>
        <body>
            <h1>Accounting Dashboard</h1>
            <nav>
                <a href="/company">Company Profile</a> |
                <a href="/invoices">Invoices</a> |
                <a href="/send_reminders">Send Reminders</a>
            </nav>
        </body>
        </html>
        """,
        'company.html': """
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
        """,
        'invoices.html': """
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
        """
    }
    
    if filename in templates:
        return templates[filename]
    return "Template not found", 404

# ==============================================
# APPLICATION STARTUP
# ==============================================
def initialize_app():
    with app.app_context():
        db.create_all()
        
        # Create default company if none exists
        if not Company.query.first():
            company = Company(
                name="WoTech Accounting",
                address="123 Business Ave, Harare, Zimbabwe",
                vat_number="ZW123456789"
            )
            db.session.add(company)
            db.session.commit()

if __name__ == '__main__':
    initialize_app()
    app.run(debug=True)