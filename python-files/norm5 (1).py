import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import platform
import re
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import json
import os
import webbrowser

class PingWindow:
    def __init__(self, root, ip_address, ip_name=None):
        self.root = root
        self.ip_address = ip_address
        self.ip_name = ip_name or ip_address
        self.is_pinging = False
        self.ping_thread = None
        
        self.create_window()
        
    def create_window(self):
        self.window = tk.Toplevel(self.root)
        self.window.title(f"Ping Monitor - {self.ip_name} ({self.ip_address})")
        self.window.geometry("400x300")
        self.window.resizable(True, True)
        
        # Main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # IP display
        ip_frame = ttk.Frame(main_frame)
        ip_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ip_frame, text=f"Мониторинг:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(ip_frame, text=f"{self.ip_name} ({self.ip_address})", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="▶️ Старт", command=self.start_ping)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Стоп", command=self.stop_ping, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Статистика", padding="5")
        stats_frame.pack(fill=tk.X, pady=5)
        
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        ttk.Label(stats_grid, text="📤 Отправлено:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.sent_label = ttk.Label(stats_grid, text="0")
        self.sent_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="📥 Получено:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.received_label = ttk.Label(stats_grid, text="0")
        self.received_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="❌ Потеряно:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.lost_label = ttk.Label(stats_grid, text="0%")
        self.lost_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="📊 Средняя задержка:").grid(row=0, column=2, sticky=tk.W, padx=(20,0), pady=2)
        self.avg_ping_label = ttk.Label(stats_grid, text="0 ms")
        self.avg_ping_label.grid(row=0, column=3, sticky=tk.W, pady=2)
        
        ttk.Label(stats_grid, text="⏱️ Последняя задержка:").grid(row=1, column=2, sticky=tk.W, padx=(20,0), pady=2)
        self.last_ping_label = ttk.Label(stats_grid, text="0 ms")
        self.last_ping_label.grid(row=1, column=3, sticky=tk.W, pady=2)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="📝 Лог пингов", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Text widget with scrollbar
        self.log_text = tk.Text(log_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Initialize statistics
        self.sent_count = 0
        self.received_count = 0
        self.ping_times = []
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def get_ping_command(self, ip):
        """Возвращает команду ping в зависимости от ОС"""
        if platform.system().lower() == "windows":
            return ["ping", "-n", "1", "-w", "1000", ip]
        else:  # Linux/Mac
            return ["ping", "-c", "1", "-W", "1", ip]
        
    def extract_ping_time(self, output):
        """Извлекает время пинга из вывода команды"""
        output_lower = output.lower()
        
        if platform.system().lower() == "windows":
            patterns = [
                r'время[=<>](\d+)м?с',
                r'time[=<>](\d+)\s*ms',
                r'время[=<>](\d+)\s*мс'
            ]
        else:
            patterns = [
                r'time[=<>](\d+\.?\d*)\s*ms',
                r'time[=<>](\d+)\s*ms'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, output_lower)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        
        if platform.system().lower() == "windows":
            match = re.search(r'(\d+)\s*м?с\s*$', output_lower, re.MULTILINE)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        
        return None
        
    def ping_once(self, ip):
        """Выполняет один пинг и возвращает результат"""
        try:
            start_time = time.time()
            result = subprocess.run(
                self.get_ping_command(ip),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=5
            )
            ping_success = result.returncode == 0
            return ping_success, result.stdout, time.time() - start_time
        except subprocess.TimeoutExpired:
            return False, "Timeout", 0
        except Exception as e:
            return False, f"Error: {str(e)}", 0
        
    def ping_loop(self):
        """Основной цикл пинга"""
        while self.is_pinging:
            cycle_start = time.time()
            
            success, output, exec_time = self.ping_once(self.ip_address)
            self.sent_count += 1
            
            if success:
                self.received_count += 1
                ping_time = self.extract_ping_time(output)
                if ping_time is not None:
                    self.ping_times.append(ping_time)
                    log_message = f"[{time.strftime('%H:%M:%S')}] Ответ: время={ping_time:.1f}мс"
                    last_ping = f"{ping_time:.1f} ms"
                else:
                    estimated_time = exec_time * 1000
                    self.ping_times.append(estimated_time)
                    log_message = f"[{time.strftime('%H:%M:%S')}] Ответ: время≈{estimated_time:.1f}мс"
                    last_ping = f"{estimated_time:.1f} ms"
            else:
                log_message = f"[{time.strftime('%H:%M:%S')}] Таймаут"
                last_ping = "Timeout"
            
            self.window.after(0, self.update_ui, log_message, last_ping)
            
            elapsed = time.time() - cycle_start
            sleep_time = max(0, 1.0 - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
            
    def update_ui(self, log_message, last_ping):
        """Обновляет интерфейс из основного потока"""
        self.log_text.insert(tk.END, log_message + "\n")
        self.log_text.see(tk.END)
        
        self.sent_label.config(text=str(self.sent_count))
        self.received_label.config(text=str(self.received_count))
        
        if self.sent_count > 0:
            lost_percent = ((self.sent_count - self.received_count) / self.sent_count) * 100
            self.lost_label.config(text=f"{lost_percent:.1f}%")
        
        self.last_ping_label.config(text=last_ping)
        
        if self.ping_times:
            avg_ping = sum(self.ping_times) / len(self.ping_times)
            self.avg_ping_label.config(text=f"{avg_ping:.1f} ms")
        
    def start_ping(self):
        """Запускает пинг"""
        if self.is_pinging:
            return
            
        self.is_pinging = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.sent_count = 0
        self.received_count = 0
        self.ping_times = []
        self.log_text.delete(1.0, tk.END)
        
        self.ping_thread = threading.Thread(target=self.ping_loop, daemon=True)
        self.ping_thread.start()
        
    def stop_ping(self):
        """Останавливает пинг"""
        self.is_pinging = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
    def on_close(self):
        """Обработчик закрытия окна"""
        self.stop_ping()
        self.window.destroy()

class PingGraph:
    def __init__(self, parent, width=3, height=1.5):
        self.parent = parent
        self.width = width
        self.height = height
        self.data = deque(maxlen=100)  # Максимум 100 точек данных
        self.timestamps = deque(maxlen=100)
        
        # Создаем фигуру matplotlib
        self.fig = Figure(figsize=(width, height), dpi=50)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#f0f0f0')
        self.fig.patch.set_facecolor('#f0f0f0')
        
        # Настраиваем оси
        self.ax.set_ylim(0, 500)  # Диапазон пинга от 0 до 500 мс
        self.ax.tick_params(axis='both', which='major', labelsize=6)
        self.ax.grid(True, alpha=0.3)
        
        # Убираем подписи снизу
        self.ax.set_xticklabels([])
        
        # Создаем холст tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas.draw()
        self.widget = self.canvas.get_tk_widget()
        self.widget.config(width=width*50, height=height*50)
        
    def add_point(self, ping_time, timestamp):
        """Добавляет точку данных на график"""
        if ping_time is not None:
            self.data.append(ping_time)
            self.timestamps.append(timestamp)
            self.update_plot()
    
    def update_plot(self):
        """Обновляет график"""
        self.ax.clear()
        
        if self.data:
            # Преобразуем временные метки в относительное время
            if self.timestamps:
                start_time = self.timestamps[0]
                relative_times = [t - start_time for t in self.timestamps]
                
                self.ax.plot(relative_times, self.data, 'b-', linewidth=1)
                self.ax.fill_between(relative_times, self.data, alpha=0.3)
        
        self.ax.set_ylim(0, max(500, max(self.data) * 1.2 if self.data else 500))
        self.ax.grid(True, alpha=0.3)
        self.ax.tick_params(axis='both', which='major', labelsize=6)
        self.ax.set_facecolor('#f0f0f0')
        
        # Убираем подписи снизу
        self.ax.set_xticklabels([])
        
        self.canvas.draw()
    
    def resize(self, width, height):
        """Изменяет размер графика"""
        self.width = width
        self.height = height
        self.fig.set_size_inches(width, height)
        self.widget.config(width=width*50, height=height*50)
        self.update_plot()

class PingMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Multi IP Ping Monitor")
        self.root.geometry("900x700")  # Увеличил размер окна для графиков
        self.root.resizable(True, True)
        
        self.ping_windows = {}  # Словарь для отслеживания открытых окон
        self.status_indicators = []  # Индикаторы статуса для каждого IP
        self.ping_graphs = []  # Графики пинга для каждого IP
        self.status_thread = None
        self.is_monitoring = False
        
        # Настройки графиков по умолчанию
        self.graph_update_frequency = 1  # секунды
        self.graph_time_window = 60     # секунды
        self.graph_width = 3  # ширина графика по умолчанию
        self.graph_height = 1.5  # высота графика по умолчанию
        
        # Файл для сохранения настроек
        self.settings_file = "ping_monitor_settings.json"
        
        self.setup_ui()
        self.load_settings()  # Загружаем настройки при запуске
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="🌐 Мониторинг нескольких IP-адресов", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # IP list frame
        list_frame = ttk.LabelFrame(main_frame, text="📋 Список IP-адресов для мониторинга", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create main container for scrollable area
        container = ttk.Frame(list_frame)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create scrollable frame for IP list
        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack in correct order: scrollable area first, then scrollbar
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # IP entries list
        self.name_entries = []
        self.ip_entries = []
        self.ping_labels = []  # Метки для отображения текущего пинга
        self.browser_buttons = []  # Кнопки браузера
        self.delete_buttons = []
        self.row_frames = []  # Store reference to row frames for deletion
        
        # Control buttons frame - теперь содержит все элементы управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        
        # Левая часть - кнопки мониторинга
        left_control_frame = ttk.Frame(control_frame)
        left_control_frame.pack(side=tk.LEFT, padx=5)
        
        # Start monitoring button
        self.start_monitor_button = ttk.Button(left_control_frame, text="▶️ Запустить мониторинг", 
                                             command=self.start_monitoring)
        self.start_monitor_button.pack(side=tk.LEFT, padx=5)
        
        # Stop monitoring button
        self.stop_monitor_button = ttk.Button(left_control_frame, text="⏹️ Остановить мониторинг", 
                                            command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_monitor_button.pack(side=tk.LEFT, padx=5)
        
        # Центральная часть - настройки графиков
        center_control_frame = ttk.Frame(control_frame)
        center_control_frame.pack(side=tk.LEFT, padx=20)
        
        # Settings for graphs
        settings_label = ttk.Label(center_control_frame, text="📊 Настройки графиков:", font=('Arial', 9))
        settings_label.pack(anchor=tk.W)
        
        settings_grid = ttk.Frame(center_control_frame)
        settings_grid.pack(fill=tk.X, pady=2)
        
        ttk.Label(settings_grid, text="⏱️ Частота (сек):").grid(row=0, column=0, sticky=tk.W, padx=2)
        self.freq_var = tk.StringVar(value="1")
        freq_entry = ttk.Entry(settings_grid, textvariable=self.freq_var, width=6)
        freq_entry.grid(row=0, column=1, sticky=tk.W, padx=2)
        
        ttk.Label(settings_grid, text="🪟 Окно (сек):").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.window_var = tk.StringVar(value="60")
        window_entry = ttk.Entry(settings_grid, textvariable=self.window_var, width=6)
        window_entry.grid(row=0, column=3, sticky=tk.W, padx=2)
        
        ttk.Button(settings_grid, text="✅ Применить", 
                  command=self.apply_graph_settings).grid(row=0, column=4, padx=5)
        
        # Правая часть - кнопки управления
        right_control_frame = ttk.Frame(control_frame)
        right_control_frame.pack(side=tk.RIGHT, padx=5)
        
        # Save settings button
        ttk.Button(right_control_frame, text="💾 Сохранить", 
                  command=self.save_settings).pack(side=tk.RIGHT, padx=5)
        
        # Add button
        ttk.Button(right_control_frame, text="➕ Добавить IP", 
                  command=self.add_ip_row).pack(side=tk.RIGHT, padx=5)
        
        # Bottom frame for graph size settings
        bottom_frame = ttk.LabelFrame(main_frame, text="📐 Размер графиков", padding="10")
        bottom_frame.pack(fill=tk.X, pady=10)
        
        size_grid = ttk.Frame(bottom_frame)
        size_grid.pack(fill=tk.X)
        
        ttk.Label(size_grid, text="📏 Ширина:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.width_var = tk.StringVar(value=str(self.graph_width))
        width_entry = ttk.Entry(size_grid, textvariable=self.width_var, width=8)
        width_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(size_grid, text="📏 Высота:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.height_var = tk.StringVar(value=str(self.graph_height))
        height_entry = ttk.Entry(size_grid, textvariable=self.height_var, width=8)
        height_entry.grid(row=0, column=3, sticky=tk.W, padx=5)
        
        ttk.Button(size_grid, text="✅ Применить", 
                  command=self.apply_graph_size).grid(row=0, column=4, padx=10)
        
    def load_settings(self):
        """Загружает настройки из файла"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                
                # Очищаем существующие строки
                for row_frame in self.row_frames:
                    row_frame.destroy()
                
                self.name_entries.clear()
                self.ip_entries.clear()
                self.ping_labels.clear()
                self.browser_buttons.clear()
                self.delete_buttons.clear()
                self.row_frames.clear()
                self.status_indicators.clear()
                self.ping_graphs.clear()
                
                # Создаем строки из сохраненных данных
                if 'ip_list' in settings:
                    for ip_data in settings['ip_list']:
                        name = ip_data.get('name', '')
                        ip = ip_data.get('ip', '')
                        self.create_ip_row(name, ip)
                
                # Загружаем настройки графиков
                if 'graph_settings' in settings:
                    graph_settings = settings['graph_settings']
                    self.freq_var.set(str(graph_settings.get('frequency', 1)))
                    self.window_var.set(str(graph_settings.get('window', 60)))
                    self.width_var.set(str(graph_settings.get('width', 3)))
                    self.height_var.set(str(graph_settings.get('height', 1.5)))
                    
                    # Применяем настройки графиков
                    self.apply_graph_settings()
                    self.apply_graph_size()
                
                messagebox.showinfo("Успех", "Настройки загружены")
            else:
                # Создаем стандартные IP если файла нет
                default_names = [
                    "Google DNS 1", "Cloudflare 1", "Yandex DNS", "OpenDNS 1", "Google DNS 2"
                ]
                
                default_ips = [
                    "8.8.8.8", "1.1.1.1", "77.88.8.8", "208.67.222.222", "8.8.4.4"
                ]
                
                for i in range(5):
                    self.create_ip_row(default_names[i], default_ips[i])
                
                # Сохраняем стандартные настройки
                self.save_settings()
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки настроек: {e}")
    
    def save_settings(self):
        """Сохраняет настройки в файл"""
        try:
            settings = {
                'ip_list': [],
                'graph_settings': {
                    'frequency': float(self.freq_var.get()),
                    'window': float(self.window_var.get()),
                    'width': float(self.width_var.get()),
                    'height': float(self.height_var.get())
                }
            }
            
            # Сохраняем список IP
            for name_entry, ip_entry in zip(self.name_entries, self.ip_entries):
                name = name_entry.get().strip()
                ip = ip_entry.get().strip()
                if name or ip:  # Сохраняем только непустые записи
                    settings['ip_list'].append({
                        'name': name,
                        'ip': ip
                    })
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Успех", "Настройки сохранены")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения настроек: {e}")
        
    def apply_graph_settings(self):
        """Применяет настройки графиков"""
        try:
            new_freq = float(self.freq_var.get())
            new_window = float(self.window_var.get())
            
            if new_freq <= 0 or new_window <= 0:
                raise ValueError("Значения должны быть положительными")
                
            self.graph_update_frequency = new_freq
            self.graph_time_window = new_window
            
            # Обновляем максимальную длину данных для графиков
            max_points = int(new_window / new_freq)
            for graph in self.ping_graphs:
                graph.data = deque(graph.data, maxlen=max_points)
                graph.timestamps = deque(graph.timestamps, maxlen=max_points)
                graph.update_plot()
                
            messagebox.showinfo("Успех", "Настройки графиков применены")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
    
    def apply_graph_size(self):
        """Применяет размер графиков ко всем"""
        try:
            new_width = float(self.width_var.get())
            new_height = float(self.height_var.get())
            
            if new_width <= 0 or new_height <= 0:
                raise ValueError("Значения должны быть положительными")
                
            self.graph_width = new_width
            self.graph_height = new_height
            
            # Обновляем размер всех графиков
            for graph in self.ping_graphs:
                graph.resize(new_width, new_height)
                
            messagebox.showinfo("Успех", "Размер графиков обновлен")
            
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Некорректные значения: {e}")
        
    def create_status_indicator(self, parent):
        """Создает круглый индикатор статуса"""
        canvas = tk.Canvas(parent, width=20, height=20, highlightthickness=0)
        canvas.pack(side=tk.LEFT, padx=5)
        
        # Рисуем серый круг по умолчанию
        canvas.create_oval(2, 2, 18, 18, fill="gray", outline="")
        return canvas
        
    def update_status_indicator(self, canvas, status):
        """Обновляет цвет индикатора статуса"""
        canvas.delete("all")
        if status == "online":
            canvas.create_oval(2, 2, 18, 18, fill="green", outline="")
        elif status == "offline":
            canvas.create_oval(2, 2, 18, 18, fill="red", outline="")
        else:  # blinking state
            canvas.create_oval(2, 2, 18, 18, fill="gray", outline="")
        
    def create_ip_row(self, name="", ip=""):
        """Создает строку с полями для имени и IP"""
        row_frame = ttk.Frame(self.scrollable_frame)
        row_frame.pack(fill=tk.X, pady=3)
        self.row_frames.append(row_frame)
        
        # Status indicator
        status_indicator = self.create_status_indicator(row_frame)
        self.status_indicators.append({"canvas": status_indicator, "status": "unknown", "blink_state": False})
        
        # Name entry
        name_entry = ttk.Entry(row_frame, width=20)
        name_entry.pack(side=tk.LEFT, padx=2)
        name_entry.insert(0, name)
        self.name_entries.append(name_entry)
        
        # IP entry
        ip_entry = ttk.Entry(row_frame, width=15)
        ip_entry.pack(side=tk.LEFT, padx=2)
        ip_entry.insert(0, ip)
        self.ip_entries.append(ip_entry)
        
        # Ping label
        ping_label = ttk.Label(row_frame, text="0 ms", width=8, anchor="center", justify="center")
        ping_label.pack(side=tk.LEFT, padx=0)
        self.ping_labels.append(ping_label)
        
        # Graph
        graph_frame = ttk.Frame(row_frame)
        graph_frame.pack(side=tk.LEFT, padx=0, fill=tk.X, expand=True)  # Убрали отступы
        
        max_points = int(self.graph_time_window / self.graph_update_frequency)
        ping_graph = PingGraph(graph_frame, width=self.graph_width, height=self.graph_height)
        ping_graph.widget.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ping_graphs.append(ping_graph)
        
        # Browser button (слово "веб" вместо смайлика)
        browser_button = ttk.Button(row_frame, text="🌐 Веб",
                                  command=lambda idx=len(self.name_entries)-1: self.open_browser(idx))
        browser_button.pack(side=tk.LEFT, padx=1)  # Минимальные отступы
        self.browser_buttons.append(browser_button)
        
        # Delete button with "X"
        delete_button = ttk.Button(row_frame, text="❌ Удалить",
                                 command=lambda idx=len(self.name_entries)-1: self.delete_ip_row(idx))
        delete_button.pack(side=tk.RIGHT, padx=1)  # Минимальные отступы
        self.delete_buttons.append(delete_button)
        
        return row_frame
        
    def open_browser(self, index):
        """Открывает браузер с IP-адресом"""
        ip = self.ip_entries[index].get().strip()
        if not ip:
            messagebox.showerror("Ошибка", "Введите IP адрес")
            return
        
        # Пробуем открыть как URL (добавляем протокол если нужно)
        url = ip
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'
        
        try:
            webbrowser.open(url)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть браузер: {e}")
        
    def add_ip_row(self):
        """Добавляет новую строку для IP-адреса"""
        # Создаем новую строку в scrollable области
        self.create_ip_row(f"Новый IP {len(self.name_entries) + 1}", "")
        
        # Обновляем прокрутку
        self.scrollable_frame.update_idletasks()
        canvas = self.scrollable_frame.winfo_parent()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def delete_ip_row(self, index):
        """Удаляет строку с IP-адресом"""
        if len(self.name_entries) <= 1:
            messagebox.showinfo("Информация", "Нельзя удалить последний IP-адрес")
            return
            
        # Удаляем фрейм строки
        self.row_frames[index].destroy()
        
        # Удаляем элементы из списков
        self.row_frames.pop(index)
        self.name_entries.pop(index)
        self.ip_entries.pop(index)
        self.ping_labels.pop(index)
        self.browser_buttons.pop(index)
        self.delete_buttons.pop(index)
        self.status_indicators.pop(index)
        self.ping_graphs.pop(index)
        
        # Обновляем команды для оставшихся кнопок
        for i, (browser_button, delete_button) in enumerate(zip(self.browser_buttons, self.delete_buttons)):
            browser_button.configure(command=lambda idx=i: self.open_browser(idx))
            delete_button.configure(command=lambda idx=i: self.delete_ip_row(idx))
        
        # Обновляем прокрутку
        self.scrollable_frame.update_idletasks()
        canvas = self.scrollable_frame.winfo_parent()
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    def get_ping_command(self, ip):
        """Возвращает команду ping в зависимости от ОС"""
        if platform.system().lower() == "windows":
            return ["ping", "-n", "1", "-w", "1000", ip]
        else:
            return ["ping", "-c", "1", "-W", "1", ip]
        
    def extract_ping_time(self, output):
        """Извлекает время пинга из вывода команды"""
        output_lower = output.lower()
        
        if platform.system().lower() == "windows":
            patterns = [
                r'время[=<>](\d+)м?с',
                r'time[=<>](\d+)\s*ms',
                r'время[=<>](\d+)\s*мс'
            ]
        else:
            patterns = [
                r'time[=<>](\d+\.?\d*)\s*ms',
                r'time[=<>](\d+)\s*ms'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, output_lower)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    continue
        return None
        
    def ping_single_ip(self, ip):
        """Пингует один IP и возвращает результат"""
        try:
            result = subprocess.run(
                self.get_ping_command(ip),
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                timeout=5
            )
            success = result.returncode == 0
            ping_time = self.extract_ping_time(result.stdout) if success else None
            return success, ping_time
        except:
            return False, None
    
    def update_status_display(self, index):
        """Обновляет отображение статуса для конкретного индикатора"""
        indicator = self.status_indicators[index]
        if self.is_monitoring:
            # В режиме мониторинга - мигание
            if indicator["status"] == "online":
                # Зеленый/серый для онлайн
                color = "green" if indicator["blink_state"] else "gray"
            else:
                # Красный/серый для оффлайн
                color = "red" if indicator["blink_state"] else "gray"
            
            indicator["canvas"].delete("all")
            indicator["canvas"].create_oval(2, 2, 18, 18, fill=color, outline="")
            indicator["blink_state"] = not indicator["blink_state"]
        else:
            # Вне режима мониторинга - статический цвет
            if indicator["status"] == "online":
                self.update_status_indicator(indicator["canvas"], "online")
            elif indicator["status"] == "offline":
                self.update_status_indicator(indicator["canvas"], "offline")
            else:
                self.update_status_indicator(indicator["canvas"], "unknown")
    
    def toggle_editing(self, enabled):
        """Включает/выключает редактирование полей ввода"""
        state = tk.NORMAL if enabled else tk.DISABLED
        
        for ip_entry in self.ip_entries:
            ip_entry.config(state=state)
        
        # Поля имени всегда доступны для редактирования
        for name_entry in self.name_entries:
            name_entry.config(state=tk.NORMAL)
    
    def monitoring_loop(self):
        """Основной цикл мониторинга статуса"""
        blink_counter = 0
        last_graph_update = time.time()
        
        while self.is_monitoring:
            current_time = time.time()
            
            # Каждые 0.5 секунд обновляем статус (2 раза в секунду)
            if blink_counter % 2 == 0:  # Каждую секунду проверяем статус
                for i, (name_entry, ip_entry) in enumerate(zip(self.name_entries, self.ip_entries)):
                    ip = ip_entry.get().strip()
                    if ip and i < len(self.status_indicators):
                        success, ping_time = self.ping_single_ip(ip)
                        self.status_indicators[i]["status"] = "online" if success else "offline"
                        
                        # Обновляем отображение пинга
                        if success and ping_time is not None:
                            ping_text = f"{ping_time:.1f} ms"
                        else:
                            ping_text = "Timeout"
                        
                        self.root.after(0, lambda idx=i, text=ping_text: self.ping_labels[idx].config(text=text))
                        self.root.after(0, self.update_status_display, i)
            
            # Обновляем графики с заданной частотой
            if current_time - last_graph_update >= self.graph_update_frequency:
                for i, (name_entry, ip_entry) in enumerate(zip(self.name_entries, self.ip_entries)):
                    ip = ip_entry.get().strip()
                    if ip and i < len(self.ping_graphs):
                        success, ping_time = self.ping_single_ip(ip)
                        if success and ping_time is not None:
                            self.root.after(0, lambda idx=i, pt=ping_time, ts=current_time: 
                                          self.ping_graphs[idx].add_point(pt, ts))
                
                last_graph_update = current_time
            
            blink_counter += 1
            time.sleep(0.5)  # 2 обновления в секунду
    
    def start_monitoring(self):
        """Запускает мониторинг статуса"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.start_monitor_button.config(state=tk.DISABLED)
        self.stop_monitor_button.config(state=tk.NORMAL)
        
        # Блокируем редактирование IP-адресов
        self.toggle_editing(False)
        
        # Запускаем поток мониторинга
        self.status_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
        self.status_thread.start()
    
    def stop_monitoring(self):
        """Останавливает мониторинг статуса"""
        self.is_monitoring = False
        self.start_monitor_button.config(state=tk.NORMAL)
        self.stop_monitor_button.config(state=tk.DISABLED)
        
        # Разблокируем редактирование IP-адресов
        self.toggle_editing(True)
        
        # Сбрасываем все индикаторы в серый цвет
        for i, indicator in enumerate(self.status_indicators):
            indicator["status"] = "unknown"
            indicator["blink_state"] = False
            self.root.after(0, self.update_status_display, i)
            
        # Сбрасываем значения пинга
        for ping_label in self.ping_labels:
            ping_label.config(text="0 ms")

def main():
    root = tk.Tk()
    app = PingMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()