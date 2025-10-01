#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Araç Bakım Kayıtları Yönetim Sistemi - Modern GUI
PyQt6 ile geliştirilmiş modern arayüz
"""

import sys
import sqlite3
import pandas as pd
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QComboBox, QDateEdit, QSpinBox, QTextEdit, QMessageBox,
    QTabWidget, QGroupBox, QFrame, QSplitter, QHeaderView, QAbstractItemView,
    QFileDialog, QProgressBar, QStatusBar, QMenuBar, QMenu, QDialog,
    QDialogButtonBox, QFormLayout, QCheckBox, QScrollArea
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal, QThread, QSize
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QAction, QPixmap

# ---------------------- Yardımcı: Excel Sütun Normalizasyonu ----------------------
TURKISH_MAP = {
    'İ': 'I', 'I': 'I', 'ı': 'i', 'Ş': 'S', 'ş': 's', 'Ğ': 'G', 'ğ': 'g',
    'Ü': 'U', 'ü': 'u', 'Ö': 'O', 'ö': 'o', 'Ç': 'C', 'ç': 'c'
}

def normalize_text(value: str) -> str:
    if value is None:
        return ''
    text = str(value).strip()
    # Türkçe karakterleri dönüştür
    text = ''.join(TURKISH_MAP.get(ch, ch) for ch in text)
    # Nokta, boşluk ve alt çizgileri tek biçime getir
    text = text.replace('.', ' ').replace('_', ' ')
    # Birden fazla boşluğu teke indir
    text = ' '.join(text.split())
    return text.upper()

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Excel'den gelen sütun adlarını esnek eşleştirme ile normalize eder."""
    # Desteklenen hedef adlar
    TARGETS = {
        'S.NO': { 'S NO', 'S.NO', 'SNO', 'SAYI', 'SIRA', 'SIRA NO', 'S_NO' },
        'PLAKA': { 'PLAKA', 'ARAC PLAKA', 'ARAC', 'ARAC NO' },
        'BÖLGE': { 'BOLGE', 'BÖLGE', 'BOLGE ADI' },
        'TARİH': { 'TARIH', 'TARİH', 'TARIHİ', 'BAKIM TARIHI' },
        'BAKIM ESNASINDA KM': { 'BAKIM ESNASINDA KM', 'BAKIM KM', 'KM', 'BAKIMDA KM' },
        'BİR SONRAKİ BAKIM KM': { 'BIR SONRAKI BAKIM KM', 'SONRAKI BAKIM KM', 'SONRAKI KM', 'BIR SONRAKI KM' },
        'YAPILAN İŞLEM': { 'YAPILAN ISLEM', 'YAPILAN İŞLEM', 'ISLEM', 'YAPILANLAR', 'YAPILAN' },
        'DİĞER': { 'DIGER', 'DİGER', 'DİĞER', 'NOT', 'NOTLAR', 'ACIKLAMA', 'AÇIKLAMA' },
        'BAKIMI YAPAN': { 'BAKIMI YAPAN', 'BAKIM YAPAN', 'UYGULAYAN', 'TEKNISYEN', 'TEKNISYEN ADI' }
    }
    # Normalize edilmiş ad -> orijinal ad eşlemesi
    normalized_to_original = { normalize_text(c): c for c in df.columns }
    rename_map = {}
    for target, variants in TARGETS.items():
        for variant in variants:
            key = normalize_text(variant)
            if key in normalized_to_original:
                rename_map[normalized_to_original[key]] = target
                break
    # Yeniden adlandır
    return df.rename(columns=rename_map)

def parse_km(value):
    """Excel'den gelen KM alanlarını güvenli biçimde sayıya çevirir."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        if isinstance(value, (int, float)):
            return int(value)
        # string; nokta/virgül/boşluk temizle
        s = str(value).strip().replace(" ", "").replace(".", "").replace(",", "")
        return int(s) if s else None
    except Exception:
        return None

class DatabaseManager:
    """Veritabanı yönetim sınıfı"""
    
    def __init__(self, db_name="bakim_kayitlari.db"):
        self.db_name = db_name
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Veritabanını başlat ve tabloyu oluştur"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            cursor = self.conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bakimlar (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    s_no INTEGER,
                    plaka TEXT NOT NULL,
                    bolge TEXT,
                    tarih TEXT,
                    bakim_km INTEGER,
                    sonraki_bakim_km INTEGER,
                    yapilan_islem TEXT,
                    diger TEXT,
                    bakim_yapan TEXT,
                    kayit_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Veritabanı hatası: {e}")
            return False
    
    def get_all_records(self):
        """Tüm kayıtları getir"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, s_no, plaka, bolge, tarih, bakim_km, sonraki_bakim_km, 
                       yapilan_islem, diger, bakim_yapan, kayit_tarihi
                FROM bakimlar 
                ORDER BY id DESC
            ''')
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Kayıt getirme hatası: {e}")
            return []
    
    def add_record(self, data):
        """Yeni kayıt ekle"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO bakimlar (s_no, plaka, bolge, tarih, bakim_km, sonraki_bakim_km, 
                                    yapilan_islem, diger, bakim_yapan)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data)
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Kayıt ekleme hatası: {e}")
            return None
    
    def update_record(self, record_id, data):
        """Kayıt güncelle"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE bakimlar 
                SET s_no = ?, plaka = ?, bolge = ?, tarih = ?, bakim_km = ?, 
                    sonraki_bakim_km = ?, yapilan_islem = ?, diger = ?, bakim_yapan = ?
                WHERE id = ?
            ''', data + (record_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kayıt güncelleme hatası: {e}")
            return False
    
    def delete_record(self, record_id):
        """Kayıt sil"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM bakimlar WHERE id = ?", (record_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Kayıt silme hatası: {e}")
            return False
    
    def delete_all(self):
        """Tüm kayıtları sil"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM bakimlar")
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Toplu silme hatası: {e}")
            return False
    
    def search_records(self, plaka):
        """Plaka ile ara"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, s_no, plaka, bolge, tarih, bakim_km, sonraki_bakim_km, 
                       yapilan_islem, diger, bakim_yapan, kayit_tarihi
                FROM bakimlar 
                WHERE plaka LIKE ?
                ORDER BY id DESC
            ''', (f'%{plaka}%',))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Arama hatası: {e}")
            return []
    
    def get_statistics(self):
        """İstatistikleri getir"""
        try:
            cursor = self.conn.cursor()
            
            # Toplam kayıt sayısı
            cursor.execute("SELECT COUNT(*) FROM bakimlar")
            toplam_kayit = cursor.fetchone()[0]
            
            # Toplam araç sayısı
            cursor.execute("SELECT COUNT(DISTINCT plaka) FROM bakimlar")
            toplam_arac = cursor.fetchone()[0]
            
            # En çok bakım yapılan araç
            cursor.execute('''
                SELECT plaka, COUNT(*) as bakim_sayisi 
                FROM bakimlar 
                GROUP BY plaka 
                ORDER BY bakim_sayisi DESC 
                LIMIT 1
            ''')
            en_cok_bakim = cursor.fetchone()
            
            # En son bakım tarihi
            cursor.execute("SELECT MAX(tarih) FROM bakimlar WHERE tarih IS NOT NULL")
            son_bakim = cursor.fetchone()[0]
            
            return {
                'toplam_kayit': toplam_kayit,
                'toplam_arac': toplam_arac,
                'en_cok_bakim': en_cok_bakim,
                'son_bakim': son_bakim
            }
        except sqlite3.Error as e:
            print(f"İstatistik hatası: {e}")
            return {}

class ModernTableWidget(QTableWidget):
    """Modern tablo widget'ı"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Tablo arayüzünü ayarla"""
        # Tablo ayarları
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setSortingEnabled(True)
        
        # Sütun başlıkları
        headers = [
            "ID", "PLAKA", "BÖLGE", "TARİH", 
            "BAKIM KM", "SONRAKI KM", "YAPILAN İŞLEM", "BAKIM YAPAN"
        ]
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        
        # Sütun genişlikleri
        header = self.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # PLAKA
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # BÖLGE
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # TARİH
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # BAKIM KM
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # SONRAKI KM
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # YAPILAN İŞLEM
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # BAKIM YAPAN
        
        self.setColumnWidth(0, 50)   # ID
        
        # Satır yüksekliği
        self.verticalHeader().setDefaultSectionSize(35)
        # ID sütununu gizle (tabloya yine yazacağız, seçimlerde kullanacağız)
        self.setColumnHidden(0, True)
        
        # Stil (Excel benzeri, koyu temayla uyumlu)
        self.setStyleSheet("""
            QTableWidget {
                gridline-color: #cfcfcf;
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
                selection-background-color: #0078d4;
                selection-color: #ffffff;
                border: 1px solid #cfcfcf;
                border-radius: 6px;
                color: #222;
            }
            QTableWidget::item { padding: 6px; border: none; }
            QHeaderView::section {
                background-color: #f1f1f1;
                padding: 8px;
                border: 1px solid #d7d7d7;
                font-weight: bold;
                color: #222;
            }
        """)

class RecordDialog(QDialog):
    """Kayıt ekleme/düzenleme dialog'u"""
    
    def __init__(self, parent=None, record_data=None):
        super().__init__(parent)
        self.record_data = record_data
        self.setup_ui()
        
        if record_data:
            self.load_data()
    
    def setup_ui(self):
        """Dialog arayüzünü ayarla"""
        self.setWindowTitle("Kayıt Ekle/Düzenle" if not self.record_data else "Kayıt Düzenle")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Sıra No
        self.s_no_spin = QSpinBox()
        self.s_no_spin.setRange(1, 9999)
        self.s_no_spin.setValue(1)
        form_layout.addRow("Sıra No:", self.s_no_spin)
        
        # Plaka
        self.plaka_edit = QLineEdit()
        self.plaka_edit.setPlaceholderText("Örn: 06 ABC 123")
        form_layout.addRow("Plaka *:", self.plaka_edit)
        
        # Bölge
        self.bolge_edit = QLineEdit()
        self.bolge_edit.setPlaceholderText("Örn: KARAKÖY")
        form_layout.addRow("Bölge:", self.bolge_edit)
        
        # Tarih
        self.tarih_edit = QDateEdit()
        self.tarih_edit.setDate(QDate.currentDate())
        self.tarih_edit.setCalendarPopup(True)
        self.tarih_edit.setDisplayFormat("dd.MM.yyyy")
        form_layout.addRow("Tarih:", self.tarih_edit)
        
        # Bakım KM
        self.bakim_km_spin = QSpinBox()
        self.bakim_km_spin.setRange(0, 9999999)
        self.bakim_km_spin.setValue(0)
        form_layout.addRow("Bakım Esnasında KM:", self.bakim_km_spin)
        
        # Sonraki Bakım KM
        self.sonraki_km_spin = QSpinBox()
        self.sonraki_km_spin.setRange(0, 9999999)
        self.sonraki_km_spin.setValue(0)
        form_layout.addRow("Bir Sonraki Bakım KM:", self.sonraki_km_spin)
        
        # Yapılan İşlem
        self.yapilan_islem_edit = QTextEdit()
        self.yapilan_islem_edit.setMaximumHeight(100)
        self.yapilan_islem_edit.setPlaceholderText("Yapılan işlemleri yazın...")
        form_layout.addRow("Yapılan İşlem:", self.yapilan_islem_edit)
        
        # Diğer
        self.diger_edit = QLineEdit()
        self.diger_edit.setPlaceholderText("Diğer notlar...")
        form_layout.addRow("Diğer:", self.diger_edit)
        
        # Bakım Yapan
        self.bakim_yapan_edit = QLineEdit()
        self.bakim_yapan_edit.setPlaceholderText("Örn: YUNUS AFŞİN")
        form_layout.addRow("Bakımı Yapan:", self.bakim_yapan_edit)
        
        layout.addLayout(form_layout)
        
        # Butonlar
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
        
        # Stil
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
            QLineEdit, QSpinBox, QDateEdit, QTextEdit {
                padding: 8px;
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus, QSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #0078d4;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
    
    def load_data(self):
        """Mevcut veriyi yükle"""
        if not self.record_data:
            return
        
        data = self.record_data
        self.s_no_spin.setValue(data[1] or 1)
        self.plaka_edit.setText(data[2] or "")
        self.bolge_edit.setText(data[3] or "")
        
        if data[4]:
            try:
                date = QDate.fromString(data[4], "dd.MM.yyyy")
                self.tarih_edit.setDate(date)
            except:
                pass
        
        self.bakim_km_spin.setValue(data[5] or 0)
        self.sonraki_km_spin.setValue(data[6] or 0)
        self.yapilan_islem_edit.setPlainText(data[7] or "")
        self.diger_edit.setText(data[8] or "")
        self.bakim_yapan_edit.setText(data[9] or "")
    
    def get_data(self):
        """Form verilerini al"""
        tarih = self.tarih_edit.date().toString("dd.MM.yyyy")
        
        return (
            self.s_no_spin.value() if self.s_no_spin.value() > 0 else None,
            self.plaka_edit.text().strip(),
            self.bolge_edit.text().strip() or None,
            tarih,
            self.bakim_km_spin.value() if self.bakim_km_spin.value() > 0 else None,
            self.sonraki_km_spin.value() if self.sonraki_km_spin.value() > 0 else None,
            self.yapilan_islem_edit.toPlainText().strip() or None,
            self.diger_edit.text().strip() or None,
            self.bakim_yapan_edit.text().strip() or None
        )

class MainWindow(QMainWindow):
    """Ana pencere"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Ana pencere arayüzünü ayarla"""
        self.setWindowTitle("🚗 Öztaç Petrol A.Ş. Araç Bakım Kayıtları Yönetim Sistemi")
        self.setGeometry(100, 100, 1400, 800)
        
        # Merkez widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Ana layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Üst toolbar
        self.create_toolbar(main_layout)
        
        # Ana içerik (sidebar kaldırıldı)
        content_layout = QHBoxLayout()
        
        # Sol panel kaldırıldı (eski sidebar)
        
        # Sağ panel - Sekmeler (Kayıtlar + Dashboard)
        right_tabs = QTabWidget()
        right_tabs.setTabPosition(QTabWidget.TabPosition.North)
        right_tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333; } 
            QTabBar::tab { background: #2b2b2b; color: #e6e6e6; padding: 8px 16px; margin-right: 2px; }
            QTabBar::tab:selected { background: #3a3a3a; }
        """)
        # Kayıtlar sekmesi
        records_panel = self.create_right_panel()
        right_tabs.addTab(records_panel, "Kayıtlar")
        # Dashboard sekmesi
        dashboard_panel = self.create_dashboard_panel()
        right_tabs.addTab(dashboard_panel, "Dashboard")
        content_layout.addWidget(right_tabs, 3)
        
        main_layout.addLayout(content_layout)
        
        # Footer ekle
        footer = self.create_footer()
        main_layout.addWidget(footer)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Hazır")
        
        # Stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #e1e5e9;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #0078d4;
            }
        """)
        
        # Varsayılan: Karanlık tema uygula
        self.apply_dark_theme()
        
        # Sidebar'ı modernleştir: kart benzeri görünüm
        self.sidebar_style = """
            QGroupBox#Kontroller {
                background: white;
                border: none;
            }
        """
    
    def create_toolbar(self, layout):
        """Üst toolbar oluştur"""
        toolbar_frame = QFrame()
        toolbar_frame.setFrameStyle(QFrame.Shape.Box)
        # Light theme with gradient
        toolbar_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #e9f0ff);
                border: 1px solid #cfd8e3;
                border-radius: 10px;
                margin: 6px;
            }
        """)
        
        toolbar_layout = QHBoxLayout()
        toolbar_frame.setLayout(toolbar_layout)
        
        # Başlık
        title_label = QLabel("🚗 Araç Bakım Kayıtları Yönetim Sistemi")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 22px;
                font-weight: 800;
                color: #1a2b49;
                padding: 10px;
            }
        """)
        toolbar_layout.addWidget(title_label)
        
        # Orta kısımda arama
        search_wrap = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Plaka ile ara...")
        self.search_edit.textChanged.connect(self.search_records)
        self.search_edit.setFixedWidth(320)
        self.search_edit.setStyleSheet("QLineEdit{padding:8px 12px;border:1px solid #cfd8e3;border-radius:8px;background:#ffffff}")
        search_wrap.addWidget(self.search_edit)
        toolbar_layout.addLayout(search_wrap)
        toolbar_layout.addStretch()
        
        # Karanlık mod: varsayılan uygulanacak, buton kaldırıldı
        
        # Yeni kayıt butonu
        top_add_btn = QPushButton("➕ Yeni Kayıt")
        top_add_btn.clicked.connect(self.add_record)
        toolbar_layout.addWidget(top_add_btn)
        
        # Tümünü sil butonu
        wipe_btn = QPushButton("🗑️ Tümünü Sil")
        wipe_btn.clicked.connect(self.delete_all_records)
        toolbar_layout.addWidget(wipe_btn)
        
        # Yenile butonu
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(self.load_data)
        toolbar_layout.addWidget(refresh_btn)
        
        # Excel import butonu
        import_btn = QPushButton("📁 Excel İçe Aktar")
        import_btn.clicked.connect(self.import_excel)
        toolbar_layout.addWidget(import_btn)

        # Light button style
        for btn in [top_add_btn, wipe_btn, refresh_btn, import_btn]:
            btn.setStyleSheet("""
                QPushButton{background:#1a73e8;color:#fff;border:none;padding:8px 12px;border-radius:8px;}
                QPushButton:hover{background:#1765c1}
            """)
        
        layout.addWidget(toolbar_frame)
        
    def create_footer(self):
        """Sağ altta tıklanabilir footer"""
        frame = QFrame()
        h = QHBoxLayout()
        h.addStretch()
        # Toplam kayıt rozeti
        self.footer_total = QLabel("Toplam kayıt: 0")
        self.footer_total.setStyleSheet('QLabel{padding:6px 10px;color:#1a2b49;background:#ffffff;border:1px solid #cfd8e3;border-radius:6px;}')
        h.addWidget(self.footer_total)
        # Coded by
        label = QLabel(
            '<a style="text-decoration:none;color:#1a73e8;" '
            'href="https://wa.me/905439761400?text=merhaba%20%C5%9Fantiye%20takip%20program%C4%B1ndan%20geliyorum%20bir!">'
            'Coded By Yunus AÇIKGÖZ</a>'
        )
        label.setOpenExternalLinks(True)
        label.setStyleSheet('QLabel{padding:6px 10px;color:#1a73e8;background:#ffffff;border:1px solid #cfd8e3;border-radius:6px; margin-left:8px;}')
        h.addWidget(label)
        frame.setLayout(h)
        frame.setStyleSheet('QFrame{background:transparent;}')
        return frame
    
    def create_left_panel(self):
        """Sol panel oluştur"""
        panel = QGroupBox("Kontroller")
        panel.setObjectName("Kontroller")
        layout = QVBoxLayout()
        
        # Arama grubu
        search_group = QGroupBox("Arama")
        search_layout = QVBoxLayout()
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Plaka ile ara...")
        self.search_edit.textChanged.connect(self.search_records)
        search_layout.addWidget(self.search_edit)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # İşlemler grubu
        actions_group = QGroupBox("İşlemler")
        actions_layout = QVBoxLayout()
        
        # Yeni kayıt butonu
        add_btn = QPushButton("➕ Yeni Kayıt Ekle")
        add_btn.clicked.connect(self.add_record)
        actions_layout.addWidget(add_btn)
        
        # Tümünü sil butonu (sidebar)
        wipe_btn_side = QPushButton("🗑️ Tüm Kayıtları Sil")
        wipe_btn_side.clicked.connect(self.delete_all_records)
        wipe_btn_side.setObjectName("danger")
        actions_layout.addWidget(wipe_btn_side)
        
        # Düzenle butonu
        edit_btn = QPushButton("✏️ Kayıt Düzenle")
        edit_btn.clicked.connect(self.edit_record)
        actions_layout.addWidget(edit_btn)
        
        # Sil butonu
        delete_btn = QPushButton("🗑️ Kayıt Sil")
        delete_btn.clicked.connect(self.delete_record)
        actions_layout.addWidget(delete_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        # İstatistikler grubu
        stats_group = QGroupBox("İstatistikler")
        stats_layout = QVBoxLayout()
        
        self.stats_label = QLabel("İstatistikler yükleniyor...")
        self.stats_label.setWordWrap(True)
        self.stats_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                background-color: #f8f9fa;
                border-radius: 6px;
                font-size: 12px;
            }
        """)
        stats_layout.addWidget(self.stats_label)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        layout.addStretch()
        # Sidebar koyu stil
        panel.setStyleSheet("""
            QGroupBox { color: #e6e6e6; border: 1px solid #333; border-radius: 8px; background:#1f1f1f; }
            QLineEdit { background: #2b2b2b; color: #e6e6e6; border: 1px solid #3a3a3a; }
            QPushButton { background: #2e7d32; color: #ffffff; border: none; padding: 10px; border-radius: 6px; font-weight:600; }
            QPushButton:hover { background: #388e3c; }
            QPushButton#danger { background:#b71c1c; }
            QPushButton#danger:hover { background:#d32f2f; }
            QLabel { color: #e6e6e6; }
        """)
        panel.setLayout(layout)
        return panel
    
    def create_right_panel(self):
        """Sağ panel oluştur"""
        panel = QWidget()
        layout = QVBoxLayout()
        self.table = ModernTableWidget()
        layout.addWidget(self.table)
        panel.setLayout(layout)
        return panel

    def create_dashboard_panel(self):
        """Dashboard paneli"""
        panel = QWidget()
        layout = QVBoxLayout()
        
        # Üstte özet kartlar
        cards = QHBoxLayout()
        self.kpi_total = QLabel("Toplam Kayıt: 0")
        kpi_style = "padding:12px;background:#ffffff;color:#1a2b49;border:1px solid #cfd8e3;border-radius:8px;"
        self.kpi_total.setStyleSheet(kpi_style)
        self.kpi_vehicles = QLabel("Toplam Araç: 0")
        self.kpi_vehicles.setStyleSheet(kpi_style)
        self.kpi_last = QLabel("Son Bakım: -")
        self.kpi_last.setStyleSheet(kpi_style)
        cards.addWidget(self.kpi_total)
        cards.addWidget(self.kpi_vehicles)
        cards.addWidget(self.kpi_last)
        layout.addLayout(cards)
        
        # Bakımı yapan kişilere dair mini tablo
        group = QGroupBox("Bakımı Yapanlar")
        group.setStyleSheet("QGroupBox{color:#1a2b49;border:1px solid #cfd8e3;border-radius:8px;background:#ffffff}")
        g_layout = QVBoxLayout()
        self.person_table = QTableWidget(0, 2)
        self.person_table.setHorizontalHeaderLabels(["Bakım Yapan", "Bakım Sayısı"])
        self.person_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.person_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.person_table.setAlternatingRowColors(True)
        self.person_table.setStyleSheet("QTableWidget{background:#ffffff;color:#1a2b49;alternate-background-color:#f9fbff;border:1px solid #cfd8e3}")
        g_layout.addWidget(self.person_table)
        group.setLayout(g_layout)
        layout.addWidget(group)
        
        panel.setLayout(layout)
        return panel
    
    def load_data(self):
        """Verileri yükle"""
        records = self.db_manager.get_all_records()
        self.populate_table(records)
        self.update_statistics()
        self.status_bar.showMessage(f"Toplam {len(records)} kayıt yüklendi")
        if hasattr(self, 'footer_total'):
            self.footer_total.setText(f"Toplam kayıt: {len(records)}")
    
    def populate_table(self, records):
        """Tabloyu doldur"""
        self.table.setRowCount(len(records))
        # Map: veritabanı kolon indeksleri -> tablo kolon indeksleri
        # DB: (0)id,(1)s_no,(2)plaka,(3)bolge,(4)tarih,(5)bakim_km,(6)sonraki_km,(7)yapilan,(8)diger,(9)bakim_yapan,(10)kayit_tarihi
        # UI: [ID gizli], PLAKA, BÖLGE, TARİH, BAKIM ESNASINDA KM, BİR SONRAKİ BAKIM KM, YAPILAN İŞLEM, DİĞER, BAKIMI YAPAN
        db_to_ui = {2:1, 3:2, 4:3, 5:4, 6:5, 7:6, 8:7, 9:8}
        for row, record in enumerate(records):
            for db_index, ui_col in db_to_ui.items():
                value = record[db_index]
                # KM kolonları: 4 ve 5 (UI)
                if ui_col in (4, 5):
                    numeric = None
                    if isinstance(value, (int, float)):
                        numeric = int(value)
                    else:
                        try:
                            numeric = int(str(value).replace(" ", "").replace(".", "").replace(",", "")) if value not in (None, "", "-") else None
                        except Exception:
                            numeric = None
                    display_value = f"{numeric:,}" if numeric is not None else "-"
                else:
                    display_value = str(value) if value not in (None, "") else "-"
                item = QTableWidgetItem(display_value)
                item.setData(Qt.ItemDataRole.UserRole, record[0])
                self.table.setItem(row, ui_col, item)
    
    def update_statistics(self):
        """İstatistikleri güncelle"""
        stats = self.db_manager.get_statistics()
        
        stats_text = f"""
        📊 Toplam Kayıt: {stats.get('toplam_kayit', 0)}
        🚗 Toplam Araç: {stats.get('toplam_arac', 0)}
        """
        
        if stats.get('en_cok_bakim'):
            stats_text += f"\n🏆 En Çok Bakım: {stats['en_cok_bakim'][0]} ({stats['en_cok_bakim'][1]} bakım)"
        
        if stats.get('son_bakim'):
            stats_text += f"\n📅 Son Bakım: {stats['son_bakim']}"
        
        if hasattr(self, 'stats_label') and self.stats_label is not None:
            self.stats_label.setText(stats_text)
        # Dashboard KPI'ları da güncelle
        if hasattr(self, 'kpi_total'):
            self.kpi_total.setText(f"Toplam Kayıt: {stats.get('toplam_kayit', 0)}")
            self.kpi_vehicles.setText(f"Toplam Araç: {stats.get('toplam_arac', 0)}")
            self.kpi_last.setText(f"Son Bakım: {stats.get('son_bakim') or '-'}")
            # Personel istatistikleri
            try:
                cursor = self.db_manager.conn.cursor()
                cursor.execute("""
                    SELECT COALESCE(bakim_yapan,'-') AS ad, COUNT(*)
                    FROM bakimlar
                    GROUP BY ad
                    ORDER BY COUNT(*) DESC
                    LIMIT 10
                """)
                rows = cursor.fetchall()
                self.person_table.setRowCount(len(rows))
                for r, (ad, sayi) in enumerate(rows):
                    self.person_table.setItem(r, 0, QTableWidgetItem(ad or '-'))
                    self.person_table.setItem(r, 1, QTableWidgetItem(str(sayi)))
            except Exception:
                pass
    
    def search_records(self):
        """Kayıt ara"""
        search_text = self.search_edit.text().strip()
        
        if not search_text:
            self.load_data()
            return
        
        records = self.db_manager.search_records(search_text)
        self.populate_table(records)
        self.status_bar.showMessage(f"'{search_text}' için {len(records)} kayıt bulundu")
    
    def add_record(self):
        """Yeni kayıt ekle"""
        dialog = RecordDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            if not data[1]:  # Plaka boşsa
                QMessageBox.warning(self, "Uyarı", "Plaka alanı zorunludur!")
                return
            
            record_id = self.db_manager.add_record(data)
            if record_id:
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla eklendi!")
                self.load_data()
            else:
                QMessageBox.critical(self, "Hata", "Kayıt eklenirken hata oluştu!")
    
    def edit_record(self):
        """Kayıt düzenle"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen düzenlenecek kaydı seçin!")
            return
        
        # Seçili kaydın ID'sini al
        item = self.table.item(current_row, 0)
        if not item:
            return
        
        record_id = item.data(Qt.ItemDataRole.UserRole)
        
        # Kaydı veritabanından getir
        records = self.db_manager.get_all_records()
        record_data = None
        for record in records:
            if record[0] == record_id:
                record_data = record
                break
        
        if not record_data:
            QMessageBox.critical(self, "Hata", "Kayıt bulunamadı!")
            return
        
        dialog = RecordDialog(self, record_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            
            if not data[1]:  # Plaka boşsa
                QMessageBox.warning(self, "Uyarı", "Plaka alanı zorunludur!")
                return
            
            if self.db_manager.update_record(record_id, data):
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla güncellendi!")
                self.load_data()
            else:
                QMessageBox.critical(self, "Hata", "Kayıt güncellenirken hata oluştu!")
    
    def delete_record(self):
        """Kayıt sil"""
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen silinecek kaydı seçin!")
            return
        
        # Seçili kaydın ID'sini al
        item = self.table.item(current_row, 0)
        if not item:
            return
        
        record_id = item.data(Qt.ItemDataRole.UserRole)
        
        # Onay al
        reply = QMessageBox.question(
            self, "Onay", 
            "Bu kaydı silmek istediğinizden emin misiniz?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db_manager.delete_record(record_id):
                QMessageBox.information(self, "Başarılı", "Kayıt başarıyla silindi!")
                self.load_data()
            else:
                QMessageBox.critical(self, "Hata", "Kayıt silinirken hata oluştu!")
    
    def delete_all_records(self):
        """Tüm kayıtları sil"""
        reply = QMessageBox.question(
            self, "Onay",
            "Tüm kayıtları silmek üzeresiniz. Bu işlem geri alınamaz. Devam edilsin mi?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        if self.db_manager.delete_all():
            QMessageBox.information(self, "Başarılı", "Tüm kayıtlar silindi!")
            self.load_data()
        else:
            QMessageBox.critical(self, "Hata", "Toplu silme sırasında hata oluştu!")
    
    def import_excel(self):
        """Excel dosyasından veri aktar"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Excel Dosyası Seç", "", "Excel Dosyaları (*.xlsx *.xls)"
        )
        
        if not file_path:
            return
        
        try:
            # Excel dosyasını oku (engine otomatik)
            try:
                df = pd.read_excel(file_path, engine='openpyxl')
            except Exception:
                # openpyxl başarısız olursa varsayılan engine ile dene
                df = pd.read_excel(file_path)
            # Sütunları normalize et ve olabildiğince eşleştir
            df = normalize_columns(df)
            
            # Zorunlu sütunlar (minimum)
            required_min = ['PLAKA']
            missing_min = [col for col in required_min if col not in df.columns]
            if missing_min:
                QMessageBox.critical(
                    self, "Hata",
                    "Excel dosyasında zorunlu sütun bulunamadı: PLAKA\n"
                    "Lütfen dosya başlıklarını kontrol edin."
                )
                return
            
            # Opsiyonel sütunlar için yoksa oluştur
            optional_cols = ['S.NO','BÖLGE','TARİH','BAKIM ESNASINDA KM','BİR SONRAKİ BAKIM KM',
                             'YAPILAN İŞLEM','DİĞER','BAKIMI YAPAN']
            for col in optional_cols:
                if col not in df.columns:
                    df[col] = None
            
            # Verileri aktar
            success_count = 0
            for index, row in df.iterrows():
                if pd.isna(row['PLAKA']):
                    continue
                
                # Tarih formatını düzelt
                tarih = row['TARİH'] if 'TARİH' in df.columns else None
                if pd.notna(tarih):
                    if isinstance(tarih, str):
                        try:
                            datetime.strptime(tarih, '%d.%m.%Y')
                        except ValueError:
                            try:
                                tarih = pd.to_datetime(tarih).strftime('%d.%m.%Y')
                            except:
                                tarih = None
                    else:
                        tarih = tarih.strftime('%d.%m.%Y')
                
                # KM değerlerini temizle (dayanıklı parser)
                bakim_km = parse_km(row['BAKIM ESNASINDA KM']) if 'BAKIM ESNASINDA KM' in df.columns else None
                sonraki_bakim_km = parse_km(row['BİR SONRAKİ BAKIM KM']) if 'BİR SONRAKİ BAKIM KM' in df.columns else None
                
                # Veritabanına ekle
                data = (
                    None,  # Excel'den gelen S.NO'yu kullanmıyoruz, uygulama kendi s_no alanını yönetebilir
                    str(row['PLAKA']),
                    str(row['BÖLGE']) if 'BÖLGE' in df.columns and pd.notna(row['BÖLGE']) else None,
                    tarih,
                    bakim_km,
                    sonraki_bakim_km,
                    str(row['YAPILAN İŞLEM']) if 'YAPILAN İŞLEM' in df.columns and pd.notna(row['YAPILAN İŞLEM']) else None,
                    str(row['DİĞER']) if 'DİĞER' in df.columns and pd.notna(row['DİĞER']) else None,
                    str(row['BAKIMI YAPAN']) if 'BAKIMI YAPAN' in df.columns and pd.notna(row['BAKIMI YAPAN']) else None
                )
                
                if self.db_manager.add_record(data):
                    success_count += 1
            
            QMessageBox.information(
                self, "Başarılı", 
                f"{success_count} kayıt başarıyla aktarıldı!"
            )
            self.load_data()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Excel aktarım hatası: {str(e)}\n\n"
                                         "Lütfen dosyada hücre birleştirmesi/özel biçim olup olmadığını kontrol edin.")

    def apply_dark_theme(self):
        """Uygulamaya koyu tema uygula (varsayılan)."""
        # Koyu palet
        palette = self.palette()
        palette.setColor(self.backgroundRole(), QColor(30, 30, 30))
        palette.setColor(self.foregroundRole(), QColor(230, 230, 230))
        palette.setColor(QPalette.ColorRole.Window, QColor(30,30,30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(230,230,230))
        palette.setColor(QPalette.ColorRole.Base, QColor(33,33,33))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(38,38,38))
        palette.setColor(QPalette.ColorRole.Text, QColor(230,230,230))
        palette.setColor(QPalette.ColorRole.Button, QColor(45,45,45))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(230,230,230))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(0,120,212))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(255,255,255))
        self.setPalette(palette)
        # Koyu QSS
        # Uygulamayı aydınlık temaya döndür (dark kaldırıldı)
        self.setPalette(QApplication.instance().palette())
        self.setStyleSheet("""
            QMainWindow { background: #f6f9ff; }
            QGroupBox { border: 1px solid #cfd8e3; color: #1a2b49; background:#ffffff; border-radius:10px; }
            QLabel { color: #1a2b49; }
            QLineEdit { background: #ffffff; color: #1a2b49; border: 1px solid #cfd8e3; border-radius:8px; }
            QLineEdit:focus { border-color: #1a73e8; }
            QPushButton { background-color: #1a73e8; color: #ffffff; border-radius: 8px; }
            QPushButton:hover { background-color: #1765c1; }
            QTableWidget { background: #ffffff; alternate-background-color: #f9fbff; color: #1a2b49; border: 1px solid #cfd8e3; }
            QHeaderView::section { background: #eef3ff; color: #1a2b49; border: 1px solid #cfd8e3; }
        """)

def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    
    # Uygulama ayarları
    app.setApplicationName("Araç Bakım Kayıtları Yönetim Sistemi")
    app.setApplicationVersion("1.0")
    
    # Ana pencere
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()


