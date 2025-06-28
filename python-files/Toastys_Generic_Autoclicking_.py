import sys
import threading
import time
import ctypes
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QSizePolicy
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt

# ctypes mouse click constants
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
user32 = ctypes.windll.user32

def click_mouse():
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

CLICK_INTERVAL = 0.1
clicking = False

def click_loop():
    while clicking:
        click_mouse()
        time.sleep(CLICK_INTERVAL)

class AutoClickerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Toastys Generic Autoclicker")
        self.setFixedSize(600, 600)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")

        # Header label (top bar style)
        self.header_label = QLabel("Toastys Generic Studio")
        self.header_label.setFixedHeight(60)
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("background-color: #3e3e3e; font-weight: bold;")
        self.header_label.setFont(QFont("Comic Sans MS", 24))

        # Title label
        self.title_label = QLabel("Toastys Generic\nAutoclicker!")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Comic Sans MS", 36, QFont.Weight.Bold))
        self.title_label.setContentsMargins(0, 40, 0, 40)

        # Buttons
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")

        # Button styles
        btn_style = """
            QPushButton {
                background-color: #4e4e4e; 
                color: white; 
                font: 24pt "Comic Sans MS"; 
                border-radius: 10px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #505050;
            }
            QPushButton:disabled {
                background-color: #2f2f2f;
                color: #777777;
            }
        """
        self.start_btn.setStyleSheet(btn_style)
        self.stop_btn.setStyleSheet(btn_style)
        self.stop_btn.setDisabled(True)

        self.start_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Layout for buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(60)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)

        # Main vertical layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.header_label)
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(btn_layout)
        main_layout.setContentsMargins(40, 20, 40, 20)
        main_layout.setSpacing(40)

        self.setLayout(main_layout)

        # Connect buttons
        self.start_btn.clicked.connect(self.start_clicking)
        self.stop_btn.clicked.connect(self.stop_clicking)

        self.clicking = False
        self.click_thread = None

    def start_clicking(self):
        global clicking
        if not self.clicking:
            self.clicking = True
            clicking = True
            self.start_btn.setDisabled(True)
            self.stop_btn.setEnabled(True)
            self.click_thread = threading.Thread(target=click_loop, daemon=True)
            self.click_thread.start()

    def stop_clicking(self):
        global clicking
        self.clicking = False
        clicking = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setDisabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Optional: Dark Fusion style for more modern dark look
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(46, 46, 46))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(78, 78, 78))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    app.setPalette(palette)

    window = AutoClickerWindow()
    window.show()

    sys.exit(app.exec())