import sys
import numpy as np
import math
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit, QPushButton,
    QSlider, QLabel, QHBoxLayout, QCheckBox
)
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QTimer


safe_namespace = {
    "x": 0, "y": 0,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "exp": math.exp,
    "log": math.log,
    "sqrt": math.sqrt,
    "pi": math.pi,
    "e": math.e,
    "abs": abs
}


class SlopeFieldWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setMouseTracking(True)
        self.grid_size = 20
        self.field_density = 25
        self.zoom = 40
        self.func_text = "x - y"
        self.magnet_mode = False
        self.trails = False
        self.mouse_pos = (0, 0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

        self.particles = np.random.rand(300, 2) * [800, 800]

    def set_function(self, text):
        self.func_text = text

    def set_zoom(self, value):
        self.zoom = value

    def set_density(self, value):
        self.field_density = value

    def toggle_magnet(self):
        self.magnet_mode = not self.magnet_mode

    def toggle_trails(self, state):
        self.trails = bool(state)

    def mouseMoveEvent(self, event):
        self.mouse_pos = (event.x(), event.y())

    def paintEvent(self, event):
        painter = QPainter(self)
        if not self.trails:
            painter.fillRect(self.rect(), QColor(0, 0, 0))
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0, 20))

        pen = QPen(QColor(255, 255, 255))
        pen.setWidth(1)
        painter.setPen(pen)

        width = self.width()
        height = self.height()

        gx = np.linspace(0, width, self.field_density)
        gy = np.linspace(0, height, self.field_density)

        for x_screen in gx:
            for y_screen in gy:
                x = (x_screen - width / 2) / self.zoom
                y = (height / 2 - y_screen) / self.zoom

                try:
                    safe_namespace['x'] = x
                    safe_namespace['y'] = y
                    slope = eval(self.func_text, {"__builtins__": {}}, safe_namespace)
                except Exception:
                    continue

                angle = math.atan(slope)
                dx = math.cos(angle) * 8
                dy = -math.sin(angle) * 8

                if self.magnet_mode:
                    mx, my = self.mouse_pos
                    dist = math.hypot(x_screen - mx, y_screen - my)
                    strength = max(1, dist / 100)
                    dx += (mx - x_screen) / strength
                    dy += (my - y_screen) / strength

                x1 = x_screen - dx / 2
                y1 = y_screen - dy / 2
                x2 = x_screen + dx / 2
                y2 = y_screen + dy / 2

                painter.drawLine(int(x1), int(y1), int(x2), int(y2))

        if self.trails:
            for i, (px, py) in enumerate(self.particles):
                x = (px - width / 2) / self.zoom
                y = (height / 2 - py) / self.zoom
                try:
                    safe_namespace['x'] = x
                    safe_namespace['y'] = y
                    slope = eval(self.func_text, {"__builtins__": {}}, safe_namespace)
                    angle = math.atan(slope)
                    dx = math.cos(angle)
                    dy = -math.sin(angle)

                    if self.magnet_mode:
                        mx, my = self.mouse_pos
                        dist = math.hypot(px - mx, py - my)
                        dx += (mx - px) / max(1, dist * 5)
                        dy += (my - py) / max(1, dist * 5)

                    self.particles[i, 0] += dx * 2
                    self.particles[i, 1] += dy * 2

                    # wraparound
                    if self.particles[i, 0] < 0 or self.particles[i, 0] > width or \
                       self.particles[i, 1] < 0 or self.particles[i, 1] > height:
                        self.particles[i] = [np.random.rand() * width, np.random.rand() * height]

                    painter.drawPoint(int(self.particles[i, 0]), int(self.particles[i, 1]))

                except Exception:
                    continue


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Radar Field, Magnet Lines, Slope Field, Calibration Area Tester (Primary Slope Field Magnet)")
        self.setStyleSheet("background-color: black;")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Enter dy/dx = f(x, y), e.g. x - y")
        self.input.setStyleSheet("color: white; background: #222; padding: 6px; font-size: 14px;")
        layout.addWidget(self.input)

        self.magnet_button = QPushButton("Toggle Magnet Mode")
        self.magnet_button.setStyleSheet("background-color: #444; color: white; font-weight: bold;")
        layout.addWidget(self.magnet_button)

        controls = QHBoxLayout()
        layout.addLayout(controls)

        zoom_label = QLabel("Zoom")
        zoom_label.setStyleSheet("color: white;")
        self.zoom_slider = QSlider(Qt.Horizontal)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(100)
        self.zoom_slider.setValue(40)
        controls.addWidget(zoom_label)
        controls.addWidget(self.zoom_slider)

        density_label = QLabel("Density")
        density_label.setStyleSheet("color: white;")
        self.density_slider = QSlider(Qt.Horizontal)
        self.density_slider.setMinimum(10)
        self.density_slider.setMaximum(60)
        self.density_slider.setValue(25)
        controls.addWidget(density_label)
        controls.addWidget(self.density_slider)

        self.trail_checkbox = QCheckBox("Enable Trails")
        self.trail_checkbox.setStyleSheet("color: white;")
        layout.addWidget(self.trail_checkbox)

        self.slope_field = SlopeFieldWidget()
        layout.addWidget(self.slope_field)

        self.input.textChanged.connect(self.slope_field.set_function)
        self.zoom_slider.valueChanged.connect(self.slope_field.set_zoom)
        self.density_slider.valueChanged.connect(self.slope_field.set_density)
        self.magnet_button.clicked.connect(self.slope_field.toggle_magnet)
        self.trail_checkbox.stateChanged.connect(self.slope_field.toggle_trails)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1000, 900)
    window.show()
    sys.exit(app.exec_())
