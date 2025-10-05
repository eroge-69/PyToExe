import sys
import threading
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QColorDialog
import keyboard  # global hotkeys

class OverlayRect(QtWidgets.QWidget):
    def __init__(self, color, geometry):
        super().__init__()
        self.color = QtGui.QColor(color)
        self.setGeometry(*geometry)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setCursor(QtCore.Qt.SizeAllCursor)
        self.drag_pos = None
        self.resizing = False
        self.resize_margin = 10

    def paintEvent(self, _):
        p = QtGui.QPainter(self)
        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.setBrush(QtGui.QBrush(self.color))
        p.setPen(QtGui.QPen(QtCore.Qt.black, 2))
        p.drawRect(self.rect())

    def mousePressEvent(self, e):
        r = self.rect()
        self.resizing = (
            r.right() - self.resize_margin <= e.x() <= r.right()
            and r.bottom() - self.resize_margin <= e.y() <= r.bottom()
        )
        self.drag_pos = e.globalPos()
        e.accept()

    def mouseMoveEvent(self, e):
        if not self.drag_pos:
            return
        diff = e.globalPos() - self.drag_pos
        if self.resizing:
            self.resize(max(50, self.width() + diff.x()),
                        max(50, self.height() + diff.y()))
        else:
            self.move(self.x() + diff.x(), self.y() + diff.y())
        self.drag_pos = e.globalPos()
        e.accept()

    def mouseReleaseEvent(self, e):
        self.drag_pos = None
        self.resizing = False
        e.accept()

    def mouseDoubleClickEvent(self, e):
        new_color = QColorDialog.getColor(self.color, self, "Choose color")
        if new_color.isValid():
            self.color = new_color
            self.update()


class OverlayController(QtWidgets.QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)

        self.rects = [
            OverlayRect("black", (0, 0, 1950, 80)),
            OverlayRect("black", (0, 985, 1950, 150))
        ]
        for r in self.rects:
            r.show()

        self.visible = True

        # Start a background thread to listen for global Ctrl+H
        threading.Thread(target=self.setup_global_hotkey, daemon=True).start()

    def setup_global_hotkey(self):
        keyboard.add_hotkey('ctrl+m', lambda: QtCore.QTimer.singleShot(0, self.toggle_visibility))
        keyboard.wait()  # keep thread alive

    def toggle_visibility(self):
        self.visible = not self.visible
        for r in self.rects:
            if self.visible:
                r.show()
                r.raise_()
            else:
                r.hide()


if __name__ == "__main__":
    app = OverlayController(sys.argv)
    sys.exit(app.exec_())
