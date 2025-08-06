import sys
import socket
import sounddevice as sd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                             QPushButton, QLabel, QLineEdit, QComboBox, 
                             QGroupBox, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal

class AudioClientThread(QThread):
    update_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)

    def __init__(self, host, port, sample_rate, channels, parent=None):
        super().__init__(parent)
        self.host = host
        self.port = port
        self.sample_rate = sample_rate
        self.channels = channels
        self.running = True

    def run(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.port))
                self.update_signal.emit(f"Подключено к {self.host}:{self.port}")

                def callback(indata, frames, time, status):
                    if not self.running:
                        raise sd.CallbackAbort
                    s.sendall(indata.tobytes())
                
                with sd.InputStream(samplerate=self.sample_rate, channels=self.channels,
                                  dtype=np.int16, callback=callback):
                    while self.running:
                        pass

        except Exception as e:
            self.error_signal.emit(f"Ошибка: {str(e)}")
        finally:
            self.update_signal.emit("Клиент остановлен")

    def stop(self):
        self.running = False

class AudioClientGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.client_thread = None

    def initUI(self):
        self.setWindowTitle("Аудио Клиент")
        self.setGeometry(300, 300, 400, 300)

        # Основные элементы
        self.status_label = QLabel("Статус: Не подключен")
        self.connect_btn = QPushButton("Подключиться")
        self.disconnect_btn = QPushButton("Отключиться")
        self.disconnect_btn.setEnabled(False)

        # Настройки подключения
        connection_group = QGroupBox("Настройки подключения")
        self.server_ip = QLineEdit()
        self.server_ip.setPlaceholderText("Введите IP сервера")
        
        # Настройки звука
        audio_group = QGroupBox("Настройки звука")
        self.rate_combo = QComboBox()
        self.rate_combo.addItems(["44100", "48000", "96000"])
        self.channel_combo = QComboBox()
        self.channel_combo.addItems(["1 (Моно)", "2 (Стерео)"])
        
        # Layouts
        connection_layout = QVBoxLayout()
        connection_layout.addWidget(QLabel("IP сервера:"))
        connection_layout.addWidget(self.server_ip)
        connection_group.setLayout(connection_layout)

        audio_layout = QVBoxLayout()
        audio_layout.addWidget(QLabel("Частота дискретизации:"))
        audio_layout.addWidget(self.rate_combo)
        audio_layout.addWidget(QLabel("Каналы:"))
        audio_layout.addWidget(self.channel_combo)
        audio_group.setLayout(audio_layout)

        # Основной layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(connection_group)
        main_layout.addWidget(audio_group)
        main_layout.addWidget(self.connect_btn)
        main_layout.addWidget(self.disconnect_btn)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Подключение сигналов
        self.connect_btn.clicked.connect(self.start_client)
        self.disconnect_btn.clicked.connect(self.stop_client)

    def start_client(self):
        if self.client_thread and self.client_thread.isRunning():
            return

        host = self.server_ip.text().strip()
        if not host:
            QMessageBox.warning(self, "Ошибка", "Введите IP сервера")
            return

        port = 50007
        sample_rate = int(self.rate_combo.currentText())
        channels = 1 if self.channel_combo.currentIndex() == 0 else 2

        self.client_thread = AudioClientThread(host, port, sample_rate, channels)
        self.client_thread.update_signal.connect(self.update_status)
        self.client_thread.error_signal.connect(self.show_error)
        self.client_thread.start()

        self.connect_btn.setEnabled(False)
        self.disconnect_btn.setEnabled(True)
        self.update_status(f"Подключение к {host}:{port}...")

    def stop_client(self):
        if self.client_thread:
            self.client_thread.stop()
            self.client_thread.quit()
            self.client_thread.wait()
        self.connect_btn.setEnabled(True)
        self.disconnect_btn.setEnabled(False)
        self.update_status("Отключено")

    def update_status(self, message):
        self.status_label.setText(f"Статус: {message}")

    def show_error(self, message):
        self.status_label.setText(f"Ошибка: {message}")
        self.stop_client()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioClientGUI()
    window.show()
    sys.exit(app.exec_())