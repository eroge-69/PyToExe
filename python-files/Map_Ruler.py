#!/usr/bin/env python3
import sys
import math
import os
import configparser
import webbrowser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QComboBox,
    QPushButton, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QPainter, QPen, QColor, QFont, QFontMetrics

# Базовый масштаб (метров на пиксель) для масштаба 225
BASE_SCALE_225 = 3.722132
BASE_SCALE_VALUE = 225

# Список масштабов карт
MAP_SCALES = [150, 170, 180, 190, 200, 225, 250, 275, 300, 325, 400, 450, 500, 550]

class MapRuler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Дальномер для War Thunder")
        self.setFixedSize(500, 480)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Центральный виджет и макет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Панель управления
        self.control_panel = self.create_control_panel()
        main_layout.addLayout(self.control_panel)

        # Настройки
        self.selected_scale = BASE_SCALE_VALUE
        self.scale_factor = BASE_SCALE_225
        self.start_point = None
        self.end_point = None
        self.temp_point = None
        self.calibration_mode = False
        self.calibration_result = None

        # Загрузка конфигурации
        self.config_file = os.path.expanduser("~/.wt_map_ruler.ini")
        self.load_config()
        self.recalculate_scale()

        # Перемещение окна
        self.old_pos = None

    def create_control_panel(self):
        layout = QHBoxLayout()

        # Кнопка калибровки
        self.calibration_btn = QPushButton("Калибровка")
        self.calibration_btn.setCheckable(True)
        self.calibration_btn.setToolTip("Режим калибровки (измерение метров на пиксель)")
        self.calibration_btn.toggled.connect(self.on_calibration_toggled)
        layout.addWidget(self.calibration_btn)

        # Выбор масштаба
        layout.addWidget(QLabel("Масштаб карты:"))
        self.scale_combo = QComboBox()
        for scale in MAP_SCALES:
            self.scale_combo.addItem(str(scale))
        self.scale_combo.currentTextChanged.connect(self.on_scale_changed)
        layout.addWidget(self.scale_combo)

        # Текущий масштаб
        layout.addWidget(QLabel("Текущий масштаб:"))
        self.scale_value = QLabel(f"{self.scale_factor:.6f} м/пикс")
        layout.addWidget(self.scale_value)

        # Дистанция
        layout.addWidget(QLabel("Дистанция:"))
        self.distance_value = QLabel("0.00 м")
        layout.addWidget(self.distance_value)

        # Кнопка сброса
        self.reset_btn = QPushButton("↺")
        self.reset_btn.setToolTip("Сбросить точки измерения (R)")
        self.reset_btn.clicked.connect(self.reset_points)
        layout.addWidget(self.reset_btn)

        # Кнопка YouTube
        self.youtube_btn = QPushButton("Y")
        self.youtube_btn.setToolTip("YouTube канал EXTRUD")
        self.youtube_btn.clicked.connect(lambda: webbrowser.open("https://www.youtube.com/@EXTRUD/shorts"))
        layout.addWidget(self.youtube_btn)

        # Кнопка поверх окон
        self.top_btn = QPushButton("🔝")
        self.top_btn.setCheckable(True)
        self.top_btn.setChecked(True)
        self.top_btn.setToolTip("Всегда поверх других окон")
        self.top_btn.toggled.connect(self.on_top_toggled)
        layout.addWidget(self.top_btn)

        return layout

    def load_config(self):
        config = configparser.ConfigParser()
        if os.path.exists(self.config_file):
            config.read(self.config_file)
            try:
                scale = int(config.get('DEFAULT', 'selected_scale', fallback=str(BASE_SCALE_VALUE)))
                if scale in MAP_SCALES:
                    self.selected_scale = scale
            except (ValueError, configparser.NoSectionError, configparser.NoOptionError):
                pass

    def save_config(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'selected_scale': str(self.selected_scale)}
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

    def recalculate_scale(self):
        self.scale_factor = BASE_SCALE_225 * (self.selected_scale / BASE_SCALE_VALUE)
        self.scale_value.setText(f"{self.scale_factor:.6f} м/пикс")
        self.update_distance_display()

    def on_calibration_toggled(self, checked):
        self.calibration_mode = checked
        self.calibration_result = None

        if self.calibration_mode:
            self.scale_combo.setCurrentText("225")
            self.scale_combo.setEnabled(False)
            self.distance_value.setText("0.00")
        else:
            self.scale_combo.setEnabled(True)
            self.distance_value.setText("0.00 м")

        self.reset_points()

    def on_top_toggled(self, checked):
        self.setWindowFlag(Qt.WindowStaysOnTopHint, checked)
        self.show()

    def on_scale_changed(self, text):
        try:
            self.selected_scale = int(text)
            self.recalculate_scale()
            self.save_config()
            self.update()
        except ValueError:
            pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Полупрозрачный фон
        painter.fillRect(self.rect(), QColor(50, 50, 50, 200))

        # Рисуем точки и линии
        if self.start_point:
            # Начальная точка (зеленая)
            self.draw_cross(painter, self.start_point, QColor(0, 255, 0))

            # Конечная точка (красная)
            target = self.end_point if self.end_point else self.temp_point
            if target:
                if self.end_point:
                    self.draw_cross(painter, target, QColor(255, 0, 0))

                # Линия между точками
                painter.setPen(QPen(Qt.white, 2))
                painter.drawLine(self.start_point, target)

                # Расчёт расстояния
                distance = math.sqrt(
                    (target.x() - self.start_point.x())**2 +
                    (target.y() - self.start_point.y())**2
                )

                # Текст расстояния
                painter.setFont(QFont("Arial", 24))
                painter.setPen(QPen(Qt.white))

                if self.calibration_mode:
                    if self.end_point:
                        meters_per_pixel = BASE_SCALE_VALUE / distance
                        text = f"{meters_per_pixel:.6f} м/пикс"
                    else:
                        text = f"{distance:.1f} пикс"
                else:
                    meters = distance * self.scale_factor
                    text = f"{meters:.1f} м"

                # Позиция текста
                text_x = (self.start_point.x() + target.x()) / 2
                text_y = (self.start_point.y() + target.y()) / 2 - 40
                painter.drawText(int(text_x), int(text_y), text)

                # Инструкция для калибровки
                if self.calibration_mode and not self.end_point:
                    painter.setFont(QFont("Arial", 12))
                    painter.drawText(10, self.height() - 20,
                                    "Измерьте расстояние 225 м между двумя точками")

    def draw_cross(self, painter, point, color):
        painter.setPen(QPen(color, 2))
        size = 10

        # Горизонтальная линия
        painter.drawLine(
            point.x() - size, point.y(),
            point.x() + size, point.y()
        )

        # Вертикальная линия
        painter.drawLine(
            point.x(), point.y() - size,
            point.x(), point.y() + size
        )

    def update_distance_display(self):
        if self.start_point and self.end_point:
            distance = math.sqrt(
                (self.end_point.x() - self.start_point.x())**2 +
                (self.end_point.y() - self.start_point.y())**2
            )

            if self.calibration_mode:
                meters_per_pixel = BASE_SCALE_VALUE / distance
                self.distance_value.setText(f"{meters_per_pixel:.6f}")
            else:
                meters = distance * self.scale_factor
                self.distance_value.setText(f"{meters:.1f} м")
        else:
            if self.calibration_mode:
                self.distance_value.setText("0.00")
            else:
                self.distance_value.setText("0.00 м")

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.start_point = event.pos()
            self.end_point = None
            self.update()
        elif event.button() == Qt.LeftButton and self.start_point:
            self.end_point = event.pos()
            self.update_distance_display()
            self.update()
        elif event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.start_point and not self.end_point:
            self.temp_point = event.pos()
            self.update()

        # Перемещение окна
        if self.old_pos:
            delta = event.globalPos() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Escape:
            self.save_config()
            self.close()
        elif key == Qt.Key_R:
            self.reset_points()
        elif key == Qt.Key_T:
            self.top_btn.toggle()
        elif key == Qt.Key_C:
            self.calibration_btn.toggle()
        elif key == Qt.Key_Y:
            webbrowser.open("https://www.youtube.com/@EXTRUD/shorts")

    def reset_points(self):
        self.start_point = None
        self.end_point = None
        self.temp_point = None
        self.calibration_result = None
        self.update_distance_display()
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapRuler()
    window.show()

    # Позиционирование в правом нижнем углу
    screen = app.primaryScreen().geometry()
    window.move(
        screen.width() - window.width(),
        screen.height() - window.height()
    )

    sys.exit(app.exec_())
