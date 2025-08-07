from PyQt5 import QtWidgets, QtGui, QtCore
import sys
import colorsys

class RGBBorderWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Window setup
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(QtWidgets.QApplication.desktop().screenGeometry())

        # Border and color flow setup
        self.border_thickness = 10
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_color)
        self.timer.start(50)  # update every 50 ms
        self.hue = 0
        self.current_color = QtGui.QColor(255, 0, 0)  # Start red

    def update_color(self):
        self.hue = (self.hue + 0.005) % 1.0
        r, g, b = colorsys.hsv_to_rgb(self.hue, 1.0, 1.0)
        self.current_color = QtGui.QColor(int(r * 255), int(g * 255), int(b * 255))
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setBrush(self.current_color)
        painter.setPen(QtCore.Qt.NoPen)

        w = self.width()
        h = self.height()
        t = self.border_thickness

        # Draw top, bottom, left, right borders
        painter.drawRect(0, 0, w, t)           # Top
        painter.drawRect(0, h - t, w, t)       # Bottom
        painter.drawRect(0, 0, t, h)           # Left
        painter.drawRect(w - t, 0, t, h)       # Right

def run_app():
    app = QtWidgets.QApplication(sys.argv)
    window = RGBBorderWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    run_app()