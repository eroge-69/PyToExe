# -*- coding: utf-8 -*-
import serial
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation
from collections import deque
import ctypes
import sys
import platform
import random

class BrakeForceMonitor:
    def __init__(self, root):
        self.root = root
        root.title("Монитор тормозных усилий с автотаррировкой")
        
        # Установка размера окна под разрешение 1920x1080
        self.screen_width = 1920
        self.screen_height = 1080
        root.geometry(f"{self.screen_width}x{self.screen_height}")
        
        # Настройка полноэкранного режима
        self.fullscreen_state = True
        root.attributes('-fullscreen', self.fullscreen_state)
        
        # Защита от выгорания экрана
        self.screen_saver_active = False
        self.screen_saver_last_update = time.time()
        self.screen_saver_delay = 300  # 5 минут бездействия
        self.screen_saver_label = None
        self.screen_saver_position = [0, 0]
        self.screen_saver_velocity = [3, 3]  # Увеличена скорость для большего экрана
        
        # Флаг для отслеживания достижения порога 500 Н·м
        self.threshold_reached = False
        
        # Предотвращение засыпания экрана
        self.prevent_sleep()
        
        # Инициализация данных
        self.data_queue = queue.Queue()
        self.max_points = 600  # Увеличено количество точек для большего экрана
        self.time_data = deque(maxlen=self.max_points)
        self.left_data = deque(maxlen=self.max_points)
        self.right_data = deque(maxlen=self.max_points)
        self.diff_data = deque(maxlen=self.max_points)
        
        self.max_left = 0.0
        self.max_right = 0.0
        self.max_diff = 0.0
        self.min_torque = 200.0  # Минимальное отображаемое усилие
        self.start_time = time.time()
        
        # Настройка графиков
        self.setup_plots()
        
        # Создание интерфейса
        self.create_interface()
        
        # Настройка последовательного порта
        self.baudrate = 9600
        self.ser = None
        self.connected = False
        self.emergency_stop = False
        self.is_calibrated = False
        
        # Поиск Arduino и подключение
        self.find_arduino()
        self.auto_connect_to_com4()
        
        # Запуск потоков
        self.running = True
        self.thread = threading.Thread(target=self.read_serial)
        self.thread.daemon = True
        self.thread.start()
        
        # Обновление интерфейса
        self.update_interface()
        
        # Привязка клавиш
        self.setup_key_bindings()
        
        root.protocol("WM_DELETE_WINDOW", self.on_close)

    def prevent_sleep(self):
        """Предотвращение засыпания экрана"""
        try:
            if platform.system() == 'Windows':
                ES_CONTINUOUS = 0x80000000
                ES_SYSTEM_REQUIRED = 0x00000001
                ES_DISPLAY_REQUIRED = 0x00000002
                ctypes.windll.kernel32.SetThreadExecutionState(
                    ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
            elif platform.system() == 'Linux':
                import subprocess
                subprocess.run(["xset", "s", "off"])
                subprocess.run(["xset", "-dpms"])
        except Exception as e:
            print(f"Ошибка предотвращения сна: {e}")

    def allow_sleep(self):
        """Разрешение засыпания экрана"""
        try:
            if platform.system() == 'Windows':
                ES_CONTINUOUS = 0x80000000
                ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            elif platform.system() == 'Linux':
                import subprocess
                subprocess.run(["xset", "s", "on"])
                subprocess.run(["xset", "+dpms"])
        except Exception as e:
            print(f"Ошибка разрешения сна: {e}")

    def setup_key_bindings(self):
        """Настройка горячих клавиш"""
        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.toggle_fullscreen)
        self.root.bind('<F5>', lambda e: self.reset())
        self.root.bind('<F12>', lambda e: self.do_emergency_stop())
        self.root.bind('<F1>', lambda e: self.auto_tare())
        self.root.bind('<Motion>', self.reset_screen_saver_timer)

    def reset_screen_saver_timer(self, event=None):
        """Сброс таймера защиты от выгорания при движении мыши"""
        self.screen_saver_last_update = time.time()
        if self.screen_saver_active:
            self.deactivate_screen_saver()

    def toggle_fullscreen(self, event=None):
        """Переключение полноэкранного режима"""
        self.fullscreen_state = not self.fullscreen_state
        self.root.attributes('-fullscreen', self.fullscreen_state)
        return "break"

    def auto_connect_to_com4(self):
        """Автоподключение к COM4"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        
        if 'COM4' in ports:
            self.port_combo.set('COM4')
            self.connect()
            time.sleep(2)  # Ожидание подключения
            if not self.connected:
                self.data_queue.put(("status", "Ошибка подключения к COM4", "red"))
        else:
            self.data_queue.put(("status", "COM4 не найден", "red"))

    def setup_plots(self):
        """Настройка графиков для 1920x1080"""
        self.fig = Figure(figsize=(16, 9), dpi=100, facecolor='#f0f0f0')  # Увеличены размеры для 16:9
        
        # График усилий
        self.ax1 = self.fig.add_subplot(211)
        self.ax1.set_title('Тормозные усилия (от 200 Н·м)', fontsize=18, pad=20)  # Увеличен шрифт
        self.ax1.set_ylabel('Усилие (Н·м)', fontsize=16)
        self.ax1.grid(True, linestyle='--', alpha=0.6)
        self.line_left, = self.ax1.plot([], [], 'r-', linewidth=4, label='Левое')  # Увеличена толщина линии
        self.line_right, = self.ax1.plot([], [], 'b-', linewidth=4, label='Правое')
        
        self.max_left_line = self.ax1.axhline(0, color='r', linestyle='--', alpha=0.5)
        self.max_right_line = self.ax1.axhline(0, color='b', linestyle='--', alpha=0.5)
        
        self.max_left_text = self.ax1.text(0.01, 0.86, '', transform=self.ax1.transAxes, 
                                          color='r', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))  # Увеличен шрифт
        self.max_right_text = self.ax1.text(0.01, 0.70, '', transform=self.ax1.transAxes, 
                                           color='b', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        self.ax1.legend(loc='upper right', fontsize=14)  # Увеличен шрифт
        self.ax1.set_ylim(0, 4000)
        self.ax1.set_xlim(0, 15)  # Увеличен диапазон по времени
        
        # График разницы с ограничением до 35%
        self.ax2 = self.fig.add_subplot(212)
        self.ax2.set_title('Разница усилий (макс. 35%)', fontsize=16, pad=20)
        self.ax2.set_xlabel('Время (с)', fontsize=16)
        self.ax2.set_ylabel('Разница (%)', fontsize=16)
        self.ax2.grid(True, linestyle='--', alpha=0.6)
        self.line_diff, = self.ax2.plot([], [], 'g-', linewidth=4, label='Разница')
        
        self.max_diff_line = self.ax2.axhline(0, color='g', linestyle='--', alpha=0.5)
        self.max_diff_text = self.ax2.text(0.01, 0.90, '', transform=self.ax2.transAxes, 
                                          color='g', fontsize=10, bbox=dict(facecolor='white', alpha=0.7))
        
        # Линия предела 35%
        self.limit_line = self.ax2.axhline(35, color='red', linestyle='-', alpha=0.7, linewidth=3)  # Увеличена толщина
        
        self.ax2.legend(loc='upper right', fontsize=14)
        self.ax2.set_ylim(0, 40)
        self.ax2.set_xlim(0, 15)  # Увеличен диапазон по времени

    def create_interface(self):
        """Создание интерфейса для 1920x1080"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 12))  # Увеличен базовый шрифт
        style.configure('TButton', font=('Arial', 12), padding=6)  # Увеличен шрифт и отступы
        style.configure('Emergency.TButton', font=('Arial', 14, 'bold'), foreground='red')  # Увеличен шрифт
        
        # Основной контейнер
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill='both', expand=True, padx=15, pady=15)  # Увеличены отступы
        
        # Фрейм управления
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill='x', pady=(0, 15))  # Увеличен отступ
        
        # Фрейм графиков
        self.graph_frame = ttk.Frame(self.main_frame)
        self.graph_frame.pack(fill='both', expand=True)
        
        # Панель управления
        self.setup_control_panel(control_frame)
        
        # Графики
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=8, pady=8)  # Увеличены отступы
        
        # Анимация графиков
        self.ani = animation.FuncAnimation(
            self.fig, 
            self.update_plots,
            interval=100, 
            blit=True,
            cache_frame_data=False
        )

    def setup_control_panel(self, parent):
        """Панель управления для 1920x1080"""
        # Левый индикатор
        left_frame = ttk.Frame(parent)
        left_frame.pack(side='left', expand=True, padx=60)  # Увеличены отступы
        
        ttk.Label(left_frame, text="ЛЕВОЕ УСИЛИЕ:", font=('Arial', 18, 'bold')).pack(pady=(0, 15))  # Увеличен шрифт
        self.left_label = ttk.Label(left_frame, text="0.0 Н·м", font=('Arial', 96, 'bold'))  # Увеличен шрифт
        self.left_label.pack(pady=(0, 30))  # Увеличен отступ
        
        # Максимальное левое усилие
        self.max_left_frame = ttk.Frame(left_frame)
        self.max_left_frame.pack(fill='x')
        ttk.Label(self.max_left_frame, text="Максимум:", font=('Arial', 16)).pack(side='left')  # Увеличен шрифт
        self.max_left_value = ttk.Label(self.max_left_frame, text="0.0 Н·м", font=('Arial', 16, 'bold'))
        self.max_left_value.pack(side='left', padx=(8, 0))  # Увеличен отступ
        
        # Правый индикатор
        right_frame = ttk.Frame(parent)
        right_frame.pack(side='left', expand=True, padx=60)  # Увеличены отступы
        
        ttk.Label(right_frame, text="ПРАВОЕ УСИЛИЕ:", font=('Arial', 18, 'bold')).pack(pady=(0, 15))
        self.right_label = ttk.Label(right_frame, text="0.0 Н·м", font=('Arial', 96, 'bold'))
        self.right_label.pack(pady=(0, 30))
        
        # Максимальное правое усилие
        self.max_right_frame = ttk.Frame(right_frame)
        self.max_right_frame.pack(fill='x')
        ttk.Label(self.max_right_frame, text="Максимум:", font=('Arial', 16)).pack(side='left')
        self.max_right_value = ttk.Label(self.max_right_frame, text="0.0 Н·м", font=('Arial', 16, 'bold'))
        self.max_right_value.pack(side='left', padx=(8, 0))
        
        # Максимальная разница (под правым индикатором)
        diff_frame = ttk.Frame(right_frame)
        diff_frame.pack(fill='x', pady=(15, 0))  # Увеличен отступ
        ttk.Label(diff_frame, text="Макс. разница:", font=('Arial', 16)).pack(side='left')
        self.max_diff_value = ttk.Label(diff_frame, text="0.0%", font=('Arial', 16, 'bold'))
        self.max_diff_value.pack(side='left', padx=(8, 0))
        
        # Кнопки управления
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(side='right', padx=30)  # Увеличен отступ
        
        ttk.Button(btn_frame, text="Автотаррировка (F1)", command=self.auto_tare, width=22).pack(fill='x', pady=8)  # Увеличены кнопки
        ttk.Button(btn_frame, text="Сбросить (F5)", command=self.reset, width=22).pack(fill='x', pady=8)
        ttk.Button(btn_frame, text="СТОП (F12)", command=self.do_emergency_stop,
                 style="Emergency.TButton", width=22).pack(fill='x', pady=8)
        
        # Выбор порта
        port_frame = ttk.Frame(btn_frame)
        port_frame.pack(fill='x', pady=12)  # Увеличен отступ
        
        ttk.Label(port_frame, text="Порт:", font=('Arial', 12)).pack(side='left')
        self.port_combo = ttk.Combobox(port_frame, width=14, font=('Arial', 12))  # Увеличен шрифт
        self.port_combo.pack(side='left', padx=8)  # Увеличен отступ
        ttk.Button(port_frame, text="Подключить", command=self.connect).pack(side='left')
        
        self.status_label = ttk.Label(btn_frame, text="Ожидание подключения", foreground="gray", font=('Arial', 12))
        self.status_label.pack(fill='x', pady=8)  # Увеличен отступ
        
        # Кнопка полноэкранного режима
        ttk.Button(btn_frame, text="Полный экран (F11/ESC)", 
                  command=self.toggle_fullscreen, width=22).pack(fill='x', pady=8)

    def update_plots(self, frame):
        """Обновление графиков"""
        if self.time_data:
            self.line_left.set_data(self.time_data, self.left_data)
            self.line_right.set_data(self.time_data, self.right_data)
            self.line_diff.set_data(self.time_data, self.diff_data)
            
            self.max_left_line.set_ydata([self.max_left, self.max_left])
            self.max_right_line.set_ydata([self.max_right, self.max_right])
            self.max_diff_line.set_ydata([self.max_diff, self.max_diff])
            
            self.max_left_text.set_text(f'Макс. левое: {self.max_left:.1f} Н·м')
            self.max_right_text.set_text(f'Макс. правое: {self.max_right:.1f} Н·м')
            self.max_diff_text.set_text(f'Макс. разница: {self.max_diff:.1f}%')
            
            current_time = self.time_data[-1]
            self.ax1.set_xlim(max(0, current_time-15), current_time+1)  # Увеличен диапазон
            self.ax2.set_xlim(max(0, current_time-15), current_time+1)
        
        return (self.line_left, self.line_right, self.line_diff,
                self.max_left_line, self.max_right_line, self.max_diff_line,
                self.max_left_text, self.max_right_text, self.max_diff_text)

    def update_interface(self):
        """Обновление интерфейса с защитой от выгорания"""
        try:
            while not self.data_queue.empty():
                data_type, *data = self.data_queue.get_nowait()
                
                if data_type == "data":
                    left, right, diff = data
                    self.process_measurements(left, right, diff)
                    
                    # Обновление цифровых индикаторов
                    self.left_label.config(text=f"{left:.1f} Н·м")
                    self.right_label.config(text=f"{right:.1f} Н·м")
                    
                    # Обновление максимальных значений
                    self.max_left_value.config(text=f"{self.max_left:.1f} Н·м")
                    self.max_right_value.config(text=f"{self.max_right:.1f} Н·м")
                    self.max_diff_value.config(text=f"{self.max_diff:.1f}%")
                    
                    # Проверка на запуск моторов (усилие > 200 Н·м)
                    if left > 200 or right > 200:
                        self.screen_saver_last_update = time.time()
                        if self.screen_saver_active:
                            self.deactivate_screen_saver()
                elif data_type == "status":
                    text, color = data
                    self.status_label.config(text=text, foreground=color)
                
        except queue.Empty:
            pass
        
        # Проверка необходимости активации защиты от выгорания
        if not self.screen_saver_active and (time.time() - self.screen_saver_last_update) > self.screen_saver_delay:
            self.activate_screen_saver()
        
        # Обновление позиции заставки
        if self.screen_saver_active:
            self.update_screen_saver_position()
            
        self.root.after(100, self.update_interface)

    def process_measurements(self, left, right, diff):
        """Обработка измерений с фильтрацией значений < 200 Н·м"""
        current_time = time.time() - self.start_time
        
        # Проверяем, достигнуто ли пороговое значение 500 Н·м
        if not self.threshold_reached and (left >= 500 or right >= 500):
            self.threshold_reached = True
            print("Порог 500 Н·м достигнут, начинаем расчет разницы")
        
        # Фильтрация значений менее 200 Н·м
        display_left = left if left >= 200 else 0
        display_right = right if right >= 200 else 0
        
        # Разницу считаем только после достижения порога 500 Н·м
        if self.threshold_reached:
            display_diff = diff if (left >= 200 and right >= 200) else 0
        else:
            display_diff = 0
        
        self.time_data.append(current_time)
        self.left_data.append(display_left)
        self.right_data.append(display_right)
        self.diff_data.append(display_diff)
        
        # Обновление максимумов только для значений >= 200 Н·м и после достижения порога
        if left >= 200 and right >= 200 and self.threshold_reached:
            self.max_left = max(self.max_left, left)
            self.max_right = max(self.max_right, right)
            self.max_diff = max(self.max_diff, diff)

    def activate_screen_saver(self):
        """Активация защиты от выгорания"""
        if not self.screen_saver_active:
            self.screen_saver_active = True
            
            # Создаем черный фон
            self.screen_saver_label = tk.Label(
                self.root, 
                bg='black', 
                fg='white',
                font=('Arial', 28),  # Увеличен шрифт
                text='Защита от выгорания экрана\nДвигайте мышью или нажмите любую клавишу'
            )
            
            # Размещаем поверх всего интерфейса
            self.screen_saver_label.place(relx=0.5, rely=0.5, anchor='center')
            
            # Начальная позиция для движущегося текста
            self.screen_saver_position = [
                random.randint(200, self.screen_width - 200),  # Учтено большее разрешение
                random.randint(200, self.screen_height - 200)
            ]
            self.screen_saver_velocity = [3, 3]  # Увеличена скорость

    def deactivate_screen_saver(self):
        """Деактивация защиты от выгорания"""
        if self.screen_saver_active:
            self.screen_saver_active = False
            if self.screen_saver_label:
                self.screen_saver_label.destroy()
                self.screen_saver_label = None

    def update_screen_saver_position(self):
        """Обновление позиции движущегося текста заставки"""
        if self.screen_saver_active and self.screen_saver_label:
            # Используем фиксированные размеры для 1920x1080
            width = self.screen_width
            height = self.screen_height
            
            # Обновляем позицию
            self.screen_saver_position[0] += self.screen_saver_velocity[0]
            self.screen_saver_position[1] += self.screen_saver_velocity[1]
            
            # Проверка столкновения с границами
            if self.screen_saver_position[0] <= 0 or self.screen_saver_position[0] >= width:
                self.screen_saver_velocity[0] *= -1
            if self.screen_saver_position[1] <= 0 or self.screen_saver_position[1] >= height:
                self.screen_saver_velocity[1] *= -1
            
            # Устанавливаем новую позицию
            self.screen_saver_label.place(
                x=self.screen_saver_position[0],
                y=self.screen_saver_position[1],
                anchor='center'
            )

    def read_serial(self):
        """Чтение данных с порта"""
        while self.running:
            if not self.connected:
                time.sleep(0.1)
                continue
                
            try:
                if self.ser and self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    self.process_serial_data(line)
            except Exception as e:
                print(f"Ошибка чтения: {e}")
                self.connected = False
                self.data_queue.put(("status", "Ошибка соединения", "red"))
                time.sleep(1)

    def process_serial_data(self, data):
        """Обработка данных с порта"""
        try:
            if "L:" in data and "R:" in data:
                left_str = right_str = None
                
                for part in data.split():
                    if part.startswith("L:"):
                        left_str = part[2:]
                    elif part.startswith("R:"):
                        right_str = part[2:]
                
                left = float(left_str) if left_str and left_str.replace('.','',1).isdigit() else 0.0
                right = float(right_str) if right_str and right_str.replace('.','',1).isdigit() else 0.0
                
                if left > 0 and right > 0:
                    diff = abs(left - right) / max(left, right) * 100
                else:
                    diff = 0.0
                
                self.data_queue.put(("data", left, right, diff))
                
                if "STATE:EMG_STOP" in data:
                    self.emergency_stop = True
                    self.data_queue.put(("status", "АВАРИЙНЫЙ СТОП", "red"))
            
            elif "Auto-taring complete" in data:
                self.is_calibrated = True
                self.data_queue.put(("status", "Автотаррировка завершена", "green"))
            
        except Exception as e:
            print(f"Ошибка обработка данных: {e}\nДанные: {data}")

    def find_arduino(self):
        """Поиск Arduino"""
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        for port in ports:
            if 'arduino' in port.lower() or 'ch340' in port.lower():
                self.port_combo.set(port)
                break
        else:
            if ports:
                self.port_combo.set(ports[0])

    def connect(self):
        """Подключение к порту"""
        if self.connected:
            self.disconnect()
            return
            
        port = self.port_combo.get()
        if not port:
            messagebox.showerror("Ошибка", "Выберите порт!")
            return
            
        try:
            self.ser = serial.Serial(port, self.baudrate, timeout=1)
            self.connected = True
            self.data_queue.put(("status", f"Подключено к {port}", "green"))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться:\n{e}")

    def disconnect(self):
        """Отключение от порта"""
        if self.ser and self.ser.is_open:
            self.ser.close()
        self.connected = False
        self.data_queue.put(("status", "Отключено", "red"))

    def auto_tare(self):
        """Автотаррировка"""
        if self.connected:
            try:
                self.ser.write(b'AUTO_TARE\n')
                self.data_queue.put(("status", "Выполняется автотаррировка...", "blue"))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка автотаррировки:\n{e}")
        else:
            messagebox.showwarning("Ошибка", "Сначала подключитесь к устройству")

    def do_emergency_stop(self):
        """Аварийная остановка"""
        if self.connected:
            try:
                self.ser.write(b'EMERGENCY_STOP\n')
            except Exception as e:
                print(f"Ошибка при отправке команды STOP: {e}")
        self.emergency_stop = True
        self.data_queue.put(("status", "АВАРИЙНЫЙ СТОП", "red"))

    def reset(self):
        """Сброс показаний"""
        self.max_left = 0.0
        self.max_right = 0.0
        self.max_diff = 0.0
        self.threshold_reached = False  # Сбрасываем флаг порога
        self.max_left_value.config(text="0.0 Н·м")
        self.max_right_value.config(text="0.0 Н·м")
        self.max_diff_value.config(text="0.0%")
        self.data_queue.put(("status", "Показания сброшены", "blue"))

    def on_close(self):
        """Закрытие программы"""
        self.running = False
        self.disconnect()
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)
        
        self.allow_sleep()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BrakeForceMonitor(root)
    root.mainloop()