import sys
import time
import threading
import json
import os
import logging
from datetime import datetime
from struct import pack, unpack
import pandas as pd
import telebot
from telebot import types
import requests
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusIOException
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, 
                             QHBoxLayout, QPushButton, QComboBox, QSpinBox, 
                             QDoubleSpinBox, QGroupBox, QStatusBar, QFileDialog,
                             QTabWidget, QFrame, QGridLayout, QLineEdit, QCheckBox,
                             QTextEdit, QScrollArea)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from openpyxl import load_workbook

class TelegramBot:
    def __init__(self, token, chat_id, parent_app):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        self.parent = parent_app
        self.measurement_name = parent_app.telegram_test_name.text()
        self.send_interval = parent_app.telegram_interval.value()
        self.running = False
        self.is_group_chat = str(chat_id).startswith('-')

        @self.bot.message_handler(commands=['start', 'help'])
        def start(message):
            self.bot.send_message(message.chat.id, "🔔 Бот мониторинга температур активен!\n"
                               "Доступные команды:\n"
                               "/graph - получить графики\n"
                               "/status - статус измерения\n"
                               "/test - тестовое сообщение\n"
                               "/thresholds - текущие пороговые значения")

        @self.bot.message_handler(commands=['graph'])
        def send_graph(message):
            self.send_current_graphs()

        @self.bot.message_handler(commands=['test'])
        def test(message):
            reply = "✅ Тестовое сообщение!"
            if self.is_group_chat:
                self.bot.reply_to(message, reply)
            else:
                self.bot.send_message(message.chat.id, reply)

        @self.bot.message_handler(commands=['status'])
        def status(message):
            status_text = "📊 Статус:\n"
            status_text += f"Измерение: {self.measurement_name}\n"
            status_text += f"Интервал отправки: {self.send_interval} сек.\n"
            status_text += f"Режим: {'Групповой чат' if self.is_group_chat else 'ЛС'}"
            
            if self.is_group_chat:
                self.bot.reply_to(message, status_text)
            else:
                self.bot.send_message(message.chat.id, status_text)

        @self.bot.message_handler(commands=['thresholds'])
        def send_thresholds(message):
            thresholds_text = "📊 Текущие пороговые значения:\n"
            for i in range(8):
                enabled = "✅" if self.parent.threshold_checkboxes[i].isChecked() else "❌"
                thresholds_text += (f"Канал {i+1}: {enabled} "
                                  f"{self.parent.threshold_spinboxes[i].value()}°C\n")
            
            if self.is_group_chat:
                self.bot.reply_to(message, thresholds_text)
            else:
                self.bot.send_message(message.chat.id, thresholds_text)

    def send_message(self, text):
        if self.chat_id:
            self.bot.send_message(self.chat_id, text)

    def send_current_graphs(self):
        if not self.parent.data_log:
            self.send_message("📭 Нет данных для графиков!")
            return
        
        self.parent.figure.savefig("temp_graph.png", dpi=150)
        with open("temp_graph.png", "rb") as graph_file:
            if self.is_group_chat:
                self.bot.send_photo(self.chat_id, graph_file, 
                                 reply_to_message_id=self.parent.last_group_message_id,
                                 caption="📈 Графики температур")
            else:
                self.bot.send_photo(self.chat_id, graph_file, 
                                 caption="📈 Графики температур")

    def run(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.bot.polling, daemon=True).start()

class ModernTemperatureMonitor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Мониторинг температур МВ110-8А")
        self.setGeometry(100, 100, 1200, 900)
        
        # Параметры подключения
        self.port = 'COM3'
        self.baudrate = 9600
        self.parity = 'N'
        self.stopbits = 1
        self.bytesize = 8
        self.timeout = 1.0
        self.slave_id = 16
        self.update_interval = 2000
        
        # Данные
        self.data_log = []
        self.excel_file = "temperature_data.xlsx"
        self.config_file = "config.json"
        self.last_group_message_id = None
        self.excel_auto_save = False
        self.excel_writer = None
        self.channel_names = [f"Канал {i+1}" for i in range(8)]
        self.telegram_bot = None
        self.threshold_alerts_sent = [False] * 8
        
        # Инициализация компонентов
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_temperatures)
        self.client = None
        
        # Настройка интерфейса
        self.init_ui()
        self.setup_logging()
        self.load_config()
        
    def setup_logging(self):
        self.log_handler = logging.StreamHandler()
        self.log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.logger = logging.getLogger('TemperatureMonitor')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.log_handler)
        
    def log_message(self, message, level=logging.INFO):
        self.logger.log(level, message)
        if hasattr(self, 'log_text_edit'):
            self.log_text_edit.append(f"{datetime.now().strftime('%H:%M:%S.%f')[:-3]} - {message}")
            cursor = self.log_text_edit.textCursor()
            cursor.movePosition(cursor.End)
            self.log_text_edit.setTextCursor(cursor)

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # Стили
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f5f5; }
            QGroupBox { border: 1px solid #ddd; border-radius: 5px; margin-top: 10px; padding-top: 15px; font-weight: bold; }
            QPushButton { background-color: #4CAF50; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:disabled { background-color: #cccccc; }
            QPushButton#stopButton { background-color: #f44336; }
            QPushButton#stopButton:hover { background-color: #d32f2f; }
            QLineEdit, QComboBox, QSpinBox { padding: 5px; border: 1px solid #ddd; border-radius: 3px; }
            QTextEdit { background-color: white; border: 1px solid #ddd; border-radius: 3px; padding: 5px; font-family: monospace; }
        """)
        
        # Панель управления Modbus
        control_group = QGroupBox("Настройки Modbus")
        control_layout = QGridLayout()
        
        control_layout.addWidget(QLabel("COM порт:"), 0, 0)
        self.port_combo = QComboBox()
        self.port_combo.addItems([f"COM{i}" for i in range(1, 21)])
        self.port_combo.setCurrentText(self.port)
        control_layout.addWidget(self.port_combo, 0, 1)
        
        control_layout.addWidget(QLabel("Скорость (bps):"), 0, 2)
        self.baudrate_spin = QSpinBox()
        self.baudrate_spin.setRange(1200, 115200)
        self.baudrate_spin.setValue(self.baudrate)
        control_layout.addWidget(self.baudrate_spin, 0, 3)
        
        control_layout.addWidget(QLabel("Slave ID:"), 1, 0)
        self.slave_spin = QSpinBox()
        self.slave_spin.setRange(1, 247)
        self.slave_spin.setValue(self.slave_id)
        control_layout.addWidget(self.slave_spin, 1, 1)
        
        control_layout.addWidget(QLabel("Интервал (мс):"), 1, 2)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(500, 10000)
        self.interval_spin.setValue(self.update_interval)
        self.interval_spin.valueChanged.connect(self.set_update_interval)
        control_layout.addWidget(self.interval_spin, 1, 3)
        
        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)
        
        # Вкладки
        self.tabs = QTabWidget()
        
        # Вкладка с графиками
        self.graph_tab = QWidget()
        self.graph_tab_layout = QVBoxLayout(self.graph_tab)
        self.figure = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.graph_tab_layout.addWidget(self.canvas)
        
        self.axes = []
        self.lines = []
        for i in range(8):
            ax = self.figure.add_subplot(4, 2, i+1)
            line, = ax.plot([], [], label=f'Канал {i+1}', linewidth=2)
            ax.set_title(f'Канал {i+1}', fontsize=10)
            ax.set_ylabel('°C', fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            self.axes.append(ax)
            self.lines.append(line)
            
        self.figure.tight_layout()
        self.tabs.addTab(self.graph_tab, "Графики")
        
        # Вкладка с текущими значениями
        self.values_tab = QWidget()
        self.values_tab_layout = QGridLayout(self.values_tab)
        self.value_labels = []
        for i in range(8):
            frame = QFrame()
            frame.setFrameShape(QFrame.StyledPanel)
            frame_layout = QVBoxLayout(frame)
            
            title = QLabel(f"Канал {i+1}")
            title.setFont(QFont('Arial', 10, QFont.Bold))
            title.setAlignment(Qt.AlignCenter)
            frame_layout.addWidget(title)
            
            label = QLabel("-- °C")
            label.setAlignment(Qt.AlignCenter)
            label.setFont(QFont('Arial', 14, QFont.Bold))
            frame_layout.addWidget(label)
            
            self.value_labels.append(label)
            self.values_tab_layout.addWidget(frame, i//4, i%4)
        
        self.tabs.addTab(self.values_tab, "Текущие значения")
        
        # Вкладка с настройками каналов
        self.channels_tab = QWidget()
        self.channels_tab_layout = QVBoxLayout(self.channels_tab)
        
        channels_group = QGroupBox("Настройки названий каналов")
        channels_grid = QGridLayout()
        
        self.channel_name_edits = []
        for i in range(8):
            channels_grid.addWidget(QLabel(f"Канал {i+1}:"), i, 0)
            edit = QLineEdit(f"Канал {i+1}")
            edit.textChanged.connect(lambda text, idx=i: self.update_channel_name(idx, text))
            self.channel_name_edits.append(edit)
            channels_grid.addWidget(edit, i, 1)
        
        channels_group.setLayout(channels_grid)
        self.channels_tab_layout.addWidget(channels_group)
        
        # Группа пороговых значений
        threshold_group = QGroupBox("Уведомления при пороговой температуре")
        threshold_layout = QGridLayout()
        
        self.threshold_checkboxes = []
        self.threshold_spinboxes = []
        
        for i in range(8):
            chk = QCheckBox(f"Канал {i+1}")
            self.threshold_checkboxes.append(chk)
            threshold_layout.addWidget(chk, i, 0)
            
            spin = QDoubleSpinBox()
            spin.setRange(-50, 150)
            spin.setValue(50)
            spin.setSuffix(" °C")
            self.threshold_spinboxes.append(spin)
            threshold_layout.addWidget(spin, i, 1)
        
        threshold_group.setLayout(threshold_layout)
        self.channels_tab_layout.addWidget(threshold_group)
        self.channels_tab_layout.addStretch()
        
        self.tabs.addTab(self.channels_tab, "Настройки каналов")
        
        # Вкладка Telegram
        self.telegram_tab = QWidget()
        self.telegram_tab_layout = QVBoxLayout(self.telegram_tab)
        
        telegram_settings_group = QGroupBox("Настройки Telegram")
        telegram_settings_layout = QGridLayout()
        
        self.telegram_enable = QCheckBox("Включить Telegram бота")
        self.telegram_token = QLineEdit()
        self.telegram_token.setPlaceholderText("Введите токен бота")
        self.telegram_token.setText("8101843469:AAETKjUw7hx1mL3KrijQZBDCCB1fX7ser1o")
        self.telegram_chat_id = QLineEdit()
        self.telegram_chat_id.setPlaceholderText("Введите ID чата/группы")
        
        telegram_settings_layout.addWidget(QLabel("Токен бота:"), 0, 0)
        telegram_settings_layout.addWidget(self.telegram_token, 0, 1)
        telegram_settings_layout.addWidget(QLabel("ID чата:"), 1, 0)
        telegram_settings_layout.addWidget(self.telegram_chat_id, 1, 1)
        
        self.telegram_test_name = QLineEdit()
        self.telegram_test_name.setPlaceholderText("Название теста")
        self.telegram_test_name.setText("Тест")
        telegram_settings_layout.addWidget(QLabel("Название теста:"), 2, 0)
        telegram_settings_layout.addWidget(self.telegram_test_name, 2, 1)
        
        self.telegram_interval = QSpinBox()
        self.telegram_interval.setRange(10, 3600)
        self.telegram_interval.setValue(60)
        self.telegram_interval.setSuffix(" сек.")
        telegram_settings_layout.addWidget(QLabel("Интервал отправки:"), 3, 0)
        telegram_settings_layout.addWidget(self.telegram_interval, 3, 1)
        
        telegram_settings_group.setLayout(telegram_settings_layout)
        self.telegram_tab_layout.addWidget(telegram_settings_group)
        
        telegram_buttons_layout = QHBoxLayout()
        self.telegram_test_btn = QPushButton("Тест сообщение")
        self.telegram_test_btn.clicked.connect(self.send_test_telegram_message)
        telegram_buttons_layout.addWidget(self.telegram_test_btn)
        
        self.telegram_detect_btn = QPushButton("Определить chat_id")
        self.telegram_detect_btn.clicked.connect(self.detect_chat_id)
        telegram_buttons_layout.addWidget(self.telegram_detect_btn)
        
        self.telegram_tab_layout.addLayout(telegram_buttons_layout)
        self.telegram_tab_layout.addStretch()
        
        self.tabs.addTab(self.telegram_tab, "Настройки Telegram")
        
        # Вкладка Excel
        self.excel_tab = QWidget()
        self.excel_tab_layout = QVBoxLayout(self.excel_tab)
        
        excel_settings_group = QGroupBox("Настройки Excel")
        excel_settings_layout = QGridLayout()
        
        self.excel_auto_save_check = QCheckBox("Автоматическое сохранение в Excel")
        self.excel_auto_save_check.stateChanged.connect(self.toggle_auto_save)
        excel_settings_layout.addWidget(self.excel_auto_save_check, 0, 0, 1, 2)
        
        self.excel_file_edit = QLineEdit()
        self.excel_file_edit.setText(self.excel_file)
        excel_settings_layout.addWidget(QLabel("Файл Excel:"), 1, 0)
        excel_settings_layout.addWidget(self.excel_file_edit, 1, 1)
        
        self.excel_file_btn = QPushButton("Выбрать файл")
        self.excel_file_btn.clicked.connect(self.select_excel_file)
        excel_settings_layout.addWidget(self.excel_file_btn, 2, 0, 1, 2)
        
        excel_settings_group.setLayout(excel_settings_layout)
        self.excel_tab_layout.addWidget(excel_settings_group)
        self.excel_tab_layout.addStretch()
        
        self.tabs.addTab(self.excel_tab, "Настройки Excel")
        
        # Вкладка логов
        self.log_tab = QWidget()
        self.log_tab_layout = QVBoxLayout(self.log_tab)
        
        log_group = QGroupBox("Логи программы")
        log_layout = QVBoxLayout()
        
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setLineWrapMode(QTextEdit.NoWrap)
        
        log_buttons_layout = QHBoxLayout()
        self.clear_log_btn = QPushButton("Очистить логи")
        self.clear_log_btn.clicked.connect(self.clear_logs)
        log_buttons_layout.addWidget(self.clear_log_btn)
        
        self.save_log_btn = QPushButton("Сохранить логи")
        self.save_log_btn.clicked.connect(self.save_logs)
        log_buttons_layout.addWidget(self.save_log_btn)
        
        log_layout.addWidget(self.log_text_edit)
        log_layout.addLayout(log_buttons_layout)
        log_group.setLayout(log_layout)
        self.log_tab_layout.addWidget(log_group)
        
        self.tabs.addTab(self.log_tab, "Логи")
        
        main_layout.addWidget(self.tabs)
        
        # Кнопки управления
        button_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Подключиться")
        self.connect_btn.clicked.connect(self.toggle_connection)
        button_layout.addWidget(self.connect_btn)
        
        self.export_btn = QPushButton("Экспорт в Excel")
        self.export_btn.clicked.connect(self.export_to_excel)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)
        
        self.clear_btn = QPushButton("Очистить данные")
        self.clear_btn.clicked.connect(self.clear_data)
        self.clear_btn.setEnabled(False)
        button_layout.addWidget(self.clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Готов к подключению")

    def set_update_interval(self, interval):
        self.update_interval = max(500, min(interval, 10000))
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.setInterval(self.update_interval)
        self.log_message(f"Интервал обновления установлен: {self.update_interval} мс")

    def update_channel_name(self, channel_idx, new_name):
        self.channel_names[channel_idx] = new_name
        self.axes[channel_idx].set_title(new_name, fontsize=10)
        self.lines[channel_idx].set_label(new_name)
        
        if self.lines[channel_idx].get_label() and not self.lines[channel_idx].get_label().startswith('_'):
            self.axes[channel_idx].legend()
        
        self.canvas.draw()
        
        if channel_idx < len(self.value_labels):
            frame = self.value_labels[channel_idx].parent().parent()
            if frame and frame.layout():
                title_item = frame.layout().itemAt(0)
                if title_item:
                    title_label = title_item.widget()
                    if isinstance(title_label, QLabel):
                        title_label.setText(new_name)

    def clear_logs(self):
        self.log_text_edit.clear()
        self.log_message("Логи очищены")

    def save_logs(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить логи", 
            "temperature_monitor_log.txt", 
            "Text Files (*.txt)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.log_text_edit.toPlainText())
                self.log_message(f"Логи сохранены в {file_name}")
            except Exception as e:
                self.log_message(f"Ошибка сохранения логов: {str(e)}", logging.ERROR)

    def toggle_auto_save(self, state):
        self.excel_auto_save = (state == Qt.Checked)
        if self.excel_auto_save:
            self.excel_file = self.excel_file_edit.text()
            try:
                self.excel_writer = pd.ExcelWriter(self.excel_file, engine='openpyxl')
                self.log_message(f"Автосохранение включено. Файл: {self.excel_file}")
            except Exception as e:
                self.log_message(f"Ошибка открытия файла Excel: {str(e)}", logging.ERROR)
                self.excel_auto_save_check.setChecked(False)
        elif not self.excel_auto_save and hasattr(self, 'excel_writer') and self.excel_writer:
            self.save_excel_data()
            self.excel_writer = None
            self.log_message("Автосохранение отключено")

    def select_excel_file(self):
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Выберите файл Excel", 
            self.excel_file, 
            "Excel Files (*.xlsx)"
        )
        if file_name:
            self.excel_file_edit.setText(file_name)
            self.excel_file = file_name
            if self.excel_auto_save and hasattr(self, 'excel_writer') and self.excel_writer:
                self.save_excel_data()
                try:
                    self.excel_writer = pd.ExcelWriter(self.excel_file, engine='openpyxl')
                except Exception as e:
                    self.log_message(f"Ошибка открытия файла Excel: {str(e)}", logging.ERROR)
                    self.excel_auto_save_check.setChecked(False)

    def save_excel_data(self):
        if hasattr(self, 'excel_writer') and self.excel_writer and self.data_log:
            try:
                df = pd.DataFrame(self.data_log)
                df.set_index('timestamp', inplace=True)
                df.to_excel(self.excel_writer)
                self.excel_writer.close()
                self.excel_writer = pd.ExcelWriter(self.excel_file, engine='openpyxl')
                self.log_message(f"Данные сохранены в {self.excel_file}")
            except PermissionError:
                self.log_message("Ошибка: Файл Excel занят другим процессом!", logging.ERROR)
            except Exception as e:
                self.log_message(f"Ошибка сохранения в Excel: {str(e)}", logging.ERROR)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.telegram_token.setText(config.get('telegram_token', ''))
                    self.telegram_chat_id.setText(config.get('telegram_chat_id', ''))
                    self.telegram_enable.setChecked(config.get('telegram_enabled', False))
                    self.telegram_test_name.setText(config.get('telegram_test_name', 'Тест B1B7'))
                    self.telegram_interval.setValue(config.get('telegram_interval', 60))
                    self.excel_auto_save_check.setChecked(config.get('excel_auto_save', False))
                    self.excel_file_edit.setText(config.get('excel_file', 'temperature_data.xlsx'))
                    self.excel_file = config.get('excel_file', 'temperature_data.xlsx')
                    
                    channel_names = config.get('channel_names', [])
                    for i, name in enumerate(channel_names):
                        if i < len(self.channel_name_edits):
                            self.channel_name_edits[i].setText(name)
                            self.channel_names[i] = name
                            self.update_channel_name(i, name)
                    
                    threshold_enabled = config.get('threshold_enabled', [False]*8)
                    threshold_values = config.get('threshold_values', [50.0]*8)
                    
                    for i in range(8):
                        if i < len(self.threshold_checkboxes):
                            self.threshold_checkboxes[i].setChecked(threshold_enabled[i])
                        if i < len(self.threshold_spinboxes):
                            self.threshold_spinboxes[i].setValue(threshold_values[i])
                
                self.log_message("Конфигурация загружена")
            except Exception as e:
                self.log_message(f"Ошибка загрузки конфига: {e}", logging.ERROR)

    def save_config(self):
        config = {
            'telegram_token': self.telegram_token.text(),
            'telegram_chat_id': self.telegram_chat_id.text(),
            'telegram_enabled': self.telegram_enable.isChecked(),
            'telegram_test_name': self.telegram_test_name.text(),
            'telegram_interval': self.telegram_interval.value(),
            'excel_auto_save': self.excel_auto_save_check.isChecked(),
            'excel_file': self.excel_file_edit.text(),
            'channel_names': self.channel_names,
            'threshold_enabled': [chk.isChecked() for chk in self.threshold_checkboxes],
            'threshold_values': [spin.value() for spin in self.threshold_spinboxes]
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
        self.log_message("Конфигурация сохранена")

    def detect_chat_id(self):
        token = self.telegram_token.text()
        if not token:
            self.log_message("Введите токен бота!", logging.WARNING)
            return
            
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates"
            response = requests.get(url).json()
            
            if response.get('ok'):
                if len(response['result']) > 0:
                    last_update = response['result'][-1]
                    chat_id = last_update['message']['chat']['id']
                    self.telegram_chat_id.setText(str(chat_id))
                    self.log_message(f"Определен chat_id: {chat_id}")
                else:
                    self.log_message("Отправьте боту сообщение в чате!", logging.WARNING)
            else:
                self.log_message("Ошибка API Telegram", logging.ERROR)
        except Exception as e:
            self.log_message(f"Ошибка: {str(e)}", logging.ERROR)

    def send_test_telegram_message(self):
        token = self.telegram_token.text()
        chat_id = self.telegram_chat_id.text()
        
        if not token or not chat_id:
            self.log_message("Введите токен и chat_id!", logging.WARNING)
            return
            
        try:
            if not self.telegram_bot:
                self.telegram_bot = TelegramBot(token, chat_id, self)
                self.telegram_bot.run()
            
            self.telegram_bot.send_message("✅ Программа включена")
            self.log_message("Тестовое сообщение отправлено")
        except Exception as e:
            self.log_message(f"Ошибка Telegram: {str(e)}", logging.ERROR)

    def toggle_connection(self):
        if self.timer.isActive():
            self.stop_monitoring()
        else:
            self.start_monitoring()

    def start_monitoring(self):
        self.port = self.port_combo.currentText()
        self.baudrate = self.baudrate_spin.value()
        self.slave_id = self.slave_spin.value()
        
        self.log_message(f"Подключение к {self.port} (Slave ID: {self.slave_id})...")
        
        try:
            self.client = ModbusSerialClient(
                port=self.port,
                baudrate=self.baudrate,
                parity=self.parity,
                stopbits=self.stopbits,
                bytesize=self.bytesize,
                timeout=self.timeout
            )
            
            if not self.client.connect():
                self.log_message("Не удалось подключиться к устройству!", logging.ERROR)
                return
                
            # Тестовый запрос для проверки связи
            try:
                test_response = self.client.read_input_registers(address=4, count=2, slave=self.slave_id)
                if test_response.isError():
                    self.log_message(f"Тестовый запрос не удался: {test_response}", logging.ERROR)
                else:
                    self.log_message(f"Тестовый запрос успешен: регистры {test_response.registers}", logging.DEBUG)
            except Exception as test_error:
                self.log_message(f"Ошибка тестового запроса: {str(test_error)}", logging.ERROR)
            
            self.log_message(f"Успешное подключение к {self.port} (Slave ID: {self.slave_id})")
            
            self.connect_btn.setText("Остановить")
            self.connect_btn.setStyleSheet("background-color: #f44336;")
            self.export_btn.setEnabled(True)
            self.clear_btn.setEnabled(True)
            
            self.threshold_alerts_sent = [False] * 8
            
            if self.telegram_enable.isChecked():
                token = self.telegram_token.text()
                chat_id = self.telegram_chat_id.text()
                if token and chat_id:
                    try:
                        self.telegram_bot = TelegramBot(token, chat_id, self)
                        self.telegram_bot.run()
                        msg = f"🔴 Начато измерение: {self.telegram_bot.measurement_name}"
                        self.telegram_bot.send_message(msg)
                        self.log_message("Telegram бот запущен")
                        
                        if str(chat_id).startswith('-'):
                            self.last_group_message_id = self.get_last_message_id(token, chat_id)
                    except Exception as e:
                        self.log_message(f"Ошибка Telegram: {str(e)}", logging.ERROR)
            
            if self.excel_auto_save_check.isChecked():
                self.toggle_auto_save(Qt.Checked)
            
            self.timer.start(self.update_interval)
            self.log_message(f"Таймер запущен с интервалом {self.update_interval} мс")
            self.save_config()
            
        except Exception as e:
            self.log_message(f"Ошибка при запуске мониторинга: {str(e)}", logging.CRITICAL)
            if hasattr(self, 'client') and self.client:
                self.client.close()

    def get_last_message_id(self, token, chat_id):
        try:
            url = f"https://api.telegram.org/bot{token}/getUpdates?chat_id={chat_id}"
            response = requests.get(url).json()
            if response.get('ok') and response.get('result'):
                return response['result'][-1]['message']['message_id']
        except:
            return None

    def stop_monitoring(self):
        self.timer.stop()
        if hasattr(self, 'client') and self.client and self.client.connected:
            self.client.close()
        
        self.connect_btn.setText("Подключиться")
        self.connect_btn.setStyleSheet("background-color: #4CAF50;")
        
        if hasattr(self, 'telegram_bot') and self.telegram_bot:
            self.telegram_bot.send_message(f"🟢 Измерение завершено: {self.telegram_bot.measurement_name}")
            self.log_message("Telegram бот остановлен")
        
        if hasattr(self, 'excel_writer') and self.excel_writer and self.excel_auto_save:
            self.save_excel_data()
            self.excel_writer = None
        
        self.log_message("Мониторинг остановлен")
        self.save_config()

    def update_temperatures(self):
        if not hasattr(self, 'client') or not self.client or not self.client.connected:
            self.log_message("Ошибка: Modbus клиент не подключен!", logging.ERROR)
            self.stop_monitoring()
            return
            
        temps = []
        timestamp = datetime.now()
        self.log_message(f"=== Начало чтения данных ({timestamp}) ===", logging.DEBUG)
        
        try:
            for channel in range(8):
                try:
                    address = 4 + channel * 6
                    self.log_message(f"Чтение канала {channel+1} (адрес: {address}, Slave ID: {self.slave_id})...", logging.DEBUG)
                    
                    response = self.client.read_input_registers(
                        address=address,
                        count=2,
                        slave=self.slave_id
                    )

                    if response.isError():
                        self.log_message(f"Ошибка Modbus для канала {channel+1}: {response}", logging.ERROR)
                        temps.append(None)
                        continue
                        
                    self.log_message(f"Канал {channel+1}: получены регистры {response.registers}", logging.DEBUG)
                    
                    try:
                        packed = pack('>HH', *response.registers)
                        temperature = unpack('>f', packed)[0]
                        temp = round(temperature, 2)
                        temps.append(temp)
                        self.log_message(f"Канал {channel+1}: температура = {temp}°C", logging.DEBUG)
                        
                        if (self.threshold_checkboxes[channel].isChecked() and 
                            temp > self.threshold_spinboxes[channel].value() and
                            not self.threshold_alerts_sent[channel]):
                            
                            alert_msg = (f"⚠️ ПРЕВЫШЕНИЕ ТЕМПЕРАТУРЫ!\n"
                                       f"Канал: {self.channel_names[channel]}\n"
                                       f"Текущая температура: {temp} °C\n"
                                       f"Пороговое значение: {self.threshold_spinboxes[channel].value()} °C")
                            
                            if hasattr(self, 'telegram_bot') and self.telegram_bot:
                                self.telegram_bot.send_message(alert_msg)
                            
                            self.threshold_alerts_sent[channel] = True
                            self.log_message(f"Превышение порога на канале {channel+1}: {temp}°C", logging.WARNING)
                        
                        elif (temp <= self.threshold_spinboxes[channel].value() and 
                              self.threshold_alerts_sent[channel]):
                            self.threshold_alerts_sent[channel] = False
                            self.log_message(f"Температура на канале {channel+1} вернулась в норму: {temp}°C", logging.INFO)
                            
                    except Exception as conv_error:
                        self.log_message(f"Ошибка преобразования данных канала {channel+1}: {str(conv_error)}", logging.ERROR)
                        temps.append(None)
                        
                except ModbusIOException as mb_error:
                    self.log_message(f"Ошибка Modbus IO для канала {channel+1}: {str(mb_error)}", logging.ERROR)
                    temps.append(None)
                except Exception as ch_error:
                    self.log_message(f"Неожиданная ошибка канала {channel+1}: {str(ch_error)}", logging.ERROR)
                    temps.append(None)
                    
            self.update_display(temps, timestamp)
            self.log_message("=== Данные успешно обновлены ===", logging.DEBUG)
            
            if hasattr(self, 'telegram_bot') and self.telegram_bot and len(self.data_log) % 10 == 0:
                self.telegram_bot.send_current_graphs()
                self.log_message("Графики отправлены в Telegram")
                
        except Exception as e:
            self.log_message(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}", logging.CRITICAL)
            self.stop_monitoring()
    
    def update_display(self, temps, timestamp):
        for i, temp in enumerate(temps):
            if temp is not None:
                self.value_labels[i].setText(f"{temp} °C")
                color = QColor(255, 0, 0) if temp > 50 else QColor(0, 128, 0)
                self.value_labels[i].setStyleSheet(f"color: {color.name()};")
            else:
                self.value_labels[i].setText("Ошибка")
                self.value_labels[i].setStyleSheet("color: gray;")
        
        log_entry = {'timestamp': timestamp}
        for i, temp in enumerate(temps, 1):
            log_entry[f'channel_{i}'] = temp
        self.data_log.append(log_entry)
        
        for i in range(8):
            times = [entry['timestamp'] for entry in self.data_log if entry[f'channel_{i+1}'] is not None]
            values = [entry[f'channel_{i+1}'] for entry in self.data_log if entry[f'channel_{i+1}'] is not None]
            
            if times and values:
                self.lines[i].set_data(mdates.date2num(times), values)
                self.axes[i].relim()
                self.axes[i].autoscale_view()
                
        self.canvas.draw()
        
        if (self.excel_auto_save and hasattr(self, 'excel_writer') and 
            self.excel_writer and len(self.data_log) % 10 == 0):
            self.save_excel_data()
    
    def export_to_excel(self):
        if not self.data_log:
            self.log_message("Нет данных для экспорта", logging.WARNING)
            return
            
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Сохранить данные", 
            self.excel_file, 
            "Excel Files (*.xlsx)"
        )
        
        if file_name:
            self.excel_file = file_name
            df = pd.DataFrame(self.data_log)
            df.set_index('timestamp', inplace=True)
            df.to_excel(file_name)
            self.log_message(f"Данные экспортированы в {file_name}")
    
    def clear_data(self):
        self.data_log = []
        for line in self.lines:
            line.set_data([], [])
        for label in self.value_labels:
            label.setText("-- °C")
            label.setStyleSheet("color: black;")
        self.canvas.draw()
        self.log_message("Данные очищены")

    def closeEvent(self, event):
        self.save_config()
        if hasattr(self, 'telegram_bot') and self.telegram_bot:
            self.telegram_bot.send_message("🛑 Программа закрыта")
            self.log_message("Telegram бот остановлен")
        if hasattr(self, 'client') and self.client and self.client.connected:
            self.client.close()
            self.log_message("Modbus соединение закрыто")
        if hasattr(self, 'excel_writer') and self.excel_writer and self.excel_auto_save:
            self.save_excel_data()
            self.excel_writer = None
            self.log_message("Excel автосохранение завершено")
        self.log_message("Программа закрыта")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    monitor = ModernTemperatureMonitor()
    monitor.show()
    sys.exit(app.exec_())