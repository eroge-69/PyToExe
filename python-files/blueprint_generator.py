import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QComboBox, QSpinBox, QCheckBox, QPushButton,
                             QColorDialog, QFileDialog)
from PyQt5.QtGui import QColor
from PIL import Image, ImageDraw

# Стандартные размеры форматов в мм (ширина x высота)
SIZES = {
    "A0": (841, 1189),
    "A1": (594, 841),
    "A2": (420, 594),
    "A3": (297, 420),
    "A4": (210, 297),
}


class BlueprintGenerator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Генератор чертежных блюпринтов')
        self.setGeometry(300, 300, 400, 500)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()

        # Выбор формата
        layout.addWidget(QLabel('Формат:'))
        self.size_combo = QComboBox()
        self.size_combo.addItems(['A0', 'A1', 'A2', 'A3', 'A4'])
        layout.addWidget(self.size_combo)

        # Ориентация
        layout.addWidget(QLabel('Ориентация:'))
        self.orientation_combo = QComboBox()
        self.orientation_combo.addItems(['Книжная', 'Альбомная'])
        layout.addWidget(self.orientation_combo)

        # Цвет фона
        layout.addWidget(QLabel('Цвет фона:'))
        self.bg_color_btn = QPushButton('Выбрать')
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        self.bg_color = QColor(255, 255, 255)  # Белый по умолчанию
        layout.addWidget(self.bg_color_btn)

        # Настройки сетки
        layout.addWidget(QLabel('Сетка:'))

        # Цвет сетки
        layout.addWidget(QLabel('Цвет сетки:'))
        self.grid_color_btn = QPushButton('Выбрать')
        self.grid_color_btn.clicked.connect(self.choose_grid_color)
        self.grid_color = QColor(200, 200, 200)  # Светло-серый по умолчанию
        layout.addWidget(self.grid_color_btn)

        # Шаг сетки
        layout.addWidget(QLabel('Шаг сетки (мм):'))
        self.grid_step = QSpinBox()
        self.grid_step.setRange(1, 100)
        self.grid_step.setValue(10)
        layout.addWidget(self.grid_step)

        # Толщина сетки
        layout.addWidget(QLabel('Толщина сетки (px):'))
        self.grid_thickness = QSpinBox()
        self.grid_thickness.setRange(1, 10)
        self.grid_thickness.setValue(1)
        layout.addWidget(self.grid_thickness)

        # Рамка
        self.border_check = QCheckBox('Рамка по ГОСТ')
        self.border_check.setChecked(True)
        layout.addWidget(self.border_check)

        # Цвет рамки
        layout.addWidget(QLabel('Цвет рамки:'))
        self.border_color_btn = QPushButton('Выбрать')
        self.border_color_btn.clicked.connect(self.choose_border_color)
        self.border_color = QColor(0, 0, 0)  # Черный по умолчанию
        layout.addWidget(self.border_color_btn)

        # Толщина рамки
        layout.addWidget(QLabel('Толщина рамки (px):'))
        self.border_thickness = QSpinBox()
        self.border_thickness.setRange(1, 10)
        self.border_thickness.setValue(2)
        layout.addWidget(self.border_thickness)

        # Кнопка генерации
        self.generate_btn = QPushButton('Сгенерировать блюпринт')
        self.generate_btn.clicked.connect(self.generate_blueprint)
        layout.addWidget(self.generate_btn)

        main_widget.setLayout(layout)

    def choose_bg_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.bg_color = color

    def choose_grid_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.grid_color = color

    def choose_border_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.border_color = color

    def generate_blueprint(self):
        # Получаем параметры
        size = self.size_combo.currentText()
        orientation = self.orientation_combo.currentText()
        bg_color = self.bg_color.getRgb()[:3]
        grid_color = self.grid_color.getRgb()[:3]
        grid_step = self.grid_step.value()
        grid_thickness = self.grid_thickness.value()
        border = self.border_check.isChecked()
        border_color = self.border_color.getRgb()[:3]
        border_thickness = self.border_thickness.value()

        # Получаем размер в мм и переводим в пиксели (1 мм ≈ 3.78 пикселя при 300 DPI)
        mm_to_px = 3.78
        width_mm, height_mm = SIZES[size]

        if orientation == 'Альбомная':
            width_mm, height_mm = height_mm, width_mm

        width_px = int(width_mm * mm_to_px)
        height_px = int(height_mm * mm_to_px)

        # Создаем изображение
        img = Image.new("RGB", (width_px, height_px), bg_color)
        draw = ImageDraw.Draw(img)

        # Рисуем сетку
        for x in range(0, width_px, int(grid_step * mm_to_px)):
            draw.line([(x, 0), (x, height_px)], fill=grid_color, width=grid_thickness)
        for y in range(0, height_px, int(grid_step * mm_to_px)):
            draw.line([(0, y), (width_px, y)], fill=grid_color, width=grid_thickness)

        # Рисуем рамку (ГОСТ 2.301-68)
        if border:
            border_margin = 20  # Отступ рамки от края в мм
            border_px = int(border_margin * mm_to_px)
            draw.rectangle(
                [(border_px, border_px), (width_px - border_px, height_px - border_px)],
                outline=border_color,
                width=border_thickness,
            )

        # Сохраняем изображение
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить блюпринт", "",
            "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg)",
            options=options
        )

        if file_path:
            if file_path.lower().endswith(('.png', '.jpg', '.jpeg')):
                img.save(file_path)
            else:
                file_path += '.png'
                img.save(file_path)
            self.statusBar().showMessage(f"Файл сохранен: {file_path}", 3000)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = BlueprintGenerator()
    ex.show()
    sys.exit(app.exec_())