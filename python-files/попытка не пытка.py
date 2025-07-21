#не лазь в коде , пидарас
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLineEdit, QPushButton, QLabel, QHBoxLayout,
                            QDialog, QColorDialog, QFileDialog, QFormLayout,
                            QComboBox, QGroupBox, QCheckBox, QSpinBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, QSettings, QSize
from PyQt5.QtGui import QPixmap, QColor, QIcon, QPalette, QBrush

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки Temmie.Net")
        self.setWindowIcon(QIcon("settings_icon.png"))
        self.resize(600, 500)
        
        self.settings = parent.settings
        self.main_window = parent
        self.icon_path = ""
        self.bg_image_path = ""
        
        layout = QVBoxLayout()
        
        # Группа внешнего вида
        appearance_group = QGroupBox("Внешний вид")
        form_layout = QFormLayout()
        
        # Выбор фона (цвет или изображение)
        self.bg_type_combo = QComboBox()
        self.bg_type_combo.addItems(["Цвет", "Изображение"])
        self.bg_type_combo.currentTextChanged.connect(self.toggle_bg_options)
        form_layout.addRow("Тип фона:", self.bg_type_combo)
        
        # Цвет фона
        self.bg_color_btn = QPushButton("Выбрать цвет")
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        form_layout.addRow("Цвет фона:", self.bg_color_btn)
        
        # Изображение фона
        self.bg_image_btn = QPushButton("Выбрать изображение")
        self.bg_image_btn.clicked.connect(self.choose_bg_image)
        form_layout.addRow("Изображение фона:", self.bg_image_btn)
        
        # Прозрачность фона
        self.bg_opacity_spin = QSpinBox()
        self.bg_opacity_spin.setRange(10, 100)
        self.bg_opacity_spin.setSuffix("%")
        form_layout.addRow("Прозрачность фона:", self.bg_opacity_spin)
        
        # Цвет текста
        self.text_color_btn = QPushButton("Выбрать цвет")
        self.text_color_btn.clicked.connect(self.choose_text_color)
        form_layout.addRow("Цвет текста:", self.text_color_btn)
        
        # Иконка
        self.icon_btn = QPushButton("Выбрать иконку")
        self.icon_btn.clicked.connect(self.choose_icon)
        form_layout.addRow("Иконка:", self.icon_btn)
        
        # Подзаголовок
        self.subtitle_edit = QLineEdit()
        form_layout.addRow("Подзаголовок:", self.subtitle_edit)
        
        # Размер шрифта заголовка
        self.title_size_spin = QSpinBox()
        self.title_size_spin.setRange(10, 72)
        self.title_size_spin.setSuffix("px")
        form_layout.addRow("Размер шрифта заголовка:", self.title_size_spin)
        
        # Масштаб
        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(["50%", "75%", "80%", "90%", "100%", "110%", "120%", "130%", "140%", "150%", "175%", "200%"])
        form_layout.addRow("Масштаб по умолчанию:", self.zoom_combo)
        
        # Стиль кнопок
        self.button_style_combo = QComboBox()
        self.button_style_combo.addItems(["Стандартный", "Плоский", "Градиент"])
        form_layout.addRow("Стиль кнопок:", self.button_style_combo)
        
        # Скругление кнопок
        self.button_radius_spin = QSpinBox()
        self.button_radius_spin.setRange(0, 30)
        self.button_radius_spin.setSuffix("px")
        form_layout.addRow("Скругление кнопок:", self.button_radius_spin)
        
        appearance_group.setLayout(form_layout)
        layout.addWidget(appearance_group)
        
        # Группа приватности
        privacy_group = QGroupBox("Приватность")
        privacy_layout = QVBoxLayout()
        
        self.js_checkbox = QCheckBox("Разрешить JavaScript")
        self.cookies_checkbox = QCheckBox("Разрешить cookies")
        self.cache_checkbox = QCheckBox("Разрешить кэширование")
        self.geolocation_checkbox = QCheckBox("Разрешить геолокацию")
        self.webgl_checkbox = QCheckBox("Разрешить WebGL")
        
        privacy_layout.addWidget(self.js_checkbox)
        privacy_layout.addWidget(self.cookies_checkbox)
        privacy_layout.addWidget(self.cache_checkbox)
        privacy_layout.addWidget(self.geolocation_checkbox)
        privacy_layout.addWidget(self.webgl_checkbox)
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Сохранить")
        save_btn.clicked.connect(self.save_settings)
        cancel_btn = QPushButton("Отмена")
        cancel_btn.clicked.connect(self.reject)
        reset_btn = QPushButton("Сбросить")
        reset_btn.clicked.connect(self.reset_settings)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(reset_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.load_settings()
        self.toggle_bg_options()
    
    def toggle_bg_options(self):
        bg_type = self.bg_type_combo.currentText()
        self.bg_color_btn.setVisible(bg_type == "Цвет")
        self.bg_image_btn.setVisible(bg_type == "Изображение")
    
    def load_settings(self):
        # Загрузка текущих настроек
        self.subtitle_edit.setText(self.settings.value("subtitle", ""))
        
        zoom = float(self.settings.value("zoom", "1.0")) * 100
        self.zoom_combo.setCurrentText(f"{int(zoom)}%")
        
        # Цвета
        bg_color = self.settings.value("bg_color", "#0a1f3a")
        self.bg_color_btn.setStyleSheet(f"background-color: {bg_color};")
        
        text_color = self.settings.value("text_color", "#f4b400")
        self.text_color_btn.setStyleSheet(f"background-color: {text_color};")
        
        # Тип фона
        bg_type = self.settings.value("bg_type", "Цвет")
        self.bg_type_combo.setCurrentText(bg_type)
        
        # Прозрачность
        opacity = int(float(self.settings.value("bg_opacity", "1.0")) * 100)
        self.bg_opacity_spin.setValue(opacity)
        
        # Размер шрифта
        title_size = int(self.settings.value("title_size", "52"))
        self.title_size_spin.setValue(title_size)
        
        # Стиль кнопок
        button_style = self.settings.value("button_style", "Стандартный")
        self.button_style_combo.setCurrentText(button_style)
        
        # Скругление кнопок
        button_radius = int(self.settings.value("button_radius", "15"))
        self.button_radius_spin.setValue(button_radius)
        
        # Настройки приватности
        self.js_checkbox.setChecked(self.settings.value("javascript", False, type=bool))
        self.cookies_checkbox.setChecked(self.settings.value("cookies", False, type=bool))
        self.cache_checkbox.setChecked(self.settings.value("cache", False, type=bool))
        self.geolocation_checkbox.setChecked(self.settings.value("geolocation", False, type=bool))
        self.webgl_checkbox.setChecked(self.settings.value("webgl", False, type=bool))
    
    def choose_bg_color(self):
        color = QColorDialog.getColor(QColor(self.settings.value("bg_color", "#0a1f3a")))
        if color.isValid():
            self.bg_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def choose_text_color(self):
        color = QColorDialog.getColor(QColor(self.settings.value("text_color", "#f4b400")))
        if color.isValid():
            self.text_color_btn.setStyleSheet(f"background-color: {color.name()};")
    
    def choose_icon(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите иконку", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.icon_path = file
    
    def choose_bg_image(self):
        file, _ = QFileDialog.getOpenFileName(self, "Выберите фоновое изображение", "", "Images (*.png *.jpg *.bmp)")
        if file:
            self.bg_image_path = file
    
    def reset_settings(self):
        self.settings.clear()
        self.load_settings()
    
    def save_settings(self):
        # Сохраняем настройки
        self.settings.setValue("bg_type", self.bg_type_combo.currentText())
        self.settings.setValue("bg_color", self.bg_color_btn.palette().button().color().name())
        self.settings.setValue("text_color", self.text_color_btn.palette().button().color().name())
        self.settings.setValue("subtitle", self.subtitle_edit.text())
        
        opacity = self.bg_opacity_spin.value() / 100
        self.settings.setValue("bg_opacity", str(opacity))
        
        if self.icon_path:
            self.settings.setValue("icon_path", self.icon_path)
        
        if self.bg_image_path:
            self.settings.setValue("bg_image_path", self.bg_image_path)
        
        zoom = int(self.zoom_combo.currentText().replace("%", "")) / 100
        self.settings.setValue("zoom", str(zoom))
        
        self.settings.setValue("title_size", self.title_size_spin.value())
        self.settings.setValue("button_style", self.button_style_combo.currentText())
        self.settings.setValue("button_radius", self.button_radius_spin.value())
        
        # Настройки приватности
        self.settings.setValue("javascript", self.js_checkbox.isChecked())
        self.settings.setValue("cookies", self.cookies_checkbox.isChecked())
        self.settings.setValue("cache", self.cache_checkbox.isChecked())
        self.settings.setValue("geolocation", self.geolocation_checkbox.isChecked())
        self.settings.setValue("webgl", self.webgl_checkbox.isChecked())
        
        # Применяем изменения
        self.main_window.apply_settings()
        self.accept()

class TemmieBrowser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("TemmieNet", "SecureBrowser")
        self.init_ui()
        self.apply_settings()
    
    def init_ui(self):
        self.setWindowTitle("Temmie.Net - Secure Browser")
        self.resize(1280, 900)
        self.is_fullscreen = False
        
        # Создаем кнопку настроек
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.clicked.connect(self.show_settings)
        
        # Главный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setSpacing(20)
        
        # --- Заголовок с логотипом и кнопкой настроек ---
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignCenter)
        
        # Логотип
        self.temmie_logo = QLabel()
        title_layout.addWidget(self.temmie_logo)
        
        # Название и подзаголовок
        text_layout = QVBoxLayout()
        self.title_label = QLabel("Temmie.Net")
        self.subtitle_label = QLabel()
        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.subtitle_label)
        title_layout.addLayout(text_layout)
        
        # Кнопка настроек (в правом углу)
        title_layout.addStretch()
        title_layout.addWidget(self.settings_btn)
        
        self.layout.addLayout(title_layout)
        
        # --- Поисковая строка ---
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Введите запрос или URL...")
        self.search_bar.returnPressed.connect(self.search)
        self.layout.addWidget(self.search_bar, alignment=Qt.AlignCenter)
        
        # --- Кнопки ---
        self.init_buttons()
        
        # --- Браузер ---
        self.init_browser()
        
        # --- Кнопка "Зайти в телеграмм Temmie" ---
        self.telegram_btn = QPushButton("Зайти в телеграмм Temmie")
        self.telegram_btn.setIcon(QIcon.fromTheme("internet-telegram"))
        self.telegram_btn.setIconSize(QSize(24, 24))
        self.telegram_btn.clicked.connect(lambda: self.browser.setUrl(QUrl("https://t.me/pickup12345")))
        self.layout.addWidget(self.telegram_btn, alignment=Qt.AlignCenter)
        
        # Копирайт
        self.copyright_label = QLabel("сделано темми и дипсиком | Персонализированная версия")
        self.copyright_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.copyright_label)
        
        # Отступы
        self.layout.setContentsMargins(30, 20, 30, 15)
        
        # Горячие клавиши
        self.search_bar.setFocus()
    
    def init_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        
        # Кнопка "Поискать"
        search_button = QPushButton("🔍 Поискать")
        search_button.clicked.connect(self.search)
        button_layout.addWidget(search_button)
        
        # Кнопка "Полный экран"
        fullscreen_button = QPushButton("🖥 Полный экран (F11)")
        fullscreen_button.clicked.connect(self.toggle_fullscreen)
        button_layout.addWidget(fullscreen_button)
        
        # Кнопки масштаба
        zoom_in_button = QPushButton("➕ Увеличить")
        zoom_in_button.clicked.connect(self.zoom_in)
        button_layout.addWidget(zoom_in_button)
        
        zoom_out_button = QPushButton("➖ Уменьшить")
        zoom_out_button.clicked.connect(self.zoom_out)
        button_layout.addWidget(zoom_out_button)
        
        self.layout.addLayout(button_layout)
    
    def init_browser(self):
        self.browser = QWebEngineView()
        self.profile = QWebEngineProfile("TemmiePrivateProfile", self.browser)
        self.apply_privacy_settings()
        
        self.layout.addWidget(self.browser, stretch=1)
    
    def apply_settings(self):
        # Применяем настройки внешнего вида
        bg_type = self.settings.value("bg_type", "Цвет")
        text_color = self.settings.value("text_color", "#f4b400")
        opacity = float(self.settings.value("bg_opacity", "1.0"))
        title_size = self.settings.value("title_size", "52")
        button_style = self.settings.value("button_style", "Стандартный")
        button_radius = self.settings.value("button_radius", "15")
        
        # Устанавливаем фон
        if bg_type == "Цвет":
            bg_color = self.settings.value("bg_color", "#0a1f3a")
            self.setStyleSheet(f"QMainWindow {{ background-color: {bg_color}; }}")
        else:
            bg_image = self.settings.value("bg_image_path", "")
            if bg_image:
                palette = self.palette()
                palette.setBrush(QPalette.Window, QBrush(QPixmap(bg_image)))
                self.setPalette(palette)
        
        # Стиль кнопок
        button_style_sheet = ""
        if button_style == "Плоский":
            button_style_sheet = "border: none;"
        elif button_style == "Градиент":
            button_style_sheet = f"""
                border: none;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {text_color}, stop:1 #f6c542);
            """
        else:  # Стандартный
            button_style_sheet = f"background-color: {text_color};"
        
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: transparent;
            }}
            QLineEdit {{
                background-color: rgba(255, 255, 255, {opacity*0.8});
                color: #000000;
                border-radius: 15px;
                padding: 10px;
                font-size: 18px;
                min-width: 400px;
                border: 2px solid {text_color};
            }}
            QPushButton {{
                {button_style_sheet}
                color: #000000;
                border-radius: {button_radius}px;
                padding: 10px 20px;
                font-size: 16px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #f6c542;
            }}
            QWebEngineView {{
                background-color: #121212;
                border-radius: 10px;
            }}
        """)
        
        # Заголовок и подзаголовок
        self.title_label.setStyleSheet(f"""
            color: {text_color};
            font-size: {title_size}px;
            font-weight: bold;
            margin-left: 15px;
        """)
        
        subtitle = self.settings.value("subtitle", "")
        self.subtitle_label.setText(subtitle)
        self.subtitle_label.setStyleSheet(f"""
            color: {text_color};
            font-size: 16px;
            margin-left: 15px;
        """)
        
        # Кнопка настроек
        self.settings_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: {text_color};
            }}
            QPushButton:hover {{
                color: #ffffff;
            }}
        """)
        
        # Иконка
        icon_path = self.settings.value("icon_path", "temmie.png")
        try:
            pixmap = QPixmap(icon_path).scaled(72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.temmie_logo.setPixmap(pixmap)
        except:
            pass
        
        # Масштаб
        zoom = float(self.settings.value("zoom", "1.0"))
        self.browser.setZoomFactor(zoom)
        
        # Приватность
        self.apply_privacy_settings()
        
        # Обновляем палитру
        palette = self.palette()
        palette.setColor(palette.WindowText, QColor(text_color))
        palette.setColor(palette.ButtonText, QColor(text_color))
        self.setPalette(palette)
    
    def apply_privacy_settings(self):
        # Применяем настройки приватности
        js_enabled = self.settings.value("javascript", False, type=bool)
        cookies_enabled = self.settings.value("cookies", False, type=bool)
        cache_enabled = self.settings.value("cache", False, type=bool)
        geolocation_enabled = self.settings.value("geolocation", False, type=bool)
        webgl_enabled = self.settings.value("webgl", False, type=bool)
        
        settings = self.browser.settings()
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, js_enabled)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, cookies_enabled)
        settings.setAttribute(QWebEngineSettings.ScreenCaptureEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebGLEnabled, webgl_enabled)
        settings.setAttribute(QWebEngineSettings.AllowGeolocationOnInsecureOrigins, geolocation_enabled)
        
        self.profile.setHttpCacheType(QWebEngineProfile.NoCache if not cache_enabled else QWebEngineProfile.DiskHttpCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies if not cookies_enabled else QWebEngineProfile.AllowPersistentCookies)
    
    def show_settings(self):
        dialog = SettingsDialog(self)
        dialog.exec_()
    
    def search(self):
        query = self.search_bar.text().strip()
        if not query:
            return
            
        if query.startswith(('http://', 'https://')):
            url = query
        elif '.' in query and ' ' not in query:
            url = f"https://{query}"
        else:
            url = f"https://duckduckgo.com/?q={query}&kae=d&k1=-1&kaj=m&kam=osm&kau=-1"
        
        self.browser.setUrl(QUrl(url))
    
    def toggle_fullscreen(self):
        if self.is_fullscreen:
            self.showNormal()
        else:
            self.showFullScreen()
        self.is_fullscreen = not self.is_fullscreen
    
    def zoom_in(self):
        current_zoom = self.browser.zoomFactor()
        self.browser.setZoomFactor(min(current_zoom + 0.1, 3.0))
    
    def zoom_out(self):
        current_zoom = self.browser.zoomFactor()
        self.browser.setZoomFactor(max(current_zoom - 0.1, 0.5))
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.toggle_fullscreen()
        elif event.key() == Qt.Key_Escape and self.is_fullscreen:
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    browser = TemmieBrowser()
    browser.show()
    sys.exit(app.exec_())
