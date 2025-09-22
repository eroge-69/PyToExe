import sys
import threading
import time
import webbrowser
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QPushButton, QTextEdit, QLabel,
                               QMessageBox, QFrame, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from PySide6.QtGui import QFont, QTextCursor, QPalette, QColor
from main import app  # Ваш Flask app


class FlaskServerThread(QThread):
    """Поток для запуска Flask сервера"""
    log_signal = Signal(str)
    status_signal = Signal(bool)

    def __init__(self):
        super().__init__()
        self.is_running = True

    def run(self):
        """Запуск Flask сервера"""
        try:
            self.log_signal.emit("Запуск Flask сервера...")
            app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        except Exception as e:
            self.log_signal.emit(f"Ошибка сервера: {str(e)}")
        finally:
            self.is_running = False
            self.status_signal.emit(False)

    def stop(self):
        """Остановка сервера"""
        if self.is_running:
            # Здесь можно добавить корректную остановку Flask
            self.is_running = False
            self.terminate()
            self.wait()


class ModernFlaskController(QMainWindow):
    def __init__(self):
        super().__init__()
        self.server_thread = None
        self.is_running = False
        self.setup_ui()
        self.setup_styles()

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowTitle("Flask Application Controller - Modern")
        self.setGeometry(100, 100, 1000, 700)
        self.setMinimumSize(900, 600)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        # Заголовок
        title_label = QLabel("Flask Application Controller")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                border-radius: 8px;
                color: white;
            }
        """)
        layout.addWidget(title_label)

        # Панель статуса
        self.setup_status_panel(layout)

        # Панель управления
        self.setup_control_panel(layout)

        # Журнал событий
        self.setup_log_panel(layout)

        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

    def setup_status_panel(self, layout):
        """Панель статуса"""
        status_frame = QFrame()
        status_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(status_frame)

        # Статус сервера
        status_label = QLabel("Статус сервера:")
        status_label.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.status_indicator = QLabel("●")
        self.status_indicator.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #e74c3c;
            }
        """)

        self.status_text = QLabel("Выключено")
        self.status_text.setStyleSheet("font-size: 14px; color: #e74c3c; font-weight: bold;")

        status_layout.addWidget(status_label)
        status_layout.addWidget(self.status_indicator)
        status_layout.addWidget(self.status_text)
        status_layout.addStretch()

        # Информация о подключении
        info_label = QLabel("http://127.0.0.1:5000")
        info_label.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                color: white;
                padding: 5px 10px;
                border-radius: 4px;
                font-family: monospace;
            }
        """)
        status_layout.addWidget(info_label)

        layout.addWidget(status_frame)

    def setup_control_panel(self, layout):
        """Панель управления"""
        control_frame = QFrame()
        control_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        control_layout = QHBoxLayout(control_frame)

        # Кнопки управления
        self.start_btn = self.create_button("▶ Запуск", "#27ae60", self.start_server)
        self.stop_btn = self.create_button("⏹ Остановка", "#e74c3c", self.stop_server, False)
        self.restart_btn = self.create_button("↻ Перезагрузка", "#f39c12", self.restart_server, False)
        self.browser_btn = self.create_button("🌐 Открыть в браузере", "#3498db", self.open_browser)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.restart_btn)
        control_layout.addWidget(self.browser_btn)
        control_layout.addStretch()

        # Кнопка очистки логов
        self.clear_btn = self.create_button("🗑️ Очистить журнал", "#95a5a6", self.clear_logs)
        control_layout.addWidget(self.clear_btn)

        layout.addWidget(control_frame)

    def setup_log_panel(self, layout):
        """Панель журнала событий"""
        log_frame = QFrame()
        log_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border: 2px solid #34495e;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        log_layout = QVBoxLayout(log_frame)

        log_label = QLabel("Журнал событий:")
        log_label.setStyleSheet("color: #ecf0f1; font-weight: bold; font-size: 14px;")
        log_layout.addWidget(log_label)

        # Текстовое поле для логов
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a1a;
                color: #00ff00;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        log_layout.addWidget(self.log_text)

        layout.addWidget(log_frame)

    def create_button(self, text, color, callback, enabled=True):
        """Создает стилизованную кнопку"""
        button = QPushButton(text)
        button.setEnabled(enabled)
        button.clicked.connect(callback)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 15px;
                font-weight: bold;
                border-radius: 5px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
                color: #7f8c8d;
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 40)};
            }}
        """)
        return button

    def darken_color(self, color, percent=20):
        """Затемняет цвет на указанный процент"""
        color = QColor(color)
        return color.darker(100 + percent).name()

    def setup_styles(self):
        """Настройка глобальных стилей"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ecf0f1;
            }
        """)

    def log(self, message):
        """Добавляет сообщение в журнал"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"

        # Добавляем сообщение в журнал
        self.log_text.append(log_entry)

        # Автопрокрутка к новому сообщению
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)

        # Обновляем интерфейс
        QApplication.processEvents()

    def start_server(self):
        """Запуск сервера"""
        if not self.is_running:
            self.show_progress(True)
            self.log("Инициализация запуска сервера...")

            # Запуск в отдельном потоке
            self.server_thread = FlaskServerThread()
            self.server_thread.log_signal.connect(self.log)
            self.server_thread.status_signal.connect(self.server_status_changed)
            self.server_thread.start()

            # Таймер для проверки статуса
            QTimer.singleShot(1000, self.check_server_status)

    def stop_server(self):
        """Остановка сервера"""
        if self.is_running and self.server_thread:
            self.log("Остановка сервера...")
            self.show_progress(True)
            self.server_thread.stop()
            self.is_running = False
            self.update_ui_state()

    def restart_server(self):
        """Перезагрузка сервера"""
        self.log("Инициализация перезагрузки...")
        self.stop_server()
        QTimer.singleShot(2000, self.delayed_restart)

    def delayed_restart(self):
        """Задержанный перезапуск"""
        self.start_server()

    def open_browser(self):
        """Открытие в браузере"""
        if self.is_running:
            try:
                webbrowser.open('http://127.0.0.1:5000')
                self.log("Браузер открыт: http://127.0.0.1:5000")
            except Exception as e:
                self.log(f"Ошибка открытия браузера: {str(e)}")
        else:
            self.show_warning("Сервер не запущен", "Запустите сервер перед открытием в браузере")
            self.log("Попытка открыть браузер при остановленном сервере")

    def server_status_changed(self, status):
        """Обработчик изменения статуса сервера"""
        self.is_running = status
        self.show_progress(False)
        self.update_ui_state()

        if status:
            self.log("Сервер успешно запущен на http://127.0.0.1:5000")
            # Авто-открытие браузера через 1 секунду
            QTimer.singleShot(1000, self.auto_open_browser)
        else:
            self.log("Сервер остановлен")

    def check_server_status(self):
        """Проверка статуса сервера"""
        if self.server_thread and self.server_thread.isRunning():
            self.is_running = True
            self.update_ui_state()
            self.show_progress(False)

    def update_ui_state(self):
        """Обновление состояния интерфейса"""
        if self.is_running:
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.restart_btn.setEnabled(True)
            self.status_indicator.setStyleSheet("color: #2ecc71; font-size: 20px; font-weight: bold;")
            self.status_text.setText("Запущен")
            self.status_text.setStyleSheet("color: #2ecc71; font-weight: bold; font-size: 14px;")
        else:
            self.start_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            self.status_indicator.setStyleSheet("color: #e74c3c; font-size: 20px; font-weight: bold;")
            self.status_text.setText("Остановлен")
            self.status_text.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")

    def show_progress(self, show):
        """Показывает/скрывает прогресс-бар"""
        self.progress_bar.setVisible(show)
        if show:
            self.progress_bar.setRange(0, 0)  # Бесконечный прогресс

    def auto_open_browser(self):
        """Автоматическое открытие браузера после запуска"""
        if self.is_running:
            self.open_browser()

    def clear_logs(self):
        """Очистка журнала"""
        self.log_text.clear()
        self.log("Журнал очищен")

    def show_warning(self, title, message):
        """Показывает предупреждение"""
        QMessageBox.warning(self, title, message)

    def closeEvent(self, event):
        """Обработчик закрытия окна"""
        if self.is_running:
            reply = QMessageBox.question(
                self,
                "Подтверждение закрытия",
                "Сервер все еще работает. Вы уверены, что хотите выйти?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                if self.server_thread:
                    self.server_thread.stop()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    app = QApplication(sys.argv)

    # Установка стиля приложения
    app.setStyle('Fusion')

    window = ModernFlaskController()
    window.show()

    # Начальное сообщение в журнал
    window.log("Система управления Flask запущена")
    window.log("Для начала работы нажмите 'Запуск'")

    sys.exit(app.exec())


if __name__ == '__main__':
    main()