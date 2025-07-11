import sys
import os
import ctypes
import subprocess
import winreg
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
                             QHBoxLayout, QListWidget, QMessageBox, QComboBox, QMenu,
                             QAction, QListWidgetItem, QLineEdit, QTextEdit, QFileDialog)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QCursor
from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from PyQt5.QtWinExtras import QWinTaskbarButton

class MUnlockerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MUnlocker Pro by Mastak")
        self.setFixedSize(800, 600)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Стили
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(30, 30, 30, 220);
                color: white;
                border-radius: 15px;
            }
            QPushButton {
                background-color: rgba(80, 0, 0, 150);
                color: white;
                border: none;
                padding: 8px;
                border-radius: 8px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: rgba(120, 0, 0, 180);
            }
            QListWidget {
                background-color: rgba(40, 40, 40, 180);
                border-radius: 10px;
                border: 1px solid #444;
            }
            QLineEdit, QTextEdit {
                background-color: rgba(50, 50, 50, 200);
                border: 1px solid #555;
                border-radius: 8px;
                padding: 5px;
            }
            QMenu {
                background-color: rgba(50, 50, 50, 220);
                color: white;
                border: 1px solid #666;
                border-radius: 5px;
            }
            QMenu::item:selected {
                background-color: rgba(80, 0, 0, 180);
            }
        """)
        
        self.init_ui()
        self.old_pos = None

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Заголовок с кнопкой закрытия
        title_bar = QHBoxLayout()
        title_bar.setSpacing(10)
        
        self.title = QLabel("MUnlocker Pro by Mastak")
        self.title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_bar.addWidget(self.title)
        
        title_bar.addStretch()
        
        self.btn_close = QPushButton("✕")
        self.btn_close.setFixedSize(30, 30)
        self.btn_close.clicked.connect(self.close)
        title_bar.addWidget(self.btn_close)
        
        main_layout.addLayout(title_bar)

        # Основные кнопки
        btn_layout = QHBoxLayout()
        self.btn_registry = QPushButton("Реестр")
        self.btn_startup = QPushButton("Автозагрузка")
        self.btn_processes = QPushButton("Процессы")
        self.btn_services = QPushButton("Службы")
        self.btn_files = QPushButton("Файлы")
        
        btn_layout.addWidget(self.btn_registry)
        btn_layout.addWidget(self.btn_startup)
        btn_layout.addWidget(self.btn_processes)
        btn_layout.addWidget(self.btn_services)
        btn_layout.addWidget(self.btn_files)
        
        main_layout.addLayout(btn_layout)

        # Основной контент
        self.content_area = QListWidget()
        self.content_area.setContextMenuPolicy(Qt.CustomContextMenu)
        self.content_area.customContextMenuRequested.connect(self.show_context_menu)
        self.content_area.itemDoubleClicked.connect(self.item_double_clicked)
        main_layout.addWidget(self.content_area)

        # Статус бар
        self.status_bar = QLabel("Готово")
        self.status_bar.setFont(QFont("Segoe UI", 8))
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)

        # Подключение кнопок
        self.btn_registry.clicked.connect(self.load_registry)
        self.btn_startup.clicked.connect(self.load_startup)
        self.btn_processes.clicked.connect(self.load_processes)
        self.btn_services.clicked.connect(self.load_services)
        self.btn_files.clicked.connect(self.load_files)

    # ===== Функции для работы с интерфейсом =====
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def show_context_menu(self, pos):
        item = self.content_area.itemAt(pos)
        if not item:
            return
            
        menu = QMenu()
        
        # Общие действия
        delete_action = QAction("Удалить", self)
        delete_action.triggered.connect(lambda: self.delete_item(item))
        menu.addAction(delete_action)
        
        # Дополнительные действия в зависимости от контекста
        if hasattr(item, 'file_path'):
            open_action = QAction("Открыть в проводнике", self)
            open_action.triggered.connect(lambda: os.startfile(os.path.dirname(item.file_path)))
            menu.addAction(open_action)
            
            edit_action = QAction("Редактировать", self)
            edit_action.triggered.connect(lambda: self.edit_file(item.file_path))
            menu.addAction(edit_action)
            
        elif hasattr(item, 'service_name'):
            start_action = QAction("Запустить службу", self)
            start_action.triggered.connect(lambda: self.control_service(item.service_name, "start"))
            menu.addAction(start_action)
            
            stop_action = QAction("Остановить службу", self)
            stop_action.triggered.connect(lambda: self.control_service(item.service_name, "stop"))
            menu.addAction(stop_action)
            
        elif hasattr(item, 'process_id'):
            kill_action = QAction("Завершить процесс", self)
            kill_action.triggered.connect(lambda: self.kill_process(item.process_id))
            menu.addAction(kill_action)
            
        menu.exec_(self.content_area.mapToGlobal(pos))

    def item_double_clicked(self, item):
        if hasattr(item, 'file_path'):
            self.edit_file(item.file_path)
        elif hasattr(item, 'registry_key'):
            self.edit_registry(item.registry_key)

    # ===== Основные функции =====
    def load_registry(self):
        self.content_area.clear()
        self.status_bar.setText("Загрузка данных реестра...")
        QApplication.processEvents()
        
        try:
            # Автозагрузка HKCU
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               r"Software\Microsoft\Windows\CurrentVersion\Run")
            self.add_registry_items(key, "HKCU Автозагрузка")
            
            # Автозагрузка HKLM
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"Software\Microsoft\Windows\CurrentVersion\Run")
            self.add_registry_items(key, "HKLM Автозагрузка")
            
            self.status_bar.setText("Реестр загружен")
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def add_registry_items(self, key, prefix):
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                item = QListWidgetItem(f"{prefix}: {name} -> {value}")
                item.registry_key = (key, name)
                self.content_area.addItem(item)
                i += 1
            except OSError:
                break

    def load_startup(self):
        self.content_area.clear()
        self.status_bar.setText("Загрузка автозагрузки...")
        QApplication.processEvents()
        
        try:
            # Пользовательская автозагрузка
            path = os.path.expandvars("%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            if os.path.exists(path):
                for f in os.listdir(path):
                    full_path = os.path.join(path, f)
                    item = QListWidgetItem(f"Автозагрузка: {f}")
                    item.file_path = full_path
                    self.content_area.addItem(item)
            
            # Общая автозагрузка
            path = os.path.expandvars("%ProgramData%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup")
            if os.path.exists(path):
                for f in os.listdir(path):
                    full_path = os.path.join(path, f)
                    item = QListWidgetItem(f"Общая автозагрузка: {f}")
                    item.file_path = full_path
                    self.content_area.addItem(item)
                    
            self.status_bar.setText("Автозагрузка загружена")
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def load_processes(self):
        self.content_area.clear()
        self.status_bar.setText("Загрузка процессов...")
        QApplication.processEvents()
        
        try:
            result = subprocess.check_output("tasklist /fo csv /nh", shell=True).decode('cp866')
            for line in result.splitlines():
                if line.strip():
                    parts = line.split('","')
                    if len(parts) >= 5:
                        name = parts[0][1:]
                        pid = parts[1]
                        mem = parts[4][:-1]
                        item = QListWidgetItem(f"{name} (PID: {pid}, Память: {mem})")
                        item.process_id = pid
                        self.content_area.addItem(item)
                        
            self.status_bar.setText("Процессы загружены")
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def load_services(self):
        self.content_area.clear()
        self.status_bar.setText("Загрузка служб...")
        QApplication.processEvents()
        
        try:
            result = subprocess.check_output("sc query type= service state= all", shell=True).decode('cp866')
            service_name = None
            for line in result.splitlines():
                if "SERVICE_NAME:" in line:
                    service_name = line.split(":")[1].strip()
                elif "DISPLAY_NAME:" in line and service_name:
                    display_name = line.split(":")[1].strip()
                    item = QListWidgetItem(f"{display_name} ({service_name})")
                    item.service_name = service_name
                    self.content_area.addItem(item)
                    service_name = None
                    
            self.status_bar.setText("Службы загружены")
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def load_files(self):
        path = QFileDialog.getExistingDirectory(self, "Выберите папку", os.path.expanduser("~"))
        if not path:
            return
            
        self.content_area.clear()
        self.status_bar.setText(f"Загрузка файлов из {path}...")
        QApplication.processEvents()
        
        try:
            for root, dirs, files in os.walk(path):
                for name in files:
                    full_path = os.path.join(root, name)
                    item = QListWidgetItem(f"{name} ({full_path})")
                    item.file_path = full_path
                    self.content_area.addItem(item)
                    
                break  # Только первый уровень
                
            self.status_bar.setText(f"Загружено {self.content_area.count()} файлов")
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    # ===== Действия =====
    def delete_item(self, item):
        if hasattr(item, 'file_path'):
            self.delete_file(item.file_path)
        elif hasattr(item, 'registry_key'):
            self.delete_registry(item.registry_key)
        elif hasattr(item, 'process_id'):
            self.kill_process(item.process_id)
        elif hasattr(item, 'service_name'):
            self.delete_service(item.service_name)

    def delete_file(self, path):
        try:
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            self.status_bar.setText(f"Удалено: {path}")
            self.content_area.takeItem(self.content_area.row(self.content_area.currentItem()))
        except Exception as e:
            self.status_bar.setText(f"Ошибка удаления: {str(e)}")

    def delete_registry(self, key_data):
        key, name = key_data
        try:
            winreg.DeleteValue(key, name)
            self.status_bar.setText(f"Удалено из реестра: {name}")
            self.content_area.takeItem(self.content_area.row(self.content_area.currentItem()))
        except Exception as e:
            self.status_bar.setText(f"Ошибка удаления: {str(e)}")

    def kill_process(self, pid):
        try:
            subprocess.call(f"taskkill /f /pid {pid}", shell=True)
            self.status_bar.setText(f"Процесс {pid} завершен")
            self.content_area.takeItem(self.content_area.row(self.content_area.currentItem()))
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def control_service(self, name, action):
        try:
            subprocess.call(f"net {action} {name}", shell=True)
            self.status_bar.setText(f"Служба {name}: {action}")
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def delete_service(self, name):
        try:
            subprocess.call(f"sc delete {name}", shell=True)
            self.status_bar.setText(f"Служба {name} удалена")
            self.content_area.takeItem(self.content_area.row(self.content_area.currentItem()))
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def edit_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            editor = QTextEdit()
            editor.setWindowTitle(f"Редактирование: {path}")
            editor.setPlainText(content)
            editor.setMinimumSize(600, 400)
            
            save_btn = QPushButton("Сохранить")
            save_btn.clicked.connect(lambda: self.save_file(path, editor.toPlainText()))
            
            layout = QVBoxLayout()
            layout.addWidget(editor)
            layout.addWidget(save_btn)
            
            window = QWidget()
            window.setLayout(layout)
            window.setWindowFlags(Qt.Window)
            window.show()
            
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def save_file(self, path, content):
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            self.status_bar.setText(f"Файл {path} сохранен")
        except Exception as e:
            self.status_bar.setText(f"Ошибка сохранения: {str(e)}")

    def edit_registry(self, key_data):
        key, name = key_data
        try:
            value, _ = winreg.QueryValueEx(key, name)
            
            editor = QLineEdit()
            editor.setWindowTitle(f"Редактирование реестра: {name}")
            editor.setText(str(value))
            editor.setMinimumWidth(400)
            
            save_btn = QPushButton("Сохранить")
            save_btn.clicked.connect(lambda: self.save_registry(key, name, editor.text()))
            
            layout = QVBoxLayout()
            layout.addWidget(editor)
            layout.addWidget(save_btn)
            
            window = QWidget()
            window.setLayout(layout)
            window.setWindowFlags(Qt.Window)
            window.show()
            
        except Exception as e:
            self.status_bar.setText(f"Ошибка: {str(e)}")

    def save_registry(self, key, name, value):
        try:
            _, reg_type = winreg.QueryValueEx(key, name)
            winreg.SetValueEx(key, name, 0, reg_type, value)
            self.status_bar.setText(f"Реестр {name} обновлен")
        except Exception as e:
            self.status_bar.setText(f"Ошибка сохранения: {str(e)}")

if __name__ == "__main__":
    # Проверка прав администратора
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 9))
    
    window = MUnlockerApp()
    window.show()
    sys.exit(app.exec_())