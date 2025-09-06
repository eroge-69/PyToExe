import os
import sys
import time
import shutil
import threading
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional

import psutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QProgressBar,
                            QListWidget, QSystemTrayIcon, QMenu, QStyle,
                            QMessageBox, QFileDialog, QSpinBox, QComboBox)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt6.QtGui import QIcon, QAction, QFont, QPalette, QColor

class FileSyncWorker(QThread):
    """Поток для выполнения синхронизации"""
    progress_signal = pyqtSignal(int, str)
    finished_signal = pyqtSignal(bool, str)
    stats_signal = pyqtSignal(dict)

    def __init__(self, source_path: str, target_path: str, sync_mode: str):
        super().__init__()
        self.source_path = source_path
        self.target_path = target_path
        self.sync_mode = sync_mode
        self._is_running = True

    def stop(self):
        """Остановка потока"""
        self._is_running = False

    def calculate_file_hash(self, file_path: str) -> str:
        """Вычисление хэша файла для сравнения"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    if not self._is_running:
                        return ""
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return ""

    def sync_files(self):
        """Основная логика синхронизации"""
        try:
            source = Path(self.source_path)
            target = Path(self.target_path)

            if not source.exists():
                self.finished_signal.emit(False, "Исходная папка не существует")
                return

            if not target.exists():
                target.mkdir(parents=True, exist_ok=True)

            # Собираем информацию о файлах
            source_files = {}
            target_files = {}

            # Рекурсивный обход исходной папки
            total_files = sum(1 for _ in source.rglob('*') if _.is_file())
            processed = 0

            for file_path in source.rglob('*'):
                if not self._is_running:
                    return

                if file_path.is_file():
                    rel_path = file_path.relative_to(source)
                    source_files[rel_path] = {
                        'size': file_path.stat().st_size,
                        'mtime': file_path.stat().st_mtime,
                        'hash': self.calculate_file_hash(str(file_path))
                    }

                    processed += 1
                    progress = int((processed / total_files) * 50)
                    self.progress_signal.emit(progress, f"Анализ файлов: {processed}/{total_files}")

            # Анализ целевой папки
            for file_path in target.rglob('*'):
                if not self._is_running:
                    return

                if file_path.is_file():
                    rel_path = file_path.relative_to(target)
                    target_files[rel_path] = {
                        'size': file_path.stat().st_size,
                        'mtime': file_path.stat().st_mtime
                    }

            # Определение операций
            operations = {
                'copy': [],
                'update': [],
                'delete': []
            }

            # Файлы для копирования/обновления
            for rel_path, source_info in source_files.items():
                target_file = target / rel_path
                
                if rel_path not in target_files:
                    operations['copy'].append(rel_path)
                else:
                    target_info = target_files[rel_path]
                    if (source_info['size'] != target_info['size'] or 
                        source_info['mtime'] > target_info['mtime'] + 1):
                        operations['update'].append(rel_path)

            # Файлы для удаления (в режиме зеркалирования)
            if self.sync_mode == 'mirror':
                for rel_path in target_files:
                    if rel_path not in source_files:
                        operations['delete'].append(rel_path)

            # Выполнение операций
            total_ops = len(operations['copy']) + len(operations['update']) + len(operations['delete'])
            if total_ops == 0:
                self.finished_signal.emit(True, "Синхронизация не требуется")
                return

            completed_ops = 0

            # Копирование новых файлов
            for rel_path in operations['copy']:
                if not self._is_running:
                    return

                source_file = source / rel_path
                target_file = target / rel_path
                
                # Создание директорий
                target_file.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_file, target_file)
                completed_ops += 1
                progress = 50 + int((completed_ops / total_ops) * 25)
                self.progress_signal.emit(progress, f"Копирование: {rel_path}")

            # Обновление измененных файлов
            for rel_path in operations['update']:
                if not self._is_running:
                    return

                source_file = source / rel_path
                target_file = target / rel_path
                
                shutil.copy2(source_file, target_file)
                completed_ops += 1
                progress = 75 + int((completed_ops / total_ops) * 25)
                self.progress_signal.emit(progress, f"Обновление: {rel_path}")

            # Удаление лишних файлов
            for rel_path in operations['delete']:
                if not self._is_running:
                    return

                target_file = target / rel_path
                target_file.unlink()
                
                # Удаление пустых директорий
                for parent in target_file.parents:
                    if parent == target:
                        break
                    try:
                        if not any(parent.iterdir()):
                            parent.rmdir()
                    except:
                        pass

                completed_ops += 1
                progress = 75 + int((completed_ops / total_ops) * 25)
                self.progress_signal.emit(progress, f"Удаление: {rel_path}")

            stats = {
                'copied': len(operations['copy']),
                'updated': len(operations['update']),
                'deleted': len(operations['delete']),
                'total': total_ops
            }

            self.stats_signal.emit(stats)
            self.finished_signal.emit(True, "Синхронизация завершена успешно")

        except Exception as e:
            self.finished_signal.emit(False, f"Ошибка: {str(e)}")

    def run(self):
        """Запуск потока"""
        self.sync_files()

class SyncManager:
    """Менеджер синхронизации"""
    
    def __init__(self):
        self.worker: Optional[FileSyncWorker] = None
        self.sync_history = []
        self.settings = {
            'interval': 300,  # 5 минут по умолчанию
            'sync_mode': 'mirror',  # mirror или update
            'last_source': '',
            'last_target': ''
        }

    def start_sync(self, source: str, target: str, sync_mode: str) -> FileSyncWorker:
        """Запуск синхронизации"""
        self.worker = FileSyncWorker(source, target, sync_mode)
        return self.worker

    def save_settings(self):
        """Сохранение настроек"""
        # В реальном приложении здесь бы было сохранение в файл/реестр
        pass

    def load_settings(self):
        """Загрузка настроек"""
        # В реальном приложении здесь бы была загрузка из файла/реестра
        pass

class ModernSyncApp(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self):
        super().__init__()
        self.sync_manager = SyncManager()
        self.tray_icon = None
        self.sync_timer = QTimer()
        self.init_ui()
        self.setup_tray()
        self.setup_timer()

    def init_ui(self):
        """Инициализация интерфейса"""
        self.setWindowTitle("FileSync Pro")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(700, 500)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Заголовок
        title_label = QLabel("FileSync Pro - Профессиональная синхронизация файлов")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3498db, stop:1 #2c3e50);
                border-radius: 5px;
                color: white;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Панель путей
        paths_layout = QHBoxLayout()
        
        # Исходная папка
        source_layout = QVBoxLayout()
        source_layout.addWidget(QLabel("Исходная папка:"))
        self.source_label = QLabel("Не выбрана")
        self.source_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        source_layout.addWidget(self.source_label)
        
        self.source_btn = QPushButton("Выбрать...")
        self.source_btn.clicked.connect(self.select_source)
        source_layout.addWidget(self.source_btn)
        paths_layout.addLayout(source_layout)

        # Целевая папка
        target_layout = QVBoxLayout()
        target_layout.addWidget(QLabel("Целевая папка (USB):"))
        self.target_label = QLabel("Не выбрана")
        self.target_label.setStyleSheet("""
            QLabel {
                background: #f8f9fa;
                border: 1px solid #ddd;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        target_layout.addWidget(self.target_label)
        
        self.target_btn = QPushButton("Выбрать...")
        self.target_btn.clicked.connect(self.select_target)
        target_layout.addWidget(self.target_btn)
        paths_layout.addLayout(target_layout)

        layout.addLayout(paths_layout)

        # Настройки синхронизации
        settings_layout = QHBoxLayout()
        
        # Интервал
        interval_layout = QVBoxLayout()
        interval_layout.addWidget(QLabel("Интервал синхронизации (секунды):"))
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(60, 3600)
        self.interval_spin.setValue(300)
        self.interval_spin.valueChanged.connect(self.update_timer_interval)
        interval_layout.addWidget(self.interval_spin)
        settings_layout.addLayout(interval_layout)

        # Режим синхронизации
        mode_layout = QVBoxLayout()
        mode_layout.addWidget(QLabel("Режим синхронизации:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Зеркалирование", "Обновление"])
        mode_layout.addWidget(self.mode_combo)
        settings_layout.addLayout(mode_layout)

        layout.addLayout(settings_layout)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel("Готов к работе")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.sync_btn = QPushButton("Синхронизировать сейчас")
        self.sync_btn.clicked.connect(self.start_manual_sync)
        self.sync_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2ecc71;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        buttons_layout.addWidget(self.sync_btn)

        self.stop_btn = QPushButton("Остановить")
        self.stop_btn.clicked.connect(self.stop_sync)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
            QPushButton:disabled {
                background: #95a5a6;
            }
        """)
        buttons_layout.addWidget(self.stop_btn)

        layout.addLayout(buttons_layout)

        # Лог операций
        log_label = QLabel("История операций:")
        layout.addWidget(log_label)
        
        self.log_list = QListWidget()
        self.log_list.setStyleSheet("""
            QListWidget {
                background: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.log_list)

        # Статус бар
        self.statusBar().showMessage("Готов")
        self.memory_label = QLabel()
        self.statusBar().addPermanentWidget(self.memory_label)
        self.update_memory_usage()

        # Таймер для обновления использования памяти
        memory_timer = QTimer()
        memory_timer.timeout.connect(self.update_memory_usage)
        memory_timer.start(1000)

    def setup_tray(self):
        """Настройка системного трея"""
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            self.tray_icon.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon))
            
            tray_menu = QMenu()
            
            show_action = QAction("Показать", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            sync_action = QAction("Синхронизировать", self)
            sync_action.triggered.connect(self.start_manual_sync)
            tray_menu.addAction(sync_action)
            
            exit_action = QAction("Выход", self)
            exit_action.triggered.connect(self.cleanup_exit)
            tray_menu.addAction(exit_action)
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.show()
            self.tray_icon.activated.connect(self.tray_icon_activated)

    def setup_timer(self):
        """Настройка таймера автоматической синхронизации"""
        self.sync_timer.timeout.connect(self.start_auto_sync)
        self.sync_timer.start(300000)  # 5 минут по умолчанию

    def update_timer_interval(self):
        """Обновление интервала таймера"""
        interval = self.interval_spin.value() * 1000  # преобразуем в миллисекунды
        self.sync_timer.setInterval(interval)

    def select_source(self):
        """Выбор исходной папки"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите исходную папку")
        if folder:
            self.source_label.setText(folder)

    def select_target(self):
        """Выбор целевой папки"""
        folder = QFileDialog.getExistingDirectory(self, "Выберите целевую папку")
        if folder:
            self.target_label.setText(folder)

    def start_manual_sync(self):
        """Запуск ручной синхронизации"""
        self.start_sync()

    def start_auto_sync(self):
        """Запуск автоматической синхронизации"""
        if (self.source_label.text() != "Не выбрана" and 
            self.target_label.text() != "Не выбрана"):
            self.add_log("Автоматическая синхронизация запущена")
            self.start_sync()

    def start_sync(self):
        """Запуск процесса синхронизации"""
        source = self.source_label.text()
        target = self.target_label.text()
        sync_mode = "mirror" if self.mode_combo.currentIndex() == 0 else "update"

        if source == "Не выбрана" or target == "Не выбрана":
            QMessageBox.warning(self, "Ошибка", "Выберите исходную и целевую папки")
            return

        if not os.path.exists(source):
            QMessageBox.warning(self, "Ошибка", "Исходная папка не существует")
            return

        # Блокировка интерфейса во время синхронизации
        self.sync_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Синхронизация...")

        # Запуск worker'а
        self.worker = self.sync_manager.start_sync(source, target, sync_mode)
        self.worker.progress_signal.connect(self.update_progress)
        self.worker.finished_signal.connect(self.sync_finished)
        self.worker.stats_signal.connect(self.update_stats)
        self.worker.start()

    def stop_sync(self):
        """Остановка синхронизации"""
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
            self.worker.wait()
            self.status_label.setText("Синхронизация остановлена")
            self.add_log("Синхронизация остановлена пользователем")

    def update_progress(self, value: int, message: str):
        """Обновление прогресса"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)

    def sync_finished(self, success: bool, message: str):
        """Завершение синхронизации"""
        self.sync_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("Синхронизация завершена")
            self.add_log(f"✓ {message}")
        else:
            self.status_label.setText("Ошибка синхронизации")
            self.add_log(f"✗ {message}")
            QMessageBox.warning(self, "Ошибка", message)

    def update_stats(self, stats: dict):
        """Обновление статистики"""
        stats_text = (f"Скопировано: {stats['copied']}, "
                     f"Обновлено: {stats['updated']}, "
                     f"Удалено: {stats['deleted']}")
        self.add_log(f"Статистика: {stats_text}")

    def add_log(self, message: str):
        """Добавление записи в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_list.addItem(f"[{timestamp}] {message}")
        self.log_list.scrollToBottom()

    def update_memory_usage(self):
        """Обновление информации об использовании памяти"""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        self.memory_label.setText(f"Память: {memory_mb:.1f} MB")

        # Предупреждение если память превышает 45MB
        if memory_mb > 45:
            self.memory_label.setStyleSheet("color: red;")
        else:
            self.memory_label.setStyleSheet("")

    def tray_icon_activated(self, reason):
        """Обработка кликов по иконке в трее"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
            self.activateWindow()

    def cleanup_exit(self):
        """Корректный выход из приложения"""
        if hasattr(self, 'worker') and self.worker:
            self.worker.stop()
            self.worker.wait()
        
        if self.tray_icon:
            self.tray_icon.hide()
        
        QApplication.quit()

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        event.ignore()
        self.hide()
        if self.tray_icon:
            self.tray_icon.showMessage(
                "FileSync Pro",
                "Приложение продолжает работу в фоновом режиме",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )

def main():
    """Точка входа в приложение"""
    # Настройка для экономии памяти
    os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
    os.environ['QT_SCALE_FACTOR'] = '1'
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Установка стиля для экономии ресурсов
    app.setStyle('Fusion')
    
    window = ModernSyncApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()