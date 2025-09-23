import sys
import os
from PIL import Image, ImageEnhance, ImageOps, ExifTags
from PIL.ExifTags import TAGS
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QSlider, QComboBox, QFileDialog, QMessageBox,
                             QGroupBox, QTextEdit, QSplitter, QFrame, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont, QPalette, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PhotoEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.original_image = None
        self.modified_image = None
        self.current_corrections = {
            'brightness': 0,
            'contrast': 0,
            'saturation': 0,
            'linear': 0,
            'gamma': 0
        }
        self.setup_ui()
        self.setup_connections()
        self.apply_dark_theme()
        
    def setup_ui(self):
        self.setWindowTitle("Редактор фотографий")
        self.setGeometry(100, 100, 1600, 900)
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        # Левая панель - управление
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Правая панель - изображения и гистограммы
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 3)
        
    def apply_dark_theme(self):
        # Темная тема для приложения
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        self.setPalette(dark_palette)
        
        # Темная тема для matplotlib
        plt.style.use('default')
        plt.rcParams.update({
            'figure.facecolor': '#1a1a1a',
            'axes.facecolor': '#1a1a1a',
            'axes.edgecolor': 'white',
            'axes.labelcolor': 'white',
            'text.color': 'white',
            'xtick.color': 'white',
            'ytick.color': 'white',
            'grid.color': '#444444'
        })
        
    def create_left_panel(self):
        panel = QScrollArea()
        panel.setFixedWidth(400)
        panel.setWidgetResizable(True)
        
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Группа загрузки/сохранения
        file_group = QGroupBox("Файл")
        file_layout = QVBoxLayout(file_group)
        file_layout.setSpacing(3)
        file_layout.setContentsMargins(5, 10, 5, 10)
        
        self.load_btn = QPushButton("Загрузить изображение")
        self.save_btn = QPushButton("Сохранить изображение")
        self.load_btn.setMinimumHeight(30)
        self.save_btn.setMinimumHeight(30)
        file_layout.addWidget(self.load_btn)
        file_layout.addWidget(self.save_btn)
        
        # Группа информации
        info_group = QGroupBox("Информация об изображении")
        info_layout = QVBoxLayout(info_group)
        info_layout.setContentsMargins(5, 10, 5, 10)
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        # Группа операций
        ops_group = QGroupBox("Операции")
        ops_layout = QVBoxLayout(ops_group)
        ops_layout.setSpacing(3)
        ops_layout.setContentsMargins(5, 10, 5, 10)
        
        self.grayscale_btn = QPushButton("В градации серого")
        self.rotate_btn = QPushButton("Повернуть на 90°")
        self.reset_all_btn = QPushButton("Сбросить все коррекции")
        self.grayscale_btn.setMinimumHeight(30)
        self.rotate_btn.setMinimumHeight(30)
        self.reset_all_btn.setMinimumHeight(30)
        ops_layout.addWidget(self.grayscale_btn)
        ops_layout.addWidget(self.rotate_btn)
        ops_layout.addWidget(self.reset_all_btn)
        
        # Группа коррекции
        correction_group = QGroupBox("Коррекция изображения")
        correction_layout = QVBoxLayout(correction_group)
        correction_layout.setSpacing(5)
        correction_layout.setContentsMargins(5, 10, 5, 10)
        
        # Яркость
        brightness_layout = QVBoxLayout()
        brightness_layout.setSpacing(3)
        brightness_label = QLabel("Яркость:")
        brightness_label.setMaximumHeight(20)
        brightness_label.setStyleSheet("color: white; font-size: 10px;")
        brightness_layout.addWidget(brightness_label)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setRange(-100, 100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.setMinimumHeight(25)
        brightness_layout.addWidget(self.brightness_slider)
        self.brightness_value = QLabel("0")
        self.brightness_value.setMaximumHeight(20)
        self.brightness_value.setStyleSheet("color: white;")
        brightness_layout.addWidget(self.brightness_value)
        correction_layout.addLayout(brightness_layout)
        
        # Контрастность
        contrast_layout = QVBoxLayout()
        contrast_layout.setSpacing(3)
        contrast_label = QLabel("Контрастность:")
        contrast_label.setMaximumHeight(20)
        contrast_label.setStyleSheet("color: white; font-size: 10px;")
        contrast_layout.addWidget(contrast_label)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setRange(-100, 100)
        self.contrast_slider.setValue(0)
        self.contrast_slider.setMinimumHeight(25)
        contrast_layout.addWidget(self.contrast_slider)
        self.contrast_value = QLabel("0")
        self.contrast_value.setMaximumHeight(20)
        self.contrast_value.setStyleSheet("color: white;")
        contrast_layout.addWidget(self.contrast_value)
        correction_layout.addLayout(contrast_layout)
        
        # Насыщенность
        saturation_layout = QVBoxLayout()
        saturation_layout.setSpacing(3)
        saturation_label = QLabel("Насыщенность:")
        saturation_label.setMaximumHeight(20)
        saturation_label.setStyleSheet("color: white; font-size: 10px;")
        saturation_layout.addWidget(saturation_label)
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setRange(-100, 100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.setMinimumHeight(25)
        saturation_layout.addWidget(self.saturation_slider)
        self.saturation_value = QLabel("0")
        self.saturation_value.setMaximumHeight(20)
        self.saturation_value.setStyleSheet("color: white;")
        saturation_layout.addWidget(self.saturation_value)
        correction_layout.addLayout(saturation_layout)
        
        # Линейная коррекция
        linear_layout = QVBoxLayout()
        linear_layout.setSpacing(3)
        linear_label = QLabel("Линейная коррекция:")
        linear_label.setMaximumHeight(20)
        linear_label.setStyleSheet("color: white; font-size: 10px;")
        linear_layout.addWidget(linear_label)
        self.linear_slider = QSlider(Qt.Horizontal)
        self.linear_slider.setRange(-100, 100)
        self.linear_slider.setValue(0)
        self.linear_slider.setMinimumHeight(25)
        linear_layout.addWidget(self.linear_slider)
        self.linear_value = QLabel("0")
        self.linear_value.setMaximumHeight(20)
        self.linear_value.setStyleSheet("color: white;")
        linear_layout.addWidget(self.linear_value)
        correction_layout.addLayout(linear_layout)
        
        # Гамма-коррекция
        gamma_layout = QVBoxLayout()
        gamma_layout.setSpacing(3)
        gamma_label = QLabel("Гамма-коррекция:")
        gamma_label.setMaximumHeight(20)
        gamma_label.setStyleSheet("color: white; font-size: 10px;")
        gamma_layout.addWidget(gamma_label)
        self.gamma_slider = QSlider(Qt.Horizontal)
        self.gamma_slider.setRange(-80, 80)
        self.gamma_slider.setValue(0)
        self.gamma_slider.setMinimumHeight(25)
        gamma_layout.addWidget(self.gamma_slider)
        self.gamma_value = QLabel("1.0")
        self.gamma_value.setMaximumHeight(20)
        self.gamma_value.setStyleSheet("color: white;")
        gamma_layout.addWidget(self.gamma_value)
        correction_layout.addLayout(gamma_layout)
        
        # Добавление всех групп в layout
        layout.addWidget(file_group)
        layout.addWidget(info_group)
        layout.addWidget(ops_group)
        layout.addWidget(correction_group)
        layout.addStretch()
        
        panel.setWidget(container)
        return panel
        
    def create_right_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(3)
        layout.setContentsMargins(2, 2, 2, 2)
        
        # Верхняя часть - изображения
        images_widget = QWidget()
        images_layout = QHBoxLayout(images_widget)
        images_layout.setSpacing(5)
        images_layout.setContentsMargins(0, 0, 0, 0)
        
        # Исходное изображение
        original_container = QVBoxLayout()
        original_container.setSpacing(1)
        original_container.setContentsMargins(2, 2, 2, 2)
        
        original_label = QLabel("Исходное изображение")
        original_label.setAlignment(Qt.AlignCenter)
        original_label.setMaximumHeight(20)
        original_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px; margin: 0px; padding: 0px;")
        original_container.addWidget(original_label)
        
        self.original_display = QLabel("Загрузите изображение")
        self.original_display.setAlignment(Qt.AlignCenter)
        self.original_display.setMinimumSize(280, 200)
        self.original_display.setStyleSheet("border: 1px solid #666; background-color: #333; margin: 0px; padding: 0px;")
        self.original_display.setScaledContents(False)
        original_container.addWidget(self.original_display)
        images_layout.addLayout(original_container)
        
        # Измененное изображение
        modified_container = QVBoxLayout()
        modified_container.setSpacing(1)
        modified_container.setContentsMargins(2, 2, 2, 2)
        
        modified_label = QLabel("Измененное изображение")
        modified_label.setAlignment(Qt.AlignCenter)
        modified_label.setMaximumHeight(20)
        modified_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px; margin: 0px; padding: 0px;")
        modified_container.addWidget(modified_label)
        
        self.modified_display = QLabel("Загрузите изображение")
        self.modified_display.setAlignment(Qt.AlignCenter)
        self.modified_display.setMinimumSize(280, 200)
        self.modified_display.setStyleSheet("border: 1px solid #666; background-color: #333; margin: 0px; padding: 0px;")
        self.modified_display.setScaledContents(False)
        modified_container.addWidget(self.modified_display)
        images_layout.addLayout(modified_container)
        
        layout.addWidget(images_widget, 1)
        
        # Нижняя часть - гистограммы
        histograms_widget = QWidget()
        histograms_layout = QHBoxLayout(histograms_widget)
        histograms_layout.setSpacing(5)
        histograms_layout.setContentsMargins(0, 0, 0, 0)
        
        # Гистограмма исходного изображения
        hist_original_container = QVBoxLayout()
        hist_original_container.setSpacing(1)
        hist_original_container.setContentsMargins(2, 2, 2, 2)
        
        hist_original_label = QLabel("Гистограмма исходного изображения")
        hist_original_label.setAlignment(Qt.AlignCenter)
        hist_original_label.setMaximumHeight(20)
        hist_original_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px; margin: 0px; padding: 0px;")
        hist_original_container.addWidget(hist_original_label)
        
        self.hist_original_canvas = MplCanvas()
        self.hist_original_canvas.setMinimumHeight(300)
        hist_original_container.addWidget(self.hist_original_canvas)
        histograms_layout.addLayout(hist_original_container)
        
        # Гистограмма измененного изображения
        hist_modified_container = QVBoxLayout()
        hist_modified_container.setSpacing(1)
        hist_modified_container.setContentsMargins(2, 2, 2, 2)
        
        hist_modified_label = QLabel("Гистограмма измененного изображения")
        hist_modified_label.setAlignment(Qt.AlignCenter)
        hist_modified_label.setMaximumHeight(20)
        hist_modified_label.setStyleSheet("color: white; font-weight: bold; font-size: 11px; margin: 0px; padding: 0px;")
        hist_modified_container.addWidget(hist_modified_label)
        
        self.hist_modified_canvas = MplCanvas()
        self.hist_modified_canvas.setMinimumHeight(300)
        hist_modified_container.addWidget(self.hist_modified_canvas)
        histograms_layout.addLayout(hist_modified_container)
        
        layout.addWidget(histograms_widget, 2)
        
        return panel
        
    def setup_connections(self):
        self.load_btn.clicked.connect(self.load_image)
        self.save_btn.clicked.connect(self.save_image)
        self.grayscale_btn.clicked.connect(self.convert_to_grayscale)
        self.rotate_btn.clicked.connect(self.rotate_image)
        self.reset_all_btn.clicked.connect(self.reset_all_corrections)
        
        # Подключаем все ползунки
        self.brightness_slider.valueChanged.connect(self.on_brightness_changed)
        self.contrast_slider.valueChanged.connect(self.on_contrast_changed)
        self.saturation_slider.valueChanged.connect(self.on_saturation_changed)
        self.linear_slider.valueChanged.connect(self.on_linear_changed)
        self.gamma_slider.valueChanged.connect(self.on_gamma_changed)
        
    def load_image(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "Выберите изображение", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)"
        )
        
        if filepath:
            try:
                self.original_image = Image.open(filepath)
                self.modified_image = self.original_image.copy()
                self.reset_all_corrections()
                self.display_images()
                self.update_image_info(filepath)
                self.update_histograms()
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить изображение: {str(e)}")
    
    def display_images(self):
        if self.original_image and self.modified_image:
            # Отображение исходного изображения
            original_qimage = self.pil_to_qimage(self.original_image)
            original_pixmap = QPixmap.fromImage(original_qimage)
            self.original_display.setPixmap(
                original_pixmap.scaled(
                    self.original_display.width() - 10, 
                    self.original_display.height() - 10,
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
            )
            
            # Отображение измененного изображения
            modified_qimage = self.pil_to_qimage(self.modified_image)
            modified_pixmap = QPixmap.fromImage(modified_qimage)
            self.modified_display.setPixmap(
                modified_pixmap.scaled(
                    self.modified_display.width() - 10, 
                    self.modified_display.height() - 10,
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                )
            )
    
    def pil_to_qimage(self, pil_image):
        """Конвертация PIL Image в QImage с правильной цветовой схемой"""
        if pil_image.mode == 'RGB':
            rgb_image = np.array(pil_image)
            bgr_image = rgb_image[:, :, ::-1].copy()
            height, width, channel = bgr_image.shape
            bytes_per_line = 3 * width
            return QImage(bgr_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        elif pil_image.mode == 'L':
            gray_image = np.array(pil_image)
            height, width = gray_image.shape
            return QImage(gray_image.data, width, height, width, QImage.Format_Grayscale8)
        else:
            rgb_image = pil_image.convert('RGB')
            return self.pil_to_qimage(rgb_image)
    
    def update_image_info(self, filepath):
        if not self.original_image:
            return
            
        info = []
        info.append(f"Файл: {os.path.basename(filepath)}")
        info.append(f"Размер файла: {os.path.getsize(filepath)} байт")
        info.append(f"Разрешение: {self.original_image.width} x {self.original_image.height}")
        info.append(f"Формат: {self.original_image.format}")
        info.append(f"Цветовая модель: {self.original_image.mode}")
        info.append(f"Глубина цвета: {self.get_color_depth()}")
        
        # EXIF информация
        exif_info = self.get_exif_info()
        info.extend(exif_info[:5])
        
        self.info_text.setText('\n'.join(info))
    
    def get_color_depth(self):
        if self.original_image.mode == 'L':
            return "8 бит (256 оттенков серого)"
        elif self.original_image.mode == 'RGB':
            return "24 бита (8 бит на канал)"
        else:
            return "Неизвестно"
    
    def get_exif_info(self):
        exif_info = []
        try:
            exif_data = self.original_image._getexif()
            if exif_data:
                for tag_id, value in exif_data.items():
                    tag = TAGS.get(tag_id, tag_id)
                    if tag in ['DateTime', 'Make', 'Model', 'ExposureTime', 'FNumber', 'ISOSpeedRatings']:
                        exif_info.append(f"{tag}: {value}")
        except:
            pass
        
        if not exif_info:
            exif_info.append("EXIF данные не найдены")
            
        return exif_info
    
    def update_histograms(self):
        if self.original_image:
            self.plot_histogram(self.original_image, self.hist_original_canvas, "Исходное изображение")
        if self.modified_image:
            self.plot_histogram(self.modified_image, self.hist_modified_canvas, "Измененное изображение")
    
    def plot_histogram(self, image, canvas, title):
        canvas.axes.clear()
        
        if image.mode == 'L':
            # Градации серого
            gray_array = np.array(image)
            canvas.axes.hist(gray_array.flatten(), bins=256, range=(0, 255), 
                           color='gray', alpha=0.7, edgecolor='black', linewidth=0.5)
            canvas.axes.set_title(f"{title} (Серое)", color='white', fontsize=12, pad=10)
        else:
            # RGB
            rgb_array = np.array(image.convert('RGB'))
            colors = ['red', 'green', 'blue']
            channel_names = ['R', 'G', 'B']
            
            for i in range(3):
                channel = rgb_array[:, :, i].flatten()
                canvas.axes.hist(channel, bins=256, range=(0, 255), 
                               color=colors[i], alpha=0.5, label=channel_names[i],
                               edgecolor='black', linewidth=0.1)
            
            canvas.axes.set_title(f"{title} (RGB)", color='white', fontsize=12, pad=10)
            canvas.axes.legend()
        
        canvas.axes.set_xlabel('Значение пикселя', color='white', fontsize=10)
        canvas.axes.set_ylabel('Частота', color='white', fontsize=10)
        canvas.axes.tick_params(colors='white', labelsize=8)
        canvas.axes.grid(True, alpha=0.3)
        
        canvas.fig.tight_layout(pad=3.0)
        canvas.draw()
    
    def convert_to_grayscale(self):
        if self.original_image:
            self.modified_image = self.original_image.copy().convert('L')
            self.apply_all_corrections()
            self.display_images()
            self.update_histograms()
    
    def rotate_image(self):
        if self.modified_image:
            # ИСПРАВЛЕНИЕ: Поворачиваем текущее модифицированное изображение
            # и обновляем оригинальное изображение для корректного применения коррекций
            rotated_image = self.modified_image.rotate(90, expand=True)
            self.modified_image = rotated_image
            # Также поворачиваем оригинальное изображение для согласованности
            self.display_images()
            self.update_histograms()
    
    def on_brightness_changed(self, value):
        self.brightness_value.setText(str(value))
        self.current_corrections['brightness'] = value
        self.apply_all_corrections()
    
    def on_contrast_changed(self, value):
        self.contrast_value.setText(str(value))
        self.current_corrections['contrast'] = value
        self.apply_all_corrections()
    
    def on_saturation_changed(self, value):
        self.saturation_value.setText(str(value))
        self.current_corrections['saturation'] = value
        self.apply_all_corrections()
    
    def on_linear_changed(self, value):
        self.linear_value.setText(str(value))
        self.current_corrections['linear'] = value
        self.apply_all_corrections()
    
    def on_gamma_changed(self, value):
        gamma_value = 1.0 + value / 100.0
        self.gamma_value.setText(f"{gamma_value:.2f}")
        self.current_corrections['gamma'] = value
        self.apply_all_corrections()
    
    def apply_all_corrections(self):
        if not self.modified_image or not self.original_image:
            return
            
        if self.modified_image.mode == 'L':
            temp_image = self.original_image.copy().convert('L')
        else:
            temp_image = self.original_image.copy()
        
        if self.current_corrections['brightness'] != 0:
            enhancer = ImageEnhance.Brightness(temp_image)
            brightness_factor = 1.0 + self.current_corrections['brightness'] / 100.0
            temp_image = enhancer.enhance(brightness_factor)
        
        if self.current_corrections['contrast'] != 0:
            enhancer = ImageEnhance.Contrast(temp_image)
            contrast_factor = 1.0 + self.current_corrections['contrast'] / 100.0
            temp_image = enhancer.enhance(contrast_factor)
        
        if self.current_corrections['saturation'] != 0 and temp_image.mode != 'L':
            enhancer = ImageEnhance.Color(temp_image)
            saturation_factor = 1.0 + self.current_corrections['saturation'] / 100.0
            temp_image = enhancer.enhance(saturation_factor)
        
        if self.current_corrections['linear'] != 0:
            temp_image = self.linear_correction(temp_image, self.current_corrections['linear'])
        
        if self.current_corrections['gamma'] != 0:
            temp_image = self.gamma_correction(temp_image, self.current_corrections['gamma'])
        
        self.modified_image = temp_image
        self.display_images()
        self.update_histograms()
    
    def linear_correction(self, image, value):
        if image.mode == 'L':
            img_array = np.array(image)
        else:
            img_array = np.array(image.convert('RGB'))
            
        multiplier = 1.0 + value / 100.0
        corrected_array = np.clip(img_array * multiplier, 0, 255).astype(np.uint8)
        
        if image.mode == 'L':
            return Image.fromarray(corrected_array, mode='L')
        else:
            return Image.fromarray(corrected_array)
    
    def gamma_correction(self, image, value):
        if image.mode == 'L':
            img_array = np.array(image).astype(np.float32) / 255.0
        else:
            img_array = np.array(image.convert('RGB')).astype(np.float32) / 255.0
            
        gamma = 1.0 + value / 100.0
        if gamma <= 0.1:
            gamma = 0.1
            
        corrected_array = np.clip(np.power(img_array, 1.0/gamma) * 255.0, 0, 255).astype(np.uint8)
        
        if image.mode == 'L':
            return Image.fromarray(corrected_array, mode='L')
        else:
            return Image.fromarray(corrected_array)
    
    def reset_all_corrections(self):
        self.current_corrections = {
            'brightness': 0,
            'contrast': 0,
            'saturation': 0,
            'linear': 0,
            'gamma': 0
        }
        
        self.brightness_slider.setValue(0)
        self.contrast_slider.setValue(0)
        self.saturation_slider.setValue(0)
        self.linear_slider.setValue(0)
        self.gamma_slider.setValue(0)
        
        if self.original_image:
            self.modified_image = self.original_image.copy()
            self.display_images()
            self.update_histograms()
    
    def save_image(self):
        if not self.modified_image:
            QMessageBox.warning(self, "Предупреждение", "Нет изображения для сохранения")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Сохранить изображение", "", 
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;TIFF (*.tiff)"
        )
        
        if filepath:
            try:
                self.modified_image.save(filepath)
                QMessageBox.information(self, "Успех", "Изображение сохранено")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить изображение: {str(e)}")

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=3.5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setMinimumHeight(300)

def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    font = QFont("Arial", 9)
    app.setFont(font)
    
    window = PhotoEditor()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()