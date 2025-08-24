import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QSpinBox, QDoubleSpinBox, QMessageBox, QTabWidget,
                             QGroupBox, QFormLayout, QHeaderView, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

class RestaurantAccountingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نرم افزار حسابداری رستوران")
        self.setGeometry(100, 100, 1200, 800)
        self.set_dark_theme()
        self.initUI()
        self.initDatabase()
        self.loadMenuItems()
        self.updateInventoryTable()
        self.updateDailySales()
        
    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        QApplication.setPalette(dark_palette)
        
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        header = QLabel("سیستم حسابداری رستوران")
        header.setAlignment(Qt.AlignCenter)
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("padding: 15px; background-color: #2b2b2b; color: #ff9900;")
        main_layout.addWidget(header)
        
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        self.createSalesTab()
        self.createInventoryTab()
        self.createReportsTab()
        
        footer = QLabel(f"© {datetime.now().year} - نرم افزار حسابداری رستوران")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("padding: 10px; background-color: #2b2b2b; color: #cccccc;")
        main_layout.addWidget(footer)
        
    def createSalesTab(self):
        sales_tab = QWidget()
        layout = QVBoxLayout(sales_tab)
        
        title = QLabel("ثبت سفارشات")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffcc00; padding: 10px;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)
        
        menu_group = QGroupBox("منوی رستوران")
        menu_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff9900; }")
        menu_layout = QVBoxLayout()
        
        self.menu_table = QTableWidget()
        self.menu_table.setColumnCount(4)
        self.menu_table.setHorizontalHeaderLabels(["نام کالا", "قیمت", "موجودی", "عملیات"])
        menu_layout.addWidget(self.menu_table)
        menu_group.setLayout(menu_layout)
        layout.addWidget(menu_group)
        
        order_group = QGroupBox("سفارشات جاری")
        order_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff9900; }")
        order_layout = QVBoxLayout()
        
        self.order_table = QTableWidget()
        self.order_table.setColumnCount(4)
        self.order_table.setHorizontalHeaderLabels(["نام کالا", "تعداد", "قیمت واحد", "جمع"])
        order_layout.addWidget(self.order_table)
        order_group.setLayout(order_layout)
        layout.addWidget(order_group)
        
        footer_layout = QHBoxLayout()
        self.total_label = QLabel("جمع کل: 0 تومان")
        self.total_label.setStyleSheet("font-size: 12pt; font-weight: bold; color: #ff9900;")
        
        submit_btn = QPushButton("ثبت سفارش")
        submit_btn.setStyleSheet("QPushButton { background-color: #2ecc71; color: white; font-weight: bold; padding: 10px; }")
        submit_btn.clicked.connect(self.submitOrder)
        
        cancel_btn = QPushButton("لغو سفارش")
        cancel_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 10px; }")
        cancel_btn.clicked.connect(self.cancelOrder)
        
        footer_layout.addWidget(self.total_label)
        footer_layout.addWidget(submit_btn)
        footer_layout.addWidget(cancel_btn)
        layout.addLayout(footer_layout)
        
        self.tabs.addTab(sales_tab, "ثبت فروش")
        
    def createInventoryTab(self):
        inventory_tab = QWidget()
        layout = QVBoxLayout(inventory_tab)
        
        title = QLabel("مدیریت موجودی و منو")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffcc00; padding: 10px;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)
        
        form_group = QGroupBox("افزودن آیتم جدید به منو")
        form_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff9900; }")
        form_layout = QFormLayout()
        
        self.item_name = QLineEdit()
        self.item_price = QDoubleSpinBox()
        self.item_price.setMaximum(10000000)
        self.item_price.setPrefix("تومان ")
        self.item_stock = QSpinBox()
        self.item_stock.setMaximum(10000)
        
        form_layout.addRow("نام آیتم:", self.item_name)
        form_layout.addRow("قیمت:", self.item_price)
        form_layout.addRow("موجودی اولیه:", self.item_stock)
        
        add_btn = QPushButton("افزودن به منو")
        add_btn.setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 5px; }")
        add_btn.clicked.connect(self.addMenuItem)
        form_layout.addRow(add_btn)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        inventory_group = QGroupBox("موجودی کالاها")
        inventory_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff9900; }")
        inventory_layout = QVBoxLayout()
        
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(4)
        self.inventory_table.setHorizontalHeaderLabels(["ردیف", "نام کالا", "موجودی", "قیمت"])
        inventory_layout.addWidget(self.inventory_table)
        inventory_group.setLayout(inventory_layout)
        layout.addWidget(inventory_group)
        
        self.tabs.addTab(inventory_tab, "مدیریت موجودی")
        
    def createReportsTab(self):
        reports_tab = QWidget()
        layout = QVBoxLayout(reports_tab)
        
        title = QLabel("گزارشات و آمار")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #ffcc00; padding: 10px;")
        title.setAlignment(Qt.AlignRight)
        layout.addWidget(title)
        
        daily_stats = QGroupBox("آمار فروش روزانه")
        daily_stats.setStyleSheet("QGroupBox { font-weight: bold; color: #ff9900; }")
        stats_layout = QVBoxLayout()
        
        self.sales_label = QLabel("فروش امروز: 0 تومان")
        self.sales_label.setStyleSheet("font-size: 12pt; padding: 5px;")
        self.orders_label = QLabel("تعداد سفارشات: 0")
        self.orders_label.setStyleSheet("font-size: 12pt; padding: 5px;")
        self.profit_label = QLabel("سود امروز: 0 تومان")
        self.profit_label.setStyleSheet("font-size: 12pt; padding: 5px;")
        
        stats_layout.addWidget(self.sales_label)
        stats_layout.addWidget(self.orders_label)
        stats_layout.addWidget(self.profit_label)
        daily_stats.setLayout(stats_layout)
        layout.addWidget(daily_stats)
        
        sales_table_group = QGroupBox("جزئیات فروش امروز")
        sales_table_group.setStyleSheet("QGroupBox { font-weight: bold; color: #ff9900; }")
        sales_table_layout = QVBoxLayout()
        
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["زمان", "نام کالا", "تعداد", "قیمت", "جمع"])
        sales_table_layout.addWidget(self.sales_table)
        sales_table_group.setLayout(sales_table_layout)
        layout.addWidget(sales_table_group)
        
        update_btn = QPushButton("به‌روزرسانی گزارشات")
        update_btn.setStyleSheet("QPushButton { background-color: #9b59b6; color: white; font-weight: bold; padding: 10px; }")
        update_btn.clicked.connect(self.updateReports)
        layout.addWidget(update_btn)
        
        self.tabs.addTab(reports_tab, "گزارشات")
        
    def initDatabase(self):
        self.conn = sqlite3.connect('restaurant.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                quantity INTEGER,
                unit_price REAL,
                total_price REAL,
                order_time TEXT,
                FOREIGN KEY (item_id) REFERENCES menu (id)
            )
        ''')
        self.cursor.execute("SELECT COUNT(*) FROM menu")
        if self.cursor.fetchone()[0] == 0:
            default_items = [
                ("پلو خورشت مستدنی", 200000, 10),
                ("پلو جوجه کباب", 180000, 15),
                ("پلو ماهی جنوب", 250000, 8),
                ("کباب بختیاری", 300000, 12),
                ("خوراک قارچ", 150000, 20)
            ]
            for item in default_items:
                self.cursor.execute("INSERT INTO menu (name, price, stock) VALUES (?, ?, ?)", item)
        self.conn.commit()
        
    def loadMenuItems(self):
        self.cursor.execute("SELECT id, name, price, stock FROM menu")
        menu_items = self.cursor.fetchall()
        self.menu_table.setRowCount(len(menu_items))
        for row, item in enumerate(menu_items):
            item_id, name, price, stock = item
            self.menu_table.setItem(row, 0, QTableWidgetItem(name))
            self.menu_table.setItem(row, 1, QTableWidgetItem(f"{price:,.0f} تومان"))
            self.menu_table.setItem(row, 2, QTableWidgetItem(str(stock)))
            add_button = QPushButton("افزودن")
            add_button.setStyleSheet("QPushButton { background-color: #27ae60; color: white; }")
            add_button.clicked.connect(lambda checked, id=item_id, n=name, p=price: self.addToOrder(id, n, p))
            self.menu_table.setCellWidget(row, 3, add_button)
        self.menu_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def addToOrder(self, item_id, name, price):
        self.cursor.execute("SELECT stock FROM menu WHERE id = ?", (item_id,))
        stock = self.cursor.fetchone()[0]
        if stock < 1:
            QMessageBox.warning(self, "خطا", "موجودی این آیتم کافی نیست.")
            return
        row_count = self.order_table.rowCount()
        self.order_table.insertRow(row_count)
        self.order_table.setItem(row_count, 0, QTableWidgetItem(name))
        self.order_table.setItem(row_count, 1, QTableWidgetItem("1"))
        self.order_table.setItem(row_count, 2, QTableWidgetItem(f"{price:,.0f}"))
        self.order_table.setItem(row_count, 3, QTableWidgetItem(f"{price:,.0f}"))
        self.calculateTotal()
        
    def calculateTotal(self):
        total = 0
        for row in range(self.order_table.rowCount()):
            try:
                item_total = int(self.order_table.item(row, 3).text().replace(',', ''))
                total += item_total
            except:
                pass
        self.total_label.setText(f"جمع کل: {total:,.0f} تومان")
        
    def submitOrder(self):
        if self.order_table.rowCount() == 0:
            QMessageBox.warning(self, "خطا", "هیچ آیتمی در سفارش وجود ندارد.")
            return
        order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for row in range(self.order_table.rowCount()):
            item_name = self.order_table.item(row, 0).text()
            quantity = 1
            unit_price = int(self.order_table.item(row, 2).text().replace(',', ''))
            total_price = int(self.order_table.item(row, 3).text().replace(',', ''))
            self.cursor.execute("SELECT id, stock FROM menu WHERE name = ?", (item_name,))
            result = self.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "خطا", f"آیتم {item_name} یافت نشد.")
                continue
            item_id, stock = result
            if stock < quantity:
                QMessageBox.warning(self, "خطا", f"موجودی {item_name} کافی نیست.")
                continue
            self.cursor.execute('''
                INSERT INTO orders (item_id, quantity, unit_price, total_price, order_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, quantity, unit_price, total_price, order_time))
            self.cursor.execute('UPDATE menu SET stock = stock - ? WHERE id = ?', (quantity, item_id))
        self.conn.commit()
        self.order_table.setRowCount(0)
        self.total_label.setText("جمع کل: 0 تومان")
        self.loadMenuItems()
        self.updateInventoryTable()
        QMessageBox.information(self, "موفق", "سفارش با موفقیت ثبت شد.")
        
    def cancelOrder(self):
        self.order_table.setRowCount(0)
        self.total_label.setText("جمع کل: 0 تومان")
        
    def addMenuItem(self):
        name = self.item_name.text().strip()
        price = self.item_price.value()
        stock = self.item_stock.value()
        if not name:
            QMessageBox.warning(self, "خطا", "لطفا نام آیتم را وارد کنید.")
            return
        self.cursor.execute("INSERT INTO menu (name, price, stock) VALUES (?, ?, ?)", (name, price, stock))
        self.conn.commit()
        self.item_name.clear()
        self.item_price.setValue(0)
        self.item_stock.setValue(0)
        self.loadMenuItems()
        self.updateInventoryTable()
        QMessageBox.information(self, "موفق", "آیتم جدید با موفقیت افزوده شد.")
        
    def updateInventoryTable(self):
        self.cursor.execute("SELECT id, name, stock, price FROM menu")
        menu_items = self.cursor.fetchall()
        self.inventory_table.setRowCount(len(menu_items))
        for row, item in enumerate(menu_items):
            item_id, name, stock, price = item
            self.inventory_table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.inventory_table.setItem(row, 1, QTableWidgetItem(name))
            self.inventory_table.setItem(row, 2, QTableWidgetItem(str(stock)))
            self.inventory_table.setItem(row, 3, QTableWidgetItem(f"{price:,.0f}"))
        self.inventory_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def updateDailySales(self):
        today = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT SUM(total_price) FROM orders WHERE DATE(order_time) = ?", (today,))
        daily_sales = self.cursor.fetchone()[0] or 0
        self.cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(order_time) = ?", (today,))
        order_count = self.cursor.fetchone()[0] or 0
        self.sales_label.setText(f"فروش امروز: {daily_sales:,.0f} تومان")
        self.orders_label.setText(f"تعداد سفارشات: {order_count}")
        profit = daily_sales * 0.4
        self.profit_label.setText(f"سود امروز: {profit:,.0f} تومان")
        self.cursor.execute('''
            SELECT o.order_time, m.name, o.quantity, o.unit_price, o.total_price
            FROM orders o JOIN menu m ON o.item_id = m.id
            WHERE DATE(o.order_time) = ? ORDER BY o.order_time DESC
        ''', (today,))
        sales_data = self.cursor.fetchall()
        self.sales_table.setRowCount(len(sales_data))
        for row, sale in enumerate(sales_data):
            order_time, name, quantity, unit_price, total_price = sale
            time_only = order_time.split(' ')[1] if ' ' in order_time else order_time
            self.sales_table.setItem(row, 0, QTableWidgetItem(time_only))
            self.sales_table.setItem(row, 1, QTableWidgetItem(name))
            self.sales_table.setItem(row, 2, QTableWidgetItem(str(quantity)))
            self.sales_table.setItem(row, 3, QTableWidgetItem(f"{unit_price:,.0f}"))
            self.sales_table.setItem(row, 4, QTableWidgetItem(f"{total_price:,.0f}"))
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
    def updateReports(self):
        self.updateDailySales()
        QMessageBox.information(self, "به‌روزرسانی", "گزارشات با موفقیت به‌روزرسانی شدند.")
        
    def closeEvent(self, event):
        self.conn.close()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("B Nazanin")
    font.setPointSize(10)
    app.setFont(font)
    window = RestaurantAccountingApp()
    window.show()
    sys.exit(app.exec_())