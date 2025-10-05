import sys
import serial
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading
from queue import Queue, Empty
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging

# Упрощенная версия осциллографа
class SimpleArduinoOscilloscope:
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.is_simulating = False
        self.shutdown_flag = threading.Event()
        
        # Данные
        self.time_data = []
        self.voltage_data = []
        self.max_points = 500
        
        # Настройка GUI
        self.setup_gui()
        self.setup_plot()
        
        # Запуск потоков
        self.start_worker_threads()
        
    def setup_gui(self):
        self.root = tk.Tk()
        self.root.title("Arduino Oscilloscope - Fixed Version")
import serial
import serial.tools.list_ports
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import time
import threading
from queue import Queue, Empty
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from collections import deque
import json
import logging
from dataclasses import dataclass
from typing import Optional, Tuple, List
import matplotlib as mpl

# Настройка стиля matplotlib для темной темы
plt.style.use('dark_background')
mpl.rcParams['axes.grid'] = True
mpl.rcParams['grid.alpha'] = 0.2

@dataclass
class OscilloscopeConfig:
    sample_rate: int = 30
    buffer_size: int = 500
    trigger_level: float = 2.5
    trigger_slope: str = "rising"
    voltage_range: Tuple[float, float] = (0, 5)
    time_window: float = 5.0

class StableArduinoOscilloscope:
    def __init__(self):
        # Конфигурация
        self.config = OscilloscopeConfig()
        
        # Очереди данных
        self.data_queue = Queue()
        self.command_queue = Queue()
        
        # Состояние системы
        self.serial_port: Optional[serial.Serial] = None
        self.is_connected = False
        self.is_simulating = False
        self.is_recording = False
        self.shutdown_flag = threading.Event()
        
        # Данные и статистика
        self.time_data = deque(maxlen=self.config.buffer_size)
        self.voltage_data = deque(maxlen=self.config.buffer_size)
        self.recorded_data = []
        self.packet_count = 0
        self.error_count = 0
        self.connection_quality = 100
        
        # Триггер
        self.trigger_enabled = False
        self.trigger_armed = True
        
        # Протокол
        self.rx_buffer = bytearray()
        self.last_sync_time = 0
        
        # Параметры сигнала
        self.wave_type = 0
        self.frequency = 1.0
        self.amplitude = 1.0
        
        # Настройка логирования
        self.setup_logging()
        
        # Запуск GUI
        self.setup_gui()
        
    def setup_logging(self):
        """Настройка системы логирования"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('oscilloscope.log', mode='w'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_gui(self):
        """Создание современного GUI"""
        self.root = tk.Tk()
        self.root.title("Advanced Arduino Oscilloscope Pro v2.1")
        self.root.geometry("1400x900")
        self.root.configure(bg='#1a1a1a')
        
        # Обработчик закрытия окна
        self.root.protocol("WM_DELETE_WINDOW", self.safe_shutdown)
        
        # Современная тема
        self.style = ttk.Style()
        self.setup_modern_theme()
        
        # Основной layout
        self.create_main_layout()
        
        # Запуск рабочих потоков
        self.start_worker_threads()
        
        # Запуск анимации
        self.setup_plot_animation()
        
    def safe_shutdown(self):
        """Безопасное завершение работы"""
        self.logger.info("Инициировано безопасное завершение работы")
        self.shutdown_flag.set()
        
        if self.is_connected and self.serial_port:
            try:
                self.serial_port.close()
            except:
                pass
        
        # Даем время потокам завершиться
        self.root.after(100, self.root.quit)
    
    def setup_modern_theme(self):
        """Настройка современной темы"""
        self.style.theme_use('clam')
        
        # Темная цветовая схема
        colors = {
            'primary': '#2b2b2b',
            'secondary': '#3c3c3c', 
            'accent': '#00ffaa',
            'warning': '#ffaa00',
            'error': '#ff5555',
            'success': '#55ff55'
        }
        
        self.style.configure('TFrame', background=colors['primary'])
        self.style.configure('TLabel', background=colors['primary'], foreground='white')
        self.style.configure('TButton', 
                           background=colors['secondary'], 
                           foreground='white',
                           borderwidth=1,
                           focuscolor='none')
        self.style.configure('Accent.TButton', 
                           background=colors['accent'],
                           foreground='black')
        self.style.configure('TCombobox', 
                           background=colors['secondary'],
                           foreground='white')
        self.style.configure('TLabelframe',
                           background=colors['primary'],
                           foreground=colors['accent'])
        self.style.configure('TLabelframe.Label',
                           background=colors['primary'],
                           foreground=colors['accent'])
        
    def create_main_layout(self):
        """Создание основного layout"""
        # Главный контейнер
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель - управление
        left_panel = ttk.Frame(main_container, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Правая панель - осциллограф и анализатор
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заполняем панели
        self.setup_control_panel(left_panel)
        self.setup_oscilloscope_panel(right_panel)
        self.setup_analyzer_panel(right_panel)
        
    def setup_control_panel(self, parent):
        """Панель управления с индикацией качества связи"""
        # Заголовок
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="ARDUINO OSCILLOSCOPE v2.1", 
                 font=('Arial', 12, 'bold'), foreground='#00ffaa').pack()
        
        # Подключение
        self.setup_connection_section(parent)
        
        # Генератор сигналов
        self.setup_generator_section(parent)
        
        # Осциллограф
        self.setup_oscilloscope_controls(parent)
        
        # Анализатор
        self.setup_analyzer_controls(parent)
        
        # Статус
        self.setup_status_section(parent)
        
    def setup_connection_section(self, parent):
        """Секция подключения с индикацией качества"""
        conn_frame = ttk.LabelFrame(parent, text="Подключение", padding=10)
        conn_frame.pack(fill=tk.X, pady=5)
        
        # COM порт
        ttk.Label(conn_frame, text="COM Порт:").pack(anchor=tk.W)
        self.port_combo = ttk.Combobox(conn_frame, values=self.get_available_ports())
        self.port_combo.pack(fill=tk.X, pady=2)
        self.port_combo.bind('<Button-1>', lambda e: self.refresh_ports())
        
        # Индикатор качества связи
        quality_frame = ttk.Frame(conn_frame)
        quality_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(quality_frame, text="Качество связи:").pack(side=tk.LEFT)
        self.quality_label = ttk.Label(quality_frame, text="100%", foreground="green")
        self.quality_label.pack(side=tk.RIGHT)
        
        # Прогресс-бар качества связи
        self.quality_bar = ttk.Progressbar(conn_frame, orient='horizontal', length=100, mode='determinate')
        self.quality_bar.pack(fill=tk.X, pady=2)
        self.quality_bar['value'] = 100
        
        # Кнопки подключения
        btn_frame = ttk.Frame(conn_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        self.connect_btn = ttk.Button(btn_frame, text="Подключить", 
                                     command=self.toggle_connection, style='Accent.TButton')
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(btn_frame, text="Обновить", 
                  command=self.refresh_ports).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # Индикатор статуса
        self.connection_indicator = ttk.Label(conn_frame, text="● Отключено", 
                                             foreground="red", font=('Arial', 9, 'bold'))
        self.connection_indicator.pack(anchor=tk.W)
        
    def get_available_ports(self):
        """Получение списка доступных COM портов"""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
    
    def refresh_ports(self):
        """Обновление списка COM портов"""
        ports = self.get_available_ports()
        self.port_combo['values'] = ports
        if ports and not self.port_combo.get():
            self.port_combo.set(ports[0])
    
    def setup_generator_section(self, parent):
        """Секция генератора сигналов"""
        gen_frame = ttk.LabelFrame(parent, text="Генератор сигналов", padding=10)
        gen_frame.pack(fill=tk.X, pady=5)
        
        # Тип сигнала
        ttk.Label(gen_frame, text="Тип сигнала:").pack(anchor=tk.W)
        self.wave_combo = ttk.Combobox(gen_frame, 
                                      values=["Синус", "Треугольник", "Прямоугольник", "Пилообразный"])
        self.wave_combo.pack(fill=tk.X, pady=2)
        self.wave_combo.set("Синус")
        self.wave_combo.bind('<<ComboboxSelected>>', self.on_parameter_change)
        
        # Частота
        ttk.Label(gen_frame, text=f"Частота: {self.frequency:.1f} Гц").pack(anchor=tk.W)
        self.freq_var = tk.DoubleVar(value=self.frequency)
        self.freq_scale = tk.Scale(gen_frame, from_=0.1, to=10.0, resolution=0.1,
                                  orient=tk.HORIZONTAL, variable=self.freq_var,
                                  command=self.on_frequency_change, 
                                  bg='#2b2b2b', fg='white', troughcolor='#404040',
                                  highlightbackground='#2b2b2b', length=150)
        self.freq_scale.pack(fill=tk.X, pady=2)
        
        # Амплитуда
        ttk.Label(gen_frame, text=f"Амплитуда: {self.amplitude:.1f} В").pack(anchor=tk.W)
        self.amp_var = tk.DoubleVar(value=self.amplitude)
        self.amp_scale = tk.Scale(gen_frame, from_=0.1, to=2.5, resolution=0.1,
                                 orient=tk.HORIZONTAL, variable=self.amp_var,
                                 command=self.on_amplitude_change,
                                 bg='#2b2b2b', fg='white', troughcolor='#404040',
                                 highlightbackground='#2b2b2b', length=150)
        self.amp_scale.pack(fill=tk.X, pady=2)
        
        # Кнопка применения
        ttk.Button(gen_frame, text="Применить параметры", 
                  command=self.send_all_parameters).pack(fill=tk.X, pady=5)
        
    def setup_oscilloscope_controls(self, parent):
        """Управление осциллографом"""
        scope_frame = ttk.LabelFrame(parent, text="Осциллограф", padding=10)
        scope_frame.pack(fill=tk.X, pady=5)
        
        # Триггер
        trigger_frame = ttk.Frame(scope_frame)
        trigger_frame.pack(fill=tk.X, pady=2)
        
        self.trigger_var = tk.BooleanVar()
        ttk.Checkbutton(trigger_frame, text="Триггер", 
                       variable=self.trigger_var, command=self.on_trigger_toggle).pack(side=tk.LEFT)
        
        self.trigger_level_var = tk.DoubleVar(value=2.5)
        ttk.Scale(trigger_frame, from_=0, to=5.0, variable=self.trigger_level_var,
                 command=self.on_trigger_level_change, length=150).pack(side=tk.RIGHT)
        
        # Управление захватом
        capture_frame = ttk.Frame(scope_frame)
        capture_frame.pack(fill=tk.X, pady=5)
        
        self.record_btn = ttk.Button(capture_frame, text="● Запись", 
                                    command=self.toggle_recording)
        self.record_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(capture_frame, text="Сохранить данные", 
                  command=self.save_data).pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
    def setup_analyzer_controls(self, parent):
        """Управление анализатором"""
        analyzer_frame = ttk.LabelFrame(parent, text="Анализатор", padding=10)
        analyzer_frame.pack(fill=tk.X, pady=5)
        
        # Режимы анализа
        self.analysis_var = tk.StringVar(value="time")
        ttk.Radiobutton(analyzer_frame, text="Временная область", 
                       variable=self.analysis_var, value="time").pack(anchor=tk.W)
        ttk.Radiobutton(analyzer_frame, text="Частотная область (FFT)", 
                       variable=self.analysis_var, value="fft").pack(anchor=tk.W)
        
        # Калибровка
        ttk.Button(analyzer_frame, text="Калибровать", 
                  command=self.calibrate).pack(fill=tk.X, pady=5)
        
    def setup_status_section(self, parent):
        """Секция статуса"""
        status_frame = ttk.LabelFrame(parent, text="Статистика", padding=10)
        status_frame.pack(fill=tk.X, pady=5)
        
        self.status_text = tk.Text(status_frame, height=8, width=30, 
                                  bg='#2b2b2b', fg='white', font=('Consolas', 8),
                                  relief='flat')
        self.status_text.pack(fill=tk.BOTH)
        
    def setup_oscilloscope_panel(self, parent):
        """Панель осциллографа"""
        scope_frame = ttk.LabelFrame(parent, text="Осциллограф в реальном времени", padding=10)
        scope_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Создаем фигуру matplotlib
        self.fig = plt.Figure(figsize=(10, 6), facecolor='#1a1a1a')
        self.canvas = FigureCanvasTkAgg(self.fig, scope_frame)
        
        # Добавляем панель навигации
        toolbar = NavigationToolbar2Tk(self.canvas, scope_frame)
        toolbar.update()
        
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Настройка осей
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#2b2b2b')
        
        # Настройка стиля
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        
        self.ax.set_xlabel('Время (с)')
        self.ax.set_ylabel('Напряжение (В)')
        self.ax.grid(True, alpha=0.2)
        
        # Линия сигнала
        self.signal_line, = self.ax.plot([], [], 'c-', linewidth=1.5, label='Сигнал')
        
        # Линия триггера
        self.trigger_line = self.ax.axhline(y=2.5, color='r', linestyle='--', alpha=0.7, label='Триггер')
        self.trigger_line.set_visible(False)
        
        self.ax.legend()
        self.ax.set_xlim(0, self.config.time_window)
        self.ax.set_ylim(0, 5)
        
    def setup_analyzer_panel(self, parent):
        """Панель анализатора"""
        analyzer_frame = ttk.LabelFrame(parent, text="Анализатор сигнала", padding=10)
        analyzer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Создаем фигуру для анализа
        self.analysis_fig = plt.Figure(figsize=(10, 4), facecolor='#1a1a1a')
        self.analysis_canvas = FigureCanvasTkAgg(self.analysis_fig, analyzer_frame)
        self.analysis_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Две оси для разных видов анализа
        self.fft_ax = self.analysis_fig.add_subplot(111)
        self.fft_ax.set_facecolor('#2b2b2b')
        self.fft_ax.tick_params(colors='white')
        self.fft_ax.set_title('Частотный спектр (FFT)', color='white')
        self.fft_ax.set_xlabel('Частота (Гц)', color='white')
        self.fft_ax.set_ylabel('Амплитуда', color='white')
        self.fft_ax.grid(True, alpha=0.2)
        
        self.fft_line, = self.fft_ax.plot([], [], 'y-', linewidth=1)
        
    def setup_plot_animation(self):
        """Настройка анимации графиков"""
        self.animation = FuncAnimation(
            self.fig, self.update_plots, 
            interval=50, blit=False, cache_frame_data=False
        )
        
    def update_plots(self, frame):
        """Обновление всех графиков"""
        self.update_oscilloscope_plot()
        self.update_analyzer_plot()
        
    def update_oscilloscope_plot(self):
        """Обновление осциллографа"""
        current_time = time.time()
        
        # Проверка связи
        if self.is_connected and not self.is_simulating:
            time_since_data = current_time - self.last_sync_time
            if time_since_data > 3.0:  # 3 секунды таймаут
                self.handle_communication_loss()
        
        # Обработка новых данных
        self.process_incoming_data()
        
        if len(self.time_data) > 1:
            times = list(self.time_data)
            voltages = list(self.voltage_data)
            
            # Нормализация времени
            recent_times = [t - times[-1] for t in times]
            self.signal_line.set_data(recent_times, voltages)
            
            # Автомасштабирование
            time_window = self.config.time_window
            self.ax.set_xlim(-time_window, 0)
            
            if voltages:
                margin = 0.5
                y_min, y_max = min(voltages), max(voltages)
                self.ax.set_ylim(y_min - margin, y_max + margin)
            
            # Обновление заголовка
            status = "СИМУЛЯЦИЯ" if self.is_simulating else "REAL-TIME"
            trigger_status = " ТРИГГЕР" if self.trigger_enabled else ""
            self.ax.set_title(f'Осциллограф | {status}{trigger_status} | '
                            f'Точек: {len(voltages)} | Ошибок: {self.error_count}', 
                            color='#00ffaa')
        
        self.canvas.draw_idle()
        self.update_status_display()
        self.update_quality_indicator()
    
    def update_analyzer_plot(self):
        """Обновление анализатора"""
        if len(self.voltage_data) < 10:
            return
            
        voltages = np.array(list(self.voltage_data))
        
        if self.analysis_var.get() == "fft":
            # FFT анализ
            N = len(voltages)
            if N > 1:
                # Убираем DC составляющую
                signal = voltages - np.mean(voltages)
                
                # FFT
                fft = np.fft.fft(signal)
                freqs = np.fft.fftfreq(N, 1/self.config.sample_rate)
                
                # Берем только положительные частоты
                idx = np.where(freqs > 0)
                freqs = freqs[idx]
                magnitude = np.abs(fft[idx]) / N
                
                self.fft_line.set_data(freqs, magnitude)
                self.fft_ax.set_xlim(0, min(50, np.max(freqs)))
                self.fft_ax.set_ylim(0, np.max(magnitude) * 1.1)
        
        self.analysis_canvas.draw_idle()
    
    def process_incoming_data(self):
        """Обработка входящих данных"""
        max_points = 20
        
        for _ in range(max_points):
            try:
                packet_type, data = self.data_queue.get_nowait()
                
                if packet_type == 'DATA':
                    voltage, timestamp = data
                    
                    # Применяем триггер
                    if self.trigger_enabled:
                        if self.trigger_armed:
                            # Проверяем условие триггера
                            if ((self.config.trigger_slope == "rising" and 
                                 voltage >= self.config.trigger_level) or
                                (self.config.trigger_slope == "falling" and 
                                 voltage <= self.config.trigger_level)):
                                self.trigger_armed = False
                                self.time_data.clear()
                                self.voltage_data.clear()
                        else:
                            # После срабатывания триггера добавляем данные
                            self.time_data.append(timestamp)
                            self.voltage_data.append(voltage)
                    else:
                        # Без триггера - просто добавляем
                        self.time_data.append(timestamp)
                        self.voltage_data.append(voltage)
                    
                    if self.is_recording:
                        self.recorded_data.append({
                            'timestamp': timestamp,
                            'voltage': voltage,
                            'frequency': self.frequency,
                            'amplitude': self.amplitude
                        })
                    
                    self.packet_count += 1
                    
            except Empty:
                break
    
    def update_status_display(self):
        """Обновление дисплея статуса"""
        if len(self.voltage_data) == 0:
            return
            
        voltages = list(self.voltage_data)
        
        # Расчет метрик
        v_rms = np.sqrt(np.mean(np.square(voltages)))
        v_peak = np.max(voltages)
        v_peak_to_peak = np.ptp(voltages)
        v_mean = np.mean(voltages)
        v_std = np.std(voltages)
        
        status_text = f"""Состояние: {"Подключено" if self.is_connected else "Отключено"}
Режим: {"Симуляция" if self.is_simulating else "Arduino"}
Качество связи: {self.connection_quality}%
Пакеты: {self.packet_count}
Ошибки: {self.error_count}

--- Сигнал ---
Vср.кв.: {v_rms:.3f} В
Vпик: {v_peak:.3f} В  
Vпик-пик: {v_peak_to_peak:.3f} В
Vсредн: {v_mean:.3f} В
Шум: {v_std:.3f} В

--- Генератор ---
Тип: {self.wave_combo.get()}
Частота: {self.frequency:.1f} Гц
Амплитуда: {self.amplitude:.1f} В

--- Запись ---
Режим: {"ВКЛ" if self.is_recording else "ВЫКЛ"}
Точек: {len(self.recorded_data)}"""
        
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(1.0, status_text)
    
    def update_quality_indicator(self):
        """Обновление индикатора качества связи в GUI"""
        quality = self.connection_quality
        
        # Цвет в зависимости от качества
        if quality >= 80:
            color = "green"
        elif quality >= 60:
            color = "orange"
        else:
            color = "red"
        
        # Обновление в основном потоке GUI
        def update_gui():
            self.quality_label.config(text=f"{quality}%", foreground=color)
            self.quality_bar['value'] = quality
            
            # Обновление индикатора подключения
            if self.is_connected:
                if quality >= 80:
                    status_text = "● Отличное соединение"
                    status_color = "green"
                elif quality >= 60:
                    status_text = "● Удовлетворительное соединение" 
                    status_color = "orange"
                else:
                    status_text = "● Плохое соединение"
                    status_color = "red"
                
                self.connection_indicator.config(text=status_text, foreground=status_color)
        
        if self.root and not self.shutdown_flag.is_set():
            self.root.after(0, update_gui)

    # Методы управления подключением
    def toggle_connection(self):
        """Переключение состояния подключения"""
        if not self.is_connected:
            self.connect_arduino()
        else:
            self.disconnect_arduino()
    
    def connect_arduino(self):
        """Подключение к Arduino"""
        try:
            port = self.port_combo.get()
            if not port:
                messagebox.showerror("Ошибка", "Выберите COM порт!")
                return
            
            self.serial_port = serial.Serial(
                port=port,
                baudrate=9600,
                timeout=1,
                write_timeout=1
            )
            
            # Даем время на подключение
            time.sleep(3)
            
            # Очищаем буфер
            self.serial_port.reset_input_buffer()
            
            self.is_connected = True
            self.is_simulating = False
            self.connection_quality = 100
            
            self.connect_btn.config(text="Отключить")
            self.connection_indicator.config(text="● Подключение...", foreground="orange")
            
            messagebox.showinfo("Успех", f"Подключено к Arduino на {port}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {str(e)}")
            self.connection_indicator.config(text=f"● Ошибка: {str(e)}", foreground="red")
    
    def disconnect_arduino(self):
        """Отключение от Arduino"""
        if self.serial_port:
            self.serial_port.close()
        self.is_connected = False
        self.connect_btn.config(text="Подключить")
        self.connection_indicator.config(text="● Отключено", foreground="red")
    
    # Методы управления генератором
    def on_parameter_change(self, event=None):
        """Изменение параметров генератора"""
        wave_types = {"Синус": 0, "Треугольник": 1, "Прямоугольник": 2, "Пилообразный": 3}
        self.wave_type = wave_types[self.wave_combo.get()]
    
    def on_frequency_change(self, value):
        """Изменение частоты"""
        self.frequency = float(value)
    
    def on_amplitude_change(self, value):
        """Изменение амплитуды"""
        self.amplitude = float(value)
    
    def send_all_parameters(self):
        """Отправка всех параметров на Arduino"""
        if self.is_connected and not self.is_simulating:
            command = f"{self.wave_type};{self.frequency:.1f};{self.amplitude:.1f}\n"
            self.command_queue.put(command)
    
    # Методы управления осциллографом
    def on_trigger_toggle(self):
        """Включение/выключение триггера"""
        self.trigger_enabled = self.trigger_var.get()
        self.trigger_line.set_visible(self.trigger_enabled)
        self.trigger_armed = True
    
    def on_trigger_level_change(self, value):
        """Изменение уровня триггера"""
        self.config.trigger_level = float(value)
        self.trigger_line.set_ydata([self.config.trigger_level])
    
    def toggle_recording(self):
        """Включение/выключение записи"""
        self.is_recording = not self.is_recording
        if self.is_recording:
            self.record_btn.config(text="Остановить запись")
            self.recorded_data = []
        else:
            self.record_btn.config(text="● Запись")
            if self.recorded_data:
                messagebox.showinfo("Запись", f"Записано {len(self.recorded_data)} точек")
    
    def save_data(self):
        """Сохранение данных"""
        if not self.recorded_data:
            messagebox.showwarning("Нет данных", "Сначала запишите данные!")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx"), ("All files", "*.*")])
        
        if filename:
            try:
                df = pd.DataFrame(self.recorded_data)
                if filename.endswith('.xlsx'):
                    df.to_excel(filename, index=False)
                else:
                    df.to_csv(filename, index=False)
                messagebox.showinfo("Успех", f"Данные сохранены в {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")
    
    # Методы анализатора
    def calibrate(self):
        """Калибровка осциллографа"""
        if self.is_connected and not self.is_simulating:
            self.command_queue.put("CAL\n")
            messagebox.showinfo("Калибровка", "Запущена калибровка Arduino")
        else:
            messagebox.showinfo("Калибровка", "Режим симуляции - калибровка не требуется")
    
    # Методы обработки ошибок и связи
    def handle_communication_loss(self):
        """Обработка потери связи"""
        self.connection_quality = max(0, self.connection_quality - 10)
        
        if self.connection_quality <= 50:
            self.logger.warning("Потеря связи с Arduino")
    
    # Рабочие потоки
    def start_worker_threads(self):
        """Запуск рабочих потоков"""
        # Поток для Serial
        self.serial_thread = threading.Thread(target=self.serial_worker, daemon=True)
        self.serial_thread.start()
    
    def serial_worker(self):
        """Рабочий поток для Serial"""
        rx_buffer = bytearray()
        
        while not self.shutdown_flag.is_set():
            try:
                if self.is_connected and self.serial_port and not self.is_simulating:
                    # Читаем доступные данные
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)
                        rx_buffer.extend(data)
                        
                        # Обрабатываем текстовые сообщения
                        text_data = rx_buffer.decode('utf-8', errors='ignore')
                        if '\n' in text_data:
                            lines = text_data.split('\n')
                            for line in lines[:-1]:
                                line = line.strip()
                                if line:
                                    self.logger.info(f"Arduino: {line}")
                                    if line.startswith("STATUS:"):
                                        self.handle_status_message(line[7:])
                            
                            # Удаляем обработанные данные
                            processed_bytes = len('\n'.join(lines[:-1] + ['']).encode('utf-8'))
                            if processed_bytes <= len(rx_buffer):
                                rx_buffer = rx_buffer[processed_bytes:]
                        
                        # Обрабатываем бинарные пакеты
                        while len(rx_buffer) >= 5:
                            if rx_buffer[0] == 0xAA and rx_buffer[1] == 0x55:
                                packet_type = rx_buffer[2]
                                
                                if packet_type == 0xD0:  # DATA packet
                                    adc_value = (rx_buffer[3] << 8) | rx_buffer[4]
                                    voltage = (adc_value / 1023.0) * 5.0
                                    
                                    # Добавляем данные
                                    self.data_queue.put(('DATA', (voltage, time.time())))
                                    self.last_sync_time = time.time()
                                    self.connection_quality = min(100, self.connection_quality + 2)
                                    
                                    # Удаляем обработанный пакет
                                    del rx_buffer[:5]
                                else:
                                    # Неизвестный тип пакета
                                    self.logger.warning(f"Неизвестный тип пакета: 0x{packet_type:02X}")
                                    del rx_buffer[:5]
                            else:
                                # Потеря синхронизации - удаляем первый байт
                                del rx_buffer[0]
                
                # Отправка команд
                if not self.command_queue.empty():
                    command = self.command_queue.get_nowait()
                    if self.is_connected and self.serial_port:
                        try:
                            self.serial_port.write(command.encode('utf-8'))
                        except serial.SerialException as e:
                            self.logger.error(f"Ошибка отправки команды: {e}")
                
                time.sleep(0.01)
                
            except serial.SerialException as e:
                self.error_count += 1
                self.logger.error(f"Serial error: {e}")
                if self.is_connected:
                    self.disconnect_arduino()
                time.sleep(1)
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Unexpected error in serial worker: {e}")
                time.sleep(0.1)
    
    def handle_status_message(self, status):
        """Обработка статусных сообщений"""
        if "READY" in status:
            self.connection_indicator.config(text="● Подключено", foreground="green")
        elif "CALIBRATION" in status:
            self.logger.info(f"Calibration: {status}")

# Запуск приложения
if __name__ == "__main__":
    print("Advanced Arduino Oscilloscope Pro v2.1")
    print("=" * 60)
    
    app = StableArduinoOscilloscope()
    
    try:
        app.root.mainloop()
    except KeyboardInterrupt:
        app.safe_shutdown()
    except Exception as e:
        logging.error(f"Critical error: {e}")
        app.safe_shutdown()