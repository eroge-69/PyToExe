import tkinter as tk
from tkinter import ttk, messagebox
import ctypes
import sys
import time
from datetime import datetime, timedelta
import platform
import psutil
import os

class SystemControlApp:
    def __init__(self, root):
        self.root = root
        self.check_admin_privileges()
        self.setup_window()
        self.scheduled_time = None
        self.countdown_running = False
        self.current_action = None  # 'bsod', 'shutdown', 'restart'
        self.setup_ui()
        
    def check_admin_privileges(self):
        """Проверка прав администратора при запуске"""
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", sys.executable, " ".join(sys.argv), None, 1
                )
                sys.exit(0)
        except Exception as e:
            messagebox.showerror(
                "Ошибка прав доступа",
                "Не удалось запросить права администратора:\n\n" + str(e)
            )
            sys.exit(1)

    def setup_window(self):
        """Настройка основного окна"""
        self.root.title("Контроль системы (Администратор)")
        self.root.geometry("650x500")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        try:
            self.root.iconbitmap(default='icon.ico')
        except:
            pass

    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setup_styles()
        main_frame = self.create_main_frame()
        self.create_header_section(main_frame)
        self.create_action_selector(main_frame)
        self.create_input_section(main_frame)
        self.create_button_section(main_frame)
        self.create_status_section(main_frame)
        self.create_countdown_section(main_frame)
        self.create_footer(main_frame)

    def setup_styles(self):
        """Настройка стилей виджетов"""
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure('.', background='#f5f5f5')
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10))
        style.configure('TNotebook', background='#f5f5f5')
        style.configure('TNotebook.Tab', padding=[10, 5])
        
        style.configure('Red.TButton', foreground='white', background='#d9534f', 
                      font=('Segoe UI', 10, 'bold'))
        style.configure('Blue.TButton', foreground='white', background='#337ab7', 
                      font=('Segoe UI', 10, 'bold'))
        style.configure('Green.TButton', foreground='white', background='#5cb85c', 
                      font=('Segoe UI', 10))
        style.configure('Orange.TButton', foreground='white', background='#f0ad4e', 
                      font=('Segoe UI', 10, 'bold'))
        
        style.map('Red.TButton', background=[('active', '#c9302c'), ('disabled', '#d3d3d3')])
        style.map('Blue.TButton', background=[('active', '#286090'), ('disabled', '#d3d3d3')])
        style.map('Green.TButton', background=[('active', '#449d44'), ('disabled', '#d3d3d3')])
        style.map('Orange.TButton', background=[('active', '#ec971f'), ('disabled', '#d3d3d3')])

    def create_main_frame(self):
        """Создание основного фрейма"""
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.pack(fill=tk.BOTH, expand=True)
        return main_frame

    def create_header_section(self, parent):
        """Создание шапки приложения"""
        header_frame = ttk.Frame(parent)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = ttk.Label(header_frame, text="⚙", font=('Segoe UI', 24))
        icon_label.pack(side=tk.LEFT, padx=(0, 10))
        
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            title_frame,
            text="Контроль системы Windows",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor=tk.W)
        
        ttk.Label(
            title_frame,
            text="Управление завершением работы, перезагрузкой и аварийными режимами",
            font=('Segoe UI', 9)
        ).pack(anchor=tk.W)
        
        admin_frame = ttk.Frame(header_frame)
        admin_frame.pack(side=tk.RIGHT)
        
        ttk.Label(
            admin_frame,
            text="Администратор",
            foreground='green',
            font=('Segoe UI', 9, 'bold')
        ).pack()
        
        ttk.Label(
            admin_frame,
            text="✓ Полные права доступа",
            foreground='green',
            font=('Segoe UI', 8)
        ).pack()

    def create_action_selector(self, parent):
        """Создание выбора действия"""
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(
            action_frame,
            text="Выберите действие:",
            font=('Segoe UI', 10)
        ).pack(anchor=tk.W)
        
        btn_frame = ttk.Frame(action_frame)
        btn_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.action_var = tk.StringVar(value='shutdown')
        
        ttk.Radiobutton(
            btn_frame,
            text="Завершение работы",
            variable=self.action_var,
            value='shutdown',
            command=self.update_action_ui
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            btn_frame,
            text="Перезагрузка",
            variable=self.action_var,
            value='restart',
            command=self.update_action_ui
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Radiobutton(
            btn_frame,
            text="Синий экран (BSOD)",
            variable=self.action_var,
            value='bsod',
            command=self.update_action_ui
        ).pack(side=tk.LEFT, padx=5)

    def update_action_ui(self):
        """Обновление UI в зависимости от выбранного действия"""
        action = self.action_var.get()
        if action == 'bsod':
            self.schedule_btn.config(text="Запланировать BSOD", style='Red.TButton')
            self.immediate_btn.config(text="Немедленный BSOD", style='Red.TButton')
        elif action == 'shutdown':
            self.schedule_btn.config(text="Запланировать выключение", style='Blue.TButton')
            self.immediate_btn.config(text="Немедленное выключение", style='Blue.TButton')
        elif action == 'restart':
            self.schedule_btn.config(text="Запланировать перезагрузку", style='Orange.TButton')
            self.immediate_btn.config(text="Немедленная перезагрузка", style='Orange.TButton')

    def create_input_section(self, parent):
        """Создание блока ввода времени"""
        input_frame = ttk.Frame(parent)
        input_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(input_frame, text="Время (секунды):").grid(row=0, column=0, sticky=tk.W)
        self.time_entry = ttk.Entry(input_frame, width=15)
        self.time_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Label(input_frame, text="Быстрый выбор:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.time_picker = ttk.Combobox(
            input_frame, 
            values=["30 секунд", "1 минута", "5 минут", "15 минут", "30 минут", "1 час", "2 часа"],
            width=15,
            state="readonly"
        )
        self.time_picker.grid(row=1, column=1, sticky=tk.W, padx=5, pady=(10, 0))
        self.time_picker.bind("<<ComboboxSelected>>", self.update_time_entry)
        
        warning_frame = ttk.Frame(parent)
        warning_frame.pack(fill=tk.X, pady=(15, 0))
        
        self.warning_label = ttk.Label(
            warning_frame,
            text="⚠ Внимание: Завершение работы приведет к закрытию всех программ",
            foreground='red',
            font=('Segoe UI', 9, 'bold'),
            wraplength=500
        )
        self.warning_label.pack()

    def update_time_entry(self, event):
        """Обновление поля ввода при выборе из списка"""
        time_map = {
            "30 секунд": 30,
            "1 минута": 60,
            "5 минут": 300,
            "15 минут": 900,
            "30 минут": 1800,
            "1 час": 3600,
            "2 часа": 7200
        }
        selected = self.time_picker.get()
        if selected in time_map:
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, str(time_map[selected]))

    def create_button_section(self, parent):
        """Создание блока кнопок"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.schedule_btn = ttk.Button(
            button_frame,
            text="Запланировать выключение",
            command=self.schedule_action,
            style='Blue.TButton'
        )
        self.schedule_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        self.cancel_btn = ttk.Button(
            button_frame,
            text="Отменить",
            command=self.cancel_schedule,
            state=tk.DISABLED,
            style='Green.TButton'
        )
        self.cancel_btn.pack(side=tk.LEFT, padx=5, ipadx=10, ipady=5)
        
        self.immediate_btn = ttk.Button(
            button_frame,
            text="Немедленное выключение",
            command=self.immediate_action,
            style='Blue.TButton'
        )
        self.immediate_btn.pack(side=tk.RIGHT, padx=5, ipadx=10, ipady=5)

    def create_status_section(self, parent):
        """Создание блока статуса"""
        status_frame = ttk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Label(
            status_frame,
            text="Статус:",
            font=('Segoe UI', 9)
        ).pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Готов к планированию",
            font=('Segoe UI', 9),
            foreground='green'
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def create_countdown_section(self, parent):
        """Создание блока обратного отсчета"""
        countdown_frame = ttk.Frame(parent)
        countdown_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(
            countdown_frame,
            text="Обратный отсчет:",
            font=('Segoe UI', 10)
        ).pack(side=tk.LEFT)
        
        self.countdown_label = ttk.Label(
            countdown_frame,
            text="не активен",
            font=('Segoe UI', 10, 'bold'),
            foreground='red'
        )
        self.countdown_label.pack(side=tk.LEFT, padx=5)

    def create_footer(self, parent):
        """Создание нижнего колонтитула"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill=tk.X, pady=(20, 0))
        
        sys_info = ttk.Frame(footer_frame)
        sys_info.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(
            sys_info,
            text=f"Система: {platform.system()} {platform.release()} | "
                 f"Память: {psutil.virtual_memory().percent}% | "
                 f"CPU: {psutil.cpu_percent()}%",
            font=('Segoe UI', 8),
            foreground='#666'
        ).pack(anchor=tk.W)
        
        version = ttk.Frame(footer_frame)
        version.pack(side=tk.RIGHT)
        
        ttk.Label(
            version,
            text="v1.1 | © 2023",
            font=('Segoe UI', 8),
            foreground='#666'
        ).pack(anchor=tk.E)

    def schedule_action(self):
        """Планирование выбранного действия"""
        try:
            seconds = int(self.time_entry.get())
            if seconds <= 0:
                raise ValueError
            
            action = self.action_var.get()
            action_name = {
                'shutdown': 'завершение работы',
                'restart': 'перезагрузка',
                'bsod': 'синий экран смерти'
            }.get(action, 'действие')
            
            confirm = messagebox.askyesno(
                "Подтверждение",
                f"Вы уверены, что хотите выполнить {action_name} через {self.format_seconds(seconds)}?\n\n"
                "⚠ Все несохраненные данные будут потеряны!\n"
                "✔ Вы работаете с правами администратора\n"
                "✖ Отменить будет невозможно после запуска",
                icon='warning'
            )
            
            if confirm:
                self.current_action = action
                self.scheduled_time = datetime.now() + timedelta(seconds=seconds)
                self.update_ui_for_scheduled()
                self.update_countdown()
                
        except ValueError:
            messagebox.showerror(
                "Ошибка ввода", 
                "Пожалуйста, введите корректное положительное число секунд"
            )

    def immediate_action(self):
        """Немедленное выполнение выбранного действия"""
        action = self.action_var.get()
        action_name = {
            'shutdown': 'завершение работы',
            'restart': 'перезагрузка',
            'bsod': 'синий экран смерти'
        }.get(action, 'действие')
        
        confirm = messagebox.askyesno(
            f"Немедленное {action_name}",
            f"Вы уверены, что хотите немедленно выполнить {action_name}?\n\n"
            "⚠ Все несохраненные данные будут потеряны!\n"
            "✖ Это действие невозможно отменить",
            icon='error'
        )
        
        if confirm:
            self.execute_action(immediate=True)

    def format_seconds(self, seconds):
        """Форматирование секунд в читаемый вид"""
        periods = [
            ('час', 3600),
            ('минут', 60),
            ('секунд', 1)
        ]
        
        result = []
        for period_name, period_seconds in periods:
            if seconds >= period_seconds:
                period_value, seconds = divmod(seconds, period_seconds)
                if period_value > 0:
                    result.append(f"{period_value} {period_name}")
        
        return " ".join(result)

    def update_ui_for_scheduled(self):
        """Обновление UI после планирования"""
        action_names = {
            'shutdown': 'выключение',
            'restart': 'перезагрузка',
            'bsod': 'BSOD'
        }
        
        self.schedule_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.time_entry.config(state=tk.DISABLED)
        self.time_picker.config(state=tk.DISABLED)
        self.status_label.config(
            text=f"{action_names.get(self.current_action, 'Действие')} запланировано на {self.scheduled_time.strftime('%H:%M:%S')}",
            foreground='red'
        )

    def cancel_schedule(self):
        """Отмена запланированного действия"""
        self.scheduled_time = None
        self.countdown_running = False
        self.current_action = None
        self.schedule_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.time_entry.config(state=tk.NORMAL)
        self.time_picker.config(state=tk.NORMAL)
        self.status_label.config(
            text="Планирование отменено", 
            foreground='green'
        )
        self.countdown_label.config(text="не активен")

    def update_countdown(self):
        """Обновление обратного отсчета"""
        if not self.scheduled_time:
            return
        
        remaining = self.scheduled_time - datetime.now()
        if remaining.total_seconds() <= 0:
            self.execute_action()
            return
        
        hours, remainder = divmod(int(remaining.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        
        self.countdown_label.config(text=time_str)
        
        if not self.countdown_running:
            self.countdown_running = True
            self.root.after(1000, self.update_countdown)
        else:
            self.root.after(1000, self.update_countdown)

    def execute_action(self, immediate=False):
        """Выполнение выбранного действия"""
        try:
            if not ctypes.windll.shell32.IsUserAnAdmin():
                raise PermissionError("Требуются права администратора")
            
            if self.current_action == 'bsod' or (immediate and self.action_var.get() == 'bsod'):
                self.trigger_bsod()
            elif self.current_action == 'shutdown' or (immediate and self.action_var.get() == 'shutdown'):
                self.system_shutdown(immediate)
            elif self.current_action == 'restart' or (immediate and self.action_var.get() == 'restart'):
                self.system_restart(immediate)
                
        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                f"Не удалось выполнить действие:\n\n{str(e)}\n\n"
                "Попробуйте перезапустить программу с правами администратора."
            )
            self.cancel_schedule()

    def trigger_bsod(self):
        """Вызов синего экрана смерти"""
        try:
            ntdll = ctypes.windll.ntdll
            ctypes.windll.ntdll.RtlAdjustPrivilege(19, 1, 0, ctypes.byref(ctypes.c_bool(False)))
            ctypes.windll.ntdll.NtRaiseHardError(0xC000021A, 0, 0, 0, 6, ctypes.byref(ctypes.c_uint(0)))
        except Exception as e:
            raise Exception(f"Ошибка при вызове BSOD: {str(e)}")

    def system_shutdown(self, immediate=False):
        """Завершение работы системы"""
        try:
            if immediate:
                os.system("shutdown /s /t 0")
            else:
                os.system(f"shutdown /s /t {int((self.scheduled_time - datetime.now()).total_seconds())}")
        except Exception as e:
            raise Exception(f"Ошибка при завершении работы: {str(e)}")

    def system_restart(self, immediate=False):
        """Перезагрузка системы"""
        try:
            if immediate:
                os.system("shutdown /r /t 0")
            else:
                os.system(f"shutdown /r /t {int((self.scheduled_time - datetime.now()).total_seconds())}")
        except Exception as e:
            raise Exception(f"Ошибка при перезагрузке: {str(e)}")

    def on_close(self):
        """Обработчик закрытия окна"""
        if messagebox.askokcancel(
            "Выход",
            "Вы уверены, что хотите закрыть программу?\n\n"
            "Если запланировано действие, оно будет отменено."
        ):
            self.cancel_schedule()
            self.root.destroy()

if __name__ == "__main__":
    try:
        if platform.system() == "Windows":
            import ctypes
            ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass
    
    root = tk.Tk()
    try:
        app = SystemControlApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Произошла ошибка:\n\n{str(e)}")
        sys.exit(1)