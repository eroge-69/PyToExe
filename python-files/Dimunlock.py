import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import os
import subprocess
import sys
import ctypes
import platform
import psutil
import threading
import time
from datetime import datetime

class ModernAntivirusBypassTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Security Toolkit Pro")
        self.root.geometry("1200x800")
        self.root.configure(bg='#2b2b2b')
        
        # Стили
        self.setup_styles()
        
        # Переменные
        self.is_admin = self.check_admin_privileges()
        self.selected_drive = tk.StringVar(value="C:")
        self.process_list = []
        
        self.setup_ui()
        self.start_process_monitor()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Современные цвета
        style.configure('Modern.TFrame', background='#2b2b2b')
        style.configure('Card.TFrame', background='#3c3c3c', relief='raised', borderwidth=1)
        style.configure('Title.TLabel', background='#2b2b2b', foreground='#ffffff', font=('Segoe UI', 12, 'bold'))
        style.configure('Text.TLabel', background='#3c3c3c', foreground='#cccccc', font=('Segoe UI', 9))
        style.configure('Accent.TButton', background='#007acc', foreground='white', font=('Segoe UI', 9))
        style.map('Accent.TButton', background=[('active', '#005a9e')])
        style.configure('Danger.TButton', background='#d13438', foreground='white', font=('Segoe UI', 9))
        style.map('Danger.TButton', background=[('active', '#a02626')])
        style.configure('Success.TButton', background='#107c10', foreground='white', font=('Segoe UI', 9))
        
        style.configure('Modern.TNotebook', background='#2b2b2b', borderwidth=0)
        style.configure('Modern.TNotebook.Tab', background='#3c3c3c', foreground='#cccccc',
                       padding=[15, 5], font=('Segoe UI', 9))
        style.map('Modern.TNotebook.Tab', background=[('selected', '#007acc')])
        
    def check_admin_privileges(self):
        try:
            return os.getuid() == 0
        except AttributeError:
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
    
    def setup_ui(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="🔒 Security Toolkit Pro", 
                               style='Title.TLabel', font=('Segoe UI', 16, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        status_label = ttk.Label(header_frame, 
                               text=f"Admin: {'✅' if self.is_admin else '❌'} | OS: {platform.system()}",
                               style='Text.TLabel')
        status_label.pack(side=tk.RIGHT)
        
        # Создание вкладок
        self.notebook = ttk.Notebook(main_frame, style='Modern.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки
        self.setup_dashboard_tab()
        self.setup_autostart_tab()
        self.setup_process_tab()
        self.setup_debuggers_tab()
        self.setup_disk_tab()
        self.setup_system_tab()
        
    def setup_dashboard_tab(self):
        dashboard_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(dashboard_frame, text="📊 Дашборд")
        
        # Карточки быстрого доступа
        cards_frame = ttk.Frame(dashboard_frame, style='Modern.TFrame')
        cards_frame.pack(fill=tk.X, pady=10)
        
        cards_data = [
            ("🔍 Автозагрузки", "Просмотр автозагрузок", self.show_autostart),
            ("⚙️ Процессы", "Диспетчер задач", self.show_processes),
            ("🐛 Дебаггеры", "Управление дебаггерами", self.show_debuggers),
            ("💾 Диск", "Сканирование диска", self.show_disk),
            ("🛡️ Система", "Системные утилиты", self.show_system)
        ]
        
        for i, (title, desc, command) in enumerate(cards_data):
            card = ttk.Frame(cards_frame, style='Card.TFrame', width=200, height=100)
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            cards_frame.columnconfigure(i, weight=1)
            
            ttk.Label(card, text=title, style='Title.TLabel', font=('Segoe UI', 11, 'bold')).pack(pady=(10, 5))
            ttk.Label(card, text=desc, style='Text.TLabel', wraplength=180).pack(pady=5)
            ttk.Button(card, text="Открыть", command=command, style='Accent.TButton').pack(pady=10)
        
        # Системная информация
        info_frame = ttk.Frame(dashboard_frame, style='Card.TFrame')
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(info_frame, text="Системная информация", style='Title.TLabel').pack(anchor='w', padx=10, pady=10)
        
        self.system_info_text = scrolledtext.ScrolledText(info_frame, bg='#3c3c3c', fg='#cccccc', 
                                                         font=('Consolas', 9), height=15)
        self.system_info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.update_system_info()
        
    def setup_autostart_tab(self):
        autostart_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(autostart_frame, text="🔍 Автозагрузки")
        
        # Кнопки проверки
        buttons_frame = ttk.Frame(autostart_frame, style='Modern.TFrame')
        buttons_frame.pack(fill=tk.X, pady=10)
        
        check_buttons = [
            ("Userinit", self.check_userinit),
            ("Shell", self.check_shell),
            ("AppInit DLLs", self.check_appnits),
            ("Known DLLs", self.check_dll),
            ("Run Keys", self.check_cmdline),
            ("Все автозагрузки", self.check_all_autostart)
        ]
        
        for i, (text, command) in enumerate(check_buttons):
            ttk.Button(buttons_frame, text=text, command=command, style='Accent.TButton').grid(
                row=0, column=i, padx=2, sticky='ew')
            buttons_frame.columnconfigure(i, weight=1)
        
        # Область вывода
        output_frame = ttk.Frame(autostart_frame, style='Card.TFrame')
        output_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.autostart_output = scrolledtext.ScrolledText(output_frame, bg='#3c3c3c', fg='#cccccc',
                                                         font=('Consolas', 9))
        self.autostart_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_process_tab(self):
        process_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(process_frame, text="⚙️ Процессы")
        
        # Панель управления
        control_frame = ttk.Frame(process_frame, style='Modern.TFrame')
        control_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(control_frame, text="🔄 Обновить", command=self.refresh_processes,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="⏹️ Завершить", command=self.kill_process,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="📊 Подробно", command=self.show_process_details,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        # Дерево процессов
        tree_frame = ttk.Frame(process_frame, style='Card.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ('PID', 'Name', 'CPU', 'Memory', 'Status', 'User')
        self.process_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=100)
        
        self.process_tree.column('Name', width=200)
        self.process_tree.column('PID', width=80)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        self.refresh_processes()
        
    def setup_debuggers_tab(self):
        debug_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(debug_frame, text="🐛 Дебаггеры")
        
        # Панель управления
        debug_control = ttk.Frame(debug_frame, style='Modern.TFrame')
        debug_control.pack(fill=tk.X, pady=10)
        
        ttk.Button(debug_control, text="🔄 Обновить список", command=self.refresh_debuggers,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(debug_control, text="🗑️ Удалить выделенные", command=self.remove_debuggers,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Список дебаггеров
        list_frame = ttk.Frame(debug_frame, style='Card.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.debugger_list = tk.Listbox(list_frame, bg='#3c3c3c', fg='#cccccc', 
                                       selectbackground='#007acc', font=('Consolas', 9))
        self.debugger_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.refresh_debuggers()
        
    def setup_disk_tab(self):
        disk_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(disk_frame, text="💾 Диск")
        
        # Выбор диска
        disk_control = ttk.Frame(disk_frame, style='Modern.TFrame')
        disk_control.pack(fill=tk.X, pady=10)
        
        ttk.Label(disk_control, text="Выберите диск:", style='Text.TLabel').pack(side=tk.LEFT, padx=5)
        
        drives = self.get_available_drives()
        drive_combo = ttk.Combobox(disk_control, textvariable=self.selected_drive, 
                                  values=drives, state='readonly')
        drive_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(disk_control, text="🔍 Сканировать", command=self.scan_disk,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(disk_control, text="📊 Инфо о диске", command=self.show_disk_info,
                  style='Success.TButton').pack(side=tk.LEFT, padx=5)
        
        # Результаты сканирования
        result_frame = ttk.Frame(disk_frame, style='Card.TFrame')
        result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.disk_output = scrolledtext.ScrolledText(result_frame, bg='#3c3c3c', fg='#cccccc',
                                                   font=('Consolas', 9))
        self.disk_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
    def setup_system_tab(self):
        system_frame = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.notebook.add(system_frame, text="🛡️ Система")
        
        # Опасные операции
        danger_frame = ttk.Frame(system_frame, style='Card.TFrame')
        danger_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(danger_frame, text="Опасные операции", style='Title.TLabel').pack(anchor='w', padx=10, pady=10)
        
        ops_frame = ttk.Frame(danger_frame, style='Card.TFrame')
        ops_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        ttk.Button(ops_frame, text="🔄 Перезагрузка ПК", command=self.restart_pc,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(ops_frame, text="💥 Аварийное завершение", command=self.trigger_bsod,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=5)
        
        # Системные утилиты
        utils_frame = ttk.Frame(system_frame, style='Card.TFrame')
        utils_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        ttk.Label(utils_frame, text="Системные утилиты", style='Title.TLabel').pack(anchor='w', padx=10, pady=10)
        
        utils_buttons = [
            ("📁 Проводник", self.open_explorer),
            ("⚙️ Реестр", self.launch_regedit),
            ("🔧 Службы", self.launch_services),
            ("📋 Диспетчер задач", self.launch_task_manager)
        ]
        
        utils_grid = ttk.Frame(utils_frame, style='Card.TFrame')
        utils_grid.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        for i, (text, command) in enumerate(utils_buttons):
            ttk.Button(utils_grid, text=text, command=command, style='Accent.TButton').grid(
                row=0, column=i, padx=5, sticky='ew')
            utils_grid.columnconfigure(i, weight=1)
    
    def show_autostart(self):
        self.notebook.select(1)
    
    def show_processes(self):
        self.notebook.select(2)
    
    def show_debuggers(self):
        self.notebook.select(3)
    
    def show_disk(self):
        self.notebook.select(4)
    
    def show_system(self):
        self.notebook.select(5)
    
    # Методы для работы с процессами
    def refresh_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        self.process_list = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'status', 'username']):
            try:
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                self.process_tree.insert('', 'end', values=(
                    proc.info['pid'],
                    proc.info['name'],
                    f"{proc.info['cpu_percent']:.1f}%",
                    f"{memory_mb:.1f} MB",
                    proc.info['status'],
                    proc.info['username'][:20] if proc.info['username'] else 'N/A'
                ))
                self.process_list.append(proc.info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def kill_process(self):
        selection = self.process_tree.selection()
        if selection:
            item = selection[0]
            pid = self.process_tree.item(item)['values'][0]
            try:
                process = psutil.Process(pid)
                process.terminate()
                messagebox.showinfo("Успех", f"Процесс {pid} завершен")
                self.refresh_processes()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось завершить процесс: {e}")
    
    def show_process_details(self):
        selection = self.process_tree.selection()
        if selection:
            item = selection[0]
            pid = self.process_tree.item(item)['values'][0]
            try:
                process = psutil.Process(pid)
                info = f"""
Детальная информация о процессе:
PID: {pid}
Имя: {process.name()}
Статус: {process.status()}
Пользователь: {process.username()}
CPU: {process.cpu_percent()}%
Память: {process.memory_info().rss / 1024 / 1024:.1f} MB
Путь: {process.exe()}
Запущен: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}
                """
                messagebox.showinfo("Информация о процессе", info)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось получить информацию: {e}")
    
    # Методы для дебаггеров
    def refresh_debuggers(self):
        self.debugger_list.delete(0, tk.END)
        try:
            if platform.system() == "Windows":
                # Поиск распространенных дебаггеров
                debuggers = [
                    "ollydbg.exe", "x64dbg.exe", "ida64.exe", "ida.exe",
                    "windbg.exe", "devenv.exe", "ImmunityDebugger.exe"
                ]
                
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'].lower() in [d.lower() for d in debuggers]:
                        self.debugger_list.insert(tk.END, f"{proc.info['name']} (PID: {proc.pid})")
                
                if self.debugger_list.size() == 0:
                    self.debugger_list.insert(tk.END, "Дебаггеры не обнаружены")
        except Exception as e:
            self.debugger_list.insert(tk.END, f"Ошибка: {e}")
    
    def remove_debuggers(self):
        selection = self.debugger_list.curselection()
        if selection:
            for index in selection:
                debugger_info = self.debugger_list.get(index)
                pid = int(debugger_info.split("(PID: ")[1].split(")")[0])
                try:
                    process = psutil.Process(pid)
                    process.terminate()
                    messagebox.showinfo("Успех", f"Дебаггер {process.name()} завершен")
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось завершить дебаггер: {e}")
            self.refresh_debuggers()
    
    # Методы для диска
    def get_available_drives(self):
        if platform.system() == "Windows":
            return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:")]
        else:
            return ["/", "/home", "/etc"]
    
    def scan_disk(self):
        drive = self.selected_drive.get()
        self.disk_output.delete(1.0, tk.END)
        self.disk_output.insert(tk.END, f"Сканирование диска {drive}...\n\n")
        
        try:
            # Анализ использования диска
            usage = psutil.disk_usage(drive)
            self.disk_output.insert(tk.END, f"Общий размер: {usage.total / (1024**3):.2f} GB\n")
            self.disk_output.insert(tk.END, f"Использовано: {usage.used / (1024**3):.2f} GB\n")
            self.disk_output.insert(tk.END, f"Свободно: {usage.free / (1024**3):.2f} GB\n")
            self.disk_output.insert(tk.END, f"Заполнение: {usage.percent}%\n\n")
            
            # Поиск исполняемых файлов (пример)
            self.disk_output.insert(tk.END, "Поиск исполняемых файлов...\n")
            exe_count = 0
            for root, dirs, files in os.walk(drive):
                for file in files:
                    if file.lower().endswith(('.exe', '.dll', '.sys')):
                        exe_count += 1
                if exe_count > 1000:  # Ограничим вывод
                    break
            
            self.disk_output.insert(tk.END, f"Найдено исполняемых файлов: {exe_count}\n")
            
        except Exception as e:
            self.disk_output.insert(tk.END, f"Ошибка сканирования: {e}\n")
    
    def show_disk_info(self):
        drive = self.selected_drive.get()
        try:
            usage = psutil.disk_usage(drive)
            info = f"""
Информация о диске {drive}:
Общий размер: {usage.total / (1024**3):.2f} GB
Использовано: {usage.used / (1024**3):.2f} GB
Свободно: {usage.free / (1024**3):.2f} GB
Заполнение: {usage.percent}%
Файловая система: {psutil.disk_partitions()[0].fstype if psutil.disk_partitions() else 'N/A'}
            """
            messagebox.showinfo("Информация о диске", info)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить информацию о диске: {e}")
    
    # Остальные методы (из предыдущей версии)
    def check_userinit(self):
        self.autostart_output.delete(1.0, tk.END)
        # ... (реализация из предыдущего кода)
    
    def check_shell(self):
        self.autostart_output.delete(1.0, tk.END)
        # ... (реализация из предыдущего кода)
    
    def check_appnits(self):
        self.autostart_output.delete(1.0, tk.END)
        # ... (реализация из предыдущего кода)
    
    def check_dll(self):
        self.autostart_output.delete(1.0, tk.END)
        # ... (реализация из предыдущего кода)
    
    def check_cmdline(self):
        self.autostart_output.delete(1.0, tk.END)
        # ... (реализация из предыдущего кода)
    
    def check_all_autostart(self):
        self.autostart_output.delete(1.0, tk.END)
        for check_func in [self.check_userinit, self.check_shell, self.check_appnits, 
                          self.check_dll, self.check_cmdline]:
            check_func()
    
    def restart_pc(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите перезагрузить ПК?"):
            try:
                if platform.system() == "Windows":
                    os.system("shutdown /r /t 0")
                else:
                    os.system("sudo reboot")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось перезагрузить: {e}")
    
    def trigger_bsod(self):
        if messagebox.askyesno("ВНИМАНИЕ!", 
                              "Эта операция вызовет аварийное завершение системы!\n"
                              "Все несохраненные данные будут потеряны!\n\n"
                              "Продолжить?"):
            try:
                if platform.system() == "Windows":
                    ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                    ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
                else:
                    os.system("echo c > /proc/sysrq-trigger")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось выполнить операцию: {e}")
    
    def open_explorer(self):
        try:
            if platform.system() == "Windows":
                os.system("explorer")
            else:
                os.system("nautilus")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть проводник: {e}")
    
    def launch_regedit(self):
        try:
            if platform.system() == "Windows":
                os.system("regedit")
            else:
                messagebox.showinfo("Информация", "Редактор реестра доступен только в Windows")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить редактор реестра: {e}")
    
    def launch_services(self):
        try:
            if platform.system() == "Windows":
                os.system("services.msc")
            else:
                os.system("systemctl")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть службы: {e}")
    
    def launch_task_manager(self):
        try:
            if platform.system() == "Windows":
                os.system("taskmgr")
            else:
                os.system("gnome-system-monitor")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить диспетчер задач: {e}")
    
    def update_system_info(self):
        info = f"""
Системная информация:
ОС: {platform.system()} {platform.release()}
Версия: {platform.version()}
Архитектура: {platform.architecture()[0]}
Процессор: {platform.processor()}
Пользователь: {os.getlogin()}
Права администратора: {'Да' if self.is_admin else 'Нет'}
Рабочая директория: {os.getcwd()}
Время работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Системные ресурсы:
CPU загрузка: {psutil.cpu_percent()}%
Память: {psutil.virtual_memory().percent}% использовано
Диски: {len(psutil.disk_partitions())} разделов
        """
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(tk.END, info)
    
    def start_process_monitor(self):
        def monitor():
            while True:
                self.update_system_info()
                time.sleep(5)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

def main():
    root = tk.Tk()
    app = ModernAntivirusBypassTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()
