
import os, re
from datetime import date, datetime
from decimal import Decimal
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, DateField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Optional, NumberRange
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session
from werkzeug.utils import secure_filename

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
from pdfminer.high_level import extract_text

APP_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(APP_DIR, "data.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-key"
app.config["UPLOAD_FOLDER"] = os.path.join(APP_DIR, "uploads")
app.config["STATIC_DIR"] = os.path.join(APP_DIR, "static")

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False))
Base = declarative_base()

# ---------------- Models ----------------
class Setting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True)
    company_name = Column(String(200), default="Your Company")
    address = Column(Text, default="Address line 1\nCity, Country")
    phone = Column(String(50), default="")
    email = Column(String(120), default="")
    logo_filename = Column(String(200), default="logo.png")  # place your logo as static/logo.png

class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(150), unique=True, nullable=False)
    email = Column(String(150))
    phone = Column(String(50))
    address = Column(Text)
    currency = Column(String(10), default="SAR")

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    sku = Column(String(64), unique=True, nullable=False)
    name = Column(String(200), nullable=False)
    uom = Column(String(20), default="unit")
    default_price = Column(Numeric(12,2), default=0)

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    id = Column(Integer, primary_key=True)
    number = Column(String(50), unique=True, nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    order_date = Column(Date, default=date.today)
    status = Column(String(20), default="Open")
    notes = Column(Text)
    supplier = relationship("Supplier")
    lines = relationship("POLine", cascade="all, delete-orphan")

class POLine(Base):
    __tablename__ = "po_lines"
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    description = Column(Text)
    qty = Column(Numeric(12,3), default=0)
    price = Column(Numeric(12,2), default=0)

class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    bill_number = Column(String(50), nullable=False)
    bill_date = Column(Date, default=date.today)
    due_date = Column(Date)
    notes = Column(Text)
    supplier = relationship("Supplier")
    lines = relationship("BillLine", cascade="all, delete-orphan")

class BillLine(Base):
    __tablename__ = "bill_lines"
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    description = Column(Text, nullable=False)
    qty = Column(Numeric(12,3), default=0)
    price = Column(Numeric(12,2), default=0)

class Quotation(Base):
    __tablename__ = "quotations"
    id = Column(Integer, primary_key=True)
    quote_number = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(150), nullable=False)
    quote_date = Column(Date, default=date.today)
    notes = Column(Text)
    currency = Column(String(10), default="SAR")
    lines = relationship("QuotationLine", cascade="all, delete-orphan")

class QuotationLine(Base):
    __tablename__ = "quotation_lines"
    id = Column(Integer, primary_key=True)
    quotation_id = Column(Integer, ForeignKey("quotations.id"))
    description = Column(Text, nullable=False)
    qty = Column(Numeric(12,3), default=0)
    price = Column(Numeric(12,2), default=0)

def init_db():
    Base.metadata.create_all(engine)
    s = Session()
    if not s.query(Setting).first():
        s.add(Setting())
        s.commit()

# --------------- Forms -----------------
from flask_wtf.file import FileAllowed
class SettingsForm(FlaskForm):
    company_name = StringField("Company Name", validators=[Optional()])
    address = TextAreaField("Address", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional()])
    email = StringField("Email", validators=[Optional()])
    logo = FileField("Logo (PNG/JPG)", validators=[Optional(), FileAllowed(["png","jpg","jpeg"], "Images only!")])

class SupplierForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional()])
    address = TextAreaField("Address", validators=[Optional()])
    currency = StringField("Currency", validators=[Optional()])

class ItemForm(FlaskForm):
    sku = StringField("SKU", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    uom = StringField("UoM", validators=[Optional()])
    default_price = DecimalField("Default Price", places=2, validators=[Optional()])

class POForm(FlaskForm):
    number = StringField("PO Number", validators=[DataRequired()])
    supplier_id = SelectField("Supplier", coerce=int, validators=[DataRequired()])
    order_date = DateField("Order Date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

class BillForm(FlaskForm):
    supplier_id = SelectField("Supplier", coerce=int, validators=[DataRequired()])
    bill_number = StringField("Bill #", validators=[DataRequired()])
    bill_date = DateField("Bill Date", validators=[Optional()])
    due_date = DateField("Due Date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

class QuotationForm(FlaskForm):
    quote_number = StringField("Quote #", validators=[DataRequired()])
    customer_name = StringField("Customer", validators=[DataRequired()])
    quote_date = DateField("Date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    currency = StringField("Currency", validators=[Optional()])

# --------------- Helpers --------------
def money(x):
    return f"{Decimal(x or 0):,.2f}"
app.jinja_env.filters["money"] = money

def ensure_logo_path(settings):
    # ensure logo file exists
    logo_path = os.path.join(app.config["STATIC_DIR"], settings.logo_filename or "logo.png")
    if not os.path.exists(logo_path):
        # write a placeholder
        from PIL import Image, ImageDraw, ImageFont  # pillow not installed; fallback to no image
        return None
    return logo_path

def draw_header(c, settings, title):
    width, height = A4
    # Logo
    logo_path = os.path.join(app.config["STATIC_DIR"], settings.logo_filename or "logo.png")
    if os.path.exists(logo_path):
        try:
            c.drawImage(logo_path, 20*mm, height-40*mm, width=35*mm, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass
    # Company info
    x = width - 20*mm
    y = height - 20*mm
    c.setFont("Helvetica-Bold", 14)
    c.drawRightString(x, y, settings.company_name or "Company")
    c.setFont("Helvetica", 9)
    for i, line in enumerate((settings.address or "").splitlines()[:4]):
        c.drawRightString(x, y- (12*(i+1)), line)
    if settings.phone:
        c.drawRightString(x, y-60, f"Phone: {settings.phone}")
    if settings.email:
        c.drawRightString(x, y-72, f"Email: {settings.email}")
    # Title
    c.setFillColor(colors.HexColor("#222222"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20*mm, height-55*mm, title)
    c.setFillColor(colors.black)

def draw_table(c, headers, rows, start_y):
    width, height = A4
    x = 20*mm
    col_widths = [70*mm, 25*mm, 25*mm, 30*mm]
    # headers
    c.setFont("Helvetica-Bold", 10)
    y = start_y
    for i, h in enumerate(headers):
        c.drawString(x + sum(col_widths[:i]) + 2, y, h)
    # lines
    y -= 10
    c.line(x, y, width-20*mm, y)
    c.setFont("Helvetica", 10)
    for row in rows:
        y -= 14
        for i, text in enumerate(row):
            c.drawString(x + sum(col_widths[:i]) + 2, y, str(text))
    return y

def export_quotation_pdf(q):
    s = Session()
    settings = s.query(Setting).first()
    width, height = A4
    buff = BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    draw_header(c, settings, "Quotation")
    # Meta
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, height-70*mm, f"Quotation #: {q.quote_number}")
    c.drawString(20*mm, height-78*mm, f"Date: {q.quote_date.isoformat()}")
    c.drawString(20*mm, height-86*mm, f"Customer: {q.customer_name}")
    # table
    headers = ["Description", "Qty", "Unit Price", "Line Total"]
    rows = []
    subtotal = 0.0
    for ln in q.lines:
        line_total = float(ln.qty)*float(ln.price)
        rows.append([ln.description, f"{ln.qty:.3f}", f"{float(ln.price):,.2f} {q.currency}", f"{line_total:,.2f} {q.currency}"])
        subtotal += line_total
    y = draw_table(c, headers, rows, height-100*mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width-20*mm, y-20, f"Subtotal: {subtotal:,.2f} {q.currency}")
    c.drawRightString(width-20*mm, y-36, f"Total: {subtotal:,.2f} {q.currency}")
    c.showPage()
    c.save()
    buff.seek(0)
    return buff

def export_bill_pdf(bill):
    s = Session()
    settings = s.query(Setting).first()
    width, height = A4
    buff = BytesIO()
    c = canvas.Canvas(buff, pagesize=A4)
    draw_header(c, settings, "Invoice")
    c.setFont("Helvetica", 10)
    c.drawString(20*mm, height-70*mm, f"Invoice #: {bill.bill_number}")
    c.drawString(20*mm, height-78*mm, f"Date: {bill.bill_date.isoformat()}")
    c.drawString(20*mm, height-86*mm, f"Supplier: {bill.supplier.name}")
    headers = ["Description", "Qty", "Unit Price", "Line Total"]
    rows = []
    subtotal = 0.0
    for ln in bill.lines:
        lt = float(ln.qty)*float(ln.price)
        rows.append([ln.description, f"{ln.qty:.3f}", f"{float(ln.price):,.2f}", f"{lt:,.2f}"])
        subtotal += lt
    y = draw_table(c, headers, rows, height-100*mm)
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width-20*mm, y-20, f"Total: {subtotal:,.2f}")
    c.showPage()
    c.save()
    buff.seek(0)
    return buff

# --------------- Routes ---------------
@app.route("/")
def index():
    s = Session()
    stats = {
        "suppliers": s.query(Supplier).count(),
        "pos": s.query(PurchaseOrder).count(),
        "bills": s.query(Bill).count(),
        "quotes": s.query(Quotation).count(),
    }
    return render_template("index.html", stats=stats)

@app.route("/settings", methods=["GET","POST"])
def settings():
    s = Session()
    st = s.query(Setting).first()
    form = SettingsForm(obj=st)
    if form.validate_on_submit():
        st.company_name = form.company_name.data or st.company_name
        st.address = form.address.data or st.address
        st.phone = form.phone.data or st.phone
        st.email = form.email.data or st.email
        file = form.logo.data
        if file and file.filename:
            fname = secure_filename(file.filename)
            ext = os.path.splitext(fname)[1].lower()
            fname = "logo"+ext
            path = os.path.join(app.config["STATIC_DIR"], fname)
            file.save(path)
            st.logo_filename = fname
        s.commit()
        flash("Settings saved","success")
        return redirect(url_for("settings"))
    return render_template("settings.html", form=form, st=st)

# Suppliers
@app.route("/suppliers")
def suppliers():
    s = Session()
    data = s.query(Supplier).order_by(Supplier.name.asc()).all()
    return render_template("suppliers.html", data=data)

@app.route("/suppliers/new", methods=["GET","POST"])
def supplier_new():
    form = SupplierForm()
    if form.validate_on_submit():
        s = Session()
        s.add(Supplier(**form.data))
        s.commit()
        return redirect(url_for("suppliers"))
    return render_template("supplier_form.html", form=form, title="New Supplier")

# Items
@app.route("/items")
def items():
    s = Session()
    data = s.query(Item).order_by(Item.sku.asc()).all()
    return render_template("items.html", data=data)

@app.route("/items/new", methods=["GET","POST"])
def item_new():
    form = ItemForm()
    if form.validate_on_submit():
        s = Session()
        s.add(Item(**form.data))
        s.commit()
        return redirect(url_for("items"))
    return render_template("item_form.html", form=form, title="New Item")

# POs
@app.route("/pos")
def pos():
    s = Session()
    data = s.query(PurchaseOrder).order_by(PurchaseOrder.order_date.desc()).all()
    return render_template("pos.html", data=data)

@app.route("/pos/new", methods=["GET","POST"])
def po_new():
    s = Session()
    form = POForm()
    form.supplier_id.choices = [(x.id, x.name) for x in s.query(Supplier).order_by(Supplier.name.asc())]
    items = s.query(Item).order_by(Item.name.asc()).all()
    if request.method == "POST":
        po = PurchaseOrder(
            number=request.form.get("number"),
            supplier_id=int(request.form.get("supplier_id")),
            order_date=request.form.get("order_date") or date.today(),
            notes=request.form.get("notes")
        )
        s.add(po); s.flush()
        idx = 0
        while True:
            if f"desc-{idx}" in request.form:
                desc = request.form.get(f"desc-{idx}")
                qty = Decimal(request.form.get(f"qty-{idx}") or "0")
                price = Decimal(request.form.get(f"price-{idx}") or "0")
                if qty>0:
                    s.add(POLine(po_id=po.id, description=desc, qty=qty, price=price))
                idx+=1
            else:
                break
        s.commit()
        return redirect(url_for("pos"))
    return render_template("po_form.html", form=form)

# Bills
@app.route("/bills")
def bills():
    s = Session()
    data = s.query(Bill).order_by(Bill.bill_date.desc()).all()
    return render_template("bills.html", data=data)

@app.route("/bills/new", methods=["GET","POST"])
def bill_new():
    s = Session()
    form = BillForm()
    form.supplier_id.choices = [(x.id, x.name) for x in s.query(Supplier).order_by(Supplier.name.asc())]
    if form.validate_on_submit():
        b = Bill(
            supplier_id=form.supplier_id.data,
            bill_number=form.bill_number.data,
            bill_date=form.bill_date.data or date.today(),
            due_date=form.due_date.data,
            notes=form.notes.data
        )
        s.add(b); s.flush()
        idx=0
        while True:
            if f"desc-{idx}" in request.form:
                desc = request.form.get(f"desc-{idx}")
                qty = Decimal(request.form.get(f"qty-{idx}") or "0")
                price = Decimal(request.form.get(f"price-{idx}") or "0")
                if qty>0:
                    s.add(BillLine(bill_id=b.id, description=desc, qty=qty, price=price))
                idx+=1
            else:
                break
        s.commit()
        return redirect(url_for("bills"))
    return render_template("bill_form.html", form=form)

@app.route("/bills/<int:bill_id>/pdf")
def bill_pdf(bill_id):
    s = Session()
    bill = s.get(Bill, bill_id)
    pdf = export_bill_pdf(bill)
    return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name=f"Invoice_{bill.bill_number}.pdf")

# Quotations
@app.route("/quotes")
def quotes():
    s = Session()
    data = s.query(Quotation).order_by(Quotation.quote_date.desc()).all()
    return render_template("quotes.html", data=data)

@app.route("/quotes/new", methods=["GET","POST"])
def quote_new():
    form = QuotationForm()
    if form.validate_on_submit():
        s = Session()
        q = Quotation(
            quote_number=form.quote_number.data,
            customer_name=form.customer_name.data,
            quote_date=form.quote_date.data or date.today(),
            notes=form.notes.data,
            currency=form.currency.data or "SAR"
        )
        s.add(q); s.flush()
        idx=0
        while True:
            if f"desc-{idx}" in request.form:
                desc = request.form.get(f"desc-{idx}")
                qty = Decimal(request.form.get(f"qty-{idx}") or "0")
                price = Decimal(request.form.get(f"price-{idx}") or "0")
                if qty>0:
                    s.add(QuotationLine(quotation_id=q.id, description=desc, qty=qty, price=price))
                idx+=1
            else:
                break
        s.commit()
        return redirect(url_for("quotes"))
    return render_template("quote_form.html", form=form)

@app.route("/quotes/<int:quote_id>/pdf")
def quote_pdf(quote_id):
    s = Session()
    q = s.get(Quotation, quote_id)
    pdf = export_quotation_pdf(q)
    return send_file(pdf, mimetype="application/pdf", as_attachment=True, download_name=f"Quotation_{q.quote_number}.pdf")

# PDF Import for PO
@app.route("/pos/import", methods=["GET","POST"])
def po_import():
    if request.method == "POST":
        file = request.files.get("pdf")
        if not file or not file.filename.lower().endswith(".pdf"):
            flash("Please upload a PDF file", "info")
            return redirect(url_for("po_import"))
        path = os.path.join(app.config["UPLOAD_FOLDER"], secure_filename(file.filename))
        file.save(path)
        try:
            text = extract_text(path)
        except Exception as e:
            flash(f"Failed to read PDF: {e}", "info")
            return redirect(url_for("po_import"))
        # naive extraction
        po_number = re.search(r"(PO\s*#?:?\s*)([A-Za-z0-9\-_/]+)", text, re.I)
        po_number = po_number.group(2) if po_number else "PO-IMPORTED"
        date_match = re.search(r"(\d{4}-\d{2}-\d{2})|(\d{2}/\d{2}/\d{4})", text)
        order_date = date.today()
        if date_match:
            val = date_match.group(0)
            try:
                if "-" in val:
                    order_date = date.fromisoformat(val)
                else:
                    d,m,y = val.split("/")
                    order_date = date(int(y), int(m), int(d))
            except:
                pass
        supplier_name = None
        m = re.search(r"Supplier[:\s]+([A-Za-z0-9 &().,-]+)", text, re.I)
        if m:
            supplier_name = m.group(1).strip()
        # Build a preview (no line parsing for MVP)
        return render_template("po_import_preview.html", po_number=po_number, order_date=order_date, supplier_name=supplier_name, raw=text[:4000], filename=os.path.basename(path))
    return render_template("po_import.html")

# Save imported PO
@app.route("/pos/import/save", methods=["POST"])
def po_import_save():
    s = Session()
    number = request.form.get("number") or "PO-IMPORTED"
    supplier_name = request.form.get("supplier_name") or "Imported Supplier"
    order_date = request.form.get("order_date") or date.today().isoformat()
    sup = s.query(Supplier).filter_by(name=supplier_name).first()
    if not sup:
        sup = Supplier(name=supplier_name)
        s.add(sup); s.flush()
    po = PurchaseOrder(number=number, supplier_id=sup.id, order_date=order_date, notes="Imported from PDF")
    s.add(po); s.commit()
    flash("Imported PO saved","success")
    return redirect(url_for("pos"))

# ----------- Run -----------
@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
