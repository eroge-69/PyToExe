import sys
import threading
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt
from pynput import keyboard
from pynput.keyboard import Controller

class KeySpammer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tuş Spam Uygulaması")
        self.setStyleSheet("background-color: #f4f4f4; font-size: 16px;")
        self.setFixedSize(300, 320)

        self.layout = QVBoxLayout()

        # Tuş bilgileri
        self.label1 = QLabel("1. Atanmış Tuş: Yok")
        self.label1.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label1)

        self.button1 = QPushButton("1. Tuş Ata")
        self.button1.clicked.connect(self.assign_key1)
        self.button1.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.button1)

        self.label2 = QLabel("2. Atanmış Tuş: Yok")
        self.label2.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label2)

        self.button2 = QPushButton("2. Tuş Ata")
        self.button2.clicked.connect(self.assign_key2)
        self.button2.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.button2)

        # Başla / Durdur
        self.start_button = QPushButton("Başla")
        self.start_button.clicked.connect(self.start_spam)
        self.start_button.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Durdur")
        self.stop_button.clicked.connect(self.stop_spam)
        self.stop_button.setStyleSheet("padding: 10px;")
        self.layout.addWidget(self.stop_button)

        self.setLayout(self.layout)

        # Durumlar
        self.spam_thread1 = None
        self.spam_thread2 = None
        self.running = False
        self.assigned_key1 = None
        self.assigned_key2 = None
        self.keyboard_controller = Controller()

    def assign_key1(self):
        self.label1.setText("Bir tuşa bas (1)...")
        self.assigned_key1 = None

        def on_press(key):
            try:
                self.assigned_key1 = key.char
            except AttributeError:
                self.assigned_key1 = key.name
            self.label1.setText(f"1. Atanmış Tuş: {self.assigned_key1}")
            listener.stop()

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def assign_key2(self):
        self.label2.setText("Bir tuşa bas (2)...")
        self.assigned_key2 = None

        def on_press(key):
            try:
                self.assigned_key2 = key.char
            except AttributeError:
                self.assigned_key2 = key.name
            self.label2.setText(f"2. Atanmış Tuş: {self.assigned_key2}")
            listener.stop()

        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def spam_key(self, key, delay):
        while self.running:
            if key:
                try:
                    self.keyboard_controller.press(key)
                    self.keyboard_controller.release(key)
                except Exception as e:
                    print("Hata:", e)
            time.sleep(delay)

    def start_spam(self):
        if not self.assigned_key1 or not self.assigned_key2:
            QMessageBox.warning(self, "Uyarı", "Lütfen her iki tuşu da atayın!")
            return
        if not self.running:
            self.running = True
            self.spam_thread1 = threading.Thread(target=self.spam_key, args=(self.assigned_key1, 0.5))
            self.spam_thread2 = threading.Thread(target=self.spam_key, args=(self.assigned_key2, 0.1))
            self.spam_thread1.start()
            self.spam_thread2.start()
            self.label1.setText(f"Spam Başladı: {self.assigned_key1}")
            self.label2.setText(f"Spam Başladı: {self.assigned_key2}")

    def stop_spam(self):
        self.running = False
        self.label1.setText(f"1. Tuş Spam Durduruldu")
        self.label2.setText(f"2. Tuş Spam Durduruldu")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KeySpammer()
    window.show()
    sys.exit(app.exec_())

