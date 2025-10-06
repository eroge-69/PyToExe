import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import subprocess
import psutil
import platform
import winreg as reg
from datetime import datetime

class DimUnlockPC:
    def __init__(self, root):
        self.root = root
        self.root.title("DimUnlock PC v. 1.0")
        self.root.geometry("700x500")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)
        
        # Центрирование окна
        self.center_window()
        
        # Переменные
        self.is_admin = self.check_admin_privileges()
        self.selected_drive = tk.StringVar(value="C:")
        
        self.setup_styles()
        self.setup_ui()
        
    def center_window(self):
        self.root.update_idletasks()
        width = 700
        height = 500
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Темная тема
        style.configure('TFrame', background='#2d2d30')
        style.configure('TLabel', background='#2d2d30', foreground='#cccccc')
        style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#333333', foreground='#cccccc',
                       padding=[15, 5], font=('Arial', 9))
        style.map('TNotebook.Tab', background=[('selected', '#007acc')])
        
        # Стили для кнопок
        style.configure('Accent.TButton', background='#007acc', foreground='white',
                       font=('Arial', 8, 'bold'), padding=6)
        style.map('Accent.TButton', background=[('active', '#005a9e')])
        
        style.configure('Danger.TButton', background='#d13438', foreground='white',
                       font=('Arial', 8, 'bold'), padding=6)
        style.map('Danger.TButton', background=[('active', '#a02626')])
        
        style.configure('Success.TButton', background='#107c10', foreground='white',
                       font=('Arial', 8, 'bold'), padding=6)
        style.map('Success.TButton', background=[('active', '#0e6a0e')])
        
    def check_admin_privileges(self):
        try:
            return os.getuid() == 0
        except AttributeError:
            try:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
    
    def setup_ui(self):
        # Главный контейнер
        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = ttk.Label(header_frame, text="DimUnlock PC v. 1.0", 
                               font=('Arial', 12, 'bold'), foreground='#ffffff')
        title_label.pack(side=tk.LEFT)
        
        status_label = ttk.Label(header_frame, 
                               text=f"Admin: {'✅' if self.is_admin else '❌'}",
                               font=('Arial', 8))
        status_label.pack(side=tk.RIGHT)
        
        # Контейнер для вкладок и контента
        content_frame = ttk.Frame(main_frame, style='TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Вкладки слева
        self.notebook = ttk.Notebook(content_frame, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Создание вкладок
        self.setup_main_tab()
        self.setup_autostart_tab()
        self.setup_process_tab()
        self.setup_tools_tab()
        self.setup_system_tab()
        
    def setup_main_tab(self):
        main_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(main_frame, text="Главная")
        
        # Статус системы
        status_frame = ttk.LabelFrame(main_frame, text="Статус системы", style='TFrame')
        status_frame.pack(fill=tk.X, pady=5, padx=5)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=8, 
                                                   font=('Consolas', 8),
                                                   bg='#1e1e1e', fg='#cccccc')
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Быстрые действия
        actions_frame = ttk.LabelFrame(main_frame, text="Быстрые действия", style='TFrame')
        actions_frame.pack(fill=tk.X, pady=5, padx=5)
        
        actions_grid = ttk.Frame(actions_frame, style='TFrame')
        actions_grid.pack(fill=tk.X, padx=5, pady=5)
        
        actions = [
            ("🔍 Автозагрузка", self.check_all_autostart, 'Accent.TButton'),
            ("⚙️ Процессы", self.show_processes, 'Accent.TButton'),
            ("🐛 Дебаггеры", self.find_debuggers, 'Danger.TButton'),
            ("💾 Диск", self.scan_disk, 'Success.TButton'),
            ("🔄 Рестарт", self.restart_pc, 'Danger.TButton'),
            ("📊 Инфо", self.show_system_info, 'Success.TButton')
        ]
        
        for i, (text, command, style_name) in enumerate(actions):
            btn = ttk.Button(actions_grid, text=text, command=command, 
                           style=style_name, width=15)
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
            actions_grid.columnconfigure(i%3, weight=1)
        
        self.update_system_info()
        
    def setup_autostart_tab(self):
        autostart_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(autostart_frame, text="Автозагрузка")
        
        # Кнопки проверки
        buttons_frame = ttk.Frame(autostart_frame, style='TFrame')
        buttons_frame.pack(fill=tk.X, pady=5, padx=5)
        
        buttons = [
            ("Userinit", self.check_userinit),
            ("Shell", self.check_shell),
            ("AppInit", self.check_appnits),
            ("DLLs", self.check_dll),
            ("Run Keys", self.check_cmdline),
            ("ВСЁ", self.check_all_autostart)
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(buttons_frame, text=text, command=command, 
                           style='Accent.TButton', width=10)
            btn.grid(row=i//3, column=i%3, padx=2, pady=2, sticky='ew')
            buttons_frame.columnconfigure(i%3, weight=1)
        
        # Результаты
        result_frame = ttk.LabelFrame(autostart_frame, text="Результаты", style='TFrame')
        result_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        self.autostart_output = scrolledtext.ScrolledText(result_frame, height=10,
                                                         font=('Consolas', 8),
                                                         bg='#1e1e1e', fg='#cccccc')
        self.autostart_output.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def setup_process_tab(self):
        process_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(process_frame, text="Процессы")
        
        # Управление
        control_frame = ttk.Frame(process_frame, style='TFrame')
        control_frame.pack(fill=tk.X, pady=5, padx=5)
        
        ttk.Button(control_frame, text="Обновить", 
                  command=self.refresh_processes,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Завершить", 
                  command=self.kill_process,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(control_frame, text="Подробно", 
                  command=self.show_process_details,
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
        
        # Список процессов
        list_frame = ttk.LabelFrame(process_frame, text="Список процессов", style='TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5, padx=5)
        
        # Treeview с прокруткой
        tree_frame = ttk.Frame(list_frame, style='TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('PID', 'Name', 'CPU', 'Memory')
        self.process_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)
        
        # Настройка колонок
        column_widths = {'PID': 50, 'Name': 150, 'CPU': 60, 'Memory': 80}
        for col in columns:
            self.process_tree.heading(col, text=col)
            self.process_tree.column(col, width=column_widths[col])
        
        # Прокрутка
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.process_tree.yview)
        self.process_tree.configure(yscrollcommand=scrollbar.set)
        
        self.process_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.refresh_processes()
        
    def setup_tools_tab(self):
        tools_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(tools_frame, text="Инструменты")
        
        # Дебаггеры
        debug_frame = ttk.LabelFrame(tools_frame, text="Дебаггеры", style='TFrame')
        debug_frame.pack(fill=tk.X, pady=5, padx=5)
        
        debug_controls = ttk.Frame(debug_frame, style='TFrame')
        debug_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(debug_controls, text="Найти", 
                  command=self.find_debuggers,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(debug_controls, text="Удалить", 
                  command=self.remove_debuggers,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        
        self.debugger_list = tk.Listbox(debug_frame, height=3, bg='#1e1e1e', fg='#cccccc')
        self.debugger_list.pack(fill=tk.X, padx=5, pady=5)
        
        # Диск
        disk_frame = ttk.LabelFrame(tools_frame, text="Диск", style='TFrame')
        disk_frame.pack(fill=tk.X, pady=5, padx=5)
        
        disk_controls = ttk.Frame(disk_frame, style='TFrame')
        disk_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(disk_controls, text="Диск:", style='TLabel').pack(side=tk.LEFT, padx=2)
        
        drives = self.get_available_drives()
        drive_combo = ttk.Combobox(disk_controls, textvariable=self.selected_drive, 
                                  values=drives, state='readonly', width=8)
        drive_combo.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(disk_controls, text="Сканировать", 
                  command=self.scan_disk,
                  style='Accent.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(disk_controls, text="Инфо", 
                  command=self.show_disk_info,
                  style='Success.TButton').pack(side=tk.LEFT, padx=2)
        
        self.disk_output = scrolledtext.ScrolledText(disk_frame, height=4,
                                                   font=('Consolas', 8),
                                                   bg='#1e1e1e', fg='#cccccc')
        self.disk_output.pack(fill=tk.X, padx=5, pady=5)
        
    def setup_system_tab(self):
        system_frame = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(system_frame, text="Система")
        
        # Опасные операции
        danger_frame = ttk.LabelFrame(system_frame, text="Опасные операции", style='TFrame')
        danger_frame.pack(fill=tk.X, pady=5, padx=5)
        
        danger_controls = ttk.Frame(danger_frame, style='TFrame')
        danger_controls.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(danger_controls, text="Перезагрузка", 
                  command=self.restart_pc,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(danger_controls, text="BSOD", 
                  command=self.trigger_bsod,
                  style='Danger.TButton').pack(side=tk.LEFT, padx=2)
        
        # Утилиты
        utils_frame = ttk.LabelFrame(system_frame, text="Утилиты", style='TFrame')
        utils_frame.pack(fill=tk.X, pady=5, padx=5)
        
        utils_controls = ttk.Frame(utils_frame, style='TFrame')
        utils_controls.pack(fill=tk.X, padx=5, pady=5)
        
        utils = [
            ("Проводник", self.open_explorer),
            ("Реестр", self.launch_regedit),
            ("Службы", self.launch_services),
            ("Задачи", self.launch_task_manager)
        ]
        
        for i, (text, command) in enumerate(utils):
            ttk.Button(utils_controls, text=text, command=command,
                      style='Accent.TButton').grid(row=0, column=i, padx=2, sticky='ew')
            utils_controls.columnconfigure(i, weight=1)
    
    # Методы для автозагрузки
    def check_userinit(self):
        self.autostart_output.delete(1.0, tk.END)
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon")
            value, _ = reg.QueryValueEx(key, "Userinit")
            self.autostart_output.insert(tk.END, f"Userinit:\n{value}\n")
            reg.CloseKey(key)
        except Exception as e:
            self.autostart_output.insert(tk.END, f"Ошибка: {e}\n")
    
    def check_shell(self):
        self.autostart_output.delete(1.0, tk.END)
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon")
            value, _ = reg.QueryValueEx(key, "Shell")
            self.autostart_output.insert(tk.END, f"Shell:\n{value}\n")
            reg.CloseKey(key)
        except Exception as e:
            self.autostart_output.insert(tk.END, f"Ошибка: {e}\n")
    
    def check_appnits(self):
        self.autostart_output.delete(1.0, tk.END)
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Windows")
            value, _ = reg.QueryValueEx(key, "AppInit_DLLs")
            self.autostart_output.insert(tk.END, f"AppInit_DLLs:\n{value}\n")
            reg.CloseKey(key)
        except Exception as e:
            self.autostart_output.insert(tk.END, f"Ошибка: {e}\n")
    
    def check_dll(self):
        self.autostart_output.delete(1.0, tk.END)
        try:
            key = reg.OpenKey(reg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\KnownDLLs")
            self.autostart_output.insert(tk.END, "KnownDLLs:\n")
            i = 0
            while True:
                try:
                    name, value, _ = reg.EnumValue(key, i)
                    self.autostart_output.insert(tk.END, f"{name}\n")
                    i += 1
                except WindowsError:
                    break
            reg.CloseKey(key)
        except Exception as e:
            self.autostart_output.insert(tk.END, f"Ошибка: {e}\n")
    
    def check_cmdline(self):
        self.autostart_output.delete(1.0, tk.END)
        try:
            locations = [
                (reg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
                (reg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run")
            ]
            
            for hive, location in locations:
                self.autostart_output.insert(tk.END, f"{location}:\n")
                try:
                    key = reg.OpenKey(hive, location)
                    i = 0
                    while True:
                        try:
                            name, value, _ = reg.EnumValue(key, i)
                            self.autostart_output.insert(tk.END, f"{name}: {value}\n")
                            i += 1
                        except WindowsError:
                            break
                    reg.CloseKey(key)
                except Exception as e:
                    self.autostart_output.insert(tk.END, f"Ошибка: {e}\n")
        except Exception as e:
            self.autostart_output.insert(tk.END, f"Ошибка: {e}\n")
    
    def check_all_autostart(self):
        self.autostart_output.delete(1.0, tk.END)
        self.autostart_output.insert(tk.END, "=== АВТОЗАГРУЗКА ===\n\n")
        for check_func in [self.check_userinit, self.check_shell, self.check_appnits, 
                          self.check_dll, self.check_cmdline]:
            try:
                check_func()
                self.autostart_output.insert(tk.END, "\n")
            except Exception as e:
                self.autostart_output.insert(tk.END, f"Ошибка: {e}\n\n")
    
    # Методы для процессов
    def refresh_processes(self):
        for item in self.process_tree.get_children():
            self.process_tree.delete(item)
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                memory_mb = proc.info['memory_info'].rss / 1024 / 1024
                self.process_tree.insert('', 'end', values=(
                    proc.info['pid'],
                    proc.info['name'][:20],
                    f"{proc.info['cpu_percent']:.1f}%",
                    f"{memory_mb:.1f}M"
                ))
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
PID: {pid}
Имя: {process.name()}
CPU: {process.cpu_percent()}%
Память: {process.memory_info().rss / 1024 / 1024:.1f} MB
Путь: {process.exe() or 'N/A'}
                """
                messagebox.showinfo("Информация", info)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    # Методы для дебаггеров
    def find_debuggers(self):
        self.debugger_list.delete(0, tk.END)
        try:
            debuggers = ["ollydbg.exe", "x64dbg.exe", "ida64.exe", "ida.exe", "windbg.exe"]
            
            found = False
            for proc in psutil.process_iter(['name']):
                if proc.info['name'].lower() in [d.lower() for d in debuggers]:
                    self.debugger_list.insert(tk.END, f"{proc.info['name']} (PID: {proc.pid})")
                    found = True
            
            if not found:
                self.debugger_list.insert(tk.END, "Дебаггеры не найдены")
        except Exception as e:
            self.debugger_list.insert(tk.END, f"Ошибка: {e}")
    
    def remove_debuggers(self):
        selection = self.debugger_list.curselection()
        if selection:
            for index in selection:
                debugger_info = self.debugger_list.get(index)
                if "PID:" in debugger_info:
                    pid = int(debugger_info.split("(PID: ")[1].split(")")[0])
                    try:
                        process = psutil.Process(pid)
                        process.terminate()
                        messagebox.showinfo("Успех", f"Дебаггер завершен")
                    except Exception as e:
                        messagebox.showerror("Ошибка", f"Ошибка: {e}")
            self.find_debuggers()
    
    # Методы для диска
    def get_available_drives(self):
        return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:")]
    
    def scan_disk(self):
        drive = self.selected_drive.get()
        self.disk_output.delete(1.0, tk.END)
        self.disk_output.insert(tk.END, f"Сканирование {drive}...\n\n")
        
        try:
            usage = psutil.disk_usage(drive)
            self.disk_output.insert(tk.END, f"Размер: {usage.total / (1024**3):.1f}G\n")
            self.disk_output.insert(tk.END, f"Использовано: {usage.used / (1024**3):.1f}G\n")
            self.disk_output.insert(tk.END, f"Свободно: {usage.free / (1024**3):.1f}G\n")
            self.disk_output.insert(tk.END, f"Заполнение: {usage.percent}%\n")
        except Exception as e:
            self.disk_output.insert(tk.END, f"Ошибка: {e}\n")
    
    def show_disk_info(self):
        drive = self.selected_drive.get()
        try:
            usage = psutil.disk_usage(drive)
            info = f"""
Диск {drive}:
Размер: {usage.total / (1024**3):.1f} GB
Использовано: {usage.used / (1024**3):.1f} GB  
Свободно: {usage.free / (1024**3):.1f} GB
Заполнение: {usage.percent}%
            """
            messagebox.showinfo("Информация", info)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    # Системные методы
    def show_system_info(self):
        info = f"""
Система:
ОС: {platform.system()} {platform.release()}
Версия: {platform.version()}
Пользователь: {os.getlogin()}
Админ: {'Да' if self.is_admin else 'Нет'}

Ресурсы:
CPU: {psutil.cpu_percent()}%
Память: {psutil.virtual_memory().percent}%
        """
        messagebox.showinfo("Информация", info)
    
    def update_system_info(self):
        info = f"""
ОС: {platform.system()} {platform.release()}
Версия: {platform.version()}
Пользователь: {os.getlogin()}
Админ: {'✅ Да' if self.is_admin else '❌ Нет'}
Время: {datetime.now().strftime('%H:%M:%S')}

Ресурсы:
CPU: {psutil.cpu_percent()}%
Память: {psutil.virtual_memory().percent}%
Диски: {len(psutil.disk_partitions())}
        """
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, info)
    
    def restart_pc(self):
        if messagebox.askyesno("Подтверждение", "Перезагрузить компьютер?"):
            try:
                os.system("shutdown /r /t 0")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def trigger_bsod(self):
        if messagebox.askyesno("ВНИМАНИЕ!", "Вызвать BSOD?\nДанные будут потеряны!"):
            try:
                import ctypes
                ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool()))
                ctypes.windll.ntdll.NtRaiseHardError(0xDEADDEAD, 0, 0, 0, 6, ctypes.byref(ctypes.c_ulong()))
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {e}")
    
    def open_explorer(self):
        os.system("explorer")
    
    def launch_regedit(self):
        os.system("regedit")
    
    def launch_services(self):
        os.system("services.msc")
    
    def launch_task_manager(self):
        os.system("taskmgr")
    
    def show_processes(self):
        self.notebook.select(2)

def main():
    root = tk.Tk()
    app = DimUnlockPC(root)
    root.mainloop()

if __name__ == "__main__":
    main()
