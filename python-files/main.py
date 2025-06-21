import sys
import socket
import threading
import time
import io
import os
import requests
import json
import hashlib
import uuid
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pickle
import struct

# Hide console window on Windows
if os.name == 'nt':
    import ctypes
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

try:
    from PIL import ImageGrab, Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("PIL not available. Install with: pip install Pillow")

class KeyAuth:
    def __init__(self, name, ownerid, secret, version):
        self.name = name
        self.ownerid = ownerid
        self.secret = secret
        self.version = version
        self.sessionid = ""
        self.initialized = False
        
    def init(self):
        try:
            hwid = str(uuid.getnode())
            init_iv = hashlib.md5(self.name.encode()).hexdigest()[:16]
            
            post_data = {
                "type": "init",
                "ver": self.version,
                "hash": hashlib.md5(open(sys.argv[0], 'rb').read()).hexdigest(),
                "enckey": init_iv,
                "name": self.name,
                "ownerid": self.ownerid
            }
            
            response = requests.post("https://keyauth.win/api/1.2/", data=post_data, timeout=10)
            json_response = response.json()
            
            if json_response["success"]:
                self.sessionid = json_response["sessionid"]
                self.initialized = True
                return True
            else:
                return False
                
        except Exception as e:
            print(f"KeyAuth init error: {e}")
            return False
    
    def login(self, username, password):
        if not self.initialized:
            return False
            
        try:
            hwid = str(uuid.getnode())
            
            post_data = {
                "type": "login",
                "username": username,
                "pass": password,
                "hwid": hwid,
                "sessionid": self.sessionid,
                "name": self.name,
                "ownerid": self.ownerid
            }
            
            response = requests.post("https://keyauth.win/api/1.2/", data=post_data, timeout=10)
            json_response = response.json()
            
            return json_response.get("success", False)
            
        except Exception as e:
            print(f"KeyAuth login error: {e}")
            return False
    
    def license(self, key):
        if not self.initialized:
            return False
            
        try:
            hwid = str(uuid.getnode())
            
            post_data = {
                "type": "license",
                "key": key,
                "hwid": hwid,
                "sessionid": self.sessionid,
                "name": self.name,
                "ownerid": self.ownerid
            }
            
            response = requests.post("https://keyauth.win/api/1.2/", data=post_data, timeout=10)
            json_response = response.json()
            
            return json_response.get("success", False)
            
        except Exception as e:
            print(f"KeyAuth license error: {e}")
            return False

class LoginDialog(QDialog):
    def __init__(self, keyauth_instance):
        super().__init__()
        self.keyauth = keyauth_instance
        self.authenticated = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Authentication Required")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Apply same styling as main window
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #2c3e50, stop:1 #34495e);
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #ecf0f1;
                min-height: 16px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                color: white;
                min-height: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
            }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("Remote Screen Share - Authentication")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Tab widget for login methods
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Username/Password tab
        login_tab = QWidget()
        tab_widget.addTab(login_tab, "Login")
        
        login_layout = QVBoxLayout(login_tab)
        login_layout.setSpacing(12)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        login_layout.addWidget(self.username_input)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        login_layout.addWidget(self.password_input)
        
        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)
        
        # License key tab
        license_tab = QWidget()
        tab_widget.addTab(license_tab, "License Key")
        
        license_layout = QVBoxLayout(license_tab)
        license_layout.setSpacing(12)
        
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("License Key")
        license_layout.addWidget(self.license_input)
        
        license_btn = QPushButton("Activate")
        license_btn.clicked.connect(self.activate_license)
        license_layout.addWidget(license_btn)
        
        # Status label
        self.status_label = QLabel("Please authenticate to continue")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #f39c12; margin-top: 10px;")
        layout.addWidget(self.status_label)
        
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            self.status_label.setText("Please enter username and password")
            self.status_label.setStyleSheet("color: #e74c3c; margin-top: 10px;")
            return
            
        self.status_label.setText("Authenticating...")
        self.status_label.setStyleSheet("color: #f39c12; margin-top: 10px;")
        QApplication.processEvents()
        
        if self.keyauth.login(username, password):
            self.status_label.setText("Authentication successful!")
            self.status_label.setStyleSheet("color: #27ae60; margin-top: 10px;")
            self.authenticated = True
            QTimer.singleShot(1000, self.accept)
        else:
            self.status_label.setText("Authentication failed")
            self.status_label.setStyleSheet("color: #e74c3c; margin-top: 10px;")
    
    def activate_license(self):
        license_key = self.license_input.text()
        
        if not license_key:
            self.status_label.setText("Please enter license key")
            self.status_label.setStyleSheet("color: #e74c3c; margin-top: 10px;")
            return
            
        self.status_label.setText("Activating license...")
        self.status_label.setStyleSheet("color: #f39c12; margin-top: 10px;")
        QApplication.processEvents()
        
        if self.keyauth.license(license_key):
            self.status_label.setText("License activated successfully!")
            self.status_label.setStyleSheet("color: #27ae60; margin-top: 10px;")
            self.authenticated = True
            QTimer.singleShot(1000, self.accept)
        else:
            self.status_label.setText("License activation failed")
            self.status_label.setStyleSheet("color: #e74c3c; margin-top: 10px;")

class ScreenCaptureThread(QThread):
    frame_ready = pyqtSignal(bytes)
    
    def __init__(self):
        super().__init__()
        self.running = False
        
    def run(self):
        while self.running:
            if PIL_AVAILABLE:
                screenshot = ImageGrab.grab()
                # Resize for better performance
                screenshot = screenshot.resize((1280, 720), Image.LANCZOS)
                
                # Convert to bytes
                img_buffer = io.BytesIO()
                screenshot.save(img_buffer, format='JPEG', quality=70)
                img_data = img_buffer.getvalue()
                
                self.frame_ready.emit(img_data)
            
            time.sleep(0.1)  # 10 FPS
    
    def start_capture(self):
        self.running = True
        self.start()
        
    def stop_capture(self):
        self.running = False
        self.wait()

class ServerThread(QThread):
    client_connected = pyqtSignal(str)
    client_disconnected = pyqtSignal()
    
    def __init__(self, port, password):
        super().__init__()
        self.port = port
        self.password = password
        self.server_socket = None
        self.client_socket = None
        self.running = False
        
    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(1)
            self.running = True
            
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    
                    # Authentication
                    client_password = client_socket.recv(1024).decode()
                    if client_password == self.password:
                        client_socket.send(b"AUTH_OK")
                        self.client_socket = client_socket
                        self.client_connected.emit(f"{addr[0]}:{addr[1]}")
                        self.handle_client()
                    else:
                        client_socket.send(b"AUTH_FAIL")
                        client_socket.close()
                        
                except Exception as e:
                    if self.running:
                        print(f"Server error: {e}")
                        
        except Exception as e:
            print(f"Server setup error: {e}")
            
    def handle_client(self):
        try:
            while self.running and self.client_socket:
                # Keep connection alive
                time.sleep(1)
        except:
            pass
        finally:
            if self.client_socket:
                self.client_socket.close()
                self.client_socket = None
            self.client_disconnected.emit()
    
    def send_frame(self, frame_data):
        if self.client_socket:
            try:
                # Send frame size first
                frame_size = len(frame_data)
                self.client_socket.send(struct.pack("!I", frame_size))
                # Send frame data
                self.client_socket.sendall(frame_data)
            except:
                self.client_socket = None
                self.client_disconnected.emit()
    
    def stop_server(self):
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

class ClientThread(QThread):
    frame_received = pyqtSignal(bytes)
    connection_lost = pyqtSignal()
    
    def __init__(self, host, port, password):
        super().__init__()
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.running = False
        
    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            
            # Send password
            self.socket.send(self.password.encode())
            response = self.socket.recv(1024)
            
            if response != b"AUTH_OK":
                return
                
            self.running = True
            while self.running:
                try:
                    # Receive frame size
                    frame_size_data = self.socket.recv(4)
                    if not frame_size_data:
                        break
                        
                    frame_size = struct.unpack("!I", frame_size_data)[0]
                    
                    # Receive frame data
                    frame_data = b""
                    while len(frame_data) < frame_size:
                        chunk = self.socket.recv(frame_size - len(frame_data))
                        if not chunk:
                            break
                        frame_data += chunk
                    
                    if len(frame_data) == frame_size:
                        self.frame_received.emit(frame_data)
                        
                except Exception as e:
                    print(f"Client receive error: {e}")
                    break
                    
        except Exception as e:
            print(f"Client connection error: {e}")
        finally:
            self.connection_lost.emit()
    
    def stop_client(self):
        self.running = False
        if self.socket:
            self.socket.close()

class FullScreenViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Viewer")
        self.showFullScreen()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: black;")
        self.setCentralWidget(self.label)
        
        # ESC to exit
        self.shortcut = QShortcut(QKeySequence("Escape"), self)
        self.shortcut.activated.connect(self.close)
        
    def update_frame(self, frame_data):
        pixmap = QPixmap()
        pixmap.loadFromData(frame_data)
        
        # Scale to fit screen
        scaled_pixmap = pixmap.scaled(
            self.size(), 
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.label.setPixmap(scaled_pixmap)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Remote Screen Share")
        self.setFixedSize(500, 400)
        
        # KeyAuth Configuration
        self.keyauth = KeyAuth(
            name="Pentium's Application",
            ownerid="kqVVq5ovJ0",
            secret="1346ef0015f29bd5984190c1b675c56fc4998b3b5206f21b910ee6c043a577cb",
            version="1.0"
        )
        
        # Initialize KeyAuth and show login dialog
        if not self.init_keyauth():
            sys.exit()
            
        # Apply modern dark theme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #2c3e50, stop:1 #34495e);
            }
            QWidget {
                background-color: transparent;
                color: #ecf0f1;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                color: #ecf0f1;
                min-height: 16px;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: rgba(255, 255, 255, 0.15);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3498db, stop:1 #2980b9);
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
                color: white;
                min-height: 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5dade2, stop:1 #3498db);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2980b9, stop:1 #21618c);
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
                color: #bdc3c7;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 13px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                background-color: rgba(255, 255, 255, 0.05);
                margin-top: 10px;
            }
            QTabBar::tab {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 12px 25px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 13px;
                min-width: 100px;
                min-height: 25px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        
        # Initialize components
        self.server_thread = None
        self.client_thread = None
        self.capture_thread = None
        self.viewer = None
        
        self.init_ui()
        
    def init_keyauth(self):
        # Initialize KeyAuth
        if not self.keyauth.init():
            QMessageBox.critical(self, "Error", "Failed to initialize authentication system")
            return False
        
        # Show login dialog
        login_dialog = LoginDialog(self.keyauth)
        if login_dialog.exec_() == QDialog.Accepted and login_dialog.authenticated:
            return True
        else:
            return False
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # Title
        title = QLabel("Remote Screen Share")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # Tab widget
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Host tab
        host_tab = QWidget()
        tab_widget.addTab(host_tab, "Share Screen")
        
        host_layout = QVBoxLayout(host_tab)
        host_layout.setSpacing(12)
        host_layout.setContentsMargins(20, 20, 20, 20)
        
        host_layout.addWidget(QLabel("Share your screen with others"))
        
        self.host_port_input = QLineEdit("5555")
        self.host_port_input.setPlaceholderText("Port (default: 5555)")
        host_layout.addWidget(self.host_port_input)
        
        self.host_password_input = QLineEdit()
        self.host_password_input.setPlaceholderText("Password")
        self.host_password_input.setEchoMode(QLineEdit.Password)
        host_layout.addWidget(self.host_password_input)
        
        self.start_server_btn = QPushButton("Start Sharing")
        self.start_server_btn.clicked.connect(self.start_server)
        host_layout.addWidget(self.start_server_btn)
        
        self.server_status = QLabel("Not sharing")
        self.server_status.setAlignment(Qt.AlignCenter)
        host_layout.addWidget(self.server_status)
        
        # Client tab
        client_tab = QWidget()
        tab_widget.addTab(client_tab, "View Screen")
        
        client_layout = QVBoxLayout(client_tab)
        client_layout.setSpacing(12)
        client_layout.setContentsMargins(20, 20, 20, 20)
        
        client_layout.addWidget(QLabel("Connect to someone's shared screen"))
        
        self.client_host_input = QLineEdit()
        self.client_host_input.setPlaceholderText("Host IP Address")
        client_layout.addWidget(self.client_host_input)
        
        self.client_port_input = QLineEdit("5555")
        self.client_port_input.setPlaceholderText("Port (default: 5555)")
        client_layout.addWidget(self.client_port_input)
        
        self.client_password_input = QLineEdit()
        self.client_password_input.setPlaceholderText("Password")
        self.client_password_input.setEchoMode(QLineEdit.Password)
        client_layout.addWidget(self.client_password_input)
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_to_server)
        client_layout.addWidget(self.connect_btn)
        
        self.client_status = QLabel("Not connected")
        self.client_status.setAlignment(Qt.AlignCenter)
        client_layout.addWidget(self.client_status)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
    def start_server(self):
        if not PIL_AVAILABLE:
            QMessageBox.warning(self, "Error", "PIL/Pillow is required for screen capture.\nInstall with: pip install Pillow")
            return
            
        if self.server_thread and self.server_thread.isRunning():
            # Stop server
            self.server_thread.stop_server()
            if self.capture_thread:
                self.capture_thread.stop_capture()
            self.start_server_btn.setText("Start Sharing")
            self.server_status.setText("Not sharing")
            return
        
        port = int(self.host_port_input.text() or "5555")
        password = self.host_password_input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return
        
        self.server_thread = ServerThread(port, password)
        self.server_thread.client_connected.connect(self.on_client_connected)
        self.server_thread.client_disconnected.connect(self.on_client_disconnected)
        self.server_thread.start()
        
        self.capture_thread = ScreenCaptureThread()
        self.capture_thread.frame_ready.connect(self.on_frame_ready)
        self.capture_thread.start_capture()
        
        self.start_server_btn.setText("Stop Sharing")
        self.server_status.setText(f"Sharing on port {port}")
        
    def on_client_connected(self, client_info):
        self.server_status.setText(f"Client connected: {client_info}")
        
    def on_client_disconnected(self):
        self.server_status.setText("Client disconnected")
        
    def on_frame_ready(self, frame_data):
        if self.server_thread:
            self.server_thread.send_frame(frame_data)
    
    def connect_to_server(self):
        if self.client_thread and self.client_thread.isRunning():
            # Disconnect
            self.client_thread.stop_client()
            if self.viewer:
                self.viewer.close()
                self.viewer = None
            self.connect_btn.setText("Connect")
            self.client_status.setText("Not connected")
            return
            
        host = self.client_host_input.text()
        port = int(self.client_port_input.text() or "5555")
        password = self.client_password_input.text()
        
        if not host or not password:
            QMessageBox.warning(self, "Error", "Please enter host and password")
            return
        
        self.client_thread = ClientThread(host, port, password)
        self.client_thread.frame_received.connect(self.on_frame_received)
        self.client_thread.connection_lost.connect(self.on_connection_lost)
        self.client_thread.start()
        
        self.viewer = FullScreenViewer()
        self.viewer.show()
        
        self.connect_btn.setText("Disconnect")
        self.client_status.setText(f"Connected to {host}:{port}")
        
    def on_frame_received(self, frame_data):
        if self.viewer:
            self.viewer.update_frame(frame_data)
    
    def on_connection_lost(self):
        self.client_status.setText("Connection lost")
        self.connect_btn.setText("Connect")
        if self.viewer:
            self.viewer.close()
            self.viewer = None
    
    def closeEvent(self, event):
        if self.server_thread:
            self.server_thread.stop_server()
        if self.client_thread:
            self.client_thread.stop_client()
        if self.capture_thread:
            self.capture_thread.stop_capture()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())
