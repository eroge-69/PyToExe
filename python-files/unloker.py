import random
import string
import psutil
import os
import platform
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import webbrowser
from datetime import datetime
from PIL import Image, ImageTk
import hashlib
import threading
import time
import winreg
import requests


class AntivirusUnlockerPro(tk.Tk):
    def __init__(self):
        super().__init__()

        # Генерация уникального случайного имени (6 разных букв от A до Z)
        self.title(f"AV_{''.join(random.sample(string.ascii_uppercase, 6))}_{random.randint(100, 999)}")
        self.geometry("1300x900")
        self.minsize(1100, 750)


        # Скрытые атрибуты для обхода блокировок
        self.stealth_mode = False
        self.fake_process_names = ["svchost.exe", "explorer.exe", "System"]

        # База данных вирусов (можно расширить)
        self.virus_db = {
            "malware.exe": "Trojan.Win32.Generic",
            "cryptominer.exe": "Riskware.Win32.Miner",
            "ransomware.exe": "Trojan-Ransom.Win32.Generic"
        }

        # Настройка приложения
        self.set_icon()
        self.setup_styles()
        self.create_widgets()
        self.update_process_list()

        # Настройка автообновления
        self.auto_update_interval = 2500  # 2.5 секунды
        self.setup_auto_update()

        # Переменные для сортировки
        self.sort_column = 'memory'
        self.sort_reverse = True

        # Защита от закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Запуск фоновых проверок
        self.start_background_checks()

    def generate_random_name(self):
        """Генерация случайного имени для обхода блокировщиков"""
        prefixes = ["svc", "win", "sys", "net", "dll"]
        suffixes = ["host", "manager", "service", "helper", "update"]
        return f"{random.choice(prefixes)}_{random.choice(suffixes)}_{random.randint(1000, 9999)}"

    def set_icon(self):
        """Установка иконки из интернета (если локальная не найдена)"""
        try:
            img = Image.open("icon.png")
        except:
            try:
                # Попытка загрузить иконку из интернета
                response = requests.get("https://cdn-icons-png.flaticon.com/512/2889/2889676.png")
                img = Image.open(BytesIO(response.content))
            except:
                img = Image.new('RGB', (16, 16), color='gray')

        self.iconphoto(False, ImageTk.PhotoImage(img))

    def setup_styles(self):
        """Настройка стилей с защитным цветовым режимом"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Цветовая схема защиты
        bg_color = '#1e1e2d'
        fg_color = '#e0e0f0'
        accent_color = '#45aaf2'
        warning_color = '#ff4757'
        header_color = '#252538'
        select_color = '#3e3e5a'

        self.configure(bg=bg_color)
        self.style.configure('.', background=bg_color, foreground=fg_color)

        # Стиль для Treeview
        self.style.configure('Treeview', background=bg_color, foreground=fg_color,
                             fieldbackground=bg_color, rowheight=25, font=('Consolas', 9))
        self.style.configure('Treeview.Heading', background=header_color,
                             foreground=accent_color, font=('Segoe UI', 9, 'bold'))
        self.style.map('Treeview', background=[('selected', select_color)],
                       foreground=[('selected', fg_color)])

    def create_widgets(self):
        """Создание интерфейса с дополнительными защитными функциями"""
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Верхняя панель с кнопками защиты
        self.create_protection_toolbar(main_frame)

        # Панель быстрых действий
        self.create_quick_actions_panel(main_frame)

        # Таблица процессов с цветовой индикацией угроз
        self.create_process_tree(main_frame)

        # Нижняя панель с информацией и статусом
        self.create_status_panel(main_frame)

        # Скрытая панель для экспертных функций
        self.create_expert_panel(main_frame)

        # Окно для вывода сообщений
        self.create_message_window(main_frame)

        # Контекстное меню с дополнительными опциями
        self.setup_context_menu()

    def create_message_window(self, parent):
        """Создание окна для вывода сообщений"""
        message_frame = ttk.LabelFrame(parent, text="Сообщения системы", padding=5)
        message_frame.pack(fill=tk.X, pady=(10, 0))

        self.message_area = scrolledtext.ScrolledText(
            message_frame,
            wrap=tk.WORD,
            width=40,
            height=4,
            font=('Consolas', 9)
        )
        self.message_area.pack(fill=tk.BOTH, expand=True)
        self.message_area.configure(state='disabled')

    def log_message(self, message, msg_type='info'):
        """Вывод сообщения в окно сообщений"""
        self.message_area.configure(state='normal')

        # Цвета для разных типов сообщений
        colors = {
            'info': 'black',
            'warning': 'orange',
            'error': 'red',
            'success': 'green'
        }

        self.message_area.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n", msg_type)
        self.message_area.tag_config(msg_type, foreground=colors.get(msg_type, 'black'))
        self.message_area.see(tk.END)
        self.message_area.configure(state='disabled')

    def create_protection_toolbar(self, parent):
        """Панель инструментов защиты"""
        toolbar = ttk.Frame(parent)
        toolbar.pack(fill=tk.X, pady=(0, 10))

        protection_buttons = [
            ("🛡️ Защитить систему", self.run_system_protection),
            ("🔍 Проверить процессы", self.scan_for_malware),
            ("🧹 Очистить ОЗУ", self.clean_memory),
            ("🚫 Блокировать вирусы", self.block_viruses),
            ("👻 Скрытый режим", self.toggle_stealth_mode),
            ("⚡ Экстренная остановка", self.emergency_stop)
        ]

        for text, cmd in protection_buttons:
            btn = ttk.Button(toolbar, text=text, command=cmd, style='Bold.TButton')
            btn.pack(side=tk.LEFT, padx=2)

        self.style.configure('Bold.TButton', font=('Segoe UI', 9, 'bold'))

    def create_search_panel(self, parent):
        """Панель поиска процессов"""
        search_frame = ttk.Frame(parent)
        search_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.search_entry.bind('<KeyRelease>', self.filter_processes)

        search_btn = ttk.Button(search_frame, text="🔍", command=self.filter_processes, width=3)
        search_btn.pack(side=tk.LEFT, padx=2)

    def filter_processes(self, event=None):
        """Фильтрация процессов по введенному тексту"""
        search_term = self.search_var.get().lower()

        for child in self.tree.get_children():
            item = self.tree.item(child)
            process_name = item['values'][1].lower()
            if search_term in process_name:
                self.tree.selection_add(child)
                self.tree.focus(child)
                self.tree.see(child)
            else:
                self.tree.selection_remove(child)

    def create_quick_actions_panel(self, parent):
        """Панель быстрых действий"""
        quick_frame = ttk.Frame(parent)
        quick_frame.pack(fill=tk.X, pady=(0, 10))

        # Поиск с расширенными фильтрами
        self.create_search_panel(quick_frame)

        # Кнопки быстрого доступа
        actions_frame = ttk.Frame(quick_frame)
        actions_frame.pack(side=tk.RIGHT)

        quick_buttons = [
            ("🔄", self.update_process_list),
            ("⏹️", self.kill_selected_process),
            ("📂", self.open_selected_process_path),
            ("🔐", self.show_startup_manager),
            ("📌", self.toggle_topmost),
            ("🎭", self.change_window_name)
        ]

        for icon, cmd in quick_buttons:
            btn = ttk.Button(actions_frame, text=icon, command=cmd, width=3)
            btn.pack(side=tk.LEFT, padx=1)

    def create_process_tree(self, parent):
        """Таблица процессов с маркировкой угроз"""
        self.tree_frame = ttk.Frame(parent)
        self.tree_frame.pack(fill=tk.BOTH, expand=True)

        # Дополнительные колонки для информации об угрозах
        columns = ('pid', 'name', 'memory', 'cpu', 'status', 'user', 'threat', 'hash')

        self.tree = ttk.Treeview(self.tree_frame, columns=columns, show='headings')

        # Настройка колонок
        self.tree.heading('pid', text='PID', command=lambda: self.sort_column('pid'))
        self.tree.heading('name', text='Имя процесса', command=lambda: self.sort_column('name'))
        self.tree.heading('memory', text='ОЗУ (MB)', command=lambda: self.sort_column('memory'))
        self.tree.heading('cpu', text='CPU %', command=lambda: self.sort_column('cpu'))
        self.tree.heading('status', text='Статус', command=lambda: self.sort_column('status'))
        self.tree.heading('user', text='Пользователь', command=lambda: self.sort_column('user'))
        self.tree.heading('threat', text='Угроза', command=lambda: self.sort_column('threat'))
        self.tree.heading('hash', text='Хэш', command=lambda: self.sort_column('hash'))

        # Настройка ширины колонок
        widths = {'pid': 70, 'name': 220, 'memory': 90, 'cpu': 70,
                  'status': 90, 'user': 120, 'threat': 120, 'hash': 100}

        for col, width in widths.items():
            self.tree.column(col, width=width, anchor=tk.CENTER if col != 'name' else tk.W)

        # Добавляем полосу прокрутки
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Теги для цветовой маркировки
        self.tree.tag_configure('suspicious', foreground='orange')
        self.tree.tag_configure('malicious', foreground='red')
        self.tree.tag_configure('trusted', foreground='green')
        self.tree.tag_configure('system', foreground='#45aaf2')

        # Привязка контекстного меню
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<Double-1>', self.show_process_details)

    def create_status_panel(self, parent):
        """Панель статуса с информацией о защите"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(10, 0))

        # Информация о системе
        sys_info = ttk.Label(status_frame, text=self.get_system_info())
        sys_info.pack(side=tk.LEFT, padx=5)

        # Статус защиты
        self.protection_status = ttk.Label(status_frame, text="🟢 Защита активна", foreground="green")
        self.protection_status.pack(side=tk.LEFT, padx=20)

        # Счетчик угроз
        self.threat_count = ttk.Label(status_frame, text="Угроз: 0", foreground="white")
        self.threat_count.pack(side=tk.LEFT)

        # Время последнего обновления
        self.update_time = ttk.Label(status_frame, text="")
        self.update_time.pack(side=tk.RIGHT, padx=5)

        # Кнопка очистки сообщений
        clear_btn = ttk.Button(status_frame, text="Очистить логи", command=self.clear_messages, width=10)
        clear_btn.pack(side=tk.RIGHT, padx=5)

    def clear_messages(self):
        """Очистка окна сообщений"""
        self.message_area.configure(state='normal')
        self.message_area.delete(1.0, tk.END)
        self.message_area.configure(state='disabled')

    def create_expert_panel(self, parent):
        """Скрытая панель для экспертных функций"""
        self.expert_frame = ttk.Frame(parent)

        # Кнопка для показа/скрытия экспертной панели
        expert_btn = ttk.Button(parent, text="⚙️ Экспертный режим",
                                command=self.toggle_expert_panel, style='Small.TButton')
        expert_btn.pack(fill=tk.X, pady=(5, 0))

        self.style.configure('Small.TButton', font=('Segoe UI', 8))

        # Элементы экспертной панели (изначально скрыты)
        ttk.Label(self.expert_frame, text="MD5 хэш процесса:").pack(side=tk.LEFT, padx=5)
        self.hash_entry = ttk.Entry(self.expert_frame, width=40)
        self.hash_entry.pack(side=tk.LEFT, padx=5)

        check_btn = ttk.Button(self.expert_frame, text="Проверить в VirusTotal",
                               command=self.check_virustotal)
        check_btn.pack(side=tk.LEFT, padx=5)

        block_btn = ttk.Button(self.expert_frame, text="Добавить в черный список",
                               command=self.add_to_blacklist)
        block_btn.pack(side=tk.LEFT, padx=5)

        self.expert_shown = False

    def toggle_expert_panel(self):
        """Переключение видимости экспертной панели"""
        if self.expert_shown:
            self.expert_frame.pack_forget()
            self.log_message("Экспертный режим скрыт")
        else:
            self.expert_frame.pack(fill=tk.X, pady=(5, 0))
            self.log_message("Экспертный режим активирован")
        self.expert_shown = not self.expert_shown

    def setup_context_menu(self):
        """Контекстное меню с расширенными функциями"""
        self.context_menu = tk.Menu(self, tearoff=0)

        self.context_menu.add_command(label="Завершить процесс", command=self.kill_selected_process)
        self.context_menu.add_command(label="Завершить дерево процессов", command=self.kill_process_tree)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Открыть расположение файла", command=self.open_selected_process_path)
        self.context_menu.add_command(label="Скопировать путь", command=self.copy_process_path)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Проверить на вирусы", command=self.scan_selected_process)
        self.context_menu.add_command(label="Поиск в интернете", command=self.search_process_online)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Свойства", command=self.show_process_details)

        # Меню для добавления в черный/белый списки
        lists_menu = tk.Menu(self.context_menu, tearoff=0)
        lists_menu.add_command(label="Добавить в черный список", command=self.add_to_blacklist)
        lists_menu.add_command(label="Добавить в белый список", command=self.add_to_whitelist)
        self.context_menu.add_cascade(label="Списки доступа", menu=lists_menu)

    def show_context_menu(self, event):
        """Показать контекстное меню"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

            # Обновляем хэш в экспертной панели
            selected = self.tree.selection()
            if selected:
                item = self.tree.item(selected[0])
                pid = item['values'][0]
                self.update_hash_entry(pid)

    def update_hash_entry(self, pid):
        """Обновление поля хэша для выбранного процесса"""
        try:
            process = psutil.Process(pid)
            exe_path = process.exe()
            if os.path.exists(exe_path):
                file_hash = self.calculate_md5(exe_path)
                self.hash_entry.delete(0, tk.END)
                self.hash_entry.insert(0, file_hash)
                self.log_message(f"Хэш процесса {process.name()}: {file_hash}")
        except:
            self.hash_entry.delete(0, tk.END)
            self.hash_entry.insert(0, "Не удалось вычислить")
            self.log_message("Не удалось вычислить хэш процесса", 'error')

    def calculate_md5(self, file_path):
        """Вычисление MD5 хэша файла"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def update_process_list(self):
        """Обновление списка процессов"""
        for i in self.tree.get_children():
            self.tree.delete(i)

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status', 'username']):
            try:
                mem_usage = proc.info['memory_info'].rss / (1024 * 1024)  # в MB
                cpu_usage = proc.info['cpu_percent']
                status = proc.info['status']
                username = proc.info['username'].split('\\')[-1] if proc.info['username'] else "SYSTEM"

                # Проверка на вирусы
                threat = "Проверка..."
                tags = ()
                if proc.info['name'].lower() in self.virus_db:
                    threat = self.virus_db[proc.info['name'].lower()]
                    tags = ('malicious',)
                elif "system" in username.lower():
                    tags = ('system',)

                self.tree.insert('', 'end', values=(
                    proc.info['pid'],
                    proc.info['name'],
                    f"{mem_usage:.1f}",
                    f"{cpu_usage:.1f}",
                    status,
                    username,
                    threat,
                    ""
                ), tags=tags)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        self.update_time.config(text=f"Обновлено: {datetime.now().strftime('%H:%M:%S')}")
        self.log_message("Список процессов обновлен", 'info')

    def sort_column(self, col):
        """Сортировка по выбранной колонке"""
        if col == self.sort_column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = col
            self.sort_reverse = False

        # Получаем все элементы
        items = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]

        # Сортируем элементы
        try:
            items.sort(key=lambda x: float(x[0]), reverse=self.sort_reverse)
        except ValueError:
            items.sort(reverse=self.sort_reverse)

        # Перемещаем элементы в отсортированном порядке
        for index, (val, child) in enumerate(items):
            self.tree.move(child, '', index)

        # Обновляем заголовок с указанием направления сортировки
        self.tree.heading(col, command=lambda: self.sort_column(col))
        self.log_message(f"Сортировка по колонке: {col}", 'info')

    def scan_for_malware(self):
        """Сканирование всех процессов на наличие угроз"""
        threat_count = 0

        for child in self.tree.get_children():
            item = self.tree.item(child)
            process_name = item['values'][1].lower()

            # Проверка по базе данных вирусов
            threat = self.virus_db.get(process_name, None)
            if threat:
                self.tree.item(child, values=(*item['values'][:-2], threat, ""))
                self.tree.item(child, tags=('malicious',))
                threat_count += 1
                self.log_message(f"Обнаружен вредоносный процесс: {process_name} ({threat})", 'warning')
            elif any(name in process_name for name in self.fake_process_names):
                self.tree.item(child, values=(*item['values'][:-2], "Подозрительное имя", ""))
                self.tree.item(child, tags=('suspicious',))
                threat_count += 1
                self.log_message(f"Подозрительное имя процесса: {process_name}", 'warning')
            elif float(item['values'][3]) > 50:  # Высокая загрузка CPU
                self.tree.item(child, values=(*item['values'][:-2], "Высокая нагрузка", ""))
                self.tree.item(child, tags=('suspicious',))
                threat_count += 1
                self.log_message(f"Высокая нагрузка CPU процессом: {process_name}", 'warning')
            else:
                self.tree.item(child, values=(*item['values'][:-2], "Нет угроз", ""))
                self.tree.item(child, tags=('trusted',))

        self.threat_count.config(text=f"Угроз: {threat_count}")
        if threat_count > 0:
            self.protection_status.config(text="🔴 Обнаружены угрозы!", foreground="red")
            self.log_message(f"Обнаружено {threat_count} потенциальных угроз!", 'error')
        else:
            self.protection_status.config(text="🟢 Угроз не обнаружено", foreground="green")
            self.log_message("Угроз не обнаружено", 'success')

    def run_system_protection(self):
        """Запуск комплексной защиты системы"""
        self.protection_status.config(text="🟡 Сканирование...", foreground="orange")
        self.update()
        self.log_message("Запуск комплексной проверки системы...", 'info')

        # Сканирование процессов
        self.scan_for_malware()

        # Проверка автозагрузки
        self.check_startup_programs()

        # Очистка временных файлов
        self.clean_temp_files()

        self.protection_status.config(text="🟢 Защита активна", foreground="green")
        self.log_message("Комплексная проверка системы завершена", 'success')

    def block_viruses(self):
        """Блокировка обнаруженных вирусов"""
        count = 0

        for child in self.tree.get_children():
            item = self.tree.item(child)
            if item['values'][6] != "Нет угроз":  # Проверяем колонку "Угроза"
                try:
                    pid = item['values'][0]
                    p = psutil.Process(pid)
                    p.kill()
                    count += 1
                    self.log_message(f"Завершен процесс: {p.name()} (PID: {pid})", 'warning')
                except:
                    continue

        self.update_process_list()
        self.threat_count.config(text=f"Угроз: 0")
        self.protection_status.config(text="🟢 Угроз не обнаружено", foreground="green")
        self.log_message(f"Завершено {count} потенциально опасных процессов", 'success')

    def clean_memory(self):
        """Очистка памяти от ненужных процессов"""
        before_mem = psutil.virtual_memory().percent

        # Завершаем процессы с низким приоритетом
        for proc in psutil.process_iter():
            try:
                if proc.memory_percent() < 0.1 and proc.status() == 'sleeping':
                    proc.kill()
                    self.log_message(f"Очистка памяти: завершен процесс {proc.name()}", 'info')
            except:
                continue

        after_mem = psutil.virtual_memory().percent
        self.log_message(f"Освобождено памяти: {before_mem - after_mem:.1f}%", 'success')
        self.update_process_list()

    def toggle_stealth_mode(self):
        """Переключение скрытого режима"""
        self.stealth_mode = not self.stealth_mode

        if self.stealth_mode:
            # Маскируемся под системный процесс
            self.title(random.choice(self.fake_process_names))
            self.protection_status.config(text="👻 Скрытый режим", foreground="gray")
            self.log_message("Активирован скрытый режим (маскировка под системный процесс)", 'info')
        else:
            self.title(f"SystemHelper_{self.generate_random_name()}")
            self.protection_status.config(text="🟢 Защита активна", foreground="green")
            self.log_message("Скрытый режим деактивирован", 'info')

    def emergency_stop(self):
        """Экстренная остановка всех подозрительных процессов"""
        self.log_message("Запуск экстренной остановки подозрительных процессов...", 'warning')

        count = 0
        for proc in psutil.process_iter():
            try:
                if proc.name().lower() in self.virus_db or proc.memory_percent() > 20:
                    proc.kill()
                    count += 1
                    self.log_message(f"Экстренная остановка: завершен процесс {proc.name()}", 'warning')
            except:
                continue

        self.log_message(f"Экстренная остановка завершена. Завершено {count} процессов", 'info')
        self.update_process_list()

    def check_virustotal(self):
        """Проверка хэша на VirusTotal"""
        hash_value = self.hash_entry.get()
        if len(hash_value) == 32:  # MD5 хэш
            self.log_message(f"Проверка хэша {hash_value} на VirusTotal...", 'info')
            webbrowser.open(f"https://www.virustotal.com/gui/file/{hash_value}")
        else:
            self.log_message("Ошибка: введите корректный MD5 хэш", 'error')

    def add_to_blacklist(self):
        """Добавление процесса в черный список"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            process_name = item['values'][1].lower()

            if process_name not in self.virus_db:
                self.virus_db[process_name] = "Пользовательская блокировка"
                self.log_message(f"Процесс {process_name} добавлен в черный список", 'warning')
                self.scan_for_malware()
            else:
                self.log_message("Этот процесс уже в черном списке", 'info')

    def add_to_whitelist(self):
        """Добавление процесса в белый список"""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            process_name = item['values'][1].lower()

            if process_name in self.virus_db:
                del self.virus_db[process_name]
                self.log_message(f"Процесс {process_name} удален из черного списка", 'success')
                self.scan_for_malware()
            else:
                self.log_message("Этот процесс не в черном списке", 'info')

    def kill_selected_process(self):
        """Завершение выбранного процесса"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для завершения", 'error')
            return

        item = self.tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]

        try:
            p = psutil.Process(pid)
            p.kill()
            self.update_process_list()
            self.log_message(f"Процесс {name} (PID: {pid}) успешно завершен", 'success')
        except Exception as e:
            self.log_message(f"Не удалось завершить процесс: {e}", 'error')

    def kill_process_tree(self):
        """Завершение процесса и всех дочерних процессов"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для завершения", 'error')
            return

        item = self.tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]

        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)

            for child in children:
                try:
                    child.kill()
                    self.log_message(f"Завершен дочерний процесс: {child.name()} (PID: {child.pid})", 'warning')
                except:
                    continue

            parent.kill()
            self.update_process_list()
            self.log_message(f"Дерево процессов {name} (PID: {pid}) успешно завершено", 'success')
        except Exception as e:
            self.log_message(f"Не удалось завершить дерево процессов: {e}", 'error')

    def open_selected_process_path(self):
        """Открытие расположения файла процесса"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для открытия", 'error')
            return

        item = self.tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]

        try:
            process = psutil.Process(pid)
            exe_path = process.exe()
            dir_path = os.path.dirname(exe_path)
            os.startfile(dir_path)
            self.log_message(f"Открыто расположение файла: {exe_path}", 'info')
        except Exception as e:
            self.log_message(f"Не удалось открыть расположение файла: {e}", 'error')

    def copy_process_path(self):
        """Копирование пути к процессу в буфер обмена"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для копирования", 'error')
            return

        item = self.tree.item(selected[0])
        pid = item['values'][0]
        name = item['values'][1]

        try:
            process = psutil.Process(pid)
            exe_path = process.exe()
            self.clipboard_clear()
            self.clipboard_append(exe_path)
            self.log_message(f"Путь скопирован в буфер обмена: {exe_path}", 'success')
        except Exception as e:
            self.log_message(f"Не удалось получить путь: {e}", 'error')

    def scan_selected_process(self):
        """Проверка выбранного процесса на вирусы"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для проверки", 'error')
            return

        item = self.tree.item(selected[0])
        process_name = item['values'][1].lower()

        if process_name in self.virus_db:
            threat = self.virus_db[process_name]
            self.log_message(f"Обнаружена угроза! Процесс {process_name} идентифицирован как: {threat}", 'error')
        else:
            self.log_message(f"Процесс {process_name} не обнаружен в базе угроз", 'success')

    def search_process_online(self):
        """Поиск информации о процессе в интернете"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для поиска", 'error')
            return

        item = self.tree.item(selected[0])
        process_name = item['values'][1]
        self.log_message(f"Поиск информации о процессе {process_name} в интернете...", 'info')
        webbrowser.open(f"https://www.google.com/search?q={process_name}+process")

    def show_process_details(self, event=None):
        """Отображение подробной информации о процессе"""
        selected = self.tree.selection()
        if not selected:
            self.log_message("Не выбран процесс для просмотра", 'error')
            return

        item = self.tree.item(selected[0])
        pid = item['values'][0]

        try:
            process = psutil.Process(pid)
            details = (
                f"Имя процесса: {process.name()}\n"
                f"PID: {process.pid}\n"
                f"Статус: {process.status()}\n"
                f"Пользователь: {process.username()}\n\n"
                f"Использование CPU: {process.cpu_percent()}%\n"
                f"Использование памяти: {process.memory_info().rss / (1024 * 1024):.1f} MB\n\n"
                f"Путь к исполняемому файлу: {process.exe()}\n"
                f"Дата запуска: {datetime.fromtimestamp(process.create_time())}\n\n"
                f"Количество потоков: {process.num_threads()}\n"
                f"Приоритет: {process.nice()}"
            )

            self.log_message(f"Свойства процесса {process.name()} (PID: {pid}):\n{details}", 'info')
        except Exception as e:
            self.log_message(f"Не удалось получить информацию: {e}", 'error')

    def show_startup_manager(self):
        """Отображение менеджера автозагрузки"""
        self.log_message("Запуск менеджера автозагрузки...", 'info')
        startup_programs = []

        if platform.system() == "Windows":
            try:
                # Проверка автозагрузки текущего пользователя
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run"
                )

                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup_programs.append((name, value, "Current User"))
                        i += 1
                    except OSError:
                        break

                # Проверка системной автозагрузки
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run"
                )

                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        startup_programs.append((name, value, "All Users"))
                        i += 1
                    except OSError:
                        break

            except Exception as e:
                self.log_message(f"Не удалось проверить автозагрузку: {e}", 'error')
                return

        # Отображение списка программ в автозагрузке
        if startup_programs:
            top = tk.Toplevel(self)
            top.title("Менеджер автозагрузки")
            top.geometry("800x500")

            tree = ttk.Treeview(top, columns=('name', 'path', 'scope'), show='headings')
            tree.heading('name', text='Имя программы')
            tree.heading('path', text='Путь')
            tree.heading('scope', text='Область')
            tree.column('name', width=200)
            tree.column('path', width=450)
            tree.column('scope', width=150)

            for name, path, scope in startup_programs:
                tree.insert('', 'end', values=(name, path, scope))

            scrollbar = ttk.Scrollbar(top, orient=tk.VERTICAL, command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            tree.pack(fill=tk.BOTH, expand=True)

            # Кнопка удаления из автозагрузки
            def remove_from_startup():
                selected = tree.selection()
                if not selected:
                    return

                item = tree.item(selected[0])
                name = item['values'][0]
                scope = item['values'][2]

                try:
                    if scope == "Current User":
                        key = winreg.OpenKey(
                            winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_WRITE
                        )
                    else:
                        key = winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            0, winreg.KEY_WRITE
                        )

                    winreg.DeleteValue(key, name)
                    winreg.CloseKey(key)
                    tree.delete(selected[0])
                    self.log_message(f"Программа {name} удалена из автозагрузки", 'success')
                except Exception as e:
                    self.log_message(f"Не удалось удалить программу: {e}", 'error')

            remove_btn = ttk.Button(top, text="Удалить из автозагрузки", command=remove_from_startup)
            remove_btn.pack(pady=5)

            self.log_message("Менеджер автозагрузки запущен", 'info')
        else:
            self.log_message("Программ в автозагрузке не обнаружено", 'info')

    def check_startup_programs(self):
        """Проверка программ в автозагрузке"""
        self.log_message("Проверка программ в автозагрузке...", 'info')
        suspicious_count = 0

        if platform.system() == "Windows":
            try:
                # Проверка автозагрузки текущего пользователя
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\Microsoft\Windows\CurrentVersion\Run"
                )

                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if any(virus in value.lower() for virus in self.virus_db):
                            suspicious_count += 1
                            self.log_message(f"Подозрительная программа в автозагрузке: {name} ({value})", 'warning')
                        i += 1
                    except OSError:
                        break

                # Проверка системной автозагрузки
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    r"Software\Microsoft\Windows\CurrentVersion\Run"
                )

                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if any(virus in value.lower() for virus in self.virus_db):
                            suspicious_count += 1
                            self.log_message(f"Подозрительная программа в автозагрузке: {name} ({value})", 'warning')
                        i += 1
                    except OSError:
                        break

            except Exception as e:
                self.log_message(f"Не удалось проверить автозагрузку: {e}", 'error')

        if suspicious_count > 0:
            self.log_message(f"Обнаружено {suspicious_count} подозрительных программ в автозагрузке!", 'error')
        else:
            self.log_message("Подозрительных программ в автозагрузке не обнаружено", 'success')

    def clean_temp_files(self):
        """Очистка временных файлов"""
        self.log_message("Очистка временных файлов...", 'info')
        if platform.system() == "Windows":
            try:
                temp_dir = os.path.join(os.environ['TEMP'])
                count = 0

                for filename in os.listdir(temp_dir):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            count += 1
                    except:
                        continue

                self.log_message(f"Удалено {count} временных файлов", 'success')
            except Exception as e:
                self.log_message(f"Не удалось очистить временные файлы: {e}", 'error')

    def get_system_info(self):
        """Получение информации о системе"""
        info = f"""
        Система: {platform.system()} {platform.release()}
        Процессор: {platform.processor()}
        Память: {psutil.virtual_memory().total / (1024 ** 3):.1f} GB
        """
        return ' | '.join(line.strip() for line in info.split('\n') if line.strip())

    def show_help(self):
        """Отображение помощи"""
        help_text = """
        Antivirus Unlocker Pro - инструмент для борьбы с вирусами

        Основные функции:
        - Обнаружение и блокировка вредоносных процессов
        - Завершение подозрительных процессов
        - Проверка автозагрузки на наличие угроз
        - Очистка временных файлов
        - Скрытый режим для обхода блокировок

        Используйте контекстное меню (ПКМ) для доступа к дополнительным функциям.
        """
        self.log_message("Справка по программе:\n" + help_text, 'info')

    def on_close(self):
        """Обработчик закрытия окна"""
        self.log_message("Запрос на закрытие приложения...", 'info')
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите закрыть защитник?"):
            self.log_message("Приложение завершает работу", 'info')
            self.destroy()

    def setup_auto_update(self):
        """Настройка автоматического обновления списка процессов"""
        self.after(self.auto_update_interval, self.auto_update)

    def auto_update(self):
        """Автоматическое обновление списка процессов"""
        self.update_process_list()
        self.setup_auto_update()

    def toggle_topmost(self):
        """Переключение режима поверх всех окон"""
        is_topmost = not self.attributes('-topmost')
        self.attributes('-topmost', is_topmost)
        if is_topmost:
            self.log_message("Окно теперь поверх других окон", 'info')
        else:
            self.log_message("Обычный режим окна", 'info')

    def change_window_name(self):
        """Изменение имени окна"""
        new_name = simpledialog.askstring("Смена имени", "Введите новое имя окна:")
        if new_name:
            self.title(new_name)
            self.log_message(f"Имя окна изменено на: {new_name}", 'info')

    def start_background_checks(self):
        """Запуск фоновых проверок"""

        def checker():
            while True:
                try:
                    # Проверяем высокую загрузку CPU
                    for proc in psutil.process_iter():
                        try:
                            if proc.cpu_percent() > 90 and proc.pid != os.getpid():
                                self.log_message(
                                    f"Высокая нагрузка! Процесс {proc.name()} (PID: {proc.pid}) использует {proc.cpu_percent()}% CPU!",
                                    'warning'
                                )
                        except:
                            continue

                    # Проверяем использование памяти
                    if psutil.virtual_memory().percent > 90:
                        self.log_message(
                            f"Нехватка памяти! Используется {psutil.virtual_memory().percent}% ОЗУ!",
                            'warning'
                        )

                    # Задержка между проверками
                    time.sleep(10)
                except:
                    continue

        # Запускаем в отдельном потоке
        threading.Thread(target=checker, daemon=True).start()


if __name__ == "__main__":
    app = AntivirusUnlockerPro()
    app.mainloop()