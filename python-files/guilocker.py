import os
import sys
import json
import base64
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QFileDialog, QLineEdit, QMessageBox, 
                            QProgressBar, QGroupBox, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

class EncryptionThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, operation, file_path, password, output_path=None):
        super().__init__()
        self.operation = operation  # 'encrypt' or 'decrypt'
        self.file_path = file_path
        self.password = password
        self.output_path = output_path

    def run(self):
        try:
            if self.operation == 'encrypt':
                self.encrypt_file()
            else:
                self.decrypt_file()
            self.finished_signal.emit(True, "Operation completed successfully!")
        except Exception as e:
            self.finished_signal.emit(False, str(e))

    def encrypt_file(self):
        # Generate a random salt
        salt = get_random_bytes(32)
        
        # Derive key from password
        key = PBKDF2(self.password, salt, dkLen=32, count=1000000)
        
        # Create cipher object
        cipher = AES.new(key, AES.MODE_GCM)
        
        # Read file data
        with open(self.file_path, 'rb') as f:
            file_data = f.read()
        
        # Encrypt data
        ciphertext, tag = cipher.encrypt_and_digest(file_data)
        
        # Prepare output data (salt + nonce + tag + ciphertext)
        output_data = salt + cipher.nonce + tag + ciphertext
        
        # Write to output file
        output_path = self.output_path if self.output_path else self.file_path + '.sec'
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        self.progress_signal.emit(100)

    def decrypt_file(self):
        # Read encrypted file
        with open(self.file_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Extract components
        salt = encrypted_data[:32]
        nonce = encrypted_data[32:48]
        tag = encrypted_data[48:64]
        ciphertext = encrypted_data[64:]
        
        # Derive key
        key = PBKDF2(self.password, salt, dkLen=32, count=1000000)
        
        # Decrypt
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        try:
            decrypted_data = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            raise Exception("Incorrect password or corrupted file")
        
        # Determine output path
        if self.file_path.endswith('.sec'):
            output_path = self.file_path[:-4]
        else:
            output_path = self.file_path + '.decrypted'
        
        # Write decrypted file
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)
        
        self.progress_signal.emit(100)

class FileEncrypter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Military-Grade File Encrypter")
        self.setGeometry(100, 100, 600, 450)
        
        # Set dark theme
        self.set_dark_theme()
        
        # Main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Layout
        self.layout = QVBoxLayout()
        self.main_widget.setLayout(self.layout)
        
        # Title
        self.title = QLabel("MILITARY-GRADE FILE ENCRYPTER")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont('Arial', 16, QFont.Bold))
        self.title.setStyleSheet("color: #00FF00;")
        self.layout.addWidget(self.title)
        
        # File selection
        self.file_group = QGroupBox("File Operations")
        self.file_group.setStyleSheet("QGroupBox { color: #00FF00; border: 1px solid #00FF00; }")
        self.file_layout = QVBoxLayout()
        
        self.file_label = QLabel("Selected File: None")
        self.file_label.setStyleSheet("color: #AAAAAA;")
        self.file_layout.addWidget(self.file_label)
        
        self.select_file_btn = QPushButton("Select File")
        self.select_file_btn.setStyleSheet(self.get_button_style())
        self.select_file_btn.clicked.connect(self.select_file)
        self.file_layout.addWidget(self.select_file_btn)
        
        self.file_group.setLayout(self.file_layout)
        self.layout.addWidget(self.file_group)
        
        # Password
        self.password_group = QGroupBox("Security Parameters")
        self.password_group.setStyleSheet("QGroupBox { color: #00FF00; border: 1px solid #00FF00; }")
        self.password_layout = QVBoxLayout()
        
        self.password_label = QLabel("Enter Password:")
        self.password_label.setStyleSheet("color: #AAAAAA;")
        self.password_layout.addWidget(self.password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("background: #111111; color: #00FF00; border: 1px solid #00FF00;")
        self.password_layout.addWidget(self.password_input)
        
        self.confirm_label = QLabel("Confirm Password:")
        self.confirm_label.setStyleSheet("color: #AAAAAA;")
        self.password_layout.addWidget(self.confirm_label)
        
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        self.confirm_input.setStyleSheet("background: #111111; color: #00FF00; border: 1px solid #00FF00;")
        self.password_layout.addWidget(self.confirm_input)
        
        self.password_group.setLayout(self.password_layout)
        self.layout.addWidget(self.password_group)
        
        # Progress
        self.progress = QProgressBar()
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #00FF00;
                text-align: center;
                color: #00FF00;
            }
            QProgressBar::chunk {
                background-color: #00AA00;
            }
        """)
        self.layout.addWidget(self.progress)
        
        # Buttons
        self.button_layout = QHBoxLayout()
        
        self.encrypt_btn = QPushButton("ENCRYPT")
        self.encrypt_btn.setStyleSheet(self.get_button_style())
        self.encrypt_btn.clicked.connect(self.encrypt)
        self.button_layout.addWidget(self.encrypt_btn)
        
        self.decrypt_btn = QPushButton("DECRYPT")
        self.decrypt_btn.setStyleSheet(self.get_button_style())
        self.decrypt_btn.clicked.connect(self.decrypt)
        self.button_layout.addWidget(self.decrypt_btn)
        
        self.layout.addLayout(self.button_layout)
        
        # Log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background: #111111; color: #00FF00; border: 1px solid #00FF00;")
        self.layout.addWidget(self.log)
        
        # Variables
        self.current_file = None
        self.worker_thread = None

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #003300;
                color: #00FF00;
                border: 1px solid #00FF00;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #005500;
            }
            QPushButton:pressed {
                background-color: #007700;
            }
        """

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.WindowText, QColor(0, 255, 0))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(0, 255, 0))
        palette.setColor(QPalette.Text, QColor(0, 255, 0))
        palette.setColor(QPalette.Button, QColor(0, 50, 0))
        palette.setColor(QPalette.ButtonText, QColor(0, 255, 0))
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Highlight, QColor(0, 100, 0))
        palette.setColor(QPalette.HighlightedText, QColor(0, 255, 0))
        self.setPalette(palette)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.current_file = file_path
            self.file_label.setText(f"Selected File: {os.path.basename(file_path)}")
            self.log_message(f"File selected: {file_path}")

    def log_message(self, message):
        self.log.append(f"> {message}")

    def validate_password(self):
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        
        if not password:
            QMessageBox.warning(self, "Warning", "Password cannot be empty!")
            return None
        
        if password != confirm:
            QMessageBox.warning(self, "Warning", "Passwords do not match!")
            return None
        
        return password

    def encrypt(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return
        
        password = self.validate_password()
        if not password:
            return
        
        self.log_message(f"Starting encryption of {os.path.basename(self.current_file)}")
        
        # Start encryption thread
        self.worker_thread = EncryptionThread('encrypt', self.current_file, password)
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.finished_signal.connect(self.operation_finished)
        self.worker_thread.start()
        
        self.set_buttons_enabled(False)

    def decrypt(self):
        if not self.current_file:
            QMessageBox.warning(self, "Warning", "Please select a file first!")
            return
        
        password = self.validate_password()
        if not password:
            return
        
        self.log_message(f"Starting decryption of {os.path.basename(self.current_file)}")
        
        # Start decryption thread
        self.worker_thread = EncryptionThread('decrypt', self.current_file, password)
        self.worker_thread.progress_signal.connect(self.update_progress)
        self.worker_thread.finished_signal.connect(self.operation_finished)
        self.worker_thread.start()
        
        self.set_buttons_enabled(False)

    def update_progress(self, value):
        self.progress.setValue(value)

    def operation_finished(self, success, message):
        self.set_buttons_enabled(True)
        self.progress.setValue(0)
        
        if success:
            self.log_message("Operation completed successfully!")
            QMessageBox.information(self, "Success", message)
        else:
            self.log_message(f"Error: {message}")
            QMessageBox.critical(self, "Error", message)

    def set_buttons_enabled(self, enabled):
        self.encrypt_btn.setEnabled(enabled)
        self.decrypt_btn.setEnabled(enabled)
        self.select_file_btn.setEnabled(enabled)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set dark theme for the entire application
    app.setStyle("Fusion")
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.WindowText, QColor(0, 255, 0))
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    dark_palette.setColor(QPalette.ToolTipText, QColor(0, 255, 0))
    dark_palette.setColor(QPalette.Text, QColor(0, 255, 0))
    dark_palette.setColor(QPalette.Button, QColor(0, 50, 0))
    dark_palette.setColor(QPalette.ButtonText, QColor(0, 255, 0))
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Highlight, QColor(0, 100, 0))
    dark_palette.setColor(QPalette.HighlightedText, QColor(0, 255, 0))
    app.setPalette(dark_palette)
    
    window = FileEncrypter()
    window.show()
    sys.exit(app.exec_())