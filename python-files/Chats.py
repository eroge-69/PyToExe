import sys
import socket
import threading
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                             QListWidget, QLabel, QAction, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

class ServerThread(QThread):
    new_message = pyqtSignal(str)
    new_client = pyqtSignal(str)
    client_disconnected = pyqtSignal(str)
    file_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = []
        self.running = True

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.new_message.emit(f"Server {self.host}:{self.port} ünvanında işə salındı...")
            
            while self.running:
                client_socket, client_address = self.server_socket.accept()
                client_thread = ClientHandler(client_socket, client_address, self)
                client_thread.start()
                self.clients.append(client_thread)
                self.new_client.emit(f"{client_address[0]}:{client_address[1]}")
                
        except Exception as e:
            self.new_message.emit(f"Server xətası: {str(e)}")
            
    def stop(self):
        self.running = False
        for client in self.clients:
            client.stop()
        self.server_socket.close()

    def broadcast(self, message, sender=None):
        for client in self.clients:
            if client != sender:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    self.remove_client(client)

    def remove_client(self, client):
        if client in self.clients:
            self.clients.remove(client)
            self.client_disconnected.emit(f"{client.address[0]}:{client.address[1]}")

class ClientHandler(threading.Thread):
    def __init__(self, socket, address, server):
        super().__init__()
        self.socket = socket
        self.address = address
        self.server = server
        self.running = True

    def run(self):
        while self.running:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                if data.startswith("FILE:"):
                    # Fayl qəbulu
                    file_info = data[5:].split("|")
                    file_name = file_info[0]
                    file_size = int(file_info[1])
                    
                    self.socket.send("READY".encode('utf-8'))
                    
                    received = 0
                    file_data = b""
                    while received < file_size:
                        chunk = self.socket.recv(4096)
                        if not chunk:
                            break
                        file_data += chunk
                        received += len(chunk)
                    
                    # Faylı yadda saxla
                    downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")
                    if not os.path.exists(downloads_dir):
                        os.makedirs(downloads_dir)
                    
                    file_path = os.path.join(downloads_dir, file_name)
                    with open(file_path, "wb") as f:
                        f.write(file_data)
                    
                    self.server.file_received.emit(f"{self.address[0]} fayl göndərdi: {file_name}")
                    self.server.broadcast(f"{self.address[0]} fayl göndərdi: {file_name}", self)
                else:
                    # Mesajı yayımla
                    message = f"{self.address[0]}: {data}"
                    self.server.new_message.emit(message)
                    self.server.broadcast(message, self)
                    
            except Exception as e:
                print(f"ClientHandler xətası: {e}")
                break
                
        self.server.remove_client(self)
        self.socket.close()

    def send(self, message):
        try:
            self.socket.send(message.encode('utf-8'))
        except:
            self.server.remove_client(self)

    def stop(self):
        self.running = False
        self.socket.close()

class ClientConnection(QThread):
    message_received = pyqtSignal(str)
    file_received = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.socket = None
        self.running = True

    def run(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.message_received.emit(f"{self.host}:{self.port} serverinə qoşuldu...")
            
            while self.running:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break
                    
                if data == "READY":
                    # Fayl göndərmə hazırlığı
                    continue
                    
                self.message_received.emit(data)
                
        except Exception as e:
            self.message_received.emit(f"Bağlantı xətası: {str(e)}")
            
    def send_message(self, message):
        if self.socket:
            try:
                self.socket.send(message.encode('utf-8'))
            except:
                self.message_received.emit("Mesaj göndərilmədi")

    def send_file(self, file_path):
        if self.socket:
            try:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                
                # Fayl məlumatlarını göndər
                self.socket.send(f"FILE:{file_name}|{file_size}".encode('utf-8'))
                
                # Cavab gözlə
                response = self.socket.recv(4096).decode('utf-8')
                if response == "READY":
                    # Faylı göndər
                    with open(file_path, "rb") as f:
                        data = f.read()
                        self.socket.sendall(data)
                
                self.message_received.emit(f"Fayl göndərildi: {file_name}")
            except Exception as e:
                self.message_received.emit(f"Fayl göndərilmədi: {str(e)}")

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.client_connection = None
        self.is_server = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('IP Chat və Fayl Paylaşım Proqramı')
        self.setGeometry(100, 100, 900, 600)
        
        # Mərkəzi widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Əsas layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Sol panel (istifadəçi siyahısı)
        left_panel = QVBoxLayout()
        user_label = QLabel('Qoşulmuş İstifadəçilər:')
        user_label.setFont(QFont('Arial', 10, QFont.Bold))
        left_panel.addWidget(user_label)
        
        self.user_list = QListWidget()
        left_panel.addWidget(self.user_list)
        
        main_layout.addLayout(left_panel, 1)
        
        # Sağ panel (chat və giriş)
        right_panel = QVBoxLayout()
        
        # Chat hissəsi
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        right_panel.addWidget(self.chat_display, 3)
        
        # Giriş hissəsi
        input_layout = QHBoxLayout()
        
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText('Mesajınızı yazın...')
        self.message_input.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.message_input, 3)
        
        self.send_button = QPushButton('Göndər')
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button, 1)
        
        self.file_button = QPushButton('Fayl Göndər')
        self.file_button.clicked.connect(self.send_file)
        input_layout.addWidget(self.file_button, 1)
        
        right_panel.addLayout(input_layout, 1)
        
        main_layout.addLayout(right_panel, 3)
        
        # Status bar
        self.statusBar().showMessage('Hazır')
        
        # Menyu bar
        menubar = self.menuBar()
        
        # Server menyusu
        server_menu = menubar.addMenu('Server')
        
        start_server_action = QAction('Server İşə Sal', self)
        start_server_action.triggered.connect(self.start_server)
        server_menu.addAction(start_server_action)
        
        stop_server_action = QAction('Server Dayandır', self)
        stop_server_action.triggered.connect(self.stop_server)
        server_menu.addAction(stop_server_action)
        
        # Client menyusu
        client_menu = menubar.addMenu('Client')
        
        connect_action = QAction('Serverə Qoşul', self)
        connect_action.triggered.connect(self.connect_to_server)
        client_menu.addAction(connect_action)
        
        disconnect_action = QAction('Serverdən Ayrıl', self)
        disconnect_action.triggered.connect(self.disconnect_from_server)
        client_menu.addAction(disconnect_action)
        
        # Çıxış
        exit_action = QAction('Çıxış', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)
        
    def start_server(self):
        from PyQt5.QtWidgets import QInputDialog
        
        port, ok = QInputDialog.getInt(self, 'Server Portu', 'Port nömrəsini daxil edin:', 12345, 1024, 65535, 1)
        if ok:
            # Öz IP ünvanımızı alaq
            host = self.get_local_ip()
            
            self.server_thread = ServerThread(host, port)
            self.server_thread.new_message.connect(self.display_message)
            self.server_thread.new_client.connect(self.add_client)
            self.server_thread.client_disconnected.connect(self.remove_client)
            self.server_thread.file_received.connect(self.display_message)
            self.server_thread.start()
            
            self.is_server = True
            self.display_message(f"Server {host}:{port} ünvanında işə salındı")
            self.statusBar().showMessage(f'Server modu: {host}:{port}')
            
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
            
    def stop_server(self):
        if self.server_thread:
            self.server_thread.stop()
            self.server_thread.wait()
            self.display_message("Server dayandırıldı")
            self.statusBar().showMessage('Server dayandırıldı')
            self.user_list.clear()
            self.is_server = False
            
    def connect_to_server(self):
        from PyQt5.QtWidgets import QInputDialog
        
        host, ok = QInputDialog.getText(self, 'Server Ünvanı', 'Server IP ünvanını daxil edin:')
        if ok and host:
            port, ok = QInputDialog.getInt(self, 'Server Portu', 'Port nömrəsini daxil edin:', 12345, 1024, 65535, 1)
            if ok:
                self.client_connection = ClientConnection(host, port)
                self.client_connection.message_received.connect(self.display_message)
                self.client_connection.file_received.connect(self.display_message)
                self.client_connection.start()
                
                self.statusBar().showMessage(f'Serverə qoşuldu: {host}:{port}')
                
    def disconnect_from_server(self):
        if self.client_connection:
            self.client_connection.stop()
            self.client_connection.wait()
            self.display_message("Serverdən ayrıldınız")
            self.statusBar().showMessage('Serverdən ayrıldı')
            
    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            if self.is_server and self.server_thread:
                self.server_thread.broadcast(f"Server: {message}")
                self.display_message(f"Siz: {message}")
            elif self.client_connection:
                self.client_connection.send_message(message)
                self.display_message(f"Siz: {message}")
            else:
                self.display_message("Bağlantı yoxdur")
                
            self.message_input.clear()
            
    def send_file(self):
        if not (self.is_server or self.client_connection):
            QMessageBox.warning(self, "Xəbərdarlıq", "Əvvəlcə serverə qoşulun və ya server yaradın")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Fayl Seç", 
            os.path.expanduser("~"),
            "Bütün fayllar (*.*);;Şəkillər (*.jpg *.jpeg *.png *.gif);;Səs faylları (*.mp3 *.wav);;Sənədlər (*.pdf *.doc *.docx);;Arxivlər (*.rar *.zip)"
        )
        
        if file_path:
            if self.is_server and self.server_thread:
                # Server modunda bütün clientlərə fayl göndəririk
                for client in self.server_thread.clients:
                    try:
                        file_name = os.path.basename(file_path)
                        file_size = os.path.getsize(file_path)
                        
                        client.send(f"FILE:{file_name}|{file_size}".encode('utf-8'))
                        
                        response = client.socket.recv(4096).decode('utf-8')
                        if response == "READY":
                            with open(file_path, "rb") as f:
                                data = f.read()
                                client.socket.sendall(data)
                                
                        self.display_message(f"Fayl göndərildi: {file_name}")
                    except Exception as e:
                        self.display_message(f"Fayl göndərilmədi: {str(e)}")
            elif self.client_connection:
                # Client modunda faylı serverə göndəririk
                self.client_connection.send_file(file_path)
                
    def display_message(self, message):
        self.chat_display.append(message)
        
    def add_client(self, client_info):
        self.user_list.addItem(client_info)
        
    def remove_client(self, client_info):
        items = self.user_list.findItems(client_info, Qt.MatchExactly)
        for item in items:
            row = self.user_list.row(item)
            self.user_list.takeItem(row)
            
    def closeEvent(self, event):
        self.stop_server()
        self.disconnect_from_server()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChatWindow()
    window.show()
    sys.exit(app.exec_())