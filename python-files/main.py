# main.py
import sys, os, sqlite3
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QTableView, QVBoxLayout, QWidget, QPushButton, QLabel, QLineEdit
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "planning.db")  # local DB by default

class LoginDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ورود - شیمی گستران سبز مامطیر")
        self.setFixedSize(360,200)
        layout = QtWidgets.QVBoxLayout()
        lbl = QLabel("سیستم برنامه‌ریزی - ورود")
        lbl.setAlignment(QtCore.Qt.AlignCenter)
        self.user = QLineEdit(); self.user.setPlaceholderText("نام کاربری")
        self.passw = QLineEdit(); self.passw.setPlaceholderText("رمز عبور"); self.passw.setEchoMode(QLineEdit.Password)
        btn = QPushButton("ورود"); btn.clicked.connect(self.check)
        layout.addWidget(lbl)
        layout.addWidget(self.user); layout.addWidget(self.passw); layout.addWidget(btn)
        self.setLayout(layout)
        self.authenticated = False

    def check(self):
        u = self.user.text().strip(); p = self.passw.text().strip()
        conn = sqlite3.connect(DB_PATH); c = conn.cursor()
        c.execute("SELECT role FROM users WHERE username=? AND password=?", (u,p))
        row = c.fetchone(); conn.close()
        if row:
            self.accept()
        else:
            QMessageBox.warning(self, "خطا", "نام کاربری یا رمز عبور اشتباه است.")

class TableTab(QWidget):
    def __init__(self, table_name, title):
        super().__init__()
        self.table_name = table_name
        layout = QVBoxLayout()
        self.view = QTableView()
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.model = None
        self.setup_model()

    def setup_model(self):
        db = QSqlDatabase.addDatabase("QSQLITE", self.table_name)
        db.setDatabaseName(DB_PATH)
        if not db.open():
            QMessageBox.critical(self, "DB Error", db.lastError().text())
            return
        model = QSqlTableModel(self, db)
        model.setTable(self.table_name)
        model.select()
        self.view.setModel(model)
        self.model = model

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("سیستم برنامه‌ریزی - شیمی گستران سبز مامطیر")
        self.resize(1000,700)
        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout()
        central.setLayout(layout)

        tabs = QtWidgets.QTabWidget(); tabs.setLayoutDirection(QtCore.Qt.RightToLeft)
        # Tables to show
        tables = [
            ("products","محصولات"),
            ("materials","مواد اولیه"),
            ("packing","اقلام بسته‌بندی"),
            ("orders","سفارش‌ها"),
            ("mos","دستور ساخت"),
            ("qc","آزمایشگاه"),
            ("production","تولید"),
            ("shipments","بارگیری")
        ]
        for tbl, title in tables:
            tab = TableTab(tbl, title)
            tabs.addTab(tab, title)
        layout.addWidget(tabs)

        btn_refresh = QPushButton("به‌روزرسانی جداول"); btn_refresh.clicked.connect(self.refresh)
        layout.addWidget(btn_refresh)

    def refresh(self):
        QMessageBox.information(self, "توجه", "برای به‌روزرسانی جداول، تب را دوباره باز کنید.")

def main():
    if not os.path.exists(DB_PATH):
        from db_init import init_db
        init_db(DB_PATH)
    app = QtWidgets.QApplication(sys.argv)
    login = LoginDialog()
    if login.exec_() != QtWidgets.QDialog.Accepted:
        return
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
