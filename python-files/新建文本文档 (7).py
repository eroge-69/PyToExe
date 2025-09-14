import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QColorDialog, QSpinBox, QFileDialog, QHBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
from PIL import ImageGrab

class ScreenshotAnnotator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot & Annotate")
        self.setGeometry(100, 100, 900, 650)

        self.label = QLabel(self)
        self.label.setGeometry(0, 0, 900, 550)
        self.pixmap = QPixmap(900, 550)
        self.pixmap.fill(Qt.white)
        self.label.setPixmap(self.pixmap)

        self.start_point = QPoint()
        self.end_point = QPoint()
        self.drawing = False
        self.pen_color = Qt.red
        self.pen_width = 3

        # Buttons
        self.btn_screenshot = QPushButton("Take Screenshot", self)
        self.btn_screenshot.setGeometry(10, 560, 150, 30)
        self.btn_screenshot.clicked.connect(self.take_screenshot)

        self.btn_color = QPushButton("Choose Color", self)
        self.btn_color.setGeometry(170, 560, 120, 30)
        self.btn_color.clicked.connect(self.choose_color)

        self.spin_width = QSpinBox(self)
        self.spin_width.setGeometry(300, 560, 60, 30)
        self.spin_width.setRange(1, 20)
        self.spin_width.setValue(3)
        self.spin_width.valueChanged.connect(self.change_width)

        self.btn_save = QPushButton("Save Image", self)
        self.btn_save.setGeometry(370, 560, 120, 30)
        self.btn_save.clicked.connect(self.save_image)

    def take_screenshot(self):
        img = ImageGrab.grab()
        img.save("screenshot_temp.png")
        self.pixmap.load("screenshot_temp.png")
        self.label.setPixmap(self.pixmap)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.pen_color = color

    def change_width(self, value):
        self.pen_width = value

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.label.underMouse():
            self.start_point = event.pos()
            self.drawing = True

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = event.pos()
            temp_pixmap = QPixmap(self.pixmap)
            painter = QPainter(temp_pixmap)
            pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.start_point, self.end_point)
            painter.end()
            self.label.setPixmap(temp_pixmap)
            self.start_point = self.end_point

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.pixmap = self.label.pixmap()

    def save_image(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "PNG Files (*.png);;JPEG Files (*.jpg)")
        if filename:
            self.pixmap.save(filename)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenshotAnnotator()
    window.show()
    sys.exit(app.exec_())
