import os
import sys
import json
import time
import threading
import psutil
import subprocess
import gc
from datetime import datetime

# ===== FIX QT PLUGIN ERROR =====
import os

if hasattr(sys, '_MEIPASS'):
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt5', 'plugins')
else:
    try:
        import PyQt5

        pyqt_path = os.path.dirname(PyQt5.__file__)
        plugins_path = os.path.join(pyqt_path, 'Qt5', 'plugins')
        if os.path.exists(plugins_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path
    except ImportError:
        pass
# ===============================

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QPushButton, QLabel,
                             QFileDialog, QMessageBox, QSystemTrayIcon,
                             QMenu, QAction, QTabWidget, QStatusBar, QTextEdit,
                             QLineEdit, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont


class AntivirusSignals(QObject):
    update_signal = pyqtSignal(str)
    block_signal = pyqtSignal(str, str)
    threat_signal = pyqtSignal(str)
    website_block_signal = pyqtSignal(str, str)


class AntivirusCore:
    def __init__(self):
        self.blocked_apps = []
        self.blocked_websites = []
        self.is_monitoring = False
        self.is_website_blocking = False
        self.monitor_thread = None
        self.website_block_thread = None
        self.signals = AntivirusSignals()
        self.load_data()

    def load_data(self):
        """Загрузка данных из файлов"""
        try:
            if os.path.exists('blocked_apps.json'):
                with open('blocked_apps.json', 'r', encoding='utf-8') as f:
                    self.blocked_apps = json.load(f)
        except Exception as e:
            self.blocked_apps = []
            self.signals.update_signal.emit(f"Ошибка загрузки приложений: {e}")

        try:
            if os.path.exists('blocked_websites.json'):
                with open('blocked_websites.json', 'r', encoding='utf-8') as f:
                    self.blocked_websites = json.load(f)
        except Exception as e:
            self.blocked_websites = []
            self.signals.update_signal.emit(f"Ошибка загрузки сайтов: {e}")

    def save_data(self):
        """Сохранение данных в файлы"""
        try:
            with open('blocked_apps.json', 'w', encoding='utf-8') as f:
                json.dump(self.blocked_apps, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка сохранения приложений: {e}")

        try:
            with open('blocked_websites.json', 'w', encoding='utf-8') as f:
                json.dump(self.blocked_websites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка сохранения сайтов: {e}")

    def add_app_to_blocklist(self, app_path):
        """Добавление приложения в черный список"""
        try:
            if os.path.exists(app_path) and app_path not in self.blocked_apps:
                self.blocked_apps.append(app_path)
                self.save_data()
                app_name = os.path.basename(app_path)
                self.signals.update_signal.emit(f"Добавлено приложение: {app_name}")
                return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка добавления приложения: {e}")
        return False

    def remove_app_from_blocklist(self, app_path):
        """Удаление приложения из черного списка"""
        try:
            if app_path in self.blocked_apps:
                self.blocked_apps.remove(app_path)
                self.save_data()
                app_name = os.path.basename(app_path)
                self.signals.update_signal.emit(f"Удалено приложение: {app_name}")
                return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка удаления приложения: {e}")
        return False

    def add_website_to_blocklist(self, website):
        """Добавление сайта в черный список"""
        try:
            website = website.strip().lower()
            if website and website not in self.blocked_websites:
                # Убедимся, что это домен без http:// и www
                website = website.replace('http://', '').replace('https://', '').replace('www.', '')
                if '.' in website:  # Проверяем что это валидный домен
                    self.blocked_websites.append(website)
                    self.save_data()
                    self.update_hosts_file()
                    self.signals.update_signal.emit(f"Добавлен сайт: {website}")
                    return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка добавления сайта: {e}")
        return False

    def remove_website_from_blocklist(self, website):
        """Удаление сайта из черного списка"""
        try:
            if website in self.blocked_websites:
                self.blocked_websites.remove(website)
                self.save_data()
                self.update_hosts_file()
                self.signals.update_signal.emit(f"Удален сайт: {website}")
                return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка удаления сайта: {e}")
        return False

    def update_hosts_file(self):
        """Обновление файла hosts для блокировки сайтов"""
        try:
            if os.name == 'nt':  # Windows
                hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
            else:  # Linux/Mac
                hosts_path = '/etc/hosts'

            # Читаем текущий файл hosts
            with open(hosts_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Удаляем старые блокировки от нашего антивируса
            new_lines = []
            for line in lines:
                if not line.strip().startswith('# ANTIVIRUS BLOCK') and not any(
                        site in line for site in self.blocked_websites):
                    new_lines.append(line)

            # Добавляем новые блокировки
            for site in self.blocked_websites:
                new_lines.append(f'127.0.0.1 {site} # ANTIVIRUS BLOCK\n')
                new_lines.append(f'127.0.0.1 www.{site} # ANTIVIRUS BLOCK\n')

            # Записываем обратно (требуются права администратора)
            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            # Очищаем DNS кэш
            self.flush_dns()

        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка обновления hosts: {e}")

    def flush_dns(self):
        """Очистка DNS кэша"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, shell=True)
            else:  # Linux/Mac
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], capture_output=True)
        except:
            pass

    def monitor_processes(self):
        """Оптимизированный мониторинг процессов с уменьшением утечек памяти"""
        last_checked = time.time()
        checked_processes = set()

        while self.is_monitoring:
            try:
                current_time = time.time()

                # Проверяем процессы каждые 5 секунд вместо 2 для уменьшения нагрузки
                if current_time - last_checked < 5:
                    time.sleep(0.1)
                    continue

                last_checked = current_time
                checked_processes.clear()

                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        if proc.info['pid'] in checked_processes:
                            continue

                        checked_processes.add(proc.info['pid'])
                        proc_exe = proc.info['exe']

                        if proc_exe and proc_exe in self.blocked_apps:
                            proc_name = proc.info['name']
                            proc.terminate()
                            time.sleep(0.1)

                            if proc.is_running():
                                proc.kill()

                            self.signals.block_signal.emit(proc_name, datetime.now().strftime("%H:%M:%S"))
                            self.log_event(f"BLOCKED APP: {proc_name}")

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                    except Exception as e:
                        self.signals.update_signal.emit(f"Ошибка обработки процесса: {e}")

                # Периодическая проверка угроз
                if current_time % 30 < 5:  # Каждые 30 секунд
                    self.check_for_threats()

                # Принудительный сбор мусора каждую минуту
                if current_time % 60 < 5:
                    gc.collect()

            except Exception as e:
                self.signals.update_signal.emit(f"Ошибка мониторинга: {e}")
                time.sleep(5)

    def monitor_network_connections(self):
        """Мониторинг сетевых соединений с оптимизацией"""
        last_checked = time.time()

        while self.is_website_blocking:
            try:
                current_time = time.time()

                # Проверяем соединения каждые 10 секунд
                if current_time - last_checked < 10:
                    time.sleep(0.1)
                    continue

                last_checked = current_time

                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        if proc.info['connections']:
                            for conn in proc.info['connections']:
                                if hasattr(conn, 'raddr') and conn.raddr:
                                    ip_addr = conn.raddr[0] if conn.raddr else ''
                                    for blocked_site in self.blocked_websites:
                                        if blocked_site in str(conn.raddr):
                                            self.signals.website_block_signal.emit(
                                                proc.info['name'], blocked_site)
                                            self.log_event(f"BLOCKED SITE: {blocked_site} from {proc.info['name']}")
                                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                    except Exception as e:
                        self.signals.update_signal.emit(f"Ошибка обработки сети: {e}")

                # Сбор мусора каждые 2 минуты
                if current_time % 120 < 10:
                    gc.collect()

            except Exception as e:
                self.signals.update_signal.emit(f"Ошибка мониторинга сети: {e}")
                time.sleep(10)

    def check_for_threats(self):
        """Проверка на известные угрозы"""
        known_threats = [
            'virus', 'malware', 'trojan', 'worm', 'keylogger',
            'ransomware', 'spyware', 'adware', 'botnet', 'miner'
        ]

        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                for threat in known_threats:
                    if threat in proc_name:
                        self.signals.threat_signal.emit(f"Обнаружена угроза: {proc_name}")
                        self.log_event(f"THREAT: {proc_name}")
                        break
            except:
                continue

    def log_event(self, message):
        """Логирование событий"""
        try:
            with open('antivirus_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}: {message}\n")
        except:
            pass

    def cleanup_memory(self):
        """Очистка памяти и ресурсов"""
        try:
            self.is_monitoring = False
            self.is_website_blocking = False
            time.sleep(1)  # Даем время потокам завершиться

            # Ждем завершения потоков
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2.0)

            if self.website_block_thread and self.website_block_thread.is_alive():
                self.website_block_thread.join(timeout=2.0)

            # Принудительный сбор мусора
            gc.collect()

            self.signals.update_signal.emit("Память очищена")

        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка очистки памяти: {e}")

    def start_monitoring(self):
        """Запуск мониторинга"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            self.monitor_thread.start()
            self.signals.update_signal.emit("Мониторинг приложений запущен")

    def start_website_blocking(self):
        """Запуск блокировки сайтов"""
        if not self.is_website_blocking:
            self.is_website_blocking = True
            self.website_block_thread = threading.Thread(target=self.monitor_network_connections, daemon=True)
            self.website_block_thread.start()
            self.signals.update_signal.emit("Блокировка сайтов запущена")

    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
        self.is_website_blocking = False
        self.cleanup_memory()
        self.signals.update_signal.emit("Мониторинг остановлен")

    def scan_system(self):
        """Сканирование системы"""
        threats = []
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                suspicious = ['crypt', 'miner', 'hack', 'inject', 'keylog']
                if any(word in proc_name for word in suspicious):
                    threats.append(proc_name)
            except:
                continue
        return threats


class AntivirusGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.antivirus = AntivirusCore()
        self.init_ui()

        # Подключаем сигналы
        self.antivirus.signals.update_signal.connect(self.update_status)
        self.antivirus.signals.block_signal.connect(self.add_blocked_event)
        self.antivirus.signals.threat_signal.connect(self.show_threat_alert)
        self.antivirus.signals.website_block_signal.connect(self.add_website_block_event)

        # Запускаем мониторинг
        self.antivirus.start_monitoring()
        self.antivirus.start_website_blocking()

    def init_ui(self):
        self.setWindowTitle('Антивирус - Блокировщик приложений и сайтов')
        self.setGeometry(300, 200, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладка приложений
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)

        app_group = QGroupBox("Блокировка приложений")
        app_group_layout = QVBoxLayout(app_group)

        app_group_layout.addWidget(QLabel("Заблокированные приложения:"))
        self.app_list = QListWidget()
        app_group_layout.addWidget(self.app_list)

        app_btn_layout = QHBoxLayout()
        self.add_app_btn = QPushButton("Добавить приложение")
        self.add_app_btn.clicked.connect(self.add_app)
        app_btn_layout.addWidget(self.add_app_btn)

        self.remove_app_btn = QPushButton("Удалить приложение")
        self.remove_app_btn.clicked.connect(self.remove_app)
        app_btn_layout.addWidget(self.remove_app_btn)

        app_group_layout.addLayout(app_btn_layout)
        app_layout.addWidget(app_group)
        tabs.addTab(app_tab, "Приложения")

        # Вкладка сайтов
        site_tab = QWidget()
        site_layout = QVBoxLayout(site_tab)

        site_group = QGroupBox("Блокировка сайтов")
        site_group_layout = QVBoxLayout(site_group)

        site_group_layout.addWidget(QLabel("Заблокированные сайты:"))
        self.site_list = QListWidget()
        site_group_layout.addWidget(self.site_list)

        site_input_layout = QHBoxLayout()
        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("Введите сайт (example.com)")
        site_input_layout.addWidget(self.site_input)

        self.add_site_btn = QPushButton("Добавить сайт")
        self.add_site_btn.clicked.connect(self.add_site)
        site_input_layout.addWidget(self.add_site_btn)

        site_group_layout.addLayout(site_input_layout)

        self.remove_site_btn = QPushButton("Удалить сайт")
        self.remove_site_btn.clicked.connect(self.remove_site)
        site_group_layout.addWidget(self.remove_site_btn)

        site_layout.addWidget(site_group)
        tabs.addTab(site_tab, "Сайты")

        # Вкладка логов
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)

        log_group = QGroupBox("Логи и управление")
        log_group_layout = QVBoxLayout(log_group)

        log_group_layout.addWidget(QLabel("Лог событий:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_group_layout.addWidget(self.log_text)

        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Сканировать систему")
        self.scan_btn.clicked.connect(self.scan_system)
        btn_layout.addWidget(self.scan_btn)

        self.cleanup_btn = QPushButton("Очистить память")
        self.cleanup_btn.clicked.connect(self.cleanup_memory)
        btn_layout.addWidget(self.cleanup_btn)

        log_group_layout.addLayout(btn_layout)
        log_layout.addWidget(log_group)
        tabs.addTab(log_tab, "Логи")

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Антивирус активен")
        self.status_bar.addWidget(self.status_label)

        self.update_app_list()
        self.update_site_list()

    def add_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите приложение", "", "Executable files (*.exe);;All files (*.*)"
        )
        if file_path and self.antivirus.add_app_to_blocklist(file_path):
            self.update_app_list()

    def remove_app(self):
        current = self.app_list.currentItem()
        if current and self.antivirus.remove_app_from_blocklist(current.data(Qt.UserRole)):
            self.update_app_list()

    def add_site(self):
        site = self.site_input.text().strip()
        if site and self.antivirus.add_website_to_blocklist(site):
            self.update_site_list()
            self.site_input.clear()

    def remove_site(self):
        current = self.site_list.currentItem()
        if current and self.antivirus.remove_website_from_blocklist(current.data(Qt.UserRole)):
            self.update_site_list()

    def update_app_list(self):
        self.app_list.clear()
        for app_path in self.antivirus.blocked_apps:
            app_name = os.path.basename(app_path)
            item = QListWidgetItem(app_name)
            item.setData(Qt.UserRole, app_path)
            self.app_list.addItem(item)

    def update_site_list(self):
        self.site_list.clear()
        for site in self.antivirus.blocked_websites:
            item = QListWidgetItem(site)
            item.setData(Qt.UserRole, site)
            self.site_list.addItem(item)

    def update_status(self, message):
        self.status_label.setText(message)
        self.log_text.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")

    def add_blocked_event(self, app_name, time_str):
        self.log_text.append(f"{time_str}: Заблокировано приложение {app_name}")

    def add_website_block_event(self, proc_name, website):
        self.log_text.append(f"{datetime.now().strftime('%H:%M:%S')}: Блокировка сайта {website} от {proc_name}")

    def show_threat_alert(self, message):
        QMessageBox.warning(self, "Обнаружена угроза!", message)
        self.log_text.append(f"ВНИМАНИЕ: {message}")

    def cleanup_memory(self):
        """Очистка памяти по кнопке"""
        self.antivirus.cleanup_memory()
        QMessageBox.information(self, "Очистка", "Память успешно очищена")

    def scan_system(self):
        threats = self.antivirus.scan_system()
        if threats:
            msg = f"Найдено подозрительных процессов: {len(threats)}\n" + "\n".join(threats[:10])  # Ограничиваем вывод
            if len(threats) > 10:
                msg += f"\n...и еще {len(threats) - 10} процессов"
            QMessageBox.warning(self, "Результаты сканирования", msg)
        else:
            QMessageBox.information(self, "Результаты сканирования", "Угроз не обнаружено")

    def closeEvent(self, event):
        # Очистка памяти перед закрытием
        self.antivirus.cleanup_memory()

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Антивирус продолжит работать в фоне. Завершить полностью?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.antivirus.stop_monitoring()
            event.accept()
        else:
            event.ignore()
            self.hide()


def is_admin():
    """Проверка прав администратора"""
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        return os.getuid() == 0
    except:
        return False


def main():
    # Проверка прав администратора
    if not is_admin():
        print("Предупреждение: Для блокировки сайтов запустите от имени администратора")

    # Проверка зависимостей
    try:
        import psutil
    except ImportError:
        print("Установите psutil: pip install psutil")
        return

    try:
        import PyQt5
    except ImportError:
        print("Установите PyQt5: pip install PyQt5")
        return

    app = QApplication(sys.argv)
    window = AntivirusGUI()
    window.show()

    # Очистка при завершении
    app.aboutToQuit.connect(window.antivirus.cleanup_memory)

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()import os
import sys
import json
import time
import threading
import psutil
import subprocess
import gc
from datetime import datetime

# ===== FIX QT PLUGIN ERROR =====
import os
if hasattr(sys, '_MEIPASS'):
    os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = os.path.join(sys._MEIPASS, 'PyQt5', 'Qt5', 'plugins')
else:
    try:
        import PyQt5
        pyqt_path = os.path.dirname(PyQt5.__file__)
        plugins_path = os.path.join(pyqt_path, 'Qt5', 'plugins')
        if os.path.exists(plugins_path):
            os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugins_path
    except ImportError:
        pass
# ===============================

from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QListWidget, QPushButton, QLabel,
                             QFileDialog, QMessageBox, QSystemTrayIcon,
                             QMenu, QAction, QTabWidget, QStatusBar, QTextEdit,
                             QLineEdit, QGroupBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QFont

class AntivirusSignals(QObject):
    update_signal = pyqtSignal(str)
    block_signal = pyqtSignal(str, str)
    threat_signal = pyqtSignal(str)
    website_block_signal = pyqtSignal(str, str)

class AntivirusCore:
    def __init__(self):
        self.blocked_apps = []
        self.blocked_websites = []
        self.is_monitoring = False
        self.is_website_blocking = False
        self.monitor_thread = None
        self.website_block_thread = None
        self.signals = AntivirusSignals()
        self.load_data()

    def load_data(self):
        """Загрузка данных из файлов"""
        try:
            if os.path.exists('blocked_apps.json'):
                with open('blocked_apps.json', 'r', encoding='utf-8') as f:
                    self.blocked_apps = json.load(f)
        except Exception as e:
            self.blocked_apps = []
            self.signals.update_signal.emit(f"Ошибка загрузки приложений: {e}")

        try:
            if os.path.exists('blocked_websites.json'):
                with open('blocked_websites.json', 'r', encoding='utf-8') as f:
                    self.blocked_websites = json.load(f)
        except Exception as e:
            self.blocked_websites = []
            self.signals.update_signal.emit(f"Ошибка загрузки сайтов: {e}")

    def save_data(self):
        """Сохранение данных в файлы"""
        try:
            with open('blocked_apps.json', 'w', encoding='utf-8') as f:
                json.dump(self.blocked_apps, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка сохранения приложений: {e}")

        try:
            with open('blocked_websites.json', 'w', encoding='utf-8') as f:
                json.dump(self.blocked_websites, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка сохранения сайтов: {e}")

    def add_app_to_blocklist(self, app_path):
        """Добавление приложения в черный список"""
        try:
            if os.path.exists(app_path) and app_path not in self.blocked_apps:
                self.blocked_apps.append(app_path)
                self.save_data()
                app_name = os.path.basename(app_path)
                self.signals.update_signal.emit(f"Добавлено приложение: {app_name}")
                return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка добавления приложения: {e}")
        return False

    def remove_app_from_blocklist(self, app_path):
        """Удаление приложения из черного списка"""
        try:
            if app_path in self.blocked_apps:
                self.blocked_apps.remove(app_path)
                self.save_data()
                app_name = os.path.basename(app_path)
                self.signals.update_signal.emit(f"Удалено приложение: {app_name}")
                return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка удаления приложения: {e}")
        return False

    def add_website_to_blocklist(self, website):
        """Добавление сайта в черный список"""
        try:
            website = website.strip().lower()
            if website and website not in self.blocked_websites:
                # Убедимся, что это домен без http:// и www
                website = website.replace('http://', '').replace('https://', '').replace('www.', '')
                if '.' in website:  # Проверяем что это валидный домен
                    self.blocked_websites.append(website)
                    self.save_data()
                    self.update_hosts_file()
                    self.signals.update_signal.emit(f"Добавлен сайт: {website}")
                    return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка добавления сайта: {e}")
        return False

    def remove_website_from_blocklist(self, website):
        """Удаление сайта из черного списка"""
        try:
            if website in self.blocked_websites:
                self.blocked_websites.remove(website)
                self.save_data()
                self.update_hosts_file()
                self.signals.update_signal.emit(f"Удален сайт: {website}")
                return True
        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка удаления сайта: {e}")
        return False

    def update_hosts_file(self):
        """Обновление файла hosts для блокировки сайтов"""
        try:
            if os.name == 'nt':  # Windows
                hosts_path = r'C:\Windows\System32\drivers\etc\hosts'
            else:  # Linux/Mac
                hosts_path = '/etc/hosts'

            # Читаем текущий файл hosts
            with open(hosts_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Удаляем старые блокировки от нашего антивируса
            new_lines = []
            for line in lines:
                if not line.strip().startswith('# ANTIVIRUS BLOCK') and not any(site in line for site in self.blocked_websites):
                    new_lines.append(line)

            # Добавляем новые блокировки
            for site in self.blocked_websites:
                new_lines.append(f'127.0.0.1 {site} # ANTIVIRUS BLOCK\n')
                new_lines.append(f'127.0.0.1 www.{site} # ANTIVIRUS BLOCK\n')

            # Записываем обратно (требуются права администратора)
            with open(hosts_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            # Очищаем DNS кэш
            self.flush_dns()

        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка обновления hosts: {e}")

    def flush_dns(self):
        """Очистка DNS кэша"""
        try:
            if os.name == 'nt':  # Windows
                subprocess.run(['ipconfig', '/flushdns'], capture_output=True, shell=True)
            else:  # Linux/Mac
                subprocess.run(['sudo', 'systemd-resolve', '--flush-caches'], capture_output=True)
        except:
            pass

    def monitor_processes(self):
        """Оптимизированный мониторинг процессов с уменьшением утечек памяти"""
        last_checked = time.time()
        checked_processes = set()

        while self.is_monitoring:
            try:
                current_time = time.time()

                # Проверяем процессы каждые 5 секунд вместо 2 для уменьшения нагрузки
                if current_time - last_checked < 5:
                    time.sleep(0.1)
                    continue

                last_checked = current_time
                checked_processes.clear()

                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        if proc.info['pid'] in checked_processes:
                            continue

                        checked_processes.add(proc.info['pid'])
                        proc_exe = proc.info['exe']

                        if proc_exe and proc_exe in self.blocked_apps:
                            proc_name = proc.info['name']
                            proc.terminate()
                            time.sleep(0.1)

                            if proc.is_running():
                                proc.kill()

                            self.signals.block_signal.emit(proc_name, datetime.now().strftime("%H:%M:%S"))
                            self.log_event(f"BLOCKED APP: {proc_name}")

                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                    except Exception as e:
                        self.signals.update_signal.emit(f"Ошибка обработки процесса: {e}")

                # Периодическая проверка угроз
                if current_time % 30 < 5:  # Каждые 30 секунд
                    self.check_for_threats()

                # Принудительный сбор мусора каждую минуту
                if current_time % 60 < 5:
                    gc.collect()

            except Exception as e:
                self.signals.update_signal.emit(f"Ошибка мониторинга: {e}")
                time.sleep(5)

    def monitor_network_connections(self):
        """Мониторинг сетевых соединений с оптимизацией"""
        last_checked = time.time()

        while self.is_website_blocking:
            try:
                current_time = time.time()

                # Проверяем соединения каждые 10 секунд
                if current_time - last_checked < 10:
                    time.sleep(0.1)
                    continue

                last_checked = current_time

                for proc in psutil.process_iter(['pid', 'name', 'connections']):
                    try:
                        if proc.info['connections']:
                            for conn in proc.info['connections']:
                                if hasattr(conn, 'raddr') and conn.raddr:
                                    ip_addr = conn.raddr[0] if conn.raddr else ''
                                    for blocked_site in self.blocked_websites:
                                        if blocked_site in str(conn.raddr):
                                            self.signals.website_block_signal.emit(
                                                proc.info['name'], blocked_site)
                                            self.log_event(f"BLOCKED SITE: {blocked_site} from {proc.info['name']}")
                                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                    except Exception as e:
                        self.signals.update_signal.emit(f"Ошибка обработки сети: {e}")

                # Сбор мусора каждые 2 минуты
                if current_time % 120 < 10:
                    gc.collect()

            except Exception as e:
                self.signals.update_signal.emit(f"Ошибка мониторинга сети: {e}")
                time.sleep(10)

    def check_for_threats(self):
        """Проверка на известные угрозы"""
        known_threats = [
            'virus', 'malware', 'trojan', 'worm', 'keylogger',
            'ransomware', 'spyware', 'adware', 'botnet', 'miner'
        ]

        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                for threat in known_threats:
                    if threat in proc_name:
                        self.signals.threat_signal.emit(f"Обнаружена угроза: {proc_name}")
                        self.log_event(f"THREAT: {proc_name}")
                        break
            except:
                continue

    def log_event(self, message):
        """Логирование событий"""
        try:
            with open('antivirus_log.txt', 'a', encoding='utf-8') as f:
                f.write(f"{datetime.now()}: {message}\n")
        except:
            pass

    def cleanup_memory(self):
        """Очистка памяти и ресурсов"""
        try:
            self.is_monitoring = False
            self.is_website_blocking = False
            time.sleep(1)  # Даем время потокам завершиться

            # Ждем завершения потоков
            if self.monitor_thread and self.monitor_thread.is_alive():
                self.monitor_thread.join(timeout=2.0)

            if self.website_block_thread and self.website_block_thread.is_alive():
                self.website_block_thread.join(timeout=2.0)

            # Принудительный сбор мусора
            gc.collect()

            self.signals.update_signal.emit("Память очищена")

        except Exception as e:
            self.signals.update_signal.emit(f"Ошибка очистки памяти: {e}")

    def start_monitoring(self):
        """Запуск мониторинга"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
            self.monitor_thread.start()
            self.signals.update_signal.emit("Мониторинг приложений запущен")

    def start_website_blocking(self):
        """Запуск блокировки сайтов"""
        if not self.is_website_blocking:
            self.is_website_blocking = True
            self.website_block_thread = threading.Thread(target=self.monitor_network_connections, daemon=True)
            self.website_block_thread.start()
            self.signals.update_signal.emit("Блокировка сайтов запущена")

    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
        self.is_website_blocking = False
        self.cleanup_memory()
        self.signals.update_signal.emit("Мониторинг остановлен")

    def scan_system(self):
        """Сканирование системы"""
        threats = []
        for proc in psutil.process_iter(['name']):
            try:
                proc_name = proc.info['name'].lower()
                suspicious = ['crypt', 'miner', 'hack', 'inject', 'keylog']
                if any(word in proc_name for word in suspicious):
                    threats.append(proc_name)
            except:
                continue
        return threats

class AntivirusGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.antivirus = AntivirusCore()
        self.init_ui()

        # Подключаем сигналы
        self.antivirus.signals.update_signal.connect(self.update_status)
        self.antivirus.signals.block_signal.connect(self.add_blocked_event)
        self.antivirus.signals.threat_signal.connect(self.show_threat_alert)
        self.antivirus.signals.website_block_signal.connect(self.add_website_block_event)

        # Запускаем мониторинг
        self.antivirus.start_monitoring()
        self.antivirus.start_website_blocking()

    def init_ui(self):
        self.setWindowTitle('Антивирус - Блокировщик приложений и сайтов')
        self.setGeometry(300, 200, 900, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Вкладка приложений
        app_tab = QWidget()
        app_layout = QVBoxLayout(app_tab)

        app_group = QGroupBox("Блокировка приложений")
        app_group_layout = QVBoxLayout(app_group)

        app_group_layout.addWidget(QLabel("Заблокированные приложения:"))
        self.app_list = QListWidget()
        app_group_layout.addWidget(self.app_list)

        app_btn_layout = QHBoxLayout()
        self.add_app_btn = QPushButton("Добавить приложение")
        self.add_app_btn.clicked.connect(self.add_app)
        app_btn_layout.addWidget(self.add_app_btn)

        self.remove_app_btn = QPushButton("Удалить приложение")
        self.remove_app_btn.clicked.connect(self.remove_app)
        app_btn_layout.addWidget(self.remove_app_btn)

        app_group_layout.addLayout(app_btn_layout)
        app_layout.addWidget(app_group)
        tabs.addTab(app_tab, "Приложения")

        # Вкладка сайтов
        site_tab = QWidget()
        site_layout = QVBoxLayout(site_tab)

        site_group = QGroupBox("Блокировка сайтов")
        site_group_layout = QVBoxLayout(site_group)

        site_group_layout.addWidget(QLabel("Заблокированные сайты:"))
        self.site_list = QListWidget()
        site_group_layout.addWidget(self.site_list)

        site_input_layout = QHBoxLayout()
        self.site_input = QLineEdit()
        self.site_input.setPlaceholderText("Введите сайт (example.com)")
        site_input_layout.addWidget(self.site_input)

        self.add_site_btn = QPushButton("Добавить сайт")
        self.add_site_btn.clicked.connect(self.add_site)
        site_input_layout.addWidget(self.add_site_btn)

        site_group_layout.addLayout(site_input_layout)

        self.remove_site_btn = QPushButton("Удалить сайт")
        self.remove_site_btn.clicked.connect(self.remove_site)
        site_group_layout.addWidget(self.remove_site_btn)

        site_layout.addWidget(site_group)
        tabs.addTab(site_tab, "Сайты")

        # Вкладка логов
        log_tab = QWidget()
        log_layout = QVBoxLayout(log_tab)

        log_group = QGroupBox("Логи и управление")
        log_group_layout = QVBoxLayout(log_group)

        log_group_layout.addWidget(QLabel("Лог событий:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_group_layout.addWidget(self.log_text)

        btn_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Сканировать систему")
        self.scan_btn.clicked.connect(self.scan_system)
        btn_layout.addWidget(self.scan_btn)

        self.cleanup_btn = QPushButton("Очистить память")
        self.cleanup_btn.clicked.connect(self.cleanup_memory)
        btn_layout.addWidget(self.cleanup_btn)

        log_group_layout.addLayout(btn_layout)
        log_layout.addWidget(log_group)
        tabs.addTab(log_tab, "Логи")

        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel("Антивирус активен")
        self.status_bar.addWidget(self.status_label)

        self.update_app_list()
        self.update_site_list()

    def add_app(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите приложение", "", "Executable files (*.exe);;All files (*.*)"
        )
        if file_path and self.antivirus.add_app_to_blocklist(file_path):
            self.update_app_list()

    def remove_app(self):
        current = self.app_list.currentItem()
        if current and self.antivirus.remove_app_from_blocklist(current.data(Qt.UserRole)):
            self.update_app_list()

    def add_site(self):
        site = self.site_input.text().strip()
        if site and self.antivirus.add_website_to_blocklist(site):
            self.update_site_list()
            self.site_input.clear()

    def remove_site(self):
        current = self.site_list.currentItem()
        if current and self.antivirus.remove_website_from_blocklist(current.data(Qt.UserRole)):
            self.update_site_list()

    def update_app_list(self):
        self.app_list.clear()
        for app_path in self.antivirus.blocked_apps:
            app_name = os.path.basename(app_path)
            item = QListWidgetItem(app_name)
            item.setData(Qt.UserRole, app_path)
            self.app_list.addItem(item)

    def update_site_list(self):
        self.site_list.clear()
        for site in self.antivirus.blocked_websites:
            item = QListWidgetItem(site)
            item.setData(Qt.UserRole, site)
            self.site_list.addItem(item)

    def update_status(self, message):
        self.status_label.setText(message)
        self.log_text.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")

    def add_blocked_event(self, app_name, time_str):
        self.log_text.append(f"{time_str}: Заблокировано приложение {app_name}")

    def add_website_block_event(self, proc_name, website):
        self.log_text.append(f"{datetime.now().strftime('%H:%M:%S')}: Блокировка сайта {website} от {proc_name}")

    def show_threat_alert(self, message):
        QMessageBox.warning(self, "Обнаружена угроза!", message)
        self.log_text.append(f"ВНИМАНИЕ: {message}")

    def cleanup_memory(self):
        """Очистка памяти по кнопке"""
        self.antivirus.cleanup_memory()
        QMessageBox.information(self, "Очистка", "Память успешно очищена")

    def scan_system(self):
        threats = self.antivirus.scan_system()
        if threats:
            msg = f"Найдено подозрительных процессов: {len(threats)}\n" + "\n".join(threats[:10])  # Ограничиваем вывод
            if len(threats) > 10:
                msg += f"\n...и еще {len(threats) - 10} процессов"
            QMessageBox.warning(self, "Результаты сканирования", msg)
        else:
            QMessageBox.information(self, "Результаты сканирования", "Угроз не обнаружено")

    def closeEvent(self, event):
        # Очистка памяти перед закрытием
        self.antivirus.cleanup_memory()

        reply = QMessageBox.question(
            self, 'Подтверждение',
            'Антивирус продолжит работать в фоне. Завершить полностью?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.antivirus.stop_monitoring()
            event.accept()
        else:
            event.ignore()
            self.hide()

def is_admin():
    """Проверка прав администратора"""
    try:
        if os.name == 'nt':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        return os.getuid() == 0
    except:
        return False

def main():
    # Проверка прав администратора
    if not is_admin():
        print("Предупреждение: Для блокировки сайтов запустите от имени администратора")

    # Проверка зависимостей
    try:
        import psutil
    except ImportError:
        print("Установите psutil: pip install psutil")
        return

    try:
        import PyQt5
    except ImportError:
        print("Установите PyQt5: pip install PyQt5")
        return

    app = QApplication(sys.argv)
    window = AntivirusGUI()
    window.show()

    # Очистка при завершении
    app.aboutToQuit.connect(window.antivirus.cleanup_memory)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()