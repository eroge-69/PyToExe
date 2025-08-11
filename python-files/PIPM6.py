import sys
import subprocess
import requests
import importlib.metadata
import os
import zipfile
import tempfile
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QPushButton, QLineEdit, 
    QTextEdit, QHBoxLayout, QMessageBox, QScrollArea, QListWidget, 
    QMenu, QAction, QMenuBar, QWidget, QFileDialog, QProgressBar,
    QLabel, QInputDialog, QSplitter
)
from PyQt5.QtCore import Qt, QUrl, QThread, pyqtSignal
from PyQt5.QtGui import QDesktopServices, QTextCursor, QIcon, QKeySequence
from PyQt5.QtWidgets import QShortcut

class PackageManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.library_window = None
        self.setWindowIcon(QIcon('icon.png'))  # Добавьте иконку в папку с программой
        self.setMinimumSize(800, 600)

    def initUI(self):
        self.setWindowTitle('Менеджер пакетов Python')
        
        # Главный контейнер
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Создаем сплиттер для разделения областей
        splitter = QSplitter(Qt.Vertical)
        main_layout.addWidget(splitter)
        
        # Верхняя панель: управление пакетами
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        splitter.addWidget(top_widget)
        
        # Панель поиска
        search_layout = QHBoxLayout()
        self.package_input = QLineEdit()
        self.package_input.setPlaceholderText("Введите название пакета...")
        self.package_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.package_input)
        
        self.search_button = QPushButton('Поиск')
        self.search_button.setShortcut("Return")
        search_layout.addWidget(self.search_button)
        top_layout.addLayout(search_layout)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        self.install_button = QPushButton('Установить')
        self.uninstall_button = QPushButton('Удалить')
        self.update_button = QPushButton('Обновить')
        self.show_libraries_button = QPushButton('Показать библиотеки')
        
        button_layout.addWidget(self.install_button)
        button_layout.addWidget(self.uninstall_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.show_libraries_button)
        top_layout.addLayout(button_layout)
        
        # Информация о пакете
        self.package_info = QTextEdit()
        self.package_info.setReadOnly(True)
        self.package_info.setMaximumHeight(150)
        top_layout.addWidget(self.package_info)
        
        # Нижняя панель: вывод и прогресс
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout(bottom_widget)
        splitter.addWidget(bottom_widget)
        
        # Прогресс-бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        bottom_layout.addWidget(self.progress_bar)
        
        # Текстовый вывод
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        bottom_layout.addWidget(self.output_text)
        
        # Статус бар
        self.statusBar().showMessage("Готово")
        
        # Настройка пропорций сплиттера
        splitter.setSizes([200, 400])
        
        # Подключение сигналов
        self.install_button.clicked.connect(self.install_package)
        self.uninstall_button.clicked.connect(self.uninstall_package)
        self.update_button.clicked.connect(self.update_package)
        self.search_button.clicked.connect(self.search_package)
        self.show_libraries_button.clicked.connect(self.show_libraries)
        
        # Контекстное меню
        self.setup_context_menu()
        
        # Верхнее меню
        self.setup_menu_bar()
        
        # Горячие клавиши
        self.setup_shortcuts()

    def setup_context_menu(self):
        self.context_menu = QMenu(self)
        
        self.action_copy = QAction('Копировать', self)
        self.action_copy.triggered.connect(self.copy_text)
        
        self.action_clear = QAction('Очистить', self)
        self.action_clear.triggered.connect(self.clear_output)
        
        self.action_save_log = QAction('Сохранить лог', self)
        self.action_save_log.triggered.connect(self.save_log)
        
        self.context_menu.addAction(self.action_copy)
        self.context_menu.addAction(self.action_clear)
        self.context_menu.addAction(self.action_save_log)
        
        self.output_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.output_text.customContextMenuRequested.connect(
            lambda pos: self.context_menu.exec_(self.output_text.mapToGlobal(pos))
        )

    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        
        save_action = QAction('Сохранить окружение', self)
        save_action.triggered.connect(self.save_environment)
        file_menu.addAction(save_action)
        
        restore_action = QAction('Восстановить окружение', self)
        restore_action.triggered.connect(self.restore_environment)
        file_menu.addAction(restore_action)
        
        export_action = QAction('Экспорт списка пакетов', self)
        export_action.triggered.connect(self.export_packages)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Сервис
        tools_menu = menubar.addMenu('Сервис')
        
        upgrade_pip_action = QAction('Обновить pip', self)
        upgrade_pip_action.triggered.connect(self.upgrade_pip)
        tools_menu.addAction(upgrade_pip_action)
        
        check_updates_action = QAction('Проверить обновления', self)
        check_updates_action.triggered.connect(self.check_updates)
        tools_menu.addAction(check_updates_action)
        
        # Меню Справка
        help_menu = menubar.addMenu('Справка')
        
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Ссылки
        menubar.addAction('Автор').triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl('https://vk.com/satunish')))
        
        # ИСПРАВЛЕННАЯ ССЫЛКА НА РЕПОЗИТОРИЙ
        menubar.addAction('Репозиторий').triggered.connect(
            lambda: QDesktopServices.openUrl(QUrl('https://vk.com/market-231227888')))

    def setup_shortcuts(self):
        QShortcut(QKeySequence.Copy, self.output_text, self.copy_text)
        QShortcut("Ctrl+L", self, self.clear_output)
        QShortcut("Ctrl+F", self, self.package_input.setFocus)

    def copy_text(self):
        if self.output_text.textCursor().hasSelection():
            self.output_text.copy()
        else:
            QApplication.clipboard().setText(self.output_text.toPlainText())

    def clear_output(self):
        self.output_text.clear()

    def save_log(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить лог", "", "Текстовые файлы (*.txt);;Все файлы (*)")
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.output_text.toPlainText())
                self.statusBar().showMessage(f"Лог сохранён в {file_path}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")

    def install_package(self):
        package = self.package_input.text().strip()
        if not package:
            QMessageBox.warning(self, "Ошибка", "Введите название пакета")
            return
            
        self.run_pip_command(['install', package], "Установка")

    def uninstall_package(self):
        package = self.package_input.text().strip()
        if not package:
            QMessageBox.warning(self, "Ошибка", "Введите название пакета")
            return
            
        reply = QMessageBox.question(
            self, 'Подтверждение', 
            f"Вы уверены, что хотите удалить пакет {package}?",
            QMessageBox.Yes | QMessageBox.No)
            
        if reply == QMessageBox.Yes:
            self.run_pip_command(['uninstall', '-y', package], "Удаление")

    def update_package(self):
        package = self.package_input.text().strip()
        if not package:
            QMessageBox.warning(self, "Ошибка", "Введите название пакета")
            return
            
        self.run_pip_command(['install', '--upgrade', package], "Обновление")

    def run_pip_command(self, command, action):
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Индикатор процесса
        
        self.output_text.append(f"{action} пакета...\n")
        self.statusBar().showMessage(f"{action} пакета...")
        
        # Запуск в отдельном потоке
        self.worker = PipThread(command)
        self.worker.finished.connect(self.on_pip_finished)
        self.worker.error.connect(self.on_pip_error)
        self.worker.start()

    def on_pip_finished(self, result):
        self.progress_bar.setVisible(False)
        self.output_text.append(result)
        self.output_text.append("\n" + "="*50 + "\n")
        self.statusBar().showMessage("Операция завершена", 5000)
        self.search_package()  # Обновить информацию

    def on_pip_error(self, error):
        self.progress_bar.setVisible(False)
        self.output_text.append(f"ОШИБКА: {error}")
        self.statusBar().showMessage("Ошибка выполнения", 5000)

    def search_package(self):
        package = self.package_input.text().strip()
        if not package:
            return
            
        self.package_info.clear()
        self.statusBar().showMessage(f"Поиск информации о {package}...")
        
        try:
            response = requests.get(
                f'https://pypi.org/pypi/{package}/json',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                info = data['info']
                
                text = f"""
                <b>Название:</b> {info['name']}<br>
                <b>Версия:</b> {info['version']}<br>
                <b>Лицензия:</b> {info.get('license', 'Не указана')}<br>
                <b>Автор:</b> {info.get('author', 'Не указан')}<br>
                <b>Описание:</b> {info['summary']}<br>
                <b>Домашняя страница:</b> <a href="{info['home_page']}">{info['home_page']}</a>
                """
                self.package_info.setHtml(text)
                self.statusBar().showMessage(f"Найдена информация о {package}", 5000)
            else:
                self.package_info.setText("Пакет не найден в репозитории PyPI")
        except Exception as e:
            self.package_info.setText(f"Ошибка при выполнении запроса: {str(e)}")

    def show_libraries(self):
        try:
            packages = [
                (dist.metadata['Name'], dist.version) 
                for dist in importlib.metadata.distributions()
            ]
            
            if not packages:
                QMessageBox.information(self, "Библиотеки", "Не найдено установленных пакетов")
                return
                
            # Создаем окно, если его нет
            if not hasattr(self, 'library_window') or not self.library_window:
                self.library_window = QMainWindow(self)
                self.library_window.setWindowTitle('Установленные библиотеки')
                self.library_window.resize(500, 600)
                
                central_widget = QWidget()
                layout = QVBoxLayout()
                central_widget.setLayout(layout)
                
                # Поиск в списке
                search_layout = QHBoxLayout()
                self.filter_input = QLineEdit()
                self.filter_input.setPlaceholderText("Фильтр...")
                search_layout.addWidget(self.filter_input)
                
                self.filter_button = QPushButton("Применить")
                self.filter_button.clicked.connect(self.filter_packages)
                search_layout.addWidget(self.filter_button)
                layout.addLayout(search_layout)
                
                # Список пакетов
                self.package_list = QListWidget()
                layout.addWidget(self.package_list)
                
                # Кнопки управления
                btn_layout = QHBoxLayout()
                self.update_selected_btn = QPushButton("Обновить выбранное")
                self.update_selected_btn.clicked.connect(self.update_selected)
                btn_layout.addWidget(self.update_selected_btn)
                
                self.uninstall_selected_btn = QPushButton("Удалить выбранное")
                self.uninstall_selected_btn.clicked.connect(self.uninstall_selected)
                btn_layout.addWidget(self.uninstall_selected_btn)
                layout.addLayout(btn_layout)
                
                self.library_window.setCentralWidget(central_widget)
            
            # Обновляем список
            self.package_list.clear()
            for name, version in sorted(packages, key=lambda x: x[0].lower()):
                self.package_list.addItem(f"{name}=={version}")
            
            self.library_window.show()
            self.library_window.activateWindow()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить список пакетов: {str(e)}")

    def filter_packages(self):
        filter_text = self.filter_input.text().strip().lower()
        if not filter_text:
            return
            
        for i in range(self.package_list.count()):
            item = self.package_list.item(i)
            item.setHidden(filter_text not in item.text().lower())

    def update_selected(self):
        selected = [item.text().split("==")[0] for item in self.package_list.selectedItems()]
        if not selected:
            return
            
        self.package_input.setText(" ".join(selected))
        self.update_package()

    def uninstall_selected(self):
        selected = [item.text().split("==")[0] for item in self.package_list.selectedItems()]
        if not selected:
            return
            
        self.package_input.setText(" ".join(selected))
        self.uninstall_package()

    def save_environment(self):
        """Сохранить текущее окружение в requirements.txt"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить окружение", "", "Требования (*.txt);;Все файлы (*)")
        
        if not file_path:
            return
            
        try:
            result = subprocess.run(
                ['pip', 'freeze'], 
                capture_output=True, 
                text=True, 
                check=True
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
                
            self.statusBar().showMessage(f"Окружение сохранено в {file_path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить окружение: {str(e)}")

    def restore_environment(self):
        """Восстановить окружение из requirements.txt"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл требований", "", "Требования (*.txt);;Все файлы (*)")
        
        if not file_path:
            return
            
        try:
            self.run_pip_command(['install', '-r', file_path], "Восстановление окружения")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка восстановления: {str(e)}")

    def export_packages(self):
        """Экспортировать список пакетов в JSON"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Экспорт пакетов", "", "JSON файлы (*.json);;Все файлы (*)")
        
        if not file_path:
            return
            
        try:
            packages = [
                {"name": dist.metadata['Name'], "version": dist.version}
                for dist in importlib.metadata.distributions()
            ]
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "packages": packages
                }, f, indent=2)
                
            self.statusBar().showMessage(f"Экспорт завершен: {file_path}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка экспорта: {str(e)}")

    def upgrade_pip(self):
        self.run_pip_command(['install', '--upgrade', 'pip'], "Обновление pip")

    def check_updates(self):
        try:
            self.output_text.append("Проверка обновлений...\n")
            result = subprocess.run(
                ['pip', 'list', '--outdated'], 
                capture_output=True, 
                text=True,
                check=True
            )
            self.output_text.append(result.stdout)
            
            if not result.stdout.strip():
                self.output_text.append("\nВсе пакеты обновлены!")
        except Exception as e:
            self.output_text.append(f"Ошибка: {str(e)}")

    def show_about(self):
        about_text = """
        <h2>Менеджер пакетов Python</h2>
        <p>Версия: 2.0</p>
        <p>Программа для управления Python-пакетами с графическим интерфейсом.</p>
        <p><b>Основные возможности:</b></p>
        <ul>
            <li>Установка, удаление и обновление пакетов</li>
            <li>Поиск информации о пакетах в PyPI</li>
            <li>Просмотр установленных библиотек</li>
            <li>Сохранение и восстановление окружения</li>
            <li>Экспорт списка пакетов</li>
        </ul>
        <p>© 2023 Разработчик: Ваше Имя</p>
        """
        QMessageBox.about(self, "О программе", about_text)


class PipThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, command):
        super().__init__()
        self.command = ['pip'] + command

    def run(self):
        try:
            result = subprocess.run(
                self.command,
                capture_output=True,
                text=True,
                check=True
            )
            output = result.stdout + "\n" + result.stderr
            self.finished.emit(output)
        except subprocess.CalledProcessError as e:
            self.error.emit(f"{e.stderr}\nКод ошибки: {e.returncode}")
        except Exception as e:
            self.error.emit(str(e))


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Современный стиль интерфейса
    
    # Проверка наличия pip
    try:
        subprocess.run(['pip', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        QMessageBox.critical(
            None, 
            "Критическая ошибка", 
            "Pip не найден! Убедитесь, что Python установлен правильно."
        )
        return 1
    
    window = PackageManager()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())