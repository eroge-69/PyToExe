import sys
import hashlib
import requests
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QWidget, QMessageBox,
                             QGroupBox, QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.Qt import QImage, QByteArray

class FacebookStyleLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("512 Films - Login")
        self.setGeometry(300, 200, 1000, 600)
        self.setStyleSheet("background-color: #f0f2f5;")
        
        # Credentials
        self.correct_username = "512 Films"
        self.correct_password_hash = hashlib.sha256("512filmshihaiyar".encode()).hexdigest()
        
        self.initUI()
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        
        # Left Side - Branding with Photographer Image
        left_frame = QFrame()
        left_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0066ff, stop:1 #0044cc);
                border-radius: 15px;
                margin: 20px;
            }
        """)
        left_layout = QVBoxLayout()
        
        # 512 Films Logo
        logo_label = QLabel("512 Films")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            QLabel {
                font-size: 48pt;
                font-weight: bold;
                color: white;
                margin-top: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
        """)
        
        tagline_label = QLabel("Professional Video Editing Suite")
        tagline_label.setAlignment(Qt.AlignCenter)
        tagline_label.setStyleSheet("""
            QLabel {
                font-size: 16pt;
                color: rgba(255,255,255,0.9);
                margin-top: 10px;
                margin-bottom: 20px;
            }
        """)
        
        # Photographer Image (Direct URL use karte hue)
        photographer_label = QLabel()
        photographer_label.setAlignment(Qt.AlignCenter)
        photographer_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0,0,0,0.3);
                border-radius: 10px;
                margin: 10px;
                padding: 5px;
            }
        """)
        
        # Load photographer image from URL
        try:
            photographer_url = "https://aiphrasefinder.com/wp-content/uploads/2024/02/night-1927265_1280.jpg"
            response = requests.get(photographer_url)
            if response.status_code == 200:
                image_data = QByteArray(response.content)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                # Scale the image to fit properly
                pixmap = pixmap.scaled(350, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                photographer_label.setPixmap(pixmap)
                photographer_label.setStyleSheet("border-radius: 10px; margin: 10px;")
            else:
                raise Exception("Image download failed")
        except:
            # If image loading fails, show text instead
            photographer_label.setText("📸 Photographer at Work")
            photographer_label.setStyleSheet("""
                QLabel {
                    font-size: 18pt;
                    color: white;
                    background-color: rgba(0,0,0,0.3);
                    border-radius: 10px;
                    padding: 50px;
                    margin: 10px;
                }
            """)
        
        left_layout.addWidget(logo_label)
        left_layout.addWidget(tagline_label)
        left_layout.addWidget(photographer_label)
        left_layout.addStretch()
        left_frame.setLayout(left_layout)
        
        # Right Side - Login Form with Couple Photo
        right_frame = QFrame()
        right_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                margin: 50px;
                padding: 30px;
            }
        """)
        right_layout = QVBoxLayout()
        
        # Login Title
        login_title = QLabel("Log in to 512 Films")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet("""
            QLabel {
                font-size: 24pt;
                font-weight: bold;
                color: #1a1a1a;
                margin-bottom: 20px;
            }
        """)
        
        # Couple Photo in Right Side
        couple_label = QLabel()
        couple_label.setAlignment(Qt.AlignCenter)
        couple_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border-radius: 10px;
                margin: 10px 30px;
                padding: 10px;
            }
        """)
        
        # Load couple image from URL
        try:
            couple_url = "https://thelane.com/wp-content/uploads/2022/02/TildeMitchell-244-2-scaled.jpg"
            response = requests.get(couple_url)
            if response.status_code == 200:
                image_data = QByteArray(response.content)
                pixmap = QPixmap()
                pixmap.loadFromData(image_data)
                # Scale the image to fit properly
                pixmap = pixmap.scaled(280, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                couple_label.setPixmap(pixmap)
                couple_label.setStyleSheet("border-radius: 10px; margin: 10px 30px;")
            else:
                raise Exception("Image download failed")
        except:
            # If image loading fails, show text instead
            couple_label.setText("👫 Couple Photo")
            couple_label.setStyleSheet("""
                QLabel {
                    font-size: 16pt;
                    color: #666666;
                    background-color: #f8f9fa;
                    border: 2px dashed #cccccc;
                    border-radius: 10px;
                    padding: 40px;
                    margin: 10px 30px;
                }
            """)
        
        # Username Field
        username_label = QLabel("Username")
        username_label.setStyleSheet("font-size: 11pt; color: #606770; margin-bottom: 5px; margin-top: 20px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.setText("512 Films")  # Default username
        self.username_input.setStyleSheet("""
            QLineEdit {
                font-size: 14pt;
                padding: 12px;
                border: 1px solid #dddfe2;
                border-radius: 6px;
                background-color: #f5f6f7;
            }
            QLineEdit:focus {
                border: 1px solid #1877f2;
                background-color: white;
            }
        """)
        
        # Password Field
        password_label = QLabel("Password")
        password_label.setStyleSheet("font-size: 11pt; color: #606770; margin-bottom: 5px; margin-top: 15px;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                font-size: 14pt;
                padding: 12px;
                border: 1px solid #dddfe2;
                border-radius: 6px;
                background-color: #f5f6f7;
            }
            QLineEdit:focus {
                border: 1px solid #1877f2;
                background-color: white;
            }
        """)
        
        # Login Button
        login_btn = QPushButton("Log In")
        login_btn.clicked.connect(self.check_login)
        login_btn.setStyleSheet("""
            QPushButton {
                font-size: 18pt;
                font-weight: bold;
                padding: 12px;
                background-color: #1877f2;
                color: white;
                border: none;
                border-radius: 6px;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
            QPushButton:pressed {
                background-color: #29487d;
            }
        """)
        
        # Forgot Password
        forgot_link = QLabel("<a href='#' style='color: #1877f2; text-decoration: none; font-size: 11pt;'>Forgotten password?</a>")
        forgot_link.setAlignment(Qt.AlignCenter)
        forgot_link.setStyleSheet("margin-top: 15px;")
        forgot_link.linkActivated.connect(self.forgot_password)
        
        right_layout.addWidget(login_title)
        right_layout.addWidget(couple_label)  # Couple photo added here
        right_layout.addWidget(username_label)
        right_layout.addWidget(self.username_input)
        right_layout.addWidget(password_label)
        right_layout.addWidget(self.password_input)
        right_layout.addWidget(login_btn)
        right_layout.addWidget(forgot_link)
        right_frame.setLayout(right_layout)
        
        # Add frames to main layout
        main_layout.addWidget(left_frame, 2)
        main_layout.addWidget(right_frame, 1)
        central_widget.setLayout(main_layout)
    
    def check_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if username != self.correct_username:
            QMessageBox.warning(self, "Login Failed", "Incorrect username!")
            return
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        if hashed_password == self.correct_password_hash:
            self.show_activator_screen()
        else:
            QMessageBox.warning(self, "Login Failed", "Incorrect password!")
    
    def forgot_password(self):
        # WhatsApp number show karega
        QMessageBox.information(self, "Contact Support", 
                               "📞 WhatsApp Support:\n"
                               "+92 305 61 81 000\n\n"
                               "Please contact us on WhatsApp for password recovery.")
    
    def show_activator_screen(self):
        # New window for activator
        self.activator_window = ActivatorWindow()
        self.activator_window.show()
        self.hide()

class ActivatorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("512 Films - EDIUS Activator")
        self.setGeometry(400, 200, 800, 600)
        self.setStyleSheet("background-color: #f0f2f5;")
        self.initUI()
    
    def initUI(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        
        # Header
        header = QLabel("EDIUS ACTIVATOR")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("""
            QLabel {
                font-size: 28pt;
                font-weight: bold;
                color: #1877f2;
                margin: 30px;
                padding: 20px;
                background-color: white;
                border-radius: 10px;
            }
        """)
        
        # Activator Card
        activator_card = QFrame()
        activator_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                margin: 20px;
                padding: 30px;
            }
        """)
        activator_layout = QVBoxLayout()
        
        version_label = QLabel("EDIUS 11.21 17141")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("font-size: 18pt; color: #1c1e21; margin: 20px;")
        
        activate_btn = QPushButton("ACTIVATE NOW")
        activate_btn.clicked.connect(self.activate)
        activate_btn.setStyleSheet("""
            QPushButton {
                font-size: 16pt;
                font-weight: bold;
                padding: 15px;
                background-color: #1877f2;
                color: white;
                border: none;
                border-radius: 8px;
                margin: 20px 50px;
            }
            QPushButton:hover {
                background-color: #166fe5;
            }
        """)
        
        activator_layout.addWidget(version_label)
        activator_layout.addWidget(activate_btn)
        activator_card.setLayout(activator_layout)
        
        layout.addWidget(header)
        layout.addWidget(activator_card)
        layout.addStretch()
        central_widget.setLayout(layout)
    
    def activate(self):
        QMessageBox.information(self, "Success", "EDIUS Activated Successfully!\n\n512 Films ®")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = FacebookStyleLogin()
    window.show()
    sys.exit(app.exec_())