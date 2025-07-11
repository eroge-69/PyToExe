import sys
import threading
import keyboard
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt

class PRDRWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("prdr")
        self.setGeometry(300, 300, 400, 200)
        self.set_dark_theme()
        self.active = False

        layout = QVBoxLayout()

        self.welcome = QLabel("Mahan jan kose nanat")
        self.welcome.setFont(QFont("B Nazanin", 20, QFont.Bold))
        self.welcome.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.welcome)

        self.toggle_btn = QPushButton("madar mahan jan")
        self.toggle_btn.setFont(QFont("B Nazanin", 16))
        self.toggle_btn.clicked.connect(self.toggle)
        layout.addWidget(self.toggle_btn)

        self.setLayout(layout)

        self.listener_thread = threading.Thread(target=self.listen_keys, daemon=True)
        self.listener_thread.start()

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, Qt.white)
        self.setPalette(palette)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #fff; }
            QPushButton { background-color: #222; color: #fff; border-radius: 8px; padding: 8px; }
            QLabel { color: #00ffd0; }
        """)

    def toggle(self):
        self.active = not self.active
        if self.active:
            self.toggle_btn.setText("babaye mahan jan")
            self.welcome.setText(" Ctrl+F = Undo")
        else:
            self.toggle_btn.setText("madar mahan jan")
            self.welcome.setText("Mahan jan kose nanat")

    def listen_keys(self):
        while True:
            keyboard.wait('ctrl+f')
            if self.active:
                # شبیه‌سازی Ctrl+Z
                keyboard.send('ctrl+z')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PRDRWindow()
    window.show()
    sys.exit(app.exec_())