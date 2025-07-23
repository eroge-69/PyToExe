import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, 
                            QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
                            QTableWidget, QTableWidgetItem, QMessageBox,
                            QTabWidget, QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate
from PyQt5 import QtGui

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Inventory Management System")
        self.setGeometry(100, 100, 800, 600)
        
        # Initialize database
        self.init_db()
        
        # Create main tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Add tabs
        self.create_product_tab()
        self.create_inventory_tab()
        self.create_report_tab()
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def init_db(self):
        self.conn = sqlite3.connect('inventory.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT,
                price REAL,
                cost REAL,
                stock_qty INTEGER,
                barcode TEXT,
                min_stock INTEGER
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                qty INTEGER,
                type TEXT,
                date TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_product_tab(self):
        # Product Management Tab
        product_tab = QWidget()
        layout = QVBoxLayout()
        
        # Form Widgets
        form_layout = QHBoxLayout()
        
        left_form = QVBoxLayout()
        self.name_input = QLineEdit()
        self.category_input = QLineEdit()
        self.price_input = QLineEdit()
        self.cost_input = QLineEdit()
        
        left_form.addWidget(QLabel("Product Name:"))
        left_form.addWidget(self.name_input)
        left_form.addWidget(QLabel("Category:"))
        left_form.addWidget(self.category_input)
        left_form.addWidget(QLabel("Price:"))
        left_form.addWidget(self.price_input)
        
        right_form = QVBoxLayout()
        self.stock_input = QLineEdit()
        self.barcode_input = QLineEdit()
        self.min_stock_input = QLineEdit()
        self.add_btn = QPushButton("Add Product")
        self.add_btn.clicked.connect(self.add_product)
        
        right_form.addWidget(QLabel("Initial Stock:"))
        right_form.addWidget(self.stock_input)
        right_form.addWidget(QLabel("Barcode:"))
        right_form.addWidget(self.barcode_input)
        right_form.addWidget(QLabel("Minimum Stock:"))
        right_form.addWidget(self.min_stock_input)
        right_form.addWidget(self.add_btn)
        
        form_layout.addLayout(left_form)
        form_layout.addLayout(right_form)
        
        # Product Table
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(7)
        self.product_table.setHorizontalHeaderLabels(["ID", "Name", "Category", "Price", "Stock", "Barcode", "Min Stock"])
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.product_table.cellDoubleClicked.connect(self.edit_product)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_products)
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_product)
        
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.delete_btn)
        
        # Add all to main layout
        layout.addLayout(form_layout)
        layout.addWidget(self.product_table)
        layout.addLayout(btn_layout)
        
        product_tab.setLayout(layout)
        self.tabs.addTab(product_tab, "Product Management")
        
        # Load initial data
        self.load_products()
    
    def create_inventory_tab(self):
        # Inventory Transactions Tab
        inventory_tab = QWidget()
        layout = QVBoxLayout()
        
        # Transaction Form
        form_layout = QHBoxLayout()
        
        left_form = QVBoxLayout()
        self.product_combo = QComboBox()
        self.trans_type_combo = QComboBox()
        self.trans_type_combo.addItems(["Purchase", "Sale", "Return"])
        
        left_form.addWidget(QLabel("Product:"))
        left_form.addWidget(self.product_combo)
        left_form.addWidget(QLabel("Transaction Type:"))
        left_form.addWidget(self.trans_type_combo)
        
        right_form = QVBoxLayout()
        self.trans_qty = QLineEdit()
        self.trans_date = QDateEdit()
        self.trans_date.setDate(QDate.currentDate())
        self.process_btn = QPushButton("Process Transaction")
        self.process_btn.clicked.connect(self.process_transaction)
        
        right_form.addWidget(QLabel("Quantity:"))
        right_form.addWidget(self.trans_qty)
        right_form.addWidget(QLabel("Date:"))
        right_form.addWidget(self.trans_date)
        right_form.addWidget(self.process_btn)
        
        form_layout.addLayout(left_form)
        form_layout.addLayout(right_form)
        
        # Transaction Table
        self.trans_table = QTableWidget()
        self.trans_table.setColumnCount(6)
        self.trans_table.setHorizontalHeaderLabels(["ID", "Product", "Type", "Qty", "Date", "Stock Change"])
        self.trans_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add all to main layout
        layout.addLayout(form_layout)
        layout.addWidget(self.trans_table)
        
        inventory_tab.setLayout(layout)
        self.tabs.addTab(inventory_tab, "Inventory Transactions")
        
        # Load initial data
        self.load_products_combo()
        self.load_transactions()
    
    def create_report_tab(self):
        # Reports Tab
        report_tab = QWidget()
        layout = QVBoxLayout()
        
        # Report Controls
        controls_layout = QHBoxLayout()
        self.report_type = QComboBox()
        self.report_type.addItems(["Stock Summary", "Low Stock Alert", "Transaction History"])
        self.generate_btn = QPushButton("Generate Report")
        self.generate_btn.clicked.connect(self.generate_report)
        
        controls_layout.addWidget(QLabel("Report Type:"))
        controls_layout.addWidget(self.report_type)
        controls_layout.addWidget(self.generate_btn)
        controls_layout.addStretch()
        
        # Report Table
        self.report_table = QTableWidget()
        self.report_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Add all to main layout
        layout.addLayout(controls_layout)
        layout.addWidget(self.report_table)
        
        report_tab.setLayout(layout)
        self.tabs.addTab(report_tab, "Reports")
    
    # Database Operations
    def add_product(self):
        name = self.name_input.text()
        category = self.category_input.text()
        price = self.price_input.text()
        cost = self.cost_input.text()
        stock = self.stock_input.text()
        barcode = self.barcode_input.text()
        min_stock = self.min_stock_input.text()
        
        if not name:
            QMessageBox.warning(self, "Warning", "Product name is required!")
            return
        
        try:
            self.cursor.execute('''
                INSERT INTO products (name, category, price, cost, stock_qty, barcode, min_stock)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, float(price), float(cost), int(stock), barcode, int(min_stock)))
            
            self.conn.commit()
            self.load_products()
            self.load_products_combo()
            
            # Clear form
            self.name_input.clear()
            self.category_input.clear()
            self.price_input.clear()
            self.cost_input.clear()
            self.stock_input.clear()
            self.barcode_input.clear()
            self.min_stock_input.clear()
            
            self.statusBar().showMessage("Product added successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add product: {str(e)}")
    
    def load_products(self):
        self.cursor.execute("SELECT * FROM products")
        products = self.cursor.fetchall()
        
        self.product_table.setRowCount(len(products))
        
        for row_idx, product in enumerate(products):
            for col_idx, value in enumerate(product):
                item = QTableWidgetItem(str(value))
                self.product_table.setItem(row_idx, col_idx, item)
    
    def load_products_combo(self):
        self.product_combo.clear()
        self.cursor.execute("SELECT id, name FROM products")
        products = self.cursor.fetchall()
        
        for product in products:
            self.product_combo.addItem(f"{product[0]} - {product[1]}", product[0])
    
    def load_transactions(self):
        self.cursor.execute('''
            SELECT t.id, p.name, t.type, t.qty, t.date, 
                   CASE WHEN t.type = 'Purchase' THEN '+' || t.qty 
                        WHEN t.type = 'Sale' THEN '-' || t.qty
                        ELSE t.qty END AS stock_change
            FROM transactions t
            JOIN products p ON t.product_id = p.id
            ORDER BY t.date DESC
        ''')
        transactions = self.cursor.fetchall()
        
        self.trans_table.setRowCount(len(transactions))
        
        for row_idx, trans in enumerate(transactions):
            for col_idx, value in enumerate(trans):
                item = QTableWidgetItem(str(value))
                self.trans_table.setItem(row_idx, col_idx, item)
    
    def edit_product(self, row, col):
        product_id = self.product_table.item(row, 0).text()
        self.cursor.execute("SELECT * FROM products WHERE id=?", (product_id,))
        product = self.cursor.fetchone()
        
        if product:
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Product")
            layout = QVBoxLayout()
            
            # Form
            form_layout = QFormLayout()
            
            name_edit = QLineEdit(product[1])
            category_edit = QLineEdit(product[2])
            price_edit = QLineEdit(str(product[3]))
            cost_edit = QLineEdit(str(product[4]))
            stock_edit = QLineEdit(str(product[5]))
            barcode_edit = QLineEdit(product[6])
            min_stock_edit = QLineEdit(str(product[7]))
            
            form_layout.addRow("Name:", name_edit)
            form_layout.addRow("Category:", category_edit)
            form_layout.addRow("Price:", price_edit)
            form_layout.addRow("Cost:", cost_edit)
            form_layout.addRow("Stock:", stock_edit)
            form_layout.addRow("Barcode:", barcode_edit)
            form_layout.addRow("Min Stock:", min_stock_edit)
            
            # Buttons
            btn_layout = QHBoxLayout()
            save_btn = QPushButton("Save")
            cancel_btn = QPushButton("Cancel")
            
            def save_changes():
                try:
                    self.cursor.execute('''
                        UPDATE products SET 
                            name=?, category=?, price=?, cost=?, 
                            stock_qty=?, barcode=?, min_stock=?
                        WHERE id=?
                    ''', (
                        name_edit.text(),
                        category_edit.text(),
                        float(price_edit.text()),
                        float(cost_edit.text()),
                        int(stock_edit.text()),
                        barcode_edit.text(),
                        int(min_stock_edit.text()),
                        product_id
                    ))
                    self.conn.commit()
                    self.load_products()
                    self.load_products_combo()
                    dialog.close()
                    self.statusBar().showMessage("Product updated successfully", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Failed to update product: {str(e)}")
            
            save_btn.clicked.connect(save_changes)
            cancel_btn.clicked.connect(dialog.close)
            
            btn_layout.addWidget(save_btn)
            btn_layout.addWidget(cancel_btn)
            
            layout.addLayout(form_layout)
            layout.addLayout(btn_layout)
            
            dialog.setLayout(layout)
            dialog.exec_()
    
    def delete_product(self):
        selected = self.product_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Warning", "Please select a product to delete")
            return
        
        product_id = selected[0].text()
        product_name = selected[1].text()
        
        reply = QMessageBox.question(
            self, 
            "Confirm Delete", 
            f"Are you sure you want to delete '{product_name}'?", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # First delete related transactions
                self.cursor.execute("DELETE FROM transactions WHERE product_id=?", (product_id,))
                # Then delete the product
                self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                self.conn.commit()
                self.load_products()
                self.load_products_combo()
                self.load_transactions()
                self.statusBar().showMessage("Product deleted successfully", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete product: {str(e)}")
    
    def process_transaction(self):
        product_id = self.product_combo.currentData()
        trans_type = self.trans_type_combo.currentText()
        qty = self.trans_qty.text()
        date = self.trans_date.date().toString("yyyy-MM-dd")
        
        if not product_id:
            QMessageBox.warning(self, "Warning", "Please select a product")
            return
        
        if not qty.isdigit() or int(qty) <= 0:
            QMessageBox.warning(self, "Warning", "Please enter a valid quantity")
            return
        
        qty = int(qty)
        
        try:
            # Get current stock
            self.cursor.execute("SELECT stock_qty FROM products WHERE id=?", (product_id,))
            current_stock = self.cursor.fetchone()[0]
            
            # Calculate new stock
            if trans_type == "Purchase":
                new_stock = current_stock + qty
            elif trans_type == "Sale":
                if current_stock < qty:
                    QMessageBox.warning(self, "Warning", "Insufficient stock")
                    return
                new_stock = current_stock - qty
            else:  # Return
                new_stock = current_stock + qty
            
            # Update product stock
            self.cursor.execute("UPDATE products SET stock_qty=? WHERE id=?", (new_stock, product_id))
            
            # Add transaction record
            self.cursor.execute('''
                INSERT INTO transactions (product_id, qty, type, date)
                VALUES (?, ?, ?, ?)
            ''', (product_id, qty, trans_type, date))
            
            self.conn.commit()
            self.load_transactions()
            self.load_products()
            
            # Clear form
            self.trans_qty.clear()
            
            self.statusBar().showMessage("Transaction processed successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process transaction: {str(e)}")
    
    def generate_report(self):
        report_type = self.report_type.currentText()
        
        try:
            if report_type == "Stock Summary":
                self.cursor.execute('''
                    SELECT id, name, category, stock_qty, price, 
                           (stock_qty * price) as stock_value
                    FROM products
                    ORDER BY stock_value DESC
                ''')
                headers = ["ID", "Name", "Category", "Stock Qty", "Price", "Stock Value"]
                
            elif report_type == "Low Stock Alert":
                self.cursor.execute('''
                    SELECT id, name, category, stock_qty, min_stock
                    FROM products
                    WHERE stock_qty < min_stock
                    ORDER BY (min_stock - stock_qty) DESC
                ''')
                headers = ["ID", "Name", "Category", "Current Stock", "Min Stock"]
                
            else:  # Transaction History
                self.cursor.execute('''
                    SELECT t.date, p.name, t.type, t.qty, 
                           p.price, (t.qty * p.price) as value
                    FROM transactions t
                    JOIN products p ON t.product_id = p.id
                    ORDER BY t.date DESC
                ''')
                headers = ["Date", "Product", "Type", "Qty", "Unit Price", "Total Value"]
            
            data = self.cursor.fetchall()
            
            self.report_table.setColumnCount(len(headers))
            self.report_table.setHorizontalHeaderLabels(headers)
            self.report_table.setRowCount(len(data))
            
            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.report_table.setItem(row_idx, col_idx, item)
            
            self.statusBar().showMessage(f"{report_type} generated", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())