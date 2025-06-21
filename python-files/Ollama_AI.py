import sys
import json
import requests
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLineEdit, QPushButton, QLabel, QScrollArea, QFrame, QDialog, QComboBox,
    QFileDialog, QSizePolicy, QSpacerItem, QListView
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QObject
from PyQt6.QtGui import QPalette, QColor, QTextCursor, QAction, QKeySequence, QGuiApplication, QFont

class InputField(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.first_line = True

    def keyPressEvent(self, event):
        # Обработка Enter и Ctrl+Enter
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            modifiers = event.modifiers()
            if modifiers == Qt.KeyboardModifier.ControlModifier:
                # Вставка новой строки при Ctrl+Enter
                self.insertPlainText("\n")
                self.first_line = False
            else:
                cursor = self.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.StartOfLine)
                line_text = cursor.block().text().strip()
                
                if self.first_line and not line_text:
                    # Если первая строка пустая - отправляем
                    if self.parent:
                        self.parent.send_message()
                elif not line_text:
                    # Если не первая строка и пустая - отправляем
                    if self.parent:
                        self.parent.send_message()
                else:
                    # Если строка не пустая - новая строка
                    self.insertPlainText("\n")
                    self.first_line = False
        else:
            # Обработка других клавиш
            super().keyPressEvent(event)
            # Сбрасываем флаг первой строки если что-то вводим
            if self.toPlainText().strip():
                self.first_line = False

    def clear(self):
        super().clear()
        self.first_line = True

class OllamaWorker(QThread):
    responseReceived = pyqtSignal(str, bool)
    errorOccurred = pyqtSignal(str)

    def __init__(self, prompt, model, system_prompt, history, file_content=None):
        super().__init__()
        self.prompt = prompt
        self.model = model
        self.system_prompt = system_prompt
        self.history = history
        self.file_content = file_content
        self._is_running = True

    def run(self):
        try:
            full_prompt = self.prompt
            if self.file_content:
                full_prompt = f"Файл: {self.file_content}\n\n{self.prompt}"

            # Формируем полный контекст с историей
            context = "\n".join(self.history[-4:])  # Берем последние 4 сообщения
            if context:
                full_prompt = f"{context}\n\n{full_prompt}"

            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": True,
                "system": self.system_prompt
            }

            # Установим таймауты для запроса
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                stream=True,
                timeout=10  # Таймаут для соединения и чтения
            )

            response.raise_for_status()
            
            full_response = ""
            for line in response.iter_lines():
                if not self._is_running:
                    break
                if line:
                    decoded_line = line.decode('utf-8')
                    data = json.loads(decoded_line)
                    token = data.get("response", "")
                    full_response += token
                    self.responseReceived.emit(token, False)
            
            if self._is_running:
                self.responseReceived.emit("", True)
                return full_response

        except Exception as e:
            self.errorOccurred.emit(str(e))
            return None
    
    def stop(self):
        self._is_running = False
        # Завершаем поток немедленно
        if self.isRunning():
            self.terminate()
            self.wait()

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройки")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Модель
        layout.addWidget(QLabel("Модель:"))
        self.model_combo = QComboBox()
        
        # Настраиваем выпадающий список для открытия вниз
        list_view = QListView()
        list_view.setStyleSheet("""
            QListView {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
            }
            QListView::item {
                padding: 5px;
            }
            QListView::item:selected {
                background-color: #094771;
            }
        """)
        self.model_combo.setView(list_view)
        self.model_combo.setStyleSheet("""
            QComboBox {
                combobox-popup: 0;
            }
        """)
        
        layout.addWidget(self.model_combo)
        
        # Системный промт
        layout.addWidget(QLabel("Системный промт:"))
        self.system_prompt = QTextEdit()
        self.system_prompt.setFixedHeight(100)
        layout.addWidget(self.system_prompt)
        
        # Таймаут
        layout.addWidget(QLabel("Таймаут (секунды):"))
        self.timeout = QLineEdit()
        layout.addWidget(self.timeout)
        
        # Каталог моделей
        layout.addWidget(QLabel("Каталог моделей:"))
        self.model_path = QLineEdit()
        layout.addWidget(self.model_path)
        self.browse_btn = QPushButton("Обзор...")
        self.browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_btn)
        
        # Кнопки
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.apply_dark_theme()
    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите каталог моделей")
        if folder:
            self.model_path.setText(folder)
    
    def apply_dark_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #dcdcdc;
            }
            QLabel {
                color: #dcdcdc;
            }
            QComboBox, QTextEdit, QLineEdit, QPushButton {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2d2d30;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                color: #dcdcdc;
                selection-background-color: #094771;
                border: 1px solid #3c3c3c;
            }
        """)

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ollama Chat")
        self.setMinimumSize(800, 600)
        
        # Центрирование окна
        screen = QGuiApplication.primaryScreen().geometry()
        self.move(screen.center() - self.rect().center())
        
        # Настройки
        self.model = "llama3"
        self.system_prompt = "You are a helpful AI assistant."
        self.timeout = 120
        self.model_path = os.path.expanduser("~/.ollama/models")
        self.attached_file = None
        self.history = []  # Для хранения истории сообщений
        
        # Состояние приложения
        self.generating = False
        self.worker = None
        self.is_active = True  # Флаг активности окна
        
        self.init_ui()
        self.apply_dark_theme()
        self.check_ollama()
        
    def init_ui(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Область чата - растягивается на всё доступное пространство
        self.chat_area = QTextEdit()
        self.chat_area.setReadOnly(True)
        self.chat_area.setFrameStyle(QFrame.Shape.NoFrame)
        self.chat_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.chat_area)
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        main_layout.addWidget(scroll_area, 1)  # Фактор растяжения 1
        
        # Плавающая панель управления
        floating_panel = QWidget()
        floating_panel.setMaximumWidth(800)
        floating_layout = QVBoxLayout()
        floating_layout.setContentsMargins(0, 0, 0, 0)
        
        # Область информации
        self.info_label = QLabel("Готов к работе")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setFixedHeight(20)
        floating_layout.addWidget(self.info_label)
        
        # Поле ввода
        self.input_field = InputField(self)
        self.input_field.setPlaceholderText("Введите сообщение...")
        self.input_field.setFixedHeight(80)
        self.input_field.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        floating_layout.addWidget(self.input_field)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        self.attach_btn = QPushButton("Прикрепить")
        self.attach_btn.setFixedSize(100, 30)
        self.attach_btn.clicked.connect(self.attach_file)
        
        self.clear_input_btn = QPushButton("Очистить")
        self.clear_input_btn.setFixedSize(100, 30)
        self.clear_input_btn.clicked.connect(self.clear_input)
        
        self.clear_history_btn = QPushButton("Очистить историю")
        self.clear_history_btn.setFixedSize(120, 30)
        self.clear_history_btn.clicked.connect(self.clear_history)
        
        self.settings_btn = QPushButton("Настройки")
        self.settings_btn.setFixedSize(100, 30)
        self.settings_btn.clicked.connect(self.open_settings)
        
        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.setFixedSize(100, 30)
        self.stop_btn.clicked.connect(self.stop_generation)
        self.stop_btn.setEnabled(False)
        
        self.send_btn = QPushButton("Отправить")
        self.send_btn.setFixedSize(100, 30)
        self.send_btn.clicked.connect(self.send_message)
        
        buttons_layout.addWidget(self.attach_btn)
        buttons_layout.addWidget(self.clear_input_btn)
        buttons_layout.addWidget(self.clear_history_btn)
        buttons_layout.addWidget(self.settings_btn)
        buttons_layout.addStretch(1)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.send_btn)
        
        floating_layout.addLayout(buttons_layout)
        floating_panel.setLayout(floating_layout)
        
        # Центрируем плавающую панель
        center_layout = QHBoxLayout()
        center_layout.addStretch(1)
        center_layout.addWidget(floating_panel, 2)
        center_layout.addStretch(1)
        
        main_layout.addLayout(center_layout, 0)  # Фактор растяжения 0
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Контекстное меню
        self.setup_context_menu()
        
    def setup_context_menu(self):
        # Ввод
        self.input_field.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        paste_action = QAction("Вставить", self.input_field)
        paste_action.triggered.connect(self.input_field.paste)
        paste_action.setShortcut(QKeySequence("Ctrl+V"))
        self.input_field.addAction(paste_action)
        
        copy_action = QAction("Копировать", self.input_field)
        copy_action.triggered.connect(self.input_field.copy)
        copy_action.setShortcut(QKeySequence("Ctrl+C"))
        self.input_field.addAction(copy_action)
        
        # Чат
        self.chat_area.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        chat_copy_action = QAction("Копировать", self.chat_area)
        chat_copy_action.triggered.connect(self.copy_chat)
        chat_copy_action.setShortcut(QKeySequence("Ctrl+C"))
        self.chat_area.addAction(chat_copy_action)
    
    def copy_chat(self):
        if self.chat_area.textCursor().hasSelection():
            self.chat_area.copy()
    
    def apply_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 30, 30))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
        dark_palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(142, 45, 197).darker())
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        self.setPalette(dark_palette)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
            QTextEdit {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3c3c3c;
                border-radius: 10px;
                padding: 10px;
                font-size: 12pt;
            }
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                background: #252526;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #3c3c3c;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QPushButton {
                background-color: #2d2d30;
                color: #dcdcdc;
                border: 1px solid #3c3c3c;
                border-radius: 5px;
                padding: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
            QPushButton:disabled {
                background-color: #252526;
                color: #6d6d6d;
            }
            QLabel {
                color: #dcdcdc;
                font-size: 10pt;
            }
            QComboBox {
                background-color: #252526;
                color: #dcdcdc;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 5px;
            }
            #floatingPanel {
                background-color: rgba(30, 30, 30, 200);
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        # Специфичные стили
        self.info_label.setStyleSheet("""
            QLabel {
                background-color: transparent;
                color: #aaaaaa;
                font-size: 10pt;
            }
        """)
        
        self.chat_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                font-size: 11pt;
                border: none;
            }
        """)
    
    def check_ollama(self):
        try:
            response = requests.get("http://localhost:11434", timeout=3)
            if response.status_code == 200:
                self.update_info("Ollama работает")
            else:
                self.update_info("Ollama не отвечает")
        except:
            self.update_info("Ollama не запущена")
    
    def update_info(self, message):
        if not self.is_active:
            return
            
        # Сбрасываем прикрепленный файл при любом обновлении информации
        if not message.startswith("Прикреплен файл:"):
            self.attached_file = None
            
        self.info_label.setText(message)
        QTimer.singleShot(5000, self.reset_info_label)
    
    def reset_info_label(self):
        if self.is_active and not self.generating:
            self.info_label.setText("Готов к работе")
    
    def attach_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выберите файл")
        if file_path:
            self.attached_file = file_path
            self.update_info(f"Прикреплен файл: {os.path.basename(file_path)}")
    
    def clear_input(self):
        self.input_field.clear()
        self.attached_file = None
        self.update_info("Ввод очищен")
    
    def clear_history(self):
        self.chat_area.clear()
        self.history = []
        self.update_info("История очищена")
    
    def open_settings(self):
        dialog = SettingsDialog(self)
        dialog.model_combo.addItems(self.get_available_models())
        dialog.model_combo.setCurrentText(self.model)
        dialog.system_prompt.setText(self.system_prompt)
        dialog.timeout.setText(str(self.timeout))
        dialog.model_path.setText(self.model_path)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.model = dialog.model_combo.currentText()
            self.system_prompt = dialog.system_prompt.toPlainText()
            self.timeout = int(dialog.timeout.text())
            self.model_path = dialog.model_path.text()
            self.update_info("Настройки сохранены")
    
    def get_available_models(self):
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            models = [model['name'] for model in response.json()['models']]
            return models
        except:
            return ["llama3", "mistral", "phi3"]
    
    def send_message(self):
        if self.generating:
            return
            
        prompt = self.input_field.toPlainText().strip()
        file_attached = self.attached_file is not None
        
        # Если нет текста и нет файла - не отправляем
        if not prompt and not file_attached:
            return
            
        # Чтение файла если прикреплен
        file_content = None
        if self.attached_file:
            try:
                with open(self.attached_file, 'r', encoding='utf-8') as f:
                    file_content = f.read(5000)  # Ограничение на размер
            except Exception as e:
                self.update_info(f"Ошибка чтения файла: {str(e)}")
                file_content = None
        
        # Формируем сообщение пользователя с учетом файла
        user_message = "Я: "
        if prompt:
            user_message += prompt
        if file_attached:
            if prompt:
                user_message += " "
            user_message += f"(прикреплен файл: {os.path.basename(self.attached_file)})"
        
        # Добавление сообщения пользователя в чат и историю
        self.chat_area.append(user_message)
        self.history.append(user_message)
        
        self.input_field.clear()
        self.attached_file = None
        
        # Блокировка интерфейса
        self.generating = True
        self.stop_btn.setEnabled(True)
        self.send_btn.setEnabled(False)
        self.update_info("Генерация ответа...")
        
        # Запуск потока с передачей истории
        self.worker = OllamaWorker(prompt, self.model, self.system_prompt, self.history, file_content)
        self.worker.responseReceived.connect(self.handle_response)
        self.worker.errorOccurred.connect(self.handle_error)
        self.worker.finished.connect(self.generation_finished)
        self.worker.start()
    
    def handle_response(self, token, finished):
        if not self.is_active:
            return
            
        try:
            if token:
                cursor = self.chat_area.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                
                # Если это первый токен, добавляем заголовок модели в одну строку
                if not hasattr(self, 'last_response_position'):
                    self.chat_area.insertPlainText(f"\n{self.model}: ")
                    cursor = self.chat_area.textCursor()
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    self.last_response_position = cursor.position()
                
                cursor.setPosition(self.last_response_position)
                cursor.insertText(token)
                self.last_response_position = cursor.position()
                
                # Прокрутка вниз
                self.chat_area.ensureCursorVisible()
            
            if finished:
                if hasattr(self, 'last_response_position'):
                    delattr(self, 'last_response_position')
                self.chat_area.append("\n")
                # Добавляем ответ в историю
                if token:  # Добавляем только если был получен ответ
                    self.history.append(f"{self.model}: {token}")
        except Exception as e:
            print(f"Ошибка в handle_response: {e}")
    
    def handle_error(self, error):
        if not self.is_active:
            return
            
        try:
            self.update_info(f"Ошибка: {error}")
            self.chat_area.append(f"Система: {error}\n")
            self.generation_finished()
        except Exception as e:
            print(f"Ошибка в handle_error: {e}")
    
    def generation_finished(self):
        if not self.is_active:
            return
            
        try:
            self.generating = False
            self.stop_btn.setEnabled(False)
            self.send_btn.setEnabled(True)
            self.update_info("Готов к работе")
            
            # Безопасное завершение потока
            if self.worker:
                try:
                    self.worker.responseReceived.disconnect()
                    self.worker.errorOccurred.disconnect()
                    self.worker.finished.disconnect()
                except Exception:
                    pass
                self.worker = None
        except Exception as e:
            print(f"Ошибка в generation_finished: {e}")
    
    def stop_generation(self):
        if self.worker:
            self.worker.stop()
        self.generation_finished()
        self.update_info("Генерация остановлена")
        
    def closeEvent(self, event):
        # Устанавливаем флаг закрытия
        self.is_active = False
        
        # Останавливаем генерацию при закрытии окна
        if self.worker:
            try:
                # Останавливаем поток немедленно
                self.worker.stop()
                
                # Обрабатываем все оставшиеся события
                QApplication.processEvents()
                
                # Отключаем сигналы
                try:
                    self.worker.responseReceived.disconnect()
                    self.worker.errorOccurred.disconnect()
                    self.worker.finished.disconnect()
                except Exception:
                    pass
                
                # Удаляем ссылку на worker
                self.worker = None
            except Exception as e:
                print(f"Ошибка остановки воркера: {e}")
                
        # Принимаем событие закрытия
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ChatWindow()
    window.show()
    
    # Обработка необработанных исключений
    def exception_handler(exc_type, exc_value, exc_traceback):
        print(f"Необработанное исключение: {exc_value}")
        # Здесь можно добавить запись в лог или другие действия
    sys.excepthook = exception_handler
    
    sys.exit(app.exec())
