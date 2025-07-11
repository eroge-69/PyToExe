import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import cos, sin, radians, pi, sqrt
import random
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPalette, QColor


class JCalculator:
    def __init__(self):
        self.G, self.nu, self.cracks = 1.0, 0.3, []

    def calc_j(self, crack, side='left'):
        radius = crack['length'] / 2
        theta_start = pi / 2 if side == 'left' else -pi / 2
        theta_end = 3 * pi / 2 if side == 'left' else pi / 2
        theta_range = np.linspace(theta_start, theta_end, 100)

        Jx = Jy = 0
        for i in range(len(theta_range) - 1):
            theta = theta_range[i]
            dtheta = theta_range[i + 1] - theta_range[i]
            x = crack['x'] + radius * cos(theta)
            y = crack['y'] + radius * sin(theta)

            factor = self.G / (2 * pi * (1 - self.nu))
            nx, ny = cos(theta), sin(theta)

            dJx = factor * crack['bx'] * nx * radius * dtheta
            dJy = factor * crack['by'] * ny * radius * dtheta
            Jx += dJx
            Jy += dJy

        return Jx, Jy, sqrt(Jx ** 2 + Jy ** 2)


class Canvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(10, 6))
        super().__init__(self.fig)

    def plot_cracks(self, cracks, title="Yoriqlar"):
        self.fig.clear()
        ax = self.fig.add_subplot(111)
        colors = ['red', 'blue', 'green', 'orange', 'purple']

        for i, crack in enumerate(cracks):
            color = colors[i % len(colors)]
            angle_rad = radians(crack['angle'])
            dx = crack['length'] * cos(angle_rad) / 2
            dy = crack['length'] * sin(angle_rad) / 2

            x1, y1 = crack['x'] - dx, crack['y'] - dy
            x2, y2 = crack['x'] + dx, crack['y'] + dy

            ax.plot([x1, x2], [y1, y2], color=color, linewidth=4, label=f"Yoriq {crack['id']}")
            ax.plot(crack['x'], crack['y'], 'ko', markersize=8)
            ax.text(crack['x'] + 0.1, crack['y'] + 0.1, f"{crack['id']}", fontsize=12, fontweight='bold')

            ax.arrow(crack['x'], crack['y'], crack['bx'] * 0.3, crack['by'] * 0.3,
                     head_width=0.05, head_length=0.05, fc=color, ec=color, alpha=0.7)

        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_title(title)
        ax.legend()
        self.draw()

    def plot_dynamic_topo(self, center_x=5.5, center_y=5.0, height_scale=1.0, num_levels=4, rotation=0):
        """Dinamik topografik xarita"""
        self.fig.clear()
        ax = self.fig.add_subplot(111)

        # Parametrlarga asoslangan kontur yaratish
        contours = []
        colors = ['#8B4513', '#CD853F', '#F4A460', '#FFE4B5', '#F0F8FF']

        # Har bir daraja uchun kontur chizish
        for level in range(num_levels + 1):
            # Radius va shakl parametrlari
            base_radius = 1.5 + level * 0.8 * height_scale
            noise_factor = 0.3 + level * 0.1

            # Kontur nuqtalarini yaratish
            angles = np.linspace(0, 2 * pi, 32)
            contour_points = []

            for angle in angles:
                # Asosiy radius + shovqin + aylanish
                r = base_radius + noise_factor * np.sin(4 * angle + rotation) * np.cos(3 * angle)

                # Koordinatalar
                x = center_x + r * cos(angle + radians(rotation))
                y = center_y + r * sin(angle + radians(rotation))

                # Chegaralarni cheklash
                x = max(0.5, min(11.5, x))
                y = max(0.5, min(9.5, y))

                contour_points.append([x, y])

            contour_points.append(contour_points[0])  # Yopiq kontur
            contours.append(np.array(contour_points))

        # Konturlarni chizish (tashqaridan ichkariga)
        for i, contour in enumerate(reversed(contours)):
            color_idx = len(contours) - 1 - i
            if color_idx < len(colors):
                ax.fill(contour[:, 0], contour[:, 1], color=colors[color_idx], alpha=0.6)
                ax.plot(contour[:, 0], contour[:, 1], 'k-', linewidth=1.5)

        # Balandlik raqamlarini qo'shish
        for level in range(1, num_levels + 1):
            # Har bir kontur uchun bir necha joyga raqam qo'yish
            for angle in [45, 135, 225, 315]:
                r = 1.5 + (level - 1) * 0.8 * height_scale + 0.4
                x = center_x + r * cos(radians(angle + rotation))
                y = center_y + r * sin(radians(angle + rotation))

                if 0 < x < 12 and 0 < y < 10:
                    ax.text(x, y, str(level), fontsize=11, fontweight='bold',
                            ha='center', va='center',
                            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))

        # Markazda xususiy belgilar
        # Oval
        oval_size = 0.2 * height_scale
        oval = plt.Circle((center_x, center_y), oval_size, fill=False, linestyle='--', linewidth=2)
        ax.add_patch(oval)

        # Chiziq (yo'nalishga bog'liq)
        line_length = 0.4 * height_scale
        line_angle = radians(rotation)
        x1 = center_x - line_length * cos(line_angle)
        y1 = center_y - line_length * sin(line_angle)
        x2 = center_x + line_length * cos(line_angle)
        y2 = center_y + line_length * sin(line_angle)
        ax.plot([x1, x2], [y1, y2], 'k-', linewidth=3)

        ax.set_xlim(0, 12)
        ax.set_ylim(0, 10)
        ax.set_xlabel('X koordinata')
        ax.set_ylabel('Y koordinata')
        ax.set_title(f'Dinamik Topografik Xarita (H={height_scale:.1f}, Θ={rotation}°)')
        ax.grid(True, alpha=0.3)
        self.draw()


class BasicTab(QWidget):
    def __init__(self):
        super().__init__()
        self.calc = JCalculator()
        layout = QHBoxLayout(self)

        # Chap panel
        left = QWidget()
        left_layout = QVBoxLayout(left)

        params = QGroupBox("Parametrlar")
        p_layout = QGridLayout(params)

        p_layout.addWidget(QLabel("G:"), 0, 0)
        self.g_input = QDoubleSpinBox()
        self.g_input.setValue(1.0)
        p_layout.addWidget(self.g_input, 0, 1)

        p_layout.addWidget(QLabel("ν:"), 1, 0)
        self.nu_input = QDoubleSpinBox()
        self.nu_input.setValue(0.3)
        p_layout.addWidget(self.nu_input, 1, 1)

        p_layout.addWidget(QLabel("Yoriqlar:"), 2, 0)
        self.n_input = QSpinBox()
        self.n_input.setRange(1, 9)
        self.n_input.setValue(2)
        self.n_input.valueChanged.connect(self.update_table)
        p_layout.addWidget(self.n_input, 2, 1)

        left_layout.addWidget(params)

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["X", "Y", "Uzunlik", "Burchak°", "Bx", "By", "Bz"])
        left_layout.addWidget(self.table)

        btns = QHBoxLayout()
        rand_btn = QPushButton("Tasodifiy")
        rand_btn.clicked.connect(self.random_data)
        calc_btn = QPushButton("Hisoblash")
        calc_btn.clicked.connect(self.calculate)
        calc_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        btns.addWidget(rand_btn)
        btns.addWidget(calc_btn)
        left_layout.addLayout(btns)

        layout.addWidget(left, 1)

        # O'ng panel
        right = QWidget()
        right_layout = QVBoxLayout(right)

        tabs = QTabWidget()

        result_tab = QWidget()
        result_layout = QVBoxLayout(result_tab)
        self.result_table = QTableWidget()
        self.result_table.setColumnCount(7)
        self.result_table.setHorizontalHeaderLabels(
            ["№", "Jx_left", "Jy_left", "J_left", "Jx_right", "Jy_right", "J_right"])
        result_layout.addWidget(self.result_table)
        tabs.addTab(result_tab, "Natijalar")

        graph_tab = QWidget()
        graph_layout = QVBoxLayout(graph_tab)
        self.canvas = Canvas()
        graph_layout.addWidget(self.canvas)
        tabs.addTab(graph_tab, "Grafik")

        right_layout.addWidget(tabs)
        layout.addWidget(right, 2)

        self.update_table()

    def update_table(self):
        n = self.n_input.value()
        self.table.setRowCount(n)
        for i in range(n):
            for j in range(7):
                if self.table.item(i, j) is None:
                    self.table.setItem(i, j, QTableWidgetItem("0.0"))

    def random_data(self):
        self.g_input.setValue(round(random.uniform(0.5, 5.0), 3))
        self.nu_input.setValue(round(random.uniform(0.2, 0.4), 3))

        n = random.randint(2, 9)
        self.n_input.setValue(n)
        self.update_table()

        for i in range(n):
            vals = [
                round(random.uniform(-3, 3), 2),
                round(random.uniform(-3, 3), 2),
                round(random.uniform(0.5, 2), 2),
                round(random.uniform(-180, 180), 1),
                round(random.uniform(-1, 1), 2),
                round(random.uniform(-1, 1), 2),
                round(random.uniform(-1, 1), 2)
            ]
            for j, val in enumerate(vals):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

        self.update_viz()

    def calculate(self):
        try:
            self.calc.G = self.g_input.value()
            self.calc.nu = self.nu_input.value()
            self.calc.cracks = []

            n = self.n_input.value()
            for i in range(n):
                crack = {
                    'id': i + 1,
                    'x': float(self.table.item(i, 0).text()),
                    'y': float(self.table.item(i, 1).text()),
                    'length': float(self.table.item(i, 2).text()),
                    'angle': float(self.table.item(i, 3).text()),
                    'bx': float(self.table.item(i, 4).text()),
                    'by': float(self.table.item(i, 5).text()),
                    'bz': float(self.table.item(i, 6).text())
                }
                self.calc.cracks.append(crack)

            results = []
            for crack in self.calc.cracks:
                Jx_l, Jy_l, J_l = self.calc.calc_j(crack, 'left')
                Jx_r, Jy_r, J_r = self.calc.calc_j(crack, 'right')
                results.append([crack['id'], Jx_l, Jy_l, J_l, Jx_r, Jy_r, J_r])

            self.result_table.setRowCount(len(results))
            for i, row in enumerate(results):
                for j, val in enumerate(row):
                    self.result_table.setItem(i, j, QTableWidgetItem(f"{val:.6f}" if j > 0 else str(val)))

            self.update_viz()
        except:
            QMessageBox.critical(self, "Xatolik", "Hisoblashda xatolik!")

    def update_viz(self):
        if self.calc.cracks:
            self.canvas.plot_cracks(self.calc.cracks, "J-Integral: Asosiy")


class RotateTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        params = QGroupBox("Aylanuvchi yoriq")
        p_layout = QGridLayout(params)

        labels = ["G:", "ν:", "Y1-X:", "Y1-Y:", "Y1-L:", "Y2-X:", "Y2-Y:", "Y2-L:", "Burchak:"]
        self.inputs = []

        for i, label in enumerate(labels):
            p_layout.addWidget(QLabel(label), i, 0)
            if i < 8:
                inp = QDoubleSpinBox()
                inp.setRange(-10, 10) if i > 1 else inp.setRange(0, 10)
                inp.setValue([1, 0.3, 0, 0, 1, 1.5, 1.5, 1][i])
            else:
                inp = QSlider(Qt.Horizontal)
                inp.setRange(0, 360)
                inp.valueChanged.connect(self.update_viz)
            self.inputs.append(inp)
            p_layout.addWidget(inp, i, 1)

        self.angle_label = QLabel("0°")
        p_layout.addWidget(self.angle_label, 9, 1)

        left_layout.addWidget(params)

        btns = QHBoxLayout()
        anim_btn = QPushButton("Animatsiya")
        anim_btn.clicked.connect(self.animate)
        btns.addWidget(anim_btn)
        left_layout.addLayout(btns)

        layout.addWidget(left, 1)

        self.canvas = Canvas()
        layout.addWidget(self.canvas, 2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.anim_step)
        self.anim_angle = 0

        self.update_viz()

    def update_viz(self):
        angle = self.inputs[8].value()
        self.angle_label.setText(f"{angle}°")

        cracks = [
            {'id': 1, 'x': self.inputs[2].value(), 'y': self.inputs[3].value(),
             'length': self.inputs[4].value(), 'angle': 0, 'bx': 1, 'by': 1, 'bz': 1},
            {'id': 2, 'x': self.inputs[5].value(), 'y': self.inputs[6].value(),
             'length': self.inputs[7].value(), 'angle': angle, 'bx': 1, 'by': 0, 'bz': 0}
        ]
        self.canvas.plot_cracks(cracks, f"Aylanuvchi - {angle}°")

    def animate(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(50)

    def anim_step(self):
        self.anim_angle = (self.anim_angle + 2) % 360
        self.inputs[8].setValue(self.anim_angle)


class LengthTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        params = QGroupBox("O'zgaruvchan uzunlik")
        p_layout = QGridLayout(params)

        labels = ["G:", "ν:", "Y1-L:", "Y1-X:", "Y1-Y:", "Y2-X:", "Y2-Y:", "Min-L:", "Max-L:", "Joriy-L:"]
        self.inputs = []

        for i, label in enumerate(labels):
            p_layout.addWidget(QLabel(label), i, 0)
            if i < 9:
                inp = QDoubleSpinBox()
                inp.setRange(-10, 10) if i > 2 else inp.setRange(0, 10)
                inp.setValue([1, 0.3, 2, 0, 0, 3, 0, 0.5, 4][i])
            else:
                inp = QSlider(Qt.Horizontal)
                inp.setRange(50, 400)
                inp.setValue(100)
                inp.valueChanged.connect(self.update_viz)
            self.inputs.append(inp)
            p_layout.addWidget(inp, i, 1)

        self.length_label = QLabel("1.0")
        p_layout.addWidget(self.length_label, 10, 1)

        left_layout.addWidget(params)

        btns = QHBoxLayout()
        anim_btn = QPushButton("Animatsiya")
        anim_btn.clicked.connect(self.animate)
        btns.addWidget(anim_btn)
        left_layout.addLayout(btns)

        layout.addWidget(left, 1)

        self.canvas = Canvas()
        layout.addWidget(self.canvas, 2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.anim_step)
        self.direction = 1

        self.update_viz()

    def update_viz(self):
        length = self.inputs[9].value() / 100.0
        self.length_label.setText(f"{length:.1f}")

        cracks = [
            {'id': 1, 'x': self.inputs[3].value(), 'y': self.inputs[4].value(),
             'length': self.inputs[2].value(), 'angle': 0, 'bx': 1, 'by': 0, 'bz': 0},
            {'id': 2, 'x': self.inputs[5].value(), 'y': self.inputs[6].value(),
             'length': length, 'angle': 0, 'bx': 1, 'by': 0, 'bz': 0}
        ]
        self.canvas.plot_cracks(cracks, f"Uzunlik - {length:.1f}")

    def animate(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(100)

    def anim_step(self):
        current = self.inputs[9].value()
        if current >= 400:
            self.direction = -1
        elif current <= 50:
            self.direction = 1
        self.inputs[9].setValue(current + self.direction * 5)


class MotionTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        left = QWidget()
        left_layout = QVBoxLayout(left)

        params = QGroupBox("Chiziqli harakat")
        p_layout = QGridLayout(params)

        labels = ["G:", "ν:", "Y1-X:", "Y1-Y:", "Y1-L:", "Y2-L:", "Y2-A:", "X-pos:", "Y-min:", "Y-max:", "Joriy-Y:"]
        self.inputs = []

        for i, label in enumerate(labels):
            p_layout.addWidget(QLabel(label), i, 0)
            if i < 10:
                inp = QDoubleSpinBox()
                inp.setRange(-10, 10)
                inp.setValue([1, 0.3, 0, 0, 1, 2, 30, 3, -5, 5][i])
            else:
                inp = QSlider(Qt.Horizontal)
                inp.setRange(-500, 500)
                inp.setValue(0)
                inp.valueChanged.connect(self.update_viz)
            self.inputs.append(inp)
            p_layout.addWidget(inp, i, 1)

        self.y_label = QLabel("0.0")
        p_layout.addWidget(self.y_label, 11, 1)

        left_layout.addWidget(params)

        btns = QHBoxLayout()
        anim_btn = QPushButton("Animatsiya")
        anim_btn.clicked.connect(self.animate)
        btns.addWidget(anim_btn)
        left_layout.addLayout(btns)

        layout.addWidget(left, 1)

        self.canvas = Canvas()
        layout.addWidget(self.canvas, 2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.anim_step)
        self.direction = 1

        self.update_viz()

    def update_viz(self):
        y_pos = self.inputs[10].value() / 100.0
        self.y_label.setText(f"{y_pos:.1f}")

        cracks = [
            {'id': 1, 'x': self.inputs[2].value(), 'y': self.inputs[3].value(),
             'length': self.inputs[4].value(), 'angle': 0, 'bx': 0, 'by': 1, 'bz': 0},
            {'id': 2, 'x': self.inputs[7].value(), 'y': y_pos,
             'length': self.inputs[5].value(), 'angle': self.inputs[6].value(), 'bx': 0, 'by': 1, 'bz': 0}
        ]
        self.canvas.plot_cracks(cracks, f"Harakat - Y: {y_pos:.1f}")

    def animate(self):
        if self.timer.isActive():
            self.timer.stop()
        else:
            self.timer.start(100)

    def anim_step(self):
        current = self.inputs[10].value()
        if current >= 500:
            self.direction = -1
        elif current <= -500:
            self.direction = 1
        self.inputs[10].setValue(current + self.direction * 10)


class DynamicTopoTab(QWidget):
    """Dinamik topografik xarita tab"""

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        # Chap panel - parametrlar
        left = QWidget()
        left_layout = QVBoxLayout(left)

        params = QGroupBox("Topografik parametrlar")
        p_layout = QGridLayout(params)

        # Parametrlar
        p_layout.addWidget(QLabel("Markaz X:"), 0, 0)
        self.center_x = QDoubleSpinBox()
        self.center_x.setRange(2, 10)
        self.center_x.setValue(5.5)
        self.center_x.valueChanged.connect(self.update_map)
        p_layout.addWidget(self.center_x, 0, 1)

        p_layout.addWidget(QLabel("Markaz Y:"), 1, 0)
        self.center_y = QDoubleSpinBox()
        self.center_y.setRange(2, 8)
        self.center_y.setValue(5.0)
        self.center_y.valueChanged.connect(self.update_map)
        p_layout.addWidget(self.center_y, 1, 1)

        p_layout.addWidget(QLabel("Balandlik:"), 2, 0)
        self.height_scale = QDoubleSpinBox()
        self.height_scale.setRange(0.3, 3.0)
        self.height_scale.setValue(1.0)
        self.height_scale.setSingleStep(0.1)
        self.height_scale.valueChanged.connect(self.update_map)
        p_layout.addWidget(self.height_scale, 2, 1)

        p_layout.addWidget(QLabel("Darajalar:"), 3, 0)
        self.num_levels = QSpinBox()
        self.num_levels.setRange(2, 8)
        self.num_levels.setValue(4)
        self.num_levels.valueChanged.connect(self.update_map)
        p_layout.addWidget(self.num_levels, 3, 1)

        p_layout.addWidget(QLabel("Aylanish:"), 4, 0)
        self.rotation = QSlider(Qt.Horizontal)
        self.rotation.setRange(0, 360)
        self.rotation.setValue(0)
        self.rotation.valueChanged.connect(self.update_rotation)
        p_layout.addWidget(self.rotation, 4, 1)

        self.rotation_label = QLabel("0°")
        p_layout.addWidget(self.rotation_label, 5, 1)

        left_layout.addWidget(params)

        # Tugmalar
        btns = QVBoxLayout()

        random_btn = QPushButton("Tasodifiy parametrlar")
        random_btn.clicked.connect(self.random_params)
        random_btn.setStyleSheet("background-color: #FF9800; color: white;")
        btns.addWidget(random_btn)

        animate_btn = QPushButton("Aylanish animatsiyasi")
        animate_btn.clicked.connect(self.animate_rotation)
        btns.addWidget(animate_btn)

        export_btn = QPushButton("Eksport PNG")
        export_btn.clicked.connect(self.export_map)
        export_btn.setStyleSheet("background-color: #2196F3; color: white;")
        btns.addWidget(export_btn)

        btns.addStretch()
        left_layout.addLayout(btns)

        layout.addWidget(left, 1)

        # O'ng panel - xarita
        self.canvas = Canvas()
        layout.addWidget(self.canvas, 3)

        # Timer
        self.rotation_timer = QTimer()
        self.rotation_timer.timeout.connect(self.rotation_step)

        # Dastlabki xarita
        self.update_map()

    def update_rotation(self):
        angle = self.rotation.value()
        self.rotation_label.setText(f"{angle}°")
        self.update_map()

    def update_map(self):
        """Xaritani yangilash"""
        center_x = self.center_x.value()
        center_y = self.center_y.value()
        height_scale = self.height_scale.value()
        num_levels = self.num_levels.value()
        rotation = self.rotation.value()

        self.canvas.plot_dynamic_topo(center_x, center_y, height_scale, num_levels, rotation)

    def random_params(self):
        """Tasodifiy parametrlar"""
        self.center_x.setValue(round(random.uniform(3, 9), 1))
        self.center_y.setValue(round(random.uniform(3, 7), 1))
        self.height_scale.setValue(round(random.uniform(0.5, 2.5), 1))
        self.num_levels.setValue(random.randint(3, 6))
        self.rotation.setValue(random.randint(0, 360))
        self.update_map()

    def animate_rotation(self):
        """Aylanish animatsiyasi"""
        if self.rotation_timer.isActive():
            self.rotation_timer.stop()
        else:
            self.rotation_timer.start(100)

    def rotation_step(self):
        """Aylanish qadami"""
        current = self.rotation.value()
        new_value = (current + 5) % 360
        self.rotation.setValue(new_value)

    def export_map(self):
        """Xaritani eksport qilish"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Topografik xaritani saqlash", "dynamic_topo.png", "PNG (*.png)")
        if filename:
            self.canvas.fig.savefig(filename, dpi=300, bbox_inches='tight')
            QMessageBox.information(self, "Muvaffaqiyat", f"Xarita saqlandi: {filename}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("J-Integral va Dinamik Topografik Xarita")
        self.setGeometry(100, 100, 1500, 900)

        tabs = QTabWidget()
        tabs.addTab(BasicTab(), "J-POS")
        tabs.addTab(RotateTab(), "Aylanuvchi")
        tabs.addTab(LengthTab(), "Uzunlik")
        tabs.addTab(MotionTab(), "Harakat")
        tabs.addTab(DynamicTopoTab(), "🗺️ Dinamik Xarita")

        self.setCentralWidget(tabs)
        self.statusBar().showMessage("Tayyor - Dinamik topografik xarita qo'shildi!")

        # Style
        self.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #ccc; }
            QTabBar::tab { background: #eee; padding: 8px 12px; margin-right: 2px; }
            QTabBar::tab:selected { background: #4CAF50; color: white; }
            QGroupBox { font-weight: bold; border: 2px solid #ccc; border-radius: 5px; margin: 3px; padding-top: 10px; }
        """)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    app.setPalette(palette)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())

main()