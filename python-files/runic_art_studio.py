import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QColorDialog, QFileDialog, QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint

class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.white)
        self.last_point = QPoint()
        self.brush_color = Qt.black
        self.brush_size = 3

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            painter = QPainter(self.pixmap)
            pen = QPen(self.brush_color, self.brush_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.pos())
            self.last_point = event.pos()
            self.update()

    def clear(self):
        self.pixmap.fill(Qt.white)
        self.update()

class RunicArtStudio(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Runic Art Studio")
        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)
        self.initUI()

    def initUI(self):
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.canvas.clear)
        file_menu.addAction(clear_action)

        # Brush menu
        brush_menu = menubar.addMenu("Brush")
        color_action = QAction("Select Color", self)
        color_action.triggered.connect(self.select_color)
        brush_menu.addAction(color_action)

    def select_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.canvas.brush_color = color

    def save(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if path:
            self.canvas.pixmap.save(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RunicArtStudio()
    window.show()
    sys.exit(app.exec_())
