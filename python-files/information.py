import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

app = QApplication(sys.argv)

window = QWidget()
window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
window.setStyleSheet("background-color: blue;")

label = QLabel("We know everything now!", window)
label.setAlignment(Qt.AlignCenter)
label.setStyleSheet("color: white;")
label.setFont(QFont("Arial", 32, QFont.Bold))

window.showFullScreen()
label.resize(window.size())

sys.exit(app.exec_())