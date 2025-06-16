from PyQt5 import QtWidgets, QtGui, QtCore
import sys

class TransparentLine(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Giant Arrow Aimer")
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.Tool
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setGeometry(0, 0, 1920, 1080)
        
        # Line settings
        self.line_length = 300
        self.line_angle = 0
        self.line_pos = QtCore.QPoint(960, 540)
        self.dragging = False

        self.show()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtCore.Qt.red, 3)
        painter.setPen(pen)
        
        rad = QtCore.qDegreesToRadians(self.line_angle)
        dx = self.line_length * QtCore.qCos(rad)
        dy = self.line_length * QtCore.qSin(rad)
        end_point = QtCore.QPointF(self.line_pos.x() + dx, self.line_pos.y() + dy)
        
        painter.drawLine(self.line_pos, end_point)

    def mousePressEvent(self, event):
        if self.point_near_line(event.pos()):
            self.dragging = True
            self.drag_offset = event.pos() - self.line_pos

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.line_pos = event.pos() - self.drag_offset
            self.update()

    def mouseReleaseEvent(self, event):
        self.dragging = False

    def wheelEvent(self, event):
        self.line_angle += event.angleDelta().y() / 8
        self.update()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Up:
            self.line_length += 10
        elif event.key() == QtCore.Qt.Key_Down:
            self.line_length -= 10
        self.update()

    def point_near_line(self, point):
        rad = QtCore.qDegreesToRadians(self.line_angle)
        dx = self.line_length * QtCore.qCos(rad)
        dy = self.line_length * QtCore.qSin(rad)
        end_point = QtCore.QPointF(self.line_pos.x() + dx, self.line_pos.y() + dy)
        
        line = QtCore.QLineF(self.line_pos, end_point)
        distance = line.p1().distanceToPoint(point)
        return distance < 10

app = QtWidgets.QApplication(sys.argv)
window = TransparentLine()
sys.exit(app.exec_())
