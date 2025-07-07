import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QLineEdit, QFileDialog, QMessageBox, QSpacerItem, QSizePolicy, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import qrcode
from PIL.ImageQt import ImageQt
import re

# === Встроенные модули кодировки ===

# --- verhoeff/v1.py ---
def verhoeff_checksum_v1(number: str) -> int:
    mul_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
    ]

    perm_table = [
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
        [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
        [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
        [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
        [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
        [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
        [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
    ]

    c = 0
    for i, item in enumerate(reversed(number)):
        c = mul_table[c][perm_table[(i + 1) % 8][int(item)]]
    return c

def full_encode_v1(number: int) -> str:
    alphabet = '!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_'
    result = ''
    checksum = verhoeff_checksum_v1(str(number))
    value = number * 10 + checksum
    while value:
        result = alphabet[value % len(alphabet)] + result
        value //= len(alphabet)
    return '!' + result

# --- verhoeff/v2.py ---
def verhoeff_checksum_v2(number: str) -> int:
    # Аналогичный алгоритм, но может отличаться (вставьте при необходимости)
    return verhoeff_checksum_v1(number)  # Заглушка, замените при необходимости

def full_encode_v2(number: int) -> str:
    alphabet = 'АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789!"#$%&\'()*+,-./:;<=>?@[\\]^_'
    result = ''
    checksum = verhoeff_checksum_v2(str(number))
    value = number * 10 + checksum
    while value:
        result = alphabet[value % len(alphabet)] + result
        value //= len(alphabet)
    return '*' + result

# === Графический интерфейс ===
class StickerEncoderGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WB Sticker Encoder")
        self.setWindowIcon(QIcon.fromTheme("document-save"))
        self.resize(600, 500)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Верхняя панель ввода
        self.inputField = QLineEdit()
        self.inputField.setPlaceholderText("Введите числовой идентификатор")
        self.inputField.textChanged.connect(self.onTextChanged)
        self.inputField.returnPressed.connect(self.onReturnPressed)

        self.encodedLabel = QLabel("Результат: ")

        topLayout = QHBoxLayout()
        topLayout.addWidget(QLabel("ID:"))
        topLayout.addWidget(self.inputField)
        topLayout.addWidget(self.encodedLabel)

        layout.addLayout(topLayout)

        # QR-код по центру
        self.qrLabel = QLabel("QR-код появится здесь")
        self.qrLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qrLabel)

        # Кнопки снизу
        bottomLayout = QHBoxLayout()

        self.saveButton = QPushButton("Сохранить")
        self.saveButton.setIcon(QIcon.fromTheme("document-save"))
        self.saveButton.clicked.connect(self.saveQRCode)

        self.printButton = QPushButton("Печать")
        self.printButton.setIcon(QIcon.fromTheme("printer"))
        self.printButton.clicked.connect(self.printQRCode)

        bottomLayout.addWidget(self.saveButton)
        bottomLayout.addWidget(self.printButton)
        layout.addLayout(bottomLayout)

        self.setLayout(layout)

    def onTextChanged(self, text):
        self.inputField.blockSignals(True)
        self.inputField.setText(re.sub(r'\D', '', text))
        self.inputField.blockSignals(False)

    def onReturnPressed(self):
        text = self.inputField.text()
        if not text.isdigit():
            return

        num = int(text)
        encoded = full_encode_v1(num) if num <= 4294967295 else full_encode_v2(num)
        self.encodedLabel.setText(f"Результат: {encoded}")

        qr = qrcode.make(encoded)
        pixmap = QPixmap.fromImage(ImageQt(qr))
        self.qrLabel.setPixmap(pixmap.scaled(300, 300, Qt.KeepAspectRatio))
        self.qrImage = qr

    def saveQRCode(self):
        if not hasattr(self, 'qrImage'):
            QMessageBox.warning(self, "Ошибка", "Сначала введите значение")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить QR-код", '', "PNG Files (*.png)")
        if path:
            self.qrImage.save(path)

    def printQRCode(self):
        if not hasattr(self, 'qrImage'):
            QMessageBox.warning(self, "Ошибка", "Сначала введите значение")
            return
        self.qrImage.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = StickerEncoderGUI()
    window.show()
    sys.exit(app.exec_())
