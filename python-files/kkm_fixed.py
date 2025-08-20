import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import socket
import uuid
import datetime
import time
import select
import threading
import ipaddress
import subprocess
import sys
import os
from xml.etree import ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from ipaddress import ip_address, summarize_address_range

# Проверяем наличие pandas и пытаемся установить если нет
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("pandas не установлен. Попытка установки...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas", "openpyxl"])
        import pandas as pd
        PANDAS_AVAILABLE = True
        print("pandas успешно установлен!")
    except:
        print("Не удалось установить pandas автоматически")

class KKTCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("KKT Checker Pro")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2c3e50')
        
        # Конфигурация
        self.DEVICES_FILE = "devices.txt"
        self.STORE_MAPPING_FILE = "store_mapping.xlsx"
        self.RESULTS_FILE = "results.csv"
        self.DEFAULT_PORT = 6667
        self.SOCKET_TIMEOUT = 5
        self.MAX_WORKERS = 100
        self.TERMINATOR = b'\x00'
        self.MAX_IPS_PER_GATEWAY = 24
        
        # Переменные
        self.is_running = False
        self.results = []
        self.total_devices = 0
        self.checked_count = 0
        self.success_count = 0
        self.store_mapping = {}
        self.devices_to_check = []
        
        # Переменные для фильтров
        self.filter_vars = {
            'IP': tk.StringVar(),
            'Port': tk.StringVar(),
            'Status': tk.StringVar(),
            'FN_Serial': tk.StringVar(),
            'ExpirationDate': tk.StringVar(),
            'FW_Version': tk.StringVar(),
            'Address': tk.StringVar(),
            'Error': tk.StringVar(),
            'StoreName': tk.StringVar()
        }
        
        # Настройка стилей
        self.setup_styles()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Проверяем доступность pandas
        if not PANDAS_AVAILABLE:
            self.show_pandas_error()
        
        # Центрируем окно
        self.center_window()
    
    def show_pandas_error(self):
        """Показать сообщение об ошибке pandas"""
        error_msg = (
            "Библиотека pandas не установлена!\n\n"
            "Установите её вручную командой:\n"
            "pip install pandas openpyxl\n\n"
            "Или перезапустите приложение для автоматической установки."
        )
        messagebox.showerror("Ошибка", error_msg)
        self.status_var.set("Ошибка: pandas не установлен")
    
    def setup_styles(self):
        """Настройка современных стилей"""
        style = ttk.Style()
        
        # Современная темная тема
        style.theme_use('clam')
        
        # Конфигурация стилей
        style.configure('Modern.TFrame', background='#34495e')
        style.configure('Modern.TLabelframe', background='#2c3e50', foreground='white', 
                       font=('Segoe UI', 10, 'bold'))
        style.configure('Modern.TLabelframe.Label', background='#2c3e50', foreground='white')
        style.configure('Modern.TButton', background='#3498db', foreground='white', 
                       font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('Modern.TButton', 
                 background=[('active', '#2980b9'), ('pressed', '#21618c')])
        
        # Стиль для таблицы
        style.configure("Treeview",
                      background="#ecf0f1",
                      foreground="#2c3e50",
                      rowheight=28,
                      fieldbackground="#ecf0f1",
                      font=('Segoe UI', 9))
        style.configure("Treeview.Heading",
                      background="#3498db",
                      foreground="white",
                      font=('Segoe UI', 10, 'bold'))
        style.map('Treeview', background=[('selected', '#e74c3c')])
    
    def load_store_mapping(self, file_path):
        """Загрузка маппинга торговых точек из Excel файла"""
        if not PANDAS_AVAILABLE:
            self.show_pandas_error()
            return False
            
        try:
            # Читаем Excel файл
            df = pd.read_excel(file_path)
            
            # Проверяем необходимые колонки
            required_columns = ['Торговая Точка', 'IP адрес шлюза']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Ошибка", f"Файл должен содержать колонку '{col}'")
                    return False
            
            self.store_mapping = {}
            for _, row in df.iterrows():
                store_name = str(row['Торговая Точка']).strip()
                gateway_ip = str(row['IP адрес шлюза']).strip()
                
                if store_name and gateway_ip and gateway_ip != 'nan':
                    self.store_mapping[gateway_ip] = store_name
            
            messagebox.showinfo("Успех", f"Загружено {len(self.store_mapping)} записей маппинга")
            return True
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл маппинга: {str(e)}")
            return False
    
    def generate_ips_from_gateway(self, gateway_ip, store_name):
        """Генерация 23 IP адресов из подсети шлюза (исключая сам шлюз)"""
        try:
            # Создаем сеть на основе шлюза
            network = ipaddress.IPv4Network(f"{gateway_ip}/24", strict=False)
            ips = []
            
            # Генерируем все адреса сети, исключая шлюз и broadcast
            count = 0
            for ip in network.hosts():
                if count >= 23:  # Максимум 23 адреса (все кроме шлюза)
                    break
                
                # Пропускаем сам шлюз
                if str(ip) == gateway_ip:
                    continue
                
                ips.append({
                    'ip': str(ip),
                    'port': self.DEFAULT_PORT,
                    'gateway': gateway_ip,
                    'store_name': store_name
                })
                count += 1
            
            return ips
            
        except Exception as e:
            print(f"Ошибка генерации IP из шлюза {gateway_ip}: {e}")
            return []
    
    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="15", style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        title_label = tk.Label(header_frame, 
                              text="KKT CHECKER PRO", 
                              font=('Segoe UI', 20, 'bold'),
                              fg='#3498db',
                              bg='#2c3e50')
        title_label.pack(pady=10)
        
        subtitle_label = tk.Label(header_frame,
                                 text="Professional KKT Device Monitoring System with Store Mapping",
                                 font=('Segoe UI', 10),
                                 fg='#bdc3c7',
                                 bg='#2c3e50')
        subtitle_label.pack()
        
        # Панель управления
        control_frame = ttk.LabelFrame(main_frame, text="Управление", padding="12", style='Modern.TLabelframe')
        control_frame.pack(fill=tk.X, pady=(0, 12))
        
        # Кнопки управления
        button_frame = ttk.Frame(control_frame, style='Modern.TFrame')
        button_frame.pack(fill=tk.X, pady=8)
        
        # Создаем современные кнопки
        buttons = [
            ("📁 Загрузить маппинг Excel", self.load_store_mapping_file, '#f39c12'),
            ("🌐 Сгенерировать устройства", self.generate_devices, '#27ae60'),
            ("▶️ Запуск проверки", self.start_check, '#3498db'),
            ("⏹️ Остановить", self.stop_check, '#e74c3c'),
            ("💾 Экспорт результатов", self.export_results, '#9b59b6')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(button_frame, 
                          text=text,
                          command=command,
                          font=('Segoe UI', 10, 'bold'),
                          bg=color,
                          fg='white',
                          relief='flat',
                          bd=0,
                          padx=12,
                          pady=8,
                          cursor='hand2',
                          activebackground=self.darken_color(color),
                          activeforeground='white')
            btn.pack(side=tk.LEFT, padx=5)
        
        # Статус бар
        status_frame = tk.Frame(control_frame, bg='#34495e', relief='flat', height=40)
        status_frame.pack(fill=tk.X, pady=8)
        status_frame.pack_propagate(False)
        
        self.status_var = tk.StringVar(value="Готов к работе - загрузите Excel файл с маппингом")
        status_bar = tk.Label(status_frame, 
                             textvariable=self.status_var,
                             font=('Segoe UI', 10),
                             bg='#34495e',
                             fg='#ecf0f1',
                             padx=15,
                             pady=8)
        status_bar.pack(fill=tk.X)
        
        # Прогресс бар
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(status_frame, 
                                     variable=self.progress_var,
                                     maximum=100,
                                     style='Modern.Horizontal.TProgressbar')
        progress_bar.pack(fill=tk.X, padx=15, pady=(0, 8))
        
        # Параметры проверки
        params_frame = ttk.LabelFrame(main_frame, text="Параметры", padding="12", style='Modern.TLabelframe')
        params_frame.pack(fill=tk.X, pady=(0, 12))
        
        params_grid = tk.Frame(params_frame, bg='#34495e')
        params_grid.pack(fill=tk.X, pady=8, padx=5)
        
        # Параметры
        self.timeout_var = tk.StringVar(value=str(self.SOCKET_TIMEOUT))
        self.workers_var = tk.StringVar(value=str(self.MAX_WORKERS))
        self.port_var = tk.StringVar(value=str(self.DEFAULT_PORT))
        
        labels = [
            ("Таймаут (сек):", self.timeout_var, 0, 0),
            ("Потоков:", self.workers_var, 0, 2),
            ("Порт:", self.port_var, 0, 4),
        ]
        
        for text, var, row, col in labels:
            label = tk.Label(params_grid, text=text, bg='#34495e', fg='#ecf0f1', 
                           font=('Segoe UI', 9, 'bold'))
            label.grid(row=row, column=col, padx=8, pady=8, sticky='e')
            
            entry = tk.Entry(params_grid, textvariable=var, width=8, 
                           font=('Segoe UI', 10), bg='#ecf0f1', fg='#2c3e50',
                           relief='flat', bd=2, highlightthickness=1,
                           highlightcolor='#3498db', highlightbackground='#bdc3c7')
            entry.grid(row=row, column=col+1, padx=8, pady=8)
        
        # Статистика
        stats_frame = tk.Frame(params_grid, bg='#34495e')
        stats_frame.grid(row=0, column=6, columnspan=2, padx=20, pady=8, sticky='e')
        
        self.stats_var = tk.StringVar(value="Шлюзов: 0 | Устройств: 0 | Успешно: 0")
        stats_label = tk.Label(stats_frame, textvariable=self.stats_var,
                              bg='#34495e', fg='#ecf0f1', font=('Segoe UI', 9))
        stats_label.pack()
        
        # Таблица результатов
        results_container = ttk.LabelFrame(main_frame, text="Результаты", padding="12", style='Modern.TLabelframe')
        results_container.pack(fill=tk.BOTH, expand=True)
        
        # Фрейм для фильтры
        filter_frame = tk.Frame(results_container, bg='#34495e')
        filter_frame.pack(fill=tk.X, pady=(0, 8))
        
        tk.Label(filter_frame, text="Фильтры:", bg='#34495e', fg='#ecf0f1', 
                font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, padx=8, pady=8)
        
        # Упрощенные фильтры
        columns = ['IP', 'Status', 'FN_Serial', 'StoreName']
        for i, col in enumerate(columns):
            tk.Label(filter_frame, text=f"{col}:", bg='#34495e', fg='#ecf0f1',
                    font=('Segoe UI', 8)).grid(row=0, column=i*2+1, padx=4, pady=8)
            
            var = tk.StringVar()
            self.filter_vars[col] = var
            
            entry = tk.Entry(filter_frame, textvariable=var, width=12, 
                           bg='#ecf0f1', fg='#2c3e50', relief='flat', bd=1,
                           font=('Segoe UI', 8))
            entry.grid(row=0, column=i*2+2, padx=4, pady=8)
            entry.bind('<KeyRelease>', lambda e: self.apply_filters())
        
        # Кнопки фильтров
        filter_buttons = [
            ("Применить", self.apply_filters, '#27ae60'),
            ("Сбросить", self.reset_filters, '#e74c3c')
        ]
        
        for i, (text, command, color) in enumerate(filter_buttons):
            btn = tk.Button(filter_frame, text=text, command=command,
                          bg=color, fg='white', font=('Segoe UI', 8, 'bold'),
                          relief='flat', bd=0, padx=12, pady=4,
                          activebackground=self.darken_color(color))
            btn.grid(row=0, column=len(columns)*2+1+i, padx=6, pady=8)
        
        # Контейнер для таблицы
        table_container = tk.Frame(results_container, bg='#2c3e50')
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Таблица
        self.tree = ttk.Treeview(table_container, 
                                columns=('IP', 'Port', 'Status', 'FN_Serial', 'ExpirationDate', 'FW_Version', 'Address', 'Error', 'StoreName'), 
                                show='headings',
                                height=15)
        
        # Настройка колонок
        column_config = {
            'IP': ('IP', 120),
            'Port': ('Порт', 60),
            'Status': ('Статус', 100),
            'FN_Serial': ('Серийный № ФН', 120),
            'ExpirationDate': ('Окончание ФН', 120),
            'FW_Version': ('Версия ПО', 100),
            'Address': ('Адрес', 200),
            'Error': ('Ошибка', 200),
            'StoreName': ('Торговая Точка', 150)
        }
        
        for col, (heading, width) in column_config.items():
            self.tree.heading(col, text=heading)
            self.tree.column(col, width=width, anchor=tk.W)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Контекстное меню
        self.context_menu = tk.Menu(self.root, tearoff=0, bg='#34495e', fg='white',
                                  font=('Segoe UI', 9))
        self.context_menu.add_command(label="Копировать IP", command=self.copy_ip)
        self.context_menu.add_command(label="Подробности", command=self.show_details)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        # Добавляем нижнюю панель
        self.create_bottom_panel(main_frame)
    
    def load_store_mapping_file(self):
        """Загрузка Excel файла с маппингом торговых точек"""
        if not PANDAS_AVAILABLE:
            self.show_pandas_error()
            return
            
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите Excel файл с маппингом торговых точек",
                filetypes=(("Excel files", "*.xlsx *.xls"), ("Все файлы", "*.*")),
                initialfile="store_mapping.xlsx"
            )
            
            if file_path:
                if self.load_store_mapping(file_path):
                    self.status_var.set(f"Загружен маппинг: {len(self.store_mapping)} шлюзов")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить файл маппинга: {str(e)}")
    
    def generate_devices(self):
        """Генерация устройств на основе загруженного маппинга"""
        if not self.store_mapping:
            messagebox.showwarning("Предупреждение", "Сначала загрузите Excel файл с маппингом")
            return
        
        # Очистка предыдущих результатов
        self.results = []
        self.checked_count = 0
        self.success_count = 0
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Генерация устройств
        devices = []
        for gateway_ip, store_name in self.store_mapping.items():
            gateway_ips = self.generate_ips_from_gateway(gateway_ip, store_name)
            if gateway_ips:
                devices.extend(gateway_ips)
                print(f"Для шлюза {gateway_ip} сгенерировано {len(gateway_ips)} IP адресов")
        
        self.total_devices = len(devices)
        self.devices_to_check = devices
        self.status_var.set(f"Сгенерировано {self.total_devices} устройств из {len(self.store_mapping)} шлюзов")
        self.stats_var.set(f"Шлюзов: {len(self.store_mapping)} | Устройств: {self.total_devices} | Успешно: 0")
        
        messagebox.showinfo("Успех", f"Сгенерировано {self.total_devices} устройств для проверки")
    
    def darken_color(self, color):
        """Затемнение цвета для эффектов наведения"""
        if color.startswith('#'):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f'#{max(0, r-30):02x}{max(0, g-30):02x}{max(0, b-30):02x}'
        return color
    
    def create_bottom_panel(self, parent):
        """Создание нижней информационной панели"""
        bottom_frame = tk.Frame(parent, bg='#34495e', height=30, relief='flat')
        bottom_frame.pack(fill=tk.X, pady=(12, 0))
        bottom_frame.pack_propagate(False)
        
        # Индикатор статуса
        self.status_indicator = tk.Label(bottom_frame, 
                                       text="●",
                                       font=('Arial', 12),
                                       fg='#e74c3c',
                                       bg='#34495e')
        self.status_indicator.pack(side=tk.LEFT, padx=15)
        
        status_text = tk.Label(bottom_frame, 
                             text="Остановлено",
                             font=('Segoe UI', 9),
                             fg='#bdc3c7',
                             bg='#34495e')
        status_text.pack(side=tk.LEFT)
        
        # Версия
        version_text = tk.Label(bottom_frame, 
                              text="v2.1.0 | Store Mapping Edition",
                              font=('Segoe UI', 8),
                              fg='#95a5a6',
                              bg='#34495e')
        version_text.pack(side=tk.RIGHT, padx=15)
    
    def update_status_indicator(self):
        """Обновление индикатора статуса"""
        if self.is_running:
            self.status_indicator.config(fg='#27ae60')
            status_text = "● Работает"
        else:
            self.status_indicator.config(fg='#e74c3c')
            status_text = "● Остановлено"
        
        # Находим текстовый лейбл и обновляем его
        for widget in self.status_indicator.master.winfo_children():
            if isinstance(widget, tk.Label) and widget != self.status_indicator:
                widget.config(text=status_text)
                break
    
    def apply_filters(self):
        """Применение фильтров к таблице"""
        try:
            filters = {col: var.get().lower() for col, var in self.filter_vars.items()}
            
            for item in self.tree.get_children():
                values = [str(v).lower() for v in self.tree.item(item, 'values')]
                show = True
                
                for i, col in enumerate(self.tree['columns']):
                    if col in filters:
                        filter_text = filters[col]
                        if filter_text and filter_text not in values[i]:
                            show = False
                            break
                
                if show:
                    self.tree.item(item, tags=('visible',))
                else:
                    self.tree.item(item, tags=('hidden',))
            
            self.tree.tag_configure('visible', display='')
            self.tree.tag_configure('hidden', display='none')
            
        except Exception:
            pass
    
    def reset_filters(self):
        """Сброс всех фильтров"""
        for var in self.filter_vars.values():
            var.set('')
        self.apply_filters()
    
    def start_check(self):
        """Запуск проверки устройств"""
        if self.is_running:
            messagebox.showwarning("Предупреждение", "Проверка уже выполняется")
            return
        
        if not hasattr(self, 'devices_to_check') or not self.devices_to_check:
            messagebox.showwarning("Предупреждение", "Сначала сгенерируйте устройства из маппинга")
            return
        
        try:
            # Обновление параметров
            self.SOCKET_TIMEOUT = int(self.timeout_var.get())
            self.MAX_WORKERS = int(self.workers_var.get())
            self.DEFAULT_PORT = int(self.port_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Некорректные параметры")
            return
        
        # Запуск проверки в отдельном потоке
        self.is_running = True
        self.update_status_indicator()
        threading.Thread(target=self.run_check, daemon=True).start()
    
    def stop_check(self):
        """Остановка проверки"""
        self.is_running = False
        self.update_status_indicator()
        self.status_var.set("Проверка остановлена")
    
    def run_check(self):
        """Основная функция проверки"""
        devices = self.devices_to_check
        
        if not devices:
            self.root.after(0, lambda: messagebox.showwarning("Предупреждение", "Нет устройств для проверки"))
            self.is_running = False
            self.update_status_indicator()
            return
        
        self.total_devices = len(devices)
        
        # Подсчет уникальных торговых точек
        unique_stores = set(device['store_name'] for device in devices)
        
        self.root.after(0, lambda: self.status_var.set(f"Проверка: 0/{self.total_devices} (0 успешно)"))
        self.root.after(0, lambda: self.progress_var.set(0))
        self.root.after(0, lambda: self.stats_var.set(f"Шлюзов: {len(self.store_mapping)} | Устройств: {self.total_devices} | Успешно: 0"))
        
        # Параллельная проверка устройств
        start_time = time.time()
        
        try:
            with ThreadPoolExecutor(max_workers=min(self.MAX_WORKERS, 50)) as executor:
                futures = {executor.submit(self.check_device, device): device for device in devices}
                
                for future in as_completed(futures):
                    if not self.is_running:
                        executor.shutdown(wait=False)
                        break
                    
                    try:
                        result = future.result()
                        self.results.append(result)
                        self.checked_count += 1
                        
                        if result['Status'] == 'Success':
                            self.success_count += 1
                            self.root.after(0, self.add_result_to_tree, result)
                        
                        progress = self.checked_count / self.total_devices * 100
                        self.root.after(0, self.update_status, progress)
                        
                    except Exception:
                        self.checked_count += 1
                        progress = self.checked_count / self.total_devices * 100
                        self.root.after(0, self.update_status, progress)
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка при проверке: {str(e)}"))
        
        # Завершение
        elapsed_time = time.time() - start_time
        self.is_running = False
        self.update_status_indicator()
        
        self.root.after(0, lambda: messagebox.showinfo(
            "Завершено", 
            f"Проверка завершена за {elapsed_time:.2f} секунд\n"
            f"Проверено устройств: {self.checked_count} из {self.total_devices}\n"
            f"Найдено рабочих: {self.success_count}\n"
            f"Торговых точек: {len(unique_stores)}"
        ))
        
        self.root.after(0, lambda: self.status_var.set(
            f"Завершено: {self.checked_count}/{self.total_devices} ({self.success_count} успешно)"
        ))
        
        # Сохранение результатов
        self.save_results()
    
    def update_status(self, progress):
        """Обновление статус бара"""
        self.status_var.set(f"Проверка: {self.checked_count}/{self.total_devices} ({self.success_count} успешно) - {progress:.1f}%")
        self.progress_var.set(progress)
        
        # Подсчет уникальных торговых точек в результатах
        unique_stores = set()
        for result in self.results:
            if 'StoreName' in result:
                unique_stores.add(result['StoreName'])
        
        self.stats_var.set(f"Шлюзов: {len(self.store_mapping)} | Устройств: {self.total_devices} | Успешно: {self.success_count}")
    
    def add_result_to_tree(self, result):
        """Добавление результата в таблицу"""
        try:
            values = (
                result['IP'],
                result['Port'],
                result['Status'],
                result['FN_Serial'],
                result['ExpirationDate'],
                result['FW_Version'],
                result['Address'],
                result['Error'],
                result.get('StoreName', 'Неизвестно')
            )
            
            item = self.tree.insert("", tk.END, values=values)
            self.tree.see(item)
        except Exception:
            pass
    
    def check_device(self, device: dict) -> dict:
        """Проверка одного устройства"""
        ip = device['ip']
        port = device['port']
        store_name = device['store_name']
        
        device_info = {
            'IP': ip,
            'Port': port,
            'Timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Status': 'Не отвечает',
            'Error': '',
            'FN_Serial': '',
            'ShiftState': '',
            'LastDocNumber': '',
            'FW_Version': '',
            'IP_Address': '',
            'ExpirationDate': 'Не указана',
            'pa_1013': '',
            'Command50_Status': '',
            'Command50_Error': '',
            'Address': '',
            'StoreName': store_name
        }
        
        if not self.is_running:
            return device_info
        
        try:
            # 1. Подключение (команда 58)
            response = self.send_request(ip, port, 58)
            if not response:
                device_info['Error'] = 'Нет ответа на команду подключения'
                return device_info
            
            # 2. Запрос статуса (команда 2)
            status_response = self.send_request(ip, port, 2)
            if not status_response:
                device_info['Error'] = 'Нет ответа на запрос статуса'
                return device_info
            
            parsed_data = self.parse_response(status_response)
            device_info.update(parsed_data)
            
            # 3. Отправка команды 50 с FFD версией 4
            cmd50_response = self.send_request(ip, port, 50, 4)
            if cmd50_response:
                cmd50_data = self.parse_response(cmd50_response, command=50)
                device_info.update({
                    'Command50_Status': cmd50_data['Command50_Status'],
                    'Command50_Error': cmd50_data['Command50_Error'],
                    'Address': cmd50_data['Address']
                })
            else:
                device_info.update({
                    'Command50_Status': 'Error',
                    'Command50_Error': 'Нет ответа на команду 50'
                })
                
        except Exception as e:
            device_info['Error'] = f'Ошибка проверки: {str(e)}'
        
        return device_info
    
    def send_request(self, ip: str, port: int, command: int, ffd_version: int = 2) -> str:
        """Отправка запроса и получение ответа"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.SOCKET_TIMEOUT)
                s.connect((ip, port))
                
                request = self.create_request(command, ffd_version)
                s.sendall(request)
                
                response = b''
                while True:
                    ready, _, _ = select.select([s], [], [], self.SOCKET_TIMEOUT)
                    if ready:
                        data = s.recv(4096)
                        if not data:
                            break
                        response += data
                        if self.TERMINATOR in data:
                            break
                    else:
                        break

                return response.decode('utf-8', errors='ignore').strip() if response else ""
        except Exception:
            return ""
    
    def create_request(self, command: int, ffd_version: int = 2) -> bytes:
        """Создание XML-запроса"""
        try:
            request = ET.Element("ArmRequest")
            body = ET.SubElement(request, "RequestBody")
            
            ET.SubElement(body, "ProtocolLabel").text = "OFDFNARMUKM"
            ET.SubElement(body, "ProtocolVersion").text = "13.0"
            ET.SubElement(body, "RequestId").text = f"{{{uuid.uuid4()}}}"
            ET.SubElement(body, "DateTime").text = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ET.SubElement(body, "Command").text = str(command)
            ET.SubElement(body, "msgFFDVer").text = str(ffd_version)
            ET.SubElement(body, "msgContVer").text = "1"
            ET.SubElement(request, "RequestData").text = "<![CDATA[]]>"
            
            xml_data = ET.tostring(request, encoding='UTF-8')
            xml_declaration = b'<?xml version="1.0" encoding="UTF-8"?>\n'
            return xml_declaration + xml_data + self.TERMINATOR
        except Exception as e:
            raise Exception(f"Ошибка создания запроса: {str(e)}")
    
    def parse_response(self, response: str, command: int = None) -> dict:
        """Парсинг XML-ответа"""
        result = {
            'Status': 'Error',
            'Error': '',
            'FN_Serial': '',
            'ShiftState': '',
            'LastDocNumber': '',
            'FW_Version': '',
            'IP_Address': '',
            'ExpirationDate': 'Не указана',
            'pa_1013': '',
            'Command50_Status': '',
            'Command50_Error': '',
            'Address': ''
        }
        
        if not response or not response.startswith('<'):
            result['Error'] = 'Некорректный формат ответа'
            return result
            
        try:
            clean_response = response.replace('\x00', '').strip()
            root = ET.fromstring(clean_response)
            
            body = root.find('ResponseBody')
            if body is not None:
                result_code = body.find('Result')
                status = 'Success' if (result_code is not None and result_code.text == '0') else 'Error'
                
                if command == 50:
                    result['Command50_Status'] = status
                    error_desc = body.find('ErrorDescription')
                    result['Command50_Error'] = error_desc.text if error_desc is not None else ''
                else:
                    result['Status'] = status
                    error_desc = body.find('ErrorDescription')
                    result['Error'] = error_desc.text if error_desc is not None else ''
            
            data = root.find('ResponseData')
            if data is not None and data.text:
                try:
                    cdata = data.text.strip()
                    if cdata.startswith('<'):
                                               clean_cdata = cdata.replace('<![CDATA[', '').replace(']]>', '')
                        data_root = ET.fromstring(clean_cdata)
                        
                        for elem in data_root.iter():
                            if ('n' in elem.attrib and elem.attrib['n'] == 'ExpirationDate') or elem.tag == 'ExpirationDate':
                                if elem.text and elem.text.strip():
                                    result['ExpirationDate'] = elem.text.strip()
                            
                            if elem.tag == 'pa':
                                n = elem.get('n')
                                t = elem.get('t', '')
                                text = elem.text.strip() if elem.text else ''
                                
                                if n == "1041":
                                    result['FN_Serial'] = text
                                elif n == "ShiftState":
                                    result['ShiftState'] = text
                                elif n == "lastDocNumber":
                                    result['LastDocNumber'] = text
                                elif n == "KKTFWVersion":
                                    result['FW_Version'] = text
                                elif n == "1013" and t == "1":
                                    result['pa_1013'] = text if text else 'Не указано'
                                elif n == "NetworkInterface" and text and 'IP=' in text:
                                    result['IP_Address'] = text.split('IP=')[1].split()[0]
                                elif n == "1009" and t == "1":
                                    result['Address'] = text if text else 'Не указан'
                except ET.ParseError:
                    pass
                    
        except Exception as e:
            error_msg = f"Ошибка парсинга XML: {str(e)}"
            if command == 50:
                result['Command50_Error'] = error_msg
            else:
                result['Error'] = error_msg
        
        return result
    
    def save_results(self):
        """Сохранение результатов в CSV"""
        try:
            fieldnames = [
                'IP', 'Port', 'Timestamp', 'Status', 'Error',
                'FN_Serial', 'ShiftState', 'LastDocNumber',
                'FW_Version', 'IP_Address', 'ExpirationDate',
                'pa_1013', 'Command50_Status', 'Command50_Error',
                'Address', 'StoreName'
            ]
            
            with open(self.RESULTS_FILE, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
        except Exception as e:
            print(f"Ошибка сохранения результатов: {e}")
    
    def export_results(self):
        """Экспорт результатов в файл"""
        if not self.results:
            messagebox.showwarning("Предупреждение", "Нет данных для экспорта")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Экспорт результатов",
            filetypes=(("CSV файлы", "*.csv"), ("Все файлы", "*.*")),
            defaultextension=".csv",
            initialfile="kkt_results.csv"
        )
        
        if file_path:
            try:
                fieldnames = [
                    'IP', 'Port', 'Timestamp', 'Status', 'Error',
                    'FN_Serial', 'ShiftState', 'LastDocNumber',
                    'FW_Version', 'IP_Address', 'ExpirationDate',
                    'pa_1013', 'Command50_Status', 'Command50_Error',
                    'Address', 'StoreName'
                ]
                
                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.results)
                
                messagebox.showinfo("Успех", "Результаты успешно экспортированы")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать результаты: {str(e)}")
    
    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def copy_ip(self):
        """Копировать IP в буфер обмена"""
        selected_item = self.tree.selection()
        if selected_item:
            ip = self.tree.item(selected_item, 'values')[0]
            self.root.clipboard_clear()
            self.root.clipboard_append(ip)
            self.status_var.set(f"IP {ip} скопирован в буфер")
    
    def show_details(self):
        """Показать подробную информацию об устройстве"""
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, 'values')
            ip = values[0]
            
            for result in self.results:
                if result['IP'] == ip:
                    details = "\n".join([f"{k}: {v}" for k, v in result.items() if v])
                    messagebox.showinfo(f"Подробности для {ip}", details)
                    break

# Создаем батник для установки зависимостей
def create_install_bat():
    bat_content = '''@echo off
echo Установка зависимостей для KKT Checker...
python -m pip install --upgrade pip
pip install pandas openpyxl
echo Зависимости установлены!
pause
'''
    with open("install_dependencies.bat", "w", encoding='utf-8') as f:
        f.write(bat_content)

# Запуск приложения
if __name__ == "__main__":
    # Создаем батник для установки зависимостей
    create_install_bat()
    
    # Проверяем наличие pandas
    if not PANDAS_AVAILABLE:
        print("pandas не установлен. Запустите install_dependencies.bat для установки зависимостей")
        response = messagebox.askyesno(
            "Ошибка зависимостей", 
            "Библиотека pandas не установлена!\n\n"
            "Хотите запустить установку зависимостей?\n"
            "(Требуются права администратора)"
        )
        if response:
            try:
                subprocess.run("install_dependencies.bat", shell=True)
                # Перезапускаем приложение после установки
                os.execv(sys.executable, ['python'] + sys.argv)
            except:
                messagebox.showerror("Ошибка", "Не удалось установить зависимости")
        else:
            sys.exit(1)
    
    root = tk.Tk()
    app = KKTCheckerApp(root)
    root.mainloop()