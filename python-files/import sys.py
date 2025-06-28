import sys
import socket
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QLineEdit, 
                            QTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class ConnectionThread(QThread):
    message_received = pyqtSignal(str)
    status_update = pyqtSignal(str)
    connection_established = pyqtSignal()
    connection_closed = pyqtSignal()

    def __init__(self, host, port, is_server=False):
        super().__init__()
        self.host = host
        self.port = port
        self.is_server = is_server
        self.running = True
        self.socket = None
        self.conn = None

    def run(self):
        try:
            if self.is_server:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.socket.bind((self.host, self.port))
                self.socket.listen(1)
                self.status_update.emit(f"Сервер запущен на {self.host}:{self.port}. Ожидание подключения...")
                
                self.conn, addr = self.socket.accept()
                self.status_update.emit(f"Подключен клиент: {addr[0]}")
                self.connection_established.emit()
                
                while self.running:
                    try:
                        data = self.conn.recv(1024)
                        if not data:
                            break
                        self.message_received.emit(f"Друг: {data.decode('utf-8')}")
                    except ConnectionResetError:
                        break
            else:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.status_update.emit(f"Подключено к {self.host}:{self.port}")
                self.connection_established.emit()
                
                while self.running:
                    try:
                        data = self.socket.recv(1024)
                        if not data:
                            break
                        self.message_received.emit(f"Друг: {data.decode('utf-8')}")
                    except ConnectionResetError:
                        break

        except Exception as e:
            self.status_update.emit(f"Ошибка: {str(e)}")
        finally:
            self.cleanup()
            self.connection_closed.emit()

    def send_message(self, message):
        if not self.running:
            return
            
        try:
            target = self.conn if self.is_server else self.socket
            if target:
                target.sendall(message.encode('utf-8'))
        except Exception as e:
            self.status_update.emit(f"Ошибка отправки: {str(e)}")
            self.cleanup()

    def cleanup(self):
        self.running = False
        try:
            if self.conn:
                self.conn.close()
            if self.socket:
                self.socket.close()
        except:
            pass

class P2PApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("P2P Соединение")
        self.setGeometry(100, 100, 500, 500)
        self.connection_thread = None
        
        self.init_ui()
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ddd;
            }
        """)

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()
        
        # Режим подключения
        mode_group = QWidget()
        mode_layout = QHBoxLayout()
        
        self.server_btn = QPushButton("Создать сервер")
        self.server_btn.clicked.connect(self.start_server)
        mode_layout.addWidget(self.server_btn)
        
        self.client_btn = QPushButton("Подключиться")
        self.client_btn.clicked.connect(self.start_client)
        mode_layout.addWidget(self.client_btn)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # Настройки подключения
        settings_group = QWidget()
        settings_layout = QVBoxLayout()
        
        # Поле для IP
        ip_layout = QHBoxLayout()
        ip_layout.addWidget(QLabel("IP сервера:"))
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("0.0.0.0 для сервера")
        ip_layout.addWidget(self.ip_input)
        settings_layout.addLayout(ip_layout)
        
        # Поле для порта
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("Порт:"))
        self.port_input = QLineEdit("5555")
        port_layout.addWidget(self.port_input)
        settings_layout.addLayout(port_layout)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Статус
        self.status_label = QLabel("Статус: Не подключено")
        self.status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Чат
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Отправка сообщений
        message_group = QWidget()
        message_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Введите сообщение...")
        self.message_input.returnPressed.connect(self.send_message)
        message_layout.addWidget(self.message_input)
        
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        self.send_btn.setEnabled(False)
        message_layout.addWidget(self.send_btn)
        
        message_group.setLayout(message_layout)
        layout.addWidget(message_group)
        
        # Кнопка отключения
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.clicked.connect(self.disconnect)
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setStyleSheet("background-color: #f44336;")
        layout.addWidget(self.disconnect_btn)
        
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)
    
    def start_server(self):
        host = self.ip_input.text() or "0.0.0.0"
        try:
            port = int(self.port_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректный номер порта")
            return
            
        self.server_btn.setEnabled(False)
        self.client_btn.setEnabled(False)
        
        self.connection_thread = ConnectionThread(host, port, is_server=True)
        self.connection_thread.message_received.connect(self.display_message)
        self.connection_thread.status_update.connect(self.update_status)
        self.connection_thread.connection_established.connect(self.on_connected)
        self.connection_thread.connection_closed.connect(self.on_disconnected)
        self.connection_thread.start()
    
    def start_client(self):
        host = self.ip_input.text()
        if not host:
            QMessageBox.warning(self, "Ошибка", "Введите IP сервера")
            return
            
        try:
            port = int(self.port_input.text())
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Некорректный номер порта")
            return
            
        self.server_btn.setEnabled(False)
        self.client_btn.setEnabled(False)
        
        self.connection_thread = ConnectionThread(host, port, is_server=False)
        self.connection_thread.message_received.connect(self.display_message)
        self.connection_thread.status_update.connect(self.update_status)
        self.connection_thread.connection_established.connect(self.on_connected)
        self.connection_thread.connection_closed.connect(self.on_disconnected)
        self.connection_thread.start()
    
    def update_status(self, message):
        self.status_label.setText(f"Статус: {message}")
    
    def display_message(self, message):
        self.chat_display.append(message)
    
    def on_connected(self):
        self.send_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(True)
        self.display_message("--- Соединение установлено ---")
    
    def on_disconnected(self):
        self.server_btn.setEnabled(True)
        self.client_btn.setEnabled(True)
        self.send_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(False)
        self.display_message("--- Соединение разорвано ---")
        self.update_status("Не подключено")
    
    def send_message(self):
        message = self.message_input.text()
        if not message or not self.connection_thread:
            return
            
        self.display_message(f"Я: {message}")
        self.connection_thread.send_message(message)
        self.message_input.clear()
    
    def disconnect(self):
        if self.connection_thread:
            self.connection_thread.cleanup()
    
    def closeEvent(self, event):
        self.disconnect()
        event.accept()

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    window = P2PApp()
    window.show()
    sys.exit(app.exec_())