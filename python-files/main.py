import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QStackedLayout, QHBoxLayout, QTableWidget, QComboBox, QTableWidgetItem, QDialog, QFormLayout, QDialogButtonBox, QDoubleSpinBox, QSpinBox, QDateEdit, QGroupBox, QCompleter, QTabWidget, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QDate
import database # Import our database module
from datetime import datetime
import stock_management # Import our new stock_management module
import customer_management # Import our new customer_management module
import sales_module # Import our new sales_module module
import purchase_module # Import our new purchase_module module
import reports_module # Import our new reports_module module
import accounts_finance # Import our new accounts_finance module
import settings_module # Import our new settings_module module
import notifications_module # Import our new notifications_module module

class LoginScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Health King Pharma - Login")
        self.setGeometry(100, 100, 400, 300) # Smaller window for login

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter) # Center content

        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")

        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password) # Hide password

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def attempt_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        role = database.check_user_credentials(username, password)

        if role:
            QMessageBox.information(self, "Login Success", f"Welcome, {username}! Role: {role.capitalize()}")
            database.record_activity(username, "User logged in") # Record activity
            self.parent().show_main_dashboard(role) # Pass role to main app
            self.close()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")

class HealthKingPharmaApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Health King Pharma")
        self.setGeometry(100, 100, 800, 600)  # x, y, width, height

        self.current_user_role = None # To store the role of the logged-in user

        self.init_ui()

    def init_ui(self):
        self.stack_layout = QStackedLayout() # Use QStackedLayout for screen switching
        self.setLayout(self.stack_layout)

        self.login_screen = LoginScreen(self)
        self.stack_layout.addWidget(self.login_screen)

        self.dashboard_screen = DashboardScreen(self) # Initialize Dashboard
        self.stack_layout.addWidget(self.dashboard_screen)

        self.stock_management_screen = stock_management.StockManagementScreen(self)
        self.stack_layout.addWidget(self.stock_management_screen)
        self.stock_management_screen.hide()

        self.customer_management_screen = customer_management.CustomerManagementScreen(self)
        self.stack_layout.addWidget(self.customer_management_screen)
        self.customer_management_screen.hide()

        self.sales_module_screen = sales_module.SalesModuleScreen(self)
        self.stack_layout.addWidget(self.sales_module_screen)
        self.sales_module_screen.hide()

        self.purchase_module_screen = purchase_module.PurchaseModuleScreen(self)
        self.stack_layout.addWidget(self.purchase_module_screen)
        self.purchase_module_screen.hide()

        self.reports_module_screen = reports_module.ReportsModuleScreen(self)
        self.stack_layout.addWidget(self.reports_module_screen)
        self.reports_module_screen.hide()

        self.accounts_finance_screen = accounts_finance.AccountsFinanceScreen(self)
        self.stack_layout.addWidget(self.accounts_finance_screen)
        self.accounts_finance_screen.hide()

        self.settings_screen = settings_module.SettingsScreen(self) # Initialize Settings Screen
        self.stack_layout.addWidget(self.settings_screen)
        self.settings_screen.hide()

        self.notifications_screen = notifications_module.NotificationsScreen(self) # Initialize Notifications Screen
        self.stack_layout.addWidget(self.notifications_screen)
        self.notifications_screen.hide()

        # Connect logout signal from dashboard to show login screen
        self.dashboard_screen.logout_requested.connect(self.show_login_screen)

    def show_main_dashboard(self, role):
        self.current_user_role = role
        self.stack_layout.setCurrentWidget(self.dashboard_screen)
        self.dashboard_screen.show() # Ensure it's shown
        self.setWindowTitle(f"Health King Pharma - Logged in as {role.capitalize()}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_F1: # Dashboard
            self.show_main_dashboard(self.current_user_role)
        elif event.key() == Qt.Key.Key_F2: # Sales Module
            self.show_sales_module()
        elif event.key() == Qt.Key.Key_F3: # Purchase Module
            self.show_purchase_module()
        elif event.key() == Qt.Key.Key_F4: # Stock Management
            self.show_stock_management()
        elif event.key() == Qt.Key.Key_F5: # Reports Module
            self.show_reports_module()
        elif event.key() == Qt.Key.Key_F6: # Accounts & Finance
            self.show_accounts_finance()
        elif event.key() == Qt.Key.Key_F7: # Customer Management
            self.show_customer_management()
        elif event.key() == Qt.Key.Key_F8: # Settings
            self.show_settings()
        elif event.key() == Qt.Key.Key_F9: # Notifications
            self.show_notifications()
        # F10 (Backup & Restore) will be added when those modules are present.
        else:
            super().keyPressEvent(event)

    def show_stock_management(self):
        self.stack_layout.setCurrentWidget(self.stock_management_screen)
        self.stock_management_screen.show()
        self.setWindowTitle("Health King Pharma - Stock Management")
        self.stock_management_screen.load_products() # Refresh data when shown

    def show_customer_management(self):
        self.stack_layout.setCurrentWidget(self.customer_management_screen)
        self.customer_management_screen.show()
        self.setWindowTitle("Health King Pharma - Customer Management")
        self.customer_management_screen.load_customers() # Refresh data when shown

    def show_sales_module(self):
        self.stack_layout.setCurrentWidget(self.sales_module_screen)
        self.sales_module_screen.show()
        self.setWindowTitle("Health King Pharma - Sales Module")
        self.sales_module_screen.load_sales_invoices() # Refresh data when shown

    def show_purchase_module(self):
        self.stack_layout.setCurrentWidget(self.purchase_module_screen)
        self.purchase_module_screen.show()
        self.setWindowTitle("Health King Pharma - Purchase Module")
        self.purchase_module_screen.load_purchase_invoices() # Refresh data when shown

    def show_reports_module(self):
        self.stack_layout.setCurrentWidget(self.reports_module_screen)
        self.reports_module_screen.show()
        self.setWindowTitle("Health King Pharma - Reports Module")

    def show_accounts_finance(self):
        self.stack_layout.setCurrentWidget(self.accounts_finance_screen)
        self.accounts_finance_screen.show()
        self.setWindowTitle("Health King Pharma - Accounts & Finance")

    def show_settings(self):
        self.stack_layout.setCurrentWidget(self.settings_screen)
        self.settings_screen.show()
        self.setWindowTitle("Health King Pharma - Settings")
        self.settings_screen.update_ui_for_role()
        self.settings_screen.load_users()

    def show_notifications(self):
        self.stack_layout.setCurrentWidget(self.notifications_screen)
        self.notifications_screen.show()
        self.setWindowTitle("Health King Pharma - Notifications")
        self.notifications_screen.load_notifications()

    def show_login_screen(self):
        self.stack_layout.setCurrentWidget(self.login_screen)
        self.login_screen.username_input.clear() # Clear fields on logout
        self.login_screen.password_input.clear()
        self.login_screen.show()
        self.setWindowTitle("Health King Pharma - Login")

class DashboardScreen(QWidget):
    logout_requested = pyqtSignal() # Define a signal for logout

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent # Reference to the main app
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header with Branding
        header_label = QLabel("👑 Health King Pharma")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("font-size: 24px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header_label)

        # Quick View Cards/Widgets
        quick_view_layout = QHBoxLayout()
        self.stock_value_label = QLabel("Stock Value: $0.00")
        self.total_sales_label = QLabel("Total Sales: $0.00")
        self.total_purchases_label = QLabel("Total Purchases: $0.00")
        self.revenue_label = QLabel("Revenue: $0.00")
        self.expenses_label = QLabel("Expenses: $0.00")
        self.accounts_balance_label = QLabel("Accounts Balance: $0.00")

        quick_view_layout.addWidget(self.stock_value_label)
        quick_view_layout.addWidget(self.total_sales_label)
        quick_view_layout.addWidget(self.total_purchases_label)
        quick_view_layout.addWidget(self.revenue_label)
        quick_view_layout.addWidget(self.expenses_label)
        quick_view_layout.addWidget(self.accounts_balance_label)
        main_layout.addLayout(quick_view_layout)

        # Navigation Buttons (Placeholders)
        navigation_layout = QVBoxLayout()
        sales_button = QPushButton("Sales Module (F2)")
        sales_button.clicked.connect(self.parent_app.show_sales_module)
        purchase_button = QPushButton("Purchase Module (F3)")
        purchase_button.clicked.connect(self.parent_app.show_purchase_module) # Connect purchase button
        stock_button = QPushButton("Stock Management (F4)")
        reports_button = QPushButton("Reports Module (F5)")
        accounts_button = QPushButton("Accounts & Finance (F6)")
        customer_button = QPushButton("Customer Management (F7)")
        settings_button = QPushButton("Settings (F8)")
        backup_button = QPushButton("Backup & Restore (F9)") # F9 for Backup
        notifications_button = QPushButton("Notifications (F10)") # F10 for Notifications
        logout_button = QPushButton("Logout")

        stock_button.clicked.connect(self.parent_app.show_stock_management)
        customer_button.clicked.connect(self.parent_app.show_customer_management)
        reports_button.clicked.connect(self.parent_app.show_reports_module)
        accounts_button.clicked.connect(self.parent_app.show_accounts_finance)
        settings_button.clicked.connect(self.parent_app.show_settings)
        logout_button.clicked.connect(self.logout_requested.emit) # Emit signal for logout
        notifications_button.clicked.connect(self.parent_app.show_notifications) # Connect notifications button

        navigation_layout.addWidget(sales_button)
        navigation_layout.addWidget(purchase_button)
        navigation_layout.addWidget(stock_button)
        navigation_layout.addWidget(reports_button)
        navigation_layout.addWidget(accounts_button)
        navigation_layout.addWidget(customer_button)
        navigation_layout.addWidget(settings_button)
        navigation_layout.addWidget(backup_button)
        navigation_layout.addWidget(notifications_button)
        navigation_layout.addWidget(logout_button)
        main_layout.addLayout(navigation_layout)

        main_layout.addStretch(1) # Push content to top

        self.setLayout(main_layout)

        self.load_dashboard_data()

    def load_dashboard_data(self):
        stock_value = database.get_total_stock_value()
        total_sales = database.get_total_sales_amount()
        total_purchases = database.get_total_purchases_amount()
        total_revenue = database.get_total_revenue()
        total_expenses = database.get_total_overall_expenses()
        accounts_balance = database.get_accounts_balance()

        self.stock_value_label.setText(f"Stock Value: ${stock_value:.2f}")
        self.total_sales_label.setText(f"Total Sales: ${total_sales:.2f}")
        self.total_purchases_label.setText(f"Total Purchases: ${total_purchases:.2f}")
        self.revenue_label.setText(f"Revenue: ${total_revenue:.2f}")
        self.expenses_label.setText(f"Expenses: ${total_expenses:.2f}")
        self.accounts_balance_label.setText(f"Accounts Balance: ${accounts_balance:.2f}")

class StockManagementScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Dashboard")
        back_button.clicked.connect(lambda: self.parent_app.show_main_dashboard(self.parent_app.current_user_role)) # Pass current role back
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("Stock Management")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Search and Filter
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search products...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_products)
        filter_category_combo = QComboBox()
        filter_category_combo.addItem("All Categories")
        # Populate with actual categories from database later
        filter_category_combo.currentIndexChanged.connect(self.filter_products)

        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(QLabel("Filter by Category:"))
        search_layout.addWidget(filter_category_combo)
        main_layout.addLayout(search_layout)

        # Product Table (Placeholder)
        self.product_table = QTableWidget()
        self.product_table.setColumnCount(9) # Product Name, Category, Packing, Quantity, Price, Total Value, Min Stock, Max Stock, Expiry Status (calculated)
        self.product_table.setHorizontalHeaderLabels(["ID", "Product Name", "Category", "Packing", "Quantity", "Price", "Total Value", "Min Stock", "Max Stock"])
        self.product_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers) # Make table non-editable by default
        self.product_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) # Select entire rows
        main_layout.addWidget(self.product_table)

        # Action Buttons
        action_button_layout = QHBoxLayout()
        self.add_product_button = QPushButton("Add Product")
        self.edit_product_button = QPushButton("Edit Product")
        self.delete_product_button = QPushButton("Delete Product")
        self.manage_batches_button = QPushButton("Manage Batches")
        self.reorder_list_button = QPushButton("Generate Reorder List")

        self.add_product_button.clicked.connect(self.show_add_product_dialog)
        self.edit_product_button.clicked.connect(self.show_edit_product_dialog)
        self.delete_product_button.clicked.connect(self.delete_selected_product)
        self.manage_batches_button.clicked.connect(self.show_manage_batches_dialog)
        self.reorder_list_button.clicked.connect(self.show_reorder_list_dialog)

        action_button_layout.addWidget(self.add_product_button)
        action_button_layout.addWidget(self.edit_product_button)
        action_button_layout.addWidget(self.delete_product_button)
        action_button_layout.addWidget(self.manage_batches_button)
        action_button_layout.addWidget(self.reorder_list_button)
        main_layout.addLayout(action_button_layout)

        self.setLayout(main_layout)

        # Initial data load
        self.load_products()

    def load_products(self, products_data=None):
        if products_data is None:
            products = database.get_all_products()
        else:
            products = products_data

        self.product_table.setRowCount(len(products))
        for row_idx, product in enumerate(products):
            for col_idx, data in enumerate(product):
                item = QTableWidgetItem(str(data))
                if col_idx == 0: # Assuming the first column is the ID
                    item.setData(Qt.ItemDataRole.UserRole, product[0]) # Store product ID in UserRole
                self.product_table.setItem(row_idx, col_idx, item)
        self.product_table.resizeColumnsToContents()
        self.product_table.horizontalHeader().setStretchLastSection(True)

    def search_products(self):
        search_text = self.search_input.text().strip()
        if search_text:
            # In a real scenario, this would involve a database query
            # For now, let's filter the currently loaded products
            all_products = database.get_all_products()
            filtered_products = [p for p in all_products if search_text.lower() in p[1].lower()] # Search by product name
            self.load_products(filtered_products)
        else:
            self.load_products() # Reload all if search is empty

    def filter_products(self):
        # This will be implemented when categories are properly managed
        pass

    def show_add_product_dialog(self):
        dialog = AddProductDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text()
            category = dialog.category_input.text()
            packing = dialog.packing_input.text()
            price = dialog.price_input.value()
            min_stock = dialog.min_stock_input.value()
            max_stock = dialog.max_stock_input.value()

            product_id = database.add_product(name, category, packing, price, min_stock, max_stock)
            if product_id:
                QMessageBox.information(self, "Success", f"Product '{name}' added successfully.")
                database.record_activity(self.parent_app.current_user_role, f"Added product: {name}") # Log activity
                self.load_products() # Refresh the table
            else:
                QMessageBox.warning(self, "Error", f"Product '{name}' already exists or an error occurred.")

    def show_edit_product_dialog(self):
        selected_item = self.product_table.currentItem()
        if selected_item:
            product_id = selected_item.data(Qt.ItemDataRole.UserRole) # Assuming ID is stored in UserRole
            product_data = database.get_product_by_id(product_id)
            if product_data:
                dialog = EditProductDialog(product_data, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    name = dialog.name_input.text()
                    category = dialog.category_input.text()
                    packing = dialog.packing_input.text()
                    price = dialog.price_input.value()
                    min_stock = dialog.min_stock_input.value()
                    max_stock = dialog.max_stock_input.value()

                    success = database.update_product(product_id, name, category, packing, price, min_stock, max_stock)
                    if success:
                        QMessageBox.information(self, "Success", f"Product '{name}' updated successfully.")
                        database.record_activity(self.parent_app.current_user_role, f"Updated product: {name}") # Log activity
                        self.load_products() # Refresh the table
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to update product '{name}'.")
            else:
                QMessageBox.warning(self, "Error", "Product not found.")
        else:
            QMessageBox.warning(self, "Error", "Please select a product to edit.")

    def delete_selected_product(self):
        selected_item = self.product_table.currentItem()
        if selected_item:
            product_id = selected_item.data(Qt.ItemDataRole.UserRole)
            product_name = self.product_table.item(selected_item.row(), 1).text() # Get name from column 1 of selected row

            reply = QMessageBox.question(self, 'Confirm Delete',
                                         f"Are you sure you want to delete product '{product_name}'?\nThis action cannot be undone.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = database.delete_product(product_id)
                if success:
                    QMessageBox.information(self, "Success", f"Product '{product_name}' deleted successfully.")
                    database.record_activity(self.parent_app.current_user_role, f"Deleted product: {product_name}") # Log activity
                    self.load_products() # Refresh the table
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete product '{product_name}'.")
        else:
            QMessageBox.warning(self, "Error", "Please select a product to delete.")

    def show_reorder_list_dialog(self):
        dialog = ReorderListDialog(self)
        dialog.exec()

    def show_manage_batches_dialog(self):
        selected_item = self.product_table.currentItem()
        if selected_item:
            product_id = selected_item.data(Qt.ItemDataRole.UserRole)
            product_name = self.product_table.item(selected_item.row(), 1).text()
            dialog = ManageBatchesDialog(product_id, product_name, self) # Pass self for parent reference
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.load_products() # Refresh product list to show updated quantity
        else:
            QMessageBox.warning(self, "Error", "Please select a product to manage batches.")

class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Product")
        self.setGeometry(200, 200, 400, 300)

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., Paracetamol 500mg")
        layout.addRow("Product Name:", self.name_input)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("e.g., Analgesics")
        layout.addRow("Category:", self.category_input)

        self.packing_input = QLineEdit()
        self.packing_input.setPlaceholderText("e.g., Blister Pack of 10")
        layout.addRow("Packing:", self.packing_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 1000000.00)
        self.price_input.setPrefix("$")
        self.price_input.setDecimals(2)
        layout.addRow("Price per Unit:", self.price_input)

        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 1000000)
        layout.addRow("Minimum Stock:", self.min_stock_input)

        self.max_stock_input = QSpinBox()
        self.max_stock_input.setRange(0, 1000000)
        layout.addRow("Maximum Stock:", self.max_stock_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

class ReorderListDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Products to Reorder")
        self.setGeometry(250, 250, 600, 400)
        self.init_ui()
        self.load_reorder_list()

    def init_ui(self):
        main_layout = QVBoxLayout()

        self.reorder_table = QTableWidget()
        self.reorder_table.setColumnCount(6) # ID, Product Name, Category, Packing, Current Quantity, Min Stock
        self.reorder_table.setHorizontalHeaderLabels(["ID", "Product Name", "Category", "Packing", "Current Qty", "Min Stock"])
        self.reorder_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.reorder_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.reorder_table)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def load_reorder_list(self):
        reorder_products = database.get_products_for_reorder()
        self.reorder_table.setRowCount(len(reorder_products))
        for row_idx, product in enumerate(reorder_products):
            for col_idx, data in enumerate(product):
                item = QTableWidgetItem(str(data))
                self.reorder_table.setItem(row_idx, col_idx, item)
        self.reorder_table.resizeColumnsToContents()
        self.reorder_table.horizontalHeader().setStretchLastSection(True)

class EditProductDialog(QDialog):
    def __init__(self, product_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Product")
        self.setGeometry(200, 200, 400, 300)
        self.product_data = product_data # (id, name, category, packing, quantity, price, total_value, min_stock, max_stock)

        self.init_ui()
        self.load_product_data()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("Product Name:", self.name_input)

        self.category_input = QLineEdit()
        layout.addRow("Category:", self.category_input)

        self.packing_input = QLineEdit()
        layout.addRow("Packing:", self.packing_input)

        self.price_input = QDoubleSpinBox()
        self.price_input.setRange(0.01, 1000000.00)
        self.price_input.setPrefix("$")
        self.price_input.setDecimals(2)
        layout.addRow("Price per Unit:", self.price_input)

        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 1000000)
        layout.addRow("Minimum Stock:", self.min_stock_input)

        self.max_stock_input = QSpinBox()
        self.max_stock_input.setRange(0, 1000000)
        layout.addRow("Maximum Stock:", self.max_stock_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_product_data(self):
        # product_data: (id, name, category, packing, quantity, price, total_value, min_stock, max_stock)
        self.name_input.setText(self.product_data[1])
        self.category_input.setText(self.product_data[2])
        self.packing_input.setText(self.product_data[3])
        self.price_input.setValue(self.product_data[5])
        self.min_stock_input.setValue(self.product_data[7])
        self.max_stock_input.setValue(self.product_data[8])

class ManageBatchesDialog(QDialog):
    def __init__(self, product_id, product_name, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.product_name = product_name
        self.parent_screen = parent # Reference to StockManagementScreen
        self.setWindowTitle(f"Manage Batches for {product_name}")
        self.setGeometry(200, 200, 600, 400)

        self.init_ui()
        self.load_batches()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Batch Table
        self.batch_table = QTableWidget()
        self.batch_table.setColumnCount(4) # ID, Batch Number, Expiry Date, Quantity
        self.batch_table.setHorizontalHeaderLabels(["ID", "Batch Number", "Expiry Date", "Quantity"])
        self.batch_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.batch_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.batch_table)

        # Action Buttons for Batches
        action_layout = QHBoxLayout()
        self.add_batch_button = QPushButton("Add Batch")
        self.edit_batch_button = QPushButton("Edit Batch Quantity") # For simplicity, only quantity edit for batches
        self.delete_batch_button = QPushButton("Delete Batch")

        self.add_batch_button.clicked.connect(self.show_add_batch_dialog)
        self.edit_batch_button.clicked.connect(self.show_edit_batch_quantity_dialog)
        self.delete_batch_button.clicked.connect(self.delete_selected_batch)

        action_layout.addWidget(self.add_batch_button)
        action_layout.addWidget(self.edit_batch_button)
        action_layout.addWidget(self.delete_batch_button)
        main_layout.addLayout(action_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.clicked.connect(self.accept) # Use accept to close the dialog gracefully
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def load_batches(self):
        batches = database.get_batches_for_product(self.product_id)
        self.batch_table.setRowCount(len(batches))
        for row_idx, batch in enumerate(batches):
            for col_idx, data in enumerate(batch):
                item = QTableWidgetItem(str(data))
                if col_idx == 0: # Assuming first column is ID
                    item.setData(Qt.ItemDataRole.UserRole, batch[0]) # Store batch ID
                self.batch_table.setItem(row_idx, col_idx, item)
        self.batch_table.resizeColumnsToContents()
        self.batch_table.horizontalHeader().setStretchLastSection(True)

    def show_add_batch_dialog(self):
        dialog = AddBatchDialog(self.product_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_batches() # Refresh batches after adding
            self.parent_screen.load_products() # Refresh main product list quantity
            database.record_activity(self.parent_screen.parent_app.current_user_role, f"Added batch for product: {self.product_name}") # Log activity

    def show_edit_batch_quantity_dialog(self):
        selected_item = self.batch_table.currentItem()
        if selected_item:
            batch_id = selected_item.data(Qt.ItemDataRole.UserRole)
            # Need to get all batch data by ID from database.py for EditBatchQuantityDialog
            conn = database.connect_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id, batch_number, expiry_date, quantity FROM batches WHERE id = ?", (batch_id,))
            batch_data = cursor.fetchone()
            conn.close()
            
            if batch_data:
                dialog = EditBatchQuantityDialog(batch_data, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_quantity = dialog.quantity_input.value()
                    success = database.update_batch_quantity(batch_id, new_quantity)
                    if success:
                        QMessageBox.information(self, "Success", "Batch quantity updated.")
                        database.record_activity(self.parent_screen.parent_app.current_user_role, f"Updated quantity for batch {batch_data[1]} of product: {self.product_name}") # Log activity
                        self.load_batches() # Refresh batches
                        self.parent_screen.load_products() # Refresh main product list quantity
                    else:
                        QMessageBox.warning(self, "Error", "Failed to update batch quantity.")
            else:
                QMessageBox.warning(self, "Error", "Batch not found.")
        else:
            QMessageBox.warning(self, "Error", "Please select a batch to edit.")

    def delete_selected_batch(self):
        selected_item = self.batch_table.currentItem()
        if selected_item:
            batch_id = selected_item.data(Qt.ItemDataRole.UserRole)
            batch_number = self.batch_table.item(selected_item.row(), 1).text() # Get batch number from column 1

            reply = QMessageBox.question(self, 'Confirm Delete', 
                                         f"Are you sure you want to delete batch '{batch_number}'?\nThis will also adjust product quantity.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = database.delete_batch(batch_id)
                if success:
                    QMessageBox.information(self, "Success", f"Batch '{batch_number}' deleted successfully.")
                    database.record_activity(self.parent_screen.parent_app.current_user_role, f"Deleted batch {batch_number} of product: {self.product_name}") # Log activity
                    self.load_batches() # Refresh batches
                    self.parent_screen.load_products() # Refresh main product list quantity
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete batch '{batch_number}'.")
        else:
            QMessageBox.warning(self, "Error", "Please select a batch to delete.")

class AddBatchDialog(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.product_id = product_id
        self.setWindowTitle("Add New Batch")
        self.setGeometry(200, 200, 350, 250)

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.batch_number_input = QLineEdit()
        layout.addRow("Batch Number:", self.batch_number_input)

        self.expiry_date_input = QDateEdit(calendarPopup=True)
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_date_input.setDate(QDate.currentDate())
        layout.addRow("Expiry Date:", self.expiry_date_input)

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000000)
        layout.addRow("Quantity:", self.quantity_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_batch_add)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept_batch_add(self):
        batch_number = self.batch_number_input.text()
        expiry_date = self.expiry_date_input.date().toString("yyyy-MM-dd")
        quantity = self.quantity_input.value()

        if not batch_number or not quantity:
            QMessageBox.warning(self, "Input Error", "Batch Number and Quantity cannot be empty.")
            return

        batch_id = database.add_batch(self.product_id, batch_number, expiry_date, quantity)
        if batch_id:
            QMessageBox.information(self, "Success", "Batch added successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to add batch. Batch number might already exist for this product.")

class EditBatchQuantityDialog(QDialog):
    def __init__(self, batch_data, parent=None):
        super().__init__(parent)
        self.batch_data = batch_data # (id, batch_number, expiry_date, quantity)
        self.setWindowTitle(f"Edit Batch {batch_data[1]}")
        self.setGeometry(200, 200, 300, 150)

        self.init_ui()
        self.load_batch_data()

    def init_ui(self):
        layout = QFormLayout()

        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(0, 1000000) # Allow 0 for depletion
        layout.addRow("New Quantity:", self.quantity_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_batch_data(self):
        self.quantity_input.setValue(self.batch_data[3])

class CustomerManagementScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Dashboard")
        back_button.clicked.connect(lambda: self.parent_app.show_main_dashboard(self.parent_app.current_user_role))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("Customer Management")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Search and Filter
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search customers...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_customers)
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Customer Table
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4) # ID, Name, Contact Info, Credit Limit
        self.customer_table.setHorizontalHeaderLabels(["ID", "Name", "Contact Info", "Credit Limit"])
        self.customer_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.customer_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.customer_table)

        # Action Buttons
        action_button_layout = QHBoxLayout()
        self.add_customer_button = QPushButton("Add Customer")
        self.edit_customer_button = QPushButton("Edit Customer")
        self.delete_customer_button = QPushButton("Delete Customer")

        self.add_customer_button.clicked.connect(self.show_add_customer_dialog)
        self.edit_customer_button.clicked.connect(self.show_edit_customer_dialog)
        self.delete_customer_button.clicked.connect(self.delete_selected_customer)

        action_button_layout.addWidget(self.add_customer_button)
        action_button_layout.addWidget(self.edit_customer_button)
        action_button_layout.addWidget(self.delete_customer_button)
        main_layout.addLayout(action_button_layout)

        self.setLayout(main_layout)
        self.load_customers()

    def load_customers(self, customers_data=None):
        if customers_data is None:
            customers = database.get_all_customers()
        else:
            customers = customers_data

        self.customer_table.setRowCount(len(customers))
        for row_idx, customer in enumerate(customers):
            for col_idx, data in enumerate(customer):
                item = QTableWidgetItem(str(data))
                if col_idx == 0: # Assuming first column is ID
                    item.setData(Qt.ItemDataRole.UserRole, customer[0]) # Store customer ID
                self.customer_table.setItem(row_idx, col_idx, item)
        self.customer_table.resizeColumnsToContents()
        self.customer_table.horizontalHeader().setStretchLastSection(True)

    def search_customers(self):
        search_text = self.search_input.text().strip()
        if search_text:
            all_customers = database.get_all_customers()
            filtered_customers = [c for c in all_customers if search_text.lower() in c[1].lower()] # Search by name
            self.load_customers(filtered_customers)
        else:
            self.load_customers()

    def show_add_customer_dialog(self):
        dialog = AddCustomerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.name_input.text()
            contact_info = dialog.contact_input.text()
            credit_limit = dialog.credit_limit_input.value()
            
            customer_id = database.add_customer(name, contact_info, credit_limit)
            if customer_id:
                QMessageBox.information(self, "Success", f"Customer '{name}' added successfully.")
                self.load_customers() # Refresh table
            else:
                QMessageBox.warning(self, "Error", f"Customer '{name}' already exists or an error occurred.")

    def show_edit_customer_dialog(self):
        selected_item = self.customer_table.currentItem()
        if selected_item:
            customer_id = selected_item.data(Qt.ItemDataRole.UserRole)
            customer_data = database.get_customer_by_id(customer_id)
            if customer_data:
                dialog = EditCustomerDialog(customer_data, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    name = dialog.name_input.text()
                    contact_info = dialog.contact_input.text()
                    credit_limit = dialog.credit_limit_input.value()
                    
                    success = database.update_customer(customer_id, name, contact_info, credit_limit)
                    if success:
                        QMessageBox.information(self, "Success", f"Customer '{name}' updated successfully.")
                        self.load_customers() # Refresh table
                    else:
                        QMessageBox.warning(self, "Error", f"Failed to update customer '{name}'.")
            else:
                QMessageBox.warning(self, "Error", "Customer not found.")
        else:
            QMessageBox.warning(self, "Error", "Please select a customer to edit.")

    def delete_selected_customer(self):
        selected_item = self.customer_table.currentItem()
        if selected_item:
            customer_id = selected_item.data(Qt.ItemDataRole.UserRole)
            customer_name = self.customer_table.item(selected_item.row(), 1).text()

            reply = QMessageBox.question(self, 'Confirm Delete', 
                                         f"Are you sure you want to delete customer '{customer_name}'?\nThis action cannot be undone.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = database.delete_customer(customer_id)
                if success:
                    QMessageBox.information(self, "Success", f"Customer '{customer_name}' deleted successfully.")
                    database.record_activity(self.parent_app.current_user_role, f"Deleted customer: {customer_name}") # Log activity
                    self.load_customers() # Refresh table
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete customer '{customer_name}'.")
        else:
            QMessageBox.warning(self, "Error", "Please select a customer to delete.")

class AddCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Customer")
        self.setGeometry(200, 200, 350, 250)

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("Customer Name:", self.name_input)

        self.contact_input = QLineEdit()
        layout.addRow("Contact Info:", self.contact_input)

        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setRange(0.00, 1000000.00)
        self.credit_limit_input.setPrefix("$")
        self.credit_limit_input.setDecimals(2)
        layout.addRow("Credit Limit:", self.credit_limit_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

class EditCustomerDialog(QDialog):
    def __init__(self, customer_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Customer")
        self.setGeometry(200, 200, 350, 250)
        self.customer_data = customer_data # (id, name, contact_info, credit_limit)

        self.init_ui()
        self.load_customer_data()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("Customer Name:", self.name_input)

        self.contact_input = QLineEdit()
        layout.addRow("Contact Info:", self.contact_input)

        self.credit_limit_input = QDoubleSpinBox()
        self.credit_limit_input.setRange(0.00, 1000000.00)
        self.credit_limit_input.setPrefix("$")
        self.credit_limit_input.setDecimals(2)
        layout.addRow("Credit Limit:", self.credit_limit_input)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_customer_data(self):
        self.name_input.setText(self.customer_data[1])
        self.contact_input.setText(self.customer_data[2])
        self.credit_limit_input.setValue(self.customer_data[3])

    def accept(self):
        username = self.username_input.text()
        role = self.role_combo.currentData()
        status = self.status_combo.currentData()

        if not username or not role or not status:
            QMessageBox.warning(self, "Input Error", "Username, Role, and Status cannot be empty.")
            return

        success = database.update_user(self.user_data[0], username, role, status)
        if success:
            QMessageBox.information(self, "Success", f"User '{username}' updated successfully.")
            database.record_activity(self.parent().parent_app.current_user_role, f"Updated user: {username}") # Log activity
            super().accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to update user '{username}'.")

class SalesModuleScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Dashboard")
        back_button.clicked.connect(lambda: self.parent_app.show_main_dashboard(self.parent_app.current_user_role))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("Sales Module")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Search
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search invoices by number or customer...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_invoices) # Connect search function
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Sales Invoices Table
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(7) # ID, Invoice Number, Date, Customer, Total Amount, Amount Paid, Status
        self.sales_table.setHorizontalHeaderLabels(["ID", "Invoice No.", "Date", "Customer", "Total Amt.", "Paid Amt.", "Status"])
        self.sales_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.sales_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.sales_table)

        # Action Buttons
        action_button_layout = QHBoxLayout()
        self.create_invoice_button = QPushButton("Create Sales Invoice")
        self.create_invoice_button.clicked.connect(self.show_create_sales_invoice_dialog)
        action_button_layout.addWidget(self.create_invoice_button)
        # Placeholder for Edit/View Invoice, Process Return, etc.
        action_button_layout.addWidget(QPushButton("View/Edit Invoice"))
        action_button_layout.addWidget(QPushButton("Process Return"))
        main_layout.addLayout(action_button_layout)

        self.setLayout(main_layout)
        self.load_sales_invoices()

    def load_sales_invoices(self, invoices_data=None):
        if invoices_data is None:
            invoices = database.get_all_sales_invoices()
        else:
            invoices = invoices_data

        self.sales_table.setRowCount(len(invoices))
        for row_idx, invoice in enumerate(invoices):
            for col_idx, data in enumerate(invoice):
                item = QTableWidgetItem(str(data))
                if col_idx == 0: # Assuming first column is ID
                    item.setData(Qt.ItemDataRole.UserRole, invoice[0]) # Store invoice ID
                self.sales_table.setItem(row_idx, col_idx, item)
        self.sales_table.resizeColumnsToContents()
        self.sales_table.horizontalHeader().setStretchLastSection(True)

    def search_invoices(self):
        search_text = self.search_input.text().strip()
        if search_text:
            all_invoices = database.get_all_sales_invoices()
            filtered_invoices = [inv for inv in all_invoices if search_text.lower() in str(inv[1]).lower() or (inv[3] and search_text.lower() in inv[3].lower())] # Search by invoice number or customer name
            self.load_sales_invoices(filtered_invoices)
        else:
            self.load_sales_invoices()

    def show_create_sales_invoice_dialog(self):
        # This dialog will be complex, involving product selection and quantity
        # QMessageBox.information(self, "Coming Soon", "Create Sales Invoice dialog will be implemented next!") # Removed old message
        dialog = CreateSalesInvoiceDialog(self.parent_app.current_user_role, self) # Pass current_user_role
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Logic to save invoice will go here after dialog accepts
            self.load_sales_invoices() # Refresh sales table

class CreateSalesInvoiceDialog(QDialog):
    def __init__(self, current_user_role, parent=None):
        super().__init__(parent)
        self.current_user_role = current_user_role # Store current user role
        self.setWindowTitle("Create New Sales Invoice")
        self.setGeometry(150, 150, 900, 700)

        self.selected_products_for_invoice = [] # List to hold (product_id, name, price, quantity, discount_per_item, batch_id)
        self.all_products = database.get_all_products() # Cache products for search
        self.all_customers = database.get_all_customers() # Cache customers for selection

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Invoice Header Details
        header_form_layout = QFormLayout()
        
        self.invoice_number_input = QLineEdit()
        self.invoice_number_input.setPlaceholderText("Auto-generated or enter manually")
        self.invoice_number_input.setText(self.generate_invoice_number())
        self.invoice_number_input.setReadOnly(True) # Make it read-only for now
        header_form_layout.addRow("Invoice Number:", self.invoice_number_input)

        self.invoice_date_edit = QDateEdit(calendarPopup=True)
        self.invoice_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.invoice_date_edit.setDate(QDate.currentDate())
        header_form_layout.addRow("Invoice Date:", self.invoice_date_edit)

        self.customer_combo = QComboBox()
        self.customer_combo.addItem("-- Select Customer --", None)
        for customer_id, name, _, _ in self.all_customers:
            self.customer_combo.addItem(name, customer_id)
        header_form_layout.addRow("Customer:", self.customer_combo)

        main_layout.addLayout(header_form_layout)
        main_layout.addSpacing(15)

        # Product Selection Area
        product_selection_group = QGroupBox("Add Products")
        product_layout = QVBoxLayout()
        
        product_input_layout = QHBoxLayout()
        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Search product (e.g., typing 'Ch' shows 'ChatGPT')")
        self.product_search_input.textChanged.connect(self.update_product_suggestions)
        self.product_search_completer = QCompleter([p[1] for p in self.all_products]) # Product names for autocompletion
        self.product_search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.product_search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.product_search_input.setCompleter(self.product_search_completer)
        
        self.product_quantity_input = QSpinBox()
        self.product_quantity_input.setRange(1, 1000000) # Max quantity
        self.product_quantity_input.setValue(1)

        self.product_discount_input = QDoubleSpinBox()
        self.product_discount_input.setRange(0.00, 100.00)
        self.product_discount_input.setSuffix("%")
        self.product_discount_input.setDecimals(2)

        self.add_product_to_invoice_button = QPushButton("Add to Invoice")
        self.add_product_to_invoice_button.clicked.connect(self.add_product_to_invoice)

        product_input_layout.addWidget(QLabel("Product:"))
        product_input_layout.addWidget(self.product_search_input)
        product_input_layout.addWidget(QLabel("Quantity:"))
        product_input_layout.addWidget(self.product_quantity_input)
        product_input_layout.addWidget(QLabel("Discount (%):"))
        product_input_layout.addWidget(self.product_discount_input)
        product_input_layout.addWidget(self.add_product_to_invoice_button)
        product_layout.addLayout(product_input_layout)
        
        product_selection_group.setLayout(product_layout)
        main_layout.addWidget(product_selection_group)
        main_layout.addSpacing(15)

        # Invoice Items Table
        self.invoice_items_table = QTableWidget()
        self.invoice_items_table.setColumnCount(6) # Product Name, Batch (if any), Expiry, Quantity, Unit Price, Discount (%), Subtotal
        self.invoice_items_table.setHorizontalHeaderLabels(["Product Name", "Batch No.", "Expiry Date", "Quantity", "Unit Price", "Discount (%)", "Subtotal"])
        self.invoice_items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.invoice_items_table.itemChanged.connect(self.calculate_total) # Recalculate if quantity/discount changed later
        main_layout.addWidget(self.invoice_items_table)

        # Total Amount and Discount
        total_layout = QHBoxLayout()
        total_layout.addStretch(1)
        self.total_label = QLabel("Total Amount: $0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        total_layout.addWidget(self.total_label)
        main_layout.addLayout(total_layout)
        main_layout.addSpacing(10)

        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_invoice)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def generate_invoice_number(self):
        # Simple timestamp-based invoice number for now
        return datetime.now().strftime("INV-%Y%m%d-%H%M%S")

    def update_product_suggestions(self, text):
        # This function is more for connecting a custom model to QCompleter
        # The QCompleter set on the QLineEdit already handles basic suggestions.
        pass

    def add_product_to_invoice(self):
        product_name = self.product_search_input.text().strip()
        quantity = self.product_quantity_input.value()
        discount_percentage = self.product_discount_input.value()

        product_data = None
        for p in self.all_products:
            if p[1].lower() == product_name.lower(): # Case-insensitive match
                product_data = p # (id, name, category, packing, quantity, price, total_value, min_stock, max_stock)
                break

        if not product_data:
            QMessageBox.warning(self, "Input Error", "Product not found. Please select a valid product.")
            return

        product_id = product_data[0]
        available_stock = product_data[4]
        unit_price = product_data[5]

        if quantity <= 0:
            QMessageBox.warning(self, "Input Error", "Quantity must be greater than 0.")
            return

        if quantity > available_stock:
            QMessageBox.warning(self, "Stock Error", f"Only {available_stock} units of {product_name} available in stock.")
            return
        
        # Get batches to deduct from (prioritize non-expiring or earliest expiry)
        batches = database.get_batches_for_product(product_id)
        if not batches:
            QMessageBox.warning(self, "Stock Error", f"No batches found for {product_name}. Cannot add to invoice.")
            return
        
        # Sort batches by expiry date (earliest first, non-expiring last)
        batches_sorted = sorted(batches, key=lambda b: (b[2] is None, b[2])) # b[2] is expiry_date

        remaining_qty_to_deduct = quantity
        deducted_batches = [] # List of (batch_id, deducted_qty)

        for batch_id, batch_num, expiry_date, batch_qty in batches_sorted:
            if remaining_qty_to_deduct <= 0: break
            
            qty_from_this_batch = min(remaining_qty_to_deduct, batch_qty)
            deducted_batches.append((batch_id, qty_from_this_batch))
            remaining_qty_to_deduct -= qty_from_this_batch

        if remaining_qty_to_deduct > 0:
            QMessageBox.warning(self, "Stock Error", f"Insufficient stock across all batches for {product_name}. Needed {quantity}, could only allocate {quantity - remaining_qty_to_deduct}.")
            return

        # Add to selected_products_for_invoice list (including batch info)
        # For simplicity, we'll store product_id, name, price, quantity, discount, and batch_ids used.
        # A more robust solution might break it down per batch in the invoice items table.
        # For now, we will add one entry per product, and handle stock deduction per batch during save.

        # Check if product already in list, if so, update quantity
        found = False
        for item in self.selected_products_for_invoice:
            if item['product_id'] == product_id:
                item['quantity'] += quantity
                # Merge deducted_batches here if needed (complex for this pass)
                found = True
                break
        
        if not found:
            self.selected_products_for_invoice.append({
                'product_id': product_id,
                'name': product_name,
                'unit_price': unit_price,
                'quantity': quantity,
                'discount_percentage': discount_percentage,
                'deducted_batches': deducted_batches # Store which batches this quantity came from
            })

        self.update_invoice_items_table()
        self.calculate_total()
        self.product_search_input.clear()
        self.product_quantity_input.setValue(1)
        self.product_discount_input.setValue(0.0)

    def update_invoice_items_table(self):
        self.invoice_items_table.setRowCount(len(self.selected_products_for_invoice))
        total_cols = 7
        for row_idx, item in enumerate(self.selected_products_for_invoice):
            subtotal = item['quantity'] * item['unit_price'] * (1 - item['discount_percentage'] / 100)
            
            # Assuming simplified display for now, full batch breakdown might be too complex for this table
            # Product Name, Batch No., Expiry Date, Quantity, Unit Price, Discount (%), Subtotal
            self.invoice_items_table.setItem(row_idx, 0, QTableWidgetItem(item['name']))
            self.invoice_items_table.setItem(row_idx, 1, QTableWidgetItem("N/A")) # Batch info placeholder
            self.invoice_items_table.setItem(row_idx, 2, QTableWidgetItem("N/A")) # Expiry info placeholder
            self.invoice_items_table.setItem(row_idx, 3, QTableWidgetItem(str(item['quantity'])))
            self.invoice_items_table.setItem(row_idx, 4, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            self.invoice_items_table.setItem(row_idx, 5, QTableWidgetItem(f"{item['discount_percentage']:.2f}"))
            self.invoice_items_table.setItem(row_idx, 6, QTableWidgetItem(f"{subtotal:.2f}"))
        self.invoice_items_table.resizeColumnsToContents()
        self.invoice_items_table.horizontalHeader().setStretchLastSection(True)

    def calculate_total(self):
        total_amount = 0.0
        for item in self.selected_products_for_invoice:
            total_amount += item['quantity'] * item['unit_price'] * (1 - item['discount_percentage'] / 100)
        self.total_label.setText(f"Total Amount: ${total_amount:.2f}")

    def save_invoice(self):
        invoice_number = self.invoice_number_input.text()
        invoice_date = self.invoice_date_edit.date().toString("yyyy-MM-dd")
        customer_id = self.customer_combo.currentData() # Get customer ID
        
        if customer_id is None:
            QMessageBox.warning(self, "Input Error", "Please select a customer.")
            return
        
        if not self.selected_products_for_invoice:
            QMessageBox.warning(self, "Input Error", "Please add products to the invoice.")
            return
        
        total_amount_calculated = 0.0
        for item in self.selected_products_for_invoice:
            total_amount_calculated += item['quantity'] * item['unit_price'] * (1 - item['discount_percentage'] / 100)
        
        invoice_id = database.create_sales_invoice(invoice_number, invoice_date, customer_id, 0.0, total_amount_calculated) # Discount per invoice is 0 for now, handled per item
        
        if invoice_id:
            success_items = True
            for item_data in self.selected_products_for_invoice:
                product_id = item_data['product_id']
                quantity = item_data['quantity']
                unit_price = item_data['unit_price']
                discount_per_item = item_data['discount_percentage']
                deducted_batches = item_data['deducted_batches']

                # Deduct from batches and add to sales_items
                for batch_id, qty_from_this_batch in deducted_batches:
                    # Note: add_sales_item already deducts from product and batch
                    if not database.add_sales_item(invoice_id, product_id, qty_from_this_batch, unit_price, discount_per_item, batch_id):
                        success_items = False
                        break
                if not success_items: break
            
            if success_items:
                # QMessageBox.information(self, "Success", f"Invoice {invoice_number} created successfully.")
                database.record_activity(self.current_user_role, f"Created sales invoice: {invoice_number}") # Log activity
                self.accept() # Accept and close dialog
            else:
                QMessageBox.warning(self, "Error", "Invoice created, but some items failed to be added/stock deducted. Please check manually.")
                # Rollback or further handling might be needed here in a real app
        else:
            QMessageBox.warning(self, "Error", "Failed to create invoice.")
            return # Do not accept/close dialog on failure

class PurchaseModuleScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Dashboard")
        back_button.clicked.connect(lambda: self.parent_app.show_main_dashboard(self.parent_app.current_user_role))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("Purchase Module")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Search
        search_layout = QHBoxLayout()
        search_input = QLineEdit()
        search_input.setPlaceholderText("Search purchase invoices by number or supplier...")
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_invoices) # Connect search function
        search_layout.addWidget(search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Purchase Invoices Table
        self.purchase_table = QTableWidget()
        self.purchase_table.setColumnCount(5) # ID, Invoice Number, Date, Supplier, Total Amount
        self.purchase_table.setHorizontalHeaderLabels(["ID", "Invoice No.", "Date", "Supplier", "Total Amt."])
        self.purchase_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.purchase_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.purchase_table)

        # Action Buttons
        action_button_layout = QHBoxLayout()
        self.create_purchase_invoice_button = QPushButton("Create Purchase Invoice")
        self.create_purchase_invoice_button.clicked.connect(self.show_create_purchase_invoice_dialog)
        action_button_layout.addWidget(self.create_purchase_invoice_button)
        # Placeholder for View/Edit Invoice
        action_button_layout.addWidget(QPushButton("View/Edit Invoice"))
        main_layout.addLayout(action_button_layout)

        self.setLayout(main_layout)
        self.load_purchase_invoices()

    def load_purchase_invoices(self, invoices_data=None):
        if invoices_data is None:
            invoices = database.get_all_purchase_invoices()
        else:
            invoices = invoices_data

        self.purchase_table.setRowCount(len(invoices))
        for row_idx, invoice in enumerate(invoices):
            for col_idx, data in enumerate(invoice):
                item = QTableWidgetItem(str(data))
                if col_idx == 0: # Assuming first column is ID
                    item.setData(Qt.ItemDataRole.UserRole, invoice[0]) # Store invoice ID
                self.purchase_table.setItem(row_idx, col_idx, item)
        self.purchase_table.resizeColumnsToContents()
        self.purchase_table.horizontalHeader().setStretchLastSection(True)

    def search_invoices(self):
        search_text = self.search_input.text().strip()
        if search_text:
            all_invoices = database.get_all_purchase_invoices()
            filtered_invoices = [inv for inv in all_invoices if search_text.lower() in str(inv[1]).lower() or (inv[3] and search_text.lower() in inv[3].lower())] # Search by invoice number or supplier name
            self.load_purchase_invoices(filtered_invoices)
        else:
            self.load_purchase_invoices()

    def show_create_purchase_invoice_dialog(self):
        # This dialog will also be complex
        # QMessageBox.information(self, "Coming Soon", "Create Purchase Invoice dialog will be implemented next!") # Removed old message
        dialog = CreatePurchaseInvoiceDialog(self.parent_app.current_user_role, self) # Pass current_user_role
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Logic to save invoice will go here after dialog accepts
            self.load_purchase_invoices() # Refresh purchase table

class CreatePurchaseInvoiceDialog(QDialog):
    def __init__(self, current_user_role, parent=None):
        super().__init__(parent)
        self.current_user_role = current_user_role # Store current user role
        self.setWindowTitle("Create New Purchase Invoice")
        self.setGeometry(150, 150, 900, 700)

        self.selected_products_for_invoice = [] # List to hold (product_id, name, quantity, unit_price, batch_number, expiry_date)
        self.all_products = database.get_all_products() # Cache products for search

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Invoice Header Details
        header_form_layout = QFormLayout()
        
        self.invoice_number_input = QLineEdit()
        self.invoice_number_input.setPlaceholderText("Auto-generated or enter manually")
        self.invoice_number_input.setText(self.generate_invoice_number())
        self.invoice_number_input.setReadOnly(True) # Make it read-only for now
        header_form_layout.addRow("Invoice Number:", self.invoice_number_input)

        self.invoice_date_edit = QDateEdit(calendarPopup=True)
        self.invoice_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.invoice_date_edit.setDate(QDate.currentDate())
        header_form_layout.addRow("Invoice Date:", self.invoice_date_edit)

        self.supplier_name_input = QLineEdit()
        self.supplier_name_input.setPlaceholderText("Enter supplier name")
        header_form_layout.addRow("Supplier Name:", self.supplier_name_input)

        main_layout.addLayout(header_form_layout)
        main_layout.addSpacing(15)

        # Product Selection Area
        product_selection_group = QGroupBox("Add Products")
        product_layout = QVBoxLayout()
        
        product_input_layout = QHBoxLayout()
        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Search product (e.g., typing 'Ch' shows 'ChatGPT')")
        self.product_search_input.textChanged.connect(self.update_product_suggestions)
        self.product_search_completer = QCompleter([p[1] for p in self.all_products]) # Product names for autocompletion
        self.product_search_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.product_search_completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.product_search_input.setCompleter(self.product_search_completer)
        
        self.product_quantity_input = QSpinBox()
        self.product_quantity_input.setRange(1, 1000000)
        self.product_quantity_input.setValue(1)

        self.product_unit_price_input = QDoubleSpinBox()
        self.product_unit_price_input.setRange(0.01, 1000000.00)
        self.product_unit_price_input.setPrefix("$")
        self.product_unit_price_input.setDecimals(2)

        self.batch_number_input = QLineEdit()
        self.batch_number_input.setPlaceholderText("Optional Batch No.")

        self.expiry_date_input = QDateEdit(calendarPopup=True)
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setDisplayFormat("yyyy-MM-dd")
        self.expiry_date_input.setDate(QDate.currentDate())
        self.expiry_date_input.setToolTip("Leave blank for no expiry")
        
        self.add_product_to_invoice_button = QPushButton("Add to Invoice")
        self.add_product_to_invoice_button.clicked.connect(self.add_product_to_invoice)

        product_input_layout.addWidget(QLabel("Product:"))
        product_input_layout.addWidget(self.product_search_input)
        product_input_layout.addWidget(QLabel("Quantity:"))
        product_input_layout.addWidget(self.product_quantity_input)
        product_input_layout.addWidget(QLabel("Unit Price:"))
        product_input_layout.addWidget(self.product_unit_price_input)
        product_input_layout.addWidget(QLabel("Batch No.:"))
        product_input_layout.addWidget(self.batch_number_input)
        product_input_layout.addWidget(QLabel("Expiry Date:"))
        product_input_layout.addWidget(self.expiry_date_input)
        product_input_layout.addWidget(self.add_product_to_invoice_button)
        product_layout.addLayout(product_input_layout)
        
        product_selection_group.setLayout(product_layout)
        main_layout.addWidget(product_selection_group)
        main_layout.addSpacing(15)

        # Invoice Items Table
        self.invoice_items_table = QTableWidget()
        self.invoice_items_table.setColumnCount(7) # Product Name, Batch, Expiry, Quantity, Unit Price, Subtotal
        self.invoice_items_table.setHorizontalHeaderLabels(["Product Name", "Batch No.", "Expiry Date", "Quantity", "Unit Price", "Subtotal"])
        self.invoice_items_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.invoice_items_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.invoice_items_table.itemChanged.connect(self.calculate_total) # Recalculate if quantity/price changed later
        main_layout.addWidget(self.invoice_items_table)

        # Total Amount
        total_layout = QHBoxLayout()
        total_layout.addStretch(1)
        self.total_label = QLabel("Total Amount: $0.00")
        self.total_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        total_layout.addWidget(self.total_label)
        main_layout.addLayout(total_layout)
        main_layout.addSpacing(10)

        # Dialog Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.save_invoice)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

        self.setLayout(main_layout)

    def generate_invoice_number(self):
        return datetime.now().strftime("PUR-%Y%m%d-%H%M%S")

    def update_product_suggestions(self, text):
        pass # Handled by QCompleter

    def add_product_to_invoice(self):
        product_name = self.product_search_input.text().strip()
        quantity = self.product_quantity_input.value()
        unit_price = self.product_unit_price_input.value()
        batch_number = self.batch_number_input.text().strip()
        expiry_date = self.expiry_date_input.date().toString("yyyy-MM-dd") if self.expiry_date_input.date().isValid() else None

        product_data = None
        for p in self.all_products:
            if p[1].lower() == product_name.lower():
                product_data = p
                break

        if not product_data:
            QMessageBox.warning(self, "Input Error", "Product not found. Please select a valid product.")
            return

        product_id = product_data[0]

        if quantity <= 0:
            QMessageBox.warning(self, "Input Error", "Quantity must be greater than 0.")
            return
        if unit_price <= 0:
            QMessageBox.warning(self, "Input Error", "Unit Price must be greater than 0.")
            return

        # Add to selected_products_for_invoice list
        self.selected_products_for_invoice.append({
            'product_id': product_id,
            'name': product_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'batch_number': batch_number if batch_number else None,
            'expiry_date': expiry_date if expiry_date != "1899-12-30" else None, # Handle invalid QDate initial value
            'total_price': quantity * unit_price
        })

        self.update_invoice_items_table()
        self.calculate_total()
        self.product_search_input.clear()
        self.product_quantity_input.setValue(1)
        self.product_unit_price_input.setValue(0.01)
        self.batch_number_input.clear()
        self.expiry_date_input.setDate(QDate.currentDate())

    def update_invoice_items_table(self):
        self.invoice_items_table.setRowCount(len(self.selected_products_for_invoice))
        for row_idx, item in enumerate(self.selected_products_for_invoice):
            # Product Name, Batch No., Expiry Date, Quantity, Unit Price, Subtotal
            self.invoice_items_table.setItem(row_idx, 0, QTableWidgetItem(item['name']))
            self.invoice_items_table.setItem(row_idx, 1, QTableWidgetItem(item['batch_number'] or "N/A"))
            self.invoice_items_table.setItem(row_idx, 2, QTableWidgetItem(item['expiry_date'] or "N/A"))
            self.invoice_items_table.setItem(row_idx, 3, QTableWidgetItem(str(item['quantity'])))
            self.invoice_items_table.setItem(row_idx, 4, QTableWidgetItem(f"{item['unit_price']:.2f}"))
            self.invoice_items_table.setItem(row_idx, 5, QTableWidgetItem(f"{item['total_price']:.2f}"))
        self.invoice_items_table.resizeColumnsToContents()
        self.invoice_items_table.horizontalHeader().setStretchLastSection(True)

    def calculate_total(self):
        total_amount = 0.0
        for item in self.selected_products_for_invoice:
            total_amount += item['total_price']
        self.total_label.setText(f"Total Amount: ${total_amount:.2f}")

    def save_invoice(self):
        invoice_number = self.invoice_number_input.text()
        invoice_date = self.invoice_date_edit.date().toString("yyyy-MM-dd")
        supplier_name = self.supplier_name_input.text().strip()
        total_amount_calculated = sum(item['total_price'] for item in self.selected_products_for_invoice)

        if not supplier_name:
            QMessageBox.warning(self, "Input Error", "Supplier Name cannot be empty.")
            return
        if not self.selected_products_for_invoice:
            QMessageBox.warning(self, "Input Error", "Please add products to the invoice.")
            return

        purchase_id = database.create_purchase_invoice(invoice_number, invoice_date, supplier_name, total_amount_calculated)

        if purchase_id:
            success_items = True
            for item_data in self.selected_products_for_invoice:
                product_id = item_data['product_id']
                quantity = item_data['quantity']
                unit_price = item_data['unit_price']
                batch_number = item_data['batch_number']
                expiry_date = item_data['expiry_date']
                
                if not database.add_purchase_item(purchase_id, product_id, quantity, unit_price, batch_number, expiry_date):
                    success_items = False
                    break
            
            if success_items:
                QMessageBox.information(self, "Success", f"Purchase Invoice {invoice_number} created successfully.")
                database.record_activity(self.current_user_role, f"Created purchase invoice: {invoice_number}") # Log activity
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Purchase invoice created, but some items failed to be added/stock updated. Please check manually.")
        else:
            QMessageBox.warning(self, "Error", "Failed to create purchase invoice. Invoice number might already exist.")

def generate_pdf_report(filename, title, headers, data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, 0, 1, "C")
    pdf.ln(10)

    # Table Header
    pdf.set_font("Arial", "B", 10)
    col_width = pdf.w / (len(headers) + 1) # Adjust column width
    row_height = 8
    
    for header in headers:
        pdf.cell(col_width, row_height, str(header), 1, 0, "C")
    pdf.ln()

    # Table Data
    pdf.set_font("Arial", "", 10)
    for row in data:
        for item in row:
            pdf.cell(col_width, row_height, str(item), 1, 0, "C")
        pdf.ln()
    
    pdf.output(filename)

class SettingsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent # Reference to HealthKingPharmaApp
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel("Settings")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(header_label)
        main_layout.addSpacing(10)

        # Navigation Tabs
        self.settings_tabs = QTabWidget()
        self.user_management_tab = UserManagementTab(self)
        self.system_settings_tab = SystemSettingsTab(self)
        self.activity_log_tab = ActivityLogScreen(self) # Add Activity Log Tab

        self.settings_tabs.addTab(self.user_management_tab, "User Management")
        self.settings_tabs.addTab(self.activity_log_tab, "Activity Logs") # New tab for activity logs

        main_layout.addWidget(self.settings_tabs)
        self.setLayout(main_layout)

        self.update_ui_for_role()
        self.load_users()

    def update_ui_for_role(self):
        if self.parent_app.current_user_role == 'admin':
            self.settings_tabs.setTabVisible(self.settings_tabs.indexOf(self.user_management_tab), True)
            self.settings_tabs.setTabVisible(self.settings_tabs.indexOf(self.activity_log_tab), True) # Make activity logs visible for admin
        else:
            self.settings_tabs.setTabVisible(self.settings_tabs.indexOf(self.user_management_tab), False)
            self.settings_tabs.setTabVisible(self.settings_tabs.indexOf(self.activity_log_tab), False) # Hide activity logs for non-admin
    
    def change_user_password(self):
        selected_item = self.user_table.currentItem()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            username = self.user_table.item(selected_item.row(), 1).text()

            reply = QMessageBox.question(self, 'Confirm Reset Password', 
                                         f"Are you sure you want to reset the password for user '{username}'?\nThis will generate a new random password.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                new_password = database.reset_user_password(user_id)
                if new_password:
                    QMessageBox.information(self, "Success", f"Password for user '{username}' reset successfully. New password: {new_password}")
                    database.record_activity(self.parent_app.parent_app.current_user_role, f"Reset password for user: {username}") # Log activity
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to reset password for user '{username}'.")
        else:
            QMessageBox.warning(self, "Error", "Please select a user to reset password.")

    def load_users(self):
        # This method will be used to load user data for the User Management tab
        self.user_management_tab.load_users()

class UserManagementTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent # Reference to SettingsScreen
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Settings")
        back_button.clicked.connect(lambda: self.parent_app.tab_widget.setCurrentWidget(self.parent_app))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("User Management")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Search and Filter
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_users)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        main_layout.addLayout(search_layout)

        # User Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5) # ID, Username, Role, Status, Actions
        self.user_table.setHorizontalHeaderLabels(["ID", "Username", "Role", "Status", "Actions"])
        self.user_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.user_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.user_table)

        # Action Buttons
        action_button_layout = QHBoxLayout()
        self.add_user_button = QPushButton("Add New User")
        self.edit_user_button = QPushButton("Edit User")
        self.delete_user_button = QPushButton("Delete User")
        self.reset_password_button = QPushButton("Reset Password")

        self.add_user_button.clicked.connect(self.show_add_user_dialog)
        self.edit_user_button.clicked.connect(self.show_edit_user_dialog)
        self.delete_user_button.clicked.connect(self.delete_selected_user)
        self.reset_password_button.clicked.connect(self.reset_password_for_selected_user)

        action_button_layout.addWidget(self.add_user_button)
        action_button_layout.addWidget(self.edit_user_button)
        action_button_layout.addWidget(self.delete_user_button)
        action_button_layout.addWidget(self.reset_password_button)
        main_layout.addLayout(action_button_layout)

        self.setLayout(main_layout)
        self.load_users()

    def load_users(self):
        users = database.get_all_users()
        self.user_table.setRowCount(len(users))
        for row_idx, user in enumerate(users):
            for col_idx, data in enumerate(user):
                item = QTableWidgetItem(str(data))
                if col_idx == 0: # Assuming first column is ID
                    item.setData(Qt.ItemDataRole.UserRole, user[0]) # Store user ID
                self.user_table.setItem(row_idx, col_idx, item)
        self.user_table.resizeColumnsToContents()
        self.user_table.horizontalHeader().setStretchLastSection(True)

    def search_users(self):
        search_text = self.search_input.text().strip()
        if search_text:
            all_users = database.get_all_users()
            filtered_users = [u for u in all_users if search_text.lower() in u[1].lower()] # Search by username
            self.load_users(filtered_users)
        else:
            self.load_users()

    def show_add_user_dialog(self):
        dialog = AddUserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_users()

    def show_edit_user_dialog(self):
        selected_item = self.user_table.currentItem()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            user_data = database.get_user_by_id(user_id)
            if user_data:
                dialog = EditUserDialog(user_data, self)
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    self.load_users()

    def delete_selected_user(self):
        selected_item = self.user_table.currentItem()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            username = self.user_table.item(selected_item.row(), 1).text()

            reply = QMessageBox.question(self, 'Confirm Delete', 
                                         f"Are you sure you want to delete user '{username}'?\nThis action cannot be undone.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                success = database.delete_user(user_id)
                if success:
                    QMessageBox.information(self, "Success", f"User '{username}' deleted successfully.")
                    database.record_activity(self.parent_app.parent_app.current_user_role, f"Deleted user: {username}") # Log activity
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to delete user '{username}'.")
        else:
            QMessageBox.warning(self, "Error", "Please select a user to delete.")

    def reset_password_for_selected_user(self):
        selected_item = self.user_table.currentItem()
        if selected_item:
            user_id = selected_item.data(Qt.ItemDataRole.UserRole)
            username = self.user_table.item(selected_item.row(), 1).text()

            reply = QMessageBox.question(self, 'Confirm Reset Password', 
                                         f"Are you sure you want to reset the password for user '{username}'?\nThis will generate a new random password.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                new_password = database.reset_user_password(user_id)
                if new_password:
                    QMessageBox.information(self, "Success", f"Password for user '{username}' reset successfully. New password: {new_password}")
                    database.record_activity(self.parent_app.parent_app.current_user_role, f"Reset password for user: {username}") # Log activity
                    self.load_users()
                else:
                    QMessageBox.warning(self, "Error", f"Failed to reset password for user '{username}'.")
        else:
            QMessageBox.warning(self, "Error", "Please select a user to reset password.")

class AddUserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New User")
        self.setGeometry(200, 200, 400, 350)

        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        layout.addRow("Username:", self.username_input)

        self.role_combo = QComboBox()
        self.role_combo.addItem("Admin", "admin")
        self.role_combo.addItem("Manager", "manager")
        self.role_combo.addItem("Staff", "staff")
        layout.addRow("Role:", self.role_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Active", "active")
        self.status_combo.addItem("Inactive", "inactive")
        layout.addRow("Status:", self.status_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def accept(self):
        username = self.username_input.text()
        role = self.role_combo.currentData()
        status = self.status_combo.currentData()

        if not username or not role or not status:
            QMessageBox.warning(self, "Input Error", "Username, Role, and Status cannot be empty.")
            return

        user_id = database.add_user(username, role, status)
        if user_id:
            QMessageBox.information(self, "Success", f"User '{username}' added successfully.")
            database.record_activity(self.parent().parent_app.current_user_role, f"Added user: {username}") # Log activity
            super().accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to add user '{username}'. Username might already be in use.")

class EditUserDialog(QDialog):
    def __init__(self, user_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit User")
        self.setGeometry(200, 200, 400, 350)
        self.user_data = user_data # (id, username, role, status)

        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        layout.addRow("Username:", self.username_input)

        self.role_combo = QComboBox()
        self.role_combo.addItem("Admin", "admin")
        self.role_combo.addItem("Manager", "manager")
        self.role_combo.addItem("Staff", "staff")
        layout.addRow("Role:", self.role_combo)

        self.status_combo = QComboBox()
        self.status_combo.addItem("Active", "active")
        self.status_combo.addItem("Inactive", "inactive")
        layout.addRow("Status:", self.status_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def load_user_data(self):
        self.username_input.setText(self.user_data[1])
        self.role_combo.setCurrentData(self.user_data[2])
        self.status_combo.setCurrentData(self.user_data[3])

    def accept(self):
        username = self.username_input.text()
        role = self.role_combo.currentData()
        status = self.status_combo.currentData()

        if not username or not role or not status:
            QMessageBox.warning(self, "Input Error", "Username, Role, and Status cannot be empty.")
            return

        success = database.update_user(self.user_data[0], username, role, status)
        if success:
            QMessageBox.information(self, "Success", f"User '{username}' updated successfully.")
            database.record_activity(self.parent().parent_app.current_user_role, f"Updated user: {username}") # Log activity
            super().accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to update user '{username}'.")

class SystemSettingsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent # Reference to SettingsScreen
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Settings")
        back_button.clicked.connect(lambda: self.parent_app.tab_widget.setCurrentWidget(self.parent_app))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("System Settings")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Settings Content (Placeholder)
        # This will be expanded with various system settings options
        settings_content = QLabel("System settings content goes here...")
        settings_content.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_content.setStyleSheet("font-size: 16px; padding: 20px;")
        main_layout.addWidget(settings_content)

        self.setLayout(main_layout)

class ActivityLogScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent # Reference to HealthKingPharmaApp
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Settings")
        back_button.clicked.connect(lambda: self.parent_app.tab_widget.setCurrentWidget(self.parent_app))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("User Activity Logs")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        self.log_table = QTableWidget()
        self.log_table.setColumnCount(3) # Timestamp, Username, Action
        self.log_table.setHorizontalHeaderLabels(["Timestamp", "Username", "Action"])
        self.log_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.log_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.log_table)

        self.setLayout(main_layout)
        self.load_logs()

    def load_logs(self):
        logs = database.get_all_activity_logs()
        self.log_table.setRowCount(len(logs))
        for row_idx, log_entry in enumerate(logs):
            for col_idx, data in enumerate(log_entry):
                self.log_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
        self.log_table.resizeColumnsToContents()
        self.log_table.horizontalHeader().setStretchLastSection(True)

class NotificationsScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_app = parent # Reference to HealthKingPharmaApp
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        header_layout = QHBoxLayout()
        back_button = QPushButton("← Back to Dashboard")
        back_button.clicked.connect(lambda: self.parent_app.show_main_dashboard(self.parent_app.current_user_role))
        header_layout.addWidget(back_button)
        header_layout.addStretch(1)
        header_label = QLabel("Notifications")
        header_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        header_layout.addWidget(header_label)
        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        self.notification_table = QTableWidget()
        self.notification_table.setColumnCount(4) # Type, Item, Message, Date
        self.notification_table.setHorizontalHeaderLabels(["Type", "Item", "Message", "Date"])
        self.notification_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.notification_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.notification_table)

        refresh_button = QPushButton("Refresh Notifications")
        refresh_button.clicked.connect(self.load_notifications)
        main_layout.addWidget(refresh_button)

        self.setLayout(main_layout)
        self.load_notifications()

    def load_notifications(self):
        notifications = []

        # Low Stock Alerts
        reorder_products = database.get_products_for_reorder()
        for product_id, name, category, packing, quantity, min_stock in reorder_products:
            notifications.append(["Low Stock", name, f"Current: {quantity}, Min: {min_stock}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        # Expiring Products Alerts
        expiring_batches = database.get_expiring_products()
        for batch_id, product_name, batch_number, expiry_date, quantity in expiring_batches:
            notifications.append(["Expiry Alert", product_name, f"Batch: {batch_number}, Expires: {expiry_date}, Qty: {quantity}", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        self.notification_table.setRowCount(len(notifications))
        for row_idx, notification in enumerate(notifications):
            for col_idx, data in enumerate(notification):
                self.notification_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
        self.notification_table.resizeColumnsToContents()
        self.notification_table.horizontalHeader().setStretchLastSection(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HealthKingPharmaApp()
    window.show()
    sys.exit(app.exec())
