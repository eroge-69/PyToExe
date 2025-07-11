import sys
import wmi
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QListWidget, QCheckBox, 
                             QTabWidget, QGroupBox, QSpinBox, QComboBox, QMessageBox, QInputDialog)
from PyQt5.QtCore import QTimer
import configparser
import socket
#from pyzabbix import ZabbixSender  # Исправленный импорт

class WMIMonitorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("WMI Monitor for Zabbix")
        self.setGeometry(100, 100, 800, 600)
        
        self.config = configparser.ConfigParser()
        self.current_config = None
        self.load_configurations()
        
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        # Основные вкладки
        tabs = QTabWidget()
        
        # Вкладка мониторинга
        self.monitor_tab = QWidget()
        self.init_monitor_tab()
        tabs.addTab(self.monitor_tab, "Мониторинг")
        
        # Вкладка настроек
        self.settings_tab = QWidget()
        self.init_settings_tab()
        tabs.addTab(self.settings_tab, "Настройки")
        
        # Вкладка Zabbix
        self.zabbix_tab = QWidget()
        self.init_zabbix_tab()
        tabs.addTab(self.zabbix_tab, "Zabbix")
        
        self.setCentralWidget(tabs)
        
        # Статус бар
        self.statusBar().showMessage("Готово")
        
    def init_monitor_tab(self):
        layout = QVBoxLayout()
        
        # Выбор конфигурации
        config_group = QGroupBox("Конфигурация")
        config_layout = QHBoxLayout()
        
        self.config_combo = QComboBox()
        self.config_combo.addItems(self.config.sections())
        self.config_combo.currentTextChanged.connect(self.load_config)
        
        self.save_config_btn = QPushButton("Сохранить")
        self.save_config_btn.clicked.connect(self.save_current_config)
        
        self.new_config_btn = QPushButton("Новая")
        self.new_config_btn.clicked.connect(self.create_new_config)
        
        config_layout.addWidget(QLabel("Конфигурация:"))
        config_layout.addWidget(self.config_combo, 1)
        config_layout.addWidget(self.save_config_btn)
        config_layout.addWidget(self.new_config_btn)
        config_group.setLayout(config_layout)
        
        # Информация о хосте
        host_group = QGroupBox("Целевой хост")
        host_layout = QVBoxLayout()
        
        self.host_edit = QLineEdit()
        self.user_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        
        host_layout.addWidget(QLabel("Адрес хоста:"))
        host_layout.addWidget(self.host_edit)
        host_layout.addWidget(QLabel("Пользователь:"))
        host_layout.addWidget(self.user_edit)
        host_layout.addWidget(QLabel("Пароль:"))
        host_layout.addWidget(self.password_edit)
        host_group.setLayout(host_layout)
        
        # Выбор данных для сбора
        data_group = QGroupBox("Собираемые данные")
        data_layout = QVBoxLayout()
        
        # CPU
        cpu_group = QGroupBox("Процессор")
        cpu_layout = QVBoxLayout()
        self.cpu_check = QCheckBox("Собирать данные о процессоре")
        self.cpu_name_check = QCheckBox("Имя процессора")
        self.cpu_load_check = QCheckBox("Загрузка процессора (%)")
        self.cpu_cores_check = QCheckBox("Количество ядер")
        
        cpu_layout.addWidget(self.cpu_check)
        cpu_layout.addWidget(self.cpu_name_check)
        cpu_layout.addWidget(self.cpu_load_check)
        cpu_layout.addWidget(self.cpu_cores_check)
        cpu_group.setLayout(cpu_layout)
        
        # Память
        mem_group = QGroupBox("Память")
        mem_layout = QVBoxLayout()
        self.mem_check = QCheckBox("Собирать данные о памяти")
        self.mem_total_check = QCheckBox("Общий объем памяти")
        self.mem_free_check = QCheckBox("Свободная память")
        self.mem_used_check = QCheckBox("Используемая память")
        
        mem_layout.addWidget(self.mem_check)
        mem_layout.addWidget(self.mem_total_check)
        mem_layout.addWidget(self.mem_free_check)
        mem_layout.addWidget(self.mem_used_check)
        mem_group.setLayout(mem_layout)
        
        # Диски
        disk_group = QGroupBox("Диски")
        disk_layout = QVBoxLayout()
        self.disk_check = QCheckBox("Собирать данные о дисках")
        self.disk_free_check = QCheckBox("Свободное место")
        self.disk_total_check = QCheckBox("Общий объем")
        self.disk_usage_check = QCheckBox("Использование (%)")
        
        disk_layout.addWidget(self.disk_check)
        disk_layout.addWidget(self.disk_free_check)
        disk_layout.addWidget(self.disk_total_check)
        disk_layout.addWidget(self.disk_usage_check)
        disk_group.setLayout(disk_layout)
        
        data_layout.addWidget(cpu_group)
        data_layout.addWidget(mem_group)
        data_layout.addWidget(disk_group)
        data_group.setLayout(data_layout)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Старт")
        self.start_btn.clicked.connect(self.start_monitoring)
        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.clicked.connect(self.stop_monitoring)
        self.stop_btn.setEnabled(False)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.stop_btn)
        
        # Лог
        self.log_area = QListWidget()
        
        layout.addWidget(config_group)
        layout.addWidget(host_group)
        layout.addWidget(data_group)
        layout.addLayout(button_layout)
        layout.addWidget(QLabel("Лог:"))
        layout.addWidget(self.log_area, 1)
        
        self.monitor_tab.setLayout(layout)
        
    def init_settings_tab(self):
        layout = QVBoxLayout()
        
        # Настройки интервала опроса
        interval_group = QGroupBox("Интервал опроса")
        interval_layout = QHBoxLayout()
        
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(10, 3600)
        self.interval_spin.setValue(60)
        self.interval_spin.setSuffix(" сек")
        
        interval_layout.addWidget(QLabel("Интервал:"))
        interval_layout.addWidget(self.interval_spin)
        interval_group.setLayout(interval_layout)
        
        # Настройки логирования
        log_group = QGroupBox("Логирование")
        log_layout = QVBoxLayout()
        
        self.log_to_file_check = QCheckBox("Сохранять лог в файл")
        self.log_file_edit = QLineEdit()
        self.log_file_edit.setPlaceholderText("Путь к файлу лога")
        
        log_layout.addWidget(self.log_to_file_check)
        log_layout.addWidget(self.log_file_edit)
        log_group.setLayout(log_layout)
        
        layout.addWidget(interval_group)
        layout.addWidget(log_group)
        layout.addStretch(1)
        
        self.settings_tab.setLayout(layout)
        
    def init_zabbix_tab(self):
        layout = QVBoxLayout()
        
        # Настройки подключения к Zabbix
        zabbix_group = QGroupBox("Настройки Zabbix")
        zabbix_layout = QVBoxLayout()
        
        self.zabbix_enable_check = QCheckBox("Отправлять данные в Zabbix")
        
        self.zabbix_server_edit = QLineEdit()
        self.zabbix_server_edit.setPlaceholderText("zabbix.server.com")
        
        self.zabbix_port_edit = QLineEdit()
        self.zabbix_port_edit.setPlaceholderText("10051")
        self.zabbix_port_edit.setText("10051")
        
        self.zabbix_host_edit = QLineEdit()
        self.zabbix_host_edit.setPlaceholderText("Имя хоста в Zabbix")
        
        zabbix_layout.addWidget(self.zabbix_enable_check)
        zabbix_layout.addWidget(QLabel("Zabbix сервер:"))
        zabbix_layout.addWidget(self.zabbix_server_edit)
        zabbix_layout.addWidget(QLabel("Порт:"))
        zabbix_layout.addWidget(self.zabbix_port_edit)
        zabbix_layout.addWidget(QLabel("Имя хоста в Zabbix:"))
        zabbix_layout.addWidget(self.zabbix_host_edit)
        zabbix_group.setLayout(zabbix_layout)
        
        # Тестирование подключения
        test_btn = QPushButton("Проверить подключение к Zabbix")
        test_btn.clicked.connect(self.test_zabbix_connection)
        
        layout.addWidget(zabbix_group)
        layout.addWidget(test_btn)
        layout.addStretch(1)
        
        self.zabbix_tab.setLayout(layout)
        
    def init_timer(self):
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.collect_data)
        self.monitoring = False
        
    def load_configurations(self):
        try:
            self.config.read('wmi_monitor.ini')
            if not self.config.sections():
                self.create_default_config()
        except Exception as e:
            self.create_default_config()
            
    def create_default_config(self):
        self.config['Default'] = {
            'host': 'localhost',
            'user': '',
            'password': '',
            'interval': '60',
            'cpu_enabled': 'True',
            'cpu_name': 'True',
            'cpu_load': 'True',
            'cpu_cores': 'True',
            'memory_enabled': 'True',
            'memory_total': 'True',
            'memory_free': 'True',
            'memory_used': 'True',
            'disk_enabled': 'True',
            'disk_free': 'True',
            'disk_total': 'True',
            'disk_usage': 'True',
            'zabbix_enabled': 'False',
            'zabbix_server': '',
            'zabbix_port': '10051',
            'zabbix_host': ''
        }
        self.save_config()
        
    def save_config(self):
        with open('wmi_monitor.ini', 'w') as configfile:
            self.config.write(configfile)
            
    def load_config(self, config_name):
        if config_name in self.config:
            section = self.config[config_name]
            self.current_config = config_name
            
            # Загрузка параметров хоста
            self.host_edit.setText(section.get('host', 'localhost'))
            self.user_edit.setText(section.get('user', ''))
            self.password_edit.setText(section.get('password', ''))
            
            # Загрузка параметров CPU
            self.cpu_check.setChecked(section.getboolean('cpu_enabled', True))
            self.cpu_name_check.setChecked(section.getboolean('cpu_name', True))
            self.cpu_load_check.setChecked(section.getboolean('cpu_load', True))
            self.cpu_cores_check.setChecked(section.getboolean('cpu_cores', True))
            
            # Загрузка параметров памяти
            self.mem_check.setChecked(section.getboolean('memory_enabled', True))
            self.mem_total_check.setChecked(section.getboolean('memory_total', True))
            self.mem_free_check.setChecked(section.getboolean('memory_free', True))
            self.mem_used_check.setChecked(section.getboolean('memory_used', True))
            
            # Загрузка параметров дисков
            self.disk_check.setChecked(section.getboolean('disk_enabled', True))
            self.disk_free_check.setChecked(section.getboolean('disk_free', True))
            self.disk_total_check.setChecked(section.getboolean('disk_total', True))
            self.disk_usage_check.setChecked(section.getboolean('disk_usage', True))
            
            # Загрузка настроек Zabbix
            self.zabbix_enable_check.setChecked(section.getboolean('zabbix_enabled', False))
            self.zabbix_server_edit.setText(section.get('zabbix_server', ''))
            self.zabbix_port_edit.setText(section.get('zabbix_port', '10051'))
            self.zabbix_host_edit.setText(section.get('zabbix_host', ''))
            
            # Загрузка настроек приложения
            self.interval_spin.setValue(int(section.get('interval', '60')))
            self.log_to_file_check.setChecked(section.getboolean('log_to_file', False))
            self.log_file_edit.setText(section.get('log_file', ''))
            
            self.log_message(f"Загружена конфигурация: {config_name}")
            
    def save_current_config(self):
        if not self.current_config:
            QMessageBox.warning(self, "Ошибка", "Не выбрана конфигурация для сохранения")
            return
            
        # Сохранение параметров хоста
        self.config[self.current_config]['host'] = self.host_edit.text()
        self.config[self.current_config]['user'] = self.user_edit.text()
        self.config[self.current_config]['password'] = self.password_edit.text()
        
        # Сохранение параметров CPU
        self.config[self.current_config]['cpu_enabled'] = str(self.cpu_check.isChecked())
        self.config[self.current_config]['cpu_name'] = str(self.cpu_name_check.isChecked())
        self.config[self.current_config]['cpu_load'] = str(self.cpu_load_check.isChecked())
        self.config[self.current_config]['cpu_cores'] = str(self.cpu_cores_check.isChecked())
        
        # Сохранение параметров памяти
        self.config[self.current_config]['memory_enabled'] = str(self.mem_check.isChecked())
        self.config[self.current_config]['memory_total'] = str(self.mem_total_check.isChecked())
        self.config[self.current_config]['memory_free'] = str(self.mem_free_check.isChecked())
        self.config[self.current_config]['memory_used'] = str(self.mem_used_check.isChecked())
        
        # Сохранение параметров дисков
        self.config[self.current_config]['disk_enabled'] = str(self.disk_check.isChecked())
        self.config[self.current_config]['disk_free'] = str(self.disk_free_check.isChecked())
        self.config[self.current_config]['disk_total'] = str(self.disk_total_check.isChecked())
        self.config[self.current_config]['disk_usage'] = str(self.disk_usage_check.isChecked())
        
        # Сохранение настроек Zabbix
        self.config[self.current_config]['zabbix_enabled'] = str(self.zabbix_enable_check.isChecked())
        self.config[self.current_config]['zabbix_server'] = self.zabbix_server_edit.text()
        self.config[self.current_config]['zabbix_port'] = self.zabbix_port_edit.text()
        self.config[self.current_config]['zabbix_host'] = self.zabbix_host_edit.text()
        
        # Сохранение настроек приложения
        self.config[self.current_config]['interval'] = str(self.interval_spin.value())
        self.config[self.current_config]['log_to_file'] = str(self.log_to_file_check.isChecked())
        self.config[self.current_config]['log_file'] = self.log_file_edit.text()
        
        self.save_config()
        self.log_message(f"Конфигурация {self.current_config} сохранена")
        
    def create_new_config(self):
        name, ok = QInputDialog.getText(self, "Новая конфигурация", "Введите имя новой конфигурации:")
        if ok and name:
            if name in self.config.sections():
                QMessageBox.warning(self, "Ошибка", "Конфигурация с таким именем уже существует")
                return
                
            self.config[name] = {}
            self.config_combo.addItem(name)
            self.config_combo.setCurrentText(name)
            self.current_config = name
            self.save_current_config()
            
    def start_monitoring(self):
        if not self.current_config:
            QMessageBox.warning(self, "Ошибка", "Не выбрана конфигурация")
            return
            
        if not self.host_edit.text():
            QMessageBox.warning(self, "Ошибка", "Не указан хост для мониторинга")
            return
            
        self.monitoring = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        interval = self.interval_spin.value() * 1000  # преобразуем в миллисекунды
        self.monitor_timer.start(interval)
        self.log_message(f"Мониторинг запущен. Интервал: {interval/1000} сек")
        
    def stop_monitoring(self):
        self.monitoring = False
        self.monitor_timer.stop()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.log_message("Мониторинг остановлен")
        
    def collect_data(self):
        if not self.monitoring:
            return
            
        host = self.host_edit.text()
        user = self.user_edit.text()
        password = self.password_edit.text()
        
        try:
            # Подключение к WMI
            if user and password:
                conn = wmi.WMI(host, user=user, password=password)
            else:
                conn = wmi.WMI(host)
                
            collected_data = {}
            
            # Сбор данных о процессоре
            if self.cpu_check.isChecked():
                cpu_info = conn.Win32_Processor()[0]
                
                if self.cpu_name_check.isChecked():
                    collected_data['cpu_name'] = cpu_info.Name
                    self.log_message(f"CPU Name: {cpu_info.Name}")
                    
                if self.cpu_load_check.isChecked():
                    collected_data['cpu_load'] = cpu_info.LoadPercentage
                    self.log_message(f"CPU Load: {cpu_info.LoadPercentage}%")
                    
                if self.cpu_cores_check.isChecked():
                    collected_data['cpu_cores'] = cpu_info.NumberOfCores
                    self.log_message(f"CPU Cores: {cpu_info.NumberOfCores}")
            
            # Сбор данных о памяти
            if self.mem_check.isChecked():
                os_info = conn.Win32_OperatingSystem()[0]
                
                if self.mem_total_check.isChecked():
                    total_mem = int(os_info.TotalVisibleMemorySize) / 1024  # в MB
                    collected_data['memory_total'] = total_mem
                    self.log_message(f"Total Memory: {total_mem:.2f} MB")
                    
                if self.mem_free_check.isChecked():
                    free_mem = int(os_info.FreePhysicalMemory) / 1024  # в MB
                    collected_data['memory_free'] = free_mem
                    self.log_message(f"Free Memory: {free_mem:.2f} MB")
                    
                if self.mem_used_check.isChecked():
                    total = int(os_info.TotalVisibleMemorySize)
                    free = int(os_info.FreePhysicalMemory)
                    used = (total - free) / 1024  # в MB
                    collected_data['memory_used'] = used
                    self.log_message(f"Used Memory: {used:.2f} MB")
            
            # Сбор данных о дисках
            if self.disk_check.isChecked():
                disks = conn.Win32_LogicalDisk(DriveType=3)  # только фиксированные диски
                
                for i, disk in enumerate(disks):
                    if self.disk_free_check.isChecked():
                        free = int(disk.FreeSpace) / (1024**3)  # в GB
                        collected_data[f'disk_{i}_free'] = free
                        self.log_message(f"Disk {disk.DeviceID} Free: {free:.2f} GB")
                        
                    if self.disk_total_check.isChecked():
                        total = int(disk.Size) / (1024**3)  # в GB
                        collected_data[f'disk_{i}_total'] = total
                        self.log_message(f"Disk {disk.DeviceID} Total: {total:.2f} GB")
                        
                    if self.disk_usage_check.isChecked():
                        total = int(disk.Size)
                        free = int(disk.FreeSpace)
                        if total > 0:
                            usage = 100 - (free / total * 100)
                            collected_data[f'disk_{i}_usage'] = usage
                            self.log_message(f"Disk {disk.DeviceID} Usage: {usage:.2f}%")
            
            # Отправка данных в Zabbix
            if self.zabbix_enable_check.isChecked() and collected_data:
                self.send_to_zabbix(collected_data)
                
        except Exception as e:
            self.log_message(f"Ошибка при сборе данных: {str(e)}", error=True)
            
    def send_to_zabbix(self, data):
        try:
            zabbix_server = self.zabbix_server_edit.text()
            zabbix_port = int(self.zabbix_port_edit.text())
            zabbix_host = self.zabbix_host_edit.text()
            
            if not zabbix_server or not zabbix_host:
                self.log_message("Не указаны параметры Zabbix сервера", error=True)
                return
                
            # Подготовка данных для Zabbix
            items = []
            for key, value in data.items():
                items.append((key, str(value)))
                
            # Создание и настройка отправителя
            sender = ZabbixSender(zabbix_server, port=zabbix_port)  # Исправленное создание sender
            sender.timeout = 5  # Таймаут 5 секунд
            
            # Отправка данных
            response = sender.send(items, zabbix_host)
            
            if response.failed == 0:
                self.log_message(f"Данные успешно отправлены в Zabbix. Обработано: {response.processed}")
            else:
                self.log_message(f"Ошибка отправки данных в Zabbix. Успешно: {response.processed}, Ошибки: {response.failed}", error=True)
                
        except Exception as e:
            self.log_message(f"Ошибка при отправке в Zabbix: {str(e)}", error=True)

    def test_zabbix_connection(self):
        zabbix_server = self.zabbix_server_edit.text()
        zabbix_port = self.zabbix_port_edit.text()
        
        if not zabbix_server or not zabbix_port:
            QMessageBox.warning(self, "Ошибка", "Не указаны параметры Zabbix сервера")
            return
            
        try:
            port = int(zabbix_port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((zabbix_server, port))
            sock.close()
            
            if result == 0:
                QMessageBox.information(self, "Успех", "Подключение к Zabbix серверу успешно")
            else:
                QMessageBox.warning(self, "Ошибка", f"Не удалось подключиться к Zabbix серверу. Код ошибки: {result}")
                
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при проверке подключения: {str(e)}")
            
    def log_message(self, message, error=False):
        if error:
            message = f"[ОШИБКА] {message}"
        self.log_area.addItem(message)
        self.log_area.scrollToBottom()
        
        # Логирование в файл
        if self.log_to_file_check.isChecked() and self.log_file_edit.text():
            try:
                with open(self.log_file_edit.text(), 'a') as f:
                    f.write(f"{message}\n")
            except Exception as e:
                self.statusBar().showMessage(f"Ошибка записи в лог-файл: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WMIMonitorApp()
    window.show()
    sys.exit(app.exec_())