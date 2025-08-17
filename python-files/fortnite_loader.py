import sys
import time
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QMessageBox, 
    QComboBox, QGroupBox, QRadioButton, QFrame, QSizePolicy
)
from PyQt5.QtGui import (
    QPixmap, QIcon, QPainter, QPainterPath, QBrush, QColor, 
    QLinearGradient, QFont, QFontDatabase, QImage, QMovie
)
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer, QPoint, QByteArray

class SquircleButton(QPushButton):
    def __init__(self, text, parent=None, color="#a855f7"):
        super().__init__(text, parent)
        self.setFixedSize(180, 60)
        self.setFont(QFont("Grand Prix", 12))
        self.base_color = QColor(color)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        radius = min(rect.width(), rect.height()) / 3
        path.addRoundedRect(rect, radius, radius)
        
        gradient = QLinearGradient(0, 0, 0, self.height())
        if self.isDown():
            gradient.setColorAt(0, self.base_color.darker(150))
            gradient.setColorAt(1, self.base_color.darker(200))
        else:
            gradient.setColorAt(0, self.base_color.lighter(120))
            gradient.setColorAt(1, self.base_color)
            
        painter.fillPath(path, QBrush(gradient))
        painter.setPen(Qt.white)
        painter.drawPath(path)
        
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())

class AnimatedLoader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FLOWIS LOADER")
        self.setFixedSize(1200, 800)
        self.last_hwid_reset = 0
        self.cooldown = 3600  # 1 hour cooldown
        self.valid_key = "flowissocutehaha"
        self.current_theme = "PURPLE STORM"
        
        # Load custom font
        QFontDatabase.addApplicationFont("grandprix.ttf")
        
        # Set window flags for custom shape
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Central widget with squircle mask
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(30, 30, 30, 30)
        self.main_layout.setSpacing(30)
        
        # Sidebar
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(220)
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
        self.sidebar_layout.setSpacing(25)
        
        # Logo with animation
        self.logo = QLabel()
        self.logo_movie = QMovie("loader_logo.gif")
        self.logo.setMovie(self.logo_movie)
        self.logo_movie.start()
        self.logo.setAlignment(Qt.AlignCenter)
        self.sidebar_layout.addWidget(self.logo)
        
        # Sidebar buttons
        self.btn_inject = SquircleButton("INJECT", color="#a855f7")
        self.btn_settings = SquircleButton("SETTINGS", color="#a855f7")
        self.btn_spoofer = SquircleButton("TEMP SPOOFER", color="#a855f7")
        
        self.sidebar_layout.addWidget(self.btn_inject)
        self.sidebar_layout.addWidget(self.btn_settings)
        self.sidebar_layout.addWidget(self.btn_spoofer)
        self.sidebar_layout.addStretch()
        
        # Discord button at bottom
        self.discord_btn = QPushButton()
        self.discord_btn.setIcon(QIcon("discord_logo.png"))
        self.discord_btn.setIconSize(QSize(40, 40))
        self.discord_btn.setFixedSize(50, 50)
        self.discord_btn.setStyleSheet("background: transparent; border: none;")
        self.discord_btn.clicked.connect(lambda: webbrowser.open("https://discord.gg/KWfHkq7h"))
        self.sidebar_layout.addWidget(self.discord_btn, alignment=Qt.AlignRight)
        
        # Divider line
        self.divider = QFrame()
        self.divider.setFrameShape(QFrame.VLine)
        self.divider.setFrameShadow(QFrame.Sunken)
        self.divider.setLineWidth(2)
        
        # Main content area
        self.stacked_pages = QStackedWidget()
        
        # Add widgets to main layout
        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.divider)
        self.main_layout.addWidget(self.stacked_pages)
        
        # Create pages
        self.create_inject_page()
        self.create_settings_page()
        self.create_spoofer_page()
        
        # Connect signals
        self.btn_inject.clicked.connect(lambda: self.stacked_pages.setCurrentWidget(self.inject_page))
        self.btn_settings.clicked.connect(lambda: self.stacked_pages.setCurrentWidget(self.settings_page))
        self.btn_spoofer.clicked.connect(lambda: self.stacked_pages.setCurrentWidget(self.spoofer_page))
        
        # Set default theme
        self.change_theme("PURPLE STORM")
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw squircle window
        path = QPainterPath()
        rect = QRectF(0, 0, self.width(), self.height())
        radius = 40
        path.addRoundedRect(rect, radius, radius)
        
        # Window background
        painter.fillPath(path, QBrush(QColor(20, 20, 30, 220)))
        painter.drawPath(path)
        
        # Storm effect
        if hasattr(self, 'storm_movie'):
            storm_rect = QRectF(0, 0, self.width(), self.height())
            painter.drawImage(storm_rect, self.storm_movie.currentImage())
    
    def create_inject_page(self):
        self.inject_page = QWidget()
        layout = QVBoxLayout(self.inject_page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Key input
        key_group = QGroupBox("ACTIVATE LOADER")
        key_layout = QVBoxLayout()
        key_layout.setSpacing(20)
        
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("ENTER ACTIVATION KEY")
        self.key_input.setFont(QFont("Grand Prix", 12))
        self.key_input.setFixedHeight(60)
        self.key_input.setStyleSheet("padding-left: 15px;")
        
        self.activate_btn = SquircleButton("ACTIVATE", color=self.get_theme_color())
        self.activate_btn.clicked.connect(self.activate_loader)
        
        key_layout.addWidget(self.key_input)
        key_layout.addWidget(self.activate_btn)
        key_group.setLayout(key_layout)
        
        layout.addWidget(key_group)
        layout.addStretch()
        
        self.stacked_pages.addWidget(self.inject_page)
    
    def create_settings_page(self):
        self.settings_page = QWidget()
        layout = QVBoxLayout(self.settings_page)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme selector
        theme_group = QGroupBox("LOADER THEMES")
        theme_group.setFont(QFont("Grand Prix", 14))
        theme_layout = QVBoxLayout()
        theme_layout.setSpacing(20)
        
        self.theme_combo = QComboBox()
        self.theme_combo.setFont(QFont("Grand Prix", 12))
        self.theme_combo.addItems(["PURPLE STORM", "RED STORM", "GREEN STORM"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        
        layout.addWidget(theme_group)
        layout.addStretch()
        
        self.stacked_pages.addWidget(self.settings_page)
    
    def create_spoofer_page(self):
        self.spoofer_page = QWidget()
        layout = QVBoxLayout(self.spoofer_page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)
        
        # Location selector
        loc_group = QGroupBox("SPOOF LOCATION")
        loc_group.setFont(QFont("Grand Prix", 14))
        loc_layout = QVBoxLayout()
        loc_layout.setSpacing(15)
        
        # Country selection with flags
        countries = [
            ("AUSTRALIA", "australia_flag.png"),
            ("USA", "usa_flag.png"),
            ("EUROPE", "europe_flag.png")
        ]
        
        self.location_btns = []
        for country, flag in countries:
            btn = QRadioButton(country)
            btn.setFont(QFont("Grand Prix", 12))
            btn.setIcon(QIcon(flag))
            btn.setIconSize(QSize(40, 25))
            btn.setStyleSheet("padding: 8px;")
            loc_layout.addWidget(btn)
            self.location_btns.append(btn)
        
        self.location_btns[0].setChecked(True)
        loc_group.setLayout(loc_layout)
        
        # HWID spoofer
        hwid_group = QGroupBox("HARDWARE SPOOFER")
        hwid_group.setFont(QFont("Grand Prix", 14))
        hwid_layout = QVBoxLayout()
        hwid_layout.setSpacing(15)  # Reduced spacing
        
        self.hwid_key = QLineEdit()
        self.hwid_key.setPlaceholderText("ENTER SPOOFER KEY")
        self.hwid_key.setFont(QFont("Grand Prix", 10))  # Smaller font
        self.hwid_key.setFixedHeight(50)  # Smaller height
        self.hwid_key.setStyleSheet("padding-left: 15px;")
        
        self.hwid_status = QLabel("STATUS: READY")
        self.hwid_status.setFont(QFont("Grand Prix", 10))  # Smaller font
        
        self.btn_reset_hwid = SquircleButton("SPOOF HWID", color=self.get_theme_color())
        self.btn_reset_hwid.setFixedSize(180, 50)  # Smaller button
        self.btn_reset_hwid.setFont(QFont("Grand Prix", 10))  # Smaller font
        self.btn_reset_hwid.clicked.connect(self.spoof_motherboard)
        
        hwid_layout.addWidget(self.hwid_key)
        hwid_layout.addWidget(self.hwid_status)
        hwid_layout.addWidget(self.btn_reset_hwid)
        hwid_group.setLayout(hwid_layout)
        
        layout.addWidget(loc_group)
        layout.addWidget(hwid_group)
        layout.addStretch()
        
        self.stacked_pages.addWidget(self.spoofer_page)
    
    def get_theme_color(self):
        if "PURPLE" in self.current_theme:
            return "#a855f7"
        elif "RED" in self.current_theme:
            return "#ef4444"
        else:  # GREEN
            return "#22c55e"
    
    def activate_loader(self):
        if self.key_input.text() == self.valid_key:
            QMessageBox.information(self, "ACTIVATED", "LOADER ACTIVATED SUCCESSFULLY!")
            self.btn_inject.setEnabled(False)
            self.key_input.setEnabled(False)
            self.activate_btn.setEnabled(False)
        else:
            QMessageBox.warning(self, "INVALID KEY", "WRONG ACTIVATION KEY!")
    
    def spoof_motherboard(self):
        if self.hwid_key.text() != self.valid_key:
            self.hwid_status.setText("STATUS: INVALID KEY")
            QTimer.singleShot(2000, lambda: self.hwid_status.setText("STATUS: READY"))
            return
            
        current_time = time.time()
        if current_time - self.last_hwid_reset < self.cooldown:
            remaining = int(self.cooldown - (current_time - self.last_hwid_reset))
            self.hwid_status.setText(f"STATUS: COOLDOWN ({remaining}s)")
            
            self.cooldown_timer = QTimer(self)
            self.cooldown_timer.timeout.connect(lambda: self.update_cooldown(current_time))
            self.cooldown_timer.start(1000)
        else:
            self.last_hwid_reset = current_time
            QMessageBox.information(self, "SUCCESS", "MOTHERBOARD SPOOFED SUCCESSFULLY!")
            self.hwid_status.setText("STATUS: MOTHERBOARD SPOOFED!")
            QTimer.singleShot(3000, lambda: self.hwid_status.setText("STATUS: READY"))
    
    def update_cooldown(self, reset_time):
        current_time = time.time()
        remaining = int(self.cooldown - (current_time - reset_time))
        
        if remaining <= 0:
            self.hwid_status.setText("STATUS: READY")
            self.cooldown_timer.stop()
        else:
            self.hwid_status.setText(f"STATUS: COOLDOWN ({remaining}s)")
    
    def change_theme(self, theme):
        self.current_theme = theme
        theme_color = self.get_theme_color()
        
        # Update all buttons
        for btn in [self.btn_inject, self.btn_settings, self.btn_spoofer, 
                   self.activate_btn, self.btn_reset_hwid]:
            btn.base_color = QColor(theme_color)
            btn.update()
        
        # Load animated storm background
        theme_name = theme.split()[0].lower()
        self.storm_movie = QMovie(f"{theme_name}_storm.gif")
        self.storm_movie.frameChanged.connect(self.update)
        self.storm_movie.start()
        
        # Full UI color scheme
        if "PURPLE" in theme:
            accent = "#a855f7"
            bg = "rgba(30, 10, 50, 200)"
        elif "RED" in theme:
            accent = "#ef4444"
            bg = "rgba(50, 10, 10, 200)"
        else:  # GREEN
            accent = "#22c55e"
            bg = "rgba(10, 30, 10, 200)"
        
        style = f"""
            QMainWindow {{
                background: transparent;
                color: white;
            }}
            QGroupBox {{
                border: 3px solid {accent};
                border-radius: 15px;
                margin-top: 15px;
                padding-top: 25px;
                background: {bg};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                color: {accent};
            }}
            QLineEdit, QComboBox {{
                background: rgba(0, 0, 0, 0.3);
                color: white;
                border: 2px solid {accent};
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }}
            QRadioButton {{
                spacing: 15px;
                color: white;
            }}
            QLabel {{
                color: white;
            }}
            QFrame {{
                border: 2px solid {accent};
            }}
        """
        self.setStyleSheet(style)
        self.divider.setStyleSheet(f"border: 2px solid {accent};")
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loader = AnimatedLoader()
    loader.show()
    sys.exit(app.exec_())
    import sys
import time
import webbrowser
import uuid
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QLineEdit, QMessageBox, 
    QGroupBox, QRadioButton, QFrame
)
from PyQt5.QtGui import (
    QPixmap, QIcon, QPainter, QPainterPath, QBrush, QColor, 
    QLinearGradient, QFont, QFontDatabase, QImage, QMovie
)
from PyQt5.QtCore import Qt, QSize, QRectF, QTimer

class CompactLoader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MINI SPOOFER")
        self.setFixedSize(600, 400)  # Smaller window
        self.valid_key = "flowiskey"
        self.current_hwid = str(uuid.getnode())  # Get current HWID
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Main widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(15, 15, 15, 15)
        
        # Create pages
        self.create_main_page()
        
        # Discord button
        self.discord_btn = QPushButton()
        self.discord_btn.setIcon(QIcon("discord_logo.png"))
        self.discord_btn.setIconSize(QSize(20, 20))
        self.discord_btn.setFixedSize(30, 30)
        self.discord_btn.setStyleSheet("background: transparent; border: none;")
        self.discord_btn.clicked.connect(lambda: webbrowser.open("https://discord.gg/KWfHkq7h"))
        self.layout.addWidget(self.discord_btn, 0, Qt.AlignRight)
        
        # Set purple theme by default
        self.change_theme("#a855f7")
    
    def create_main_page(self):
        # HWID Spoofer Group
        hwid_group = QGroupBox("HWID SPOOFER")
        hwid_group.setFont(QFont("Arial", 9))
        hwid_layout = QVBoxLayout()
        hwid_layout.setSpacing(10)
        
        # Current HWID
        self.lbl_current = QLabel(f"Current HWID: {self.current_hwid}")
        self.lbl_current.setFont(QFont("Consolas", 8))
        self.lbl_current.setWordWrap(True)
        
        # New HWID
        self.lbl_new = QLabel("New HWID: Not generated")
        self.lbl_new.setFont(QFont("Consolas", 8))
        
        # Key Input
        self.key_input = QLineEdit()
        self.key_input.setPlaceholderText("Enter activation key")
        self.key_input.setFont(QFont("Arial", 8))
        self.key_input.setFixedHeight(25)
        
        # Spoof Button
        self.btn_spoof = QPushButton("SPOOF HWID")
        self.btn_spoof.setFont(QFont("Arial", 8))
        self.btn_spoof.setFixedHeight(25)
        self.btn_spoof.clicked.connect(self.spoof_hwid)
        
        hwid_layout.addWidget(self.lbl_current)
        hwid_layout.addWidget(self.lbl_new)
        hwid_layout.addWidget(self.key_input)
        hwid_layout.addWidget(self.btn_spoof)
        hwid_group.setLayout(hwid_layout)
        
        self.layout.addWidget(hwid_group)
    
    def spoof_hwid(self):
        if self.key_input.text() != self.valid_key:
            QMessageBox.warning(self, "Error", "Invalid activation key!")
            return
        
        # Generate new HWID
        new_hwid = str(uuid.uuid4())
        self.current_hwid = new_hwid
        self.lbl_current.setText(f"Current HWID: {self.current_hwid}")
        self.lbl_new.setText(f"New HWID: {new_hwid}")
        
        # Simulate HWID change (in real app this would modify registry/device IDs)
        QMessageBox.information(self, "Success", "HWID spoofed successfully!\n\n"
                              f"Old HWID: {self.current_hwid}\n"
                              f"New HWID: {new_hwid}")
    
    def change_theme(self, color):
        style = f"""
            QMainWindow {{
                background: rgba(30, 30, 40, 220);
                border-radius: 10px;
                color: white;
            }}
            QGroupBox {{
                border: 2px solid {color};
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                background: rgba(20, 20, 30, 180);
                font-size: 9px;
            }}
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color}, stop:1 {QColor(color).darker(120).name()});
                color: white;
                border: none;
                border-radius: 3px;
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {QColor(color).darker(120).name()}, 
                    stop:1 {QColor(color).darker(150).name()});
            }}
            QLineEdit {{
                background: rgba(10, 10, 20, 200);
                color: white;
                border: 1px solid {color};
                border-radius: 3px;
                padding: 2px 5px;
            }}
        """
        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    loader = CompactLoader()
    loader.show()
    sys.exit(app.exec_())