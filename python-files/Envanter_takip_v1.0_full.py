# inventory_app_v9.py
"""
Envanter Takip v9 - Geliştirilmiş Sarf Malzeme ve Arayüz
- Sarf ve cihaz sayfalarında PDF'e aktar sorunu giderildi.
- Analiz ve raporlar sayfasına sayı ve yüzdelik veriler eklendi.
- Çoklu bildirim silme özelliği eklendi.
- Bakım ve garanti uyarısı 7 güne çekildi.
- Sarf malzeme için minimum stok değeri eklendi ve bildirimler ayarlandı.
- Bildirimlere çift tıklayınca ilgili ekrana geçiş yapılıyor.
- Şirket adı ve logosu sadece ana sayfada gösteriliyor.
- Sarf Malzemeleri tablosuna "tür", "adet", "marka", "model" ve "seri no" alanları eklendi.
- Cihaz ve Sarf malzeme kayıtlarını silme (sadece admin)
- Ana sayfadaki bildirimleri seçerek silme
- Masaüstü bildirim başlığını 'Envanter Takip' olarak ayarlama
- Veritabanı şemasını otomatik olarak güncelleme
- Tema değişikliği özelliği eklendi (koyu tema varsayılan)
- Admin Paneli Güncellendi: Log kayıtları, kullanıcı yönetimi (ekleme, silme, şifre değiştirme, listeleme)
- Ana Sayfa Güncellendi: Not kaydetme ve görüntüleme
- Şirket Bilgileri ve Logo Yönetimi
"""
import sys
import os
import sqlite3, os, shutil
import shutil
import secrets
import collections
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from PySide6.QtWidgets import QApplication, QMainWindow, QStyle, QSystemTrayIcon, QAbstractItemView
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout,
    QHBoxLayout, QMessageBox, QTabWidget, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QDialog, QTextEdit, QFormLayout, QCalendarWidget, QListWidget,
    QListWidgetItem, QDateEdit, QSpinBox, QMenu, QSystemTrayIcon, QCheckBox,
    QGroupBox, QInputDialog, QGraphicsScene, QGraphicsView, QGraphicsTextItem
)
from PySide6.QtGui import QPixmap, QImage, QIcon, QAction, QFont
from PySide6.QtCore import Qt, QTimer, QDate, QPropertyAnimation, QEasingCurve, QCoreApplication, QRectF,QSettings
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm

# optional libs
try:
    import qrcode
except Exception:
    qrcode = None

try:
    import cv2
except Exception:
    cv2 = None

try:
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except Exception:
    pass

try:
    import pyqtgraph as pg
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
except Exception:
    pg = None

try:
    import openpyxl
except Exception:
    openpyxl = None

# Türkçe karakter desteği için Reportlab fontu
try:
    if not os.path.exists("Vera.ttf"):
        # Font dosyasını bulamazsa default olarak sans-serif kullan
        pass
    else:
        pdfmetrics.registerFont(TTFont('Vera', 'Vera.ttf'))
        pdfmetrics.registerFont(TTFont('VeraBd', 'VeraBd.ttf'))
        pdfmetrics.registerFont(TTFont('VeraIt', 'VeraIt.ttf'))
        pdfmetrics.registerFont(TTFont('VeraBI', 'VeraBI.ttf'))
except Exception:
    pass

class Database:
    def __init__(self, db_file="inventory.db"):
        self.db_file = db_file
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_file)
            self.cursor = self.conn.cursor()
            self.create_tables()
            self.update_schema()
        except sqlite3.Error as e:
            QMessageBox.critical(None, "Veritabanı Hatası", f"Veritabanına bağlanılamadı: {e}")
            sys.exit(1)

    def create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY,
                marka_model TEXT NOT NULL,
                ip TEXT,
                mac TEXT,
                type TEXT,
                hostname TEXT UNIQUE,
                building TEXT,
                owner TEXT,
                purchase_date TEXT,
                warranty_end_date TEXT,
                maintenance_interval_months INTEGER,
                next_maintenance_date TEXT,
                status TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS consumables (
                id INTEGER PRIMARY KEY,
                type TEXT,
                name TEXT NOT NULL,
                part_number TEXT UNIQUE,
                quantity INTEGER,
                department TEXT,
                supplier TEXT,
                purchase_date TEXT,
                brand TEXT,
                model TEXT,
                serial_number TEXT,
                min_stock INTEGER
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY,
                type TEXT,
                message TEXT,
                is_read INTEGER DEFAULT 0,
                related_id INTEGER,
                created_at TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY,
                user TEXT,
                action TEXT,
                details TEXT,
                timestamp TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                timestamp TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS company (
                id INTEGER PRIMARY KEY,
                name TEXT,
                address TEXT,
                phone TEXT,
                logo_path TEXT,
                theme TEXT DEFAULT 'light'
            )
        """)
        
        self.conn.commit()

        # Varsayılan kullanıcı ekle
        self.cursor.execute("SELECT * FROM users WHERE username='admin'")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                ("admin", "admin123", "admin"))
            self.conn.commit()
            print("Varsayılan 'admin' kullanıcısı oluşturuldu.")

        # Varsayılan şirket bilgilerini ekle
        self.cursor.execute("SELECT * FROM company WHERE id=1")
        if not self.cursor.fetchone():
            self.cursor.execute("INSERT INTO company (id, name, address, phone, logo_path, theme) VALUES (?, ?, ?, ?, ?, ?)",
                                (1, "Şirket Adı", "Şirket Adresi", "Telefon", "", 'light'))
            self.conn.commit()

    def update_schema(self):
        """Mevcut veritabanı şemasını yeni sütunlarla ve tablolarla günceller."""
        self.cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in self.cursor.fetchall()]

        if 'next_maintenance_date' not in columns:
            self.cursor.execute("ALTER TABLE devices ADD COLUMN next_maintenance_date TEXT")
            self.conn.commit()
            print("Veritabanı şeması güncellendi: 'next_maintenance_date' sütunu eklendi.")

        if 'maintenance_interval_months' not in columns:
            self.cursor.execute("ALTER TABLE devices ADD COLUMN maintenance_interval_months INTEGER DEFAULT 0")
            self.conn.commit()
            print("Veritabanı şeması güncellendi: 'maintenance_interval_months' sütunu eklendi.")

        if 'mac' not in columns:
            self.cursor.execute("ALTER TABLE devices ADD COLUMN mac TEXT")
            self.conn.commit()
            print("Veritabanı şeması güncellendi: 'mac' sütunu eklendi.")

        if 'notes' not in [t[0] for t in self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
            self.cursor.execute("""
                CREATE TABLE notes (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    timestamp TEXT
                )
            """)
            self.conn.commit()
            print("Veritabanı şeması güncellendi: 'notes' tablosu eklendi.")

        self.cursor.execute("PRAGMA table_info(consumables)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'brand' not in columns:
            self.cursor.execute("ALTER TABLE consumables ADD COLUMN brand TEXT")
        if 'model' not in columns:
            self.cursor.execute("ALTER TABLE consumables ADD COLUMN model TEXT")
        if 'serial_number' not in columns:
            self.cursor.execute("ALTER TABLE consumables ADD COLUMN serial_number TEXT")
        if 'building' not in columns:
            self.cursor.execute("ALTER TABLE consumables ADD COLUMN building TEXT")
        # Yeni eklenen: min_stock sütunu
        if 'min_stock' not in columns:
            self.cursor.execute("ALTER TABLE consumables ADD COLUMN min_stock INTEGER DEFAULT 0")
        self.conn.commit()

        # 'devices' tablosuna 'department' sütunu ekleme
        self.cursor.execute("PRAGMA table_info(devices)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'department' not in columns:
            self.cursor.execute("ALTER TABLE devices ADD COLUMN department TEXT")
            self.conn.commit()
            print("Veritabanı şeması güncellendi: 'department' sütunu eklendi.")

        # 'company' tablosuna 'theme' sütunu ekleme
        self.cursor.execute("PRAGMA table_info(company)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'theme' not in columns:
            self.cursor.execute("ALTER TABLE company ADD COLUMN theme TEXT DEFAULT 'light'")
            self.conn.commit()
            print("Veritabanı şeması güncellendi: 'theme' sütunu eklendi.")


    def log_action(self, user, action, details):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO logs (user, action, details, timestamp) VALUES (?, ?, ?, ?)",
                            (user, action, details, timestamp))
        self.conn.commit()

    def get_user(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = self.cursor.fetchone()
        if user:
            return {"id": user[0], "username": user[1], "role": user[3]}
        return None
     
    def get_all_devices(self):
        self.cursor.execute("SELECT * FROM devices")
        rows = self.cursor.fetchall()
        columns = [col[0] for col in self.cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def add_notification(self, notif_type, message, related_id, unique=False):
        # Eğer unique=True ise, aynı tip ve related_id için aynı mesaj zaten varsa ekleme
        if unique:
            self.cursor.execute("""
                SELECT id FROM notifications
                WHERE type=? AND message=? AND related_id=?
            """, (notif_type, message, related_id))
            if self.cursor.fetchone():
                return  # zaten var, ekleme

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("""
            INSERT INTO notifications (type, message, related_id, created_at)
            VALUES (?, ?, ?, ?)
        """, (notif_type, message, related_id, created_at))
        self.conn.commit()

    def get_notifications(self):
        self.cursor.execute("SELECT * FROM notifications ORDER BY created_at DESC")
        return self.cursor.fetchall()
    
    def delete_old_notifications(self):
        """35 aydan eski bildirimleri siler."""
        try:
            one_month_ago = datetime.now() - timedelta(days=90)
            formatted_date = one_month_ago.strftime('%Y-%m-%d %H:%M:%S')
            self.cursor.execute("DELETE FROM notifications WHERE timestamp < ?", (formatted_date,))
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Eski bildirimleri silme hatası: {e}")
    def delete_notification(self, notif_id):
        self.cursor.execute("DELETE FROM notifications WHERE id=?", (notif_id,))
        self.conn.commit()
    

    def delete_device(self, id):
        self.cursor.execute("DELETE FROM devices WHERE id=?", (id,))
        self.conn.commit()

    def delete_consumable(self, id):
        self.cursor.execute("DELETE FROM consumables WHERE id=?", (id,))
        self.conn.commit()

    def get_notes(self):
        self.cursor.execute("SELECT id, content, timestamp FROM notes ORDER BY timestamp DESC")
        return self.cursor.fetchall()

    def save_note(self, content):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO notes (content, timestamp) VALUES (?, ?)", (content, timestamp))
        self.conn.commit()
        
    def delete_note(self, id):
        self.cursor.execute("DELETE FROM notes WHERE id=?", (id,))
        self.conn.commit()

    def get_users(self):
        self.cursor.execute("SELECT id, username, role FROM users")
        return self.cursor.fetchall()

    def add_user(self, username, password, role):
        try:
            self.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                                (username, password, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def change_user_password(self, username, new_password):
        self.cursor.execute("UPDATE users SET password=? WHERE username=?",
                            (new_password, username))
        self.conn.commit()

    def delete_user(self, username):
        self.cursor.execute("DELETE FROM users WHERE username=?", (username,))
        self.conn.commit()

    def get_logs(self):
        self.cursor.execute("SELECT * FROM logs ORDER BY timestamp DESC")
        return self.cursor.fetchall()

    def get_company_info(self):
        self.cursor.execute("SELECT name, address, phone, logo_path, theme FROM company WHERE id=1")
        info = self.cursor.fetchone()
        if info:
            return {"name": info[0], "address": info[1], "phone": info[2], "logo_path": info[3], "theme": info[4]}
        return None

    def save_company_info(self, name, address, phone, logo_path):
        self.cursor.execute("""
            INSERT OR REPLACE INTO company (id, name, address, phone, logo_path)
            VALUES (?, ?, ?, ?, ?)
        """, (1, name, address, phone, logo_path))
        self.conn.commit()

    def save_theme_setting(self, theme):
        self.cursor.execute("""
            UPDATE company SET theme=? WHERE id=1
        """, (theme,))
    
    def mark_notification_as_read(self, notif_id):
        self.cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notif_id,))        
        self.conn.commit()

class LoginDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Giriş")
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        self.title_label = QLabel("Hamarat Yazılım Envanter Takip", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Kullanıcı Adı")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Şifre")
        self.password_input.setEchoMode(QLineEdit.Password)
        
        login_button = QPushButton("Giriş")
        login_button.clicked.connect(self.login)

        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        self.setLayout(layout)

        self.user = None

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        self.user = self.db.get_user(username, password)

        if self.user:
            self.db.log_action(self.user["username"], "login", "")
            self.accept()
        else:
            QMessageBox.warning(self, "Hata", "Geçersiz kullanıcı adı veya şifre.")


class AddDeviceDialog(QDialog):
    def __init__(self, db, device_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.device_id = device_id
        self.setWindowTitle("Cihaz Ekle/Düzenle")
        self.setMinimumWidth(400)

        self.form_layout = QFormLayout()

        self.marka_model_input = QLineEdit()
        self.ip_input = QLineEdit()
        self.mac_input = QLineEdit()
        self.type_input = QLineEdit()
        self.hostname_input = QLineEdit()
        self.building_input = QLineEdit()
        self.department_input = QLineEdit()
        self.owner_input = QLineEdit()
        self.purchase_date_input = QDateEdit(calendarPopup=True)
        self.purchase_date_input.setDate(QDate.currentDate())
        self.warranty_end_date_input = QDateEdit(calendarPopup=True)
        self.maintenance_interval_input = QSpinBox()
        self.maintenance_interval_input.setMinimum(0)
        self.next_maintenance_date_input = QDateEdit(calendarPopup=True)
        self.status_input = QComboBox()
        self.status_input.addItems(["Aktif", "Pasif", "Bakımda", "Tamirde"])

        self.form_layout.addRow("Marka Model:", self.marka_model_input)
        self.form_layout.addRow("İp:", self.ip_input)
        self.form_layout.addRow("Mac:", self.mac_input)
        self.form_layout.addRow("Türü:", self.type_input)
        self.form_layout.addRow("HostName :", self.hostname_input)
        self.form_layout.addRow("Bina:", self.building_input)
        self.form_layout.addRow("Departman:", self.department_input)
        self.form_layout.addRow("Sahibi:", self.owner_input)
        self.form_layout.addRow("Satın Alma Tarihi:", self.purchase_date_input)
        self.form_layout.addRow("Garanti Bitiş Tarihi:", self.warranty_end_date_input)
        self.form_layout.addRow("Bakım Aralığı (ay):", self.maintenance_interval_input)
        self.form_layout.addRow("Sonraki Bakım Tarihi:", self.next_maintenance_date_input)
        self.form_layout.addRow("Durum:", self.status_input)
        
        # Sonraki bakım tarihi girilmemişse, bakım aralığına göre hesapla
        self.maintenance_interval_input.valueChanged.connect(self.update_next_maintenance_date)
        self.purchase_date_input.dateChanged.connect(self.update_next_maintenance_date)

        if self.device_id:
            self.load_data()

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save)
        
        self.generate_qr_button = QPushButton("QR Oluştur")
        self.generate_qr_button.clicked.connect(self.generate_qr)
        if qrcode is None:
            self.generate_qr_button.setEnabled(False)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.generate_qr_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

    def load_data(self):
        self.db.cursor.execute("SELECT * FROM devices WHERE id=?", (self.device_id,))
        data = self.db.cursor.fetchone()
        if data:
            self.marka_model_input.setText(data[1])
            self.ip_input.setText(data[2])
            self.mac_input.setText(data[3])
            self.type_input.setText(data[4])
            self.hostname_input.setText(data[5])
            self.building_input.setText(data[6])
            self.owner_input.setText(data[7])
            self.purchase_date_input.setDate(QDate.fromString(data[8], "yyyy-MM-dd"))
            self.warranty_end_date_input.setDate(QDate.fromString(data[9], "yyyy-MM-dd"))
            self.maintenance_interval_input.setValue(data[10])
            if data[11]:
                self.next_maintenance_date_input.setDate(QDate.fromString(data[11], "yyyy-MM-dd"))
            index = self.status_input.findText(data[12])
            if index != -1:
                self.status_input.setCurrentIndex(index)
            # Yeni eklenen department sütunu için veri yükle
            if len(data) > 13: # Department sütunu mevcutsa
                self.department_input.setText(data[13])

    def update_next_maintenance_date(self):
        interval = self.maintenance_interval_input.value()
        purchase_date = self.purchase_date_input.date()
        if interval > 0:
            next_date = purchase_date.addMonths(interval)
            self.next_maintenance_date_input.setDate(next_date)
       
    def save(self):
        name = self.marka_model_input.text()
        ip = self.ip_input.text()
        mac = self.mac_input.text()
        type = self.type_input.text()
        hostname = self.hostname_input.text()
        building = self.building_input.text()
        department = self.department_input.text()
        owner = self.owner_input.text()
        purchase_date = self.purchase_date_input.date().toString("yyyy-MM-dd")
        warranty_end_date = self.warranty_end_date_input.date().toString("yyyy-MM-dd")
        maintenance_interval = self.maintenance_interval_input.value()
        next_maintenance_date = self.next_maintenance_date_input.date().toString("yyyy-MM-dd")
        status = self.status_input.currentText()
        
        if not name or not hostname:
            QMessageBox.warning(self, "Uyarı", "Marka Model ve Hostname alanları boş bırakılamaz.")
            return

        if self.device_id:
            # Güncelleme
            self.db.cursor.execute("""
                UPDATE devices SET marka_model=?, ip=?, mac=?, type=?, hostname=?, building=?, department=?, owner=?,
                purchase_date=?, warranty_end_date=?, maintenance_interval_months=?, next_maintenance_date=?, status=?
                WHERE id=?
            """, (name, ip, mac, type, hostname, building, department, owner, purchase_date, warranty_end_date, maintenance_interval, next_maintenance_date, status, self.device_id))
            self.db.conn.commit()
            QMessageBox.information(self, "Başarılı", "Cihaz bilgileri güncellendi.")
        else:
            # Ekleme
            self.db.cursor.execute("""
                INSERT INTO devices (marka_model, ip, mac, type, hostname, building, department, owner,
                                     purchase_date, warranty_end_date, maintenance_interval_months, next_maintenance_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, ip, mac, type, hostname, building, department, owner,
                   purchase_date, warranty_end_date, maintenance_interval, next_maintenance_date, status))
            self.db.conn.commit()
            QMessageBox.information(self, "Başarılı", "Cihaz başarıyla eklendi.")

        self.accept()
        
    def generate_qr(self):
        hostname = self.hostname_input.text()
        if not hostname:
            QMessageBox.warning(self, "Uyarı", "QR kodu oluşturmak için Hostname gerekli.")
            return
        
        qr_data = f"HOSTNAME:{hostname}\n" \
                  f"MARKA MODEL:{self.marka_model_input.text()}\n" \
                  f"İP:{self.ip_input.text()}"
        
        img = qrcode.make(qr_data)
        file_path, _ = QFileDialog.getSaveFileName(self, "QR Kodunu Kaydet", hostname + ".png", "PNG Dosyası (*.png)")
        if file_path:
            img.save(file_path)
            QMessageBox.information(self, "Başarılı", "QR kodu başarıyla kaydedildi.")


class AddConsumableDialog(QDialog):
    def __init__(self, db, consumable_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.consumable_id = consumable_id

        self.setWindowTitle("Sarf Malzeme Ekle/Düzenle")
        self.setMinimumWidth(400)

        # Form layout
        self.form_layout = QFormLayout()

        # Widget tanımları
        self.type_input = QLineEdit()
        self.name_input = QLineEdit()
        self.part_number_input = QLineEdit()
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setMinimum(0)
        self.building_input = QLineEdit()
        self.department_input = QLineEdit()
        self.supplier_input = QLineEdit()
        self.purchase_date_input = QDateEdit(calendarPopup=True)
        self.purchase_date_input.setDate(QDate.currentDate())
        self.brand_input = QLineEdit()
        self.model_input = QLineEdit()
        self.serial_number_input = QLineEdit()

        # Form layout ekleme
        self.form_layout.addRow("Tür:", self.type_input)
        self.form_layout.addRow("Adı:", self.name_input)
        self.form_layout.addRow("SARF NOTU:", self.part_number_input)
        self.form_layout.addRow("Miktar:", self.quantity_input)
        self.form_layout.addRow("Minimum Stok:", self.min_stock_input)
        self.form_layout.addRow("Bina:", self.building_input)
        self.form_layout.addRow("Departman:", self.department_input)
        self.form_layout.addRow("Tedarikçi:", self.supplier_input)
        self.form_layout.addRow("Satın Alma Tarihi:", self.purchase_date_input)
        self.form_layout.addRow("Marka:", self.brand_input)
        self.form_layout.addRow("Model:", self.model_input)
        self.form_layout.addRow("Seri No:", self.serial_number_input)

        # Kaydet butonu
        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.save_button)

        # Ana layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)

        # Eğer consumable_id varsa, veriyi yükle
        if self.consumable_id:
            self.load_data()

    def load_data(self):
        # DB’den veriyi çek
        self.db.cursor.execute("SELECT * FROM consumables WHERE id=?", (self.consumable_id,))
        data = self.db.cursor.fetchone()
        print("DEBUG: Fetched data for consumable_id =", self.consumable_id, "->", data)

        if not data:
            print("DEBUG: No data found for consumable_id =", self.consumable_id)
            return

        # Yardımcı fonksiyonlar
        def safe_set_int(spinbox, value, default=0):
            try:
                spinbox.setValue(int(str(value).strip()))
            except (ValueError, TypeError, AttributeError):
                if hasattr(spinbox, "setValue"):
                    spinbox.setValue(default)

        def safe_text(obj):
            return obj.text() if obj else ""
        def safe_value(obj):
            return obj.value() if obj else 0

        # QLineEdit alanları
        line_edits = {
            "type_input": 1,
            "name_input": 2,
            "part_number_input": 3,
            "department_input": 5,
            "supplier_input": 6,
            "brand_input": 8,
            "model_input": 9,
            "serial_number_input": 10,
            "building_input": 11
        }
        for attr, idx in line_edits.items():
            widget = getattr(self, attr, None)
            if widget and len(data) > idx and data[idx] is not None:
                widget.setText(str(data[idx]))
                print(f"DEBUG: Set {attr} -> {data[idx]}")
            elif widget:
                widget.setText("")
                print(f"DEBUG: Set {attr} -> '' (empty)")

        # QSpinBox alanları
        if hasattr(self, "quantity_input"):
            safe_set_int(self.quantity_input, data[4])
            print(f"DEBUG: Set quantity_input -> {data[4]}")
        if hasattr(self, "min_stock_input") and len(data) > 11:
            safe_set_int(self.min_stock_input, data[11])
            print(f"DEBUG: Set min_stock_input -> {data[12]}")

        # QDateEdit alanı
        if hasattr(self, "purchase_date_input") and data[7]:
            try:
                self.purchase_date_input.setDate(QDate.fromString(str(data[7]), "yyyy-MM-dd"))
                print(f"DEBUG: Set purchase_date_input -> {data[7]}")
            except Exception:
                print(f"WARNING: purchase_date_input could not be set -> {data[7]}")

    def save(self):
        consumable_type = self.type_input.text()
        name = self.name_input.text()
        part_number = self.part_number_input.text()
        quantity = self.quantity_input.value()
        min_stock = self.min_stock_input.value()
        building = self.building_input.text()
        department = self.department_input.text()
        supplier = self.supplier_input.text()
        purchase_date = self.purchase_date_input.date().toString("yyyy-MM-dd")
        brand = self.brand_input.text()
        model = self.model_input.text()
        serial_number = self.serial_number_input.text()

        if not name or not part_number:
            QMessageBox.warning(self, "Uyarı", "Ad ve Sarf Notu alanları boş bırakılamaz.")
            return

        if self.consumable_id:
            # Güncelleme
            self.db.cursor.execute("""
                UPDATE consumables SET type=?, name=?, part_number=?, quantity=?, min_stock=?, building=?, department=?, supplier=?, purchase_date=?, brand=?, model=?, serial_number=?
                WHERE id=?
            """, (consumable_type, name, part_number, quantity, min_stock, building, department, supplier, purchase_date, brand, model, serial_number, self.consumable_id))
            self.db.conn.commit()
            QMessageBox.information(self, "Başarılı", "Sarf malzeme bilgileri güncellendi.")
        else:
            # Ekleme
            self.db.cursor.execute("""
                INSERT INTO consumables (type, name, part_number, quantity, min_stock, building, department, supplier, purchase_date, brand, model, serial_number)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (consumable_type, name, part_number, quantity, min_stock, building, department, supplier, purchase_date, brand, model, serial_number))
            self.db.conn.commit()
            QMessageBox.information(self, "Başarılı", "Sarf malzeme başarıyla eklendi.")
            self.accept()

    

class QRScannerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("QR Kod Tarayıcı")
        self.scanned_data = None
        # QRScannerDialog'ın içeriği
        # Bu bölüm, OpenCV yüklü değilse çalışmaz.
        self.layout = QVBoxLayout(self)
        self.camera_view = QLabel("Kamera Görüntüsü")
        self.layout.addWidget(self.camera_view)
        self.cap = None
        self.timer = QTimer(self)
        if cv2:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                QMessageBox.warning(self, "Hata", "Kamera açılamadı.")
                self.reject()
                return
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30)
        else:
            self.layout.addWidget(QLabel("OpenCV yüklü değil. Bu özellik kullanılamaz."))

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            try:
                # QR kodu taranıyor
                detector = cv2.QRCodeDetector()
                data, bbox, _ = detector.detectAndDecode(frame)
                if data:
                    self.scanned_data = data
                    self.accept()
                # Görüntüyü PySide6'ya dönüştür
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
                self.camera_view.setPixmap(QPixmap.fromImage(qt_image).scaled(self.camera_view.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            except Exception as e:
                print(f"QR tarama hatası: {e}")

    def reject(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.timer.stop()
        super().reject()

    def accept(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
            self.timer.stop()
        super().accept()

class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hakkında")
        self.setFixedSize(300, 200)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("<h2>Envanter Takip Uygulaması</h2>"))
        layout.addWidget(QLabel("Versiyon: 1.0"))
        layout.addWidget(QLabel("Yazar: Hamarat Yazılım"))
        layout.addWidget(QLabel("Bu uygulama, envanter yönetimi için çözümdür. \nTüm Hakları Saklıdır.2025 "))
        
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

class CompanyInfoDialog(QDialog):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setWindowTitle("Şirket Bilgileri")
        self.setMinimumWidth(400)
        self.info = self.db.get_company_info()
        self.form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setText(self.info.get('name', ''))
        self.address_input = QLineEdit()
        self.address_input.setText(self.info.get('address', ''))
        self.phone_input = QLineEdit()
        self.phone_input.setText(self.info.get('phone', ''))
        
        self.logo_path = self.info.get('logo_path', '')
        self.logo_label = QLabel("Logo Dosyası Yok")
        if self.logo_path:
            self.logo_label.setText(self.logo_path.split("/")[-1])
        
        self.logo_button = QPushButton("Logo Seç")
        self.logo_button.clicked.connect(self.select_logo)

        self.form_layout.addRow("Şirket Adı:", self.name_input)
        self.form_layout.addRow("Adres:", self.address_input)
        self.form_layout.addRow("Telefon:", self.phone_input)
        self.form_layout.addRow("Logo:", self.logo_label)
        self.form_layout.addRow("", self.logo_button)

        self.save_button = QPushButton("Kaydet")
        self.save_button.clicked.connect(self.save)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.form_layout)
        main_layout.addWidget(self.save_button)
        self.setLayout(main_layout)

    def select_logo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Logo Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_path:
            self.logo_path = file_path
            self.logo_label.setText(os.path.basename(file_path))

    def save(self):
        name = self.name_input.text()
        address = self.address_input.text()
        phone = self.phone_input.text()
        self.db.save_company_info(name, address, phone, self.logo_path)
        QMessageBox.information(self, "Başarılı", "Şirket bilgileri güncellendi.")
        self.accept()

class AdminPanel(QTabWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db  # Veritabanı bağlantısı veya sınıfı
        self.settings = QSettings("MyCompany", "EnvanterApp")
        self.db_path = self.settings.value("db_path", "inventory.db")
        self.file_path = os.path.dirname(self.db_path) if self.db_path else ""
        #self.db_path = "inventory.db"  # Sabit veritabanı dosyası
        #self.file_path = ""           # Kullanıcının seçeceği klasör/dosya yolu
        self.current_user = None
        self.setTabsClosable(False)

        

        self.logs_tab = QWidget()
        self.addTab(self.logs_tab, "Loglar")
        self.setup_logs_tab()

        self.users_tab = QWidget()
        self.addTab(self.users_tab, "Kullanıcılar")
        self.setup_users_tab()

        self.db_tab = QWidget()
        self.addTab(self.db_tab, "Veritabanı İşlemleri")
        self.setup_db_tab()
        
    from PySide6.QtCore import QSettings
import os, shutil
from PySide6.QtWidgets import (
    QTabWidget, QWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QMessageBox
)


class AdminPanel(QTabWidget):
    def __init__(self, db,default_db="inventory.db", parent=None):
        super().__init__(parent)
        self.db = db

        # QSettings ile kalıcı ayarlar
        self.settings = QSettings("MyCompany", "EnvanterApp")

        # Daha önce kaydedilen yol varsa onu al
        self.db_path = self.settings.value("db_path", "inventroy.db")
        #self.file_path = os.path.dirname(self.db_path) if self.db_path else ""
        self.db_path = os.path.join(os.path.dirname(__file__), default_db)        
        self.load_database(self.db_path)
        self.logs_tab = QWidget()
        self.addTab(self.logs_tab, "Loglar")
        self.setup_logs_tab()

        self.users_tab = QWidget()
        self.addTab(self.users_tab, "Kullanıcılar")
        self.setup_users_tab()

        self.db_tab = QWidget()
        self.addTab(self.db_tab, "Veritabanı İşlemleri")
        self.setup_db_tab()
        

    def setup_db_tab(self):
        layout = QVBoxLayout()

        self.db_label = QLabel(f"Seçilen veritabanı: {self.db_path}")
        layout.addWidget(self.db_label)

        self.select_btn = QPushButton("Veritabanı Yolu Seç")
        self.select_btn.clicked.connect(self.select_file_path)
        layout.addWidget(self.select_btn)

        self.backup_btn = QPushButton("Veritabanını Yedekle")
        self.backup_btn.clicked.connect(self.backup_database)
        layout.addWidget(self.backup_btn)

        self.restore_btn = QPushButton("Veritabanını Geri Yükle")
        self.restore_btn.clicked.connect(self.restore_database)
        layout.addWidget(self.restore_btn)

        self.db_tab.setLayout(layout)
    def load_database(self, path):
        """Veritabanını yükle ve kontrol et"""
        if not os.path.exists(path):
            QMessageBox.warning(self, "Hata", f"Veritabanı bulunamadı:\n{path}")
            return  # veritabanı yoksa fonksiyondan çık

        # veritabanı varsa yolu ve nesneyi güncelle
        self.db_path = path
        self.db = Database(self.db_path)

        # log tab varsa güncelle
        if hasattr(self, 'log_list'):
            self.load_logs()
    
    def select_file_path(self):
        """Kullanıcının klasör seçip veritabanını kopyalaması veya seçmesi"""
        path = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if not path:
            return

        new_db_path = os.path.join(path, "inventory.db")

        if os.path.exists(new_db_path):
            reply = QMessageBox.question(
                self,
                "Üzerine Yaz?",
                f"{new_db_path} zaten mevcut.\nÜzerine yazmak ister misiniz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                try:
                    if os.path.exists(self.db_path):
                        shutil.copy2(self.db_path, new_db_path)
                        QMessageBox.information(self, "Bilgi", "Mevcut veritabanı üzerine yazıldı.")
                except Exception as e:
                    QMessageBox.warning(self, "Hata", f"Veritabanı kopyalanamadı:\n{str(e)}")
            else:
                QMessageBox.information(self, "Bilgi", "Mevcut veritabanı kullanılacak.")
        else:
            try:
                if os.path.exists(self.db_path):
                    shutil.copy2(self.db_path, new_db_path)
                    QMessageBox.information(self, "Bilgi", f"Veritabanı kopyalandı: {new_db_path}")
                else:
                    QMessageBox.warning(self, "Hata", "Kopyalanacak mevcut veritabanı bulunamadı!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Veritabanı kopyalanamadı:\n{str(e)}")

        # Yeni veritabanı yolunu güncelle
        self.load_database(new_db_path)
        self.file_path = path
        self.db_label.setText(f"Seçilen veritabanı: {self.db_path}")

    def backup_database(self):
        """Veritabanını yedekle"""
        if not self.db_path or not os.path.exists(self.db_path):
            QMessageBox.warning(self, "Hata", "Geçerli veritabanı bulunamadı!")
            return

        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Yedekleme Yolu Seç",
            "inventroy_backup.db",
            "SQLite Dosyası (*.db)"
        )

        if backup_path:
            try:
                shutil.copy2(self.db_path, backup_path)
                QMessageBox.information(self, "Başarılı", "Yedekleme tamamlandı!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Yedekleme yapılamadı:\n{str(e)}")
    def restore_database(self):
        if not self.db_path:
            QMessageBox.warning(self, "Hata", "Önce veritabanı yolu seçin!")
            return

        restore_path, _ = QFileDialog.getOpenFileName(self, "Geri Yüklenecek Dosya", "", "Veritabanı (*.db *.sqlite3)")
        if restore_path:
            shutil.copy2(restore_path, self.db_path)
            QMessageBox.information(self, "Başarılı", f"Geri yüklendi: {restore_path}")



    def set_current_user(self, user):
        self.current_user = user
        if user and user["role"] == "admin":
            # Admin'e özel sekmeleri aktif et
            pass

    def setup_logs_tab(self):
        layout = QVBoxLayout()
        self.log_list = QListWidget()
        layout.addWidget(self.log_list)
        self.load_logs()
        self.logs_tab.setLayout(layout)

    def load_logs(self):
        """Logları güvenli şekilde yükle"""
        if not hasattr(self, 'log_list') or not self.db:
            return

        self.log_list.clear()
        logs = self.db.get_logs()
        for log in logs:
            item = QListWidgetItem(
                f"[{log[4]}] - Kullanıcı: {log[1]}, Eylem: {log[2]}, Detaylar: {log[3]}"
            )
            self.log_list.addItem(item)
    
    def setup_users_tab(self):
        layout = QVBoxLayout()
        
        self.user_list = QListWidget()
        self.user_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        layout.addWidget(self.user_list)

        form_layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        
        form_layout.addRow("Kullanıcı Adı:", self.username_input)
        form_layout.addRow("Şifre:", self.password_input)
        form_layout.addRow("Rol:", self.role_combo)

        button_layout = QHBoxLayout()
        add_user_btn = QPushButton("Kullanıcı Ekle")
        add_user_btn.clicked.connect(self.add_user)
        change_pass_btn = QPushButton("Şifre Değiştir")
        change_pass_btn.clicked.connect(self.change_user_password)
        delete_user_btn = QPushButton("Kullanıcı Sil")
        delete_user_btn.clicked.connect(self.delete_user)
        
        button_layout.addWidget(add_user_btn)
        button_layout.addWidget(change_pass_btn)
        button_layout.addWidget(delete_user_btn)
        
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        self.users_tab.setLayout(layout)
        self.load_users()

    def load_users(self):
        self.user_list.clear()
        users = self.db.get_users()
        for user in users:
            item = QListWidgetItem(f"ID: {user[0]}, Kullanıcı Adı: {user[1]}, Rol: {user[2]}")
            self.user_list.addItem(item)
    
    def add_user(self):
        username = self.username_input.text()
        password = self.password_input.text()
        role = self.role_combo.currentText()
        if self.db.add_user(username, password, role):
            QMessageBox.information(self, "Başarılı", "Kullanıcı başarıyla eklendi.")
            self.load_users()
            self.username_input.clear()
            self.password_input.clear()
        else:
            QMessageBox.warning(self, "Hata", "Bu kullanıcı adı zaten mevcut.")
    
    def change_user_password(self):
        username, ok = QInputDialog.getText(self, "Şifre Değiştir", "Şifresini değiştireceğiniz kullanıcının adını girin:")
        if ok and username:
            new_password, ok = QInputDialog.getText(self, "Şifre Değiştir", f"{username} için yeni şifreyi girin:")
            if ok and new_password:
                self.db.change_user_password(username, new_password)
                QMessageBox.information(self, "Başarılı", "Şifre başarıyla değiştirildi.")

    def delete_user(self):
        selected_items = self.user_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bir kullanıcı seçin.")
            return

        for item in selected_items:
            username = item.text().split(",")[1].strip().split(":")[1].strip()
            if username == self.current_user["username"]:
                QMessageBox.warning(self, "Hata", "Kendi hesabınızı silemezsiniz.")
                continue
            
            reply = QMessageBox.question(self, "Onay", f"'{username}' kullanıcısını silmek istediğinizden emin misiniz?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.delete_user(username)
                QMessageBox.information(self, "Başarılı", f"'{username}' kullanıcısı başarıyla silindi.")
        self.load_users()


class MainWindow(QMainWindow):
    def __init__(self, db, current_user):
        super().__init__()
        self.db = db
        self.current_user = current_user
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_notifications)
        self.timer.start(60000) # Her 1 dakikada bir kontrol et
        self.load_data()
        self.load_company_info()
        self.update_analytics()
        self.show_startup_notification()

    def show_startup_notification(self):
        # Uygulama başladığında gösterilecek bildirim
        company_name = self.db.get_company_info().get('name', 'Şirket')
        notification_title = "Hamarat Yazılım Envanter Takip"
        notification_message = f"{company_name} Envanter Takip Uygulaması Başlatıldı."
        if QSystemTrayIcon.isSystemTrayAvailable():
            if hasattr(self, 'tray_icon'):
                self.tray_icon.showMessage(notification_title, notification_message)
            else:
                self.tray_icon = QSystemTrayIcon(self)
                self.tray_icon.setIcon(self.style().standardIcon(QStyle.SP_ComputerIcon))
                self.tray_icon.setVisible(True)
                self.tray_icon.showMessage(notification_title, notification_message)

    def init_ui(self):
        self.setWindowTitle("Hamarat Yazılım Envanter Takip ")
        self.setGeometry(100, 100, 1200, 800)

        # Ana Tab Widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Sekmeler
        self.home_tab = QWidget()
        self.devices_tab = QWidget()
        self.consumables_tab = QWidget()
        self.analytics_tab = QWidget()
        self.admin_tab = AdminPanel(self.db)
        self.admin_tab.set_current_user(self.current_user)

        self.tab_widget.addTab(self.home_tab, "Ana Sayfa")
        self.tab_widget.addTab(self.devices_tab, "Cihazlar")
        self.tab_widget.addTab(self.consumables_tab, "Sarf Malzemeleri")
        self.tab_widget.addTab(self.analytics_tab, "Analiz ve Raporlar")
        self.tab_widget.addTab(self.admin_tab, "Admin Paneli")

        self.tab_widget.currentChanged.connect(self.tab_changed)

        self.setup_home_tab()
        self.setup_devices_tab()
        self.setup_consumables_tab()
        self.setup_analytics_tab()

        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()

        # Dosya Menüsü
        file_menu = menu_bar.addMenu("Dosya")
        
        #backup_action = QAction("Veritabanını Yedekle", self)
        #backup_action.triggered.connect(self.backup_db)
        #file_menu.addAction(backup_action)
        
        #restore_action = QAction("Veritabanını Geri Yükle", self)
        #restore_action.triggered.connect(self.restore_db)
        #file_menu.addAction(restore_action)

        exit_action = QAction("Çıkış", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Ayarlar Menüsü
        settings_menu = menu_bar.addMenu("Ayarlar")
        
        company_info_action = QAction("Şirket Bilgileri", self)
        company_info_action.triggered.connect(self.show_company_info)
        settings_menu.addAction(company_info_action)

        change_theme_action = QAction("Tema Değiştir", self)
        change_theme_action.triggered.connect(self.change_theme)
        settings_menu.addAction(change_theme_action)

        # Yardım Menüsü
        help_menu = menu_bar.addMenu("Yardım")
        about_action = QAction("Hakkında", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def change_theme(self):
        current_theme = self.db.get_company_info().get('theme', 'light')
        new_theme = 'dark' if current_theme == 'light' else 'light'
        self.db.save_theme_setting(new_theme)
        QMessageBox.information(self, "Tema Değişikliği", f"Tema '{new_theme}' olarak değiştirildi. Uygulamayı yeniden başlatarak tema değişikliğini görebilirsiniz.")

    def load_theme(self):
        theme = self.db.get_company_info().get('theme', 'light')
        if theme == 'dark':
            self.setStyleSheet("""
                QMainWindow { background-color: #333; color: #fff; }
                QWidget { background-color: #333; color: #fff; }
                QTableWidget { background-color: #444; color: #fff; gridline-color: #555; }
                QTableWidget::item { border-bottom: 1px solid #555; }
                QHeaderView::section { background-color: #555; color: #fff; }
                QPushButton { background-color: #555; color: #fff; border: 1px solid #777; }
                QPushButton:hover { background-color: #666; }
                QTabWidget::pane { border: 1px solid #555; }
                QTabBar::tab { background: #444; color: #fff; }
                QTabBar::tab:selected { background: #333; border-top: 2px solid #00f; }
                QLineEdit, QTextEdit, QSpinBox, QComboBox, QDateEdit { background-color: #555; color: #fff; border: 1px solid #777; }
                QListWidget { background-color: #444; color: #fff; }
                QListWidget::item:selected { background-color: #666; }
            """)
        else:
            self.setStyleSheet("") # Clear any custom stylesheet

    def tab_changed(self, index):
        if self.tab_widget.tabText(index) == "Analiz ve Raporlar":
            self.update_analytics()
        if self.tab_widget.tabText(index) == "Admin Paneli":
            self.admin_tab.load_logs()
            self.admin_tab.load_users()
        if self.tab_widget.tabText(index) == "Ana Sayfa":
            self.load_notifications()
            self.load_notes()

    def setup_home_tab(self):
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()

        self.company_logo = QLabel()
        self.company_logo.setFixedSize(100, 100)
        self.company_logo.setScaledContents(True)
        header_layout.addWidget(self.company_logo)

        self.company_name = QLabel()
        self.company_name.setFont(QFont("Arial", 24))
        header_layout.addWidget(self.company_name)
        header_layout.addStretch()

        main_layout.addLayout(header_layout)

        # Bildirimler ve Notlar
        notes_notifications_layout = QHBoxLayout()

        # Bildirimler
        notifications_groupbox = QGroupBox("Bildirimler")
        notifications_layout = QVBoxLayout()
        self.notification_list = QListWidget()
        self.notification_list.itemDoubleClicked.connect(self.open_related_item)
        self.notification_list.setSelectionMode(QAbstractItemView.ExtendedSelection) # Çoklu seçim eklendi
        notifications_layout.addWidget(self.notification_list)

        delete_notification_btn = QPushButton("Seçili Bildirimleri Sil")
        delete_notification_btn.clicked.connect(self.delete_selected_notification)
        notifications_layout.addWidget(delete_notification_btn)

        notifications_groupbox.setLayout(notifications_layout)
        notes_notifications_layout.addWidget(notifications_groupbox)

        # Notlar
        notes_groupbox = QGroupBox("Notlar")
        notes_layout = QVBoxLayout()
        self.note_text = QTextEdit()
        self.note_list = QListWidget()
        notes_layout.addWidget(self.note_text)
        
        notes_button_layout = QHBoxLayout()
        save_note_btn = QPushButton("Notu Kaydet")
        save_note_btn.clicked.connect(self.save_note)
        delete_note_btn = QPushButton("Seçili Notu Sil")
        delete_note_btn.clicked.connect(self.delete_selected_note)
        notes_button_layout.addWidget(save_note_btn)
        notes_button_layout.addWidget(delete_note_btn)
        
        notes_layout.addLayout(notes_button_layout)
        notes_layout.addWidget(self.note_list)
        notes_groupbox.setLayout(notes_layout)
        
        notes_notifications_layout.addWidget(notes_groupbox)
        main_layout.addLayout(notes_notifications_layout)
        
        self.home_tab.setLayout(main_layout)

    def setup_devices_tab(self):
        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        add_button = QPushButton("Cihaz Ekle")
        add_button.clicked.connect(self.add_device)
        button_layout.addWidget(add_button)

        edit_button = QPushButton("Cihazı Düzenle")
        edit_button.clicked.connect(self.edit_device)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Cihazı Sil")
        delete_button.clicked.connect(self.delete_device)
        button_layout.addWidget(delete_button)

        search_layout = QHBoxLayout()
        self.search_input_devices = QLineEdit()
        self.search_input_devices.setPlaceholderText("Cihazlarda ara...")
        self.search_input_devices.textChanged.connect(self.search_devices)
        search_layout.addWidget(self.search_input_devices)
        
        pdf_button = QPushButton("PDF'e Aktar")
        pdf_button.clicked.connect(self.export_devices_pdf)
        search_layout.addWidget(pdf_button)
        
        excel_button = QPushButton("Excel'e Aktar")
        excel_button.clicked.connect(self.export_devices_excel)
        search_layout.addWidget(excel_button)

        qr_scan_button = QPushButton("QR Kod Tara")
        qr_scan_button.clicked.connect(self.scan_qr_device)
        if cv2 is None:
            qr_scan_button.setEnabled(False)
        search_layout.addWidget(qr_scan_button)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)

        self.device_table = QTableWidget()
        self.device_table.setColumnCount(14)
        self.device_table.setHorizontalHeaderLabels([
            "ID", "Marka Model", "IP", "MAC", "Tür", "Hostname", "Bina",
            "Departman", "Sahibi", "Satın Alma Tarihi", "Garanti Bitiş",
            "Bakım Aralığı","Sonraki Bakım Tarihi", "Durum"
        ])
        self.device_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.device_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.device_table)

        self.devices_tab.setLayout(main_layout)

    def setup_consumables_tab(self):
        main_layout = QVBoxLayout()

        button_layout = QHBoxLayout()
        add_button = QPushButton("Sarf Malzeme Ekle")
        add_button.clicked.connect(self.add_consumable)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Sarf Malzemeyi Düzenle")
        edit_button.clicked.connect(self.edit_consumable)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton("Sarf Malzemeyi Sil")
        delete_button.clicked.connect(self.delete_consumable)
        button_layout.addWidget(delete_button)

        search_layout = QHBoxLayout()
        self.search_input_consumables = QLineEdit()
        self.search_input_consumables.setPlaceholderText("Sarf malzemelerde ara...")
        self.search_input_consumables.textChanged.connect(self.search_consumables)
        search_layout.addWidget(self.search_input_consumables)

        pdf_button = QPushButton("PDF'e Aktar")
        pdf_button.clicked.connect(self.export_consumables_pdf)
        search_layout.addWidget(pdf_button)
        
        excel_button = QPushButton("Excel'e Aktar")
        excel_button.clicked.connect(self.export_consumables_excel)
        search_layout.addWidget(excel_button)

        main_layout.addLayout(button_layout)
        main_layout.addLayout(search_layout)

        self.consumable_table = QTableWidget()
        self.consumable_table.setColumnCount(11)
        self.consumable_table.setHorizontalHeaderLabels([
            "ID", "Tür", "Adı", "Sarf Notu", "Miktar", "Bina", "Departman", "Tedarikçi",
            "Satın Alma Tarihi", "Marka", "Model"
        ])
        self.consumable_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.consumable_table.setEditTriggers(QTableWidget.NoEditTriggers)
        main_layout.addWidget(self.consumable_table)

        self.consumables_tab.setLayout(main_layout)

    def setup_analytics_tab(self):
        main_layout = QVBoxLayout()

        self.analytics_plot_widget = pg.GraphicsLayoutWidget()
        main_layout.addWidget(self.analytics_plot_widget)
        self.analytics_tab.setLayout(main_layout)

    def update_analytics(self):
        if pg is None:
            QMessageBox.warning(self, "Hata", "pyqtgraph kütüphanesi kurulu değil. Analiz ve raporlar sayfası kullanılamaz.")
            return

        self.analytics_plot_widget.clear()

        devices = self.db.get_all_devices()
        consumables = self.db.cursor.execute("SELECT * FROM consumables").fetchall()

        # Cihaz Durum Analizi
        if devices:
            device_status_counts = collections.Counter(d['status'] for d in devices)
            statuses = list(device_status_counts.keys())
            counts = list(device_status_counts.values())
            total_devices = len(devices)

            p1 = self.analytics_plot_widget.addPlot(title="Cihaz Durum Bilgileri", row=0, col=0)
            p1.setYRange(0, max(counts) * 1.2 if counts else 10)
            bg1 = pg.BarGraphItem(x=list(range(len(statuses))), height=counts, width=0.5, brush='b')
            p1.addItem(bg1)
            p1.getAxis('bottom').setTicks([[(i, statuses[i]) for i in range(len(statuses))]])

            # Etiketler ve Yüzdelikler eklendi
            for i, status in enumerate(statuses):
                percent = (counts[i] / total_devices) * 100 if total_devices > 0 else 0
                label = f"{counts[i]} adet ({percent:.1f}%)"
                text_item = pg.TextItem(label, anchor=(0.5, 0))
                text_item.setParentItem(p1)
                text_item.setPos(i, counts[i])

        # Sarf Malzeme Tür Analizi
        if consumables:
            consumable_type_counts = collections.Counter(c[1] for c in consumables)
            types = list(consumable_type_counts.keys())
            counts = list(consumable_type_counts.values())
            total_consumables = len(consumables)

            p2 = self.analytics_plot_widget.addPlot(title="Sarf Malzeme Türleri", row=0, col=1)
            p2.setYRange(0, max(counts) * 1.2 if counts else 10)
            bg2 = pg.BarGraphItem(x=list(range(len(types))), height=counts, width=0.5, brush='r')
            p2.addItem(bg2)
            p2.getAxis('bottom').setTicks([[(i, types[i]) for i in range(len(types))]])

            # Etiketler ve Yüzdelikler eklendi
            for i, type_name in enumerate(types):
                percent = (counts[i] / total_consumables) * 100 if total_consumables > 0 else 0
                label = f"{counts[i]} adet ({percent:.1f}%)"
                text_item = pg.TextItem(label, anchor=(0.5, 0))
                text_item.setParentItem(p2)
                text_item.setPos(i, counts[i])
        
        self.analytics_plot_widget.ci.layout.setColumnStretchFactor(0, 1)
        self.analytics_plot_widget.ci.layout.setColumnStretchFactor(1, 1)


    def load_data(self):
        self.load_devices()
        self.load_consumables()
        self.load_notifications()
        self.load_notes()

    def load_devices(self):
        self.device_table.setRowCount(0)
        devices = self.db.get_all_devices()
        self.device_table.setRowCount(len(devices))
        for i, device in enumerate(devices):
            self.device_table.setItem(i, 0, QTableWidgetItem(str(device.get('id', ''))))
            self.device_table.setItem(i, 1, QTableWidgetItem(str(device.get('marka_model', ''))))
            self.device_table.setItem(i, 2, QTableWidgetItem(str(device.get('ip', ''))))
            self.device_table.setItem(i, 3, QTableWidgetItem(str(device.get('mac', ''))))
            self.device_table.setItem(i, 4, QTableWidgetItem(str(device.get('type', ''))))
            self.device_table.setItem(i, 5, QTableWidgetItem(str(device.get('hostname', ''))))
            self.device_table.setItem(i, 6, QTableWidgetItem(str(device.get('building', ''))))
            self.device_table.setItem(i, 7, QTableWidgetItem(str(device.get('department', ''))))
            self.device_table.setItem(i, 8, QTableWidgetItem(str(device.get('owner', ''))))
            self.device_table.setItem(i, 9, QTableWidgetItem(str(device.get('purchase_date', ''))))
            self.device_table.setItem(i, 10, QTableWidgetItem(str(device.get('warranty_end_date', ''))))
            self.device_table.setItem(i, 11, QTableWidgetItem(str(device.get('maintenance_interval_months', ''))))
            self.device_table.setItem(i, 12, QTableWidgetItem(str(device.get('next_maintenance_date', ''))))
            self.device_table.setItem(i, 13, QTableWidgetItem(str(device.get('status', ''))))

    def load_consumables(self):
        self.consumable_table.setRowCount(0)
        self.db.cursor.execute("SELECT id, type, name, part_number, quantity, building, department, supplier, purchase_date, brand, model FROM consumables")
        consumables = self.db.cursor.fetchall()
        self.consumable_table.setRowCount(len(consumables))
        for i, consumable in enumerate(consumables):
            for j, item in enumerate(consumable):
                self.consumable_table.setItem(i, j, QTableWidgetItem(str(item)))

    def load_notifications(self):
        self.notification_list.clear()
        notifications = self.db.get_notifications()
        for notif in notifications:
            notif_id, notif_type, notif_message, is_read, related_id, created_at = notif

            # Okunmamış bildirimleri kalın gösterelim
            if is_read == 0:
                item = QListWidgetItem(f"[{created_at}] {notif_message}")
                font = item.font()
                font.setBold(True)
                item.setFont(font)
            else:
                item = QListWidgetItem(f"[{created_at}] {notif_message}")

            # Gerekli bilgileri item içine sakla
            item.setData(Qt.UserRole, (notif_id, notif_type, related_id, is_read))
            self.notification_list.addItem(item)

    
    def load_notes(self):
        self.note_list.clear()
        notes = self.db.get_notes()
        for note in notes:
            item = QListWidgetItem(f"[{note[2]}] {note[1][:40]}...")
            item.setData(Qt.UserRole, note[0])
            self.note_list.addItem(item)
    
    def add_device(self):
        dialog = AddDeviceDialog(self.db)
        if dialog.exec() == QDialog.Accepted:
            self.load_devices()
            self.update_analytics()
    
    def edit_device(self):
        selected_rows = self.device_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir cihaz seçin.")
            return
        device_id = int(self.device_table.item(selected_rows[0].row(), 0).text())
        dialog = AddDeviceDialog(self.db, device_id=device_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_devices()
            self.update_analytics()
    
    def delete_device(self):
        selected_rows = self.device_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir cihaz seçin.")
            return
        
        reply = QMessageBox.question(self, "Onay", "Seçili cihazı silmek istediğinizden emin misiniz?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            device_id = int(self.device_table.item(selected_rows[0].row(), 0).text())
            self.db.delete_device(device_id)
            self.load_devices()
            self.update_analytics()
            QMessageBox.information(self, "Başarılı", "Cihaz başarıyla silindi.")

    def add_consumable(self):
        dialog = AddConsumableDialog(self.db)
        if dialog.exec() == QDialog.Accepted:
            self.load_consumables()
            self.update_analytics()

    def edit_consumable(self):
        selected_rows = self.consumable_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlemek için bir sarf malzeme seçin.")
            return
        consumable_id = int(self.consumable_table.item(selected_rows[0].row(), 0).text())
        dialog = AddConsumableDialog(self.db, consumable_id=consumable_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_consumables()
            self.update_analytics()

    def delete_consumable(self):
        selected_rows = self.consumable_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir sarf malzeme seçin.")
            return
        
        reply = QMessageBox.question(self, "Onay", "Seçili sarf malzemeyi silmek istediğinizden emin misiniz?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            consumable_id = int(self.consumable_table.item(selected_rows[0].row(), 0).text())
            self.db.delete_consumable(consumable_id)
            self.load_consumables()
            self.update_analytics()
            QMessageBox.information(self, "Başarılı", "Sarf malzeme başarıyla silindi.")

    def search_devices(self):
        search_text = self.search_input_devices.text().lower()
        for row in range(self.device_table.rowCount()):
            row_visible = False
            for col in range(self.device_table.columnCount()):
                item = self.device_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.device_table.setRowHidden(row, not row_visible)

    def search_consumables(self):
        search_text = self.search_input_consumables.text().lower()
        for row in range(self.consumable_table.rowCount()):
            row_visible = False
            for col in range(self.consumable_table.columnCount()):
                item = self.consumable_table.item(row, col)
                if item and search_text in item.text().lower():
                    row_visible = True
                    break
            self.consumable_table.setRowHidden(row, not row_visible)

    def save_note(self):
        content = self.note_text.toPlainText()
        if content:
            self.db.save_note(content)
            self.note_text.clear()
            self.load_notes()
            QMessageBox.information(self, "Başarılı", "Not başarıyla kaydedildi.")

    def delete_selected_note(self):
        selected_items = self.note_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek bir not seçin.")
            return
        
        reply = QMessageBox.question(self, "Onay", "Seçili notu silmek istediğinizden emin misiniz?",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for item in selected_items:
                note_id = item.data(Qt.UserRole)
                self.db.delete_note(note_id)
            self.load_notes()
            QMessageBox.information(self, "Başarılı", "Seçili notlar başarıyla silindi.")

   
    def delete_selected_notification(self):
        selected_items = self.notification_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Uyarı", "Silmek için bir bildirim seçin.")
            return

        for item in selected_items:
            # 4 değeri unpack et
            notif_id, notif_type, related_id, is_read = item.data(Qt.UserRole)
            self.db.delete_notification(notif_id)
            self.notification_list.takeItem(self.notification_list.row(item))

    def open_related_item(self, item):
        notif_id, notification_type, related_id, is_read = item.data(Qt.UserRole)

        # Çift tıklanınca bildirim "okundu" işaretlensin
        self.db.mark_notification_as_read(notif_id)
        self.load_notifications()

        if notification_type == 'device':
            dialog = AddDeviceDialog(self.db, device_id=related_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_devices()
                self.update_analytics()
        elif notification_type == 'consumable':
            dialog = AddConsumableDialog(self.db, consumable_id=related_id)
            if dialog.exec() == QDialog.Accepted:
                self.load_consumables()
                self.update_analytics()
    
    
    def check_notifications(self):
        now = datetime.now()

        # Cihaz garantisi ve bakımı
        self.db.cursor.execute("SELECT id, marka_model, warranty_end_date, next_maintenance_date FROM devices")
        devices = self.db.cursor.fetchall()
        for device_id, name, warranty_end_date_str, next_maintenance_date_str in devices:
            if warranty_end_date_str:
                warranty_date = datetime.strptime(warranty_end_date_str, "%Y-%m-%d")
                if 0 <= (warranty_date - now).days <= 7:
                    message = f"'{name}' cihazının garantisi 7 gün içinde BİTİYOR!"
                    self.db.add_notification('device', message, device_id, unique=True)  # 🔑 unique kontrol

            if next_maintenance_date_str:
                maintenance_date = datetime.strptime(next_maintenance_date_str, "%Y-%m-%d")
                if 0 <= (maintenance_date - now).days <= 7:
                    message = f"'{name}' cihazının bakımı 7 gün içinde GEREKLİ!"
                    self.db.add_notification('device', message, device_id, unique=True)

        # Sarf malzeme stoğu
        self.db.cursor.execute("SELECT id, name, quantity, min_stock FROM consumables")
        consumables = self.db.cursor.fetchall()
        for consumable_id, name, quantity, min_stock in consumables:
            if min_stock and quantity <= min_stock:
                message = f"'{name}' adlı sarf malzemenin stoğu {quantity} adete düşmüştür!"
                self.db.add_notification('consumable', message, consumable_id, unique=True)

        self.load_notifications()


    def show_about_dialog(self):
        dialog = AboutDialog(self)
        dialog.exec()

    def show_company_info(self):
        dialog = CompanyInfoDialog(self.db)
        if dialog.exec() == QDialog.Accepted:
            self.load_company_info()

    def load_company_info(self):
        info = self.db.get_company_info()
        if info:
            self.company_name.setText(info.get('name', ''))
            if info.get('logo_path') and os.path.exists(info['logo_path']):
                pixmap = QPixmap(info['logo_path'])
                self.company_logo.setPixmap(pixmap)
            else:
                self.company_logo.clear()
        self.load_theme()



    def export_devices_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Cihaz PDF Kaydet", "Cihaz Listesi.", "PDF Files (*.pdf)")
        if not path:
            return
        elements = []
        styles = getSampleStyleSheet()
        title = Paragraph("Cihaz Listesi", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 12))

        self.db.cursor.execute("SELECT id, marka_model, ip, mac, building, department, owner, type FROM devices")
        devices = self.db.cursor.fetchall()

        data = [["ID","Marka/Model","IP","MAC","Bina","Departman","Sahibi"]]
        for d in devices:
            data.append(list(d[:7]))

        t = Table(data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.gray),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black)
        ]))
        elements.append(t)
        elements.append(Spacer(1,12))

        # Tür bazlı adetler
        type_counts = {}
        for d in devices:
            type_counts[d[7]] = type_counts.get(d[7],0) +1
        for t_type, count in type_counts.items():
            elements.append(Paragraph(f"Toplam {t_type} adeti: {count}", styles['Normal']))
        elements.append(Paragraph(f"Toplam cihaz adeti: {len(devices)}", styles['Normal']))

        doc = SimpleDocTemplate(path, pagesize=A4)
        doc.build(elements)
        try:
            doc.build(elements)
            QMessageBox.information(self, "Başarılı", "Cihazlar Listesi PDF olarak kaydedildi.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"PDF oluşturulamadı: {str(e)}")


    def export_consumables_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "Sarf_Malzemeler.pdf", "PDF Files (*.pdf)")
        if not path:
            return

        self.db.cursor.execute("""
            SELECT id, type, name, part_number, quantity, min_stock, building, department, supplier, serial_number, model 
            FROM consumables
        """)
        data = self.db.cursor.fetchall()

        doc = SimpleDocTemplate(path, pagesize=A4)
        elements = []

        styles = getSampleStyleSheet()
        title = Paragraph("Sarf Malzemeler Listesi", styles['Title'])
        elements.append(title)
        elements.append(Paragraph("<br/>", styles['Normal']))

        # Tablo başlıkları
        headers = ["ID","Tür","Adı","Parça No","Miktar","Min Stok","Bina","Departman","Tedarikçi","Seri No","Model"]
        table_data = [headers] + [list(map(str, row)) for row in data]

        t = Table(table_data, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
            ('GRID', (0,0), (-1,-1), 0.5, colors.black),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ]))
        elements.append(t)

        try:
            doc.build(elements)
            QMessageBox.information(self, "Başarılı", "Sarf malzemeler PDF olarak kaydedildi.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"PDF oluşturulamadı: {str(e)}")

        # -----------------------------
        # Excel Export Fonksiyonları
        # -----------------------------
    def export_devices_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Excel Kaydet", "Cihaz_Listesi.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return

        self.db.cursor.execute("""
            SELECT id, marka_model, building, department, warranty_end_date
            FROM devices
        """)
        data = self.db.cursor.fetchall()

        headers = ["ID","Marka/Model","Bina","Departman","Garanti Bitiş"]
        df = pd.DataFrame(data, columns=headers)

        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Cihazlar")
            worksheet = writer.sheets["Cihazlar"]
            for i, col in enumerate(df.columns, 1):
                max_len = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = max_len + 2

        QMessageBox.information(self, "Başarılı", "Cihazlar Excel olarak kaydedildi.")
    def export_consumables_excel(self):
        path, _ = QFileDialog.getSaveFileName(self, "Excel Kaydet", "Sarf_Malzemeler.xlsx", "Excel Files (*.xlsx)")
        if not path:
            return

        self.db.cursor.execute("""
            SELECT id, type, name, part_number, quantity, min_stock, building, department, supplier, serial_number, model 
            FROM consumables
        """)
        data = self.db.cursor.fetchall()

        headers = ["ID","Tür","Adı","Parça No","Miktar","Min Stok","Bina","Departman","Tedarikçi","Seri No","Model"]
        df = pd.DataFrame(data, columns=headers)

        with pd.ExcelWriter(path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Sarf Malzemeler")
            worksheet = writer.sheets["Sarf Malzemeler"]
            for i, col in enumerate(df.columns, 1):
                max_len = max(df[col].astype(str).map(len).max(), len(col))
                worksheet.column_dimensions[openpyxl.utils.get_column_letter(i)].width = max_len + 2

        QMessageBox.information(self, "Başarılı", "Sarf malzemeler Excel olarak kaydedildi.")
    def scan_qr_device(self):
        dialog = QRScannerDialog(self)
        if dialog.exec() == QDialog.Accepted and dialog.scanned_data:
            qr_data = dialog.scanned_data
            data_dict = {}
            for line in qr_data.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    data_dict[key.strip()] = value.strip()
            
            hostname = data_dict.get('DEMIRBAS_KODU')
            if hostname:
                self.db.cursor.execute("SELECT id FROM devices WHERE hostname=?", (hostname,))
                result = self.db.cursor.fetchone()
                if result:
                    device_id = result[0]
                    self.tab_widget.setCurrentIndex(1) # Cihazlar sekmesine geç
                    self.search_input_devices.setText(hostname)
                    QMessageBox.information(self, "Cihaz Bulundu", f"'{hostname}' hostname'li cihaz bulundu.")
                    self.edit_device_by_id(device_id)
                else:
                    QMessageBox.warning(self, "Hata", f"'{hostname}' hostname'li cihaz veritabanında bulunamadı.")
            else:
                QMessageBox.warning(self, "Hata", "QR kodunda demirbaş kodu bilgisi bulunamadı.")
    
    def edit_device_by_id(self, device_id):
        dialog = AddDeviceDialog(self.db, device_id=device_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_devices()

    def backup_db(self):
        if self.current_user["role"] != "admin":
            QMessageBox.warning(self, "Yetki Hatası", "Sadece yöneticiler yedekleme yapabilir.")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Veritabanını Yedekle", "inventory_backup.db", "Veritabanı Dosyaları (*.db)")
        if file_path:
            try:
                shutil.copy(self.db.db_file, file_path)
                self.db.log_action(self.current_user["username"], "backup_db", f"Veritabanı yedeklendi: {file_path}")
                QMessageBox.information(self, "Başarılı", f"Veritabanı başarıyla yedeklendi:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Yedekleme sırasında bir hata oluştu: {e}")

    def restore_db(self):
        if self.current_user["role"] != "admin":
            QMessageBox.warning(self, "Yetki Hatası", "Sadece yöneticiler geri yükleme yapabilir.")
            return

        file_path, _ = QFileDialog.getOpenFileName(self, "Yedekleme Dosyasını Seç", "", "Veritabanı Dosyaları (*.db)")
        if file_path:
            reply = QMessageBox.question(self, "Onay", "Veritabanını geri yüklemek mevcut verileri silecektir. Emin misiniz?",
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.conn.close()
                shutil.copy(file_path, self.db.db_file)
                self.db.connect()
                self.db.log_action(self.current_user["username"], "restore_db", f"Geri yükleme: {file_path}")
                self.load_data()
                self.load_company_info() # Geri yüklemeden sonra şirket bilgisini yeniden yükle
                QMessageBox.information(self, "Başarılı", "Veritabanı başarıyla geri yüklendi.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    
    login_dialog = LoginDialog(db)
    if login_dialog.exec() == QDialog.Accepted:
        main_window = MainWindow(db, login_dialog.user)
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)