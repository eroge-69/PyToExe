
import os
from datetime import datetime, date
from decimal import Decimal
from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, DateField, TextAreaField, SelectField, FieldList, FormField, HiddenField
from wtforms.validators import DataRequired, NumberRange, Optional
from sqlalchemy import create_engine, Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, scoped_session

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("APP_SECRET", "dev-secret")
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, future=True)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False))
Base = declarative_base()

# ---------------------- Models ----------------------
class Supplier(Base):
    __tablename__ = "suppliers"
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False, unique=True)
    email = Column(String(120))
    phone = Column(String(50))
    address = Column(Text)
    currency = Column(String(10), default="SAR")
    notes = Column(Text)

    bills = relationship("Bill", back_populates="supplier", cascade="all, delete-orphan")
    pos = relationship("PurchaseOrder", back_populates="supplier", cascade="all, delete-orphan")

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
    status = Column(String(20), default="Open")  # Open, Partially Received, Closed, Billed
    notes = Column(Text)

    supplier = relationship("Supplier", back_populates="pos")
    lines = relationship("POLine", back_populates="po", cascade="all, delete-orphan")
    receipts = relationship("GoodsReceipt", back_populates="po", cascade="all, delete-orphan")

class POLine(Base):
    __tablename__ = "po_lines"
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"))
    item_id = Column(Integer, ForeignKey("items.id"))
    description = Column(Text)
    qty = Column(Numeric(12,3), default=0)
    price = Column(Numeric(12,2), default=0)
    received_qty = Column(Numeric(12,3), default=0)

    po = relationship("PurchaseOrder", back_populates="lines")
    item = relationship("Item")

class GoodsReceipt(Base):
    __tablename__ = "goods_receipts"
    id = Column(Integer, primary_key=True)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    grn_number = Column(String(50), unique=True, nullable=False)
    received_date = Column(Date, default=date.today)
    notes = Column(Text)

    po = relationship("PurchaseOrder", back_populates="receipts")
    lines = relationship("GRNLine", back_populates="grn", cascade="all, delete-orphan")

class GRNLine(Base):
    __tablename__ = "grn_lines"
    id = Column(Integer, primary_key=True)
    grn_id = Column(Integer, ForeignKey("goods_receipts.id"))
    po_line_id = Column(Integer, ForeignKey("po_lines.id"))
    qty_received = Column(Numeric(12,3), default=0)

    grn = relationship("GoodsReceipt", back_populates="lines")
    po_line = relationship("POLine")

class Bill(Base):
    __tablename__ = "bills"
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    bill_number = Column(String(50), nullable=False)
    bill_date = Column(Date, default=date.today)
    due_date = Column(Date)
    currency = Column(String(10), default="SAR")
    status = Column(String(20), default="Open")  # Open, Partially Paid, Paid
    notes = Column(Text)

    supplier = relationship("Supplier", back_populates="bills")
    lines = relationship("BillLine", back_populates="bill", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="bill", cascade="all, delete-orphan")

class BillLine(Base):
    __tablename__ = "bill_lines"
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"))
    description = Column(Text, nullable=False)
    qty = Column(Numeric(12,3), default=0)
    price = Column(Numeric(12,2), default=0)

    bill = relationship("Bill", back_populates="lines")

class Payment(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    payment_date = Column(Date, default=date.today)
    amount = Column(Numeric(12,2), default=0)
    method = Column(String(50), default="Bank Transfer")
    ref = Column(String(120))

    bill = relationship("Bill", back_populates="payments")

def init_db():
    Base.metadata.create_all(engine)

@app.context_processor
def inject_now():
    return {"now": datetime.utcnow()}

# ---------------------- Forms ----------------------
class SupplierForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[Optional()])
    phone = StringField("Phone", validators=[Optional()])
    address = TextAreaField("Address", validators=[Optional()])
    currency = StringField("Currency", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

class ItemForm(FlaskForm):
    sku = StringField("SKU", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    uom = StringField("UoM", validators=[Optional()])
    default_price = DecimalField("Default Price", validators=[Optional()], places=2, rounding=None)

class POLineSubForm(FlaskForm):
    item_id = SelectField("Item", coerce=int, validators=[DataRequired()])
    description = StringField("Description", validators=[Optional()])
    qty = DecimalField("Qty", validators=[DataRequired(), NumberRange(min=0.001)], places=3)
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2)

class POForm(FlaskForm):
    number = StringField("PO Number", validators=[DataRequired()])
    supplier_id = SelectField("Supplier", coerce=int, validators=[DataRequired()])
    order_date = DateField("Order Date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

class GRNForm(FlaskForm):
    grn_number = StringField("GRN Number", validators=[DataRequired()])
    received_date = DateField("Received Date", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

class BillForm(FlaskForm):
    supplier_id = SelectField("Supplier", coerce=int, validators=[DataRequired()])
    bill_number = StringField("Bill Number", validators=[DataRequired()])
    bill_date = DateField("Bill Date", validators=[Optional()])
    due_date = DateField("Due Date", validators=[Optional()])
    currency = StringField("Currency", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])

class PaymentForm(FlaskForm):
    bill_id = SelectField("Bill", coerce=int, validators=[DataRequired()])
    payment_date = DateField("Payment Date", validators=[Optional()])
    amount = DecimalField("Amount", validators=[DataRequired(), NumberRange(min=0.01)], places=2)
    method = StringField("Method", validators=[Optional()])
    ref = StringField("Reference", validators=[Optional()])

# ---------------------- Helpers ----------------------
def money(x):
    return f"{Decimal(x or 0):,.2f}"

app.jinja_env.filters["money"] = money

# ---------------------- Routes ----------------------
@app.route("/")
def index():
    s = Session()
    open_pos = s.query(PurchaseOrder).filter(PurchaseOrder.status.in_(["Open", "Partially Received"])).count()
    open_bills = s.query(Bill).filter(Bill.status.in_(["Open", "Partially Paid"])).count()
    suppliers = s.query(Supplier).count()
    total_ap = 0
    for b in s.query(Bill).all():
        paid = sum([float(p.amount) for p in b.payments])
        due = float(sum([float(l.qty) * float(l.price) for l in b.lines])) - paid
        total_ap += due
    return render_template("index.html", open_pos=open_pos, open_bills=open_bills, suppliers=suppliers, total_ap=total_ap)

# Suppliers
@app.route("/suppliers")
def suppliers():
    s = Session()
    data = s.query(Supplier).order_by(Supplier.name.asc()).all()
    return render_template("suppliers.html", data=data)

@app.route("/suppliers/new", methods=["GET","POST"])
def suppliers_new():
    form = SupplierForm()
    if form.validate_on_submit():
        s = Session()
        sup = Supplier(**form.data)
        s.add(sup)
        s.commit()
        flash("Supplier created","success")
        return redirect(url_for("suppliers"))
    return render_template("supplier_form.html", form=form, title="New Supplier")

@app.route("/suppliers/<int:supplier_id>/edit", methods=["GET","POST"])
def suppliers_edit(supplier_id):
    s = Session()
    sup = s.get(Supplier, supplier_id)
    form = SupplierForm(obj=sup)
    if form.validate_on_submit():
        for k, v in form.data.items():
            if hasattr(sup, k):
                setattr(sup, k, v)
        s.commit()
        flash("Supplier updated","success")
        return redirect(url_for("suppliers"))
    return render_template("supplier_form.html", form=form, title="Edit Supplier")

@app.route("/suppliers/<int:supplier_id>/delete", methods=["POST"])
def suppliers_delete(supplier_id):
    s = Session()
    sup = s.get(Supplier, supplier_id)
    s.delete(sup)
    s.commit()
    flash("Supplier deleted","info")
    return redirect(url_for("suppliers"))

# Items
@app.route("/items")
def items():
    s = Session()
    data = s.query(Item).order_by(Item.name.asc()).all()
    return render_template("items.html", data=data)

@app.route("/items/new", methods=["GET","POST"])
def items_new():
    form = ItemForm()
    if form.validate_on_submit():
        s = Session()
        it = Item(**form.data)
        s.add(it)
        s.commit()
        flash("Item created","success")
        return redirect(url_for("items"))
    return render_template("item_form.html", form=form, title="New Item")

@app.route("/items/<int:item_id>/edit", methods=["GET","POST"])
def items_edit(item_id):
    s = Session()
    it = s.get(Item, item_id)
    form = ItemForm(obj=it)
    if form.validate_on_submit():
        for k,v in form.data.items():
            if hasattr(it,k):
                setattr(it,k,v)
        s.commit()
        flash("Item updated","success")
        return redirect(url_for("items"))
    return render_template("item_form.html", form=form, title="Edit Item")

@app.route("/items/<int:item_id>/delete", methods=["POST"])
def items_delete(item_id):
    s = Session()
    it = s.get(Item, item_id)
    s.delete(it)
    s.commit()
    flash("Item deleted","info")
    return redirect(url_for("items"))

# Purchase Orders
@app.route("/pos")
def pos():
    s = Session()
    data = s.query(PurchaseOrder).order_by(PurchaseOrder.order_date.desc()).all()
    return render_template("pos.html", data=data)

@app.route("/pos/new", methods=["GET","POST"])
def pos_new():
    s = Session()
    form = POForm()
    form.supplier_id.choices = [(x.id, x.name) for x in s.query(Supplier).order_by(Supplier.name.asc()).all()]
    item_choices = [(x.id, f"{x.sku} - {x.name}") for x in s.query(Item).order_by(Item.sku.asc()).all()]
    if request.method == "POST":
        number = request.form.get("number")
        supplier_id = int(request.form.get("supplier_id"))
        order_date = request.form.get("order_date") or date.today().isoformat()
        notes = request.form.get("notes")
        # Lines
        lines = []
        idx = 0
        while True:
            if f"line-item_id-{idx}" in request.form:
                item_id = int(request.form.get(f"line-item_id-{idx}"))
                description = request.form.get(f"line-description-{idx}") or ""
                qty = Decimal(request.form.get(f"line-qty-{idx}") or "0")
                price = Decimal(request.form.get(f"line-price-{idx}") or "0")
                if qty > 0:
                    lines.append({"item_id": item_id, "description": description, "qty": qty, "price": price})
                idx += 1
            else:
                break
        po = PurchaseOrder(number=number, supplier_id=supplier_id, order_date=order_date, notes=notes)
        s.add(po)
        s.flush()
        for ln in lines:
            s.add(POLine(po_id=po.id, **ln))
        s.commit()
        flash("PO created","success")
        return redirect(url_for("pos"))
    return render_template("po_form.html", form=form, item_choices=item_choices)

@app.route("/pos/<int:po_id>")
def po_view(po_id):
    s = Session()
    po = s.get(PurchaseOrder, po_id)
    return render_template("po_view.html", po=po)

@app.route("/pos/<int:po_id>/receive", methods=["GET","POST"])
def po_receive(po_id):
    s = Session()
    po = s.get(PurchaseOrder, po_id)
    if request.method == "POST":
        grn_number = request.form.get("grn_number")
        received_date = request.form.get("received_date") or date.today().isoformat()
        grn = GoodsReceipt(po_id=po.id, grn_number=grn_number, received_date=received_date, notes=request.form.get("notes"))
        s.add(grn)
        s.flush()
        fully_received = True
        for ln in po.lines:
            qty_key = f"line-{ln.id}-qty_received"
            if qty_key in request.form:
                qty_received = Decimal(request.form.get(qty_key) or "0")
                if qty_received > 0:
                    s.add(GRNLine(grn_id=grn.id, po_line_id=ln.id, qty_received=qty_received))
                    ln.received_qty = Decimal(ln.received_qty or 0) + qty_received
            if ln.received_qty < ln.qty:
                fully_received = False
        po.status = "Closed" if fully_received else "Partially Received"
        s.commit()
        flash("Goods received recorded","success")
        return redirect(url_for("po_view", po_id=po.id))
    return render_template("po_receive.html", po=po)

# Bills (AP)
@app.route("/bills")
def bills():
    s = Session()
    data = s.query(Bill).order_by(Bill.bill_date.desc()).all()
    return render_template("bills.html", data=data)

@app.route("/bills/new", methods=["GET","POST"])
def bills_new():
    s = Session()
    form = BillForm()
    form.supplier_id.choices = [(x.id, x.name) for x in s.query(Supplier).order_by(Supplier.name.asc()).all()]
    if form.validate_on_submit():
        bill = Bill(
            supplier_id=form.supplier_id.data,
            bill_number=form.bill_number.data,
            bill_date=form.bill_date.data or date.today(),
            due_date=form.due_date.data,
            currency=form.currency.data or "SAR",
            notes=form.notes.data
        )
        s.add(bill)
        s.flush()
        # Parse lines
        idx = 0
        while True:
            if f"line-description-{idx}" in request.form:
                desc = request.form.get(f"line-description-{idx}")
                qty = Decimal(request.form.get(f"line-qty-{idx}") or "0")
                price = Decimal(request.form.get(f"line-price-{idx}") or "0")
                if qty > 0:
                    s.add(BillLine(bill_id=bill.id, description=desc, qty=qty, price=price))
                idx += 1
            else:
                break
        s.commit()
        flash("Bill created","success")
        return redirect(url_for("bills"))
    return render_template("bill_form.html", form=form)

@app.route("/bills/<int:bill_id>")
def bill_view(bill_id):
    s = Session()
    bill = s.get(Bill, bill_id)
    total = sum([float(l.qty)*float(l.price) for l in bill.lines])
    paid = sum([float(p.amount) for p in bill.payments])
    due = total - paid
    return render_template("bill_view.html", bill=bill, total=total, paid=paid, due=due)

@app.route("/bills/<int:bill_id>/delete", methods=["POST"])
def bill_delete(bill_id):
    s = Session()
    bill = s.get(Bill, bill_id)
    s.delete(bill)
    s.commit()
    flash("Bill deleted","info")
    return redirect(url_for("bills"))

# Convert PO to Bill
@app.route("/pos/<int:po_id>/to_bill", methods=["POST"])
def po_to_bill(po_id):
    s = Session()
    po = s.get(PurchaseOrder, po_id)
    bill = Bill(supplier_id=po.supplier_id, bill_number=f"INV-{po.number}", bill_date=date.today(), currency=po.supplier.currency or "SAR")
    s.add(bill)
    s.flush()
    for ln in po.lines:
        qty = ln.received_qty or 0
        if qty > 0:
            s.add(BillLine(bill_id=bill.id, description=ln.description or (ln.item.name if ln.item else "PO Line"), qty=qty, price=ln.price))
    s.commit()
    flash("Bill created from PO","success")
    return redirect(url_for("bill_view", bill_id=bill.id))

# Payments
@app.route("/payments", methods=["GET","POST"])
def payments():
    s = Session()
    form = PaymentForm()
    # Only list open/partially paid bills
    bills = []
    for b in s.query(Bill).order_by(Bill.bill_date.desc()).all():
        total = sum([float(l.qty)*float(l.price) for l in b.lines])
        paid = sum([float(p.amount) for p in b.payments])
        if paid < total:
            bills.append(b)
    form.bill_id.choices = [(b.id, f"{b.bill_number} - {b.supplier.name}") for b in bills]
    if form.validate_on_submit():
        pay = Payment(
            bill_id=form.bill_id.data,
            payment_date=form.payment_date.data or date.today(),
            amount=form.amount.data,
            method=form.method.data or "Bank Transfer",
            ref=form.ref.data
        )
        s.add(pay)
        # Update bill status
        b = s.get(Bill, form.bill_id.data)
        total = sum([float(l.qty)*float(l.price) for l in b.lines])
        paid = sum([float(p.amount) for p in b.payments]) + float(form.amount.data)
        if paid >= total - 0.005:
            b.status = "Paid"
        else:
            b.status = "Partially Paid"
        s.commit()
        flash("Payment recorded","success")
        return redirect(url_for("payments"))
    payments_data = s.query(Payment).order_by(Payment.payment_date.desc()).all()
    return render_template("payments.html", form=form, payments_data=payments_data)

# Reports
@app.route("/reports")
def reports():
    s = Session()
    # AP Aging: sum by supplier of due amounts
    aging = []
    for sup in s.query(Supplier).order_by(Supplier.name.asc()).all():
        total_due = 0.0
        for b in sup.bills:
            total = sum([float(l.qty)*float(l.price) for l in b.lines])
            paid = sum([float(p.amount) for p in b.payments])
            due = total - paid
            if due > 0:
                total_due += due
        aging.append((sup, total_due))
    aging = [(sup, amt) for sup, amt in aging if amt > 0]
    # Spend by month (PO value by order_date)
    spend_by_month = {}
    for po in s.query(PurchaseOrder).all():
        m = po.order_date.strftime("%Y-%m")
        val = sum([float(ln.qty)*float(ln.price) for ln in po.lines])
        spend_by_month[m] = spend_by_month.get(m, 0) + val
    spend = sorted(spend_by_month.items())
    return render_template("reports.html", aging=aging, spend=spend)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
