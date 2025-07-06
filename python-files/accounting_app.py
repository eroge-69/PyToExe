import sys
import sqlite3
import hashlib
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget, QMessageBox,
    QTableWidget, QTableWidgetItem, QComboBox, QDateEdit
)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QFont

# ------------------ Utility Functions ------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ------------------ Database Setup ------------------
conn = sqlite3.connect("accounting.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
    )
""")
c.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        type TEXT,
        amount REAL,
        category TEXT,
        date TEXT
    )
""")
conn.commit()

# ------------------ Main Application ------------------
class AccountingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Accounting App")
        self.setStyleSheet("background-color: #2e2e2e; color: white;")
        self.setGeometry(100, 100, 600, 400)

        self.stacked_widget = QStackedWidget()

        self.login_widget = self.create_login_widget()
        self.signup_widget = self.create_signup_widget()
        self.dashboard_widget = self.create_dashboard_widget()

        self.stacked_widget.addWidget(self.login_widget)
        self.stacked_widget.addWidget(self.signup_widget)
        self.stacked_widget.addWidget(self.dashboard_widget)

        layout = QVBoxLayout()
        layout.addWidget(self.stacked_widget)
        self.setLayout(layout)
        self.current_user = None

    # ------------------ UI Screens ------------------
    def create_login_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Login", font=QFont("Arial", 16)))

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        layout.addWidget(self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password.setPlaceholderText("Password")
        layout.addWidget(self.login_password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)
        layout.addWidget(login_button)

        switch_to_signup = QPushButton("No account? Sign up")
        switch_to_signup.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.signup_widget))
        layout.addWidget(switch_to_signup)

        widget.setLayout(layout)
        return widget

    def create_signup_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Sign Up", font=QFont("Arial", 16)))

        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Username")
        layout.addWidget(self.signup_username)

        self.signup_password = QLineEdit()
        self.signup_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password.setPlaceholderText("Password")
        layout.addWidget(self.signup_password)

        signup_button = QPushButton("Sign Up")
        signup_button.clicked.connect(self.handle_signup)
        layout.addWidget(signup_button)

        switch_to_login = QPushButton("Already have an account? Login")
        switch_to_login.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.login_widget))
        layout.addWidget(switch_to_login)

        widget.setLayout(layout)
        return widget

    def create_dashboard_widget(self):
        widget = QWidget()
        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        top_layout.addWidget(self.amount_input)

        self.type_box = QComboBox()
        self.type_box.addItems(["Income", "Expense"])
        top_layout.addWidget(self.type_box)

        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Category")
        top_layout.addWidget(self.category_input)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        top_layout.addWidget(self.date_input)

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_transaction)
        top_layout.addWidget(add_button)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Type", "Amount", "Category", "Date"])
        layout.addWidget(self.table)

        logout_button = QPushButton("Logout")
        logout_button.clicked.connect(self.logout)
        layout.addWidget(logout_button)

        widget.setLayout(layout)
        return widget

    # ------------------ Event Handlers ------------------
    def handle_login(self):
        username = self.login_username.text()
        password = hash_password(self.login_password.text())

        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            self.current_user = user[0]
            self.stacked_widget.setCurrentWidget(self.dashboard_widget)
            self.refresh_table()
        else:
            QMessageBox.warning(self, "Error", "Invalid credentials")

    def handle_signup(self):
        username = self.signup_username.text()
        password = hash_password(self.signup_password.text())
        try:
            c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            QMessageBox.information(self, "Success", "Account created!")
            self.stacked_widget.setCurrentWidget(self.login_widget)
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username already exists")

    def add_transaction(self):
        t_type = self.type_box.currentText()
        amount = self.amount_input.text()
        category = self.category_input.text()
        date = self.date_input.date().toString("yyyy-MM-dd")

        if not amount or not category:
            QMessageBox.warning(self, "Error", "Please fill all fields")
            return

        try:
            amount = float(amount)
        except ValueError:
            QMessageBox.warning(self, "Error", "Amount must be a number")
            return

        c.execute("INSERT INTO transactions (user_id, type, amount, category, date) VALUES (?, ?, ?, ?, ?)",
                  (self.current_user, t_type, amount, category, date))
        conn.commit()
        self.refresh_table()
        self.amount_input.clear()
        self.category_input.clear()

    def refresh_table(self):
        self.table.setRowCount(0)
        c.execute("SELECT type, amount, category, date FROM transactions WHERE user_id=?", (self.current_user,))
        for row_idx, row_data in enumerate(c.fetchall()):
            self.table.insertRow(row_idx)
            for col_idx, col in enumerate(row_data):
                self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(col)))

    def logout(self):
        self.current_user = None
        self.stacked_widget.setCurrentWidget(self.login_widget)

# ------------------ Run App ------------------
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AccountingApp()
    window.show()
    sys.exit(app.exec())
