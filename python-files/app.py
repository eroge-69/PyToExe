import sys
import os
import sqlite3
import json
import csv
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
    QStackedWidget, QHeaderView, QFormLayout, QDialog, QDialogButtonBox,
    QComboBox, QTextEdit, QMessageBox, QFileDialog, QMenu, QGridLayout,
    QSizePolicy, QDateEdit
)
from PyQt5.QtGui import QFont, QColor, QPainter, QPdfWriter, QIcon, QFontDatabase
from PyQt5.QtCore import Qt, QDateTime, QRectF, QPoint, QDate

# --- Dependency Check ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet
except ImportError:
    QMessageBox.critical(None, "Missing Dependency", "ReportLab is required.\nPlease install it using: pip install reportlab")
    sys.exit(1)

try:
    import pyqtgraph as pg
except ImportError:
    QMessageBox.critical(None, "Missing Dependency", "PyQtGraph is required for reporting.\nPlease install it using: pip install pyqtgraph")
    sys.exit(1)


# --- FONT AWESOME ICONS ---
# In a real distributable app, you'd bundle the font file.
# For this script, we'll assume it's in the same directory or use a known path.
FONT_AWESOME_PATH = "fontawesome-webfont.ttf" # Download from Font Awesome 4.7 website

# --- STYLESHEET for a professional UI ---
STYLESHEET = """
QWidget {
    background-color: #F8F9FA;
    color: #212529;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 14px;
}
QMainWindow {
    background-color: #DEE2E6;
}
QStackedWidget {
    background-color: #FFFFFF;
    border-radius: 10px;
    border: 1px solid #DEE2E6;
}
/* Navigation Buttons with Icons */
#NavButton {
    background-color: transparent;
    border: none;
    color: #495057;
    padding: 15px;
    text-align: left;
    border-radius: 8px;
    font-weight: bold;
    font-size: 15px;
}
#NavButton:hover {
    background-color: #E9ECEF;
}
#NavButton:checked {
    background-color: #007BFF;
    color: #FFFFFF;
}
QLineEdit, QTextEdit, QComboBox, QDateEdit {
    background-color: #FFFFFF;
    border: 1px solid #CED4DA;
    padding: 10px;
    border-radius: 5px;
    selection-background-color: #007BFF;
    selection-color: #FFFFFF;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus {
    border: 1px solid #80BDFF;
}
QPushButton {
    background-color: #007BFF;
    color: #FFFFFF;
    border: none;
    padding: 12px 18px;
    border-radius: 5px;
    font-weight: bold;
    min-width: 80px;
}
QPushButton:hover {
    background-color: #0069D9;
}
QPushButton#DeleteButton {
    background-color: #DC3545;
}
QPushButton#DeleteButton:hover {
    background-color: #C82333;
}
QTableWidget {
    background-color: #FFFFFF;
    border: 1px solid #DEE2E6;
    gridline-color: #DEE2E6;
    selection-background-color: #007BFF;
    selection-color: #FFFFFF;
}
QHeaderView::section {
    background-color: #F8F9FA;
    padding: 10px;
    border: none;
    border-bottom: 2px solid #DEE2E6;
    font-weight: bold;
    color: #495057;
}
QMenu {
    background-color: #FFFFFF;
    border: 1px solid #CED4DA;
    color: #212529;
}
QMenu::item:selected {
    background-color: #007BFF;
    color: #FFFFFF;
}
#TitleLabel { font-size: 28px; font-weight: bold; color: #212529; padding-bottom: 5px;}
#SubtitleLabel { font-size: 18px; color: #6C757D; }
#Card { background-color: #FFFFFF; border-radius: 10px; border: 1px solid #DEE2E6;}
#CardTitle { font-size: 16px; font-weight: bold; color: #6C757D; }
#CardValue { font-size: 32px; font-weight: bold; color: #007BFF; }
"""

# --- DATABASE MANAGEMENT ---
DB_FILE = 'shop_data.db'

class DatabaseManager:
    # ... (code unchanged)
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute('PRAGMA foreign_keys = ON;')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY, value TEXT
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL,
            price REAL NOT NULL, stock INTEGER, hsn_sac TEXT, gst_rate REAL
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, phone TEXT,
            address TEXT, gstin TEXT
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id TEXT PRIMARY KEY, customer_id TEXT, date TEXT, total REAL, items TEXT, payment_mode TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS services (
            id TEXT PRIMARY KEY, customer_id TEXT, product_name TEXT,
            issue TEXT, status TEXT, date TEXT,
            FOREIGN KEY(customer_id) REFERENCES customers(id)
        )''')
        self.conn.commit()

    def get_setting(self, key, default=None):
        self.cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = self.cursor.fetchone()
        return result[0] if result else default

    def set_setting(self, key, value):
        self.cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        self.conn.commit()

    def execute_query(self, query, params=(), fetch=None):
        self.cursor.execute(query, params)
        if fetch == 'one': result = self.cursor.fetchone()
        elif fetch == 'all': result = self.cursor.fetchall()
        else: result = None
        self.conn.commit()
        return result

    def get_next_id(self, prefix):
        key = f"last_{prefix}_id"
        last_id = int(self.get_setting(key, '0'))
        next_id = last_id + 1
        self.set_setting(key, str(next_id))
        return f"{prefix.upper()}{next_id:04d}"

# --- INVOICE PDF GENERATOR ---
class InvoiceGenerator:
    # ... (code largely unchanged)
    def __init__(self, settings, sale_data, customer_data, items_data):
        self.settings = settings
        self.sale = sale_data
        self.customer = customer_data
        self.items = items_data
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()

    def generate(self, file_path):
        c = canvas.Canvas(file_path, pagesize=A4)
        self.draw_header(c)
        self.draw_customer_details(c)
        y_pos = self.draw_items_table(c)
        self.draw_totals(c, y_pos)
        self.draw_footer(c)
        c.save()

    def draw_header(self, c):
        c.setFont("Helvetica-Bold", 18)
        c.drawString(20 * mm, self.height - 20 * mm, self.settings.get('shop_name', 'Shop Name'))
        c.setFont("Helvetica", 10)
        address_lines = self.settings.get('shop_address', 'Shop Address').split('\n')
        y = self.height - 25 * mm
        for line in address_lines:
            c.drawString(20 * mm, y, line)
            y -= 4 * mm
        c.drawString(20 * mm, y, f"GSTIN: {self.settings.get('shop_gstin', 'N/A')}")
        c.setFont("Helvetica-Bold", 14)
        c.drawRightString(self.width - 20 * mm, self.height - 20 * mm, "TAX INVOICE")

    def draw_customer_details(self, c):
        c.setStrokeColor(colors.lightgrey)
        c.line(20 * mm, self.height - 40 * mm, self.width - 20 * mm, self.height - 40 * mm)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(20 * mm, self.height - 45 * mm, "Bill To:")
        c.setFont("Helvetica", 10)
        c.drawString(20 * mm, self.height - 50 * mm, self.customer['name'])
        y = self.height - 55 * mm
        if self.customer['address']:
            for line in self.customer['address'].split('\n'):
                c.drawString(20 * mm, y, line)
                y -= 4 * mm
        c.drawString(20 * mm, y, f"Phone: {self.customer['phone']}")
        if self.customer.get('gstin'):
            y -= 4 * mm
            c.drawString(20 * mm, y, f"GSTIN: {self.customer['gstin']}")

        c.drawRightString(self.width - 20 * mm, self.height - 45 * mm, f"Invoice No: {self.sale['id']}")
        date = QDateTime.fromString(self.sale['date'], Qt.ISODate).toString("dd-MM-yyyy")
        c.drawRightString(self.width - 20 * mm, self.height - 50 * mm, f"Date: {date}")
        if self.sale.get('payment_mode'):
             c.drawRightString(self.width - 20 * mm, self.height - 55 * mm, f"Payment: {self.sale['payment_mode']}")
        c.line(20 * mm, self.height - 70 * mm, self.width - 20 * mm, self.height - 70 * mm)

    def draw_items_table(self, c):
        data = [["#", "Item Description", "HSN/SAC", "Qty", "Rate", "Taxable Value", "GST %", "Total"]]
        for i, item in enumerate(self.items):
            taxable = item['qty'] * item['price']
            total = taxable * (1 + item['gst_rate'] / 100)
            data.append([
                str(i + 1), item['name'], item['hsn_sac'], str(item['qty']),
                f"{item['price']:.2f}", f"{taxable:.2f}", f"{item['gst_rate']}%", f"{total:.2f}"
            ])
        
        table = Table(data, colWidths=[10*mm, 60*mm, 20*mm, 10*mm, 20*mm, 25*mm, 15*mm, 20*mm])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4C566A")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10), ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#ECEFF4")),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor("#2E3440"))
        ])
        table.setStyle(style)
        
        table.wrapOn(c, self.width, self.height)
        table_height = table._height
        table.drawOn(c, 20 * mm, self.height - 80 * mm - table_height)
        return self.height - 80 * mm - table_height - 10 * mm

    def draw_totals(self, c, y_pos):
        sub_total = sum(item['qty'] * item['price'] for item in self.items)
        total_gst = sum(item['qty'] * item['price'] * (item['gst_rate'] / 100) for item in self.items)
        cgst = total_gst / 2
        sgst = total_gst / 2
        
        c.setFont("Helvetica", 10)
        c.drawRightString(self.width - 45 * mm, y_pos, "Subtotal:")
        c.drawRightString(self.width - 20 * mm, y_pos, f"₹ {sub_total:.2f}")
        c.drawRightString(self.width - 45 * mm, y_pos - 5*mm, "CGST:")
        c.drawRightString(self.width - 20 * mm, y_pos - 5*mm, f"₹ {cgst:.2f}")
        c.drawRightString(self.width - 45 * mm, y_pos - 10*mm, "SGST:")
        c.drawRightString(self.width - 20 * mm, y_pos - 10*mm, f"₹ {sgst:.2f}")
        c.line(self.width - 60*mm, y_pos - 13*mm, self.width - 20*mm, y_pos - 13*mm)
        c.setFont("Helvetica-Bold", 12)
        c.drawRightString(self.width - 45 * mm, y_pos - 18*mm, "Grand Total:")
        c.drawRightString(self.width - 20 * mm, y_pos - 18*mm, f"₹ {self.sale['total']:.2f}")

    def draw_footer(self, c):
        terms = self.settings.get('invoice_terms', '1. Goods once sold will not be taken back.\n2. Warranty as per manufacturer policy.')
        p = Paragraph(terms.replace('\n', '<br/>'), self.styles['Normal'])
        p.wrapOn(c, 100 * mm, 40 * mm)
        p.drawOn(c, 20 * mm, 40 * mm)
        c.setFont("Helvetica", 8)
        c.drawCentredString(self.width / 2, 20 * mm, "This is a computer-generated invoice.")

# --- UI DIALOGS ---
class SetupDialog(QDialog):
    # ... (code unchanged)
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Initial Shop Setup")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.shop_name = QLineEdit()
        self.shop_address = QTextEdit()
        self.shop_gstin = QLineEdit()
        self.shop_phone = QLineEdit()

        form_layout.addRow("Shop Name:", self.shop_name)
        form_layout.addRow("Shop Address:", self.shop_address)
        form_layout.addRow("GSTIN:", self.shop_gstin)
        form_layout.addRow("Phone:", self.shop_phone)

        buttons = QDialogButtonBox(QDialogButtonBox.Save)
        buttons.accepted.connect(self.accept)
        
        layout.addLayout(form_layout)
        layout.addWidget(buttons)

    def get_details(self):
        return {
            'shop_name': self.shop_name.text(),
            'shop_address': self.shop_address.toPlainText(),
            'shop_gstin': self.shop_gstin.text(),
            'shop_phone': self.shop_phone.text()
        }

class SaleDetailsDialog(QDialog):
    # ... (code unchanged)
    def __init__(self, sale_id, items_json, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Details for Sale {sale_id}")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Item", "HSN/SAC", "Qty", "Rate", "Total"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        items = json.loads(items_json)
        table.setRowCount(len(items))
        for row, item in enumerate(items):
            total = item['qty'] * item['price'] * (1 + item['gst_rate'] / 100)
            table.setItem(row, 0, QTableWidgetItem(item['name']))
            table.setItem(row, 1, QTableWidgetItem(item['hsn_sac']))
            table.setItem(row, 2, QTableWidgetItem(str(item['qty'])))
            table.setItem(row, 3, QTableWidgetItem(f"{item['price']:.2f}"))
            table.setItem(row, 4, QTableWidgetItem(f"{total:.2f}"))
        
        layout.addWidget(table)
        
# --- UI PAGES ---
class DashboardPage(QWidget):
    # ... (code enhanced)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(25)
        title = QLabel("Dashboard"); title.setObjectName("TitleLabel")
        layout.addWidget(title)
        
        cards_layout = QGridLayout(); cards_layout.setSpacing(25)
        self.total_sales_card = self.create_stat_card("Total Revenue", "₹ 0")
        self.today_sales_card = self.create_stat_card("Today's Revenue", "₹ 0")
        self.pending_services_card = self.create_stat_card("Pending Services", "0")
        self.total_customers_card = self.create_stat_card("Total Customers", "0")
        
        cards_layout.addWidget(self.total_sales_card, 0, 0)
        cards_layout.addWidget(self.today_sales_card, 0, 1)
        cards_layout.addWidget(self.pending_services_card, 1, 0)
        cards_layout.addWidget(self.total_customers_card, 1, 1)

        layout.addLayout(cards_layout)
        layout.addStretch()

    def create_stat_card(self, title_text, value_text):
        card = QWidget(); card.setObjectName("Card")
        card_layout = QVBoxLayout(card); card_layout.setSpacing(10)
        title_label = QLabel(title_text); title_label.setObjectName("CardTitle")
        value_label = QLabel(value_text); value_label.setObjectName("CardValue")
        card_layout.addWidget(title_label); card_layout.addWidget(value_label)
        return card

    def update_stats(self):
        total_rev = self.db_manager.execute_query("SELECT SUM(total) FROM sales", fetch='one')[0] or 0
        self.total_sales_card.findChild(QLabel, "CardValue").setText(f"₹ {total_rev:,.2f}")
        
        today_str = QDateTime.currentDateTime().toString("yyyy-MM-dd")
        today_rev = self.db_manager.execute_query(
            "SELECT SUM(total) FROM sales WHERE date LIKE ?", (f"{today_str}%",), fetch='one')[0] or 0
        self.today_sales_card.findChild(QLabel, "CardValue").setText(f"₹ {today_rev:,.2f}")

        pending_count = self.db_manager.execute_query("SELECT COUNT(*) FROM services WHERE status='Pending'", fetch='one')[0]
        self.pending_services_card.findChild(QLabel, "CardValue").setText(str(pending_count))
        
        cust_count = self.db_manager.execute_query("SELECT COUNT(*) FROM customers", fetch='one')[0]
        self.total_customers_card.findChild(QLabel, "CardValue").setText(str(cust_count))

class SalesPage(QWidget):
    # ... (code enhanced)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_invoice_items = []
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25,25,25,25); layout.setSpacing(25)

        new_sale_widget = QWidget()
        new_sale_layout = QVBoxLayout(new_sale_widget); new_sale_layout.setSpacing(15)
        title = QLabel("New Sale"); title.setObjectName("SubtitleLabel")
        new_sale_layout.addWidget(title)
        
        form_layout = QFormLayout()
        self.customer_combo = QComboBox()
        self.product_combo = QComboBox()
        self.qty_edit = QLineEdit("1")
        self.payment_mode_combo = QComboBox(); self.payment_mode_combo.addItems(["Cash", "Card", "UPI", "Bank Transfer"])
        form_layout.addRow("Customer:", self.customer_combo)
        form_layout.addRow("Product/Service:", self.product_combo)
        form_layout.addRow("Quantity:", self.qty_edit)
        form_layout.addRow("Payment Mode:", self.payment_mode_combo)
        
        add_item_btn = QPushButton("Add Item"); add_item_btn.clicked.connect(self.add_item_to_invoice)
        
        self.invoice_table = QTableWidget()
        self.invoice_table.setColumnCount(4); self.invoice_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total"])
        self.invoice_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        self.total_label = QLabel("Total: ₹ 0.00"); self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setObjectName("SubtitleLabel")
        
        process_sale_btn = QPushButton("Process Sale"); process_sale_btn.clicked.connect(self.process_sale)

        new_sale_layout.addLayout(form_layout)
        new_sale_layout.addWidget(add_item_btn)
        new_sale_layout.addWidget(self.invoice_table)
        new_sale_layout.addWidget(self.total_label)
        new_sale_layout.addWidget(process_sale_btn)
        
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget); history_layout.setSpacing(15)
        history_title = QLabel("Sales History"); history_title.setObjectName("SubtitleLabel")
        
        self.search_edit = QLineEdit(); self.search_edit.setPlaceholderText("Search by Invoice ID or Customer Name...")
        self.search_edit.textChanged.connect(self.load_sales_history)
        
        self.sales_history_table = QTableWidget()
        self.sales_history_table.setColumnCount(4); self.sales_history_table.setHorizontalHeaderLabels(["ID", "Customer", "Date", "Total"])
        self.sales_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.sales_history_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.sales_history_table.cellDoubleClicked.connect(self.show_sale_details)

        history_layout.addWidget(history_title); history_layout.addWidget(self.search_edit); history_layout.addWidget(self.sales_history_table)
        
        layout.addWidget(new_sale_widget, 1); layout.addWidget(history_widget, 2)
    
    def show_sale_details(self, row, column):
        sale_id = self.sales_history_table.item(row, 0).text()
        items_json = self.db_manager.execute_query("SELECT items FROM sales WHERE id=?", (sale_id,), fetch='one')[0]
        dialog = SaleDetailsDialog(sale_id, items_json, self)
        dialog.exec_()
    
    def load_data(self):
        self.customer_combo.clear()
        customers = self.db_manager.execute_query("SELECT id, name FROM customers", fetch='all')
        for cust_id, name in customers: self.customer_combo.addItem(name, cust_id)
        
        self.product_combo.clear()
        products = self.db_manager.execute_query("SELECT id, name, price FROM products", fetch='all')
        for prod_id, name, price in products: self.product_combo.addItem(f"{name} (₹{price})", prod_id)

        self.load_sales_history()

    def add_item_to_invoice(self):
        prod_id = self.product_combo.currentData()
        prod_data = self.db_manager.execute_query("SELECT name, type, price, stock, hsn_sac, gst_rate FROM products WHERE id=?", (prod_id,), fetch='one')
        try: qty = int(self.qty_edit.text()); assert qty > 0
        except (ValueError, AssertionError):
            QMessageBox.warning(self, "Invalid Quantity", "Please enter a valid positive number.")
            return

        if prod_data[1] == 'Good' and qty > prod_data[3]:
            QMessageBox.warning(self, "Out of Stock", f"Only {prod_data[3]} units of {prod_data[0]} available.")
            return
            
        self.current_invoice_items.append({
            "id": prod_id, "name": prod_data[0], "qty": qty, "price": prod_data[2],
            "hsn_sac": prod_data[4], "gst_rate": prod_data[5]
        })
        self.update_invoice_table()

    def update_invoice_table(self):
        self.invoice_table.setRowCount(len(self.current_invoice_items))
        total_cost = 0
        for row, item in enumerate(self.current_invoice_items):
            item_total = item['qty'] * item['price'] * (1 + item['gst_rate'] / 100)
            total_cost += item_total
            self.invoice_table.setItem(row, 0, QTableWidgetItem(item['name']))
            self.invoice_table.setItem(row, 1, QTableWidgetItem(str(item['qty'])))
            self.invoice_table.setItem(row, 2, QTableWidgetItem(f"{item['price']:.2f}"))
            self.invoice_table.setItem(row, 3, QTableWidgetItem(f"{item_total:.2f}"))
        self.total_label.setText(f"Grand Total: ₹ {total_cost:.2f}")

    def process_sale(self):
        if not self.current_invoice_items: return
        cust_id = self.customer_combo.currentData()
        total = sum(item['qty'] * item['price'] * (1 + item['gst_rate'] / 100) for item in self.current_invoice_items)
        sale_id = self.db_manager.get_next_id('sale')
        date = QDateTime.currentDateTime().toString(Qt.ISODate)
        payment_mode = self.payment_mode_combo.currentText()
        
        items_json = json.dumps(self.current_invoice_items)
        self.db_manager.execute_query("INSERT INTO sales (id, customer_id, date, total, items, payment_mode) VALUES (?, ?, ?, ?, ?, ?)",
                                      (sale_id, cust_id, date, total, items_json, payment_mode))
        
        for item in self.current_invoice_items:
            self.db_manager.execute_query("UPDATE products SET stock = stock - ? WHERE id=? AND type='Good'", (item['qty'], item['id']))
        
        reply = QMessageBox.question(self, "Sale Processed", "Sale successfully recorded. Do you want to generate an invoice?", 
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        if reply == QMessageBox.Yes:
            self.generate_invoice(sale_id, cust_id, total, date, self.current_invoice_items, payment_mode)
            
        self.current_invoice_items = []; self.update_invoice_table()
        self.load_sales_history()
        self.window().update_all_pages()

    def generate_invoice(self, sale_id, cust_id, total, date, items, payment_mode):
        settings = {k: self.db_manager.get_setting(k) for k in ['shop_name', 'shop_address', 'shop_gstin', 'invoice_terms']}
        sale_data = {'id': sale_id, 'date': date, 'total': total, 'payment_mode': payment_mode}
        cust_data_tuple = self.db_manager.execute_query("SELECT name, phone, address, gstin FROM customers WHERE id=?", (cust_id,), fetch='one')
        customer_data = {'name': cust_data_tuple[0], 'phone': cust_data_tuple[1], 'address': cust_data_tuple[2], 'gstin': cust_data_tuple[3]}
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Invoice PDF", f"{sale_id}.pdf", "PDF Files (*.pdf)")
        if file_path:
            try:
                generator = InvoiceGenerator(settings, sale_data, customer_data, items)
                generator.generate(file_path)
                QMessageBox.information(self, "Success", f"Invoice saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to generate PDF: {e}")

    def load_sales_history(self):
        search_term = self.search_edit.text()
        query = "SELECT s.id, c.name, s.date, s.total FROM sales s JOIN customers c ON s.customer_id = c.id"
        params = []
        if search_term:
            query += " WHERE s.id LIKE ? OR c.name LIKE ?"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        query += " ORDER BY s.date DESC"
        
        sales = self.db_manager.execute_query(query, params, fetch='all')
        self.sales_history_table.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            self.sales_history_table.setItem(row, 0, QTableWidgetItem(sale[0]))
            self.sales_history_table.setItem(row, 1, QTableWidgetItem(sale[1]))
            date = QDateTime.fromString(sale[2], Qt.ISODate).toString("dd-MM-yyyy hh:mm")
            self.sales_history_table.setItem(row, 2, QTableWidgetItem(date))
            self.sales_history_table.setItem(row, 3, QTableWidgetItem(f"₹ {sale[3]:.2f}"))

class CustomersPage(QWidget):
    # ... (code enhanced with search and delete)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)

        title_layout = QHBoxLayout()
        title = QLabel("Customer Management"); title.setObjectName("TitleLabel")
        title_layout.addWidget(title)
        title_layout.addStretch()
        add_btn = QPushButton("Add New Customer"); add_btn.clicked.connect(lambda: self.show_add_edit_customer_dialog())
        title_layout.addWidget(add_btn)
        layout.addLayout(title_layout)

        self.search_edit = QLineEdit(); self.search_edit.setPlaceholderText("Search by Name or Phone...")
        self.search_edit.textChanged.connect(self.load_data)
        layout.addWidget(self.search_edit)

        self.table = QTableWidget()
        self.table.setColumnCount(5); self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Address", "GSTIN"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)

    def load_data(self):
        search_term = self.search_edit.text()
        query = "SELECT id, name, phone, address, gstin FROM customers"
        params = []
        if search_term:
            query += " WHERE name LIKE ? OR phone LIKE ?"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        query += " ORDER BY name"
        customers = self.db_manager.execute_query(query, params, fetch='all')
        self.table.setRowCount(len(customers))
        for row, cust in enumerate(customers):
            for col, data in enumerate(cust): self.table.setItem(row, col, QTableWidgetItem(str(data) if data else ""))

    def show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0: return
        cust_id = self.table.item(row, 0).text()
        
        menu = QMenu()
        edit_action = menu.addAction("Edit Customer")
        delete_action = menu.addAction("Delete Customer")
        
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == edit_action:
            self.show_add_edit_customer_dialog(cust_id)
        elif action == delete_action:
            self.delete_customer(cust_id)
            
    def delete_customer(self, cust_id):
        reply = QMessageBox.warning(self, "Delete Customer", 
                                    f"Are you sure you want to delete customer {cust_id}?\nThis cannot be undone.",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                self.db_manager.execute_query("DELETE FROM customers WHERE id=?", (cust_id,))
                self.load_data()
            except sqlite3.IntegrityError:
                QMessageBox.critical(self, "Error", "Cannot delete customer. They are linked to existing sales or services.")

    def show_add_edit_customer_dialog(self, customer_id=None):
        dialog = QDialog(self)
        form = QFormLayout(dialog)
        name_edit = QLineEdit(); phone_edit = QLineEdit(); address_edit = QTextEdit(); gstin_edit = QLineEdit()
        
        if customer_id:
            dialog.setWindowTitle("Edit Customer")
            cust_data = self.db_manager.execute_query("SELECT name, phone, address, gstin FROM customers WHERE id=?", (customer_id,), fetch='one')
            name_edit.setText(cust_data[0]); phone_edit.setText(cust_data[1]); address_edit.setPlainText(cust_data[2]); gstin_edit.setText(cust_data[3])
        else:
            dialog.setWindowTitle("Add Customer")

        form.addRow("Name:", name_edit); form.addRow("Phone:", phone_edit); form.addRow("Address:", address_edit); form.addRow("GSTIN (Optional):", gstin_edit)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject)
        form.addWidget(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name=name_edit.text(); phone=phone_edit.text(); address=address_edit.toPlainText(); gstin=gstin_edit.text()
            if not name: QMessageBox.warning(self, "Input Error", "Customer name cannot be empty."); return
            
            if customer_id:
                self.db_manager.execute_query("UPDATE customers SET name=?, phone=?, address=?, gstin=? WHERE id=?", (name, phone, address, gstin, customer_id))
            else:
                cust_id = self.db_manager.get_next_id('cust')
                self.db_manager.execute_query("INSERT INTO customers (id, name, phone, address, gstin) VALUES (?, ?, ?, ?, ?)", (cust_id, name, phone, address, gstin))
            self.load_data()
            self.window().update_all_pages()

class InventoryPage(QWidget):
    # ... (code enhanced with search and delete)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)

        title_layout = QHBoxLayout()
        title = QLabel("Inventory Management"); title.setObjectName("TitleLabel")
        title_layout.addWidget(title)
        title_layout.addStretch()
        add_btn = QPushButton("Add Product/Service")
        add_btn.clicked.connect(lambda: self.show_add_edit_product_dialog())
        title_layout.addWidget(add_btn)
        layout.addLayout(title_layout)

        self.search_edit = QLineEdit(); self.search_edit.setPlaceholderText("Search by Name or ID...")
        self.search_edit.textChanged.connect(self.load_data)
        layout.addWidget(self.search_edit)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Price", "Stock", "HSN/SAC", "GST %"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.table)
    
    def load_data(self):
        search_term = self.search_edit.text()
        query = "SELECT id, name, type, price, stock, hsn_sac, gst_rate FROM products"
        params = []
        if search_term:
            query += " WHERE name LIKE ? OR id LIKE ?"
            params.extend([f"%{search_term}%", f"%{search_term}%"])
        query += " ORDER BY name"
        
        products = self.db_manager.execute_query(query, params, fetch='all')
        self.table.setRowCount(len(products))
        for row, p in enumerate(products):
            for i, data in enumerate(p):
                item_text = ""
                if i==3: item_text=f"₹ {data:.2f}"
                elif i==4: item_text=str(data) if p[2]=='Good' else 'N/A'
                elif i==6: item_text=f"{data}%"
                else: item_text=str(data or "")
                self.table.setItem(row, i, QTableWidgetItem(item_text))

    def show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0: return
        product_id = self.table.item(row, 0).text()
        
        menu = QMenu()
        edit_action = menu.addAction("Edit Item")
        delete_action = menu.addAction("Delete Item")
        
        action = menu.exec_(self.table.mapToGlobal(pos))
        if action == edit_action:
            self.show_add_edit_product_dialog(product_id)
        elif action == delete_action:
            self.delete_product(product_id)

    def delete_product(self, product_id):
        reply = QMessageBox.warning(self, "Delete Product", f"Are you sure you want to delete {product_id}?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.db_manager.execute_query("DELETE FROM products WHERE id=?", (product_id,))
            self.load_data()
            self.window().update_all_pages()

    def show_add_edit_product_dialog(self, product_id=None):
        dialog = QDialog(self); dialog.setMinimumWidth(400)
        form = QFormLayout(dialog)
        name_edit=QLineEdit(); type_combo=QComboBox(); type_combo.addItems(["Good", "Service"])
        price_edit=QLineEdit(); stock_edit=QLineEdit("0"); hsn_edit=QLineEdit()
        gst_combo=QComboBox(); gst_combo.addItems(["0", "5", "12", "18", "28"])
        
        if product_id:
            dialog.setWindowTitle("Edit Product/Service")
            p_data = self.db_manager.execute_query("SELECT * FROM products WHERE id=?",(product_id,),fetch='one')
            name_edit.setText(p_data[1]); type_combo.setCurrentText(p_data[2]); price_edit.setText(str(p_data[3]))
            stock_edit.setText(str(p_data[4] if p_data[4]!=-1 else 0)); hsn_edit.setText(p_data[5]); gst_combo.setCurrentText(str(int(p_data[6])))
        else: dialog.setWindowTitle("Add Product/Service")
        
        form.addRow("Name:", name_edit); form.addRow("Type:", type_combo); form.addRow("Price:", price_edit)
        form.addRow("Stock (for Goods):", stock_edit); form.addRow("HSN/SAC Code:", hsn_edit)
        form.addRow("GST Rate (%):", gst_combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); form.addWidget(buttons)

        if dialog.exec_() == QDialog.Accepted:
            name=name_edit.text(); p_type=type_combo.currentText(); hsn=hsn_edit.text(); gst=float(gst_combo.currentText())
            try: price=float(price_edit.text()); stock=int(stock_edit.text()) if p_type == 'Good' else -1
            except ValueError: QMessageBox.warning(self, "Invalid Input", "Price/stock must be numbers."); return
            if not name: QMessageBox.warning(self, "Invalid Input", "Name is required."); return
            
            if product_id:
                self.db_manager.execute_query("UPDATE products SET name=?, type=?, price=?, stock=?, hsn_sac=?, gst_rate=? WHERE id=?",
                                              (name, p_type, price, stock, hsn, gst, product_id))
            else:
                p_id = self.db_manager.get_next_id('prod' if p_type == 'Good' else 'serv')
                self.db_manager.execute_query("INSERT INTO products VALUES (?,?,?,?,?,?,?)", (p_id, name, p_type, price, stock, hsn, gst))
            self.load_data(); self.window().update_all_pages()

class ServicesPage(QWidget):
    # ... (code unchanged)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25,25,25,25); layout.setSpacing(25)

        new_widget = QWidget()
        new_layout = QVBoxLayout(new_widget); new_layout.setSpacing(15)
        title = QLabel("New Service Request"); title.setObjectName("SubtitleLabel")
        new_layout.addWidget(title)
        
        form_layout = QFormLayout()
        self.customer_combo = QComboBox()
        self.product_name_edit = QLineEdit()
        self.issue_desc_edit = QTextEdit()
        form_layout.addRow("Customer:", self.customer_combo)
        form_layout.addRow("Product Name:", self.product_name_edit)
        form_layout.addRow("Issue Description:", self.issue_desc_edit)
        
        add_job_btn = QPushButton("Log Service Job"); add_job_btn.clicked.connect(self.log_service_job)
        new_layout.addLayout(form_layout); new_layout.addWidget(add_job_btn); new_layout.addStretch()
        
        history_widget = QWidget()
        history_layout = QVBoxLayout(history_widget); history_layout.setSpacing(15)
        history_title = QLabel("Service History"); history_title.setObjectName("SubtitleLabel")
        
        self.table = QTableWidget()
        self.table.setColumnCount(5); self.table.setHorizontalHeaderLabels(["Job ID", "Customer", "Product", "Date", "Status"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)
        
        history_layout.addWidget(history_title); history_layout.addWidget(self.table)
        layout.addWidget(new_widget, 1); layout.addWidget(history_widget, 2)

    def load_data(self):
        self.customer_combo.clear()
        customers = self.db_manager.execute_query("SELECT id, name FROM customers", fetch='all')
        for cust_id, name in customers: self.customer_combo.addItem(name, cust_id)
        self.load_service_history()

    def log_service_job(self):
        cust_id = self.customer_combo.currentData()
        product = self.product_name_edit.text()
        issue = self.issue_desc_edit.toPlainText()
        if not all([cust_id, product, issue]):
            QMessageBox.warning(self, "Incomplete Form", "Please fill in all fields."); return
        
        job_id = self.db_manager.get_next_id('job')
        date = QDateTime.currentDateTime().toString(Qt.ISODate)
        self.db_manager.execute_query("INSERT INTO services VALUES (?,?,?,?,?,?)", (job_id, cust_id, product, issue, "Pending", date))
        QMessageBox.information(self, "Success", "New service job logged.")
        self.product_name_edit.clear(); self.issue_desc_edit.clear()
        self.load_service_history(); self.window().update_all_pages()

    def load_service_history(self):
        services = self.db_manager.execute_query("SELECT s.id, c.name, s.product_name, s.date, s.status FROM services s JOIN customers c ON s.customer_id = c.id ORDER BY s.date DESC", fetch='all')
        self.table.setRowCount(len(services))
        for row, service in enumerate(services):
            for col, data in enumerate(service):
                if col==3: data = QDateTime.fromString(data, Qt.ISODate).toString("dd-MM-yyyy")
                item = QTableWidgetItem(data)
                if col==4:
                    if data == 'Pending': item.setForeground(QColor("#DC3545")) # Red
                    elif data == 'Completed': item.setForeground(QColor("#28A745")) # Green
                    elif data == 'In Progress': item.setForeground(QColor("#FFC107")) # Yellow
                self.table.setItem(row, col, item)

    def show_context_menu(self, pos):
        row = self.table.rowAt(pos.y())
        if row < 0: return
        job_id = self.table.item(row, 0).text()
        
        menu = QMenu()
        statuses = ["Pending", "In Progress", "Completed", "Cannot Repair"]
        for status in statuses:
            action = menu.addAction(f"Mark as {status}")
            action.triggered.connect(lambda chk, s=status, j=job_id: self.update_status(j, s))
        menu.exec_(self.table.mapToGlobal(pos))
    
    def update_status(self, job_id, status):
        self.db_manager.execute_query("UPDATE services SET status=? WHERE id=?", (status, job_id))
        self.load_service_history(); self.window().update_all_pages()

class ReportsPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25); layout.setSpacing(15)
        title = QLabel("Reports"); title.setObjectName("TitleLabel")
        layout.addWidget(title)

        # Controls
        controls_layout = QHBoxLayout()
        self.start_date_edit = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date_edit = QDateEdit(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True); self.end_date_edit.setCalendarPopup(True)
        generate_btn = QPushButton("Generate Report")
        generate_btn.clicked.connect(self.generate_report)
        export_btn = QPushButton("Export CSV")
        export_btn.clicked.connect(self.export_csv)
        
        controls_layout.addWidget(QLabel("From:"))
        controls_layout.addWidget(self.start_date_edit)
        controls_layout.addWidget(QLabel("To:"))
        controls_layout.addWidget(self.end_date_edit)
        controls_layout.addWidget(generate_btn)
        controls_layout.addWidget(export_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Chart
        pg.setConfigOption('background', '#FFFFFF')
        pg.setConfigOption('foreground', '#212529')
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setLabel('left', 'Total Sales (₹)')
        self.plot_widget.setLabel('bottom', 'Date')
        layout.addWidget(self.plot_widget)
        self.generate_report()

    def generate_report(self):
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd") + " 00:00:00"
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd") + " 23:59:59"
        
        query = "SELECT strftime('%Y-%m-%d', date), SUM(total) FROM sales WHERE date BETWEEN ? AND ? GROUP BY strftime('%Y-%m-%d', date)"
        self.report_data = self.db_manager.execute_query(query, (start_date, end_date), fetch='all')
        
        self.plot_widget.clear()
        if not self.report_data: return

        dates = [QDateTime.fromString(row[0], "yyyy-MM-dd").toSecsSinceEpoch() for row in self.report_data]
        sales = [row[1] for row in self.report_data]
        
        axis = self.plot_widget.getAxis('bottom')
        axis.setTicks([[(d, QDateTime.fromSecsSinceEpoch(d).toString("dd-MM")) for d in dates]])
        
        bar_item = pg.BarGraphItem(x=dates, height=sales, width=0.6 * (dates[1]-dates[0] if len(dates)>1 else 86400), brush='#007BFF')
        self.plot_widget.addItem(bar_item)

    def export_csv(self):
        if not hasattr(self, 'report_data') or not self.report_data:
            QMessageBox.warning(self, "No Data", "Generate a report before exporting.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Report", "sales_report.csv", "CSV Files (*.csv)")
        if file_path:
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Date", "Total Sales"])
                writer.writerows(self.report_data)
            QMessageBox.information(self, "Success", "Report exported successfully.")

    def load_data(self):
        self.generate_report()

class SettingsPage(QWidget):
    # ... (code unchanged)
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25,25,25,25); layout.setSpacing(15)
        title = QLabel("Application Settings"); title.setObjectName("TitleLabel")
        layout.addWidget(title)

        form_layout = QFormLayout()
        self.shop_name = QLineEdit()
        self.shop_address = QTextEdit()
        self.shop_gstin = QLineEdit()
        self.shop_phone = QLineEdit()
        self.invoice_terms = QTextEdit()
        
        form_layout.addRow("Shop Name:", self.shop_name)
        form_layout.addRow("Shop Address:", self.shop_address)
        form_layout.addRow("GSTIN:", self.shop_gstin)
        form_layout.addRow("Phone:", self.shop_phone)
        form_layout.addRow("Invoice Terms & Conditions:", self.invoice_terms)
        layout.addLayout(form_layout)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn, 0, Qt.AlignLeft)
        layout.addStretch()
        
    def load_data(self):
        self.shop_name.setText(self.db_manager.get_setting('shop_name', ''))
        self.shop_address.setPlainText(self.db_manager.get_setting('shop_address', ''))
        self.shop_gstin.setText(self.db_manager.get_setting('shop_gstin', ''))
        self.shop_phone.setText(self.db_manager.get_setting('shop_phone', ''))
        self.invoice_terms.setPlainText(self.db_manager.get_setting('invoice_terms', ''))

    def save_settings(self):
        settings = {
            'shop_name': self.shop_name.text(),
            'shop_address': self.shop_address.toPlainText(),
            'shop_gstin': self.shop_gstin.text(),
            'shop_phone': self.shop_phone.text(),
            'invoice_terms': self.invoice_terms.toPlainText()
        }
        for key, value in settings.items():
            self.db_manager.set_setting(key, value)
        
        QMessageBox.information(self, "Success", "Settings updated successfully.")
        self.window().setWindowTitle(settings['shop_name'])

# --- MAIN APPLICATION WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setWindowTitle(self.db_manager.get_setting('shop_name', 'Shop Management Pro'))
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(STYLESHEET)
        
        # Load Font Awesome
        if os.path.exists(FONT_AWESOME_PATH):
            font_id = QFontDatabase.addApplicationFont(FONT_AWESOME_PATH)
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.awesome_font = QFont(font_family)
        else:
            self.awesome_font = QFont() # Fallback

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0); main_layout.setContentsMargins(10, 10, 10, 10)

        nav_panel = QWidget(); nav_panel.setFixedWidth(220)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(10,10,10,10); nav_layout.setSpacing(10); nav_layout.setAlignment(Qt.AlignTop)
        
        self.nav_buttons = {
            "Dashboard": ("\uf0e4", QPushButton(" Dashboard")), "Sales": ("\uf07a", QPushButton(" Sales")),
            "Services": ("\uf0ad", QPushButton(" Services")), "Customers": ("\uf0c0", QPushButton(" Customers")),
            "Inventory": ("\uf1b2", QPushButton(" Inventory")), "Reports": ("\uf080", QPushButton(" Reports")),
            "Settings": ("\uf013", QPushButton(" Settings"))
        }
        for name, (icon_char, btn) in self.nav_buttons.items():
            btn.setObjectName("NavButton"); btn.setCheckable(True)
            btn.clicked.connect(self.switch_page)
            btn.setIcon(self.create_icon(icon_char))
            nav_layout.addWidget(btn)

        self.stacked_widget = QStackedWidget()
        self.pages = {name: None for name in self.nav_buttons.keys()} # Lazy load pages
        
        main_layout.addWidget(nav_panel); main_layout.addWidget(self.stacked_widget)
        self.nav_buttons["Dashboard"][1].setChecked(True); self.switch_page()
    
    def create_icon(self, char_code):
        icon_label = QLabel(char_code)
        icon_label.setFont(self.awesome_font)
        icon_label.setStyleSheet("color: #495057;")
        pixmap = icon_label.grab()
        return QIcon(pixmap)

    def switch_page(self):
        sender = self.sender() or self.nav_buttons["Dashboard"][1]
        for name, (icon, btn) in self.nav_buttons.items():
            if btn == sender:
                if self.pages[name] is None: # Lazy loading
                    if name == "Dashboard": self.pages[name] = DashboardPage(self.db_manager)
                    elif name == "Sales": self.pages[name] = SalesPage(self.db_manager)
                    elif name == "Services": self.pages[name] = ServicesPage(self.db_manager)
                    elif name == "Customers": self.pages[name] = CustomersPage(self.db_manager)
                    elif name == "Inventory": self.pages[name] = InventoryPage(self.db_manager)
                    elif name == "Reports": self.pages[name] = ReportsPage(self.db_manager)
                    elif name == "Settings": self.pages[name] = SettingsPage(self.db_manager)
                    self.stacked_widget.addWidget(self.pages[name])
                
                self.stacked_widget.setCurrentWidget(self.pages[name])
                btn.setChecked(True)
                if hasattr(self.pages[name], 'load_data'): self.pages[name].load_data()
                if hasattr(self.pages[name], 'update_stats'): self.pages[name].update_stats()
            else:
                btn.setChecked(False)

    def update_all_pages(self):
        if self.pages["Dashboard"] and hasattr(self.pages["Dashboard"], 'update_stats'):
            self.pages["Dashboard"].update_stats()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        db_manager = DatabaseManager()
        setup_dialog = SetupDialog()
        if setup_dialog.exec_() == QDialog.Accepted:
            details = setup_dialog.get_details()
            for key, value in details.items(): db_manager.set_setting(key, value)
            db_manager.set_setting('setup_complete', 'true')
        else: sys.exit(0)
    
    db_manager = DatabaseManager()
    window = MainWindow(db_manager)
    window.show()
    sys.exit(app.exec_())


