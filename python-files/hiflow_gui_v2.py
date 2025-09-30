import sys
import os
import json
import numpy as np
from scipy import optimize
from datetime import datetime, timedelta
import serial
import serial.tools.list_ports
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QComboBox, QDialog, QProgressBar,
                             QMessageBox, QSlider, QLineEdit, QGroupBox, QAction, 
                             QMenu, QStatusBar, QGridLayout, QFrame, QTextEdit, QCheckBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QDateTimeAxis
from PyQt5.QtCore import QDateTime

# Ебучий класс для работы с последовательным портом в отдельном потоке
class SerialThread(QThread):
    data_received = pyqtSignal(dict)
    connection_lost = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.serial_port = None
        self.is_connected = False
        self.running = True
        self.last_flow_raw = 0
        self.last_pressure_raw = 0
        
    def connect_serial(self, port_name):
        try:
            self.serial_port = serial.Serial(
                port=port_name,
                baudrate=115200,
                timeout=1,
                write_timeout=1
            )
            self.is_connected = True
            print(f"Подключились к {port_name}")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            self.is_connected = False
            
    def disconnect_serial(self):
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        self.is_connected = False
        
    def send_command(self, command):
        if self.is_connected and self.serial_port:
            try:
                self.serial_port.write(f"{command}\n".encode())
            except Exception as e:
                print(f"Ошибка отправки команды: {e}")
                self.connection_lost.emit()
                
    def run(self):
        while self.running:
            if self.is_connected and self.serial_port and self.serial_port.is_open:
                try:
                    line = self.serial_port.readline().decode().strip()
                    if line:
                        data = self.parse_data(line)
                        if data:
                            self.data_received.emit(data)
                except Exception as e:
                    print(f"Ошибка чтения: {e}")
                    self.connection_lost.emit()
                    self.is_connected = False
            else:
                self.msleep(100)
                
    def parse_data(self, line):
        try:
            data = {}
            if line.startswith("FLOW:") and "PRESSURE:" in line:
                parts = line.split(",")
                data['flow_raw'] = int(parts[0].split(":")[1])
                data['pressure_raw'] = int(parts[1].split(":")[1])
                data['timestamp'] = datetime.now()
                self.last_flow_raw = data['flow_raw']
                self.last_pressure_raw = data['pressure_raw']
            return data
        except Exception as e:
            print(f"Ошибка парсинга данных: {e}")
            return None

# Окно выбора COM порта
class PortSelectorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_port = None
        self.init_ui()
        self.refresh_ports()
        
    def init_ui(self):
        self.setWindowTitle("Выбор COM порта")
        self.setFixedSize(400, 200)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QComboBox {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #333;
                color: white;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("Выберите COM порт Arduino Mega2560")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        # ComboBox для портов
        self.port_combo = QComboBox()
        layout.addWidget(QLabel("Доступные порты:"))
        layout.addWidget(self.port_combo)
        
        # Кнопка обновления
        self.refresh_btn = QPushButton("Обновить список")
        self.refresh_btn.clicked.connect(self.refresh_ports)
        layout.addWidget(self.refresh_btn)
        
        # Кнопки подключения/отмены
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.accept_connection)
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def refresh_ports(self):
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            # Показываем полное описание как в диспетчере устройств
            display_text = f"{port.device} - {port.description}"
            self.port_combo.addItem(display_text, port.device)
            
    def accept_connection(self):
        if self.port_combo.currentIndex() >= 0:
            self.selected_port = self.port_combo.currentData()
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Выберите COM порт!")

# Класс калибровки
class CalibrationManager:
    def __init__(self):
        self.calibration_file = "turbine_calibration.json"
        self.calibration_data = None
        self.load_calibration()
        
    def load_calibration(self):
        """Загружаем данные калибровки из файла"""
        try:
            if os.path.exists(self.calibration_file):
                with open(self.calibration_file, 'r') as f:
                    self.calibration_data = json.load(f)
                print("Калибровка загружена успешно")
                return True
        except Exception as e:
            print(f"Ошибка загрузки калибровки: {e}")
        return False
        
    def save_calibration(self, data):
        """Сохраняем данные калибровки в файл"""
        try:
            with open(self.calibration_file, 'w') as f:
                json.dump(data, f, indent=2)
            self.calibration_data = data
            print("Калибровка сохранена успешно")
            return True
        except Exception as e:
            print(f"Ошибка сохранения калибровки: {e}")
            return False
            
    def calculate_flow_from_raw(self, raw_value):
        """Вычисляем поток из сырого значения с использованием калибровки"""
        if not self.calibration_data:
            return raw_value  # Возвращаем сырое значение если калибровки нет
            
        try:
            # Используем полиномиальную аппроксимацию для более точного преобразования
            coefficients = self.calibration_data['flow_calibration']['coefficients']
            # Вычитаем смещение нуля перед применением полинома
            zero_offset = self.calibration_data['flow_calibration']['zero_offset']
            adjusted_value = raw_value - zero_offset
            flow = np.polyval(coefficients, adjusted_value)
            return max(0, flow)  # Поток не может быть отрицательным
        except:
            return raw_value
            
    def calculate_pressure_from_raw(self, raw_value):
        """Вычисляем давление из сырого значения с использованием калибровки"""
        if not self.calibration_data:
            return raw_value
            
        try:
            coefficients = self.calibration_data['pressure_calibration']['coefficients']
            # Вычитаем смещение нуля перед применением полинома
            zero_offset = self.calibration_data['pressure_calibration']['zero_offset']
            adjusted_value = raw_value - zero_offset
            pressure = np.polyval(coefficients, adjusted_value)
            return pressure
        except:
            return raw_value
            
    def get_pwm_for_flow(self, target_flow):
        """Получаем значение ШИМ для достижения целевого потока"""
        if not self.calibration_data or 'flow_to_pwm' not in self.calibration_data:
            return int(target_flow * 255 / 250)  # Линейная аппроксимация если калибровки нет
            
        try:
            # Используем обратную интерполяцию для получения ШИМ по потоку
            calibration_points = self.calibration_data['flow_to_pwm']
            flows = [point['flow'] for point in calibration_points]
            pwms = [point['pwm'] for point in calibration_points]
            
            # Интерполяция с экстраполяцией
            pwm = np.interp(target_flow, flows, pwms)
            return int(np.clip(pwm, 0, 255))
        except:
            return int(target_flow * 255 / 250)

# Окно калибровки
class CalibrationWindow(QDialog):
    def __init__(self, serial_thread, calibration_mgr, parent=None):
        super().__init__(parent)
        self.serial_thread = serial_thread
        self.calibration_mgr = calibration_mgr
        self.calibration_data = {}
        self.current_stage = 0
        self.calibration_points = []
        self.flow_zero_offset = 0
        self.pressure_zero_offset = 0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Калибровка турбины")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QPushButton {
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid #555;
                border-radius: 4px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Заголовок
        self.title_label = QLabel("АВТОМАТИЧЕСКАЯ КАЛИБРОВКА")
        self.title_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
        
        # Описание этапа
        self.stage_label = QLabel("Подготовка к калибровке...")
        self.stage_label.setWordWrap(True)
        layout.addWidget(self.stage_label)
        
        # Текущие показания
        self.readings_label = QLabel("Ожидание данных...")
        self.readings_label.setWordWrap(True)
        layout.addWidget(self.readings_label)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("Начать калибровку")
        self.start_btn.clicked.connect(self.start_calibration)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        
        self.cancel_btn = QPushButton("Отмена")
        self.cancel_btn.clicked.connect(self.reject)
        self.cancel_btn.setStyleSheet("background-color: #f44336; color: white;")
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
    def start_calibration(self):
        self.current_stage = 1
        self.start_btn.setEnabled(False)
        self.perform_automatic_calibration()
        
    def perform_automatic_calibration(self):
        """Выполняем автоматическую калибровку"""
        # Этап 1: Установка 0 потока
        self.update_stage("Этап 1/3: Установка нуля потока...\nУбедитесь, что поток воздуха отсутствует", 10)
        self.serial_thread.send_command("STOP")
        
        # Ждем стабилизации и собираем данные для нуля потока
        QTimer.singleShot(3000, self.capture_flow_zero)
        
    def capture_flow_zero(self):
        """Захватываем значение нуля для потока"""
        # Используем последнее полученное значение как ноль потока
        self.flow_zero_offset = self.serial_thread.last_flow_raw
        self.update_stage(f"Этап 1/3: Ноль потока установлен (ADC={self.flow_zero_offset})", 20)
        QTimer.singleShot(1000, self.stage2_calibration)
        
    def stage2_calibration(self):
        """Этап 2: Установка 0 давления"""
        self.update_stage("Этап 2/3: Установка нуля давления...\nУбедитесь, что давление атмосферное", 30)
        
        # Ждем стабилизации и собираем данные для нуля давления
        QTimer.singleShot(3000, self.capture_pressure_zero)
        
    def capture_pressure_zero(self):
        """Захватываем значение нуля для давления"""
        # Используем последнее полученное значение как ноль давления
        self.pressure_zero_offset = self.serial_thread.last_pressure_raw
        self.update_stage(f"Этап 2/3: Ноль давления установлен (ADC={self.pressure_zero_offset})", 40)
        QTimer.singleShot(1000, self.stage3_calibration)
        
    def stage3_calibration(self):
        """Этап 3: Калибровка потока по ШИМ"""
        self.update_stage("Этап 3/3: Калибровка потока...", 50)
        self.calibrate_flow_curve()
        
    def calibrate_flow_curve(self):
        """Калибруем кривую потока"""
        self.calibration_points = []
        pwm_values = [0, 25, 51, 76, 102, 127, 153]  # 0-100% с шагом 10%
        # [0, 25, 51, 76, 102, 127, 153, 178, 204, 229, 255]
        def calibrate_next_point(index):
            if index < len(pwm_values):
                pwm = pwm_values[index]
                progress = int(50 + (index * 40 / len(pwm_values)))
                self.update_stage(f"Калибровка: ШИМ {pwm} ({int(pwm/255*100)}%)...", progress)
                
                # Устанавливаем ШИМ
                self.serial_thread.send_command(f"PWM:{pwm}")
                self.serial_thread.send_command("START")
                
                # Ждем стабилизации
                QTimer.singleShot(4000, lambda: record_point(pwm, index))
            else:
                self.finish_calibration()
                
        def record_point(pwm, index):
            # Используем последние полученные данные с датчика
            raw_flow = self.serial_thread.last_flow_raw
            # Вычисляем реальный поток (линейная зависимость для демонстрации)
            # В реальной системе здесь должно быть поверочное устройство
            actual_flow = pwm * 250 / 255  # Линейная зависимость для демонстрации
            
            # Сохраняем точку калибровки с учетом смещения нуля
            adjusted_raw_flow = raw_flow - self.flow_zero_offset
            
            self.calibration_points.append({
                'pwm': pwm,
                'flow': actual_flow,
                'raw_flow': raw_flow,
                'adjusted_raw_flow': adjusted_raw_flow
            })
            
            self.update_stage(
                f"Точка {index+1}/{len(pwm_values)}: "
                f"ШИМ={pwm}, ADC={raw_flow}, Поток={actual_flow:.1f} л/мин", 
                int(50 + (index * 40 / len(pwm_values)))
            )
            
            # Переходим к следующей точке
            calibrate_next_point(index + 1)
            
        calibrate_next_point(0)
        
    def finish_calibration(self):
        """Завершаем калибровку и сохраняем данные"""
        self.serial_thread.send_command("STOP")
        
        # Вычисляем коэффициенты полиномиальной аппроксимации
        raw_flows = [point['adjusted_raw_flow'] for point in self.calibration_points]
        actual_flows = [point['flow'] for point in self.calibration_points]
        
        # Аппроксимируем полиномом 2-й степени
        if len(raw_flows) >= 3:
            coefficients = np.polyfit(raw_flows, actual_flows, 2)
        else:
            # Если точек мало, используем линейную аппроксимацию
            coefficients = np.polyfit(raw_flows, actual_flows, 1)
        
        # Для давления используем простую линейную калибровку
        pressure_coefficients = [0.1, 0.0]  # Примерные коэффициенты
        
        calibration_data = {
            'flow_calibration': {
                'coefficients': coefficients.tolist(),
                'zero_offset': self.flow_zero_offset,
                'calibration_points': self.calibration_points,
                'timestamp': datetime.now().isoformat()
            },
            'pressure_calibration': {
                'coefficients': pressure_coefficients,
                'zero_offset': self.pressure_zero_offset,
                'timestamp': datetime.now().isoformat()
            },
            'flow_to_pwm': self.calibration_points
        }
        
        if self.calibration_mgr.save_calibration(calibration_data):
            self.update_stage("Калибровка завершена успешно!", 100)
            QTimer.singleShot(2000, self.accept)
        else:
            self.update_stage("Ошибка сохранения калибровки!", 100)
            
    def update_stage(self, message, progress):
        """Обновляем прогресс и сообщение этапа"""
        self.stage_label.setText(message)
        self.progress_bar.setValue(int(progress))

# Главное окно приложения
class MedicalVentilatorGUI(QMainWindow):
    def __init__(self, serial_thread, calibration_mgr):
        super().__init__()
        self.serial_thread = serial_thread
        self.calibration_mgr = calibration_mgr
        self.flow_data = []
        self.pressure_data = []
        self.timestamps = []
        self.max_data_points = 600  # 30 секунд при 20 Hz
        
        # Переменные для режима HIFlow
        self.target_flow = 0
        self.is_hiflow_running = False
        
        # Переменные для игнорирования тревог
        self.ignore_alarms = False
        self.alarm_triggered = False
        
        # Переменные для тревог с правильным отсчетом времени
        self.flow_deviation_detected = False
        self.flow_deviation_start_time = None
        self.flow_warning_shown = False
        
        self.pressure_increase_detected = False
        self.high_pressure_start_time = None
        self.last_pressure_value = 0
        self.normal_pressure_value = 0  # Нормальное значение давления
        
        # Таймеры безопасности
        self.safety_timer = QTimer()
        self.safety_timer.timeout.connect(self.check_safety_conditions)
        self.safety_timer.setInterval(1000)  # 1 секунда
        
        self.init_ui()
        self.setup_charts()
        self.setup_serial_handlers()
        
    def init_ui(self):
        self.setWindowTitle("Медицинская система вентиляции - Управление турбиной")
        self.setMinimumSize(1200, 800)
        
        # Устанавливаем медицинский стиль
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e3a5f;
                color: white;
            }
            QWidget {
                background-color: #1e3a5f;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4CAF50;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #666;
                color: #999;
            }
            QPushButton#stop {
                background-color: #f44336;
            }
            QPushButton#stop:hover {
                background-color: #da190b;
            }
            QPushButton#ignore {
                background-color: #FF9800;
            }
            QPushButton#ignore:hover {
                background-color: #F57C00;
            }
            QPushButton#ignore:checked {
                background-color: #FF5722;
            }
            QLabel {
                padding: 5px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999999;
                height: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
            QCheckBox {
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #999;
                background-color: #333;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Создаем меню
        self.create_menu()
        
        # Верхняя панель с цифровыми показаниями
        self.create_readings_panel(layout)
        
        # Графики
        self.create_charts_panel(layout)
        
        # Панель управления HIFlow
        self.create_control_panel(layout)
        
        # Статус бар
        self.create_status_bar()
        
    def create_menu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2b2b2b;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #4CAF50;
            }
            QMenu {
                background-color: #2b2b2b;
                color: white;
            }
            QMenu::item:selected {
                background-color: #4CAF50;
            }
        """)
        
        # Меню Файл
        file_menu = menubar.addMenu('Файл')
        exit_action = QAction('Выход', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню Экран
        screen_menu = menubar.addMenu('Экран')
        windowed_action = QAction('Оконный', self)
        fullscreen_action = QAction('Полноэкранный', self)
        windowed_action.triggered.connect(self.showNormal)
        fullscreen_action.triggered.connect(self.showFullScreen)
        screen_menu.addAction(windowed_action)
        screen_menu.addAction(fullscreen_action)
        
        # Меню Калибровка
        cal_menu = menubar.addMenu('Калибровка')
        auto_cal_action = QAction('Автоматическая', self)
        manual_cal_action = QAction('Ручная', self)
        auto_cal_action.triggered.connect(self.start_auto_calibration)
        manual_cal_action.triggered.connect(self.start_manual_calibration)
        cal_menu.addAction(auto_cal_action)
        cal_menu.addAction(manual_cal_action)
        
        # Меню О программе
        about_menu = menubar.addMenu('О программе')
        about_action = QAction('О программе', self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)
        
    def create_readings_panel(self, layout):
        readings_group = QGroupBox("ТЕКУЩИЕ ПОКАЗАНИЯ")
        readings_layout = QHBoxLayout()
        
        # Поток
        flow_frame = QFrame()
        flow_frame.setStyleSheet("background-color: #2b4b7a; border-radius: 8px; padding: 10px;")
        flow_layout = QVBoxLayout(flow_frame)
        flow_layout.addWidget(QLabel("ПОТОК ВОЗДУХА"))
        self.flow_label = QLabel("0.0")
        self.flow_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.flow_label.setStyleSheet("color: #4CAF50;")
        flow_layout.addWidget(self.flow_label)
        flow_layout.addWidget(QLabel("л/мин"))
        readings_layout.addWidget(flow_frame)
        
        # Давление
        pressure_frame = QFrame()
        pressure_frame.setStyleSheet("background-color: #2b4b7a; border-radius: 8px; padding: 10px;")
        pressure_layout = QVBoxLayout(pressure_frame)
        pressure_layout.addWidget(QLabel("ДАВЛЕНИЕ"))
        self.pressure_label = QLabel("0.0")
        self.pressure_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.pressure_label.setStyleSheet("color: #FF9800;")
        pressure_layout.addWidget(self.pressure_label)
        pressure_layout.addWidget(QLabel("см.в.ст."))
        readings_layout.addWidget(pressure_frame)
        
        # Целевой поток (для HIFlow)
        target_frame = QFrame()
        target_frame.setStyleSheet("background-color: #2b4b7a; border-radius: 8px; padding: 10px;")
        target_layout = QVBoxLayout(target_frame)
        target_layout.addWidget(QLabel("ЦЕЛЕВОЙ ПОТОК"))
        self.target_flow_label = QLabel("0.0")
        self.target_flow_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.target_flow_label.setStyleSheet("color: #2196F3;")
        target_layout.addWidget(self.target_flow_label)
        target_layout.addWidget(QLabel("л/мин"))
        readings_layout.addWidget(target_frame)
        
        # Индикатор тревоги
        alarm_frame = QFrame()
        alarm_frame.setStyleSheet("background-color: #2b4b7a; border-radius: 8px; padding: 10px;")
        alarm_layout = QVBoxLayout(alarm_frame)
        alarm_layout.addWidget(QLabel("СТАТУС ТРЕВОГИ"))
        self.alarm_label = QLabel("НОРМА")
        self.alarm_label.setFont(QFont("Arial", 16, QFont.Bold))
        self.alarm_label.setStyleSheet("color: #4CAF50;")
        alarm_layout.addWidget(self.alarm_label)
        alarm_layout.addWidget(QLabel(""))
        readings_layout.addWidget(alarm_frame)
        
        readings_group.setLayout(readings_layout)
        layout.addWidget(readings_group)
        
    def create_charts_panel(self, layout):
        charts_group = QGroupBox("ГРАФИКИ ДАННЫХ (последние 30 секунд)")
        charts_layout = QHBoxLayout()
        
        # График потока
        self.flow_chart = QChart()
        self.flow_chart_view = QChartView(self.flow_chart)
        self.flow_chart.setTitle("Поток воздуха (л/мин)")
        self.flow_chart.setTheme(QChart.ChartThemeDark)
        charts_layout.addWidget(self.flow_chart_view)
        
        # График давления
        self.pressure_chart = QChart()
        self.pressure_chart_view = QChartView(self.pressure_chart)
        self.pressure_chart.setTitle("Давление (см.в.ст.)")
        self.pressure_chart.setTheme(QChart.ChartThemeDark)
        charts_layout.addWidget(self.pressure_chart_view)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)
        
    def create_control_panel(self, layout):
        control_group = QGroupBox("РЕЖИМ HIFlow - УПРАВЛЕНИЕ ТУРБИНОЙ")
        control_layout = QVBoxLayout()
        
        # Установка целевого потока
        target_layout = QHBoxLayout()
        target_layout.addWidget(QLabel("Целевой поток:"))
        self.flow_slider = QSlider(Qt.Horizontal)
        self.flow_slider.setRange(0, 250)
        self.flow_slider.valueChanged.connect(self.on_flow_slider_changed)
        target_layout.addWidget(self.flow_slider)
        
        self.flow_edit = QLineEdit("0")
        self.flow_edit.setFixedWidth(60)
        self.flow_edit.textChanged.connect(self.on_flow_edit_changed)
        target_layout.addWidget(self.flow_edit)
        target_layout.addWidget(QLabel("л/мин"))
        
        control_layout.addLayout(target_layout)
        
        # Кнопки управления
        btn_layout = QHBoxLayout()
        self.start_btn = QPushButton("СТАРТ")
        self.start_btn.setObjectName("start")
        self.start_btn.clicked.connect(self.start_hiflow)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14pt;")
        
        self.stop_btn = QPushButton("СТОП")
        self.stop_btn.setObjectName("stop")
        self.stop_btn.clicked.connect(self.stop_hiflow)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 14pt;")
        self.stop_btn.setEnabled(False)
        
        # Кнопка игнорирования тревог
        self.ignore_btn = QPushButton("ИГНОРИРОВАТЬ ТРЕВОГИ")
        self.ignore_btn.setObjectName("ignore")
        self.ignore_btn.setCheckable(True)
        self.ignore_btn.clicked.connect(self.toggle_ignore_alarms)
        self.ignore_btn.setStyleSheet("background-color: #FF9800; color: white; font-size: 12pt;")
        
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.ignore_btn)
        control_layout.addLayout(btn_layout)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
    def create_status_bar(self):
        self.status_bar = QStatusBar()
        self.connection_indicator = QLabel("●")
        self.connection_indicator.setFont(QFont("Arial", 16))
        self.connection_indicator.setStyleSheet("color: red;")
        self.status_bar.addWidget(self.connection_indicator)
        self.status_bar.addWidget(QLabel("Нет подключения"))
        
        # Индикатор игнорирования тревог
        self.ignore_indicator = QLabel("ТРЕВОГИ АКТИВНЫ")
        self.ignore_indicator.setFont(QFont("Arial", 10))
        self.ignore_indicator.setStyleSheet("color: #4CAF50; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.ignore_indicator)
        
        self.setStatusBar(self.status_bar)
        
    def setup_charts(self):
        """Настраиваем графики"""
        # Серии данных для графиков
        self.flow_series = QLineSeries()
        self.pressure_series = QLineSeries()
        
        # Оси для графика потока
        self.flow_axisX = QDateTimeAxis()
        self.flow_axisX.setFormat("hh:mm:ss")
        self.flow_axisY = QValueAxis()
        self.flow_axisY.setRange(0, 250)
        self.flow_axisY.setTitleText("л/мин")
        
        self.flow_chart.addSeries(self.flow_series)
        self.flow_chart.addAxis(self.flow_axisX, Qt.AlignBottom)
        self.flow_chart.addAxis(self.flow_axisY, Qt.AlignLeft)
        self.flow_series.attachAxis(self.flow_axisX)
        self.flow_series.attachAxis(self.flow_axisY)
        
        # Оси для графика давления
        self.pressure_axisX = QDateTimeAxis()
        self.pressure_axisX.setFormat("hh:mm:ss")
        self.pressure_axisY = QValueAxis()
        self.pressure_axisY.setRange(-5, 40)
        self.pressure_axisY.setTitleText("см.в.ст.")
        
        self.pressure_chart.addSeries(self.pressure_series)
        self.pressure_chart.addAxis(self.pressure_axisX, Qt.AlignBottom)
        self.pressure_chart.addAxis(self.pressure_axisY, Qt.AlignLeft)
        self.pressure_series.attachAxis(self.pressure_axisX)
        self.pressure_series.attachAxis(self.pressure_axisY)
        
    def setup_serial_handlers(self):
        """Настраиваем обработчики serial порта"""
        self.serial_thread.data_received.connect(self.on_data_received)
        self.serial_thread.connection_lost.connect(self.on_connection_lost)
        
        # Таймер для обновления графиков
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_charts)
        self.update_timer.start(100)  # 10 Hz
        
    def on_data_received(self, data):
        """Обрабатываем полученные данные"""
        # Обновляем индикатор подключения
        self.connection_indicator.setStyleSheet("color: green;")
        self.status_bar.showMessage("Устройство подключено")
        
        # Вычисляем калиброванные значения
        flow_value = self.calibration_mgr.calculate_flow_from_raw(data['flow_raw'])
        pressure_value = self.calibration_mgr.calculate_pressure_from_raw(data['pressure_raw'])
        
        # Фильтруем значения для плавного отображения
        filtered_flow = self.low_pass_filter(flow_value, self.flow_data)
        filtered_pressure = self.low_pass_filter(pressure_value, self.pressure_data)
        
        # Обновляем цифровые показания
        self.flow_label.setText(f"{filtered_flow:.1f}")
        self.pressure_label.setText(f"{filtered_pressure:.1f}")
        
        # Сохраняем данные для графиков
        current_time = QDateTime.currentDateTime()
        
        if len(self.flow_data) >= self.max_data_points:
            self.flow_data.pop(0)
            self.pressure_data.pop(0)
            self.timestamps.pop(0)
            
        self.flow_data.append(filtered_flow)
        self.pressure_data.append(filtered_pressure)
        self.timestamps.append(current_time)
        
        # Проверяем условия безопасности (если не игнорируем тревоги)
        if not self.ignore_alarms:
            self.check_safety_conditions_immediate(filtered_flow, filtered_pressure)
        
    def low_pass_filter(self, new_value, data_series, alpha=0.3):
        """Простой низкочастотный фильтр для сглаживания данных"""
        if not data_series:
            return new_value
        return alpha * new_value + (1 - alpha) * data_series[-1]
        
    def update_charts(self):
        """Обновляем графики"""
        if not self.timestamps:
            return
            
        # Обновляем график потока
        self.flow_series.clear()
        for i, (timestamp, value) in enumerate(zip(self.timestamps, self.flow_data)):
            self.flow_series.append(timestamp.toMSecsSinceEpoch(), value)
            
        # Обновляем график давления
        self.pressure_series.clear()
        for i, (timestamp, value) in enumerate(zip(self.timestamps, self.pressure_data)):
            self.pressure_series.append(timestamp.toMSecsSinceEpoch(), value)
            
        # Обновляем диапазон времени на осях X
        if len(self.timestamps) > 1:
            min_time = self.timestamps[0]
            max_time = self.timestamps[-1]
            
            self.flow_axisX.setRange(min_time, max_time)
            self.pressure_axisX.setRange(min_time, max_time)
            
    def on_flow_slider_changed(self, value):
        """Обработчик изменения слайдера потока"""
        self.target_flow = value
        self.target_flow_label.setText(f"{value}")
        self.flow_edit.setText(str(value))
        
    def on_flow_edit_changed(self, text):
        """Обработчик изменения текстового поля потока"""
        try:
            value = int(text)
            value = max(0, min(250, value))
            self.target_flow = value
            self.flow_slider.setValue(value)
            self.target_flow_label.setText(f"{value}")
        except ValueError:
            pass
            
    def start_hiflow(self):
        """Запускаем режим HIFlow"""
        if self.target_flow <= 0:
            QMessageBox.warning(self, "Ошибка", "Установите целевой поток больше 0!")
            return
            
        # Сбрасываем счетчики тревог при запуске
        self.flow_deviation_detected = False
        self.flow_deviation_start_time = None
        self.flow_warning_shown = False
        self.pressure_increase_detected = False
        self.high_pressure_start_time = None
        self.alarm_triggered = False
        self.alarm_label.setText("НОРМА")
        self.alarm_label.setStyleSheet("color: #4CAF50;")
        
        # Запоминаем нормальное значение давления при старте
        if len(self.pressure_data) > 0:
            self.normal_pressure_value = self.pressure_data[-1]
        else:
            self.normal_pressure_value = 0
            
        # Вычисляем необходимый ШИМ
        pwm_value = self.calibration_mgr.get_pwm_for_flow(self.target_flow)
        
        # Устанавливаем ШИМ и запускаем турбину
        self.serial_thread.send_command(f"PWM:{pwm_value}")
        self.serial_thread.send_command("START")
        
        self.is_hiflow_running = True
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.flow_slider.setEnabled(False)
        self.flow_edit.setEnabled(False)
        
        # Запускаем таймер безопасности (если не игнорируем тревоги)
        if not self.ignore_alarms:
            self.safety_timer.start(1000)  # Проверка каждую секунду
        
        print(f"Запущен HIFlow: цель {self.target_flow} л/мин, ШИМ {pwm_value}")
        
    def stop_hiflow(self):
        """Останавливаем режим HIFlow"""
        self.serial_thread.send_command("STOP")
        self.is_hiflow_running = False
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.flow_slider.setEnabled(True)
        self.flow_edit.setEnabled(True)
        self.safety_timer.stop()
        
        # Сбрасываем состояние тревог при остановке
        self.pressure_increase_detected = False
        self.high_pressure_start_time = None
        
    def toggle_ignore_alarms(self):
        """Переключаем режим игнорирования тревог"""
        self.ignore_alarms = self.ignore_btn.isChecked()
        
        if self.ignore_alarms:
            self.ignore_btn.setStyleSheet("background-color: #FF5722; color: white; font-size: 12pt;")
            self.ignore_btn.setText("ТРЕВОГИ ИГНОРИРУЮТСЯ")
            self.ignore_indicator.setText("ТРЕВОГИ ОТКЛЮЧЕНЫ")
            self.ignore_indicator.setStyleSheet("color: #FF5722; font-weight: bold;")
            self.alarm_label.setText("ТРЕВОГИ\nОТКЛЮЧЕНЫ")
            self.alarm_label.setStyleSheet("color: #f7f745;")
            self.safety_timer.stop()
            print("Режим игнорирования тревог ВКЛЮЧЕН")
        else:
            self.ignore_btn.setStyleSheet("background-color: #FF9800; color: white; font-size: 12pt;")
            self.ignore_btn.setText("ИГНОРИРОВАТЬ ТРЕВОГИ")
            self.ignore_indicator.setText("ТРЕВОГИ АКТИВНЫ")
            self.ignore_indicator.setStyleSheet("color: #4CAF50; font-weight: bold;")
            self.alarm_label.setText("НОРМА")
            self.alarm_label.setStyleSheet("color: #4CAF50;")
            if self.is_hiflow_running:
                self.safety_timer.start(1000)
            print("Режим игнорирования тревог ВЫКЛЮЧЕН")
            
    def check_safety_conditions(self):
        """Проверяем условия безопасности (вызывается по таймеру)"""
        if not self.flow_data or not self.pressure_data:
            return
            
        current_flow = self.flow_data[-1]
        current_pressure = self.pressure_data[-1]
        self.check_safety_conditions_immediate(current_flow, current_pressure)
        
    def check_safety_conditions_immediate(self, current_flow, current_pressure):
        """Непосредственная проверка условий безопасности"""
        # Если тревоги игнорируются - выходим
        if self.ignore_alarms:
            return
            
        # ТРЕВОГА 1: Пережат контур (увеличилось давление И уменьшился/не изменился поток)
        if self.is_hiflow_running:
            # Проверяем значительное увеличение давления (более 15 см.в.ст. от нормального)
            pressure_increase = current_pressure - self.normal_pressure_value
            
            if pressure_increase > 15:  # Значительное увеличение давления
                # Проверяем, что поток не увеличился пропорционально (признак пережатия)
                flow_deviation = abs(current_flow - self.target_flow) / self.target_flow
                
                # Если поток не достиг целевого или уменьшился - это признак пережатия
                if current_flow < self.target_flow * 0.9:  # Поток меньше 90% от целевого
                    if not self.pressure_increase_detected:
                        self.pressure_increase_detected = True
                        self.high_pressure_start_time = datetime.now()
                        print(f"Обнаружены признаки пережатия контура: давление +{pressure_increase:.1f} см.в.ст., поток {current_flow:.1f} л/мин (цель {self.target_flow} л/мин). Время начала: {self.high_pressure_start_time.strftime('%H:%M:%S')}")
                    else:
                        # Проверяем, прошло ли 10 секунд
                        time_elapsed = (datetime.now() - self.high_pressure_start_time).total_seconds()
                        if time_elapsed >= 10:
                            self.trigger_high_pressure_alarm()
            else:
                # Если давление нормализовалось, сбрасываем тревогу
                if self.pressure_increase_detected and pressure_increase < 10:
                    self.pressure_increase_detected = False
                    print("Давление нормализовалось, тревога пережатия сброшена")
                
            self.last_pressure_value = current_pressure
        
        # ТРЕВОГА 2: Проблема с достижением целевого потока (давление в норме)
        if self.is_hiflow_running and self.target_flow > 0:
            deviation = abs(current_flow - self.target_flow) / self.target_flow
            
            # Проверяем отклонение потока только если давление в норме
            pressure_deviation = abs(current_pressure - self.normal_pressure_value)
            
            if deviation > 0.15 and pressure_deviation < 10:  # Большое отклонение потока И нормальное давление
                if not self.flow_deviation_detected:
                    self.flow_deviation_detected = True
                    self.flow_deviation_start_time = datetime.now()
                    print(f"Обнаружено отклонение потока: {deviation*100:.1f}% при нормальном давлении. Время начала: {self.flow_deviation_start_time.strftime('%H:%M:%S')}")
                else:
                    # Проверяем, прошло ли 10 секунд
                    time_elapsed = (datetime.now() - self.flow_deviation_start_time).total_seconds()
                    
                    # Показываем предупреждение после 5 секунд
                    if 5 <= time_elapsed < 10 and not self.flow_warning_shown:
                        self.alarm_label.setText("ПРЕДУПРЕЖДЕНИЕ: Отклонение потока")
                        self.alarm_label.setStyleSheet("color: #FF9800;")
                        self.flow_warning_shown = True
                        print("Предупреждение: отклонение потока более 5 секунд при нормальном давлении")
                    
                    # Отключаем после 10 секунд
                    if time_elapsed >= 10:
                        self.trigger_flow_deviation_alarm()
            else:
                # Если поток нормализовался или давление изменилось, сбрасываем тревогу
                if self.flow_deviation_detected:
                    self.flow_deviation_detected = False
                    self.flow_warning_shown = False
                    if not self.alarm_triggered:
                        self.alarm_label.setText("НОРМА")
                        self.alarm_label.setStyleSheet("color: #4CAF50;")
                    print("Поток нормализовался или изменилось давление, тревога сброшена")
                    
    def trigger_flow_deviation_alarm(self):
        """Срабатывание тревоги по отклонению потока"""
        if self.ignore_alarms:
            return
            
        self.alarm_triggered = True
        self.alarm_label.setText("ОШИБКА ПОТОКА!")
        self.alarm_label.setStyleSheet("color: #f44336;")
        
        time_elapsed = (datetime.now() - self.flow_deviation_start_time).total_seconds()
        print(f"Сработала тревога потока! Отклонение продолжалось {time_elapsed:.1f} секунд при нормальном давлении")
        
        self.stop_hiflow()
        QMessageBox.critical(self, "ТРЕВОГА!", 
                           "Не возможно установить целевой поток. Произведите калибровку или обратитесь в техническую поддержку")
        
    def trigger_high_pressure_alarm(self):
        """Срабатывание тревоги по высокому давлению"""
        if self.ignore_alarms:
            return
            
        self.alarm_triggered = True
        self.alarm_label.setText("ПЕРЕЖАТ КОНТУР!")
        self.alarm_label.setStyleSheet("color: #f44336;")
        
        time_elapsed = (datetime.now() - self.high_pressure_start_time).total_seconds()
        current_flow = self.flow_data[-1] if self.flow_data else 0
        current_pressure = self.pressure_data[-1] if self.pressure_data else 0
        
        print(f"Сработала тревога пережатия! Высокое давление продолжалось {time_elapsed:.1f} секунд. Поток: {current_flow:.1f} л/мин, Давление: {current_pressure:.1f} см.в.ст.")
        
        self.stop_hiflow()
        QMessageBox.critical(self, "ТРЕВОГА!", 
                           "Пережат контур на пациента - НЕ БАЛУЙСЯ")
        
    def on_connection_lost(self):
        """Обработчик потери соединения"""
        self.connection_indicator.setStyleSheet("color: red;")
        self.status_bar.showMessage("Потеряно соединение с устройством")
        self.stop_hiflow()
        
    def start_auto_calibration(self):
        """Запуск автоматической калибровки"""
        cal_window = CalibrationWindow(self.serial_thread, self.calibration_mgr, self)
        cal_window.exec_()
        
    def start_manual_calibration(self):
        """Запуск ручной калибровки"""
        QMessageBox.information(self, "Ручная калибровка", 
                              "Ручная калибровка будет реализована в следующей версии")
        
    def show_about(self):
        """Показываем информацию о программе"""
        QMessageBox.about(self, "О программе",
                        "Медицинская система управления турбиной WS7040\n\n"
                        "Версия 2.0\n"
                        "Разработано для управления медицинской турбиной\n"
                        "с датчиком потока FS6122\n"
                        "Отработка тревог и их игнорирование")
# Главная функция приложения
def main():
    app = QApplication(sys.argv)
    
    # Создаем менеджер калибровки
    calibration_mgr = CalibrationManager()
    
    # Показываем окно выбора порта
    port_dialog = PortSelectorDialog()
    if port_dialog.exec_() != QDialog.Accepted:
        sys.exit(0)
        
    selected_port = port_dialog.selected_port
    
    # Создаем и запускаем поток serial порта
    serial_thread = SerialThread()
    serial_thread.connect_serial(selected_port)
    serial_thread.start()
    
    # Проверяем наличие калибровки
    if not calibration_mgr.calibration_data:
        # Запускаем калибровку если файл не найден
        cal_window = CalibrationWindow(serial_thread, calibration_mgr)
        if cal_window.exec_() != QDialog.Accepted:
            serial_thread.running = False
            serial_thread.wait(1000)
            sys.exit(0)
    
    # Создаем и показываем главное окно
    main_window = MedicalVentilatorGUI(serial_thread, calibration_mgr)
    main_window.show()
    
    # Обработка закрытия приложения
    def cleanup():
        serial_thread.running = False
        serial_thread.disconnect_serial()
        serial_thread.wait(1000)
        
    app.aboutToQuit.connect(cleanup)
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()