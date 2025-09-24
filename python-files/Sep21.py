import subprocess
import sys, os, sqlite3
from datetime import datetime, timedelta
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem,
    QComboBox, QMessageBox, QHeaderView, QDialog, QFormLayout, QFileDialog, QTabWidget, QDateEdit,
    QScrollArea
)
from PySide6.QtCore import Qt, QDate
from weasyprint import HTML, CSS
import shutil
import re

# ---------- PATHS ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data.db")
INVOICE_DIR = os.path.join(BASE_DIR, "invoices")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
os.makedirs(INVOICE_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)

# ---------- DATABASE ----------
def check_db_writable():
    if not os.access(os.path.dirname(DB_FILE), os.W_OK):
        raise PermissionError(f"Directory {os.path.dirname(DB_FILE)} is not writable")
    if os.path.exists(DB_FILE) and not os.access(DB_FILE, os.W_OK):
        raise PermissionError(f"Database file {DB_FILE} is not writable")

def init_db():
    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute('''CREATE TABLE IF NOT EXISTS mehsullar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT UNIQUE,
                stock INTEGER,
                qiymet REAL,
                maya_deyeri REAL DEFAULT 0.0
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS musteriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT UNIQUE,
                nagd REAL DEFAULT 0,
                borc REAL DEFAULT 0
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS satislar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER,
                mehsul_id INTEGER,
                miqdar INTEGER,
                birim_qiymet REAL,
                qiymet REAL,
                beh REAL DEFAULT 0.0,
                odeyis_novu TEXT,
                tarix TEXT,
                FOREIGN KEY(musteri_id) REFERENCES musteriler(id),
                FOREIGN KEY(mehsul_id) REFERENCES mehsullar(id)
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS odeyisler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER,
                odenis REAL,
                tarix TEXT,
                FOREIGN KEY(musteri_id) REFERENCES musteriler(id)
            )''')
            c.execute('''CREATE TABLE IF NOT EXISTS invoice_counter (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                counter INTEGER DEFAULT 0
            )''')
            c.execute("INSERT OR IGNORE INTO invoice_counter (id, counter) VALUES (1, 0)")
            conn.commit()
    except sqlite3.OperationalError as e:
        raise PermissionError(f"Database error: {e}. Ensure the database file and directory are writable.")

def db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_invoice_number():
    with db_connection() as conn:
        counter = conn.execute("SELECT counter FROM invoice_counter WHERE id=1").fetchone()["counter"]
        new_counter = counter + 1
        conn.execute("UPDATE invoice_counter SET counter=? WHERE id=1", (new_counter,))
        conn.commit()
        return f"Nº0000000{new_counter:04d}"

# ---------- DIALOGS ----------
class MehsulDialog(QDialog):
    def __init__(self, parent=None, mehsul=None):
        super().__init__(parent)
        self.setWindowTitle("Məhsulu Redaktə et" if mehsul else "Yeni Məhsul")
        self.resize(400, 250)  # Resizable default size
        self.layout = QFormLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.ad_input = QLineEdit(mehsul["ad"] if mehsul else "")
        self.ad_input.setPlaceholderText("Məhsulun adını daxil edin")
        self.stock_input = QLineEdit(str(mehsul["stock"]) if mehsul else "0")
        self.stock_input.setPlaceholderText("Miqdarı daxil edin")
        self.qiymet_input = QLineEdit(str(mehsul["qiymet"]) if mehsul else "0.0")
        self.qiymet_input.setPlaceholderText("Qiyməti daxil edin (AZN)")
        self.maya_deyeri_input = QLineEdit(str(mehsul["maya_deyeri"]) if mehsul else "0.0")
        self.maya_deyeri_input.setPlaceholderText("Maya dəyərini daxil edin (AZN)")

        self.ad_input.setToolTip("Məhsulun unikal adı")
        self.stock_input.setToolTip("Anbarda olan miqdar (0 və ya daha çox)")
        self.qiymet_input.setToolTip("Satış qiyməti (AZN)")
        self.maya_deyeri_input.setToolTip("Məhsulun maya dəyəri (AZN)")

        self.layout.addRow("Ad:", self.ad_input)
        self.layout.addRow("Miqdar:", self.stock_input)
        self.layout.addRow("Defolt Satış Qiyməti:", self.qiymet_input)
        self.layout.addRow("Maya Dəyəri:", self.maya_deyeri_input)

        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Yadda saxla")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("İmtina et")
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        btn_box.addStretch()
        self.layout.addRow(btn_box)

        self.setStyleSheet("""
            QLineEdit { padding: 8px; font-size: 14px; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { padding: 8px; font-size: 14px; }
        """)

    def get_data(self):
        try:
            ad = self.ad_input.text().strip()
            stock = int(self.stock_input.text())
            qiymet = float(self.qiymet_input.text())
            maya_deyeri = float(self.maya_deyeri_input.text())
            if not ad or stock < 0 or qiymet < 0 or maya_deyeri < 0:
                raise ValueError
            return ad, stock, qiymet, maya_deyeri
        except:
            QMessageBox.warning(self, "Xəta", "Dəyərlər düzgün deyil! Bütün sahələri düzgün doldurun.")
            return None

class MusteriDialog(QDialog):
    def __init__(self, parent=None, musteri=None):
        super().__init__(parent)
        self.setWindowTitle("Müştərini Redaktə et" if musteri else "Yeni Müştəri")
        self.resize(400, 200)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.ad_input = QLineEdit(musteri["ad"] if musteri else "")
        self.ad_input.setPlaceholderText("Müştərinin adını daxil edin")
        self.nagd_input = QLineEdit(str(musteri["nagd"]) if musteri else "0.0")
        self.nagd_input.setPlaceholderText("Nağd məbləği daxil edin (AZN)")
        self.borc_input = QLineEdit(str(musteri["borc"]) if musteri else "0.0")
        self.borc_input.setPlaceholderText("Borc məbləği daxil edin (AZN)")

        self.ad_input.setToolTip("Müştərinin unikal adı")
        self.nagd_input.setToolTip("Müştərinin nağd ödənişi (AZN)")
        self.borc_input.setToolTip("Müştərinin borcu (AZN)")

        self.layout.addRow("Ad:", self.ad_input)
        self.layout.addRow("Nağd:", self.nagd_input)
        self.layout.addRow("Borc:", self.borc_input)

        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Yadda saxla")
        self.btn_cancel = QPushButton("İmtina et")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        btn_box.addStretch()
        self.layout.addRow(btn_box)

        self.setStyleSheet("""
            QLineEdit { padding: 8px; font-size: 14px; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { padding: 8px; font-size: 14px; }
        """)

    def get_data(self):
        try:
            ad = self.ad_input.text().strip()
            nagd = float(self.nagd_input.text())
            borc = float(self.borc_input.text())
            if not ad or nagd < 0 or borc < 0:
                raise ValueError
            return ad, nagd, borc
        except:
            QMessageBox.warning(self, "Xəta", "Dəyərlər düzgün deyil! Bütün sahələri düzgün doldurun.")
            return None
        
class SatisConfirmDialog(QDialog):
    def __init__(self, parent=None, musteri_ad="", items=None, total=0.0, beh=0.0):
        super().__init__(parent)
        self.setWindowTitle("Satışı Təsdiqlə")
        self.resize(600, 400)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        info_layout = QFormLayout()
        info_layout.addRow("Müştəri:", QLabel(musteri_ad))
        info_layout.addRow("Ümumi Qiymət:", QLabel(f"{total:.2f} AZN"))
        info_layout.addRow("BEH:", QLabel(f"{beh:.2f} AZN"))
        self.layout.addLayout(info_layout)

        self.tbl_items = QTableWidget()
        self.tbl_items.setColumnCount(4)
        self.tbl_items.setHorizontalHeaderLabels(["Məhsul", "Miqdar", "Birim Qiymət", "Ümumi Qiymət"])
        self.tbl_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_items.setAlternatingRowColors(True)
        self.tbl_items.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tbl_items.setRowCount(len(items))
        for i, (mehsul_ad, miqdar, birim_qiymet, qiymet) in enumerate(items):
            self.tbl_items.setItem(i, 0, QTableWidgetItem(mehsul_ad))
            self.tbl_items.setItem(i, 1, QTableWidgetItem(str(miqdar)))
            self.tbl_items.setItem(i, 2, QTableWidgetItem(f"{birim_qiymet:.2f}"))
            self.tbl_items.setItem(i, 3, QTableWidgetItem(f"{qiymet:.2f}"))
        self.layout.addWidget(self.tbl_items, stretch=1)

        btn_box = QHBoxLayout()
        self.btn_confirm = QPushButton("Təsdiqlə")
        self.btn_confirm.clicked.connect(self.accept)
        self.btn_cancel = QPushButton("İmtina et")
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_confirm)
        btn_box.addWidget(self.btn_cancel)
        btn_box.addStretch()
        self.layout.addLayout(btn_box)

        self.setStyleSheet("""
            QTableWidget { font-size: 14px; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { padding: 8px; font-size: 14px; }
        """)

class OdemeDialog(QDialog):
    def __init__(self, parent=None, musteri=None):
        super().__init__(parent)
        self.setWindowTitle("Borc Ödənişi")
        self.resize(400, 200)
        self.layout = QFormLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.musteri_ad = musteri["ad"]
        self.musteri_id = musteri["id"]
        self.borc = musteri["borc"]

        self.layout.addRow("Müştəri:", QLabel(self.musteri_ad))
        self.layout.addRow("Cari Borc:", QLabel(f"{self.borc:.2f} AZN"))
        self.odenis_input = QLineEdit("0.0")
        self.odenis_input.setPlaceholderText("Ödəniş məbləğini daxil edin (AZN)")
        self.odenis_input.setToolTip("Borcun ödəniləcək hissəsi (0 ilə cari borc arasında)")
        self.layout.addRow("Ödəniş Məbləği:", self.odenis_input)

        btn_box = QHBoxLayout()
        self.btn_save = QPushButton("Ödə")
        self.btn_cancel = QPushButton("İmtina et")
        self.btn_save.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        btn_box.addStretch()
        btn_box.addWidget(self.btn_save)
        btn_box.addWidget(self.btn_cancel)
        btn_box.addStretch()
        self.layout.addRow(btn_box)

        self.setStyleSheet("""
            QLineEdit { padding: 8px; font-size: 14px; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { padding: 8px; font-size: 14px; }
        """)

    def get_data(self):
        try:
            odenis = float(self.odenis_input.text().strip())
            if odenis < 0 or odenis > self.borc:
                raise ValueError
            return odenis
        except ValueError:
            QMessageBox.warning(self, "Xəta", "Ödəniş məbləği düzgün deyil! 0 ilə cari borc arasında bir rəqəm daxil edin.")
            return None

class CustomerStatementDialog(QDialog):
    def __init__(self, parent=None, musteri=None):
        super().__init__(parent)
        self.setWindowTitle(f"{musteri['ad']} - Hesabat")
        self.resize(800, 500)
        self.musteri = musteri
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)

        summary_layout = QFormLayout()
        summary_layout.addRow("Cari Nağd:", QLabel(f"{musteri['nagd']:.2f} AZN"))
        summary_layout.addRow("Cari Borc:", QLabel(f"{musteri['borc']:.2f} AZN"))
        self.layout.addLayout(summary_layout)

        self.tbl_statement = QTableWidget()
        self.tbl_statement.setColumnCount(7)
        self.tbl_statement.setHorizontalHeaderLabels(["Tarix", "Təsvir", "Miqdar", "Birim Qiymət", "Qiymət", "BEH", "Ödəniş Növü"])
        self.tbl_statement.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_statement.setAlternatingRowColors(True)
        self.tbl_statement.setEditTriggers(QTableWidget.NoEditTriggers)
        self.layout.addWidget(self.tbl_statement, stretch=1)

        self.load_statement(musteri["id"])

        btn_box = QHBoxLayout()
        btn_generate_faktura = QPushButton("Faktura Yarat")
        btn_generate_faktura.clicked.connect(self.generate_customer_faktura)
        btn_close = QPushButton("Bağla")
        btn_close.clicked.connect(self.accept)
        btn_box.addStretch()
        btn_box.addWidget(btn_generate_faktura)
        btn_box.addWidget(btn_close)
        btn_box.addStretch()
        self.layout.addLayout(btn_box)

        self.setStyleSheet("""
            QTableWidget { font-size: 14px; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { padding: 8px; font-size: 14px; }
        """)

    def load_statement(self, cid):
        with db_connection() as conn:
            sales = conn.execute("""
                SELECT s.tarix, p.ad as mehsul, s.miqdar, s.birim_qiymet, s.qiymet, s.beh, s.odeyis_novu
                FROM satislar s
                JOIN mehsullar p ON s.mehsul_id = p.id
                WHERE s.musteri_id = ?
                ORDER BY s.tarix DESC
            """, (cid,)).fetchall()
            payments = conn.execute("""
                SELECT o.tarix, 'Borc Ödənişi' as mehsul, 0 as miqdar, 0 as birim_qiymet, o.odenis as qiymet, 0 as beh, 'Ödənmiş' as odeyis_novu
                FROM odeyisler o
                WHERE o.musteri_id = ?
                ORDER BY o.tarix DESC
            """, (cid,)).fetchall()
        all_transactions = sales + payments
        all_transactions.sort(key=lambda x: x["tarix"], reverse=True)
        self.tbl_statement.setRowCount(len(all_transactions))
        for i, tx in enumerate(all_transactions):
            self.tbl_statement.setItem(i, 0, QTableWidgetItem(tx["tarix"]))
            self.tbl_statement.setItem(i, 1, QTableWidgetItem(tx["mehsul"]))
            self.tbl_statement.setItem(i, 2, QTableWidgetItem(str(tx["miqdar"])))
            self.tbl_statement.setItem(i, 3, QTableWidgetItem(f"{tx['birim_qiymet']:.2f}"))
            self.tbl_statement.setItem(i, 4, QTableWidgetItem(f"{tx['qiymet']:.2f}"))
            self.tbl_statement.setItem(i, 5, QTableWidgetItem(f"{tx['beh']:.2f}"))
            self.tbl_statement.setItem(i, 6, QTableWidgetItem(tx["odeyis_novu"]))

    def generate_customer_faktura(self):
        with db_connection() as conn:
            sales = conn.execute("""
                SELECT s.tarix, p.ad as mehsul, s.miqdar, s.birim_qiymet, s.qiymet, s.beh, s.odeyis_novu
                FROM satislar s
                JOIN mehsullar p ON s.mehsul_id = p.id
                WHERE s.musteri_id = ?
                ORDER BY s.tarix
            """, (self.musteri["id"],)).fetchall()
            payments = conn.execute("""
                SELECT o.tarix, 'Borc Ödənişi' as mehsul, 0 as miqdar, 0 as birim_qiymet, o.odenis as qiymet, 0 as beh, 'Ödənmiş' as odeyis_novu
                FROM odeyisler o
                WHERE o.musteri_id = ?
                ORDER BY o.tarix
            """, (self.musteri["id"],)).fetchall()
        sales = [dict(tx) for tx in sales]
        payments = [dict(p) for p in payments]
        all_transactions = sales + payments
        all_transactions.sort(key=lambda x: x["tarix"])
        if not all_transactions:
            QMessageBox.warning(self, "Xəta", "Bu müştəri üçün heç bir əməliyyat tapılmadı!")
            return
        items = [(tx["mehsul"], tx["miqdar"], tx["birim_qiymet"], tx["qiymet"]) for tx in all_transactions]
        total_amount = sum(tx["qiymet"] for tx in all_transactions)
        total_nagd = sum(tx["qiymet"] if tx["odeyis_novu"] == "Nəğd" else tx["beh"] for tx in sales) + sum(p["qiymet"] for p in payments)
        total_borc = sum(tx["qiymet"] - tx["beh"] if tx["odeyis_novu"] == "Borc" else 0.0 for tx in sales)
        old_debt = 0.0
        new_debt = self.musteri["borc"]
        self.parent().generate_invoice(
            c_name=self.musteri["ad"],
            items=items,
            old_debt=old_debt,
            total_amount=total_amount,
            payment_type="Hesabat",
            beh=0.0,
            odenis_input=total_nagd
        )

class DetailedReportDialog(QDialog):
    def __init__(self, parent=None, period="all", start=None, end=None):
        super().__init__(parent)
        self.setWindowTitle("Detallı Hesabatlar")
        self.resize(1000, 700)
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.period = period
        self.start = start
        self.end = end

        # Period selection
        hbox_period = QHBoxLayout()
        btn_today = QPushButton("Bu gün")
        btn_today.clicked.connect(lambda: self.load_reports("today"))
        btn_yesterday = QPushButton("Dünən")
        btn_yesterday.clicked.connect(lambda: self.load_reports("yesterday"))
        btn_week = QPushButton("Bu həftə")
        btn_week.clicked.connect(lambda: self.load_reports("week"))
        btn_month = QPushButton("Bu ay")
        btn_month.clicked.connect(lambda: self.load_reports("month"))
        btn_year = QPushButton("Bu il")
        btn_year.clicked.connect(lambda: self.load_reports("year"))
        btn_all = QPushButton("Bütün")
        btn_all.clicked.connect(lambda: self.load_reports("all"))
        hbox_period.addWidget(btn_today)
        hbox_period.addWidget(btn_yesterday)
        hbox_period.addWidget(btn_week)
        hbox_period.addWidget(btn_month)
        hbox_period.addWidget(btn_year)
        hbox_period.addWidget(btn_all)
        self.layout.addLayout(hbox_period)

        hbox_custom = QHBoxLayout()
        lbl_start = QLabel("Başlanğıc Tarix:")
        self.start_date = QDateEdit(QDate.currentDate())
        lbl_end = QLabel("Bitiş Tarix:")
        self.end_date = QDateEdit(QDate.currentDate())
        btn_custom = QPushButton("Göstər")
        btn_custom.clicked.connect(lambda: self.load_reports("custom", self.start_date.date().toPyDate(), self.end_date.date().toPyDate()))
        hbox_custom.addWidget(lbl_start)
        hbox_custom.addWidget(self.start_date)
        hbox_custom.addWidget(lbl_end)
        hbox_custom.addWidget(self.end_date)
        hbox_custom.addWidget(btn_custom)
        self.layout.addLayout(hbox_custom)

        self.tab_widget = QTabWidget()
        self.layout.addWidget(self.tab_widget)

        # Tab 1: Məhsul Hesabatı
        self.tab_product = QWidget()
        self.tab_product_layout = QVBoxLayout(self.tab_product)
        self.tbl_product = QTableWidget()
        self.tbl_product.setColumnCount(5)
        self.tbl_product.setHorizontalHeaderLabels(["Məhsul Adı", "Ümumi Miqdar", "Ümumi Gəlir", "Ümumi Xeyir", "Əməliyyatlar"])
        self.tbl_product.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_product.setAlternatingRowColors(True)
        self.tbl_product.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tab_product_layout.addWidget(self.tbl_product)
        btn_export_product = QPushButton("PDF Olaraq İxrac Et")
        btn_export_product.clicked.connect(self.export_product_report)
        self.tab_product_layout.addWidget(btn_export_product)
        self.tab_widget.addTab(self.tab_product, "Məhsul Hesabatı")

        # Tab 2: Müştəri Hesabatı
        self.tab_customer = QWidget()
        self.tab_customer_layout = QVBoxLayout(self.tab_customer)
        self.tbl_customer = QTableWidget()
        self.tbl_customer.setColumnCount(5)
        self.tbl_customer.setHorizontalHeaderLabels(["Müştəri Adı", "Ümumi Alış", "Ümumi Ödəniş", "Qalan Borc", "Əməliyyatlar"])
        self.tbl_customer.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_customer.setAlternatingRowColors(True)
        self.tbl_customer.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tab_customer_layout.addWidget(self.tbl_customer)
        btn_export_customer = QPushButton("PDF Olaraq İxrac Et")
        btn_export_customer.clicked.connect(self.export_customer_report)
        self.tab_customer_layout.addWidget(btn_export_customer)
        self.tab_widget.addTab(self.tab_customer, "Müştəri Hesabatı")

        # Tab 3: Anbar Hesabatı
        self.tab_inventory = QWidget()
        self.tab_inventory_layout = QVBoxLayout(self.tab_inventory)
        self.tbl_inventory = QTableWidget()
        self.tbl_inventory.setColumnCount(5)
        self.tbl_inventory.setHorizontalHeaderLabels(["Məhsul Adı", "Cari Miqdar", "Satış Dəyəri", "Maya Dəyəri", "Əməliyyatlar"])
        self.tbl_inventory.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_inventory.setAlternatingRowColors(True)
        self.tbl_inventory.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tab_inventory_layout.addWidget(self.tbl_inventory)
        btn_export_inventory = QPushButton("PDF Olaraq İxrac Et")
        btn_export_inventory.clicked.connect(self.export_inventory_report)
        self.tab_inventory_layout.addWidget(btn_export_inventory)
        self.tab_widget.addTab(self.tab_inventory, "Anbar Hesabatı")

        btn_close = QPushButton("Bağla")
        btn_close.clicked.connect(self.accept)
        self.layout.addWidget(btn_close)

        self.setStyleSheet("""
            QTableWidget { font-size: 14px; background-color: #FFFFFF; alternate-background-color: #F0F0F0; }
            QLabel { font-size: 14px; font-weight: bold; }
            QPushButton { padding: 8px; font-size: 14px; background-color: #3498DB; color: white; }
            QTabBar::tab { padding: 10px; font-size: 14px; }
        """)

        self.load_reports(self.period, self.start, self.end)

    def load_reports(self, period, start=None, end=None):
        self.period = period
        self.start = start
        self.end = end
        self.load_product_report()
        self.load_customer_report()
        self.load_inventory_report()

    def get_date_filter(self, t):
        now = datetime.now()
        include = False
        if self.period == "today" and t.date() == now.date():
            include = True
        elif self.period == "yesterday" and t.date() == (now - timedelta(days=1)).date():
            include = True
        elif self.period == "week" and t.isocalendar()[1] == now.isocalendar()[1] and t.year == now.year:
            include = True
        elif self.period == "month" and t.month == now.month and t.year == now.year:
            include = True
        elif self.period == "year" and t.year == now.year:
            include = True
        elif self.period == "all":
            include = True
        elif self.period == "custom" and self.start <= t.date() <= self.end:
            include = True
        return include

    def load_product_report(self):
        with db_connection() as conn:
            sales = conn.execute("""
                SELECT p.ad, SUM(s.miqdar) as total_miqdar, SUM(s.qiymet) as total_gelir, 
                       SUM(s.qiymet - (p.maya_deyeri * s.miqdar)) as total_xeyir, p.id
                FROM satislar s
                JOIN mehsullar p ON s.mehsul_id = p.id
                GROUP BY p.id
                ORDER BY total_gelir DESC
            """).fetchall()
        filtered = []
        for r in sales:
            # Filter by date: need to check each sale
            product_sales = conn.execute("SELECT tarix, miqdar, qiymet FROM satislar WHERE mehsul_id = ?", (r["id"],)).fetchall()
            total_miqdar = 0
            total_gelir = 0.0
            total_xeyir = 0.0
            for ps in product_sales:
                t = datetime.strptime(ps["tarix"], "%Y-%m-%d %H:%M:%S")
                if self.get_date_filter(t):
                    total_miqdar += ps["miqdar"]
                    total_gelir += ps["qiymet"]
                    total_xeyir += ps["qiymet"] - (r["maya_deyeri"] * ps["miqdar"])  # Assuming maya_deyeri constant
            if total_miqdar > 0:
                filtered.append({"ad": r["ad"], "total_miqdar": total_miqdar, "total_gelir": total_gelir, "total_xeyir": total_xeyir})
        self.tbl_product.setRowCount(len(filtered))
        for i, r in enumerate(filtered):
            self.tbl_product.setItem(i, 0, QTableWidgetItem(r["ad"]))
            self.tbl_product.setItem(i, 1, QTableWidgetItem(str(r["total_miqdar"])))
            self.tbl_product.setItem(i, 2, QTableWidgetItem(f"{r['total_gelir']:.2f}"))
            self.tbl_product.setItem(i, 3, QTableWidgetItem(f"{r['total_xeyir']:.2f}"))
            btn_detail = QPushButton("Detallar")
            btn_detail.clicked.connect(lambda checked, ad=r["ad"]: self.show_product_detail(ad))
            hbox = QHBoxLayout()
            hbox.addWidget(btn_detail)
            hbox.setContentsMargins(0, 0, 0, 0)
            cell = QWidget()
            cell.setLayout(hbox)
            self.tbl_product.setCellWidget(i, 4, cell)

    def show_product_detail(self, ad):
        QMessageBox.information(self, "Məhsul Detalları", f"{ad} üçün detallı məlumat: Gələcək inkişafda əlavə ediləcək.")

    def load_customer_report(self):
        with db_connection() as conn:
            customers = conn.execute("SELECT * FROM musteriler").fetchall()
        filtered = []
        for c in customers:
            sales = conn.execute("SELECT tarix, qiymet, beh, odeyis_novu FROM satislar WHERE musteri_id = ?", (c["id"],)).fetchall()
            payments = conn.execute("SELECT tarix, odenis FROM odeyisler WHERE musteri_id = ?", (c["id"],)).fetchall()
            total_alis = 0.0
            total_odenis = 0.0
            for s in sales:
                t = datetime.strptime(s["tarix"], "%Y-%m-%d %H:%M:%S")
                if self.get_date_filter(t):
                    total_alis += s["qiymet"]
                    if s["odeyis_novu"] == "Nəğd":
                        total_odenis += s["qiymet"]
                    else:
                        total_odenis += s["beh"]
            for p in payments:
                t = datetime.strptime(p["tarix"], "%Y-%m-%d %H:%M:%S")
                if self.get_date_filter(t):
                    total_odenis += p["odenis"]
            if total_alis > 0 or total_odenis > 0:
                filtered.append({"ad": c["ad"], "total_alis": total_alis, "total_odenis": total_odenis, "qalan_borc": c["borc"]})
        self.tbl_customer.setRowCount(len(filtered))
        for i, r in enumerate(filtered):
            self.tbl_customer.setItem(i, 0, QTableWidgetItem(r["ad"]))
            self.tbl_customer.setItem(i, 1, QTableWidgetItem(f"{r['total_alis']:.2f}"))
            self.tbl_customer.setItem(i, 2, QTableWidgetItem(f"{r['total_odenis']:.2f}"))
            self.tbl_customer.setItem(i, 3, QTableWidgetItem(f"{r['qalan_borc']:.2f}"))
            btn_detail = QPushButton("Detallar")
            btn_detail.clicked.connect(lambda checked, ad=r["ad"]: self.show_customer_detail(ad))
            hbox = QHBoxLayout()
            hbox.addWidget(btn_detail)
            hbox.setContentsMargins(0, 0, 0, 0)
            cell = QWidget()
            cell.setLayout(hbox)
            self.tbl_customer.setCellWidget(i, 4, cell)

    def show_customer_detail(self, ad):
        QMessageBox.information(self, "Müştəri Detalları", f"{ad} üçün detallı məlumat: Gələcək inkişafda əlavə ediləcək.")

    def load_inventory_report(self):
        with db_connection() as conn:
            inventory = conn.execute("SELECT ad, stock, qiymet, maya_deyeri FROM mehsullar ORDER BY ad").fetchall()
        self.tbl_inventory.setRowCount(len(inventory))
        for i, r in enumerate(inventory):
            satis_deyeri = r["stock"] * r["qiymet"]
            maya_deyeri = r["stock"] * r["maya_deyeri"]
            self.tbl_inventory.setItem(i, 0, QTableWidgetItem(r["ad"]))
            self.tbl_inventory.setItem(i, 1, QTableWidgetItem(str(r["stock"])))
            self.tbl_inventory.setItem(i, 2, QTableWidgetItem(f"{satis_deyeri:.2f}"))
            self.tbl_inventory.setItem(i, 3, QTableWidgetItem(f"{maya_deyeri:.2f}"))
            btn_detail = QPushButton("Detallar")
            btn_detail.clicked.connect(lambda checked, ad=r["ad"]: self.show_inventory_detail(ad))
            hbox = QHBoxLayout()
            hbox.addWidget(btn_detail)
            hbox.setContentsMargins(0, 0, 0, 0)
            cell = QWidget()
            cell.setLayout(hbox)
            self.tbl_inventory.setCellWidget(i, 4, cell)

    def show_inventory_detail(self, ad):
        QMessageBox.information(self, "Anbar Detalları", f"{ad} üçün detallı məlumat: Gələcək inkişafda əlavə ediləcək.")

    def export_product_report(self):
        self.export_report("Məhsul Hesabatı", self.tbl_product)

    def export_customer_report(self):
        self.export_report("Müştəri Hesabatı", self.tbl_customer)

    def export_inventory_report(self):
        self.export_report("Anbar Hesabatı", self.tbl_inventory)

    def export_report(self, title, table):
        now = datetime.now()
        file_name = os.path.join(INVOICE_DIR, f"{title.lower().replace(' ', '_')}_{now.strftime('%Y%m%d_%H%M%S')}.pdf")
        table_rows = ""
        for i in range(table.rowCount()):
            row = []
            for j in range(table.columnCount() - 1):  # Exclude the last column (actions)
                cell_text = table.item(i, j).text() if table.item(i, j) else ''
                row.append(f"<td>{cell_text}</td>")
            table_rows += f"<tr>{''.join(row)}</tr>"

        html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; font-size: 12pt; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid black; padding: 5px; text-align: center; }}
            th {{ background-color: #f2f2f2; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <table>
            <tr>{"".join(f"<th>{table.horizontalHeaderItem(j).text()}</th>" for j in range(table.columnCount() - 1))}</tr>
            {table_rows}
        </table>
    </body>
    </html>
    """
        HTML(string=html_content).write_pdf(file_name)
        QMessageBox.information(self, "İxrac", f"{title} PDF olaraq ixrac edildi: {os.path.basename(file_name)}")

# ---------- MAIN WINDOW ----------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📦 Offline Satış və Anbar Proqramı")
        self.resize(1400, 900)  # Resizable default size
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)
        self.light_theme = True
        self.setStyleSheet(self.light_stylesheet())
        btn_toggle_theme = QPushButton("Gündüz/Gecə rejimi")
        btn_toggle_theme.clicked.connect(self.toggle_theme)
        self.main_layout.addWidget(btn_toggle_theme)
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("QTabWidget::pane { border: 0; } QTabBar::tab { padding: 8px 16px; }")
        self.main_layout.addWidget(self.tab_widget)
        self.tab_products_customers = QWidget()
        self.tab_products_customers_layout = QVBoxLayout()
        self.tab_products_customers.setLayout(self.tab_products_customers_layout)
        self.tab_widget.addTab(self.tab_products_customers, "Məhsullar və Müştərilər")
        self.tab_sales = QWidget()
        self.tab_sales_layout = QVBoxLayout()
        self.tab_sales.setLayout(self.tab_sales_layout)
        self.tab_widget.addTab(self.tab_sales, "Satış")
        self.tab_reports = QWidget()
        self.tab_reports_layout = QVBoxLayout()
        self.tab_reports.setLayout(self.tab_reports_layout)
        self.tab_widget.addTab(self.tab_reports, "Hesabatlar")
        self.init_mehsullar()
        self.init_musteriler()
        self.init_satis()
        self.init_hesabat()
        self.init_backup_restore()
        self.sale_items = []  # List to store multiple sale items temporarily
        self.current_period = "today"
        self.current_start = None
        self.current_end = None

    def light_stylesheet(self):
        return """
QWidget { font-family:'Arial'; font-size:13px; background-color:#F5F6FA; color:black; }
QLabel { font-weight:bold; font-size:15px; color:#2C3E50; }
QTableWidget { background-color:#FFFFFF; gridline-color:#BDC3C7; alternate-background-color:#ECF0F1; color:black; }
QHeaderView::section { background-color:#3498DB; color:white; padding:5px; font-weight:bold; border:1px solid #2980B9; }
QPushButton { background-color:#2980B9; color:white; border-radius:0px; padding:4px 6px; font-weight:bold; }
QPushButton:hover { background-color:#1F618D; }
QLineEdit,QComboBox { border:1px solid #BDC3C7; padding:6px; border-radius:0px; background-color:#FFFFFF; color:black; font-size:14px; }
QComboBox {min-width: 200px;border: 1px solid #BDC3C7;padding: 8px;border-radius: 0px;background-color: #FFFFFF;color: black;font-size: 14px;}
QComboBox QAbstractItemView {background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #FFFFFF, stop:1 #F0F0F0);color: #000000;selection-background-color: #3498DB;selection-color: #FFFFFF;font-size: 18px;padding: 8px;border-radius: 4px;outline: none;}
QComboBox QAbstractItemView::item:hover {background-color: #E8ECEF;color: #000000;}
QTabBar::tab { background:#3498DB; color:white; padding:8px 16px; }
QTabBar::tab:selected { background:#1F618D; }
"""

    def dark_stylesheet(self):
        return """
QWidget { font-family:'Arial'; font-size:13px; background-color:#2C3E50; color:white; }
QLabel { font-weight:bold; font-size:15px; color:#ECF0F1; }
QTableWidget { background-color:#34495E; gridline-color:#7F8C8D; alternate-background-color:#3E5569; color:white; }
QHeaderView::section { background-color:#1ABC9C; color:white; padding:5px; font-weight:bold; border:1px solid #16A085; }
QPushButton { background-color:#16A085; color:white; border-radius:0px; padding:4px 6px; font-weight:bold; }
QPushButton:hover { background-color:#138D75; }
QLineEdit,QComboBox { border:1px solid #7F8C8D; padding:6px; border-radius:0px; background-color:#34495E; color:white; font-size:14px; }
QComboBox {min-width: 200px;border: 1px solid #7F8C8D;padding: 6px;border-radius: 0px;background-color: #34495E;color: white;font-size: 14px;}
QComboBox QAbstractItemView {background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34495E, stop:1 #3E5569);color: white;selection-background-color: #1ABC9C;selection-color: white;font-size: 18px;padding: 8px;border-radius: 4px;outline: none;}
QComboBox QAbstractItemView::item:hover {background-color: #48C9B0;color: white;}
QTabBar::tab { background:#1ABC9C; color:white; padding:8px 16px; }
QTabBar::tab:selected { background:#138D75; }
"""

    def toggle_theme(self):
        self.light_theme = not self.light_theme
        self.setStyleSheet(self.light_stylesheet() if self.light_theme else self.dark_stylesheet())
        self.refresh_mehsullar()
        self.refresh_musteriler()

    def open_invoice_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(INVOICE_DIR)
            elif sys.platform == "darwin":
                subprocess.call(["open", INVOICE_DIR])
            else:
                subprocess.call(["xdg-open", INVOICE_DIR])
        except Exception as e:
            QMessageBox.warning(self, "Xəta", f"Qovluq açıla bilmədi:\n{e}")

    def init_mehsullar(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(QLabel("📦 Məhsullar"))
        hbox = QHBoxLayout()
        btn_add = QPushButton("Yeni Məhsul")
        btn_add.clicked.connect(self.add_mehsul)
        self.txt_search_mehsul = QLineEdit()
        self.txt_search_mehsul.setPlaceholderText("Məhsul axtar")
        self.txt_search_mehsul.textChanged.connect(self.search_mehsul)
        hbox.addWidget(btn_add)
        hbox.addWidget(self.txt_search_mehsul)
        layout.addLayout(hbox)
        self.tbl_mehsullar = QTableWidget()
        layout.addWidget(self.tbl_mehsullar)
        self.tbl_mehsullar.setColumnCount(6)
        self.tbl_mehsullar.setHorizontalHeaderLabels(["ID", "Ad", "Miqdar", "Defolt Qiymət", "Maya Dəyəri", "Əməliyyatlar"])
        self.tbl_mehsullar.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_mehsullar.setAlternatingRowColors(True)
        self.tbl_mehsullar.setEditTriggers(QTableWidget.NoEditTriggers)
        scroll.setWidget(content)
        self.tab_products_customers_layout.addWidget(scroll)
        self.refresh_mehsullar()

    def refresh_mehsullar(self):
        with db_connection() as conn:
            mehsullar = conn.execute("SELECT * FROM mehsullar ORDER BY id DESC").fetchall()
        self.tbl_mehsullar.setRowCount(len(mehsullar))
        for i, m in enumerate(mehsullar):
            item_id = QTableWidgetItem(str(m["id"]))
            item_ad = QTableWidgetItem(m["ad"])
            item_stock = QTableWidgetItem(str(m["stock"]))
            item_qiymet = QTableWidgetItem(f"{m['qiymet']:.2f}")
            item_maya = QTableWidgetItem(f"{m['maya_deyeri']:.2f}")
            if m["stock"] < 5:
                red_brush = Qt.red if self.light_theme else Qt.darkRed
                item_id.setBackground(red_brush)
                item_ad.setBackground(red_brush)
                item_stock.setBackground(red_brush)
                item_qiymet.setBackground(red_brush)
                item_maya.setBackground(red_brush)
            self.tbl_mehsullar.setItem(i, 0, item_id)
            self.tbl_mehsullar.setItem(i, 1, item_ad)
            self.tbl_mehsullar.setItem(i, 2, item_stock)
            self.tbl_mehsullar.setItem(i, 3, item_qiymet)
            self.tbl_mehsullar.setItem(i, 4, item_maya)
            btn_edit = QPushButton("Redaktə")
            btn_remove = QPushButton("Sil")
            btn_edit.clicked.connect(lambda checked, mid=m["id"]: self.edit_mehsul(mid))
            btn_remove.clicked.connect(lambda checked, mid=m["id"]: self.remove_mehsul(mid))
            hbox_btn = QHBoxLayout()
            hbox_btn.addWidget(btn_edit)
            hbox_btn.addWidget(btn_remove)
            hbox_btn.setContentsMargins(0, 0, 0, 0)
            cell_widget = QWidget()
            cell_widget.setLayout(hbox_btn)
            self.tbl_mehsullar.setCellWidget(i, 5, cell_widget)

    def search_mehsul(self):
        text = self.txt_search_mehsul.text().lower()
        with db_connection() as conn:
            all_m = conn.execute("SELECT * FROM mehsullar").fetchall()
        filtered = [m for m in all_m if text in m["ad"].lower()]
        self.tbl_mehsullar.setRowCount(len(filtered))
        for i, m in enumerate(filtered):
            item_id = QTableWidgetItem(str(m["id"]))
            item_ad = QTableWidgetItem(m["ad"])
            item_stock = QTableWidgetItem(str(m["stock"]))
            item_qiymet = QTableWidgetItem(f"{m['qiymet']:.2f}")
            item_maya = QTableWidgetItem(f"{m['maya_deyeri']:.2f}")
            if m["stock"] < 5:
                red_brush = Qt.red if self.light_theme else Qt.darkRed
                item_id.setBackground(red_brush)
                item_ad.setBackground(red_brush)
                item_stock.setBackground(red_brush)
                item_qiymet.setBackground(red_brush)
                item_maya.setBackground(red_brush)
            self.tbl_mehsullar.setItem(i, 0, item_id)
            self.tbl_mehsullar.setItem(i, 1, item_ad)
            self.tbl_mehsullar.setItem(i, 2, item_stock)
            self.tbl_mehsullar.setItem(i, 3, item_qiymet)
            self.tbl_mehsullar.setItem(i, 4, item_maya)
            btn_edit = QPushButton("Redaktə")
            btn_remove = QPushButton("Sil")
            btn_edit.clicked.connect(lambda checked, mid=m["id"]: self.edit_mehsul(mid))
            btn_remove.clicked.connect(lambda checked, mid=m["id"]: self.remove_mehsul(mid))
            hbox_btn = QHBoxLayout()
            hbox_btn.addWidget(btn_edit)
            hbox_btn.addWidget(btn_remove)
            hbox_btn.setContentsMargins(0, 0, 0, 0)
            cell_widget = QWidget()
            cell_widget.setLayout(hbox_btn)
            self.tbl_mehsullar.setCellWidget(i, 5, cell_widget)

    def add_mehsul(self):
        dialog = MehsulDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                ad, stock, qiymet, maya_deyeri = data
                with db_connection() as conn:
                    try:
                        conn.execute("INSERT INTO mehsullar (ad, stock, qiymet, maya_deyeri) VALUES (?, ?, ?, ?)", (ad, stock, qiymet, maya_deyeri))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        QMessageBox.warning(self, "Xəta", "Bu məhsul artıq mövcuddur!")
                self.refresh_mehsullar()
                self.refresh_mehsul_combo()

    def edit_mehsul(self, mid):
        with db_connection() as conn:
            m = conn.execute("SELECT * FROM mehsullar WHERE id=?", (mid,)).fetchone()
        if not m: return
        dialog = MehsulDialog(self, m)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                ad, stock, qiymet, maya_deyeri = data
                with db_connection() as conn:
                    try:
                        conn.execute("UPDATE mehsullar SET ad=?, stock=?, qiymet=?, maya_deyeri=? WHERE id=?", (ad, stock, qiymet, maya_deyeri, mid))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        QMessageBox.warning(self, "Xəta", "Bu məhsul adı artıq mövcuddur!")
                self.refresh_mehsullar()
                self.refresh_mehsul_combo()

    def remove_mehsul(self, mid):
        reply = QMessageBox.question(self, "Sil", "Məhsulu silmək istədiyinizdən əminsiniz?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            with db_connection() as conn:
                sales_count = conn.execute("SELECT COUNT(*) FROM satislar WHERE mehsul_id=?", (mid,)).fetchone()[0]
                if sales_count > 0:
                    QMessageBox.warning(self, "Xəta", "Bu məhsul satılmışdır, silmək mümkün deyil!")
                else:
                    conn.execute("DELETE FROM mehsullar WHERE id=?", (mid,))
                    conn.commit()
            self.refresh_mehsullar()
            self.refresh_mehsul_combo()

    def init_musteriler(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.addWidget(QLabel("👤 Müştərilər"))
        hbox = QHBoxLayout()
        btn_add = QPushButton("Yeni Müştəri")
        btn_add.clicked.connect(self.add_musteri)
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Müştəri axtar")
        self.txt_search.textChanged.connect(self.search_musteri)
        hbox.addWidget(btn_add)
        hbox.addWidget(self.txt_search)
        layout.addLayout(hbox)
        self.tbl_musteriler = QTableWidget()
        layout.addWidget(self.tbl_musteriler)
        self.tbl_musteriler.setColumnCount(5)
        self.tbl_musteriler.setHorizontalHeaderLabels(["ID", "Ad", "Nağd", "Borc", "Əməliyyatlar"])
        self.tbl_musteriler.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_musteriler.setAlternatingRowColors(True)
        self.tbl_musteriler.setEditTriggers(QTableWidget.NoEditTriggers)
        scroll.setWidget(content)
        self.tab_products_customers_layout.addWidget(scroll)
        self.refresh_musteriler()

    def refresh_musteriler(self):
        with db_connection() as conn:
            musteriler = conn.execute("SELECT * FROM musteriler ORDER BY id DESC").fetchall()
        self.tbl_musteriler.setRowCount(len(musteriler))
        for i, c in enumerate(musteriler):
            self.tbl_musteriler.setItem(i, 0, QTableWidgetItem(str(c["id"])))
            self.tbl_musteriler.setItem(i, 1, QTableWidgetItem(c["ad"]))
            self.tbl_musteriler.setItem(i, 2, QTableWidgetItem(f"{c['nagd']:.2f}"))
            self.tbl_musteriler.setItem(i, 3, QTableWidgetItem(f"{c['borc']:.2f}"))
            btn_edit = QPushButton("Redaktə")
            btn_remove = QPushButton("Sil")
            btn_ode = QPushButton("Ödə")
            btn_statement = QPushButton("Hesabat")
            btn_edit.clicked.connect(lambda checked, cid=c["id"]: self.edit_musteri(cid))
            btn_remove.clicked.connect(lambda checked, cid=c["id"]: self.remove_musteri(cid))
            btn_ode.clicked.connect(lambda checked, cid=c["id"]: self.pay_debt(cid))
            btn_statement.clicked.connect(lambda checked, cid=c["id"]: self.show_customer_statement(cid))
            hbox_btn = QHBoxLayout()
            hbox_btn.addWidget(btn_edit)
            hbox_btn.addWidget(btn_remove)
            hbox_btn.addWidget(btn_ode)
            hbox_btn.addWidget(btn_statement)
            hbox_btn.setContentsMargins(0, 0, 0, 0)
            cell_widget = QWidget()
            cell_widget.setLayout(hbox_btn)
            self.tbl_musteriler.setCellWidget(i, 4, cell_widget)

    def add_musteri(self):
        dialog = MusteriDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                ad, nagd, borc = data
                with db_connection() as conn:
                    try:
                        conn.execute("INSERT INTO musteriler (ad, nagd, borc) VALUES (?, ?, ?)", (ad, nagd, borc))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        QMessageBox.warning(self, "Xəta", "Bu müştəri artıq mövcuddur!")
                self.refresh_musteriler()
                self.refresh_musteri_combo()

    def edit_musteri(self, cid):
        with db_connection() as conn:
            c = conn.execute("SELECT * FROM musteriler WHERE id=?", (cid,)).fetchone()
        if not c: return
        dialog = MusteriDialog(self, c)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                ad, nagd, borc = data
                with db_connection() as conn:
                    try:
                        conn.execute("UPDATE musteriler SET ad=?, nagd=?, borc=? WHERE id=?", (ad, nagd, borc, cid))
                        conn.commit()
                    except sqlite3.IntegrityError:
                        QMessageBox.warning(self, "Xəta", "Bu müştəri adı artıq mövcuddur!")
                self.refresh_musteriler()
                self.refresh_musteri_combo()

    def remove_musteri(self, cid):
        reply = QMessageBox.question(self, "Sil", "Müştərini silmək istədiyinizdən əminsiniz?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            with db_connection() as conn:
                sales_count = conn.execute("SELECT COUNT(*) FROM satislar WHERE musteri_id=?", (cid,)).fetchone()[0]
                payment_count = conn.execute("SELECT COUNT(*) FROM odeyisler WHERE musteri_id=?", (cid,)).fetchone()[0]
                if sales_count > 0 or payment_count > 0:
                    QMessageBox.warning(self, "Xəta", "Bu müştəri ilə əlaqəli satış və ya ödəniş var, silmək mümkün deyil!")
                else:
                    conn.execute("DELETE FROM musteriler WHERE id=?", (cid,))
                    conn.commit()
            self.refresh_musteriler()
            self.refresh_musteri_combo()

    def pay_debt(self, cid):
        with db_connection() as conn:
            musteri = conn.execute("SELECT * FROM musteriler WHERE id=?", (cid,)).fetchone()
        if not musteri: return
        if musteri["borc"] <= 0:
            QMessageBox.information(self, "Məlumat", "Bu müştərinin borcu yoxdur!")
            return
        dialog = OdemeDialog(self, musteri)
        if dialog.exec() == QDialog.Accepted:
            odenis = dialog.get_data()
            if odenis is not None:
                tarix = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with db_connection() as conn:
                    conn.execute("UPDATE musteriler SET borc=borc-?, nagd=nagd+? WHERE id=?", (odenis, odenis, cid))
                    conn.execute("INSERT INTO odeyisler (musteri_id, odenis, tarix) VALUES (?, ?, ?)", (cid, odenis, tarix))
                    conn.commit()
                self.refresh_musteriler()
                self.refresh_musteri_combo()
                self.generate_invoice(musteri["ad"], [("Borc Ödənişi", 1, odenis, odenis)], musteri["borc"], odenis, "Ödə", odenis_input=odenis)
                QMessageBox.information(self, "Uğur", "Ödəniş qeydə alındı!")
                self.show_report("today")

    def show_customer_statement(self, cid):
        with db_connection() as conn:
            musteri = conn.execute("SELECT * FROM musteriler WHERE id=?", (cid,)).fetchone()
        if not musteri: return
        dialog = CustomerStatementDialog(self, musteri)
        dialog.exec()

    def search_musteri(self):
        text = self.txt_search.text().lower()
        with db_connection() as conn:
            all_c = conn.execute("SELECT * FROM musteriler").fetchall()
        filtered = [c for c in all_c if text in c["ad"].lower()]
        self.tbl_musteriler.setRowCount(len(filtered))
        for i, c in enumerate(filtered):
            self.tbl_musteriler.setItem(i, 0, QTableWidgetItem(str(c["id"])))
            self.tbl_musteriler.setItem(i, 1, QTableWidgetItem(c["ad"]))
            self.tbl_musteriler.setItem(i, 2, QTableWidgetItem(f"{c['nagd']:.2f}"))
            self.tbl_musteriler.setItem(i, 3, QTableWidgetItem(f"{c['borc']:.2f}"))
            btn_edit = QPushButton("Redaktə")
            btn_remove = QPushButton("Sil")
            btn_ode = QPushButton("Ödə")
            btn_statement = QPushButton("Hesabat")
            btn_edit.clicked.connect(lambda checked, cid=c["id"]: self.edit_musteri(cid))
            btn_remove.clicked.connect(lambda checked, cid=c["id"]: self.remove_musteri(cid))
            btn_ode.clicked.connect(lambda checked, cid=c["id"]: self.pay_debt(cid))
            btn_statement.clicked.connect(lambda checked, cid=c["id"]: self.show_customer_statement(cid))
            hbox_btn = QHBoxLayout()
            hbox_btn.addWidget(btn_edit)
            hbox_btn.addWidget(btn_remove)
            hbox_btn.addWidget(btn_ode)
            hbox_btn.addWidget(btn_statement)
            hbox_btn.setContentsMargins(0, 0, 0, 0)
            cell_widget = QWidget()
            cell_widget.setLayout(hbox_btn)
            self.tbl_musteriler.setCellWidget(i, 4, cell_widget)

    def init_satis(self):
        self.tab_sales_layout.addWidget(QLabel("💰 Satış"))
        hbox = QHBoxLayout()
        self.cmb_musteri = QComboBox()
        self.cmb_mehsul = QComboBox()
        self.txt_miqdar = QLineEdit()
        self.txt_miqdar.setPlaceholderText("Miqdar")
        self.txt_birim_qiymet = QLineEdit()
        self.txt_birim_qiymet.setPlaceholderText("Birim Qiymət (defolt istifadə etmək üçün boş qoyun)")
        btn_add_item = QPushButton("Məhsulu Əlavə et")
        btn_add_item.clicked.connect(self.add_item_to_sale)
        hbox.addWidget(QLabel("Müştəri:"))
        hbox.addWidget(self.cmb_musteri)
        hbox.addWidget(QLabel("Məhsul:"))
        hbox.addWidget(self.cmb_mehsul)
        hbox.addWidget(QLabel("Miqdar:"))
        hbox.addWidget(self.txt_miqdar)
        hbox.addWidget(QLabel("Birim Qiymət:"))
        hbox.addWidget(self.txt_birim_qiymet)
        hbox.addWidget(btn_add_item)
        self.tab_sales_layout.addLayout(hbox)
        self.tbl_sale_items = QTableWidget()
        self.tbl_sale_items.setColumnCount(5)
        self.tbl_sale_items.setHorizontalHeaderLabels(["Məhsul", "Miqdar", "Birim Qiymət", "Ümumi Qiymət", "Əməliyyatlar"])
        self.tbl_sale_items.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_sale_items.setAlternatingRowColors(True)
        self.tbl_sale_items.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tab_sales_layout.addWidget(self.tbl_sale_items, stretch=1)
        hbox_final = QHBoxLayout()
        self.txt_beh = QLineEdit()
        self.txt_beh.setPlaceholderText("BEH (defolt 0)")
        self.cmb_odeyis = QComboBox()
        self.cmb_odeyis.addItems(["Nəğd", "Borc"])
        btn_finalize_sale = QPushButton("Satışı Yadda saxla")
        btn_finalize_sale.clicked.connect(self.finalize_sale)
        btn_clear_sale = QPushButton("Siyahını Təmizlə")
        btn_clear_sale.clicked.connect(self.clear_sale_items)
        hbox_final.addWidget(QLabel("BEH:"))
        hbox_final.addWidget(self.txt_beh)
        hbox_final.addWidget(QLabel("Ödəniş növü:"))
        hbox_final.addWidget(self.cmb_odeyis)
        hbox_final.addWidget(btn_finalize_sale)
        hbox_final.addWidget(btn_clear_sale)
        self.tab_sales_layout.addLayout(hbox_final)
        self.refresh_musteri_combo()
        self.refresh_mehsul_combo()

    def refresh_musteri_combo(self):
        with db_connection() as conn:
            self.musteri_list = conn.execute("SELECT * FROM musteriler").fetchall()
        self.cmb_musteri.clear()
        for c in self.musteri_list:
            self.cmb_musteri.addItem(f"{c['ad']} (Borc:{c['borc']:.2f})", c["id"])

    def refresh_mehsul_combo(self):
        with db_connection() as conn:
            self.mehsul_list = conn.execute("SELECT * FROM mehsullar").fetchall()
        self.cmb_mehsul.clear()
        for m in self.mehsul_list:
            self.cmb_mehsul.addItem(f"{m['ad']} (Stok:{m['stock']}, Qiymət:{m['qiymet']:.2f})", m["id"])

    def add_item_to_sale(self):
        try:
            miqdar = int(self.txt_miqdar.text())
            if miqdar <= 0: raise ValueError
        except:
            QMessageBox.warning(self, "Xəta", "Miqdar düzgün deyil!")
            return
        pid = self.cmb_mehsul.currentData()
        m = next((x for x in self.mehsul_list if x["id"] == pid), None)
        if not m: return
        current_added = sum(item["miqdar"] for item in self.sale_items if item["mehsul_id"] == pid)
        effective_stock = m["stock"] - current_added
        if miqdar > effective_stock:
            QMessageBox.warning(self, "Xəta", "Stok kifayət etmir! (Cari stok: " + str(m["stock"]) + ", Artıq əlavə edilmiş: " + str(current_added) + ")")
            return
        try:
            birim_qiymet_str = self.txt_birim_qiymet.text().strip()
            birim_qiymet = float(birim_qiymet_str) if birim_qiymet_str else m["qiymet"]
            if birim_qiymet < 0: raise ValueError
        except:
            QMessageBox.warning(self, "Xəta", "Birim qiymət düzgün deyil!")
            return
        qiymet = birim_qiymet * miqdar
        self.sale_items.append({
            "mehsul_id": pid,
            "ad": m["ad"],
            "miqdar": miqdar,
            "birim_qiymet": birim_qiymet,
            "qiymet": qiymet
        })
        self.refresh_sale_items_table()
        self.txt_miqdar.clear()
        self.txt_birim_qiymet.clear()

    def refresh_sale_items_table(self):
        self.tbl_sale_items.setRowCount(len(self.sale_items))
        for i, item in enumerate(self.sale_items):
            self.tbl_sale_items.setItem(i, 0, QTableWidgetItem(item["ad"]))
            self.tbl_sale_items.setItem(i, 1, QTableWidgetItem(str(item["miqdar"])))
            self.tbl_sale_items.setItem(i, 2, QTableWidgetItem(f"{item['birim_qiymet']:.2f}"))
            self.tbl_sale_items.setItem(i, 3, QTableWidgetItem(f"{item['qiymet']:.2f}"))
            btn_remove = QPushButton("Sil")
            btn_remove.clicked.connect(lambda checked, idx=i: self.remove_sale_item(idx))
            hbox_btn = QHBoxLayout()
            hbox_btn.addWidget(btn_remove)
            hbox_btn.setContentsMargins(0, 0, 0, 0)
            cell_widget = QWidget()
            cell_widget.setLayout(hbox_btn)
            self.tbl_sale_items.setCellWidget(i, 4, cell_widget)

    def remove_sale_item(self, index):
        self.sale_items.pop(index)
        self.refresh_sale_items_table()

    def clear_sale_items(self):
        self.sale_items.clear()
        self.refresh_sale_items_table()
        self.txt_beh.clear()

    def finalize_sale(self):
        if not self.sale_items:
            QMessageBox.warning(self, "Xəta", "Satış üçün heç bir məhsul seçilməyib!")
            return
        mid = self.cmb_musteri.currentData()
        c = next((x for x in self.musteri_list if x["id"] == mid), None)
        if not c: return
        odeyis = self.cmb_odeyis.currentText()
        total_amount = sum(item["qiymet"] for item in self.sale_items)
        beh = 0.0
        try:
            beh = float(self.txt_beh.text()) if self.txt_beh.text().strip() else 0.0
            if beh < 0: raise ValueError
        except:
            QMessageBox.warning(self, "Xəta", "BEH düzgün deyil!")
            return
        if odeyis == "Borc" and beh > total_amount:
            QMessageBox.warning(self, "Xəta", "BEH ümumi qiymətdən çox ola bilməz!")
            return
        if odeyis == "Nəğd" and beh > 0:
            beh = 0.0
        items_for_confirm = [(item["ad"], item["miqdar"], item["birim_qiymet"], item["qiymet"]) for item in self.sale_items]
        dialog = SatisConfirmDialog(self, c["ad"], items_for_confirm, total_amount, beh)
        if dialog.exec() != QDialog.Accepted:
            return
        tarix = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with db_connection() as conn:
            for item in self.sale_items:
                conn.execute("INSERT INTO satislar (musteri_id, mehsul_id, miqdar, birim_qiymet, qiymet, beh, odeyis_novu, tarix) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                             (mid, item["mehsul_id"], item["miqdar"], item["birim_qiymet"], item["qiymet"], beh if item == self.sale_items[-1] else 0.0, odeyis, tarix))
                conn.execute("UPDATE mehsullar SET stock=stock-? WHERE id=?", (item["miqdar"], item["mehsul_id"]))
            if odeyis == "Nəğd":
                conn.execute("UPDATE musteriler SET nagd=nagd+? WHERE id=?", (total_amount, mid))
            else:
                conn.execute("UPDATE musteriler SET borc=borc+?, nagd=nagd+? WHERE id=?", (total_amount - beh, beh, mid))
            conn.commit()
        self.refresh_mehsullar()
        self.refresh_musteriler()
        self.refresh_musteri_combo()
        self.refresh_mehsul_combo()
        self.generate_invoice(c["ad"], items_for_confirm, c["borc"], total_amount, odeyis, beh)
        QMessageBox.information(self, "Uğur", "Satış əlavə olundu!")
        self.sale_items.clear()
        self.refresh_sale_items_table()
        self.txt_beh.clear()
        self.show_report("today")

    def generate_invoice(self, c_name, items, old_debt, total_amount, payment_type, beh=0.0, odenis_input=0.0):
        now = datetime.now()
        invoice_num = get_invoice_number()
        tarix = now.strftime("%d.%m.%Y %H:%M")
        az_month_names = [
            "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
            "Iyul", "Avqust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
        ]
        month_name = az_month_names[now.month - 1]
        file_name = os.path.join(INVOICE_DIR, f"faktura_{now.year}{month_name}{now.day}_{now.strftime('%H%M%S')}.pdf")
        table_rows = ""
        for i, (p_name, miqdar, birim_qiymet, qiymet) in enumerate(items, 1):
            table_rows += f"<tr><td>{i}</td><td>{p_name}</td><td>{miqdar}</td><td>ƏDƏD</td><td>{birim_qiymet:.2f}</td><td></td><td></td><td>{qiymet:.2f}</td></tr>"

        def num_to_words(n):
            if n < 0: return "minus " + num_to_words(abs(n))
            if n == 0: return "sıfır"
            words, units = [], ["", "min", "milyon", "milyard"]
            idx = 0
            while n > 0:
                digit = n % 1000
                if digit > 0:
                    hundreds = digit // 100
                    tens = (digit % 100) // 10
                    ones = digit % 10
                    word = ""
                    if hundreds > 0:
                        word += ["", "yüz", "iki yüz", "üç yüz", "dörd yüz", "beş yüz", "altı yüz", "yeddi yüz", "səkkiz yüz", "doqquz yüz"][hundreds] + " "
                    if tens == 1:
                        word += ["on", "on bir", "on iki", "on üç", "on dörd", "on beş", "on altı", "on yeddi", "on səkkiz", "on doqquz"][ones] + " "
                    elif tens > 1:
                        word += ["iyirmi", "otuz", "qırx", "əlli", "altmış", "yetmiş", "səksən", "doxsan"][tens-2] + " "
                        if ones > 0:
                            word += ["", "bir", "iki", "üç", "dörd", "beş", "altı", "yeddi", "səkkiz", "doqquz"][ones] + " "
                    else:
                        word += ["", "bir", "iki", "üç", "dörd", "beş", "altı", "yeddi", "səkkiz", "doqquz"][ones] + " "
                    if units[idx]: 
                        word += units[idx] + " "
                    words.insert(0, word)
                n //= 1000
                idx += 1
            return " ".join(words).rstrip()

        if payment_type == "Nəğd":
            nagd = total_amount
            new_debt = old_debt
        elif payment_type == "Borc":
            nagd = beh
            new_debt = old_debt + total_amount - beh
        elif payment_type == "Ödə":
            nagd = odenis_input
            new_debt = max(0.0, old_debt - odenis_input)
        elif payment_type == "Hesabat":
            nagd = odenis_input
            new_debt = old_debt + total_amount - nagd
        else:
            nagd = beh
            new_debt = old_debt + (total_amount - beh)

        nagd_words = num_to_words(int(nagd)) + " manat " + str(int((nagd % 1) * 100)) + " qəpik"

        html_content = f"""
<html>
<head>
    <style>
        @page {{ size: A4 landscape; margin: 20mm; }}
        body {{ font-family: Arial, sans-serif; font-size: 12pt; line-height: 1.4; }}
        .header {{ text-align: center; font-size: 16pt; font-weight: bold; margin-bottom: 8mm; }}
        .details {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 3mm 10mm; margin-bottom: 8mm; font-size: 11pt; }}
        .details p {{ margin: 0; }}
        .table {{ width: 100%; border-collapse: collapse; margin-bottom: 8mm; }}
        .table th, .table td {{ border: 1px solid black; padding: 2mm 4mm; text-align: center; }}
        .table th {{ background-color: #f2f2f2; }}
        .totals {{ text-align: right; margin-bottom: 5mm; }}
        .signatures {{ display: flex; justify-content: space-between; margin-top: 15mm; }}
        .debt-section {{ margin-top: 8mm; border: 1px solid #ccc; padding: 4mm; background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="header">&lt;&lt;LAMINAT&gt;&gt;</div>
    <div class="details">
        <p><strong>Malların satışı:</strong> {invoice_num}</p>
        <p><strong>Tarix:</strong> {tarix}</p>
        <p><strong>Satıcı:</strong> Tahir </p>
        <p><strong>Alıcı:</strong> {c_name}</p>
        <p><strong>Valyuta:</strong> AZN</p>
    </div>
    <table class="table">
        <tr>
            <th>Nº</th><th>Məhsul</th><th>Miqdar</th><th>Ölçü V.</th><th>Qiymət (AZN)</th><th>%</th><th>Endirim</th><th>Cəmi (AZN)</th>
        </tr>
        {table_rows}
    </table>
    <div class="totals">
        <p>Ümumi Məbləğ: <strong>{total_amount:.2f} AZN</strong></p>
    </div>
    <div class="debt-section">
        <h3>Borc Məlumatları</h3>
        <p>Köhnə Borc: {old_debt:.2f} AZN</p>
        <p>Nagd: {nagd:.2f} AZN (Sözlə: {nagd_words})</p>
        <p>Yekun Borc: {new_debt:.2f} AZN</p>
    </div>
    <div class="signatures">
        <p>Təhvil Aldı: __________________</p>
        <p>Təhvil Verdi: __________________</p>
    </div>
    <p><em>Qeyd: Faktura məlumatları satış tarixindən asılıdır.</em></p>
</body>
</html>
"""
        css = CSS(string='@page { size: A4 landscape; }')
        HTML(string=html_content).write_pdf(file_name, stylesheets=[css])
        QMessageBox.information(self, "Faktura", f"Faktura PDF yaradıldı: {os.path.basename(file_name)}")

    def delete_transaction(self, nov, rid):
        with db_connection() as conn:
            if nov == "Satış":
                s = conn.execute("SELECT * FROM satislar WHERE id=?", (rid,)).fetchone()
                if s:
                    reply = QMessageBox.question(self, "Sil", "Bu satışı silmək istədiyinizdən əminsiniz?", QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        conn.execute("UPDATE mehsullar SET stock=stock+? WHERE id=?", (s["miqdar"], s["mehsul_id"]))
                        if s["odeyis_novu"] == "Nəğd":
                            conn.execute("UPDATE musteriler SET nagd=nagd-? WHERE id=?", (s["qiymet"], s["musteri_id"]))
                        else:
                            conn.execute("UPDATE musteriler SET borc=borc-?, nagd=nagd-? WHERE id=?", (s["qiymet"] - s["beh"], s["beh"], s["musteri_id"]))
                        conn.execute("DELETE FROM satislar WHERE id=?", (rid,))
                        conn.commit()
            elif nov == "Ödəniş":
                o = conn.execute("SELECT * FROM odeyisler WHERE id=?", (rid,)).fetchone()
                if o:
                    reply = QMessageBox.question(self, "Sil", "Bu ödənişi silmək istədiyinizdən əminsiniz?", QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        conn.execute("UPDATE musteriler SET borc=borc+?, nagd=nagd-? WHERE id=?", (o["odenis"], o["odenis"], o["musteri_id"]))
                        conn.execute("DELETE FROM odeyisler WHERE id=?", (rid,))
                        conn.commit()
        self.refresh_all()

    def init_hesabat(self):
        self.tab_reports_layout.addWidget(QLabel("📊 Hesabatlar"))
        self.lbl_totals = QLabel("")
        self.tab_reports_layout.addWidget(self.lbl_totals)
        hbox_period = QHBoxLayout()
        btn_today = QPushButton("Bu gün")
        btn_today.clicked.connect(lambda: self.show_report("today"))
        btn_yesterday = QPushButton("Dünən")
        btn_yesterday.clicked.connect(lambda: self.show_report("yesterday"))
        btn_week = QPushButton("Bu həftə")
        btn_week.clicked.connect(lambda: self.show_report("week"))
        btn_month = QPushButton("Bu ay")
        btn_month.clicked.connect(lambda: self.show_report("month"))
        btn_year = QPushButton("Bu il")
        btn_year.clicked.connect(lambda: self.show_report("year"))
        btn_all = QPushButton("Bütün Hesabat")
        btn_all.clicked.connect(lambda: self.show_report("all"))
        hbox_period.addWidget(btn_today)
        hbox_period.addWidget(btn_yesterday)
        hbox_period.addWidget(btn_week)
        hbox_period.addWidget(btn_month)
        hbox_period.addWidget(btn_year)
        hbox_period.addWidget(btn_all)
        self.tab_reports_layout.addLayout(hbox_period)
        hbox_custom = QHBoxLayout()
        lbl_start = QLabel("Başlanğıc Tarix:")
        self.start_date = QDateEdit(QDate.currentDate())
        lbl_end = QLabel("Bitiş Tarix:")
        self.end_date = QDateEdit(QDate.currentDate())
        btn_custom = QPushButton("Göstər")
        btn_custom.clicked.connect(lambda: self.show_report("custom", self.start_date.date().toPyDate(), self.end_date.date().toPyDate()))
        hbox_custom.addWidget(lbl_start)
        hbox_custom.addWidget(self.start_date)
        hbox_custom.addWidget(lbl_end)
        hbox_custom.addWidget(self.end_date)
        hbox_custom.addWidget(btn_custom)
        self.tab_reports_layout.addLayout(hbox_custom)
        btn_open_faktura = QPushButton("Faktura Qovluğunu Aç")
        btn_open_faktura.clicked.connect(self.open_invoice_folder)
        self.tab_reports_layout.addWidget(btn_open_faktura)
        btn_detailed = QPushButton("Detallı Hesabatlar")
        btn_detailed.clicked.connect(self.show_detailed_reports)
        self.tab_reports_layout.addWidget(btn_detailed)
        self.tbl_report = QTableWidget()
        self.tab_reports_layout.addWidget(self.tbl_report, stretch=1)
        self.tbl_report.setColumnCount(13)
        self.tbl_report.setHorizontalHeaderLabels(["Növ", "ID", "Tarix", "Müştəri", "Məhsul", "Miqdar", "Birim Qiymət", "Qiymət", "BEH", "Ödəniş Növü", "Nağd", "Borc", "Əməliyyatlar"])
        self.tbl_report.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl_report.setAlternatingRowColors(True)
        self.tbl_report.setEditTriggers(QTableWidget.NoEditTriggers)
        self.show_report("today")

    def show_detailed_reports(self):
        dialog = DetailedReportDialog(self, self.current_period, self.current_start, self.current_end)
        dialog.exec()

    def show_report(self, period, start=None, end=None):
        self.current_period = period
        self.current_start = start
        self.current_end = end
        with db_connection() as conn:
            q = """SELECT s.*, s.beh, p.ad as mehsul, p.maya_deyeri, m.ad as musteri, m.nagd, m.borc 
                FROM satislar s 
                JOIN musteriler m ON s.musteri_id=m.id 
                JOIN mehsullar p ON s.mehsul_id=p.id"""
            sales = conn.execute(q).fetchall()
            q_payments = """SELECT o.*, 'Borc Ödənişi' as mehsul, m.ad as musteri, 0 as maya_deyeri
                            FROM odeyisler o 
                            JOIN musteriler m ON o.musteri_id=m.id"""
            payments = conn.execute(q_payments).fetchall()
            all_musteriler = conn.execute("SELECT borc FROM musteriler").fetchall()
        now = datetime.now()
        filtered_sales = []
        filtered_payments = []
        total_nagd = 0.0
        total_borc = 0.0
        total_paid_borc = 0.0
        total_profit_all = 0.0
        total_profit_cash = 0.0
        for r in sales:
            t = datetime.strptime(r["tarix"], "%Y-%m-%d %H:%M:%S")
            if self.get_date_filter(t, period, now, start, end):
                filtered_sales.append(r)
                profit = r["qiymet"] - (r["maya_deyeri"] * r["miqdar"])
                total_profit_all += profit
                if r["odeyis_novu"] == "Nəğd":
                    total_profit_cash += profit
                total_nagd += r["qiymet"] if r["odeyis_novu"] == "Nəğd" else r["beh"]
                total_borc += r["qiymet"] - r["beh"] if r["odeyis_novu"] == "Borc" else 0.0
        for p in payments:
            t = datetime.strptime(p["tarix"], "%Y-%m-%d %H:%M:%S")
            if self.get_date_filter(t, period, now, start, end):
                filtered_payments.append(p)
                total_nagd += p["odenis"]
                total_paid_borc += p["odenis"]
        total_borc = max(0.0, total_borc - total_paid_borc)
        total_qazanc = total_nagd + total_paid_borc
        total_cari_borc = sum(m["borc"] for m in all_musteriler)
        self.lbl_totals.setText(
            f"Ümumi Qazanc: {total_qazanc:.2f} AZN | Ümumi Xeyir (Borc+Nağd): {total_profit_all:.2f} AZN | "
            f"Ümumi Xeyir (Yalnız Nağd): {total_profit_cash:.2f} AZN\n"
            f"Ödənilməmiş Borc: {total_borc:.2f} AZN | Ödənilmiş Borc: {total_paid_borc:.2f} AZN | "
            f"Cari Borclar Cəmi: {total_cari_borc:.2f} AZN"
        )
        all_rows = []
        for r in filtered_sales:
            all_rows.append({
                "nov": "Satış",
                "id": r["id"],
                "tarix": r["tarix"],
                "musteri": r["musteri"],
                "mehsul": r["mehsul"],
                "miqdar": r["miqdar"],
                "birim_qiymet": r["birim_qiymet"],
                "qiymet": r["qiymet"],
                "beh": r["beh"],
                "odeyis_novu": r["odeyis_novu"],
                "nagd": r["qiymet"] if r["odeyis_novu"] == "Nəğd" else r["beh"],
                "borc": r["qiymet"] - r["beh"] if r["odeyis_novu"] == "Borc" else 0.0
            })
        for p in filtered_payments:
            all_rows.append({
                "nov": "Ödəniş",
                "id": p["id"],
                "tarix": p["tarix"],
                "musteri": p["musteri"],
                "mehsul": p["mehsul"],
                "miqdar": 0,
                "birim_qiymet": 0.0,
                "qiymet": p["odenis"],
                "beh": 0.0,
                "odeyis_novu": "Ödənmiş",
                "nagd": p["odenis"],
                "borc": 0.0
            })
        all_rows.sort(key=lambda x: datetime.strptime(x["tarix"], "%Y-%m-%d %H:%M:%S"), reverse=True)
        self.tbl_report.setRowCount(len(all_rows))
        for i, r in enumerate(all_rows):
            self.tbl_report.setItem(i, 0, QTableWidgetItem(r["nov"]))
            self.tbl_report.setItem(i, 1, QTableWidgetItem(str(r["id"])))
            self.tbl_report.setItem(i, 2, QTableWidgetItem(r["tarix"]))
            self.tbl_report.setItem(i, 3, QTableWidgetItem(r["musteri"]))
            self.tbl_report.setItem(i, 4, QTableWidgetItem(r["mehsul"]))
            self.tbl_report.setItem(i, 5, QTableWidgetItem(str(r["miqdar"])))
            self.tbl_report.setItem(i, 6, QTableWidgetItem(f"{r['birim_qiymet']:.2f}"))
            self.tbl_report.setItem(i, 7, QTableWidgetItem(f"{r['qiymet']:.2f}"))
            self.tbl_report.setItem(i, 8, QTableWidgetItem(f"{r['beh']:.2f}"))
            self.tbl_report.setItem(i, 9, QTableWidgetItem(r["odeyis_novu"]))
            self.tbl_report.setItem(i, 10, QTableWidgetItem(f"{r['nagd']:.2f}"))
            self.tbl_report.setItem(i, 11, QTableWidgetItem(f"{r['borc']:.2f}"))
            btn_delete = QPushButton("Sil")
            btn_delete.clicked.connect(lambda checked, nov=r["nov"], rid=r["id"]: self.delete_transaction(nov, rid))
            hbox_btn = QHBoxLayout()
            hbox_btn.addWidget(btn_delete)
            hbox_btn.setContentsMargins(0, 0, 0, 0)
            cell_widget = QWidget()
            cell_widget.setLayout(hbox_btn)
            self.tbl_report.setCellWidget(i, 12, cell_widget)

    def get_date_filter(self, t, period, now, start, end):
        include = False
        if period == "today" and t.date() == now.date():
            include = True
        elif period == "yesterday" and t.date() == (now - timedelta(days=1)).date():
            include = True
        elif period == "week" and t.isocalendar()[1] == now.isocalendar()[1] and t.year == now.year:
            include = True
        elif period == "month" and t.month == now.month and t.year == now.year:
            include = True
        elif period == "year" and t.year == now.year:
            include = True
        elif period == "all":
            include = True
        elif period == "custom" and start <= t.date() <= end:
            include = True
        return include

    def init_backup_restore(self):
        for layout in [self.tab_products_customers_layout, self.tab_sales_layout, self.tab_reports_layout]:
            layout.addWidget(QLabel("💾 Backup və Restore"))
            hbox = QHBoxLayout()
            btn_backup = QPushButton("Məlumat Bazasını Saxla (Backup)")
            btn_backup.clicked.connect(self.backup_db)
            btn_restore = QPushButton("Məlumat Bazasını Bərpa et (Restore)")
            btn_restore.clicked.connect(self.restore_db)
            btn_new_db = QPushButton("Yeni Boş Məlumat Bazası Yarat")
            btn_new_db.clicked.connect(self.new_db)
            hbox.addWidget(btn_backup)
            hbox.addWidget(btn_restore)
            hbox.addWidget(btn_new_db)
            layout.addLayout(hbox)

    def backup_db(self):
        now = datetime.now()
        az_month_names = [
            "Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun",
            "Iyul", "Avqust", "Sentyabr", "Oktyabr", "Noyabr", "Dekabr"
        ]
        month_name = az_month_names[now.month - 1]
        base_name = f"{now.year}{month_name}{now.day}"
        counter = 1
        backup_name = f"{base_name}_{counter}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_name)
        while os.path.exists(backup_path):
            counter += 1
            backup_name = f"{base_name}_{counter}.db"
            backup_path = os.path.join(BACKUP_DIR, backup_name)
        try:
            shutil.copy(DB_FILE, backup_path)
            QMessageBox.information(self, "Uğur", f"Backup yaradıldı: {backup_name}")
        except Exception as e:
            QMessageBox.warning(self, "Xəta", f"Backup yaradılmadı: {e}")

    def restore_db(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Database Seç", BACKUP_DIR, "SQLite Files (*.db)")
        if file_path:
            reply = QMessageBox.question(self, "Təsdiq", "Cari database-i əvəz etmək istədiyinizdən əminsiniz? Bütün cari məlumatlar itiriləcək!", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    shutil.copy(file_path, DB_FILE)
                    QMessageBox.information(self, "Uğur", "Database restore edildi. Dəyişiklikləri görmək üçün proqramı yenidən başladın.")
                    self.refresh_all()
                except Exception as e:
                    QMessageBox.warning(self, "Xəta", f"Restore edilmədi: {e}")

    def new_db(self):
        reply = QMessageBox.question(self, "Təsdiq", "Yeni boş database yaratmaq istədiyinizdən əminsiniz? Bütün cari məlumatlar itiriləcək!", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                os.remove(DB_FILE)
                init_db()
                QMessageBox.information(self, "Uğur", "Yeni database yaradıldı.")
                self.refresh_all()
            except Exception as e:
                QMessageBox.warning(self, "Xəta", f"Yeni database yaradılmadı: {e}")

    def refresh_all(self):
        self.refresh_mehsullar()
        self.refresh_musteriler()
        self.refresh_musteri_combo()
        self.refresh_mehsul_combo()
        self.show_report("today")

# ---------- RUN ----------
if __name__ == "__main__":
    try:
        check_db_writable()  # Check permissions before initializing
        init_db()  # Initialize the database
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except PermissionError as e:
        print(f"Error: {e}")
        sys.exit(1)