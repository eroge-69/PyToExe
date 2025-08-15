import sys
import json
import socket
import threading
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QTextEdit, QLineEdit, QPushButton, 
                            QListWidget, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
import pyaudio
import webrtcvad
import numpy as np
from cryptography.fernet import Fernet

class VoiceCallWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Голосовой звонок")
        self.setGeometry(100, 100, 300, 150)
        
        self.layout = QVBoxLayout()
        
        self.status_label = QLabel("Статус звонка")
        self.layout.addWidget(self.status_label)
        
        self.end_call_btn = QPushButton("Завершить звонок")
        self.end_call_btn.clicked.connect(self.end_call)
        self.layout.addWidget(self.end_call_btn)
        
        self.setLayout(self.layout)
        
        # Настройка аудио
        self.audio = pyaudio.PyAudio()
        self.vad = webrtcvad.Vad(3)  # Агрессивный режим VAD
        self.stream_in = None
        self.stream_out = None
        self.calling = False
        
    def start_call(self, remote_ip):
        self.status_label.setText(f"Звонок: {remote_ip}")
        self.calling = True
        self.start_audio_streams()
        
    def end_call(self):
        self.calling = False
        if self.stream_in:
            self.stream_in.stop_stream()
            self.stream_in.close()
        if self.stream_out:
            self.stream_out.stop_stream()
            self.stream_out.close()
        self.close()
        
    def start_audio_streams(self):
        # В реальном приложении здесь было бы подключение к WebRTC или другому VoIP протоколу
        # Это упрощенная версия только для демонстрации
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        CHUNK = 480
        
        def callback(in_data, frame_count, time_info, status):
            if self.calling:
                # Здесь должен быть код передачи аудио по сети
                return (in_data, pyaudio.paContinue)
            return (None, pyaudio.paComplete)
            
        self.stream_in = self.audio.open(format=FORMAT, channels=CHANNELS,
                                        rate=RATE, input=True,
                                        frames_per_buffer=CHUNK,
                                        stream_callback=callback)
        
        self.stream_out = self.audio.open(format=FORMAT, channels=CHANNELS,
                                         rate=RATE, output=True,
                                         frames_per_buffer=CHUNK)
        
        self.stream_in.start_stream()
        self.stream_out.start_stream()

class ChatClient:
    def __init__(self, server_ip, server_port, username):
        self.server_ip = server_ip
        self.server_port = server_port
        self.username = username
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
        
    def connect(self):
        try:
            self.socket.connect((self.server_ip, self.server_port))
            # Отправляем имя пользователя и ключ шифрования
            auth_data = {
                'username': self.username,
                'key': self.encryption_key.decode()
            }
            self.socket.send(json.dumps(auth_data).encode())
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
            
    def send_message(self, message, recipient):
        try:
            encrypted_msg = self.cipher.encrypt(message.encode())
            data = {
                'type': 'message',
                'to': recipient,
                'message': encrypted_msg.decode()
            }
            self.socket.send(json.dumps(data).encode())
            return True
        except Exception as e:
            print(f"Send error: {e}")
            return False
            
    def start_call(self, recipient):
        try:
            data = {
                'type': 'call_request',
                'to': recipient
            }
            self.socket.send(json.dumps(data).encode())
            return True
        except Exception as e:
            print(f"Call error: {e}")
            return False
            
    def receive_data(self):
        while self.connected:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                    
                decoded_data = json.loads(data.decode())
                return decoded_data
            except Exception as e:
                print(f"Receive error: {e}")
                break
        return None

class CorporateMessenger(QMainWindow):
    call_requested = pyqtSignal(str)  # Сигнал о входящем звонке
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Корпоративный мессенджер")
        self.setGeometry(100, 100, 800, 600)
        
        # Инициализация клиента (в реальном приложении было бы окно входа)
        self.client = ChatClient('localhost', 5555, 'user1')
        if not self.client.connect():
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к серверу")
            sys.exit(1)
            
        self.init_ui()
        self.start_receive_thread()
        
        self.call_window = None
        self.call_requested.connect(self.handle_call_request)
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QHBoxLayout()
        
        # Список пользователей
        self.user_list = QListWidget()
        self.user_list.addItems(["user2", "user3", "user4"])  # В реальном приложении получали бы с сервера
        self.user_list.currentItemChanged.connect(self.user_selected)
        main_layout.addWidget(self.user_list, 1)
        
        # Область чата
        chat_widget = QWidget()
        chat_layout = QVBoxLayout()
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        chat_layout.addWidget(self.chat_display, 4)
        
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        chat_layout.addWidget(self.message_input, 1)
        
        button_layout = QHBoxLayout()
        self.send_btn = QPushButton("Отправить")
        self.send_btn.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_btn)
        
        self.call_btn = QPushButton("Позвонить")
        self.call_btn.clicked.connect(self.start_call)
        button_layout.addWidget(self.call_btn)
        
        chat_layout.addLayout(button_layout)
        chat_widget.setLayout(chat_layout)
        main_layout.addWidget(chat_widget, 3)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
    def user_selected(self, item):
        self.current_recipient = item.text()
        self.chat_display.clear()
        # Здесь должна быть загрузка истории сообщений с выбранным пользователем
        
    def send_message(self):
        message = self.message_input.text()
        if message and hasattr(self, 'current_recipient'):
            if self.client.send_message(message, self.current_recipient):
                self.chat_display.append(f"Вы: {message}")
                self.message_input.clear()
                
    def start_call(self):
        if hasattr(self, 'current_recipient'):
            if self.client.start_call(self.current_recipient):
                self.call_window = VoiceCallWindow(self)
                self.call_window.show()
                # В реальном приложении здесь было бы установление соединения WebRTC
                
    def start_receive_thread(self):
        def receive_loop():
            while True:
                data = self.client.receive_data()
                if data:
                    if data['type'] == 'message':
                        decrypted_msg = self.client.cipher.decrypt(data['message'].encode()).decode()
                        self.chat_display.append(f"{data['from']}: {decrypted_msg}")
                    elif data['type'] == 'call_request':
                        self.call_requested.emit(data['from'])
                        
        thread = threading.Thread(target=receive_loop, daemon=True)
        thread.start()
        
    def handle_call_request(self, caller):
        reply = QMessageBox.question(self, "Входящий звонок", 
                                   f"{caller} звонит вам. Принять звонок?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.call_window = VoiceCallWindow(self)
            self.call_window.start_call(caller)
            self.call_window.show()
            # В реальном приложении здесь было бы подтверждение звонка на сервере
            
    def closeEvent(self, event):
        if self.call_window:
            self.call_window.end_call()
        self.client.socket.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    messenger = CorporateMessenger()
    messenger.show()
    sys.exit(app.exec_())