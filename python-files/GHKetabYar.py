# GH_Ketab_Yar - main.py
# نسخه‌ی کامل: مدیریت کتابخانه مدرسه شهید سلیمی
# طراح: محمد قادری پور
# پیام خوش آمد: "به نرم‌افزار مدیریت کتابخانه شهید سلیمی خوش آمدید"

import sys, os, json, sqlite3
from datetime import datetime, timedelta
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMessageBox, QTableWidgetItem

APP_NAME = "GH Ketab Yar"
DB_FILE = "library.db"
THEMES_DIR = "themes"
FONT_FAMILY = "IRANSans, Segoe UI, B Nazanin, sans-serif"

DEFAULT_THEMES = {
    "light": {
        "name": "Light",
        "stylesheet": """
        QWidget{background: #f8fafc; color:#0b1720; font-family: '%s';}
        QPushButton{border-radius:10px; padding:6px 10px; background: #2563eb; color: white}
        QTableWidget{background:white}
        """ % FONT_FAMILY
    },
    "dark": {
        "name": "Dark",
        "stylesheet": """
        QWidget{background: #0b1220; color:#e6eef8; font-family: '%s';}
        QPushButton{border-radius:10px; padding:6px 10px; background: #4f46e5; color: white}
        QTableWidget{background:#071322}
        """ % FONT_FAMILY
    },
    "colorful": {
        "name": "Colorful",
        "stylesheet": """
        QWidget{background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #e6f7ff, stop:1 #f3e6ff); color:#062235; font-family: '%s';}
        QPushButton{border-radius:12px; padding:6px 12px; background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #7c3aed, stop:1 #0891b2); color:white}
        QTableWidget{background: rgba(255,255,255,0.9)}
        """ % FONT_FAMILY
    }
}

# ---------------- Database ----------------
class DB:
    def __init__(self, path=DB_FILE):
        self.path = path
        new_db = not os.path.exists(self.path)
        self.conn = sqlite3.connect(self.path)
        self.conn.row_factory = sqlite3.Row
        self._init()
        if new_db:
            self._seed()

    def _init(self):
        c = self.conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade TEXT,
            phone TEXT,
            join_date TEXT,
            paid REAL DEFAULT 0,
            notes TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            reg_no TEXT,
            status TEXT DEFAULT 'available',
            entry_date TEXT,
            notes TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            book_id INTEGER,
            loan_date TEXT,
            due_date TEXT,
            returned INTEGER DEFAULT 0,
            return_date TEXT,
            notes TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            amount REAL,
            date TEXT,
            method TEXT,
            notes TEXT
        )''')
        self.conn.commit()

    def _seed(self):
        now = datetime.now().strftime('%Y-%m-%d')
        self.execute('INSERT INTO members (name, grade, phone, join_date, paid, notes) VALUES (?,?,?,?,?,?)',
                     ("علی رضایی", "دهم", "09120000000", now, 0, "عضو نمونه"))
        self.execute('INSERT INTO books (title, reg_no, status, entry_date, notes) VALUES (?,?,?,?,?)',
                     ("تسخیر قله‌ها", "K-001", "available", now, "رمان"))

    def fetchall(self, query, params=()):
        return [dict(r) for r in self.conn.execute(query, params).fetchall()]

    def execute(self, query, params=()):
        c = self.conn.cursor()
        c.execute(query, params)
        self.conn.commit()
        return c.lastrowid

# ---------------- Main Window ----------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DB()
        self.setWindowTitle(APP_NAME)
        self.resize(1100, 720)
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        self._ensure_theme_files()
        self.apply_theme("colorful")

        # پیام خوش‌آمد
        self.statusBar().showMessage("به نرم‌افزار مدیریت کتابخانه شهید سلیمی خوش آمدید")

        # منو
        self._create_menu()

        # تب‌ها
        self.tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tabs)
        self._create_member_tab()
        self._create_books_tab()

    def _ensure_theme_files(self):
        os.makedirs(THEMES_DIR, exist_ok=True)
        for name, data in DEFAULT_THEMES.items():
            path = os.path.join(THEMES_DIR, f"{name}.json")
            if not os.path.exists(path):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)

    def apply_theme(self, name):
        path = os.path.join(THEMES_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                theme = json.load(f)
                self.setStyleSheet(theme["stylesheet"])

    def _create_menu(self):
        menubar = self.menuBar()
        theme_menu = menubar.addMenu("تم")
        for theme in DEFAULT_THEMES.keys():
            action = QtGui.QAction(theme.capitalize(), self)
            action.triggered.connect(lambda checked, t=theme: self.apply_theme(t))
            theme_menu.addAction(action)
        about_action = QtGui.QAction("درباره ما", self)
        about_action.triggered.connect(self._show_about)
        menubar.addAction(about_action)

    def _show_about(self):
        QMessageBox.information(self, "درباره ما",
                                "طراح: محمد قادری پور\n\nنسخه‌ی مدیریت کتابخانه مدرسه شهید سلیمی")

    # ---------------- Member Tab ----------------
    def _create_member_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)
        self.tabs.addTab(widget, "اعضا")

        self.member_table = QtWidgets.QTableWidget()
        layout.addWidget(self.member_table)
        self.member_table.setColumnCount(6)
        self.member_table.setHorizontalHeaderLabels(["نام", "پایه", "تلفن", "تاریخ عضویت", "پرداخت", "یادداشت"])
        self._load_members()

    def _load_members(self):
        members = self.db.fetchall("SELECT * FROM members")
        self.member_table.setRowCount(len(members))
        for row, m in enumerate(members):
            self.member_table.setItem(row, 0, QTableWidgetItem(m["name"]))
            self.member_table.setItem(row, 1, QTableWidgetItem(m["grade"]))
            self.member_table.setItem(row, 2, QTableWidgetItem(m["phone"]))
            self.member_table.setItem(row, 3, QTableWidgetItem(m["join_date"]))
            self.member_table.setItem(row, 4, QTableWidgetItem(str(m["paid"])))
            self.member_table.setItem(row, 5, QTableWidgetItem(m["notes"]))

    # ---------------- Books Tab ----------------
    def _create_books_tab(self):
        widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        widget.setLayout(layout)
        self.tabs.addTab(widget, "کتاب‌ها")

        self.books_table = QtWidgets.QTableWidget()
        layout.addWidget(self.books_table)
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels(["عنوان", "کد", "وضعیت", "تاریخ ورود", "یادداشت"])
        self._load_books()

    def _load_books(self):
        books = self.db.fetchall("SELECT * FROM books")
        self.books_table.setRowCount(len(books))
        for row, b in enumerate(books):
            self.books_table.setItem(row, 0, QTableWidgetItem(b["title"]))
            self.books_table.setItem(row, 1, QTableWidgetItem(b["reg_no"]))
            self.books_table.setItem(row, 2, QTableWidgetItem(b["status"]))
            self.books_table.setItem(row, 3, QTableWidgetItem(b["entry_date"]))
            self.books_table.setItem(row, 4, QTableWidgetItem(b["notes"]))

# ---------------- Run ----------------
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
