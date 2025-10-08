import sys
import serial
import re
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QTabWidget, QPushButton, QLabel, QGridLayout,
                             QGroupBox, QTextEdit, QDialog, QDialogButtonBox, 
                             QLineEdit, QFormLayout, QMessageBox, QProgressBar,
                             QFileDialog, QComboBox, QCheckBox, QSpinBox, QSizePolicy)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter, QPen
import pyqtgraph as pg
import numpy as np
# переменные 
version = 3.7 # ВЕРСИЯ МОНИТОРА И ПРОШИВКИ КОНТРОЛЕРА 
COM_SPEED = 9600 # СКОРОСТЬ КОМ ПОРТА 

# Единый стиль для всех диалоговых окон
DIALOG_STYLE = """
    QDialog {
        background-color: #252535;
        color: #ffffff;
    }
    QLabel {
        color: #ffffff;
        font-size: 11px;
    }
    QLineEdit, QSpinBox, QComboBox {
        background-color: #2a2a3a;
        color: #ffffff;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 5px;
        font-size: 11px;
        min-height: 20px;
    }
    QPushButton {
        background-color: #ff6b00;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
        min-width: 80px;
    }
    QPushButton:hover {
        background-color: #ff8c00;
    }
    QPushButton:pressed {
        background-color: #e55a00;
    }
    QGroupBox {
        color: #ffffff;
        font-weight: bold;
        border: 1px solid #555;
        border-radius: 4px;
        margin-top: 10px;
        padding-top: 10px;
        font-size: 12px;
    }
    QCheckBox {
        color: #ffffff;
        font-size: 11px;
    }
    QProgressBar {
        border: 1px solid #444;
        border-radius: 3px;
        text-align: center;
        color: white;
        background-color: #2a2a3a;
    }
    QProgressBar::chunk {
        background-color: #ff6b00;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        width: 0px;
        border: none;
    }
"""

class CalibrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Калибровка датчика топлива")
        self.setModal(True)
        self.setFixedSize(450, 350)
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.empty_voltage = QLineEdit()
        self.empty_voltage.setText("2.07")
        self.empty_voltage.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        form_layout.addRow("Напряжение пустого бака (В):", self.empty_voltage)
        
        self.full_voltage = QLineEdit()
        self.full_voltage.setText("2.48")
        self.full_voltage.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        form_layout.addRow("Напряжение полного бака (В):", self.full_voltage)
        
        self.tank_capacity = QLineEdit()
        self.tank_capacity.setText("40.0")
        self.tank_capacity.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        form_layout.addRow("Объем бака (л):", self.tank_capacity)
        
        layout.addLayout(form_layout)
        
        self.info_label = QLabel("Для калибровки:\n1. Слейте топливо до пустого бака\n2. Замерьте напряжение\n3. Заполните бак полностью\n4. Замерьте напряжение")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("background-color: #2a2a3a; padding: 10px; border-radius: 4px; color: #ffffff;")
        layout.addWidget(self.info_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class HistorySizeDialog(QDialog):
    def __init__(self, current_size, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Настройка размера истории")
        self.setModal(True)
        self.setFixedSize(350, 180)
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.history_spin = QSpinBox()
        self.history_spin.setRange(100, 10000)
        self.history_spin.setValue(current_size)
        self.history_spin.setSuffix(" точек")
        self.history_spin.setSingleStep(100)
        self.history_spin.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        form_layout.addRow("Размер истории:", self.history_spin)
        
        layout.addLayout(form_layout)
        
        info_label = QLabel("Больший размер увеличивает потребление памяти,\nно позволяет просматривать более длинные периоды")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #2a2a3a; padding: 10px; border-radius: 4px; color: #ffffff;")
        layout.addWidget(info_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class FolderSelectDialog(QDialog):
    def __init__(self, current_folder, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Выбор папки для сохранения данных")
        self.setModal(True)
        self.setFixedSize(500, 150)
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        
        form_layout = QFormLayout()
        
        self.folder_label = QLabel(current_folder)
        self.folder_label.setStyleSheet("background-color: #2a2a3a; padding: 8px; border-radius: 3px; color: #ffffff;")
        self.folder_label.setWordWrap(True)
        form_layout.addRow("Текущая папка:", self.folder_label)
        
        layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("Выбрать папку")
        self.select_btn.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_btn)
        
        button_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        button_layout.addWidget(buttons)
        
        layout.addLayout(button_layout)
        
        self.selected_folder = current_folder
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку для сохранения данных", self.selected_folder)
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(folder)

class SystemCalibrationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Калибровка системы")
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.setStyleSheet(DIALOG_STYLE)
        
        layout = QVBoxLayout(self)
        
        # Параметры двигателя
        engine_group = QGroupBox("Параметры двигателя")
        engine_layout = QFormLayout(engine_group)
        
        self.prm_idling_valve = QSpinBox()
        self.prm_idling_valve.setRange(0, 5000)
        self.prm_idling_valve.setValue(2000)
        self.prm_idling_valve.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Обороты отключения клапана ХХ:", self.prm_idling_valve)
        
        self.prm_pump = QSpinBox()
        self.prm_pump.setRange(0, 5000)
        self.prm_pump.setValue(100)
        self.prm_pump.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Обороты включения насоса:", self.prm_pump)
        
        self.temp_start = QSpinBox()
        self.temp_start.setRange(-20, 50)
        self.temp_start.setValue(20)
        self.temp_start.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Температура начала прогрева:", self.temp_start)
        
        self.temp_end = QSpinBox()
        self.temp_end.setRange(30, 100)
        self.temp_end.setValue(60)
        self.temp_end.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Температура конца прогрева:", self.temp_end)
        
        layout.addWidget(engine_group)
        
        # Параметры серво
        servo_group = QGroupBox("Параметры сервопривода")
        servo_layout = QFormLayout(servo_group)
        
        self.rpm_mid = QSpinBox()
        self.rpm_mid.setRange(0, 5000)
        self.rpm_mid.setValue(13)
        self.rpm_mid.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Обороты прогрева:", self.rpm_mid)
        
        self.angle_max = QSpinBox()
        self.angle_max.setRange(0, 180)
        self.angle_max.setValue(120)
        self.angle_max.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Максимальный угол:", self.angle_max)
        
        self.rpm_mid1 = QSpinBox()
        self.rpm_mid1.setRange(0, 5000)
        self.rpm_mid1.setValue(1400)
        self.rpm_mid1.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Верхняя граница оборотов:", self.rpm_mid1)
        
        self.rpm_mid2 = QSpinBox()
        self.rpm_mid2.setRange(0, 5000)
        self.rpm_mid2.setValue(1200)
        self.rpm_mid2.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Нижняя граница оборотов:", self.rpm_mid2)
        
        layout.addWidget(servo_group)
        
        # Калибровка напряжения
        voltage_group = QGroupBox("Калибровка напряжения")
        voltage_layout = QFormLayout(voltage_group)
        
        self.v_correction = QSpinBox()
        self.v_correction.setRange(0, 1000)
        self.v_correction.setValue(320)
        self.v_correction.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        voltage_layout.addRow("Коррекция вольтметра:", self.v_correction)
        
        layout.addWidget(voltage_group)
        
        # Информация
        info_label = QLabel(
            "Внимание! Измененные параметры будут отправлены в контроллер\n"
            "и сохранены в его энергонезависимой памяти (EEPROM).\n"
            "Это может повлиять на работу двигателя."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("background-color: #2a2a3a; padding: 10px; border-radius: 4px; color: #ffffff;")
        layout.addWidget(info_label)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

class InfernoGauge(QWidget):
    def __init__(self, title, min_val, max_val, unit=""):
        super().__init__()
        self.title = title
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.value = min_val
        self.setMinimumSize(140, 140)
        
    def setValue(self, value):
        self.value = max(self.min_val, min(self.max_val, value))
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Темный фон
        painter.fillRect(self.rect(), QColor(25, 25, 35))
        
        width = self.width()
        height = self.height()
        size = min(width, height) - 20
        x = (width - size) // 2
        y = (height - size) // 2
        
        # Рисуем дугу фона
        pen = QPen(QColor(60, 60, 80))
        pen.setWidth(8)
        painter.setPen(pen)
        painter.drawArc(x, y, size, size, 30 * 16, 300 * 16)
        
        # Вычисляем угол для значения
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        angle = 30 + (300 * ratio)
        
        # Рисуем индикатор
        pen = QPen(QColor(255, 150, 0))
        pen.setWidth(8)
        painter.setPen(pen)
        painter.drawArc(x, y, size, size, 30 * 16, int(angle - 30) * 16)
        
        # Текст значения
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        value_text = f"{self.value:.1f}{self.unit}"
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, value_text)
        
        # Заголовок
        painter.setFont(QFont("Arial", 10, QFont.Weight.Normal))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(0, 15, width, 25, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter, self.title)
        
        painter.end()

class SerialMonitor(QMainWindow):
    data_received = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        # Основные данные для отображения
        self.serial_data = {
            'Temp': 0, 'PRM': 0, 'Volt': 0, 'Fuel': 0, 'Speed': 0,
            'Throttle': 'ВЫКЛ', 'Pump': 'ВЫКЛ', 'Valve': 'ВЫКЛ',
            'ThrFactor': 1.0, 'AvgCons': 0, 'InstCons': 0, 'Range': 0,
            'Servo': 0
        }
        
        # Диагностические данные
        self.diagnostic_data = {
            'Temp1': 0, 'Temp2': 0, 'Vin_fuel': 0, 'Vfuel': 0, 'Vbat': 0,
            'RPM_impuls': 0, 'speed_counter': 0, 'A0': 0, 'A1': 0, 'A3': 0, 'A6': 0, 'A7': 0
        }
        
        # Данные калибровки системы
        self.system_calibration = {
            'PRMidlingvalve': 2000, 'PRMpump': 100, 'Tempstart': 20, 'Tempend': 60,
            'RPMmid': 13, 'Anglemax': 120, 'Vcor': 320, 'RPMmid1': 1400, 'RPMmid2': 1200
        }
        
        self.max_history = 1000
        self.history = {key: [] for key in list(self.serial_data.keys()) + list(self.diagnostic_data.keys()) 
                       if isinstance(self.serial_data.get(key, 0), (int, float)) or 
                          isinstance(self.diagnostic_data.get(key, 0), (int, float))}
        
        # Переменные для воспроизведения
        self.playback_data = None
        self.playback_index = 0
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self.playback_next)
        self.is_playing = False
        self.playback_speed = 1.0
        self.playback_loop = False
        
        # Статистика поездки
        self.max_speed = 0
        self.max_rpm = 0
        self.min_voltage = 999
        self.max_temp = 0
        self.total_distance = 0
        self.total_fuel_used = 0
        
        # Загрузка калибровочных данных
        self.calibration_data = self.load_calibration()
        
        # Создаем папку для данных если не существует
        self.data_dir = self.get_data_directory()
        
        self.init_serial()
        self.init_ui()
        
    def get_data_directory(self):
        """Получает путь к папке для сохранения данных"""
        # Папка рядом со скриптом
        script_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(script_dir, "car_data")
        
        # Создаем папку если не существует
        if not os.path.exists(data_dir):
            try:
                os.makedirs(data_dir)
                print(f"Создана папка для данных: {data_dir}")
            except Exception as e:
                print(f"Ошибка создания папки: {e}")
                # Если не удалось создать, используем папку скрипта
                data_dir = script_dir
        
        return data_dir
        
    def load_calibration(self):
        """Загрузка калибровочных данных из файла"""
        try:
            calibration_file = os.path.join(self.get_data_directory(), 'calibration.json')
            if os.path.exists(calibration_file):
                with open(calibration_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Загружаем калибровку системы если есть
                    if 'system_calibration' in data:
                        self.system_calibration.update(data['system_calibration'])
                    return data
        except Exception as e:
            print(f"Ошибка загрузки калибровки: {e}")
            
        return {
            'V_EMPTY': 2.07,
            'V_FULL': 2.48,
            'TANK_CAPACITY': 40.0,
            'R1': 4700.0,
            'R2': 1000.0
        }
        
    def save_calibration(self):
        """Сохранение калибровочных данных в файл"""
        try:
            calibration_file = os.path.join(self.data_dir, 'calibration.json')
            data = {
                'V_EMPTY': self.calibration_data['V_EMPTY'],
                'V_FULL': self.calibration_data['V_FULL'],
                'TANK_CAPACITY': self.calibration_data['TANK_CAPACITY'],
                'R1': self.calibration_data['R1'],
                'R2': self.calibration_data['R2'],
                'system_calibration': self.system_calibration
            }
            with open(calibration_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Ошибка сохранения калибровки: {e}")
            return False

    def create_backup(self):
        """Создание резервной копии калибровочных данных"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.data_dir, f'calibration_backup_{timestamp}.json')
            
            data = {
                'V_EMPTY': self.calibration_data['V_EMPTY'],
                'V_FULL': self.calibration_data['V_FULL'],
                'TANK_CAPACITY': self.calibration_data['TANK_CAPACITY'],
                'R1': self.calibration_data['R1'],
                'R2': self.calibration_data['R2'],
                'system_calibration': self.system_calibration,
                'backup_timestamp': datetime.now().isoformat()
            }
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Создана резервная копия: {os.path.basename(backup_file)}")
            return True
        except Exception as e:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка создания резервной копии: {str(e)}")
            return False
        
    def init_serial(self):
        self.ser = None
        try:
            for port in ['COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9']:
                try:
                    self.ser = serial.Serial(port, COM_SPEED, timeout=1)
                    print(f"Открыт последовательный порт {port}")
                    break
                except:
                    continue
            if not self.ser:
                print("Последовательный порт не найден")
        except Exception as e:
            print(f"Ошибка открытия порта: {e}")
            
    def send_calibration_data(self):
        """Отправка калибровочных данных в Arduino"""
        if not self.ser or not self.ser.is_open:
            QMessageBox.warning(self, "Ошибка", "Нет подключения к контроллеру")
            return False
            
        try:
            # Создаем резервную копию перед отправкой
            self.create_backup()
            
            # Формируем команду калибровки - БЕЗ ПРОБЕЛОВ в JSON
            cal_data = {
                'PRMidlingvalve': self.system_calibration['PRMidlingvalve'],
                'PRMpump': self.system_calibration['PRMpump'],
                'Tempstart': self.system_calibration['Tempstart'],
                'Tempend': self.system_calibration['Tempend'],
                'RPMmid': self.system_calibration['RPMmid'],
                'Anglemax': self.system_calibration['Anglemax'],
                'Vcor': self.system_calibration['Vcor'],
                'RPMmid1': self.system_calibration['RPMmid1'],
                'RPMmid2': self.system_calibration['RPMmid2']
            }
            
            # Формируем JSON без пробелов для Arduino
            json_str = json.dumps(cal_data, separators=(',', ':'))
            command = f"CALIBRATE:{json_str}\n"
            
            print(f"Отправка команды: {command}")  # Для отладки
            
            self.ser.write(command.encode('utf-8'))
            self.ser.flush()  # Убедимся, что данные отправлены
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Отправлены калибровочные данные")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] JSON: {json_str}")
            return True
        except Exception as e:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка отправки калибровки: {str(e)}")
            return False
            
    def init_ui(self):
        self.setWindowTitle("Мониторинг автомобиля - Inferno Dark")
        self.setGeometry(50, 50, 1400, 900)
        
        self.set_dark_theme()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Верхняя панель управления
        control_panel = QHBoxLayout()
        control_panel.setSpacing(10)
        
        # Левая часть - индикатор режима
        mode_group = QGroupBox("Режим работы")
        mode_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                font-size: 11px;
                background-color: #2a2a3a;
            }
        """)
        mode_group.setFixedHeight(70)
        mode_layout = QHBoxLayout(mode_group)
        mode_layout.setContentsMargins(10, 5, 10, 5)
        
        self.mode_indicator = QLabel("●")
        self.mode_indicator.setStyleSheet("color: #ff4444; font-size: 20px; font-weight: bold;")
        self.mode_indicator.setFixedWidth(20)
        mode_layout.addWidget(self.mode_indicator)
        
        self.mode_label = QLabel("Режим: Реальное время")
        self.mode_label.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        mode_layout.addWidget(self.mode_label)
        
        mode_layout.addStretch()
        
        self.connection_status = QLabel("Подключение: Нет")
        self.connection_status.setStyleSheet("color: #ff4444; font-size: 11px;")
        mode_layout.addWidget(self.connection_status)
        
        control_panel.addWidget(mode_group)
        
        # Центральная часть - управление воспроизведением
        playback_group = QGroupBox("Воспроизведение записей")
        playback_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
                font-size: 11px;
                background-color: #2a2a3a;
            }
        """)
        playback_group.setFixedHeight(70)
        playback_layout = QHBoxLayout(playback_group)
        playback_layout.setContentsMargins(10, 5, 10, 5)
        
        # Кнопка выбора файла
        self.file_button = QPushButton("Выбрать файл...")
        self.file_button.setFixedWidth(120)
        self.file_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a4a;
                color: white;
                border: 1px solid #555;
                padding: 6px;
                border-radius: 3px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
                border: 1px solid #666;
            }
            QPushButton:pressed {
                background-color: #2a2a3a;
            }
        """)
        self.file_button.clicked.connect(self.select_playback_file)
        playback_layout.addWidget(self.file_button)
        
        # Отображение выбранного файла с прогресс-баром
        file_progress_container = QWidget()
        file_progress_container.setFixedWidth(250)
        file_progress_layout = QVBoxLayout(file_progress_container)
        file_progress_layout.setContentsMargins(0, 0, 0, 0)
        file_progress_layout.setSpacing(2)
        
        self.file_label = QLabel("Файл не выбран")
        self.file_label.setStyleSheet("color: #ffffff; font-size: 9px;")
        self.file_label.setMinimumHeight(12)
        file_progress_layout.addWidget(self.file_label)
        
        self.playback_progress = QProgressBar()
        self.playback_progress.setRange(0, 100)
        self.playback_progress.setValue(0)
        self.playback_progress.setStyleSheet("""
            QProgressBar {
                background-color: #252535;
                color: white;
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
                font-size: 9px;
                height: 16px;
            }
            QProgressBar::chunk {
                background-color: #ff6b00;
                border-radius: 2px;
            }
        """)
        self.playback_progress.setTextVisible(False)
        file_progress_layout.addWidget(self.playback_progress)
        
        playback_layout.addWidget(file_progress_container)
        
        # Выбор скорости
        playback_layout.addWidget(QLabel("Скорость:"))
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.5x", "1x (реальное время)", "2x", "5x", "10x"])
        self.speed_combo.setCurrentIndex(1)
        self.speed_combo.setStyleSheet("""
            QComboBox {
                background-color: #2a2a3a;
                color: white;
                border: 1px solid #555;
                padding: 4px;
                border-radius: 3px;
                font-size: 10px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 1px solid #555;
                padding-left: 5px;
            }
        """)
        self.speed_combo.setFixedWidth(120)
        playback_layout.addWidget(self.speed_combo)
        
        # Чекбокс зацикливания
        self.loop_cb = QCheckBox("Зациклить")
        self.loop_cb.setStyleSheet("QCheckBox { color: #ffffff; font-size: 10px; }")
        playback_layout.addWidget(self.loop_cb)
        
        # Кнопки управления воспроизведением
        self.play_btn = QPushButton("Воспроизвести")
        self.play_btn.setFixedWidth(90)
        self.play_btn.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
            QPushButton:disabled {
                background-color: #335533;
                color: #888888;
            }
        """)
        self.play_btn.clicked.connect(self.start_playback)
        playback_layout.addWidget(self.play_btn)
        
        self.pause_btn = QPushButton("Пауза")
        self.pause_btn.setFixedWidth(70)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffaa00;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #ffcc00;
            }
            QPushButton:disabled {
                background-color: #555533;
                color: #888888;
            }
        """)
        self.pause_btn.clicked.connect(self.pause_playback)
        playback_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("Стоп")
        self.stop_btn.setFixedWidth(70)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                padding: 6px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
            QPushButton:disabled {
                background-color: #553333;
                color: #888888;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_playback)
        playback_layout.addWidget(self.stop_btn)
        
        control_panel.addWidget(playback_group, 1)
        control_panel.addStretch()
        
        layout.addLayout(control_panel)
        
        # Создаем вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #252535;
                border-radius: 4px;
            }
            QTabBar::tab {
                background-color: #2a2a3a;
                color: #ffffff;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
                border: 1px solid #444;
            }
            QTabBar::tab:selected {
                background-color: #ff6b00;
                color: #000000;
                border: 1px solid #ff8c00;
            }
            QTabBar::tab:hover {
                background-color: #3a3a4a;
            }
        """)
        layout.addWidget(tabs)
        
        # Вкладка приборной панели
        dashboard_tab = QWidget()
        tabs.addTab(dashboard_tab, "Приборная панель")
        self.setup_dashboard(dashboard_tab)
        
        # Вкладка расширенных графиков
        advanced_charts_tab = QWidget()
        tabs.addTab(advanced_charts_tab, "Расширенные графики")
        self.setup_advanced_charts_tab(advanced_charts_tab)
        
        # Вкладка диагностики
        diagnostics_tab = QWidget()
        tabs.addTab(diagnostics_tab, "Диагностика")
        self.setup_diagnostics_tab(diagnostics_tab)
        
        # Вкладка калибровки системы
        calibration_tab = QWidget()
        tabs.addTab(calibration_tab, "Калибровка системы")
        self.setup_calibration_tab(calibration_tab)
        
        # Вкладка настройки
        settings_tab = QWidget()
        tabs.addTab(settings_tab, "Настройки")
        self.setup_settings_tab(settings_tab)
        
        # Таймер для чтения данных
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_serial_data)
        self.timer.start(100)
        
        # Таймер для обновления статуса подключения
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_connection_status)
        self.status_timer.start(2000)
        
    def setup_calibration_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Основная группа калибровки системы
        main_cal_group = QGroupBox("Калибровка параметров системы")
        main_cal_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                font-size: 13px;
                background-color: #2a2a3a;
            }
        """)
        main_cal_layout = QVBoxLayout(main_cal_group)
        
        # Контейнер для параметров в две колонки
        params_container = QWidget()
        params_layout = QHBoxLayout(params_container)
        params_layout.setSpacing(20)
        
        # Левая колонка - параметры двигателя
        left_column = QWidget()
        left_layout = QVBoxLayout(left_column)
        left_layout.setSpacing(10)
        
        # Двигатель
        engine_group = QGroupBox("Двигатель")
        engine_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 10px;
                font-size: 11px;
                background-color: #2a2a3a;
            }
        """)
        engine_layout = QFormLayout(engine_group)
        engine_layout.setVerticalSpacing(8)
        engine_layout.setHorizontalSpacing(15)
        
        self.cal_prm_idling_valve = QSpinBox()
        self.cal_prm_idling_valve.setRange(0, 5000)
        self.cal_prm_idling_valve.setValue(self.system_calibration['PRMidlingvalve'])
        self.cal_prm_idling_valve.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Обороты откл. клапана ХХ:", self.cal_prm_idling_valve)
        
        self.cal_prm_pump = QSpinBox()
        self.cal_prm_pump.setRange(0, 5000)
        self.cal_prm_pump.setValue(self.system_calibration['PRMpump'])
        self.cal_prm_pump.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Обороты вкл. насоса:", self.cal_prm_pump)
        
        self.cal_temp_start = QSpinBox()
        self.cal_temp_start.setRange(-20, 50)
        self.cal_temp_start.setValue(self.system_calibration['Tempstart'])
        self.cal_temp_start.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Темп. начала прогрева:", self.cal_temp_start)
        
        self.cal_temp_end = QSpinBox()
        self.cal_temp_end.setRange(30, 100)
        self.cal_temp_end.setValue(self.system_calibration['Tempend'])
        self.cal_temp_end.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        engine_layout.addRow("Темп. конца прогрева:", self.cal_temp_end)
        
        left_layout.addWidget(engine_group)
        
        # Напряжение
        voltage_group = QGroupBox("Напряжение")
        voltage_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 10px;
                font-size: 11px;
                background-color: #2a2a3a;
            }
        """)
        voltage_layout = QFormLayout(voltage_group)
        voltage_layout.setVerticalSpacing(8)
        
        self.cal_v_correction = QSpinBox()
        self.cal_v_correction.setRange(0, 1000)
        self.cal_v_correction.setValue(self.system_calibration['Vcor'])
        self.cal_v_correction.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        voltage_layout.addRow("Коррекция вольтметра:", self.cal_v_correction)
        
        left_layout.addWidget(voltage_group)
        left_layout.addStretch()
        
        # Правая колонка - параметры серво
        right_column = QWidget()
        right_layout = QVBoxLayout(right_column)
        right_layout.setSpacing(10)
        
        servo_group = QGroupBox("Сервопривод")
        servo_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 1px solid #555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 10px;
                font-size: 11px;
                background-color: #2a2a3a;
            }
        """)
        servo_layout = QFormLayout(servo_group)
        servo_layout.setVerticalSpacing(8)
        servo_layout.setHorizontalSpacing(15)
        
        self.cal_rpm_mid = QSpinBox()
        self.cal_rpm_mid.setRange(0, 5000)
        self.cal_rpm_mid.setValue(self.system_calibration['RPMmid'])
        self.cal_rpm_mid.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Обороты прогрева:", self.cal_rpm_mid)
        
        self.cal_angle_max = QSpinBox()
        self.cal_angle_max.setRange(0, 180)
        self.cal_angle_max.setValue(self.system_calibration['Anglemax'])
        self.cal_angle_max.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Максимальный угол:", self.cal_angle_max)
        
        self.cal_rpm_mid1 = QSpinBox()
        self.cal_rpm_mid1.setRange(0, 5000)
        self.cal_rpm_mid1.setValue(self.system_calibration['RPMmid1'])
        self.cal_rpm_mid1.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Верхняя граница:", self.cal_rpm_mid1)
        
        self.cal_rpm_mid2 = QSpinBox()
        self.cal_rpm_mid2.setRange(0, 5000)
        self.cal_rpm_mid2.setValue(self.system_calibration['RPMmid2'])
        self.cal_rpm_mid2.setStyleSheet("background-color: #2a2a3a; color: #ffffff; border: 1px solid #555; border-radius: 3px; padding: 5px;")
        servo_layout.addRow("Нижняя граница:", self.cal_rpm_mid2)
        
        right_layout.addWidget(servo_group)
        right_layout.addStretch()
        
        params_layout.addWidget(left_column)
        params_layout.addWidget(right_column)
        
        main_cal_layout.addWidget(params_container)
        layout.addWidget(main_cal_group)
        
        # Калибровка датчика топлива
        fuel_cal_group = QGroupBox("Калибровка датчика топлива")
        fuel_cal_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 12px;
                font-size: 13px;
                background-color: #2a2a3a;
            }
        """)
        fuel_cal_layout = QHBoxLayout(fuel_cal_group)
        
        fuel_cal_info = QLabel(
            "Калибровка датчика уровня топлива позволяет точно определить\n"
            "соответствие между напряжением датчика и количеством топлива в баке."
        )
        fuel_cal_info.setWordWrap(True)
        fuel_cal_info.setStyleSheet("color: #ffffff; font-size: 11px; background-color: #252535; padding: 10px; border-radius: 4px;")
        fuel_cal_layout.addWidget(fuel_cal_info)
        
        self.fuel_cal_btn = QPushButton("Калибровать")
        self.fuel_cal_btn.setFixedHeight(35)
        self.fuel_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b00;
                color: white;
                border: none;
                padding: 8px 20px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
        """)
        self.fuel_cal_btn.clicked.connect(self.calibrate_fuel_sensor)
        fuel_cal_layout.addWidget(self.fuel_cal_btn)
        
        layout.addWidget(fuel_cal_group)
        
        # Кнопки управления калибровкой - ПЕРЕМЕЩЕНЫ ВНИЗ
        cal_buttons_layout = QHBoxLayout()
        cal_buttons_layout.setSpacing(15)
        
        self.load_cal_btn = QPushButton("Загрузить текущие")
        self.load_cal_btn.setFixedHeight(35)
        self.load_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a3a4a;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #4a4a5a;
            }
        """)
        self.load_cal_btn.clicked.connect(self.load_current_calibration)
        cal_buttons_layout.addWidget(self.load_cal_btn)
        
        self.save_cal_btn = QPushButton("Сохранить локально")
        self.save_cal_btn.setFixedHeight(35)
        self.save_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0088ff;
            }
        """)
        self.save_cal_btn.clicked.connect(self.save_system_calibration)
        cal_buttons_layout.addWidget(self.save_cal_btn)
        
        self.send_cal_btn = QPushButton("Отправить в контроллер")
        self.send_cal_btn.setFixedHeight(35)
        self.send_cal_btn.setStyleSheet("""
            QPushButton {
                background-color: #00aa00;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #00cc00;
            }
        """)
        self.send_cal_btn.clicked.connect(self.send_system_calibration)
        cal_buttons_layout.addWidget(self.send_cal_btn)
        
        cal_buttons_layout.addStretch()
        layout.addLayout(cal_buttons_layout)
        
    def load_current_calibration(self):
        """Загрузка текущих значений калибровки в поля ввода"""
        self.cal_prm_idling_valve.setValue(self.system_calibration['PRMidlingvalve'])
        self.cal_prm_pump.setValue(self.system_calibration['PRMpump'])
        self.cal_temp_start.setValue(self.system_calibration['Tempstart'])
        self.cal_temp_end.setValue(self.system_calibration['Tempend'])
        self.cal_rpm_mid.setValue(self.system_calibration['RPMmid'])
        self.cal_angle_max.setValue(self.system_calibration['Anglemax'])
        self.cal_v_correction.setValue(self.system_calibration['Vcor'])
        self.cal_rpm_mid1.setValue(self.system_calibration['RPMmid1'])
        self.cal_rpm_mid2.setValue(self.system_calibration['RPMmid2'])
        
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Текущие параметры калибровки загружены в форму")
        
    def save_system_calibration(self):
        """Сохранение параметров калибровки системы"""
        self.system_calibration.update({
            'PRMidlingvalve': self.cal_prm_idling_valve.value(),
            'PRMpump': self.cal_prm_pump.value(),
            'Tempstart': self.cal_temp_start.value(),
            'Tempend': self.cal_temp_end.value(),
            'RPMmid': self.cal_rpm_mid.value(),
            'Anglemax': self.cal_angle_max.value(),
            'Vcor': self.cal_v_correction.value(),
            'RPMmid1': self.cal_rpm_mid1.value(),
            'RPMmid2': self.cal_rpm_mid2.value()
        })
        
        if self.save_calibration():
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Параметры калибровки сохранены локально")
            QMessageBox.information(self, "Успех", "Параметры калибровки сохранены локально!")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить параметры калибровки")
            
    def send_system_calibration(self):
        """Отправка параметров калибровки в контроллер"""
        
        # Логируем отправляемые данные для отладки
        cal_data = {
            'PRMidlingvalve': self.cal_prm_idling_valve.value(),
            'PRMpump': self.cal_prm_pump.value(),
            'Tempstart': self.cal_temp_start.value(),
            'Tempend': self.cal_temp_end.value(),
            'RPMmid': self.cal_rpm_mid.value(),
            'Anglemax': self.cal_angle_max.value(),
            'Vcor': self.cal_v_correction.value(),
            'RPMmid1': self.cal_rpm_mid1.value(),
            'RPMmid2': self.cal_rpm_mid2.value()
        }
        
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Отправка данных: {cal_data}")
        
        # Затем отправляем в контроллер
        if self.send_calibration_data():
            QMessageBox.information(self, "Успех", 
                                  "Параметры калибровки отправлены в контроллер!\n"
                                  "Создана резервная копия параметров.")
        else:
            QMessageBox.warning(self, "Ошибка", "Не удалось отправить параметры калибровки")

    # ... (остальные методы остаются без изменений)

    def select_playback_file(self):
        """Открытие диалога выбора файла"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Выберите файл для воспроизведения", 
            self.data_dir,  # Начинаем с папки данных
            "JSON Files (*.json);;All Files (*)"
        )
        
        if filename:
            self.selected_playback_file = filename
            # Показываем только имя файла
            file_name = os.path.basename(filename)
            self.file_label.setText(file_name)
            self.file_label.setToolTip(filename)
            self.playback_progress.setValue(0)
    
    def set_dark_theme(self):
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(25, 25, 35))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(35, 35, 45))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 45, 55))
        dark_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.Button, QColor(60, 60, 80))
        dark_palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 100, 0))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(255, 150, 0))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        
        self.setPalette(dark_palette)
        
    def update_connection_status(self):
        """Обновление статуса подключения"""
        if self.is_playing:
            status_text = "Воспроизведение"
            status_color = "#00ff00"
            indicator_color = "#00ff00"
        elif self.ser and self.ser.is_open:
            status_text = "Подключено"
            status_color = "#00ff00"
            indicator_color = "#00ff00"
        else:
            status_text = "Нет подключения"
            status_color = "#ff4444"
            indicator_color = "#ff4444"
            
        self.connection_status.setText(f"Подключение: {status_text}")
        self.connection_status.setStyleSheet(f"color: {status_color}; font-size: 11px;")
        self.mode_indicator.setStyleSheet(f"color: {indicator_color}; font-size: 20px; font-weight: bold;")
        
    def start_playback(self):
        """Начало воспроизведения выбранного файла"""
        if not hasattr(self, 'selected_playback_file') or not self.selected_playback_file:
            QMessageBox.warning(self, "Ошибка", "Выберите файл для воспроизведения")
            return
        
        try:
            with open(self.selected_playback_file, 'r', encoding='utf-8') as f:
                self.playback_data = json.load(f)
            
            # Определяем скорость воспроизведения
            speed_text = self.speed_combo.currentText()
            speed_map = {"0.5x": 0.5, "1x (реальное время)": 1.0, "2x": 2.0, "5x": 5.0, "10x": 10.0}
            self.playback_speed = speed_map[speed_text]
            
            # Настройка зацикливания
            self.playback_loop = self.loop_cb.isChecked()
            
            self.playback_index = 0
            self.is_playing = True
            
            # Останавливаем получение реальных данных
            if self.ser and self.ser.is_open:
                self.ser.close()
            
            # Очищаем текущие данные
            for key in self.history:
                self.history[key].clear()
            
            # Настраиваем таймер воспроизведения
            interval = int(100 / self.playback_speed)  # Базовый интервал 100мс
            self.playback_timer.start(interval)
            
            # Обновляем UI
            self.mode_label.setText("Режим: Воспроизведение")
            self.play_btn.setEnabled(False)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.playback_progress.setValue(0)
            
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Начато воспроизведение: {os.path.basename(self.selected_playback_file)} (скорость: {speed_text})")
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def pause_playback(self):
        """Пауза воспроизведения"""
        if self.is_playing:
            self.playback_timer.stop()
            self.is_playing = False
            self.mode_label.setText("Режим: Пауза")
            self.play_btn.setEnabled(True)
            self.pause_btn.setEnabled(False)
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Воспроизведение приостановлено")
    
    def stop_playback(self):
        """Остановка воспроизведения"""
        self.playback_timer.stop()
        self.is_playing = False
        self.playback_data = None
        self.playback_index = 0
        
        # Возвращаемся к реальному времени
        self.init_serial()
        self.mode_label.setText("Режим: Реальное время")
        self.play_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.playback_progress.setValue(0)
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Воспроизведение остановлено")
    
    def playback_next(self):
        """Обработка следующей точки данных при воспроизведении"""
        if not self.playback_data or 'history' not in self.playback_data:
            self.stop_playback()
            return
        
        history_data = self.playback_data['history']
        if self.playback_index >= len(history_data):
            if self.playback_loop:
                self.playback_index = 0  # Начинаем заново
                self.playback_progress.setValue(0)
                self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Воспроизведение зациклено")
            else:
                self.stop_playback()
                return
        
        # Получаем следующую точку данных
        data_point = history_data[self.playback_index]
        
        # Обновляем данные
        for key, value in data_point.items():
            if key in self.serial_data:
                if key in ['Throttle', 'Pump', 'Valve']:
                    self.serial_data[key] = 'ВКЛ' if value == 'ON' else 'ВЫКЛ'
                else:
                    self.serial_data[key] = value
            elif key in self.diagnostic_data:
                self.diagnostic_data[key] = value
        
        # Обновляем прогресс
        if len(history_data) > 0:
            progress = int((self.playback_index / len(history_data)) * 100)
            self.playback_progress.setValue(progress)
        
        # Обновляем отображение
        self.update_display()
        
        self.playback_index += 1

    def setup_dashboard(self, parent):
        layout = QGridLayout(parent)
        layout.setSpacing(15)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Основные приборы
        self.temp_gauge = InfernoGauge("Температура двигателя", 0, 120, "°C")
        self.rpm_gauge = InfernoGauge("Обороты двигателя", 0, 8000, " об/мин")
        self.voltage_gauge = InfernoGauge("Напряжение сети", 0, 15, "В")
        self.fuel_gauge = InfernoGauge("Уровень топлива", 0, 40, "л")
        self.speed_gauge = InfernoGauge("Скорость", 0, 200, "км/ч")
        self.consumption_gauge = InfernoGauge("Средний расход", 0, 20, "л/100км")
        
        layout.addWidget(self.temp_gauge, 0, 0)
        layout.addWidget(self.rpm_gauge, 0, 1)
        layout.addWidget(self.voltage_gauge, 0, 2)
        layout.addWidget(self.fuel_gauge, 1, 0)
        layout.addWidget(self.speed_gauge, 1, 1)
        layout.addWidget(self.consumption_gauge, 1, 2)
        
        # Панель статусов системы
        status_group = QGroupBox("Статус системы")
        status_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        status_layout = QGridLayout(status_group)
        status_layout.setVerticalSpacing(8)
        status_layout.setHorizontalSpacing(10)
        
        self.status_labels = {}
        status_params = [
            ('Дроссель', 'ВЫКЛ'), ('Топливный насос', 'ВЫКЛ'), 
            ('Клапан ХХ', 'ВЫКЛ'), ('Коэф. дросселя', '1.0'),
            ('Запас хода', '0 км'), ('Мгновенный расход', '0.0 л/100км')
        ]
        
        for i, (name, default) in enumerate(status_params):
            label_name = QLabel(f"{name}:")
            label_name.setStyleSheet("color: #ffffff; font-size: 11px;")
            label_name.setMinimumHeight(25)
            
            label_value = QLabel(default)
            label_value.setStyleSheet("""
                QLabel {
                    background-color: #252535;
                    border: 2px solid #444;
                    border-radius: 5px;
                    padding: 6px;
                    font-weight: bold;
                    color: #ff9600;
                    font-size: 11px;
                    min-width: 80px;
                }
            """)
            label_value.setMinimumHeight(25)
            label_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            row = i // 2
            col = (i % 2) * 2
            status_layout.addWidget(label_name, row, col)
            status_layout.addWidget(label_value, row, col + 1)
            self.status_labels[name] = label_value
        
        layout.addWidget(status_group, 2, 0, 1, 3)
        
    def setup_advanced_charts_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Настраиваем тему pyqtgraph
        pg.setConfigOption('background', (25, 25, 35))
        pg.setConfigOption('foreground', 'w')
        
        # Создаем виджет с вкладками для графиков
        chart_tabs = QTabWidget()
        chart_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #444;
                background-color: #252535;
            }
            QTabBar::tab {
                background-color: #2a2a3a;
                color: #ffffff;
                padding: 6px 12px;
                margin: 1px;
                border-radius: 3px;
                font-size: 10px;
            }
            QTabBar::tab:selected {
                background-color: #ff6b00;
                color: #000000;
            }
        """)
        
        # Вкладка температур с улучшенной визуализацией
        temp_tab = QWidget()
        temp_layout = QVBoxLayout(temp_tab)
        
        temp_widget = pg.PlotWidget()
        temp_widget.setTitle("Мониторинг температур системы", color='w', size='12pt')
        temp_widget.setLabel('left', 'Температура (°C)', color='#ffffff')
        temp_widget.setLabel('bottom', 'Время (секунды)', color='#ffffff')
        temp_widget.addLegend()
        temp_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Добавляем зоны температур для двигателя
        temp_widget.addItem(pg.LinearRegionItem([0, 60], brush=pg.mkBrush((0, 100, 0, 50)), movable=False))
        temp_widget.addItem(pg.LinearRegionItem([60, 90], brush=pg.mkBrush((255, 255, 0, 30)), movable=False))
        temp_widget.addItem(pg.LinearRegionItem([90, 120], brush=pg.mkBrush((255, 0, 0, 20)), movable=False))
        
        self.temp_engine_curve = temp_widget.plot(pen=pg.mkPen(color='#ff5500', width=3), name='Двигатель')
        self.temp_air_curve = temp_widget.plot(pen=pg.mkPen(color='#00aaff', width=2), name='Воздух')
        self.temp_cabin_curve = temp_widget.plot(pen=pg.mkPen(color='#00ff88', width=2), name='Салон')
        
        temp_layout.addWidget(temp_widget)
        chart_tabs.addTab(temp_tab, "Температуры")
        
        # Вкладка двигателя
        engine_tab = QWidget()
        engine_layout = QVBoxLayout(engine_tab)
        
        engine_widget = pg.PlotWidget()
        engine_widget.setTitle("Параметры двигателя", color='w', size='12pt')
        engine_widget.setLabel('left', 'Значения', color='#ffffff')
        engine_widget.setLabel('bottom', 'Время (секунды)', color='#ffffff')
        engine_widget.addLegend()
        engine_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.rpm_curve = engine_widget.plot(pen=pg.mkPen(color='#ffaa00', width=2), name='Обороты (RPM)')
        self.servo_curve = engine_widget.plot(pen=pg.mkPen(color='#ff00ff', width=2), name='Положение серво')
        self.throttle_factor_curve = engine_widget.plot(pen=pg.mkPen(color='#00ffff', width=2), name='Коэф. дросселя')
        
        engine_layout.addWidget(engine_widget)
        chart_tabs.addTab(engine_tab, "Двигатель")
        
        # Вкладка скорости и расхода
        speed_cons_tab = QWidget()
        speed_cons_layout = QVBoxLayout(speed_cons_tab)
        
        speed_cons_widget = pg.PlotWidget()
        speed_cons_widget.setTitle("Динамика движения", color='w', size='12pt')
        speed_cons_widget.setLabel('left', 'Значения', color='#ffffff')
        speed_cons_widget.setLabel('bottom', 'Время (секунды)', color='#ffffff')
        speed_cons_widget.addLegend()
        speed_cons_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.speed_curve = speed_cons_widget.plot(pen=pg.mkPen(color='#0088ff', width=3), name='Скорость (км/ч)')
        self.avg_consumption_curve = speed_cons_widget.plot(pen=pg.mkPen(color='#ff4444', width=2), name='Ср. расход (л/100км)')
        self.inst_consumption_curve = speed_cons_widget.plot(pen=pg.mkPen(color='#ffaa00', width=2), name='Мгн. расход (л/100км)')
        
        speed_cons_layout.addWidget(speed_cons_widget)
        chart_tabs.addTab(speed_cons_tab, "Движение")
        
        # Вкладка топлива и напряжения
        fuel_volt_tab = QWidget()
        fuel_volt_layout = QVBoxLayout(fuel_volt_tab)
        
        fuel_volt_widget = pg.PlotWidget()
        fuel_volt_widget.setTitle("Топливо и электрика", color='w', size='12pt')
        fuel_volt_widget.setLabel('left', 'Значения', color='#ffffff')
        fuel_volt_widget.setLabel('bottom', 'Время (секунды)', color='#ffffff')
        fuel_volt_widget.addLegend()
        fuel_volt_widget.showGrid(x=True, y=True, alpha=0.3)
        
        self.fuel_curve = fuel_volt_widget.plot(pen=pg.mkPen(color='#ffff00', width=3), name='Топливо (л)')
        self.voltage_curve = fuel_volt_widget.plot(pen=pg.mkPen(color='#00ff00', width=2), name='Напряжение (В)')
        
        fuel_volt_layout.addWidget(fuel_volt_widget)
        chart_tabs.addTab(fuel_volt_tab, "Топливо")
        
        layout.addWidget(chart_tabs)
        
    def setup_diagnostics_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Диагностика работы систем
        diag_group = QGroupBox("Диагностика систем")
        diag_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        diag_layout = QGridLayout(diag_group)
        diag_layout.setVerticalSpacing(8)
        diag_layout.setHorizontalSpacing(10)
        
        # Прогресс-бары для ключевых параметров
        self.rpm_bar = QProgressBar()
        self.rpm_bar.setMaximum(8000)
        self.rpm_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #252535;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #ff5500;
            }
        """)
        diag_layout.addWidget(QLabel("Обороты двигателя:"), 0, 0)
        diag_layout.addWidget(self.rpm_bar, 0, 1)
        
        self.temp_bar = QProgressBar()
        self.temp_bar.setMaximum(120)
        self.temp_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #252535;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #ff0000;
            }
        """)
        diag_layout.addWidget(QLabel("Температура двигателя:"), 1, 0)
        diag_layout.addWidget(self.temp_bar, 1, 1)
        
        self.fuel_bar = QProgressBar()
        self.fuel_bar.setMaximum(100)
        self.fuel_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #252535;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #ffff00;
            }
        """)
        diag_layout.addWidget(QLabel("Уровень топлива:"), 2, 0)
        diag_layout.addWidget(self.fuel_bar, 2, 1)
        
        self.voltage_bar = QProgressBar()
        self.voltage_bar.setMaximum(150)
        self.voltage_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 5px;
                text-align: center;
                color: white;
                background-color: #252535;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)
        diag_layout.addWidget(QLabel("Напряжение сети:"), 3, 0)
        diag_layout.addWidget(self.voltage_bar, 3, 1)
        
        layout.addWidget(diag_group)
        
        # Дополнительные диагностические данные
        additional_group = QGroupBox("Дополнительные параметры")
        additional_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        additional_layout = QGridLayout(additional_group)
        additional_layout.setVerticalSpacing(6)
        additional_layout.setHorizontalSpacing(15)
        
        self.diagnostic_labels = {}
        diagnostic_params = [
            ('Температура воздуха', '0°C'), ('Температура салона', '0°C'),
            ('Напряжение датчика', '0.0 В'), ('Напряжение Vbat', '0.0 В'),
            ('Счетчик RPM', '0'), ('Счетчик скорости', '0'),
            ('A0 (Топливо)', '0'), ('A1 (Напряжение)', '0'),
            ('A3 (Салон)', '0'), ('A6 (Воздух)', '0'), ('A7 (Двигатель)', '0')
        ]
        
        for i, (name, default) in enumerate(diagnostic_params):
            label_name = QLabel(f"{name}:")
            label_name.setStyleSheet("color: #ffffff; font-size: 11px;")
            label_name.setMinimumHeight(20)
            
            label_value = QLabel(default)
            label_value.setStyleSheet("color: #ff9600; font-weight: bold; font-size: 11px; background-color: #252535; padding: 4px; border-radius: 3px;")
            label_value.setMinimumHeight(20)
            label_value.setMinimumWidth(80)
            
            row = i // 2
            col = (i % 2) * 2
            additional_layout.addWidget(label_name, row, col)
            additional_layout.addWidget(label_value, row, col + 1)
            self.diagnostic_labels[name] = label_value
        
        layout.addWidget(additional_group)
        
        # Статистика поездки
        stats_group = QGroupBox("Статистика поездки")
        stats_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        stats_layout = QGridLayout(stats_group)
        stats_layout.setVerticalSpacing(6)
        stats_layout.setHorizontalSpacing(15)
        
        self.stats_labels = {}
        stats_params = [
            ('Макс. скорость', '0 км/ч'), ('Макс. обороты', '0 об/мин'),
            ('Мин. напряжение', '0 В'), ('Макс. температура', '0°C'),
            ('Общий пробег', '0 км'), ('Общий расход', '0 л')
        ]
        
        for i, (name, default) in enumerate(stats_params):
            label_name = QLabel(f"{name}:")
            label_name.setStyleSheet("color: #ffffff; font-size: 11px;")
            label_name.setMinimumHeight(20)
            
            label_value = QLabel(default)
            label_value.setStyleSheet("color: #ff9600; font-weight: bold; font-size: 11px; background-color: #252535; padding: 4px; border-radius: 3px;")
            label_value.setMinimumHeight(20)
            label_value.setMinimumWidth(80)
            
            row = i // 2
            col = (i % 2) * 2
            stats_layout.addWidget(label_name, row, col)
            stats_layout.addWidget(label_value, row, col + 1)
            self.stats_labels[name] = label_value
        
        layout.addWidget(stats_group)
        
    def setup_settings_tab(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Кнопки управления
        control_group = QGroupBox("Управление системой")
        control_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        control_layout = QGridLayout(control_group)
        control_layout.setVerticalSpacing(10)
        control_layout.setHorizontalSpacing(10)
        
        buttons = [
            ("Калибровка датчика топлива", self.calibrate_fuel_sensor),
            ("Сброс статистики", self.reset_stats),
            ("Сохранить данные", self.save_data),
            ("Тест связи", self.test_connection),
            ("Очистить графики", self.clear_graphs),
            ("Настройка истории", self.configure_history)
        ]
        
        for i, (text, slot) in enumerate(buttons):
            btn = QPushButton(text)
            btn.setFixedHeight(35)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff6b00;
                    color: white;
                    border: none;
                    padding: 8px 12px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #ff8c00;
                }
                QPushButton:pressed {
                    background-color: #e55a00;
                }
            """)
            btn.clicked.connect(slot)
            control_layout.addWidget(btn, i//3, i%3)
            
        layout.addWidget(control_group)
        
        # Нижняя часть с настройками и информацией
        bottom_layout = QHBoxLayout()
        bottom_layout.setSpacing(15)
        
        # Настройки системы
        settings_group = QGroupBox("Настройки системы")
        settings_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        settings_layout = QFormLayout(settings_group)
        
        # Настройка размера истории
        self.history_size_label = QLabel(f"Текущий размер истории: {self.max_history} точек")
        self.history_size_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        settings_layout.addRow(self.history_size_label)
        
        # Информация о папке данных с кнопкой выбора
        folder_layout = QHBoxLayout()
        self.data_dir_label = QLabel(f"{self.data_dir}")
        self.data_dir_label.setStyleSheet("color: #ffffff; font-size: 10px; background-color: #252535; padding: 5px; border-radius: 3px;")
        self.data_dir_label.setWordWrap(True)
        self.data_dir_label.setFixedWidth(300)
        
        self.select_folder_btn = QPushButton("Выбрать")
        self.select_folder_btn.setFixedWidth(80)
        self.select_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff6b00;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                font-weight: bold;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #ff8c00;
            }
        """)
        self.select_folder_btn.clicked.connect(self.select_data_folder)
        
        folder_layout.addWidget(self.data_dir_label)
        folder_layout.addWidget(self.select_folder_btn)
        settings_layout.addRow("Папка данных:", folder_layout)
        
        # Автосохранение
        self.auto_save_cb = QCheckBox("Автоматическое сохранение данных каждые 5 минут")
        self.auto_save_cb.setStyleSheet("QCheckBox { color: #ffffff; font-size: 11px; }")
        settings_layout.addRow(self.auto_save_cb)
        
        settings_group.setFixedWidth(500)
        bottom_layout.addWidget(settings_group)
        
        # Информация о системе
        info_group = QGroupBox("Информация о системе")
        info_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        info_layout = QVBoxLayout(info_group)
        
        system_info = QLabel(
            f"Версия ПО: {version}\n"
            f"Статус подключения: {'Подключено' if (self.ser and self.ser.is_open) or self.is_playing else 'Нет подключения'}\n"
            f"Порт: {self.ser.port if self.ser and self.ser.is_open else 'Не найден'}\n"
            f"Скорость: {COM_SPEED} бод\n"
            f"Размер истории: {self.max_history} точек\n"
            f"Время обновления: 100 мс\n"
            f"Режим: {'Воспроизведение' if self.is_playing else 'Реальное время'}\n"
            f"Датчики: Температура, RPM, Топливо, Напряжение, Скорость"
        )
        system_info.setStyleSheet("color: #ffffff; font-size: 11px; background-color: #252535; padding: 10px; border-radius: 5px;")
        system_info.setWordWrap(True)
        info_layout.addWidget(system_info)
        
        info_group.setFixedWidth(500)
        bottom_layout.addWidget(info_group)
        
        layout.addLayout(bottom_layout)
        
        # Лог сообщений
        log_group = QGroupBox("Журнал системы")
        log_group.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 12px;
                background-color: #2a2a3a;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1a1a2a;
                color: #00ff88;
                border: 1px solid #444;
                border-radius: 4px;
                font-family: 'Consolas', 'Courier New';
                font-size: 9px;
                padding: 5px;
            }
        """)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
    def read_serial_data(self):
        if self.is_playing:
            return  # Не читаем из порта при воспроизведении
            
        if self.ser and self.ser.in_waiting:
            try:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                
                # Проверяем, не является ли строка ответом на калибровку
                if line.startswith("CALIBRATION_SUCCESS"):
                    self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Калибровка успешно применена в контроллере")
                elif line.startswith("CALIBRATION_ERROR"):
                    self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка калибровки в контроллере: {line}")
                elif line.startswith("CALIBRATION_RECEIVED"):
                    self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Контроллер получил данные калибровки")
                elif line.startswith("CALIBRATION_PARSING"):
                    self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                elif line.startswith("CALIBRATION_LOADED"):
                    self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] {line}")
                
                if line and any(keyword in line for keyword in ['Temp:', 'PRM:', 'Fuel:', 'Speed:']):
                    self.parse_serial_data(line)
                    if len(self.history['Temp']) % 20 == 0:
                        current_time = datetime.now().strftime('%H:%M:%S')
                        self.log_text.append(f"[{current_time}] Данные получены (точек: {len(self.history['Temp'])})")
                    if self.log_text.document().lineCount() > 50:
                        cursor = self.log_text.textCursor()
                        cursor.movePosition(cursor.MoveOperation.Start)
                        cursor.movePosition(cursor.MoveOperation.Down, cursor.MoveMode.MoveAnchor, 10)
                        cursor.movePosition(cursor.MoveOperation.End, cursor.MoveMode.KeepAnchor)
                        cursor.removeSelectedText()
            except Exception as e:
                self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] ОШИБКА: {str(e)}")
                try:
                    self.ser.close()
                except:
                    pass
                self.init_serial()
                
    def parse_serial_data(self, data):
        try:
            # Основные данные для приборной панели
            main_patterns = {
                'Temp': r'Temp:([\d.-]+)',
                'PRM': r'PRM:([\d.-]+)',
                'Volt': r'Volt:([\d.-]+)',
                'Fuel': r'Fuel:([\d.-]+)',
                'Speed': r'Speed:([\d.-]+)',
                'Servo': r'Servo:([\d.-]+)',
                'Throttle': r'Throttle:(\w+)',
                'Pump': r'Pump:(\w+)',
                'Valve': r'Valve:(\w+)',
                'ThrFactor': r'ThrFactor:([\d.-]+)',
                'AvgCons': r'AvgCons:([\d.-]+)',
                'InstCons': r'InstCons:([\d.-]+)',
                'Range': r'Range:([\d.-]+)'
            }
            
            # Диагностические данные
            diagnostic_patterns = {
                'Temp1': r'Temp1:([\d.-]+)',
                'Temp2': r'Temp2:([\d.-]+)',
                'Vin_fuel': r'Vin_fuel:([\d.-]+)',
                'Vfuel': r'Vfuel:([\d.-]+)',
                'Vbat': r'Vbat:([\d.-]+)',
                'RPM_impuls': r'RPM_impuls:([\d.-]+)',
                'speed_counter': r'speed_counter:([\d.-]+)',
                'A0': r'A0:([\d.-]+)',
                'A1': r'A1:([\d.-]+)',
                'A3': r'A3:([\d.-]+)',
                'A6': r'A6:([\d.-]+)',
                'A7': r'A7:([\d.-]+)'
            }
            
            # Парсим основные данные
            for key, pattern in main_patterns.items():
                match = re.search(pattern, data)
                if match:
                    value = match.group(1)
                    if key in ['Throttle', 'Pump', 'Valve']:
                        if value == 'ON':
                            self.serial_data[key] = 'ВКЛ'
                        else:
                            self.serial_data[key] = 'ВЫКЛ'
                    else:
                        try:
                            self.serial_data[key] = float(value)
                        except ValueError:
                            continue
            
            # Парсим диагностические данные
            for key, pattern in diagnostic_patterns.items():
                match = re.search(pattern, data)
                if match:
                    value = match.group(1)
                    try:
                        self.diagnostic_data[key] = float(value)
                    except ValueError:
                        continue
                        
            self.update_display()
            self.update_stats()
            
        except Exception as e:
            print(f"Ошибка парсинга: {e}")
            
    def update_display(self):
        # Обновляем приборы
        self.temp_gauge.setValue(self.serial_data['Temp'])
        self.rpm_gauge.setValue(self.serial_data['PRM'])
        self.voltage_gauge.setValue(self.serial_data['Volt'])
        self.fuel_gauge.setValue(self.serial_data['Fuel'])
        self.speed_gauge.setValue(self.serial_data['Speed'])
        self.consumption_gauge.setValue(self.serial_data['AvgCons'])
        
        # Обновляем прогресс-бары
        self.rpm_bar.setValue(int(self.serial_data['PRM']))
        self.rpm_bar.setFormat(f"{self.serial_data['PRM']:.0f} об/мин")
        
        self.temp_bar.setValue(int(self.serial_data['Temp']))
        self.temp_bar.setFormat(f"{self.serial_data['Temp']:.1f}°C")
        
        fuel_percent = (self.serial_data['Fuel'] / self.calibration_data['TANK_CAPACITY']) * 100
        self.fuel_bar.setValue(int(fuel_percent))
        self.fuel_bar.setFormat(f"{self.serial_data['Fuel']:.1f} л ({fuel_percent:.0f}%)")
        
        voltage_percent = (self.serial_data['Volt'] / 15.0) * 100
        self.voltage_bar.setValue(int(voltage_percent))
        self.voltage_bar.setFormat(f"{self.serial_data['Volt']:.1f} В")
        
        # Обновляем статусы
        self.status_labels['Дроссель'].setText(self.serial_data['Throttle'])
        self.status_labels['Топливный насос'].setText(self.serial_data['Pump'])
        self.status_labels['Клапан ХХ'].setText(self.serial_data['Valve'])
        self.status_labels['Коэф. дросселя'].setText(f"{self.serial_data['ThrFactor']:.1f}")
        self.status_labels['Запас хода'].setText(f"{self.serial_data['Range']:.0f} км")
        self.status_labels['Мгновенный расход'].setText(f"{self.serial_data['InstCons']:.1f} л/100км")
        
        # Обновляем диагностические данные
        self.diagnostic_labels['Температура воздуха'].setText(f"{self.diagnostic_data['Temp1']:.1f}°C")
        self.diagnostic_labels['Температура салона'].setText(f"{self.diagnostic_data['Temp2']:.1f}°C")
        self.diagnostic_labels['Напряжение датчика'].setText(f"{self.diagnostic_data['Vin_fuel']:.2f} В")
        self.diagnostic_labels['Напряжение Vbat'].setText(f"{self.diagnostic_data['Vbat']:.2f} В")
        self.diagnostic_labels['Счетчик RPM'].setText(f"{self.diagnostic_data['RPM_impuls']:.0f}")
        self.diagnostic_labels['Счетчик скорости'].setText(f"{self.diagnostic_data['speed_counter']:.0f}")
        self.diagnostic_labels['A0 (Топливо)'].setText(f"{self.diagnostic_data['A0']:.0f}")
        self.diagnostic_labels['A1 (Напряжение)'].setText(f"{self.diagnostic_data['A1']:.0f}")
        self.diagnostic_labels['A3 (Салон)'].setText(f"{self.diagnostic_data['A3']:.0f}")
        self.diagnostic_labels['A6 (Воздух)'].setText(f"{self.diagnostic_data['A6']:.0f}")
        self.diagnostic_labels['A7 (Двигатель)'].setText(f"{self.diagnostic_data['A7']:.0f}")
        
        # Обновляем историю для графиков
        for key in self.history:
            if key in self.serial_data:
                self.history[key].append(self.serial_data[key])
                if len(self.history[key]) > self.max_history:
                    self.history[key].pop(0)
            elif key in self.diagnostic_data:
                self.history[key].append(self.diagnostic_data[key])
                if len(self.history[key]) > self.max_history:
                    self.history[key].pop(0)
        
        # Обновляем графики
        self.update_charts()
        
    def update_charts(self):
        if not self.history['Temp']:
            return
            
        x_data = list(range(len(self.history['Temp'])))
        
        # Графики температур
        self.temp_engine_curve.setData(x_data, self.history['Temp'])
        self.temp_air_curve.setData(x_data, self.history.get('Temp1', []))
        self.temp_cabin_curve.setData(x_data, self.history.get('Temp2', []))
        
        # Графики двигателя
        self.rpm_curve.setData(x_data, self.history['PRM'])
        self.servo_curve.setData(x_data, self.history['Servo'])
        self.throttle_factor_curve.setData(x_data, self.history['ThrFactor'])
        
        # Графики скорости и расхода
        self.speed_curve.setData(x_data, self.history['Speed'])
        self.avg_consumption_curve.setData(x_data, self.history['AvgCons'])
        self.inst_consumption_curve.setData(x_data, self.history['InstCons'])
        
        # Графики топлива и напряжения
        self.fuel_curve.setData(x_data, self.history['Fuel'])
        self.voltage_curve.setData(x_data, self.history['Volt'])
        
    def update_stats(self):
        # Обновляем статистику
        self.max_speed = max(self.max_speed, self.serial_data['Speed'])
        self.max_rpm = max(self.max_rpm, self.serial_data['PRM'])
        self.min_voltage = min(self.min_voltage, self.serial_data['Volt'])
        self.max_temp = max(self.max_temp, self.serial_data['Temp'])
        
        # Обновляем отображение статистики
        self.stats_labels['Макс. скорость'].setText(f"{self.max_speed:.1f} км/ч")
        self.stats_labels['Макс. обороты'].setText(f"{self.max_rpm:.0f} об/мин")
        self.stats_labels['Мин. напряжение'].setText(f"{self.min_voltage:.1f} В")
        self.stats_labels['Макс. температура'].setText(f"{self.max_temp:.1f}°C")
        
    def select_data_folder(self):
        """Выбор папки для сохранения данных"""
        dialog = FolderSelectDialog(self.data_dir, self)
        if dialog.exec():
            self.data_dir = dialog.selected_folder
            self.data_dir_label.setText(f"{self.data_dir}")
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Папка данных изменена на: {self.data_dir}")
        
    def configure_history(self):
        """Настройка размера истории"""
        dialog = HistorySizeDialog(self.max_history, self)
        if dialog.exec():
            new_size = dialog.history_spin.value()
            self.max_history = new_size
            self.history_size_label.setText(f"Текущий размер истории: {self.max_history} точек")
            
            # Обрезаем историю если нужно
            for key in self.history:
                if len(self.history[key]) > self.max_history:
                    self.history[key] = self.history[key][-self.max_history:]
            
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Размер истории изменен на {new_size} точек")
        
    def calibrate_fuel_sensor(self):
        dialog = CalibrationDialog(self)
        if dialog.exec():
            try:
                self.calibration_data['V_EMPTY'] = float(dialog.empty_voltage.text())
                self.calibration_data['V_FULL'] = float(dialog.full_voltage.text())
                self.calibration_data['TANK_CAPACITY'] = float(dialog.tank_capacity.text())
                
                if self.save_calibration():
                    QMessageBox.information(self, "Успех", "Калибровочные данные сохранены!")
                    self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Калибровка датчика топлива обновлена")
                else:
                    QMessageBox.warning(self, "Ошибка", "Не удалось сохранить калибровку")
            except ValueError:
                QMessageBox.warning(self, "Ошибка", "Некорректные числовые значения")
                
    def reset_stats(self):
        self.max_speed = 0
        self.max_rpm = 0
        self.min_voltage = 999
        self.max_temp = 0
        self.total_distance = 0
        self.total_fuel_used = 0
        self.update_stats()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Статистика сброшена")
        
    def clear_graphs(self):
        for key in self.history:
            self.history[key].clear()
        self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Графики очищены")
        
    def save_data(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"car_data_{timestamp}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            # Сохраняем историю для последующего воспроизведения
            history_list = []
            history_length = len(self.history['Temp'])
            
            for i in range(history_length):
                data_point = {}
                for key in self.history:
                    if i < len(self.history[key]):
                        data_point[key] = self.history[key][i]
                history_list.append(data_point)
            
            data_to_save = {
                'timestamp': datetime.now().isoformat(),
                'current_data': self.serial_data,
                'diagnostic_data': self.diagnostic_data,
                'calibration': self.calibration_data,
                'system_calibration': self.system_calibration,
                'statistics': {
                    'max_speed': self.max_speed,
                    'max_rpm': self.max_rpm,
                    'min_voltage': self.min_voltage,
                    'max_temp': self.max_temp,
                    'total_distance': self.total_distance,
                    'total_fuel_used': self.total_fuel_used
                },
                'history': history_list
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, indent=2, ensure_ascii=False)
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Данные сохранены в {filepath}")
        except Exception as e:
            error_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка сохранения: {str(e)}"
            self.log_text.append(error_msg)
            QMessageBox.critical(self, "Ошибка сохранения", 
                               f"Не удалось сохранить данные:\n{str(e)}\n\n"
                               f"Проверьте права доступа к папке:\n{self.data_dir}")
            
    def test_connection(self):
        if self.is_playing:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Тест связи: РЕЖИМ ВОСПРОИЗВЕДЕНИЯ")
        elif self.ser and self.ser.is_open:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Тест связи: ПОРТ ОТКРЫТ - {self.ser.port}")
        else:
            self.log_text.append(f"[{datetime.now().strftime('%H:%M:%S')}] Тест связи: ПОРТ ЗАКРЫТ")
            
    def closeEvent(self, event):
        if self.ser and self.ser.is_open:
            self.ser.close()
        if self.playback_timer.isActive():
            self.playback_timer.stop()
        if self.status_timer.isActive():
            self.status_timer.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Устанавливаем шрифт для лучшего отображения в Windows
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = SerialMonitor()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()