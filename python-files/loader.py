import sys
import ctypes # Import ctypes for Windows API calls
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QFont
from PyQt5.QtCore import Qt, QTimer

# Windows API constants for hotkeys
MOD_NOREPEAT = 0x4000 # Prevents multiple hotkey notifications if key is held
MOD_WIN = 0x0008    # The Windows key itself (not used as modifier for VK_LWIN/VK_RWIN, but for identifying the key)
VK_LWIN = 0x5B      # Left Windows key virtual key code
VK_RWIN = 0x5C      # Right Windows key virtual key code

class RGBBorderWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Гемесенсе")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: black;")
        self.rgb_phase = 0
        self.rgb_colors = [
            (255, 0, 0),    # Red
            (255, 127, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (75, 0, 130),   # Indigo
            (148, 0, 211),  # Violet
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rgb)
        self.timer.start(42)

        # Hotkey IDs for Windows key blocking
        self._hotkey_id_lwin = 1000
        self._hotkey_id_rwin = 1001

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Authorization")
        title.setStyleSheet("color: white;")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        user_layout = QHBoxLayout()
        user_label = QLabel("Username:")
        user_label.setStyleSheet("color: white;")
        self.user_edit = QLineEdit() # Stored as instance variable
        self.user_edit.setStyleSheet("background-color: #222; color: white; border: 1px solid #444;")
        user_layout.addWidget(user_label)
        user_layout.addWidget(self.user_edit)
        layout.addLayout(user_layout)

        pass_layout = QHBoxLayout()
        pass_label = QLabel("Password:")
        pass_label.setStyleSheet("color: white;")
        self.pass_edit = QLineEdit() # Stored as instance variable
        self.pass_edit.setEchoMode(QLineEdit.Password)
        self.pass_edit.setStyleSheet("background-color: #222; color: white; border: 1px solid #444;")
        pass_layout.addWidget(pass_label)
        pass_layout.addWidget(self.pass_edit)
        layout.addLayout(pass_layout)

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(
            "QPushButton { background-color: #333; color: white; border: 1px solid #555; padding: 6px 20px; }"
            "QPushButton:hover { background-color: #444; }"
        )
        login_btn.clicked.connect(self.check_credentials) # Connect button to new method
        layout.addWidget(login_btn, alignment=Qt.AlignCenter)

        self.error_label = QLabel("") # Label for error messages
        self.error_label.setStyleSheet("color: red;")
        self.error_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.error_label)

        self.setLayout(layout)

    def update_rgb(self):
        self.rgb_phase = (self.rgb_phase + 1) % len(self.rgb_colors)
        self.update()

    def check_credentials(self):
        username = self.user_edit.text()
        password = self.pass_edit.text()

        if username == "user" and password == "pass":
            self.error_label.setStyleSheet("color: green;")
            self.error_label.setText("Login successful!")
            self.block_keyboard_and_win_key()  # Block keyboard and Windows key
            QTimer.singleShot(10000, self.unblock_keyboard_and_win_key) # Unblock after 10 seconds
            # Open the new window and close the current one
            self.success_window = SuccessWindow()
            self.success_window.showFullScreen()
            self.close()
        else:
            self.error_label.setStyleSheet("color: red;")
            self.error_label.setText("Invalid username or password.")

    def block_keyboard_and_win_key(self):
        # Block all keyboard and mouse input using BlockInput
        ctypes.windll.user32.BlockInput(True)
        # Block Windows key using hotkeys
        # RegisterHotKey needs a window handle. self.winId() provides it.
        # MOD_NOREPEAT ensures hotkey is not triggered repeatedly when key is held.
        hwnd = int(self.winId())
        ctypes.windll.user32.RegisterHotKey(hwnd, self._hotkey_id_lwin, MOD_NOREPEAT, VK_LWIN)
        ctypes.windll.user32.RegisterHotKey(hwnd, self._hotkey_id_rwin, MOD_NOREPEAT, VK_RWIN)

    def unblock_keyboard_and_win_key(self):
        # Unblock all keyboard and mouse input
        ctypes.windll.user32.BlockInput(False)
        # Unblock Windows key by unregistering hotkeys
        hwnd = int(self.winId())
        ctypes.windll.user32.UnregisterHotKey(hwnd, self._hotkey_id_lwin)
        ctypes.windll.user32.UnregisterHotKey(hwnd, self._hotkey_id_rwin)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen_width = 3
        steps = len(self.rgb_colors)
        w, h = self.width(), self.height()
        for i in range(steps):
            color = QColor(*self.rgb_colors[(self.rgb_phase + i) % steps])
            pen = QPen(color, pen_width)
            painter.setPen(pen)
            # Draw each side with a different color
            if i == 0:
                # Top
                painter.drawLine(pen_width//2, pen_width//2, w-pen_width//2, pen_width//2)
            elif i == 1:
                # Right
                painter.drawLine(w-pen_width//2, pen_width//2, w-pen_width//2, h-pen_width//2)
            elif i == 2:
                # Bottom
                painter.drawLine(w-pen_width//2, h-pen_width//2, pen_width//2, h-pen_width//2)
            elif i == 3:
                # Left
                painter.drawLine(pen_width//2, h-pen_width//2, pen_width//2, pen_width//2)
            # For more RGB steps, interpolate along the sides (optional)


class SuccessWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("СОСИ ХУЙ ПИДОРАС")
        self.setStyleSheet("background-color: pink;")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        message_label = QLabel("ПОБАЛЯКАЙ МОИ ЯЙЦА")
        message_label.setStyleSheet("color: black;")
        message_label.setFont(QFont("Arial", 120, QFont.Bold))
        message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(message_label)
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RGBBorderWindow()
    window.show()
    sys.exit(app.exec_())
