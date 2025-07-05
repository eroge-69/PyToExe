import sys
import time
import webbrowser
import random
import os
import threading
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QGridLayout, QLabel, QPushButton, 
                             QLineEdit, QTextEdit, QProgressBar, QFrame, 
                             QCheckBox, QComboBox, QFileDialog, QMessageBox,
                             QScrollArea, QSplitter, QInputDialog)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWebEngineWidgets import QWebEngineView

# Browser modülleri - öncelik sırasına göre
BROWSER_TYPE = "none"
browser_module = None

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    BROWSER_TYPE = "qtwebengine"
    browser_module = QWebEngineView
    print("✓ QWebEngineView modülü bulundu!")
except ImportError:
    try:
        from tkinterweb import HtmlFrame
        BROWSER_TYPE = "tkinterweb"
        browser_module = HtmlFrame
        print("✓ TkinterWeb modülü bulundu!")
    except ImportError:
        try:
            from cefpython3 import cefpython as cef
            BROWSER_TYPE = "cefpython"
            browser_module = cef
            print("✓ CEFPython modülü bulundu!")
        except ImportError:
            try:
                import webview
                BROWSER_TYPE = "webview"
                browser_module = webview
                print("✓ WebView modülü bulundu!")
            except ImportError:
                print("⚠️ Hiçbir browser modülü bulunamadı!")
                print("Şunlardan birini yükleyin:")
                print("• pip install PyQt6-WebEngine")
                print("• pip install tkinterweb")
                print("• pip install cefpython3")
                print("• pip install webview")
                BROWSER_TYPE = "fallback"

class LoadingThread(QThread):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
    def run(self):
        for i in range(101):
            self.progress_updated.emit(i)
            self.msleep(10)  # 10ms sleep
        self.finished.emit()

class NumberGenerationThread(QThread):
    finished = pyqtSignal(list)
    progress_updated = pyqtSignal(int)
    
    def __init__(self, quantity, prefixes):
        super().__init__()
        self.quantity = quantity
        self.prefixes = prefixes
        
    def run(self):
        numbers = []
        for i in range(self.quantity):
            prefisso = random.choice(self.prefixes)
            numero = "+39" + prefisso + ''.join(random.choice('0123456789') for _ in range(7))
            numbers.append(numero)
            
            # Progress güncelleme
            if i % max(1, self.quantity // 100) == 0:  # Her %1'de güncelle
                progress = int((i + 1) * 100 / self.quantity)
                self.progress_updated.emit(progress)
                
            # CPU'ya biraz nefes alma süresi ver
            if i % 1000 == 0:
                self.msleep(1)
        
        self.progress_updated.emit(100)
        self.finished.emit(numbers)

class GeneratoreNumeriItaliani(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VALIDATORE DI NUMERI Italiani V5.0")
        self.setGeometry(100, 100, 1100, 750)  # Boyut küçültüldü
        
        # Variabili globali
        self.numeri_generati = []
        self.email_caricati = []
        self.password_caricate = []
        self.proxy_caricati = []
        self.current_url = None
        self.browser_widget = None
        
        # Prefissi telefonici italiani
        self.prefissi_italiani = [
            "320", "324", "327", "328", "329",
            "330", "333", "334", "335", "336", "337", "338", "339",
            "340", "341", "342", "343", "344", "345", "346", "347", "348", "349",
            "350", "351", "352", "353", "354", "355", "356", "357", "358", "359",
            "360", "366", "368", "370", "373", "377", "380", "383", "388", "389",
            "390", "391", "392", "393", "394", "395", "396", "397", "398", "399"
        ]
        
        # Banka URL'leri
        self.bank_urls = {
            "UniCredit": "https://www.unicredit.it/it/privati.html", 
            "Bper": "https://www.bper.it/",
            "Credit Agricol": "https://www.credit-agricole.it/"
        }
        
        self.setup_styles()
        self.init_ui()
        
    def setup_styles(self):
        # Dark theme setup
        self.setStyleSheet("""
            QMainWindow {
                background-color: #171c28;
                color: white;
            }
            QWidget {
                background-color: #171c28;
                color: white;
            }
            QLabel {
                color: white;
                background-color: transparent;
            }
            QPushButton {
                background-color: #4f46e5;
                color: white;
                border: none;
                padding: 8px 15px;
                font-weight: bold;
                border-radius: 4px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4338ca;
            }
            QPushButton:pressed {
                background-color: #3730a3;
            }
            QLineEdit {
                background-color: #1a1f32;
                color: white;
                border: 1px solid #374151;
                padding: 6px;
                border-radius: 3px;
                font-size: 11px;
            }
            QTextEdit {
                background-color: #1f2937;
                color: #f3f4f6;
                border: 1px solid #374151;
                border-radius: 3px;
                padding: 8px;
                font-family: 'Consolas', monospace;
                font-size: 10px;
            }
            QComboBox {
                background-color: #1a1f32;
                color: white;
                border: 1px solid #374151;
                padding: 6px;
                border-radius: 3px;
                font-size: 11px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid white;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
                font-size: 11px;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
                border: 2px solid #374151;
                border-radius: 2px;
                background-color: #1a1f32;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border-color: #6366f1;
            }
            QProgressBar {
                background-color: #0f111a;
                border: none;
                border-radius: 5px;
                text-align: center;
                color: white;
                height: 12px;
                font-size: 10px;
            }
            QProgressBar::chunk {
                background-color: #6366f1;
                border-radius: 5px;
            }
            QFrame {
                background-color: #111827;
                border-radius: 6px;
            }
        """)
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 3, 10, 3)  # Üst ve alt boşluk azaltıldı (8'den 3'e)
        main_layout.setSpacing(3)  # 8'den 3'e azaltıldı
        
        # Title section
        self.create_title_section(main_layout)
        
        # Progress section
        self.create_progress_section(main_layout)
        
        # Content area with splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left column
        left_widget = QWidget()
        left_widget.setFixedWidth(300)  # Azaltıldı
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(5)  # 8'den 5'e azaltıldı
        
        self.create_generator_section(left_layout)
        self.create_upload_section(left_layout)
        self.create_proxy_section(left_layout)
        
        left_layout.addStretch()
        content_splitter.addWidget(left_widget)
        
        # Middle column
        middle_widget = QWidget()
        middle_widget.setFixedWidth(300)  # Azaltıldı
        middle_layout = QVBoxLayout(middle_widget)
        middle_layout.setSpacing(5)  # 8'den 5'e azaltıldı
        
        self.create_display_section(middle_layout)
        self.create_action_section(middle_layout)
        
        middle_layout.addStretch()
        content_splitter.addWidget(middle_widget)
        
        # Right column - Browser
        right_widget = QWidget()
        right_widget.setFixedWidth(550)  # 500'den 550'ye artırıldı
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(3)  # 5'ten 3'e azaltıldı
        
        self.create_browser_section(right_layout)
        content_splitter.addWidget(right_widget)
        
        # Set splitter proportions
        content_splitter.setSizes([300, 300, 550])  # Browser genişliği güncellendi
        
        # Footer
        self.create_footer(main_layout)
        
    def create_title_section(self, parent_layout):
        title_frame = QFrame()
        title_frame.setStyleSheet("QFrame { background-color: transparent; }")
        title_layout = QHBoxLayout(title_frame)
        title_layout.setContentsMargins(0, 0, 0, 0)  # Tamamen kaldırıldı
        
        title_label = QLabel("VALIDATORE DI NUMERI ITALIANO")
        title_label.setFont(QFont("Montserrat", 18, QFont.Weight.Bold))  # Font boyutu azaltıldı
        title_label.setStyleSheet("color: #6366f1;")
        title_layout.addWidget(title_label)
        
        version_label = QLabel("v5.0")
        version_label.setFont(QFont("Montserrat", 10))  # Font boyutu azaltıldı
        version_label.setStyleSheet("color: #64748b; margin-top: 5px;")
        title_layout.addWidget(version_label)
        
        title_layout.addStretch()
        parent_layout.addWidget(title_frame)
        
    def create_progress_section(self, parent_layout):
        self.header_frame = QFrame()
        self.header_frame.setFixedHeight(45)  # 50'den 45'e azaltıldı
        self.header_frame.setStyleSheet("QFrame { background-color: #111827; border-radius: 6px; }")
        
        header_layout = QVBoxLayout(self.header_frame)
        header_layout.setContentsMargins(12, 5, 12, 5)  # Üst ve alt boşluk azaltıldı (8'den 5'e)
        header_layout.setSpacing(3)  # 5'ten 3'e azaltıldı
        
        # Status section
        status_layout = QHBoxLayout()
        
        self.progress_label = QLabel("PRONTO")
        self.progress_label.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))  # Font boyutu azaltıldı
        self.progress_label.setStyleSheet("color: #10b981;")
        status_layout.addWidget(self.progress_label)
        
        status_layout.addStretch()
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setFont(QFont("Montserrat", 11))  # Font boyutu azaltıldı
        self.percentage_label.setStyleSheet("color: #f3f4f6;")
        status_layout.addWidget(self.percentage_label)
        
        header_layout.addLayout(status_layout)
        
        # Progress bar
        self.loading_bar = QProgressBar()
        self.loading_bar.setRange(0, 100)
        self.loading_bar.setValue(0)
        header_layout.addWidget(self.loading_bar)
        
        parent_layout.addWidget(self.header_frame)
        
    def create_section_frame(self, parent_layout, title, content_function):
        section_frame = QFrame()
        section_frame.setStyleSheet("QFrame { background-color: #111827; border-radius: 6px; padding: 8px; }")
        
        section_layout = QVBoxLayout(section_frame)
        section_layout.setContentsMargins(10, 6, 10, 6)  # 8'den 6'ya azaltıldı
        section_layout.setSpacing(4)  # 6'dan 4'e azaltıldı
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Montserrat", 12, QFont.Weight.Bold))  # Font boyutu azaltıldı
        title_label.setStyleSheet("color: #f3f4f6;")
        section_layout.addWidget(title_label)
        
        # Separator
        separator = QFrame()
        separator.setFixedHeight(1)  # Azaltıldı
        separator.setStyleSheet("QFrame { background-color: #1f2937; border: none; }")
        section_layout.addWidget(separator)
        
        # Content
        content_function(section_layout)
        
        parent_layout.addWidget(section_frame)
        return section_frame
        
    def create_generator_section(self, parent_layout):
        def add_generator_content(layout):
            # Quantity input
            quantity_layout = QHBoxLayout()
            quantity_layout.setSpacing(6)  # Azaltıldı
            
            quantity_label = QLabel("Quantità:")
            quantity_label.setFont(QFont("Montserrat", 10))  # Font boyutu azaltıldı
            quantity_label.setStyleSheet("color: #e5e7eb;")
            quantity_layout.addWidget(quantity_label)
            
            self.quantity_entry = QLineEdit("1000")
            self.quantity_entry.setFixedWidth(80)  # Azaltıldı
            self.quantity_entry.setFont(QFont("Montserrat", 10))
            quantity_layout.addWidget(self.quantity_entry)
            
            quantity_layout.addStretch()
            layout.addLayout(quantity_layout)
            
            # Generate button
            generate_button = QPushButton("GENERA NUMERI")
            generate_button.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            generate_button.clicked.connect(self.generate_numbers)
            layout.addWidget(generate_button)
            
        self.create_section_frame(parent_layout, "Generazione Numeri", add_generator_content)
        
    def create_upload_section(self, parent_layout):
        def add_upload_content(layout):
            upload_numbers_btn = QPushButton("Carica Numeri")
            upload_numbers_btn.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
            upload_numbers_btn.clicked.connect(self.upload_numbers)
            layout.addWidget(upload_numbers_btn)
            
        self.create_section_frame(parent_layout, "Carica Dati", add_upload_content)
        
    def create_display_section(self, parent_layout):
        def add_display_content(layout):
            # Headers layout
            headers_layout = QHBoxLayout()
            headers_layout.setSpacing(0)
            
            # Status label (left)
            status_label = QLabel("Status")
            status_label.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            status_label.setStyleSheet("color: #ef4444; background-color: transparent;")
            status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            headers_layout.addWidget(status_label)
            
            # Numbers label (right)
            numbers_label = QLabel("Numbers")
            numbers_label.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            numbers_label.setStyleSheet("color: #10b981; background-color: transparent;")
            numbers_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            headers_layout.addWidget(numbers_label)
            
            layout.addLayout(headers_layout)
            
            # Single display area with special formatting
            self.numbers_display = QTextEdit()
            self.numbers_display.setFont(QFont("Consolas", 12))
            self.numbers_display.setMinimumHeight(320)
            # Set tab stops for proper alignment
            from PyQt6.QtGui import QFontMetrics
            font_metrics = QFontMetrics(QFont("Consolas", 12))
            tab_width = font_metrics.horizontalAdvance(" " * 30)  # 30 character width
            self.numbers_display.setTabStopDistance(tab_width)
            layout.addWidget(self.numbers_display)
            
        self.create_section_frame(parent_layout, "Dati Caricati", add_display_content)
        
    def create_proxy_section(self, parent_layout):
        def add_proxy_content(layout):
            # Proxy options
            options_layout = QGridLayout()
            options_layout.setSpacing(6)  # Azaltıldı
            
            self.proxy_checkbox = QCheckBox("Proxy")
            self.proxy_checkbox.toggled.connect(self.toggle_proxies)
            options_layout.addWidget(self.proxy_checkbox, 0, 0)
            
            without_proxy_checkbox = QCheckBox("Senza Proxy")
            options_layout.addWidget(without_proxy_checkbox, 0, 1)
            
            # Proxy type
            proxy_type_layout = QHBoxLayout()
            proxy_type_label = QLabel("Tipo:")
            proxy_type_label.setFont(QFont("Montserrat", 10))
            proxy_type_label.setStyleSheet("color: #e5e7eb;")
            proxy_type_layout.addWidget(proxy_type_label)
            
            self.proxy_type_combo = QComboBox()
            self.proxy_type_combo.addItems(["HTTP", "SOCKS4", "SOCKS5"])
            self.proxy_type_combo.setCurrentText("HTTP")
            proxy_type_layout.addWidget(self.proxy_type_combo)
            proxy_type_layout.addStretch()
            
            options_layout.addLayout(proxy_type_layout, 1, 0, 1, 2)
            layout.addLayout(options_layout)
            
            # Upload proxy button
            self.upload_proxy_button = QPushButton("Carica Proxy")
            self.upload_proxy_button.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))
            self.upload_proxy_button.clicked.connect(self.upload_proxies)
            self.upload_proxy_button.setVisible(False)
            layout.addWidget(self.upload_proxy_button)
            
            # Bank selection
            bank_label = QLabel("Seleziona Banche:")
            bank_label.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            bank_label.setStyleSheet("color: #e5e7eb; margin-top: 8px;")
            layout.addWidget(bank_label)
            
            bank_layout = QVBoxLayout()
            bank_layout.setSpacing(3)  # Azaltıldı
            
            self.unicredit_checkbox = QCheckBox("UniCredit")
            self.unicredit_checkbox.toggled.connect(self.on_bank_selection)
            bank_layout.addWidget(self.unicredit_checkbox)
            
            self.bper_checkbox = QCheckBox("Bper")
            self.bper_checkbox.toggled.connect(self.on_bank_selection)
            bank_layout.addWidget(self.bper_checkbox)
            
            self.credit_agricol_checkbox = QCheckBox("Credit Agricol")
            self.credit_agricol_checkbox.toggled.connect(self.on_bank_selection)
            bank_layout.addWidget(self.credit_agricol_checkbox)
            
            layout.addLayout(bank_layout)
            
        self.create_section_frame(parent_layout, "Opzioni Proxy", add_proxy_content)
        
    def create_action_section(self, parent_layout):
        def add_action_content(layout):
            button_layout = QGridLayout()
            button_layout.setSpacing(6)  # Azaltıldı
            
            start_button = QPushButton("CONVALIDA")
            start_button.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            start_button.setStyleSheet("""
                QPushButton {
                    background-color: #10b981;
                    padding: 10px 18px;
                }
                QPushButton:hover {
                    background-color: #059669;
                }
            """)
            start_button.clicked.connect(self.start_validation)
            button_layout.addWidget(start_button, 0, 0)
            
            download_button = QPushButton("SCARICA VALIDI")
            download_button.setFont(QFont("Montserrat", 11, QFont.Weight.Bold))
            download_button.setStyleSheet("""
                QPushButton {
                    background-color: #8b5cf6;
                    padding: 10px 18px;
                }
                QPushButton:hover {
                    background-color: #7c3aed;
                }
            """)
            download_button.clicked.connect(self.download_valids)
            button_layout.addWidget(download_button, 0, 1)
            
            layout.addLayout(button_layout)
            
        self.create_section_frame(parent_layout, "Azioni", add_action_content)
        
    def create_browser_section(self, parent_layout):
        browser_frame = QFrame()
        browser_frame.setFixedHeight(570)  # 520'den 570'ye artırıldı
        browser_frame.setStyleSheet("QFrame { background-color: #111827; border-radius: 6px; }")
        
        browser_layout = QVBoxLayout(browser_frame)
        browser_layout.setContentsMargins(4, 2, 4, 2)  # Sağ ve sol boşluk azaltıldı (8'den 4'e)
        browser_layout.setSpacing(1)  # 3'ten 1'e azaltıldı
        
        # Browser area
        self.browser_container = QFrame()
        self.browser_container.setStyleSheet("QFrame { background-color: #1f2937; border: 2px solid #374151; border-radius: 4px; }")
        self.browser_container_layout = QVBoxLayout(self.browser_container)
        self.browser_container_layout.setContentsMargins(1, 1, 1, 1)
        
        self.show_initial_browser_message()
        
        browser_layout.addWidget(self.browser_container)
        parent_layout.addWidget(browser_frame)
        
    def create_footer(self, parent_layout):
        footer_frame = QFrame()
        footer_frame.setFixedHeight(30)  # 35'ten 30'a azaltıldı
        footer_frame.setStyleSheet("QFrame { background-color: #111827; border-radius: 6px; }")
        
        footer_layout = QHBoxLayout(footer_frame)
        footer_layout.setContentsMargins(15, 5, 15, 5)  # 8'den 5'e azaltıldı
        
        version_label = QLabel("© 2025 VALIDATORE DI NUMERI")
        version_label.setFont(QFont("Montserrat", 9))  # Font boyutu azaltıldı
        version_label.setStyleSheet("color: #9ca3af;")
        footer_layout.addWidget(version_label)
        
        footer_layout.addStretch()
        
        telegram_label = QLabel("Telegram: @Nabir25")
        telegram_label.setFont(QFont("Montserrat", 10, QFont.Weight.Bold))  # Font boyutu azaltıldı
        telegram_label.setStyleSheet("color: #6366f1; text-decoration: underline;")
        telegram_label.mousePressEvent = self.open_telegram_link
        telegram_label.setCursor(Qt.CursorShape.PointingHandCursor)
        footer_layout.addWidget(telegram_label)
        
        parent_layout.addWidget(footer_frame)
        
    def show_initial_browser_message(self):
        # Clear previous content
        for i in reversed(range(self.browser_container_layout.count())):
            child = self.browser_container_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        if BROWSER_TYPE == "none":
            message = "❌ Modulo browser non trovato!\n\nInstalla uno di questi:\n• pip install PyQt6-WebEngine\n• pip install tkinterweb\n• pip install cefpython3\n• pip install webview"
            color = "#ef4444"
        else:
            message = f"✓ Browser pronto: {BROWSER_TYPE.upper()}\n\nSeleziona una banca"
            color = "#10b981"
        
        self.browser_message = QLabel(message)
        self.browser_message.setFont(QFont("Montserrat", 10))  # Font boyutu azaltıldı
        self.browser_message.setStyleSheet(f"color: {color}; background-color: transparent;")
        self.browser_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.browser_message.setWordWrap(True)
        self.browser_container_layout.addWidget(self.browser_message)
        
    def on_bank_selection(self):
        # Only allow one bank selection at a time
        sender = self.sender()
        
        if sender == self.unicredit_checkbox and self.unicredit_checkbox.isChecked():
            self.bper_checkbox.setChecked(False)
            self.credit_agricol_checkbox.setChecked(False)
            self.load_bank_website("UniCredit")
        elif sender == self.bper_checkbox and self.bper_checkbox.isChecked():
            self.unicredit_checkbox.setChecked(False)
            self.credit_agricol_checkbox.setChecked(False)
            self.load_bank_website("Bper")
        elif sender == self.credit_agricol_checkbox and self.credit_agricol_checkbox.isChecked():
            self.unicredit_checkbox.setChecked(False)
            self.bper_checkbox.setChecked(False)
            self.load_bank_website("Credit Agricol")
        else:
            # If unchecked, clear browser
            self.clear_browser()
            
    def load_bank_website(self, bank_name):
        if bank_name not in self.bank_urls:
            return
            
        url = self.bank_urls[bank_name]
        self.current_url = url
        
        try:
            # Clear previous browser message
            if hasattr(self, 'browser_message'):
                self.browser_message.deleteLater()
            
            # Clear previous browser widget
            if self.browser_widget:
                self.browser_widget.deleteLater()
                
            # Load based on browser type
            if BROWSER_TYPE == "qtwebengine":
                self.load_with_qtwebengine(url)
            elif BROWSER_TYPE == "tkinterweb":
                self.load_with_embedded_viewer(url, bank_name)
            elif BROWSER_TYPE == "cefpython":
                self.load_with_embedded_viewer(url, bank_name)
            elif BROWSER_TYPE == "webview":
                self.load_with_webview_info(url, bank_name)
            else:
                self.load_with_embedded_viewer(url, bank_name)
                
        except Exception as e:
            print(f"Browser loading error: {e}")
            self.load_with_embedded_viewer(url, bank_name)
            
    def load_with_qtwebengine(self, url):
        try:
            self.browser_widget = QWebEngineView()
            self.browser_widget.load(QUrl(url))
            self.browser_container_layout.addWidget(self.browser_widget)
        except Exception as e:
            print(f"QWebEngineView error: {e}")
            self.load_with_embedded_viewer(url, "Bank Website")
            
    def load_with_webview_info(self, url, bank_name):
        try:
            # Create info widget
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(15, 15, 15, 15)  # Azaltıldı
            info_layout.setSpacing(12)  # Azaltıldı
            
            title_label = QLabel(f"🌐 {bank_name} - WebView")
            title_label.setFont(QFont("Montserrat", 14, QFont.Weight.Bold))  # Font boyutu azaltıldı
            title_label.setStyleSheet("color: #10b981;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(title_label)
            
            url_label = QLabel(url)
            url_label.setFont(QFont("Montserrat", 9))  # Font boyutu azaltıldı
            url_label.setStyleSheet("color: #6366f1;")
            url_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_layout.addWidget(url_label)
            
            info_text = QTextEdit()
            info_text.setFont(QFont("Montserrat", 9))  # Font boyutu azaltıldı
            info_text.setStyleSheet("QTextEdit { background-color: #111827; color: #f3f4f6; }")
            info_text.setPlainText(f"Finestra WebView aperta!\n\n{bank_name} sito web caricato in una finestra separata.\n\nURL: {url}\n\nSe la finestra WebView si chiude, premi il pulsante 'Aggiorna'.")
            info_text.setReadOnly(True)
            info_layout.addWidget(info_text)
            
            # Start WebView in separate thread
            def start_webview():
                try:
                    import webview
                    webview.create_window(f'{bank_name} - Bank Website', url, 
                                         width=900, height=700,
                                         resizable=True,
                                         on_top=False)
                    webview.start(debug=False)
                except Exception as e:
                    print(f"WebView error: {e}")
            
            webview_thread = threading.Thread(target=start_webview, daemon=True)
            webview_thread.start()
            
            self.browser_widget = info_widget
            self.browser_container_layout.addWidget(self.browser_widget)
            
        except Exception as e:
            print(f"WebView info error: {e}")
            self.load_with_embedded_viewer(url, bank_name)
            
    def load_with_embedded_viewer(self, url, bank_name="Bank Website"):
        try:
            # Create scrollable content widget
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setStyleSheet("QScrollArea { background-color: #ffffff; border: none; }")
            
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(0, 0, 0, 0)
            content_layout.setSpacing(0)
            
            # Browser header simulation
            header_frame = QFrame()
            header_frame.setFixedHeight(30)  # Azaltıldı
            header_frame.setStyleSheet("QFrame { background-color: #f8f9fa; }")
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(6, 4, 6, 4)  # Azaltıldı
            
            # Address bar simulation
            address_frame = QFrame()
            address_frame.setStyleSheet("QFrame { background-color: #ffffff; border: 1px solid #ddd; border-radius: 3px; }")
            address_layout = QHBoxLayout(address_frame)
            address_layout.setContentsMargins(5, 3, 5, 3)  # Azaltıldı
            
            lock_label = QLabel("🔒")
            lock_label.setFont(QFont("Arial", 10))  # Font boyutu azaltıldı
            lock_label.setStyleSheet("color: #666; background-color: transparent;")
            address_layout.addWidget(lock_label)
            
            url_display = QLabel(url)
            url_display.setFont(QFont("Arial", 8))  # Font boyutu azaltıldı
            url_display.setStyleSheet("color: #666; background-color: transparent;")
            address_layout.addWidget(url_display)
            address_layout.addStretch()
            
            header_layout.addWidget(address_frame)
            content_layout.addWidget(header_frame)
            
            # Bank-specific content
            if "unicredit" in url.lower() or bank_name == "UniCredit":
                self.create_unicredit_content(content_layout)
            elif "bper" in url.lower() or bank_name == "Bper":
                self.create_bper_content(content_layout)
            elif "credit-agricole" in url.lower() or bank_name == "Credit Agricol":
                self.create_credit_agricole_content(content_layout)
            else:
                self.create_generic_bank_content(content_layout, bank_name, url)
            
            scroll_area.setWidget(content_widget)
            self.browser_widget = scroll_area
            self.browser_container_layout.addWidget(self.browser_widget)
            
        except Exception as e:
            print(f"Embedded viewer error: {e}")
            self.show_error_message(url, str(e))
            
    def create_unicredit_content(self, content_layout):
        # UniCredit header
        header = QFrame()
        header.setFixedHeight(50)  # Azaltıldı
        header.setStyleSheet("QFrame { background-color: #c41e3a; }")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)  # Azaltıldı
        
        logo_label = QLabel("UniCredit")
        logo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Font boyutu azaltıldı
        logo_label.setStyleSheet("color: white; background-color: transparent;")
        header_layout.addWidget(logo_label)
        
        header_layout.addStretch()
        
        login_button = QPushButton("Area Clienti")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #ffffff;
                color: #c41e3a;
                border: none;
                padding: 6px 15px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
        """)
        header_layout.addWidget(login_button)
        
        content_layout.addWidget(header)
        
        # Navigation
        nav = QFrame()
        nav.setFixedHeight(35)  # Azaltıldı
        nav.setStyleSheet("QFrame { background-color: #f8f9fa; }")
        nav_layout = QHBoxLayout(nav)
        nav_layout.setContentsMargins(8, 8, 8, 8)  # Azaltıldı
        
        nav_items = ["Privati", "Imprese", "Corporate", "Investimenti", "Sostenibilità"]
        for item in nav_items:
            nav_btn = QLabel(item)
            nav_btn.setFont(QFont("Arial", 10))  # Font boyutu azaltıldı
            nav_btn.setStyleSheet("color: #333; background-color: transparent; padding: 0 15px;")
            nav_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            nav_layout.addWidget(nav_btn)
        
        nav_layout.addStretch()
        content_layout.addWidget(nav)
        
        # Main content
        main_content = QWidget()
        main_content.setStyleSheet("QWidget { background-color: #ffffff; }")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(25, 20, 25, 20)  # Azaltıldı
        main_layout.setSpacing(20)  # Azaltıldı
        
        # Hero section
        hero_label = QLabel("La tua banca, sempre con te")
        hero_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))  # Font boyutu azaltıldı
        hero_label.setStyleSheet("color: #c41e3a; background-color: transparent;")
        hero_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(hero_label)
        
        # Services grid
        services_widget = QWidget()
        services_layout = QGridLayout(services_widget)
        services_layout.setSpacing(10)  # Azaltıldı
        
        services = [
            ("🏠", "Mutui Casa", "Finanziamenti per la tua casa"),
            ("💳", "Conti e Carte", "Soluzioni di pagamento"),
            ("💰", "Investimenti", "Fai crescere i tuoi risparmi"),
            ("📱", "Digital Banking", "La banca sul tuo smartphone")
        ]
        
        for i, (icon, title, desc) in enumerate(services):
            service_frame = QFrame()
            service_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #ddd; border-radius: 6px; padding: 10px; }")
            service_layout = QVBoxLayout(service_frame)
            service_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            service_layout.setSpacing(5)  # Azaltıldı
            
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 18))  # Font boyutu azaltıldı
            icon_label.setStyleSheet("background-color: transparent;")
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            service_layout.addWidget(icon_label)
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # Font boyutu azaltıldı
            title_label.setStyleSheet("color: #c41e3a; background-color: transparent;")
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            service_layout.addWidget(title_label)
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Arial", 8))  # Font boyutu azaltıldı
            desc_label.setStyleSheet("color: #666; background-color: transparent;")
            desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_label.setWordWrap(True)
            service_layout.addWidget(desc_label)
            
            services_layout.addWidget(service_frame, i // 2, i % 2)
        
        main_layout.addWidget(services_widget)
        main_layout.addStretch()
        content_layout.addWidget(main_content)
        
    def create_bper_content(self, content_layout):
        # BPER header
        header = QFrame()
        header.setFixedHeight(50)  # Azaltıldı
        header.setStyleSheet("QFrame { background-color: #1f4788; }")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)  # Azaltıldı
        
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setSpacing(1)  # Azaltıldı
        
        logo_label = QLabel("BPER")
        logo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Font boyutu azaltıldı
        logo_label.setStyleSheet("color: white; background-color: transparent;")
        logo_layout.addWidget(logo_label)
        
        subtitle = QLabel("Banca Popolare dell'Emilia Romagna")
        subtitle.setFont(QFont("Arial", 8))  # Font boyutu azaltıldı
        subtitle.setStyleSheet("color: white; background-color: transparent;")
        logo_layout.addWidget(subtitle)
        
        header_layout.addWidget(logo_container)
        header_layout.addStretch()
        
        content_layout.addWidget(header)
        
        # Main content
        main_content = QWidget()
        main_content.setStyleSheet("QWidget { background-color: #ffffff; }")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(25, 20, 25, 20)  # Azaltıldı
        main_layout.setSpacing(15)  # Azaltıldı
        
        # Welcome message
        welcome_label = QLabel("Benvenuto in BPER Banca")
        welcome_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Font boyutu azaltıldı
        welcome_label.setStyleSheet("color: #1f4788; background-color: transparent;")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(welcome_label)
        
        # Content sections
        sections = [
            ("Servizi Bancari", "Conti correnti, depositi e servizi di pagamento per privati e imprese"),
            ("Mutui e Finanziamenti", "Soluzioni per l'acquisto della casa e finanziamenti personali"),
            ("Imprese", "Crediti, servizi di tesoreria e soluzioni per le PMI"),
            ("Digital Banking", "Online Banking, App Mobile e pagamenti digitali")
        ]
        
        for title, desc in sections:
            section_frame = QFrame()
            section_frame.setStyleSheet("QFrame { background-color: #f8f9fa; border-radius: 6px; padding: 10px; }")
            section_layout = QVBoxLayout(section_frame)
            section_layout.setSpacing(3)  # Azaltıldı
            
            title_label = QLabel(title)
            title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # Font boyutu azaltıldı
            title_label.setStyleSheet("color: #1f4788; background-color: transparent;")
            section_layout.addWidget(title_label)
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Arial", 9))  # Font boyutu azaltıldı
            desc_label.setStyleSheet("color: #333; background-color: transparent;")
            desc_label.setWordWrap(True)
            section_layout.addWidget(desc_label)
            
            main_layout.addWidget(section_frame)
        
        main_layout.addStretch()
        content_layout.addWidget(main_content)
        
    def create_credit_agricole_content(self, content_layout):
        # Credit Agricole header
        header = QFrame()
        header.setFixedHeight(50)  # Azaltıldı
        header.setStyleSheet("QFrame { background-color: #00a651; }")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)  # Azaltıldı
        
        logo_label = QLabel("Crédit Agricole")
        logo_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))  # Font boyutu azaltıldı
        logo_label.setStyleSheet("color: white; background-color: transparent;")
        header_layout.addWidget(logo_label)
        header_layout.addStretch()
        
        content_layout.addWidget(header)
        
        # Main content
        main_content = QWidget()
        main_content.setStyleSheet("QWidget { background-color: #ffffff; }")
        main_layout = QVBoxLayout(main_content)
        main_layout.setContentsMargins(25, 20, 25, 20)  # Azaltıldı
        main_layout.setSpacing(15)  # Azaltıldı
        
        # Hero section
        hero_label = QLabel("🌱 La banca verde per il tuo futuro")
        hero_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))  # Font boyutu azaltıldı
        hero_label.setStyleSheet("color: #00a651; background-color: transparent;")
        hero_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(hero_label)
        
        # Green services
        green_services = [
            ("Sostenibilità", "Investimenti green e progetti per l'ambiente"),
            ("Prodotti Bancari", "Conti, carte e finanziamenti sostenibili"),
            ("Business Banking", "Soluzioni per imprese attente al'ambiente"),
            ("Digital Green", "Servizi digitali per ridurre l'impatto ambientale")
        ]
        
        for title, desc in green_services:
            service_frame = QFrame()
            service_frame.setStyleSheet("QFrame { background-color: #f0f9f4; border: 1px solid #c6f6d5; border-radius: 6px; padding: 10px; }")
            service_layout = QVBoxLayout(service_frame)
            service_layout.setSpacing(3)  # Azaltıldı
            
            title_label = QLabel(f"🌿 {title}")
            title_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))  # Font boyutu azaltıldı
            title_label.setStyleSheet("color: #00a651; background-color: transparent;")
            service_layout.addWidget(title_label)
            
            desc_label = QLabel(desc)
            desc_label.setFont(QFont("Arial", 9))  # Font boyutu azaltıldı
            desc_label.setStyleSheet("color: #333; background-color: transparent;")
            desc_label.setWordWrap(True)
            service_layout.addWidget(desc_label)
            
            main_layout.addWidget(service_frame)
        
        main_layout.addStretch()
        content_layout.addWidget(main_content)
        
    def create_generic_bank_content(self, content_layout, bank_name, url):
        content_widget = QWidget()
        content_widget.setStyleSheet("QWidget { background-color: white; }")
        content_widget_layout = QVBoxLayout(content_widget)
        content_widget_layout.setContentsMargins(15, 15, 15, 15)  # Azaltıldı
        
        content_text = QTextEdit()
        content_text.setStyleSheet("QTextEdit { background-color: white; color: #333; border: none; }")
        content_text.setFont(QFont("Arial", 10))  # Font boyutu azaltıldı
        
        content = f"""
{bank_name} - Web Banking

URL: {url}

🏦 Servizi Bancari Online

Questa è una simulazione dell'interfaccia web della banca.
Per accedere al sito web reale, utilizza il pulsante "Apri nel Browser Esterno".

Funzionalità Disponibili:
• Visualizzazione saldi e movimenti
• Bonifici e pagamenti
• Ricariche telefoniche
• Investimenti e trading
• Contatti e supporto

Per una migliore esperienza del browser, installa:
• pip install PyQt6-WebEngine (consigliato)
• pip install tkinterweb
• pip install cefpython3
• pip install webview

{bank_name} - Al vostro servizio dal 1800
        """
        
        content_text.setPlainText(content)
        content_text.setReadOnly(True)
        content_widget_layout.addWidget(content_text)
        
        content_layout.addWidget(content_widget)
        
    def show_error_message(self, url, error):
        # Clear previous content
        for i in reversed(range(self.browser_container_layout.count())):
            child = self.browser_container_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        error_label = QLabel(f"❌ Errore caricamento\n\n{url}\n\nErrore: {error}")
        error_label.setFont(QFont("Montserrat", 10))  # Font boyutu azaltıldı
        error_label.setStyleSheet("color: #ef4444; background-color: transparent;")
        error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        error_label.setWordWrap(True)
        self.browser_container_layout.addWidget(error_label)
        
    def clear_browser(self):
        # Clear browser widget
        if self.browser_widget:
            self.browser_widget.deleteLater()
            self.browser_widget = None
        
        # Clear all widgets
        for i in reversed(range(self.browser_container_layout.count())):
            child = self.browser_container_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        # Show initial message
        self.show_initial_browser_message()
        
    def refresh_browser(self):
        selected_bank = None
        
        if self.unicredit_checkbox.isChecked():
            selected_bank = "UniCredit"
        elif self.bper_checkbox.isChecked():
            selected_bank = "Bper"
        elif self.credit_agricol_checkbox.isChecked():
            selected_bank = "Credit Agricol"
        
        if selected_bank:
            self.load_bank_website(selected_bank)
        else:
            self.clear_browser()
            
    def open_in_external_browser(self):
        if self.current_url:
            webbrowser.open(self.current_url)
            QMessageBox.information(self, "Browser Esterno", f"Sito aperto nel browser predefinito:\n{self.current_url}")
        else:
            QMessageBox.warning(self, "Nessun URL", "Seleziona prima una banca!")
            
    def show_loading_bar(self):
        self.progress_label.setText("ELABORAZIONE")
        self.progress_label.setStyleSheet("color: #6366f1;")
        
        self.loading_thread = LoadingThread()
        self.loading_thread.progress_updated.connect(self.update_progress)
        self.loading_thread.finished.connect(self.loading_finished)
        self.loading_thread.start()
        
    def update_progress(self, value):
        self.loading_bar.setValue(value)
        self.percentage_label.setText(f"{value}%")
        
        if value < 100:
            self.progress_label.setStyleSheet("color: #6366f1;")
        else:
            self.progress_label.setStyleSheet("color: #10b981;")
            
    def loading_finished(self):
        self.progress_label.setText("COMPLETATO")
        self.progress_label.setStyleSheet("color: #10b981;")
        self.percentage_label.setText("100%")
        
        # Reset after 2 seconds
        QTimer.singleShot(2000, self.reset_progress_indicators)
        
    def reset_progress_indicators(self):
        self.progress_label.setText("PRONTO")
        self.progress_label.setStyleSheet("color: #10b981;")
        self.percentage_label.setText("0%")
        self.loading_bar.setValue(0)
        
    def generate_numbers(self):
        try:
            quantity = int(self.quantity_entry.text())
            if quantity <= 0:
                QMessageBox.critical(self, "Errore", "Inserisci un numero positivo.")
                return
            
            if quantity > 100000:
                reply = QMessageBox.question(self, "Conferma", 
                    f"Stai per generare {quantity} numeri. Questo potrebbe richiedere tempo. Continuare?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Progress bar'ı başlat
            self.progress_label.setText("GENERAZIONE NUMERI")
            self.progress_label.setStyleSheet("color: #6366f1;")
            self.loading_bar.setValue(0)
            
            # Generate numbers in thread
            self.generation_thread = NumberGenerationThread(quantity, self.prefissi_italiani)
            self.generation_thread.finished.connect(self.numbers_generated)
            self.generation_thread.progress_updated.connect(self.update_progress)
            self.generation_thread.start()
            
        except ValueError:
            QMessageBox.critical(self, "Errore", "Inserisci un numero valido.")
            
    def numbers_generated(self, numbers):
        self.numeri_generati = numbers
        self.update_display_split(self.numeri_generati, "Numeri")
        
        # Progress bar'ı tamamla
        self.progress_label.setText("COMPLETATO")
        self.progress_label.setStyleSheet("color: #10b981;")
        self.loading_bar.setValue(100)
        self.percentage_label.setText("100%")
        
        QMessageBox.information(self, "Info", f"Generati {len(self.numeri_generati)} numeri italiani.")
        
        # 2 saniye sonra reset
        QTimer.singleShot(2000, self.reset_progress_indicators)
        
    def upload_numbers(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Carica Numeri", "", "File di testo (*.txt)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.numeri_generati = file.read().splitlines()
                self.update_display_split(self.numeri_generati, "Numeri")
                QMessageBox.information(self, "Info", f"Caricati {len(self.numeri_generati)} numeri.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile caricare il file: {str(e)}")
                
    def upload_emails(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Carica Email", "", "File di testo (*.txt)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.email_caricati = file.read().splitlines()
                self.update_display_split(self.email_caricati, "Email")
                QMessageBox.information(self, "Info", f"Caricati {len(self.email_caricati)} email.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile caricare il file: {str(e)}")
                
    def update_display_split(self, content_list, label):
        # Clear display
        self.numbers_display.clear()
        
        # Create formatted lines with HTML coloring
        displayed_count = min(100, len(content_list))
        
        for i in range(displayed_count):
            # HTML formatting with colors
            status_html = '<span style="color: #ef4444;">Not Validated</span>'  # Kırmızı
            number_html = f'<span style="color: #fbbf24;">{content_list[i]}</span>'  # Sarı
            
            # Fixed-width formatting with HTML
            formatted_line = f"{status_html}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{number_html}"
            self.numbers_display.append(formatted_line)
        
        if len(content_list) > 100:
            self.numbers_display.append(f"<br>... e altri {len(content_list) - 100} {label.lower()}")
        
        self.numbers_display.append(f"<br>Totale: {len(content_list)} {label.lower()} (tutti non validati)")
        
        # Move cursor to start
        cursor = self.numbers_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.Start)
        self.numbers_display.setTextCursor(cursor)
    def upload_proxies(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Carica Proxy", "", "File di testo (*.txt)")
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    self.proxy_caricati = file.read().splitlines()
                QMessageBox.information(self, "Info", f"Caricati {len(self.proxy_caricati)} proxy.")
            except Exception as e:
                QMessageBox.critical(self, "Errore", f"Impossibile caricare il file: {str(e)}")
                
    def toggle_proxies(self):
        self.upload_proxy_button.setVisible(self.proxy_checkbox.isChecked())
        
    def start_validation(self):
        # Parola aktivasyon kontrolü
        password, ok = QInputDialog.getText(self, 
                                          "Attivazione Necessaria", 
                                          "Inserisci la password di attivazione:",
                                          QLineEdit.EchoMode.Password)
        
        if not ok:  # Kullanıcı cancel'a bastı
            return
        
        if not password:  # Boş parola
            QMessageBox.warning(self, "Errore", "Password non può essere vuota!")
            return
        
        # Loading başlat
        self.progress_label.setText("VERIFICA PASSWORD...")
        self.progress_label.setStyleSheet("color: #6366f1;")
        self.loading_bar.setValue(0)
        
        # Password kontrolü için thread başlat
        self.password_thread = LoadingThread()
        self.password_thread.progress_updated.connect(self.update_progress)
        self.password_thread.finished.connect(lambda: self.password_check_finished(password))
        self.password_thread.start()
        
    def password_check_finished(self, entered_password):
        # Parola kontrolü (her zaman yanlış)
        QMessageBox.critical(self, "Errore di Attivazione", 
                           "Password errata!\n\nContatta l'amministratore per ottenere la password corretta.")
        
        # Progress bar'ı reset et
        self.reset_progress_indicators()
            
    def download_valids(self):
        QMessageBox.information(self, "Info", "Nessun dato valido trovato per il download. Esegui prima la convalida.")
        
    def open_telegram_link(self, event):
        webbrowser.open("https://t.me/Nabir25")
        
    def closeEvent(self, event):
        # Cleanup threads
        if hasattr(self, 'loading_thread') and self.loading_thread.isRunning():
            self.loading_thread.quit()
            self.loading_thread.wait()
        if hasattr(self, 'generation_thread') and self.generation_thread.isRunning():
            self.generation_thread.quit()
            self.generation_thread.wait()
        if hasattr(self, 'password_thread') and self.password_thread.isRunning():
            self.password_thread.quit()
            self.password_thread.wait()
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = GeneratoreNumeriItaliani()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()