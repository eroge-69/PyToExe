import sys
import os
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QProgressBar, QTextBrowser, QFrame, 
                             QComboBox, QMessageBox)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon

class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Получаем абсолютный путь к директории лаунчера
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Версии и их пути (относительно директории лаунчера)
        self.versions = {
            "beta 0.0.1": os.path.join("LATSIDE_VERSION", "LATSIDE_beta0.0.1", "app.py"),
            "beta 1.0.1": os.path.join("LATSIDE_VERSION", "LATSIDE_beta1.0.1", "app.py"),
            "beta 1.0.2": os.path.join("LATSIDE_VERSION", "LATSIDE_beta1.0.2", "app.py"),
        }
        
        self.current_version = "beta 1.0.1"
        self.setWindowTitle("LATSIDE")
        self.setFixedSize(800, 600)
        
        # Установка иконки приложения
        self.set_application_icon()
        
        self.setup_styles()
        self.init_ui()
        
    def set_application_icon(self):
        """Устанавливает иконку приложения из файла icon.png"""
        icon_path = os.path.join(self.base_dir, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Предупреждение: Файл иконки не найден по пути {icon_path}")
    
    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
            }
            QLabel {
                color: #ecf0f1;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px;
                font-size: 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #7f8c8d;
            }
            QProgressBar {
                border: 2px solid #34495e;
                border-radius: 5px;
                text-align: center;
                background-color: #34495e;
            }
            QProgressBar::chunk {
                background-color: #2ecc71;
                width: 10px;
            }
            QTextBrowser {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
            }
            QComboBox {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 5px;
                font-size: 14px;
                border-radius: 5px;
            }
            QComboBox QAbstractItemView {
                background-color: #3498db;
                color: white;
                selection-background-color: #2980b9;
            }
        """)
        
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Заголовок
        header = QLabel("LATSIDE")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Arial", 24, QFont.Bold))
        main_layout.addWidget(header)
        
        
        # Нижняя часть
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(20)
        
        # Новости
        news_frame = self.create_news_frame()
        bottom_layout.addWidget(news_frame, stretch=2)
        
        # Управление
        control_frame = self.create_control_frame()
        bottom_layout.addWidget(control_frame, stretch=1)
        
        main_layout.addLayout(bottom_layout)
        
        # Таймер для имитации загрузки
        self.load_timer = QTimer()
        self.load_timer.timeout.connect(self.update_progress)
        
        # Проверяем доступность версий при старте
        self.check_versions_availability()
        
    def set_logo_image(self):
        """Устанавливает изображение логотипа из файла"""
        logo_path = os.path.join(self.base_dir, "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Масштабируем изображение, чтобы оно помещалось в интерфейс
            self.logo.setPixmap(pixmap.scaled(400, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            print(f"Предупреждение: Файл логотипа не найден по пути {logo_path}")
            self.logo.setText("Логотип LATSIDE")
        
    def create_news_frame(self):
        news_frame = QFrame()
        news_frame.setFrameShape(QFrame.StyledPanel)
        news_layout = QVBoxLayout(news_frame)
        
        news_label = QLabel("Последние новости:")
        news_label.setFont(QFont("Arial", 14, QFont.Bold))
        news_layout.addWidget(news_label)
        
        self.news_browser = QTextBrowser()
        self.news_browser.setOpenExternalLinks(True)
        news_layout.addWidget(self.news_browser)
        
        self.news_browser.setHtml("""
            <h3>Версия beta 1.0.1 </h3>
            <p>переделана система взаимодействий с игрой.</p>
            <hr>
            <h3>добавлено</h3>
            <p>Анимация добычи и build омвещение</p>
            <hr>
            <h3>Исправления</h3>
            <p>Исправлены баги с дюпом блоков.</p>
        """)
        
        return news_frame
        
    def create_control_frame(self):
        control_frame = QFrame()
        control_frame.setFrameShape(QFrame.StyledPanel)
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(20)
        
        # Выбор версии
        version_combo_label = QLabel("Выберите версию:")
        version_combo_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(version_combo_label)
        
        self.version_combo = QComboBox()
        self.version_combo.addItems(self.versions.keys())
        self.version_combo.setCurrentText(self.current_version)
        self.version_combo.currentTextChanged.connect(self.change_version)
        control_layout.addWidget(self.version_combo)
        
        # Информация о версии
        self.version_label = QLabel(f"Версия игры: {self.current_version}")
        self.version_label.setAlignment(Qt.AlignCenter)
        self.version_label.setFont(QFont("Arial", 12))
        control_layout.addWidget(self.version_label)
        
        # Статус доступности
        self.availability_label = QLabel()
        self.availability_label.setAlignment(Qt.AlignCenter)
        control_layout.addWidget(self.availability_label)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        control_layout.addWidget(self.progress_bar)
        
        # Кнопки
        self.update_button = QPushButton("Проверить обновления")
        self.update_button.clicked.connect(self.check_for_updates)
        control_layout.addWidget(self.update_button)
        
        self.play_button = QPushButton("Играть")
        self.play_button.clicked.connect(self.launch_game)
        control_layout.addWidget(self.play_button)
        
        control_layout.addStretch()
        
        return control_frame
        
    def check_versions_availability(self):
        """Проверяет доступность всех версий и обновляет интерфейс"""
        for version, rel_path in self.versions.items():
            abs_path = os.path.join(self.base_dir, rel_path)
            if not os.path.exists(abs_path):
                print(f"Предупреждение: Версия {version} не найдена по пути {abs_path}")
        
        # Проверяем текущую выбранную версию
        self.update_version_availability(self.current_version)
        
    def update_version_availability(self, version):
        """Обновляет статус доступности выбранной версии"""
        rel_path = self.versions.get(version)
        if rel_path:
            abs_path = os.path.join(self.base_dir, rel_path)
            if os.path.exists(abs_path):
                self.availability_label.setText("Версия доступна")
                self.availability_label.setStyleSheet("color: #2ecc71;")
                self.play_button.setEnabled(True)
            else:
                self.availability_label.setText("Версия не найдена!")
                self.availability_label.setStyleSheet("color: #e74c3c;")
                self.play_button.setEnabled(False)
        
    def change_version(self, version):
        """Изменение выбранной версии"""
        self.current_version = version
        self.version_label.setText(f"Версия игры: {self.current_version}")
        self.update_version_availability(version)
        
    def check_for_updates(self):
        """Проверка обновлений"""
        self.update_button.setEnabled(False)
        self.play_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.load_timer.start(50)
        
    def update_progress(self):
        """Обновление прогресс бара"""
        value = self.progress_bar.value() + 2
        self.progress_bar.setValue(value)
        
        if value >= 100:
            self.load_timer.stop()
            self.update_button.setEnabled(True)
            self.play_button.setEnabled(os.path.exists(self.get_current_version_path()))
            
    def get_current_version_path(self):
        """Возвращает абсолютный путь к текущей версии"""
        rel_path = self.versions.get(self.current_version)
        if rel_path:
            return os.path.join(self.base_dir, rel_path)
        return None
        
    def launch_game(self):
        """Запуск игры"""
        game_path = self.get_current_version_path()
        
        if not game_path or not os.path.exists(game_path):
            QMessageBox.critical(self, "Ошибка", 
                               f"Файл игры не найден по пути:\n{game_path}")
            return
            
        self.play_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.load_timer.start(30)
        
        QTimer.singleShot(3000, self.execute_game)
        
    def execute_game(self):
        """Запуск выбранной версии игры"""
        self.load_timer.stop()
        self.progress_bar.setValue(100)
        self.play_button.setEnabled(True)
        
        game_path = self.get_current_version_path()
        
        try:
            # Запускаем игру в отдельном процессе
            subprocess.Popen([sys.executable, game_path], 
                            cwd=os.path.dirname(game_path))
            print(f"Успешно запущена версия {self.current_version}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка запуска", 
                               f"Не удалось запустить игру:\n{str(e)}")
            print(f"Ошибка при запуске игры: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = GameLauncher()
    launcher.show()
    sys.exit(app.exec_())