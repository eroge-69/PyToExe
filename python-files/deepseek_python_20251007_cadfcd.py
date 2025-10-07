import sys
import traceback
import random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor, QLinearGradient, QPainter, QPixmap, QPen, QBrush
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, pyqtProperty
import json
import os
import re
import urllib.parse

class ParticleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.particles = []
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_particles)
        self.timer.start(50)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        
    def update_particles(self):
        if random.random() < 0.3:
            self.particles.append({
                'x': random.randint(0, self.width()),
                'y': -10,
                'size': random.randint(2, 6),
                'speed': random.uniform(1, 3),
                'color': random.choice([
                    QColor(255, 107, 157, 100),
                    QColor(157, 101, 255, 100),
                    QColor(107, 214, 255, 100)
                ])
            })
        
        for particle in self.particles[:]:
            particle['y'] += particle['speed']
            if particle['y'] > self.height():
                self.particles.remove(particle)
                
        self.update()
        
    def paintEvent(self, event):
        if not self.particles:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for particle in self.particles:
            painter.setBrush(particle['color'])
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(particle['x']), 
                int(particle['y']), 
                particle['size'], 
                particle['size']
            )

class LoadingSpinner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.setFixedSize(20, 20)
        self.hide()
        
    def update_rotation(self):
        self.angle = (self.angle + 10) % 360
        self.update()
        
    def start(self):
        self.angle = 0
        self.show()
        self.timer.start(25)
        
    def stop(self):
        self.timer.stop()
        self.hide()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        
        gradient = QConicalGradient(10, 10, self.angle)
        gradient.setColorAt(0, QColor(255, 107, 157, 200))
        gradient.setColorAt(0.3, QColor(157, 101, 255, 200))
        gradient.setColorAt(0.6, QColor(107, 214, 255, 200))
        gradient.setColorAt(1, QColor(255, 107, 157, 200))
        
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(2, 2, 16, 16)

class CustomSearchEngine:
    """Кастомная поисковая система"""
    
    @staticmethod
    def search(query, engine="quantum"):
        """Выполняет поиск используя выбранную поисковую систему"""
        encoded_query = urllib.parse.quote(query)
        
        search_engines = {
            "quantum": f"https://www.google.com/search?q={encoded_query}",
            "google": f"https://www.google.com/search?q={encoded_query}",
            "yandex": f"https://yandex.ru/search/?text={encoded_query}",
            "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}",
            "bing": f"https://www.bing.com/search?q={encoded_query}"
        }
        
        return search_engines.get(engine, search_engines["quantum"])
    
    @staticmethod
    def get_engine_name(engine):
        """Возвращает читаемое имя поисковой системы"""
        names = {
            "quantum": "Quantum Search",
            "google": "Google",
            "yandex": "Яндекс",
            "duckduckgo": "DuckDuckGo",
            "bing": "Bing"
        }
        return names.get(engine, "Quantum Search")

class ModernBrowser(QMainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setWindowTitle("Quantum Browser")
            self.resize(1400, 900)
            self.setMinimumSize(800, 600)
            
            # Включаем аппаратное ускорение
            self.setAttribute(Qt.WA_TranslucentBackground)
            self.setAttribute(Qt.WA_NoSystemBackground, False)
            
            # Настройки браузера
            self.settings = self.load_settings()
            self.current_search_engine = self.settings.get("search_engine", "quantum")
            
            # Создаем виджет для частиц
            self.particle_widget = ParticleWidget(self)
            self.particle_widget.lower()
            
            # Устанавливаем современный стиль
            self.set_modern_style()
            
            # Центральный виджет для вкладок
            self.tabs = QTabWidget()
            self.tabs.setDocumentMode(True)
            self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
            self.tabs.currentChanged.connect(self.current_tab_changed)
            self.tabs.setTabsClosable(True)
            self.tabs.tabCloseRequested.connect(self.close_current_tab)
            self.tabs.setMovable(True)
            
            # Обработка средней кнопки мыши для закрытия вкладок
            self.tabs.tabBar().installEventFilter(self)
            
            self.setCentralWidget(self.tabs)
            
            # Создаем панель навигации
            self.create_modern_navbar()
            
            # Загрузка данных
            self.bookmarks = self.load_data('bookmarks.json')
            self.history = self.load_data('history.json')
            
            # Создаем начальную вкладку с главной страницей
            self.add_new_tab(home_page=True)
            
            # Устанавливаем иконку
            self.setWindowIcon(self.create_modern_icon())
            
            # Анимация появления
            self.fade_in_animation()
            
        except Exception as e:
            print(f"Ошибка в инициализации: {e}")
            traceback.print_exc()
    
    def eventFilter(self, obj, event):
        """Обработка событий для закрытия вкладок средней кнопкой мыши"""
        if obj == self.tabs.tabBar() and event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.MiddleButton:
                tab_index = obj.tabAt(event.pos())
                if tab_index >= 0:
                    self.close_current_tab(tab_index)
                    return True
        return super().eventFilter(obj, event)
    
    def closeEvent(self, event):
        """Обработчик закрытия окна - останавливаем все медиа"""
        try:
            # Останавливаем все вкладки перед закрытием
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if isinstance(browser, QWebEngineView):
                    # Останавливаем загрузку и выполняем JavaScript для остановки медиа
                    browser.stop()
                    browser.page().runJavaScript("""
                        // Останавливаем все видео и аудио
                        var videos = document.querySelectorAll('video');
                        var audios = document.querySelectorAll('audio');
                        
                        videos.forEach(function(video) {
                            video.pause();
                            video.currentTime = 0;
                        });
                        
                        audios.forEach(function(audio) {
                            audio.pause();
                            audio.currentTime = 0;
                        });
                        
                        // Останавливаем любые WebRTC соединения
                        if (window.stream) {
                            window.stream.getTracks().forEach(track => track.stop());
                        }
                        
                        // Выходим из полноэкранного режима
                        if (document.fullscreenElement) {
                            document.exitFullscreen();
                        }
                    """)
            
            # Сохраняем настройки
            self.save_settings()
            
        except Exception as e:
            print(f"Ошибка при закрытии: {e}")
        
        event.accept()
    
    def load_settings(self):
        """Загружает настройки браузера"""
        try:
            if os.path.exists('browser_settings.json'):
                with open('browser_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки настроек: {e}")
        return {}
    
    def save_settings(self):
        """Сохраняет настройки браузера"""
        try:
            settings = {
                "search_engine": self.current_search_engine,
                "window_size": [self.width(), self.height()],
                "window_position": [self.x(), self.y()]
            }
            with open('browser_settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")
    
    def fade_in_animation(self):
        """Анимация плавного появления окна"""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(500)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        self.animation.start()
    
    def set_modern_style(self):
        """Устанавливает современный стиль"""
        modern_style = """
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #0f0c29, stop: 0.5 #302b63, stop: 1 #24243e);
                color: #ffffff;
                font-family: "Segoe UI", sans-serif;
            }
            
            QToolBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(26, 26, 46, 0.95), stop: 1 rgba(22, 33, 62, 0.95));
                border: none;
                border-bottom: 1px solid rgba(255, 107, 157, 0.3);
                spacing: 8px;
                padding: 8px;
            }
            
            QLineEdit {
                background: rgba(13, 13, 26, 0.9);
                border: 2px solid rgba(255, 107, 157, 0.5);
                border-radius: 20px;
                padding: 8px 15px;
                color: #ffffff;
                font-size: 14px;
                font-weight: 500;
                selection-background-color: rgba(255, 107, 157, 0.3);
                selection-color: #ffffff;
                min-height: 20px;
            }
            
            QLineEdit:focus {
                border: 2px solid rgba(157, 101, 255, 0.8);
                background: rgba(13, 13, 26, 0.95);
            }
            
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(255, 107, 157, 0.8), stop: 1 rgba(157, 101, 255, 0.8));
                border: none;
                border-radius: 15px;
                padding: 8px 15px;
                color: #ffffff;
                font-weight: 600;
                font-size: 12px;
                min-width: 60px;
                min-height: 30px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(255, 107, 157, 1), stop: 1 rgba(157, 101, 255, 1));
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                            stop: 0 rgba(255, 107, 157, 0.6), stop: 1 rgba(157, 101, 255, 0.6));
            }
            
            QTabWidget::pane {
                border: none;
                background: transparent;
            }
            
            QTabBar::tab {
                background: rgba(45, 45, 65, 0.7);
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 8px 15px;
                color: #a0a0c0;
                font-weight: 500;
                margin-right: 2px;
                min-width: 120px;
                min-height: 25px;
            }
            
            QTabBar::tab:selected {
                background: rgba(255, 107, 157, 0.9);
                color: #ffffff;
            }
            
            QTabBar::tab:hover:!selected {
                background: rgba(157, 101, 255, 0.7);
                color: #ffffff;
            }
            
            QListWidget {
                background: rgba(13, 13, 26, 0.9);
                border: 2px solid rgba(255, 107, 157, 0.3);
                border-radius: 10px;
                color: #ffffff;
                font-size: 12px;
                outline: none;
            }
            
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 107, 157, 0.2);
                background: transparent;
            }
            
            QListWidget::item:selected {
                background: rgba(255, 107, 157, 0.3);
                color: #ffffff;
                border-radius: 6px;
            }
            
            QListWidget::item:hover {
                background: rgba(157, 101, 255, 0.2);
                border-radius: 6px;
            }
            
            QDialog {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #0f0c29, stop: 1 #24243e);
                color: #ffffff;
                border-radius: 12px;
            }
            
            QMessageBox {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                            stop: 0 #0f0c29, stop: 1 #24243e);
                color: #ffffff;
            }
            
            QScrollBar:vertical {
                background: rgba(255, 107, 157, 0.1);
                width: 10px;
                border-radius: 5px;
            }
            
            QScrollBar::handle:vertical {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop: 0 #ff6b9d, stop: 1 #9d65ff);
                border-radius: 5px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop: 0 #ff4785, stop: 1 #8a4dff);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid rgba(255, 107, 157, 0.5);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffffff;
                background: transparent;
            }
            
            QRadioButton {
                color: #ffffff;
                font-size: 14px;
                padding: 8px;
                background: transparent;
            }
            
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            
            QRadioButton::indicator:unchecked {
                border: 2px solid rgba(255, 107, 157, 0.5);
                border-radius: 8px;
                background: rgba(255, 255, 255, 0.1);
            }
            
            QRadioButton::indicator:checked {
                border: 2px solid rgba(255, 107, 157, 0.8);
                border-radius: 8px;
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.4,
                                            fx:0.5, fy:0.5,
                                            stop:0 rgba(255, 107, 157, 1),
                                            stop:1 rgba(157, 101, 255, 1));
            }
        """
        self.setStyleSheet(modern_style)
        
        # Устанавливаем современный шрифт
        font = QFont("Segoe UI", 9)
        font.setWeight(QFont.Normal)
        QApplication.setFont(font)
    
    def create_modern_navbar(self):
        """Создает современную панель навигации"""
        navbar = QToolBar()
        navbar.setMovable(False)
        navbar.setIconSize(QSize(18, 18))
        navbar.setFixedHeight(60)
        self.addToolBar(navbar)
        
        # Логотип и название
        logo_widget = QWidget()
        logo_layout = QHBoxLayout(logo_widget)
        logo_layout.setContentsMargins(5, 0, 15, 0)
        logo_layout.setSpacing(8)
        
        # Иконка браузера
        icon_label = QLabel()
        icon_pixmap = self.create_modern_icon().pixmap(28, 28)
        icon_label.setPixmap(icon_pixmap)
        logo_layout.addWidget(icon_label)
        
        # Название с градиентным эффектом
        title_label = QLabel("Quantum")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 16px;
                font-weight: bold;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #ff6b9d, stop:0.5 #9d65ff, stop:1 #6bd5ff);
                padding: 3px 8px;
                border-radius: 8px;
            }
        """)
        logo_layout.addWidget(title_label)
        logo_layout.addStretch()
        
        navbar.addWidget(logo_widget)
        
        navbar.addSeparator()
        
        # Кнопки навигации
        nav_buttons = [
            ('◀', self.navigate_back, "Назад"),
            ('▶', self.navigate_forward, "Вперед"),
            ('⟳', self.navigate_reload, "Обновить"),
            ('⌂', self.navigate_home, "Домой"),
        ]
        
        for icon, handler, tooltip in nav_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(35, 35)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(255, 107, 157, 0.3);
                    border: 1px solid rgba(255, 107, 157, 0.5);
                    border-radius: 17px;
                    font-size: 14px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background: rgba(255, 107, 157, 0.6);
                    border: 1px solid rgba(255, 107, 157, 0.8);
                }
                QPushButton:pressed {
                    background: rgba(255, 107, 157, 0.8);
                }
            """)
            btn.clicked.connect(handler)
            navbar.addWidget(btn)
        
        navbar.addSeparator()
        
        # Индикатор загрузки
        self.loading_spinner = LoadingSpinner()
        navbar.addWidget(self.loading_spinner)
        
        # Адресная строка
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("🔍 Введите URL или поисковый запрос...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setMinimumWidth(300)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background: rgba(13, 13, 26, 0.9);
                border: 2px solid rgba(255, 107, 157, 0.5);
                border-radius: 20px;
                padding: 8px 15px;
                color: #ffffff;
                font-size: 13px;
                font-weight: 500;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid rgba(157, 101, 255, 0.8);
                background: rgba(13, 13, 26, 0.95);
            }
        """)
        navbar.addWidget(self.url_bar)
        
        navbar.addSeparator()
        
        # Функциональные кнопки
        func_buttons = [
            ('⭐', self.add_bookmark, "Добавить в закладки"),
            ('📚', self.show_bookmarks, "Закладки"),
            ('⚡', self.create_desktop_shortcut, "Создать ярлык"),
            ('🔍', self.show_search_settings, "Настройки поиска"),
            ('➕', lambda: self.add_new_tab(), "Новая вкладка"),
        ]
        
        for icon, handler, tooltip in func_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.setFixedSize(35, 35)
            btn.setStyleSheet("""
                QPushButton {
                    background: rgba(157, 101, 255, 0.3);
                    border: 1px solid rgba(157, 101, 255, 0.5);
                    border-radius: 17px;
                    font-size: 14px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background: rgba(157, 101, 255, 0.6);
                    border: 1px solid rgba(157, 101, 255, 0.8);
                }
                QPushButton:pressed {
                    background: rgba(157, 101, 255, 0.8);
                }
            """)
            btn.clicked.connect(handler)
            navbar.addWidget(btn)
    
    def show_search_settings(self):
        """Показывает настройки поисковой системы"""
        dialog = QDialog(self)
        dialog.setWindowTitle("🔍 Настройки поиска")
        dialog.resize(450, 350)
        dialog.setWindowIcon(self.create_modern_icon())
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Выберите поисковую систему")
        title.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                text-align: center;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #ff6b9d, stop:0.5 #9d65ff, stop:1 #6bd5ff);
                border-radius: 8px;
                margin: 5px;
            }
        """)
        layout.addWidget(title)
        
        # Группа поисковых систем
        search_group = QGroupBox("Доступные поисковые системы")
        search_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid rgba(255, 107, 157, 0.5);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background: rgba(13, 13, 26, 0.6);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #ffffff;
                background: transparent;
            }
        """)
        
        search_layout = QVBoxLayout()
        
        search_engines = [
            ("quantum", "Quantum Search (рекомендуется)"),
            ("google", "Google"),
            ("yandex", "Яндекс"),
            ("duckduckgo", "DuckDuckGo"),
            ("bing", "Bing")
        ]
        
        self.search_buttons = QButtonGroup()
        for engine_id, engine_name in search_engines:
            radio = QRadioButton(engine_name)
            radio.engine_id = engine_id
            if engine_id == self.current_search_engine:
                radio.setChecked(True)
            search_layout.addWidget(radio)
            self.search_buttons.addButton(radio)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Текущая выбранная система
        current_label = QLabel(f"Текущая: {CustomSearchEngine.get_engine_name(self.current_search_engine)}")
        current_label.setStyleSheet("""
            QLabel {
                color: #a0a0c0;
                font-size: 12px;
                padding: 5px;
                text-align: center;
            }
        """)
        layout.addWidget(current_label)
        
        layout.addStretch(1)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        apply_btn = QPushButton("✅ Применить")
        apply_btn.setStyleSheet(self.get_button_style("primary"))
        apply_btn.clicked.connect(lambda: self.apply_search_settings(dialog))
        button_layout.addWidget(apply_btn)
        
        cancel_btn = QPushButton("❌ Отмена")
        cancel_btn.setStyleSheet(self.get_button_style("secondary"))
        cancel_btn.clicked.connect(dialog.close)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec_()
    
    def apply_search_settings(self, dialog):
        """Применяет настройки поисковой системы"""
        checked_button = self.search_buttons.checkedButton()
        if checked_button:
            self.current_search_engine = checked_button.engine_id
            self.save_settings()
            self.show_modern_message("Успех", 
                                   f"Поисковая система изменена на: {CustomSearchEngine.get_engine_name(self.current_search_engine)}", 
                                   "info")
        dialog.close()
    
    def create_modern_icon(self):
        """Создает современную круглую иконку для браузера"""
        try:
            if os.path.exists("quantum_icon.ico"):
                return QIcon("quantum_icon.ico")
            elif os.path.exists("quantum_icon.png"):
                return QIcon("quantum_icon.png")
            else:
                pixmap = QPixmap(64, 64)
                pixmap.fill(Qt.transparent)
                painter = QPainter(pixmap)
                painter.setRenderHint(QPainter.Antialiasing)
                
                gradient = QRadialGradient(32, 32, 32)
                gradient.setColorAt(0, QColor(255, 107, 157))
                gradient.setColorAt(0.7, QColor(157, 101, 255))
                gradient.setColorAt(1, QColor(107, 214, 255))
                
                painter.setBrush(QBrush(gradient))
                painter.setPen(QPen(QColor(255, 255, 255, 150), 2))
                painter.drawEllipse(2, 2, 60, 60)
                
                painter.setBrush(QBrush(QColor(26, 26, 46, 220)))
                painter.drawEllipse(8, 8, 48, 48)
                
                painter.setPen(QPen(QColor(255, 255, 255), 3))
                painter.drawEllipse(16, 16, 32, 32)
                
                painter.drawLine(32, 20, 32, 44)
                painter.drawLine(20, 32, 44, 32)
                painter.drawArc(20, 20, 24, 24, 45 * 16, 180 * 16)
                
                painter.setBrush(QBrush(QColor(255, 255, 255)))
                painter.drawEllipse(31, 31, 2, 2)
                
                painter.end()
                return QIcon(pixmap)
        except Exception as e:
            print(f"Ошибка создания иконки: {e}")
            return QApplication.style().standardIcon(QStyle.SP_ComputerIcon)
    
    def handle_search_query(self, query):
        """Обрабатывает поисковый запрос"""
        if not query:
            return
        
        if self.is_url(query):
            if not query.startswith(('http://', 'https://')):
                query = 'https://' + query
            self.open_url_in_new_tab(query)
        else:
            # Используем выбранную поисковую систему
            search_url = CustomSearchEngine.search(query, self.current_search_engine)
            self.open_url_in_new_tab(search_url)
    
    def open_url_in_new_tab(self, url):
        """Открывает URL в новой вкладке"""
        self.add_new_tab(QUrl(url))
    
    def add_new_tab(self, qurl=None, label="🌐 Новая вкладка", home_page=False):
        try:
            if home_page:
                from home_page import HomePage
                home_widget = HomePage(self)
                
                container = QWidget()
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(home_widget)
                container.setLayout(layout)
                
                i = self.tabs.addTab(container, '🏠 Главная')
                self.tabs.setCurrentIndex(i)
            else:
                if qurl is None:
                    qurl = QUrl('https://www.google.com')
                
                # Создаем браузер с современным User-Agent
                browser = QWebEngineView()
                
                # Устанавливаем современный User-Agent чтобы избежать сообщений об устаревшем браузере
                profile = browser.page().profile()
                modern_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                profile.setHttpUserAgent(modern_user_agent)
                
                # Включаем аппаратное ускорение и оптимизации
                settings = browser.settings()
                settings.setAttribute(QWebEngineSettings.Accelerated2dCanvasEnabled, True)
                settings.setAttribute(QWebEngineSettings.WebGLEnabled, True)
                settings.setAttribute(QWebEngineSettings.PlaybackRequiresUserGesture, False)
                settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
                settings.setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
                
                # Поддержка полноэкранного режима
                browser.page().fullScreenRequested.connect(self.handle_fullscreen_request)
                
                browser.setUrl(qurl)
                
                i = self.tabs.addTab(browser, label)
                self.tabs.setCurrentIndex(i)
                
                # Подключаем сигналы загрузки
                browser.loadStarted.connect(self.on_load_started)
                browser.loadProgress.connect(self.on_load_progress)
                browser.loadFinished.connect(lambda success, i=i, browser=browser: 
                    self.on_load_finished(success, i, browser))
                browser.urlChanged.connect(lambda qurl, browser=browser: 
                    self.update_urlbar(qurl, browser))
                
        except Exception as e:
            print(f"Ошибка добавления новой вкладки: {e}")
            traceback.print_exc()
    
    def handle_fullscreen_request(self, request):
        """Обрабатывает запрос на полноэкранный режим"""
        request.accept()
        if request.toggleOn():
            self.showFullScreen()
        else:
            self.showNormal()
    
    def on_load_started(self):
        """Начало загрузки страницы"""
        self.loading_spinner.start()
    
    def on_load_progress(self, progress):
        """Прогресс загрузки страницы"""
        if progress == 100:
            self.loading_spinner.stop()
    
    def on_load_finished(self, success, tab_index, browser):
        """Завершение загрузки страницы"""
        self.loading_spinner.stop()
        try:
            if success and browser.page().title():
                title = browser.page().title()[:20] + "..." if len(browser.page().title()) > 20 else browser.page().title()
                emoji = "🌐"
                if any(word in title.lower() for word in ['video', 'видео', 'youtube']):
                    emoji = "🎥"
                elif any(word in title.lower() for word in ['music', 'музыка', 'spotify']):
                    emoji = "🎵"
                elif any(word in title.lower() for word in ['social', 'соц', 'facebook', 'vk']):
                    emoji = "👥"
                elif any(word in title.lower() for word in ['mail', 'почта', 'email']):
                    emoji = "✉️"
                elif any(word in title.lower() for word in ['search', 'поиск', 'google']):
                    emoji = "🔍"
                
                self.tabs.setTabText(tab_index, f"{emoji} {title}")
        except Exception as e:
            print(f"Ошибка в завершении загрузки: {e}")
    
    def resizeEvent(self, event):
        self.particle_widget.resize(self.size())
        super().resizeEvent(event)
    
    def showEvent(self, event):
        self.particle_widget.resize(self.size())
        self.particle_widget.lower()
        super().showEvent(event)
    
    def current_browser(self):
        if self.tabs.count() > 0:
            widget = self.tabs.currentWidget()
            if isinstance(widget, QWebEngineView):
                return widget
        return None
    
    def current_tab_changed(self, index):
        try:
            if index >= 0:
                browser = self.current_browser()
                if browser:
                    current_url = browser.url()
                    self.url_bar.setText(current_url.toString())
                else:
                    self.url_bar.clear()
        except Exception as e:
            print(f"Ошибка в изменении вкладки: {e}")
    
    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()
    
    def close_current_tab(self, i):
        if self.tabs.count() > 1:
            # Останавливаем медиа перед закрытием вкладки
            browser = self.tabs.widget(i)
            if isinstance(browser, QWebEngineView):
                browser.page().runJavaScript("""
                    var videos = document.querySelectorAll('video');
                    var audios = document.querySelectorAll('audio');
                    videos.forEach(v => { v.pause(); v.currentTime = 0; });
                    audios.forEach(a => { a.pause(); a.currentTime = 0; });
                    
                    // Выходим из полноэкранного режима
                    if (document.fullscreenElement) {
                        document.exitFullscreen();
                    }
                """)
            self.tabs.removeTab(i)
    
    def update_urlbar(self, q, browser=None):
        try:
            current_browser = self.current_browser()
            if browser and browser == current_browser:
                self.url_bar.setText(q.toString())
                self.add_to_history(q.toString())
        except Exception as e:
            print(f"Ошибка обновления адресной строки: {e}")
    
    def navigate_to_url(self):
        try:
            url = self.url_bar.text().strip()
            if not url:
                return
            
            self.handle_search_query(url)
                
        except Exception as e:
            print(f"Ошибка навигации по URL: {e}")
            self.show_modern_message("Ошибка", f"Неверный URL или запрос: {e}", "error")
    
    def is_url(self, text):
        if re.match(r'^https?://', text):
            return True
        if '.' in text and ' ' not in text and not text.startswith('?'):
            return True
        if re.match(r'^localhost(?::\d+)?', text):
            return True
        if re.match(r'^\d+\.\d+\.\d+\.\d+(?::\d+)?', text):
            return True
        return False
    
    def navigate_back(self):
        browser = self.current_browser()
        if browser:
            browser.back()
    
    def navigate_forward(self):
        browser = self.current_browser()
        if browser:
            browser.forward()
    
    def navigate_reload(self):
        browser = self.current_browser()
        if browser:
            browser.reload()
    
    def navigate_home(self):
        for i in range(self.tabs.count()):
            if self.tabs.tabText(i) == '🏠 Главная':
                self.tabs.setCurrentIndex(i)
                return
        self.add_new_tab(home_page=True)
    
    def show_modern_message(self, title, message, msg_type="info"):
        msg = QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setWindowIcon(self.create_modern_icon())
        
        if msg_type == "error":
            msg.setIcon(QMessageBox.Critical)
        else:
            msg.setIcon(QMessageBox.Information)
            
        msg.setStyleSheet("""
            QMessageBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f0c29, stop:1 #24243e);
                color: #ffffff;
                font-family: "Segoe UI", sans-serif;
            }
            QMessageBox QLabel {
                color: #ffffff;
                font-size: 14px;
            }
            QMessageBox QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b9d, stop:1 #9d65ff);
                color: #ffffff;
                border: none;
                border-radius: 15px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff4785, stop:1 #8a4dff);
            }
        """)
        
        msg.exec_()
    
    def add_bookmark(self):
        try:
            browser = self.current_browser()
            if not browser:
                self.show_modern_message("Информация", "Невозможно добавить домашнюю страницу в закладки", "info")
                return
                
            current_url = browser.url().toString()
            title = browser.page().title()
            
            if not current_url:
                return
                
            if not any(bmk['url'] == current_url for bmk in self.bookmarks):
                self.bookmarks.append({'title': title, 'url': current_url})
                self.save_data('bookmarks.json', self.bookmarks)
                self.show_modern_message("Успех", "🌌 Страница добавлена в закладки!", "info")
            else:
                self.show_modern_message("Информация", "⚠️ Эта страница уже в закладках!", "info")
                
        except Exception as e:
            print(f"Ошибка добавления закладки: {e}")
            self.show_modern_message("Ошибка", "Не удалось добавить закладку", "error")
    
    def show_bookmarks(self):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("🌌 Quantum Закладки")
            dialog.resize(600, 400)
            dialog.setWindowIcon(self.create_modern_icon())
            
            layout = QVBoxLayout()
            
            title = QLabel("Ваши квантовые закладки")
            title.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 20px;
                    font-weight: bold;
                    padding: 15px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                                stop:0 #ff6b9d, stop:0.5 #9d65ff, stop:1 #6bd5ff);
                    border-radius: 8px;
                    text-align: center;
                }
            """)
            layout.addWidget(title)
            
            list_widget = QListWidget()
            list_widget.setStyleSheet("""
                QListWidget {
                    background: rgba(13, 13, 26, 0.8);
                    border: 2px solid rgba(255, 107, 157, 0.3);
                    border-radius: 10px;
                    color: #ffffff;
                    font-size: 12px;
                    margin: 10px;
                }
                QListWidget::item {
                    padding: 10px;
                    border-bottom: 1px solid rgba(255, 107, 157, 0.2);
                    background: transparent;
                }
                QListWidget::item:selected {
                    background: rgba(255, 107, 157, 0.3);
                    color: #ffffff;
                    border-radius: 6px;
                }
                QListWidget::item:hover {
                    background: rgba(157, 101, 255, 0.2);
                    border-radius: 6px;
                }
            """)
            
            for bookmark in self.bookmarks:
                item_text = f"🌐 {bookmark['title']}\n🔗 {bookmark['url']}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, bookmark['url'])
                list_widget.addItem(item)
            
            layout.addWidget(list_widget)
            
            button_layout = QHBoxLayout()
            
            open_btn = QPushButton("🚀 Перейти")
            open_btn.setStyleSheet(self.get_button_style("primary"))
            open_btn.clicked.connect(lambda: self.open_bookmark(list_widget, dialog))
            button_layout.addWidget(open_btn)
            
            delete_btn = QPushButton("🗑️ Удалить")
            delete_btn.setStyleSheet(self.get_button_style("danger"))
            delete_btn.clicked.connect(lambda: self.delete_bookmark(list_widget))
            button_layout.addWidget(delete_btn)
            
            close_btn = QPushButton("🔒 Закрыть")
            close_btn.setStyleSheet(self.get_button_style("secondary"))
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            
            dialog.setWindowOpacity(0)
            dialog.show()
            
            animation = QPropertyAnimation(dialog, b"windowOpacity")
            animation.setDuration(300)
            animation.setStartValue(0)
            animation.setEndValue(1)
            animation.setEasingCurve(QEasingCurve.OutCubic)
            animation.start()
            
            dialog.exec_()
            
        except Exception as e:
            print(f"Ошибка показа закладок: {e}")
    
    def get_button_style(self, btn_type):
        styles = {
            "primary": """
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b9d, stop:1 #9d65ff);
                    color: #ffffff;
                    border: none;
                    border-radius: 12px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff4785, stop:1 #8a4dff);
                }
            """,
            "secondary": """
                QPushButton {
                    background: rgba(107, 214, 255, 0.3);
                    color: #ffffff;
                    border: 1px solid rgba(107, 214, 255, 0.5);
                    border-radius: 12px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background: rgba(107, 214, 255, 0.6);
                }
            """,
            "danger": """
                QPushButton {
                    background: rgba(255, 77, 77, 0.3);
                    color: #ffffff;
                    border: 1px solid rgba(255, 77, 77, 0.5);
                    border-radius: 12px;
                    padding: 8px 15px;
                    font-weight: bold;
                    font-size: 13px;
                    min-height: 30px;
                }
                QPushButton:hover {
                    background: rgba(255, 77, 77, 0.6);
                }
            """
        }
        return styles.get(btn_type, styles["primary"])
    
    def open_bookmark(self, list_widget, dialog):
        try:
            current_item = list_widget.currentItem()
            if current_item:
                url = current_item.data(Qt.UserRole)
                self.open_url_in_new_tab(url)
                dialog.close()
        except Exception as e:
            print(f"Ошибка открытия закладки: {e}")
    
    def delete_bookmark(self, list_widget):
        try:
            current_row = list_widget.currentRow()
            if current_row >= 0 and current_row < len(self.bookmarks):
                del self.bookmarks[current_row]
                self.save_data('bookmarks.json', self.bookmarks)
                list_widget.takeItem(current_row)
        except Exception as e:
            print(f"Ошибка удаления закладки: {e}")
    
    def add_to_history(self, url):
        try:
            if url and url not in self.history:
                self.history.append(url)
                if len(self.history) > 100:
                    self.history = self.history[-100:]
                self.save_data('history.json', self.history)
        except Exception as e:
            print(f"Ошибка добавления в историю: {e}")
    
    def create_desktop_shortcut(self):
        try:
            browser = self.current_browser()
            if not browser:
                self.show_modern_message("Информация", "Невозможно создать ярлык для домашней страницы", "info")
                return
                
            current_url = browser.url().toString()
            title = browser.page().title()
            
            if not current_url or not title:
                self.show_modern_message("Ошибка", "Не удалось получить информацию о странице", "error")
                return
            
            clean_title = re.sub(r'[<>:"/\\|?*]', '', title)
            if not clean_title:
                clean_title = "quantum_page"
            
            import platform
            if platform.system() == "Windows":
                desktop_path = os.path.expanduser("~/Desktop")
                shortcut_path = os.path.join(desktop_path, f"{clean_title}.url")
                
                with open(shortcut_path, 'w', encoding='utf-8') as shortcut:
                    shortcut.write('[InternetShortcut]\n')
                    shortcut.write(f'URL={current_url}\n')
                    shortcut.write('IconIndex=0\n')
                
                self.show_modern_message("Успех", f"⚡ Ярлык создан!\n📁 Расположение: Рабочий стол\n📄 Имя: {clean_title}.url", "info")
            else:
                self.show_modern_message("Информация", "Функция создания ярлыков для вашей ОС будет реализована позже", "info")
                
        except Exception as e:
            print(f"Ошибка создания ярлыка: {e}")
            self.show_modern_message("Ошибка", f"Не удалось создать ярлык: {e}", "error")
    
    def load_data(self, filename):
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
        return []
    
    def save_data(self, filename, data):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения {filename}: {e}")

def excepthook(exc_type, exc_value, exc_tb):
    tb = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    print(f"Критическая ошибка:\n{tb}")
    
    error_msg = QMessageBox()
    error_msg.setWindowTitle("🌌 Quantum Browser - Ошибка")
    error_msg.setIcon(QMessageBox.Critical)
    error_msg.setText(f"⚡ Произошла квантовая ошибка:\n{exc_value}")
    error_msg.setDetailedText(tb)
    error_msg.setStyleSheet("""
        QMessageBox {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0f0c29, stop:1 #24243e);
            color: #ffffff;
            font-family: "Segoe UI", sans-serif;
        }
        QMessageBox QLabel {
            color: #ffffff;
        }
        QMessageBox QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ff6b9d, stop:1 #9d65ff);
            color: #ffffff;
            border: none;
            border-radius: 15px;
            padding: 8px 20px;
            font-weight: bold;
        }
    """)
    error_msg.exec_()

if __name__ == '__main__':
    sys.excepthook = excepthook
    
    try:
        # Включаем аппаратное ускорение
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        app = QApplication(sys.argv)
        app.setApplicationName("Quantum Browser")
        app.setApplicationVersion("5.0")
        app.setApplicationDisplayName("Quantum Browser")
        
        app.setStyle('Fusion')
        
        browser = ModernBrowser()
        browser.show()
        
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Не удалось запустить приложение: {e}")
        traceback.print_exc()