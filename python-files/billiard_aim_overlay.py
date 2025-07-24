
import sys
import math
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPoint, QTimer
import keyboard
import ctypes
import pyautogui

class AimOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Billiard Aim Helper")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.X11BypassWindowManagerHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.screen_geometry = QApplication.primaryScreen().geometry()
        self.setGeometry(self.screen_geometry)
        self.cue_ball_pos = None
        self.line_length = 300
        self.line_color = QColor(255, 0, 0)
        self.line_thickness = 2

        # Timer for redrawing
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

        # Hotkey setup
        keyboard.add_hotkey('s', self.set_cue_ball_position)

    def set_cue_ball_position(self):
        x, y = pyautogui.position()
        self.cue_ball_pos = QPoint(x, y)

    def paintEvent(self, event):
        if self.cue_ball_pos is None:
            return
        painter = QPainter(self)
        pen = QPen(self.line_color)
        pen.setWidth(self.line_thickness)
        painter.setPen(pen)

        mx, my = pyautogui.position()
        dx = mx - self.cue_ball_pos.x()
        dy = my - self.cue_ball_pos.y()
        angle = math.atan2(dy, dx)
        end_x = self.cue_ball_pos.x() + self.line_length * math.cos(angle)
        end_y = self.cue_ball_pos.y() + self.line_length * math.sin(angle)

        painter.drawLine(self.cue_ball_pos, QPoint(int(end_x), int(end_y)))

if __name__ == '__main__':
    # Make window click-through
    ctypes.windll.user32.SetProcessDPIAware()
    app = QApplication(sys.argv)
    overlay = AimOverlay()
    overlay.show()
    sys.exit(app.exec())
