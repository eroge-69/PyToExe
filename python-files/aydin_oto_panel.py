
# Aydin Oto Elektrik Paneli - Basit PyQt5 Tabanli Uygulama
# Versiyon 1.0

import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QLineEdit,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView, QTextEdit, QComboBox)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDateTime
import os, json

# ------------------- VERITABANI -------------------
def init_db():
    conn = sqlite3.connect("veriler.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS musteriler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ad TEXT,
            borc REAL,
            telefon TEXT,
            tarih TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS kasa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tur TEXT,
            tutar REAL,
            aciklama TEXT,
            tarih TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS teslimler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT,
            sorun TEXT,
            telefon TEXT,
            tarih TEXT
        )
    """)
    conn.commit()
    conn.close()

# ------------------- GİRİŞ EKRANI -------------------
class LoginScreen(QWidget):
    def __init__(self, stacked):
        super().__init__()
        self.stacked = stacked

        self.setWindowTitle("AYDIN OTO ELEKTRİK")
        self.setGeometry(200, 200, 400, 300)

        # Arka plan
        if os.path.exists("giris_arka_plan.jpg"):
            self.background = QLabel(self)
            pixmap = QPixmap("giris_arka_plan.jpg").scaled(400, 300)
            self.background.setPixmap(pixmap)
            self.background.setGeometry(0, 0, 400, 300)
            self.background.lower()

        # Giriş alanları
        layout = QVBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Kullanıcı Adı")
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.Password)
        self.pass_input.setPlaceholderText("Şifre")
        login_btn = QPushButton("GİRİŞ YAP")
        login_btn.clicked.connect(self.check_login)

        layout.addWidget(QLabel("AYDIN OTO ELEKTRİK PANELİ"))
        layout.addWidget(self.user_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(login_btn)

        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("background-color: rgba(255,255,255,0.7); padding: 20px;")

        hbox = QHBoxLayout(self)
        hbox.addStretch()
        hbox.addWidget(container)
        hbox.addStretch()

        self.setLayout(hbox)

    def check_login(self):
        username = self.user_input.text()
        password = self.pass_input.text()

        with open("ayarlar.json", "r") as f:
            settings = json.load(f)

        if username == settings.get("kullanici") and password == settings.get("sifre"):
            self.stacked.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Hatalı", "Kullanıcı adı veya şifre yanlış")

# ------------------- ANA PANEL -------------------
class MainPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.label = QLabel("Hoş geldin, sistem aktif!")
        layout.addWidget(self.label)

        self.setLayout(layout)

# ------------------- ANA UYGULAMA -------------------
class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        init_db()
        self.login = LoginScreen(self)
        self.panel = MainPanel()

        self.addWidget(self.login)
        self.addWidget(self.panel)
        self.setFixedSize(400, 300)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
