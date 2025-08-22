"""
PyQt5 POS Application
---------------------
This file converts the CLI POS to a PyQt5 desktop application. Features:
- Product management (add/list), with expiry and near-expiry alerts
- Sales (with VAT calculation, stock decrement, sales recorded)
- Expenses (net + VAT recorded)
- Reports: P&L, VAT summary, monthly VAT breakdown
- Export VAT monthly breakdown to CSV

Run:
    python pos_gui.py

Requirements:
    pip install PyQt5

Note: This app uses the same SQLite database (pos_system.db) as the CLI version.
"""

import sys
import sqlite3
import csv
from datetime import datetime, timedelta
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QLabel, QLineEdit, QFormLayout, QDialog, QDialogButtonBox, QMessageBox,
    QTableWidget, QTableWidgetItem, QSpinBox, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt

# ---------- Config ----------
DB_NAME = "pos_system.db"
VAT_RATE = 0.16  # 16% VAT
NEAR_EXPIRY_DAYS = 7
DATE_FMT = "%Y-%m-%d"

# ---------- Database / POS Logic ----------
class POS:
    def __init__(self, db_path: str = DB_NAME):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.init_db()

    def init_db(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL,
                quantity INTEGER NOT NULL,
                expiry DATE NOT NULL
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                quantity INTEGER,
                subtotal REAL,
                vat REAL,
                total REAL,
                date TEXT,
                FOREIGN KEY(product_id) REFERENCES products(id)
            );
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                vat REAL,
                total REAL,
                date TEXT
            );
            """
        )
        self.conn.commit()

    # Products
    def add_product(self, name: str, price: float, cost: float, quantity: int, expiry: str) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO products (name, price, cost, quantity, expiry) VALUES (?, ?, ?, ?, ?)",
            (name, price, cost, quantity, expiry),
        )
        self.conn.commit()
        return cur.lastrowid

    def list_products(self):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, price, cost, quantity, expiry FROM products ORDER BY name")
        return cur.fetchall()

    def get_product(self, product_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, price, cost, quantity, expiry FROM products WHERE id=?", (product_id,))
        return cur.fetchone()

    # Sales
    def sell_product(self, product_id: int, quantity: int = 1, today: Optional[str] = None, near_days: int = NEAR_EXPIRY_DAYS):
        cur = self.conn.cursor()
        cur.execute("SELECT id, name, price, cost, quantity, expiry FROM products WHERE id=?", (product_id,))
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "not_found"}
        pid, name, price, cost, stock_qty, expiry = row
        t = datetime.strptime(today, DATE_FMT).date() if today else datetime.today().date()
        exp = datetime.strptime(expiry, DATE_FMT).date()

        if exp < t:
            return {"ok": False, "error": "expired", "expired_on": expiry, "product": name}

        warning = None
        if exp <= t + timedelta(days=near_days):
            warning = f"{name} is near expiry ({expiry})"

        if stock_qty < quantity:
            return {"ok": False, "error": "insufficient_stock", "available": stock_qty}

        subtotal = round(price * quantity, 2)
        vat = round(subtotal * VAT_RATE, 2)
        total = round(subtotal + vat, 2)

        cur.execute("UPDATE products SET quantity = quantity - ? WHERE id=?", (quantity, pid))
        cur.execute(
            "INSERT INTO sales (product_id, quantity, subtotal, vat, total, date) VALUES (?, ?, ?, ?, ?, ?)",
            (pid, quantity, subtotal, vat, total, t.strftime(DATE_FMT)),
        )
        self.conn.commit()
        return {"ok": True, "product": name, "quantity": quantity, "subtotal": subtotal, "vat": vat, "total": total, "warning": warning}

    # Expenses
    def add_expense(self, description: str, amount: float, today: Optional[str] = None):
        d = today if today else datetime.today().strftime(DATE_FMT)
        vat = round(amount * VAT_RATE, 2)
        total = round(amount + vat, 2)
        cur = self.conn.cursor()
        cur.execute("INSERT INTO expenses (description, amount, vat, total, date) VALUES (?, ?, ?, ?, ?)", (description, amount, vat, total, d))
        self.conn.commit()
        return cur.lastrowid

    # Reports
    def report(self, near_days: int = NEAR_EXPIRY_DAYS):
        cur = self.conn.cursor()
        cur.execute("SELECT COALESCE(SUM(subtotal),0), COALESCE(SUM(vat),0), COALESCE(SUM(total),0) FROM sales")
        total_subtotal, total_vat_sales, total_sales = cur.fetchone()

        cur.execute("SELECT COALESCE(SUM(s.quantity * p.cost),0) FROM sales s JOIN products p ON p.id = s.product_id")
        cogs = cur.fetchone()[0]

        cur.execute("SELECT COALESCE(SUM(amount),0), COALESCE(SUM(vat),0), COALESCE(SUM(total),0) FROM expenses")
        net_expenses, vat_expenses, total_expenses = cur.fetchone()

        operating_profit = round(total_subtotal - (cogs + net_expenses), 2)
        net_profit_after_vat = round(operating_profit + (vat_expenses - total_vat_sales), 2)

        # expiry lists (only where quantity > 0)
        t = datetime.today().date()
        cur.execute("SELECT name, expiry, quantity FROM products")
        expired = []
        near = []
        for name, expiry, qty in cur.fetchall():
            if qty <= 0:
                continue
            d = datetime.strptime(expiry, DATE_FMT).date()
            if d < t:
                expired.append({"name": name, "expiry": expiry, "qty": qty})
            elif d <= t + timedelta(days=near_days):
                near.append({"name": name, "expiry": expiry, "qty": qty})

        return {
            "sales": round(total_subtotal, 2),
            "vat_sales": round(total_vat_sales, 2),
            "gross_sales": round(total_sales, 2),
            "cogs": round(cogs, 2),
            "net_expenses": round(net_expenses, 2),
            "vat_expenses": round(vat_expenses, 2),
            "total_expenses": round(total_expenses, 2),
            "operating_profit": operating_profit,
            "net_profit_after_vat": net_profit_after_vat,
            "expired": expired,
            "near_expiry": near,
        }

    def vat_monthly(self):
        cur = self.conn.cursor()
        cur.execute("SELECT strftime('%Y-%m', date) as m, COALESCE(SUM(vat),0) FROM sales GROUP BY m ORDER BY m")
        sales_vat = dict(cur.fetchall())
        cur.execute("SELECT strftime('%Y-%m', date) as m, COALESCE(SUM(vat),0) FROM expenses GROUP BY m ORDER BY m")
        exp_vat = dict(cur.fetchall())
        months = sorted(set(sales_vat.keys()) | set(exp_vat.keys()))
        rows = []
        for m in months:
            vs = round(sales_vat.get(m, 0), 2)
            ve = round(exp_vat.get(m, 0), 2)
            balance = round(ve - vs, 2)
            rows.append({"month": m, "vat_sales": vs, "vat_expenses": ve, "balance": balance})
        return rows

    def export_vat_monthly_csv(self, filepath: str):
        rows = self.vat_monthly()
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Month", "VAT Collected (Sales)", "VAT Paid (Expenses)", "Balance (Expenses - Sales)"])
            for r in rows:
                writer.writerow([r["month"], f"{r['vat_sales']:.2f}", f"{r['vat_expenses']:.2f}", f"{r['balance']:.2f}"])

# ---------- GUI Components ----------
class AddProductDialog(QDialog):
    def __init__(self, pos: POS, parent=None):
        super().__init__(parent)
        self.pos = pos
        self.setWindowTitle("Add Product")
        self.setModal(True)
        form = QFormLayout(self)
        self.name = QLineEdit()
        self.price = QLineEdit()
        self.cost = QLineEdit()
        self.qty = QSpinBox(); self.qty.setRange(0, 1000000)
        self.expiry = QLineEdit(); self.expiry.setPlaceholderText(DATE_FMT)
        form.addRow("Name:", self.name)
        form.addRow("Price:", self.price)
        form.addRow("Cost:", self.cost)
        form.addRow("Quantity:", self.qty)
        form.addRow("Expiry (YYYY-MM-DD):", self.expiry)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

    def save(self):
        try:
            name = self.name.text().strip()
            price = float(self.price.text())
            cost = float(self.cost.text())
            qty = int(self.qty.value())
            expiry = self.expiry.text().strip()
            # validate date
            datetime.strptime(expiry, DATE_FMT)
            if not name:
                raise ValueError("Name required")
        except Exception as e:
            QMessageBox.warning(self, "Validation Error", f"Invalid input: {e}")
            return
        self.pos.add_product(name, price, cost, qty, expiry)
        QMessageBox.information(self, "Success", "Product added")
        self.accept()

class SellProductDialog(QDialog):
    def __init__(self, pos: POS, parent=None):
        super().__init__(parent)
        self.pos = pos
        self.setWindowTitle("Sell Product")
        self.setModal(True)
        form = QFormLayout(self)
        self.product_cb = QComboBox()
        self.populate_products()
        self.qty = QSpinBox(); self.qty.setRange(1, 1000000)
        form.addRow("Product:", self.product_cb)
        form.addRow("Quantity:", self.qty)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(self.sell)
        buttons.rejected.connect(self.reject)

    def populate_products(self):
        self.product_cb.clear()
        for pid, name, price, cost, qty, expiry in self.pos.list_products():
            display = f"{name} (ID:{pid}) - ${price:.2f} - Qty:{qty} - Exp:{expiry}"
            self.product_cb.addItem(display, pid)

    def sell(self):
        pid = self.product_cb.currentData()
        q = int(self.qty.value())
        res = self.pos.sell_product(pid, q)
        if not res.get("ok"):
            if res.get("error") == "expired":
                QMessageBox.critical(self, "Expired", f"Cannot sell - expired on {res.get('expired_on')}")
            elif res.get("error") == "insufficient_stock":
                QMessageBox.warning(self, "Stock", f"Insufficient stock. Available: {res.get('available')}")
            else:
                QMessageBox.critical(self, "Error", "Sale failed")
            return
        msg = f"Sold {res['quantity']}x {res['product']}\nSubtotal: ${res['subtotal']:.2f}\nVAT: ${res['vat']:.2f}\nTotal: ${res['total']:.2f}"
        if res.get("warning"):
            msg += f"\n\nWARNING: {res['warning']}"
        QMessageBox.information(self, "Sale Success", msg)
        self.accept()

class AddExpenseDialog(QDialog):
    def __init__(self, pos: POS, parent=None):
        super().__init__(parent)
        self.pos = pos
        self.setWindowTitle("Add Expense")
        self.setModal(True)
        form = QFormLayout(self)
        self.desc = QLineEdit()
        self.amount = QLineEdit()
        form.addRow("Description:", self.desc)
        form.addRow("Amount (net):", self.amount)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)
        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

    def save(self):
        try:
            desc = self.desc.text().strip()
            amount = float(self.amount.text())
            if not desc:
                raise ValueError("Description required")
        except Exception as e:
            QMessageBox.warning(self, "Validation Error", f"Invalid input: {e}")
            return
        self.pos.add_expense(desc, amount)
        QMessageBox.information(self, "Success", "Expense added")
        self.accept()

class ReportsDialog(QDialog):
    def __init__(self, pos: POS, parent=None):
        super().__init__(parent)
        self.pos = pos
        self.setWindowTitle("Reports")
        self.resize(700, 500)
        layout = QVBoxLayout(self)

        self.label = QLabel()
        self.label.setWordWrap(True)
        layout.addWidget(self.label)

        btn_export_vat = QPushButton("Export VAT Monthly CSV")
        btn_export_vat.clicked.connect(self.export_vat)
        layout.addWidget(btn_export_vat)

        self.refresh()

    def refresh(self):
        rpt = self.pos.report()
        text = []
        text.append(f"Net Sales (excl. VAT): ${rpt['sales']:.2f}")
        text.append(f"VAT Collected (Sales): ${rpt['vat_sales']:.2f}")
        text.append(f"Gross Sales (incl. VAT): ${rpt['gross_sales']:.2f}")
        text.append(f"Cost of Goods Sold: ${rpt['cogs']:.2f}")
        text.append(f"Net Expenses (excl. VAT): ${rpt['net_expenses']:.2f}")
        text.append(f"VAT on Expenses: ${rpt['vat_expenses']:.2f}")
        text.append(f"Total Expenses (incl. VAT): ${rpt['total_expenses']:.2f}")
        text.append(f"Operating Profit (before VAT): ${rpt['operating_profit']:.2f}")
        text.append(f"Net Profit (after VAT): ${rpt['net_profit_after_vat']:.2f}")

        if rpt['expired']:
            text.append('\nExpired products:')
            for e in rpt['expired']:
                text.append(f" - {e['name']} (qty {e['qty']}) expired {e['expiry']}")
        if rpt['near_expiry']:
            text.append('\nNear-expiry products:')
            for e in rpt['near_expiry']:
                text.append(f" - {e['name']} (qty {e['qty']}) expires {e['expiry']}")

        self.label.setText('\n'.join(text))

    def export_vat(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save VAT CSV", "vat_report.csv", "CSV Files (*.csv)")
        if not path:
            return
        try:
            self.pos.export_vat_monthly_csv(path)
            QMessageBox.information(self, "Exported", f"VAT monthly CSV exported to: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export: {e}")

# ---------- Main Window ----------
class MainWindow(QMainWindow):
    def __init__(self, pos: POS):
        super().__init__()
        self.pos = pos
        self.setWindowTitle("POS System - GUI")
        self.resize(600, 400)

        container = QWidget()
        layout = QVBoxLayout()

        # Buttons row
        row = QHBoxLayout()
        btn_products = QPushButton("Manage Products")
        btn_sell = QPushButton("Sell Product")
        btn_expense = QPushButton("Add Expense")
        btn_reports = QPushButton("Reports")
        row.addWidget(btn_products)
        row.addWidget(btn_sell)
        row.addWidget(btn_expense)
        row.addWidget(btn_reports)

        layout.addLayout(row)

        # Products table
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Cost", "Qty", "Expiry"])
        layout.addWidget(self.table)

        # Bottom actions
        bottom = QHBoxLayout()
        btn_add = QPushButton("Add Product")
        btn_refresh = QPushButton("Refresh List")
        btn_seed = QPushButton("Seed Sample Data")
        bottom.addWidget(btn_add)
        bottom.addWidget(btn_refresh)
        bottom.addWidget(btn_seed)
        layout.addLayout(bottom)

        container.setLayout(layout)
        self.setCentralWidget(container)

        # Connections
        btn_add.clicked.connect(self.open_add_product)
        btn_refresh.clicked.connect(self.load_products)
        btn_seed.clicked.connect(self.seed)
        btn_products.clicked.connect(self.open_add_product)
        btn_sell.clicked.connect(self.open_sell)
        btn_expense.clicked.connect(self.open_expense)
        btn_reports.clicked.connect(self.open_reports)

        self.load_products()

    def load_products(self):
        rows = self.pos.list_products()
        self.table.setRowCount(0)
        for r in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            for c, value in enumerate(r):
                item = QTableWidgetItem(str(value))
                if c == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row_idx, c, item)

    def open_add_product(self):
        d = AddProductDialog(self.pos, self)
        if d.exec_():
            self.load_products()

    def open_sell(self):
        d = SellProductDialog(self.pos, self)
        if d.exec_():
            self.load_products()

    def open_expense(self):
        d = AddExpenseDialog(self.pos, self)
        if d.exec_():
            pass

    def open_reports(self):
        d = ReportsDialog(self.pos, self)
        d.exec_()

    def seed(self):
        # Add a few sample products
        try:
            self.pos.add_product("Milk", 1.5, 1.0, 10, (datetime.today() + timedelta(days=3)).strftime(DATE_FMT))
            self.pos.add_product("Bread", 1.0, 0.6, 5, (datetime.today() + timedelta(days=1)).strftime(DATE_FMT))
            self.pos.add_product("Juice", 2.0, 1.2, 0, (datetime.today() + timedelta(days=8)).strftime(DATE_FMT))
            self.pos.add_product("Cheese", 3.5, 2.0, 3, (datetime.today() + timedelta(days=6)).strftime(DATE_FMT))
            self.pos.add_product("Yogurt", 1.2, 0.8, 4, (datetime.today() - timedelta(days=7)).strftime(DATE_FMT))
            QMessageBox.information(self, "Seeded", "Sample products added")
            self.load_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to seed data: {e}")

# ---------- Entrypoint ----------
def main():
    app = QApplication(sys.argv)
    pos = POS()
    win = MainWindow(pos)
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
