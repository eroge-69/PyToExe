import os
import subprocess
import platform
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from threading import Thread
from queue import Queue
import winreg
import ctypes
from PIL import Image, ImageTk
import webbrowser

class ModernInstallerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Ultimate Driver & System Tool")
        self.root.geometry("1000x700")
        self.root.minsize(900, 600)
        
        # Очередь для обновления GUI из потока
        self.queue = Queue()
        
        # Стили
        self.setup_styles()
        
        # Иконки
        self.setup_icons()
        
        # Переменные
        self.dark_mode = tk.BooleanVar(value=False)
        self.os_info = self.get_os_info()
        self.office_info = self.check_office()
        
        self.create_widgets()
        self.check_queue()
        
        # Запускаем проверку системы
        self.update_system_info()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Светлая тема
        self.style.configure('.', background='#f0f0f0', foreground='black')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Segoe UI', 9))
        self.style.configure('TButton', font=('Segoe UI', 9), padding=6)
        self.style.configure('Treeview', font=('Segoe UI', 9), rowheight=25)
        self.style.configure('Treeview.Heading', font=('Segoe UI', 9, 'bold'))
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', font=('Segoe UI', 9))
        self.style.configure('TEntry', font=('Segoe UI', 9))
        self.style.configure('Status.TLabel', background='#e0e0e0', relief=tk.SUNKEN)
        
        # Темная тема
        self.style.map('Dark.TFrame', background=[('selected', '#404040')])
        self.style.map('Dark.TLabel', background=[('selected', '#404040')])
        self.style.map('Dark.TButton', background=[('selected', '#505050')])

    def setup_icons(self):
        try:
            self.driver_icon = ImageTk.PhotoImage(Image.open('driver.png').resize((16, 16)))
            self.system_icon = ImageTk.PhotoImage(Image.open('system.png').resize((16, 16)))
            self.office_icon = ImageTk.PhotoImage(Image.open('office.png').resize((16, 16)))
            self.activate_icon = ImageTk.PhotoImage(Image.open('activate.png').resize((16, 16)))
            self.settings_icon = ImageTk.PhotoImage(Image.open('settings.png').resize((16, 16)))
        except:
            # Заглушки если иконок нет
            self.driver_icon = None
            self.system_icon = None
            self.office_icon = None
            self.activate_icon = None
            self.settings_icon = None

    def create_widgets(self):
        # Главный контейнер
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Панель вкладок
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладка драйверов
        self.create_driver_tab()
        
        # Вкладка системы
        self.create_system_tab()
        
        # Вкладка Office
        self.create_office_tab()
        
        # Вкладка активации
        self.create_activation_tab()
        
        # Статус бар
        self.create_status_bar()
        
        # Меню
        self.create_menu()

    def create_driver_tab(self):
        self.driver_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.driver_tab, text="Драйверы", image=self.driver_icon, compound=tk.LEFT)
        
        # Панель управления
        control_frame = ttk.Frame(self.driver_tab)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(control_frame, text="Папка с драйверами:").pack(side=tk.LEFT)
        
        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(control_frame, textvariable=self.folder_path, width=50)
        self.folder_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        browse_btn = ttk.Button(control_frame, text="Обзор...", command=self.browse_folder)
        browse_btn.pack(side=tk.LEFT, padx=2)
        
        scan_btn = ttk.Button(control_frame, text="Сканировать", command=self.scan_drivers)
        scan_btn.pack(side=tk.LEFT, padx=2)
        
        self.install_btn = ttk.Button(control_frame, text="Установить выбранные", command=self.install_drivers, state=tk.DISABLED)
        self.install_btn.pack(side=tk.LEFT, padx=2)
        
        # Дерево драйверов
        tree_frame = ttk.Frame(self.driver_tab)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.drivers_tree = ttk.Treeview(tree_frame, columns=('type', 'status'), selectmode='extended')
        
        # Настройка колонок
        self.drivers_tree.column('#0', width=300, anchor=tk.W)
        self.drivers_tree.column('type', width=150, anchor=tk.W)
        self.drivers_tree.column('status', width=150, anchor=tk.W)
        
        # Заголовки
        self.drivers_tree.heading('#0', text='Драйвер')
        self.drivers_tree.heading('type', text='Тип')
        self.drivers_tree.heading('status', text='Статус')
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.drivers_tree.yview)
        self.drivers_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.drivers_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Лог
        log_frame = ttk.Frame(self.driver_tab)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        ttk.Label(log_frame, text="Лог установки:").pack(anchor=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=10)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(state=tk.DISABLED)

    def create_system_tab(self):
        self.system_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.system_tab, text="Система", image=self.system_icon, compound=tk.LEFT)
        
        # Информация о системе
        info_frame = ttk.LabelFrame(self.system_tab, text="Информация о системе")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.system_info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, width=80, height=15)
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.system_info_text.config(state=tk.DISABLED)
        
        # Кнопки
        button_frame = ttk.Frame(self.system_tab)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Обновить информацию", command=self.update_system_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Открыть параметры системы", command=self.open_system_properties).pack(side=tk.LEFT, padx=5)

    def create_office_tab(self):
        self.office_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.office_tab, text="Microsoft Office", image=self.office_icon, compound=tk.LEFT)
        
        # Информация об Office
        info_frame = ttk.LabelFrame(self.office_tab, text="Информация об Office")
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.office_info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, width=80, height=15)
        self.office_info_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.office_info_text.config(state=tk.DISABLED)
        
        # Кнопки
        button_frame = ttk.Frame(self.office_tab)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Обновить информацию", command=self.update_office_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Открыть приложение Office", command=self.open_office_app).pack(side=tk.LEFT, padx=5)

    def create_activation_tab(self):
        self.activation_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.activation_tab, text="Активация", image=self.activate_icon, compound=tk.LEFT)
        
        # Активация Windows
        win_frame = ttk.LabelFrame(self.activation_tab, text="Активация Windows")
        win_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(win_frame, text="Ключ продукта:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.win_key_entry = ttk.Entry(win_frame, width=30)
        self.win_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(win_frame, text="Активировать", command=self.activate_windows).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(win_frame, text="Загрузить из файла", command=lambda: self.load_key('win')).grid(row=0, column=3, padx=5, pady=5)
        
        # Активация Office
        office_frame = ttk.LabelFrame(self.activation_tab, text="Активация Office")
        office_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(office_frame, text="Ключ продукта:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        self.office_key_entry = ttk.Entry(office_frame, width=30)
        self.office_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        ttk.Button(office_frame, text="Активировать", command=self.activate_office).grid(row=0, column=2, padx=5, pady=5)
        
        ttk.Button(office_frame, text="Загрузить из файла", command=lambda: self.load_key('office')).grid(row=0, column=3, padx=5, pady=5)
        
        # Папка с ключами
        key_folder_frame = ttk.Frame(self.activation_tab)
        key_folder_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(key_folder_frame, text="Папка с ключами:").pack(side=tk.LEFT)
        
        self.key_folder_path = tk.StringVar()
        self.key_folder_entry = ttk.Entry(key_folder_frame, textvariable=self.key_folder_path, width=50)
        self.key_folder_entry.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        browse_btn = ttk.Button(key_folder_frame, text="Обзор...", command=self.browse_key_folder)
        browse_btn.pack(side=tk.LEFT)
        
        # Автоматическая активация
        auto_frame = ttk.Frame(self.activation_tab)
        auto_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(auto_frame, text="Автоактивация Windows", command=self.auto_activate_windows).pack(side=tk.LEFT, padx=5)
        ttk.Button(auto_frame, text="Автоактивация Office", command=self.auto_activate_office).pack(side=tk.LEFT, padx=5)
        
        # Лог активации
        log_frame = ttk.LabelFrame(self.activation_tab, text="Лог активации")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.activation_log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=10)
        self.activation_log_text.pack(fill=tk.BOTH, expand=True)
        self.activation_log_text.config(state=tk.DISABLED)

    def create_status_bar(self):
        status_frame = ttk.Frame(self.main_container)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        
        ttk.Label(status_frame, textvariable=self.status_var, style='Status.TLabel').pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Переключатель темы
        ttk.Checkbutton(status_frame, text="Темная тема", variable=self.dark_mode, 
                       command=self.toggle_theme).pack(side=tk.RIGHT, padx=5)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        help_menu.add_command(label="Помощь", command=self.show_help)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        self.root.config(menu=menubar)

    def toggle_theme(self):
        if self.dark_mode.get():
            # Темная тема
            self.root.configure(background='#404040')
            self.style.theme_use('alt')
            self.style.configure('.', background='#404040', foreground='white')
            self.style.configure('TFrame', background='#404040')
            self.style.configure('TLabel', background='#404040', foreground='white')
            self.style.configure('Treeview', background='#505050', foreground='white', fieldbackground='#505050')
            self.style.configure('Treeview.Heading', background='#404040', foreground='white')
            self.style.configure('TNotebook', background='#404040')
            self.style.configure('TNotebook.Tab', background='#404040', foreground='white')
            self.style.configure('Status.TLabel', background='#505050', foreground='white')
        else:
            # Светлая тема
            self.root.configure(background='#f0f0f0')
            self.style.theme_use('clam')
            self.style.configure('.', background='#f0f0f0', foreground='black')
            self.style.configure('TFrame', background='#f0f0f0')
            self.style.configure('TLabel', background='#f0f0f0', foreground='black')
            self.style.configure('Treeview', background='white', foreground='black', fieldbackground='white')
            self.style.configure('Treeview.Heading', background='#f0f0f0', foreground='black')
            self.style.configure('TNotebook', background='#f0f0f0')
            self.style.configure('TNotebook.Tab', background='#f0f0f0', foreground='black')
            self.style.configure('Status.TLabel', background='#e0e0e0', foreground='black')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(title="Выберите папку с драйверами")
        if folder_selected:
            self.folder_path.set(folder_selected)

    def browse_key_folder(self):
        folder_selected = filedialog.askdirectory(title="Выберите папку с ключами")
        if folder_selected:
            self.key_folder_path.set(folder_selected)

    def scan_drivers(self):
        folder = self.folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Укажите корректную папку с драйверами")
            return
        
        # Очищаем дерево
        for item in self.drivers_tree.get_children():
            self.drivers_tree.delete(item)
        
        self.log("Сканирование папки с драйверами...")
        self.status_var.set("Сканирование папки с драйверами...")
        
        # Сканируем в отдельном потоке
        Thread(target=self._scan_drivers_thread, args=(folder,), daemon=True).start()

    def _scan_drivers_thread(self, folder):
        drivers_found = []
        
        for root, dirs, files in os.walk(folder):
            for file in files:
                if file.lower().endswith('.inf'):
                    driver_path = os.path.join(root, file)
                    driver_type = self.detect_driver_type(driver_path)
                    drivers_found.append((driver_path, driver_type))
        
        # Обновляем GUI через очередь
        self.queue.put(('update_drivers_list', drivers_found))
        self.queue.put(('log', f"Найдено {len(drivers_found)} драйверов"))
        self.queue.put(('status', "Готов к установке"))

    def detect_driver_type(self, driver_path):
        # Простая эвристика для определения типа драйвера
        filename = os.path.basename(driver_path).lower()
        folder = os.path.basename(os.path.dirname(driver_path)).lower()
        
        if 'lan' in filename or 'lan' in folder or 'ethernet' in filename or 'ethernet' in folder:
            return 'LAN'
        elif 'wifi' in filename or 'wifi' in folder or 'wireless' in filename or 'wireless' in folder:
            return 'WiFi'
        elif 'bluetooth' in filename or 'bluetooth' in folder or 'bt' in filename or 'bt' in folder:
            return 'Bluetooth'
        elif 'audio' in filename or 'audio' in folder or 'sound' in filename or 'sound' in folder:
            return 'Audio'
        elif 'chipset' in filename or 'chipset' in folder:
            return 'Chipset'
        elif 'vga' in filename or 'vga' in folder or 'graphic' in filename or 'graphic' in folder:
            return 'GPU'
        elif 'touchpad' in filename or 'touchpad' in folder:
            return 'Touchpad'
        elif 'camera' in filename or 'camera' in folder or 'webcam' in filename or 'webcam' in folder:
            return 'Camera'
        else:
            return 'Другое'

    def install_drivers(self):
        selected_items = self.drivers_tree.selection()
        if not selected_items:
            messagebox.showwarning("Предупреждение", "Выберите драйверы для установки")
            return
        
        drivers_to_install = []
        for item in selected_items:
            driver_path = self.drivers_tree.item(item, 'values')[0]
            drivers_to_install.append(driver_path)
        
        self.log(f"Начало установки {len(drivers_to_install)} драйверов...")
        self.status_var.set(f"Установка {len(drivers_to_install)} драйверов...")
        self.install_btn.config(state=tk.DISABLED)
        
        # Устанавливаем в отдельном потоке
        Thread(target=self._install_drivers_thread, args=(drivers_to_install,), daemon=True).start()

    def _install_drivers_thread(self, drivers):
        for driver in drivers:
            self.queue.put(('log', f"Установка драйвера: {driver}"))
            
            try:
                result = subprocess.run(
                    ['pnputil', '/add-driver', driver, '/install'],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self.queue.put(('log', "Установка успешна!"))
                self.queue.put(('log', result.stdout))
                self.queue.put(('update_driver_status', driver, "Установлен", "green"))
            except subprocess.CalledProcessError as e:
                self.queue.put(('log', f"Ошибка при установке драйвера:"))
                self.queue.put(('log', e.stderr))
                self.queue.put(('update_driver_status', driver, "Ошибка", "red"))
            except Exception as e:
                self.queue.put(('log', f"Неизвестная ошибка:"))
                self.queue.put(('log', str(e)))
                self.queue.put(('update_driver_status', driver, "Ошибка", "red"))
        
        self.queue.put(('status', "Установка завершена"))
        self.queue.put(('install_complete',))

    def get_os_info(self):
        os_info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'bits': '64-bit' if platform.machine().endswith('64') else '32-bit',
            'edition': self.get_windows_edition(),
            'activated': self.check_windows_activation()
        }
        return os_info

    def get_windows_edition(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
            product_name, _ = winreg.QueryValueEx(key, "ProductName")
            winreg.CloseKey(key)
            return product_name
        except:
            return "Неизвестная версия"

    def check_windows_activation(self):
        try:
            result = subprocess.run(['cscript', os.path.join(os.environ['SYSTEMROOT'], 'System32', 'slmgr.vbs'), '/dli'], 
                                  capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            return "Активирована" if "licensed" in result.stdout.lower() else "Не активирована"
        except:
            return "Статус неизвестен"

    def check_office(self):
        office_info = {
            'installed': False,
            'version': "Не установлен",
            'activated': "Неизвестно",
            'path': "Не найден"
        }
        
        # Проверяем наличие Office в реестре
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
            for i in range(0, winreg.QueryInfoKey(key)[0]):
                try:
                    subkey_name = winreg.EnumKey(key, i)
                    subkey = winreg.OpenKey(key, subkey_name)
                    display_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                    if "Microsoft Office" in display_name:
                        office_info['installed'] = True
                        office_info['version'] = display_name
                        break
                except:
                    continue
            winreg.CloseKey(key)
        except:
            pass
        
        # Проверяем активацию Office
        try:
            result = subprocess.run(['cscript', os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft Office', 'Office16', 'OSPP.VBS'), '/dstatus'], 
                                  capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            if "licensed" in result.stdout.lower():
                office_info['activated'] = "Активирован"
            else:
                office_info['activated'] = "Не активирован"
        except:
            office_info['activated'] = "Статус неизвестен"
        
        return office_info

    def update_system_info(self):
        self.os_info = self.get_os_info()
        info_text = f"""Операционная система: {self.os_info['system']} {self.os_info['release']}
Версия: {self.os_info['version']}
Издание: {self.os_info['edition']}
Архитектура: {self.os_info['bits']}
Процессор: {self.os_info['processor']}
Статус активации: {self.os_info['activated']}"""
        
        self.system_info_text.config(state=tk.NORMAL)
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(tk.END, info_text)
        self.system_info_text.config(state=tk.DISABLED)

    def update_office_info(self):
        self.office_info = self.check_office()
        info_text = f"""Установлен: {'Да' if self.office_info['installed'] else 'Нет'}
Версия: {self.office_info['version']}
Статус активации: {self.office_info['activated']}"""
        
        self.office_info_text.config(state=tk.NORMAL)
        self.office_info_text.delete(1.0, tk.END)
        self.office_info_text.insert(tk.END, info_text)
        self.office_info_text.config(state=tk.DISABLED)

    def open_system_properties(self):
        try:
            subprocess.Popen('SystemPropertiesAdvanced', shell=True)
        except:
            messagebox.showerror("Ошибка", "Не удалось открыть параметры системы")

    def open_office_app(self):
        try:
            subprocess.Popen('winword', shell=True)
        except:
            messagebox.showerror("Ошибка", "Не удалось открыть Microsoft Word")

    def activate_windows(self):
        key = self.win_key_entry.get().strip()
        if not key:
            messagebox.showwarning("Предупреждение", "Введите ключ продукта Windows")
            return
        
        self.activation_log("Попытка активации Windows...")
        
        try:
            result = subprocess.run(['slmgr', '/ipk', key], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            result = subprocess.run(['slmgr', '/ato'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if "successful" in result.stdout.lower():
                self.activation_log("Windows успешно активирован!")
                self.os_info['activated'] = "Активирована"
                self.update_system_info()
            else:
                self.activation_log("Ошибка активации Windows:")
                self.activation_log(result.stdout)
                self.activation_log(result.stderr)
        except Exception as e:
            self.activation_log(f"Ошибка при активации Windows: {str(e)}")

    def activate_office(self):
        key = self.office_key_entry.get().strip()
        if not key:
            messagebox.showwarning("Предупреждение", "Введите ключ продукта Office")
            return
        
        self.activation_log("Попытка активации Office...")
        
        try:
            # Ищем путь к OSPP.VBS
            office_path = None
            possible_paths = [
                os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft Office', 'Office16', 'OSPP.VBS'),
                os.path.join(os.environ['ProgramFiles'], 'Microsoft Office', 'Office16', 'OSPP.VBS'),
                os.path.join(os.environ['ProgramFiles(x86)'], 'Microsoft Office', 'Office15', 'OSPP.VBS'),
                os.path.join(os.environ['ProgramFiles'], 'Microsoft Office', 'Office15', 'OSPP.VBS')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    office_path = path
                    break
            
            if not office_path:
                self.activation_log("Не удалось найти OSPP.VBS для активации Office")
                return
            
            result = subprocess.run(['cscript', office_path, '/inpkey:' + key], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            result = subprocess.run(['cscript', office_path, '/act'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            
            if "successful" in result.stdout.lower():
                self.activation_log("Office успешно активирован!")
                self.office_info['activated'] = "Активирован"
                self.update_office_info()
            else:
                self.activation_log("Ошибка активации Office:")
                self.activation_log(result.stdout)
                self.activation_log(result.stderr)
        except Exception as e:
            self.activation_log(f"Ошибка при активации Office: {str(e)}")

    def load_key(self, key_type):
        folder = self.key_folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Укажите корректную папку с ключами")
            return
        
        filename = 'win_key.txt' if key_type == 'win' else 'office_key.txt'
        filepath = os.path.join(folder, filename)
        
        if not os.path.exists(filepath):
            messagebox.showerror("Ошибка", f"Файл {filename} не найден в указанной папке")
            return
        
        try:
            with open(filepath, 'r') as f:
                keys = f.readlines()
                if keys:
                    key = keys[0].strip()
                    if key_type == 'win':
                        self.win_key_entry.delete(0, tk.END)
                        self.win_key_entry.insert(0, key)
                    else:
                        self.office_key_entry.delete(0, tk.END)
                        self.office_key_entry.insert(0, key)
                    self.activation_log(f"Загружен ключ из файла {filename}")
                else:
                    messagebox.showwarning("Предупреждение", f"Файл {filename} пуст")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл {filename}: {str(e)}")

    def auto_activate_windows(self):
        folder = self.key_folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Укажите корректную папку с ключами")
            return
        
        filepath = os.path.join(folder, 'win_key.txt')
        
        if not os.path.exists(filepath):
            messagebox.showerror("Ошибка", "Файл win_key.txt не найден в указанной папке")
            return
        
        try:
            with open(filepath, 'r') as f:
                keys = f.readlines()
                if keys:
                    for key in keys:
                        key = key.strip()
                        if key:
                            self.win_key_entry.delete(0, tk.END)
                            self.win_key_entry.insert(0, key)
                            self.activate_windows()
                            if self.os_info['activated'] == "Активирована":
                                break
                else:
                    messagebox.showwarning("Предупреждение", "Файл win_key.txt пуст")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл win_key.txt: {str(e)}")

    def auto_activate_office(self):
        folder = self.key_folder_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Ошибка", "Укажите корректную папку с ключами")
            return
        
        filepath = os.path.join(folder, 'office_key.txt')
        
        if not os.path.exists(filepath):
            messagebox.showerror("Ошибка", "Файл office_key.txt не найден в указанной папке")
            return
        
        try:
            with open(filepath, 'r') as f:
                keys = f.readlines()
                if keys:
                    for key in keys:
                        key = key.strip()
                        if key:
                            self.office_key_entry.delete(0, tk.END)
                            self.office_key_entry.insert(0, key)
                            self.activate_office()
                            if self.office_info['activated'] == "Активирован":
                                break
                else:
                    messagebox.showwarning("Предупреждение", "Файл office_key.txt пуст")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать файл office_key.txt: {str(e)}")

    def activation_log(self, message):
        self.activation_log_text.config(state=tk.NORMAL)
        self.activation_log_text.insert(tk.END, message + "\n")
        self.activation_log_text.config(state=tk.DISABLED)
        self.activation_log_text.see(tk.END)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.config(state=tk.DISABLED)
        self.log_text.see(tk.END)

    def show_about(self):
        about_text = """Ultimate Driver & System Tool
Версия 1.0

Программа для установки драйверов и управления системой:
- Установка драйверов с автоматической классификацией
- Просмотр информации о системе
- Активация Windows и Office
- Поддержка темной и светлой темы

© 2025 Все права защищены"""
Программу сделал Sweetsvt для личного использования
        
        messagebox.showinfo("О программе", about_text)

    def show_help(self):
        help_text = """Инструкция по использованию:

1. Вкладка 'Драйверы':
   - Укажите папку с драйверами
   - Нажмите 'Сканировать' для поиска драйверов
   - Выберите нужные драйверы и нажмите 'Установить'

2. Вкладка 'Система':
   - Просмотр информации о вашей ОС
   - Проверка статуса активации

3. Вкладка 'Microsoft Office':
   - Проверка установленного Office
   - Проверка статуса активации

4. Вкладка 'Активация':
   - Активация Windows и Office
   - Автоматическая активация из файлов win_key.txt и office_key.txt"""
        
        messagebox.showinfo("Помощь", help_text)

    def check_queue(self):
        while not self.queue.empty():
            task = self.queue.get()
            
            if task[0] == 'update_drivers_list':
                drivers = task[1]
                for driver, driver_type in drivers:
                    self.drivers_tree.insert('', tk.END, text=os.path.basename(driver), 
                                           values=(driver, driver_type, "Не установлен"), tags=('pending',))
                
                if drivers:
                    self.install_btn.config(state=tk.NORMAL)
            
            elif task[0] == 'update_driver_status':
                driver, status, color = task[1], task[2], task[3]
                for item in self.drivers_tree.get_children():
                    if self.drivers_tree.item(item, 'values')[0] == driver:
                        self.drivers_tree.item(item, values=(driver, self.drivers_tree.item(item, 'values')[1], status))
                        self.drivers_tree.set(item, 'status', status)
                        self.drivers_tree.tag_configure(color, foreground=color)
                        self.drivers_tree.item(item, tags=(color,))
                        break
            
            elif task[0] == 'log':
                self.log(task[1])
            
            elif task[0] == 'status':
                self.status_var.set(task[1])
            
            elif task[0] == 'install_complete':
                self.install_btn.config(state=tk.NORMAL)
                messagebox.showinfo("Готово", "Установка драйверов завершена")
        
        self.root.after(100, self.check_queue)

def main():
    root = tk.Tk()
    app = ModernInstallerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()