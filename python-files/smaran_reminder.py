import sys
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QSystemTrayIcon, QMenu, QAction, qApp
)
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QIcon, QFont

# === Settings ===
INTERVAL_MS = 2 * 60 * 1000   # 10 minutes
POPUP_DURATION = 5000          # 2 seconds
POPUP_OPACITY = 0.70           # 30% opacity

# === Popup Window ===
class SmaranPopup(QWidget):
    def __init__(self):
        super().__init__()
        self._drag_active = False
        self._drag_position = QPoint()
        self.initUI()

    def initUI(self):
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(POPUP_OPACITY)
        self.resize(300, 100)
        self.move_to_center()

        self.label = QLabel("Smaran", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                font-size: 36px;
                color: white;
                background-color: rgba(0, 0, 0, 200);
                border-radius: 12px;
                padding: 10px;
            }
        """)

        # Stylish font
        self.label.setFont(QFont("Segoe Script", 36, QFont.Bold))
        self.label.setGeometry(0, 0, 300, 100)

        QTimer.singleShot(POPUP_DURATION, self.close)

    def move_to_center(self):
        # Using your fixed screen resolution: 1366 x 768
        screen_width = 1366
        screen_height = 768

        x = (screen_width - self.width()) // 2
        y = (screen_height - self.height()) // 2

        self.move(x, y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_active = True
            self._drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_active and event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_active = False

class SmaranApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        self.tray_icon = self.create_tray_icon()
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_smaran_popup)
        self.timer.start(INTERVAL_MS)
        self.show_smaran_popup()  # Show immediately

    def create_tray_icon(self):
        tray = QSystemTrayIcon()
        tray.setIcon(QIcon.fromTheme("face-smile") or QIcon("icon.png"))

        menu = QMenu()
        quit_action = QAction("Quit")
        quit_action.triggered.connect(qApp.quit)
        menu.addAction(quit_action)

        tray.setContextMenu(menu)
        tray.show()
        return tray

    def show_smaran_popup(self):
        self.popup = SmaranPopup()
        self.popup.show()

if __name__ == '__main__':
    app = SmaranApp(sys.argv)
    sys.exit(app.exec_())
