import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import time
import sys
import os

def is_admin():
    """Проверяет, запущено ли приложение с правами администратора"""
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

class NetworkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сброс сетевых настроек v0.6")
        self.root.geometry("750x550")
        self.root.resizable(False, False)
        self.root.configure(bg='white')
        
        # Центрирование окна на экране
        self.center_window()
        
        # Инициализация атрибута adapter
        self.adapter = None
        
        # Проверка прав администратора
        if not is_admin():
            messagebox.showerror("Ошибка", "Это приложение должно быть запущено с правами администратора!")
            sys.exit(1)
        
        self.create_widgets()
        self.detect_network_adapter()
    
    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def create_widgets(self):
        # Цветовая гамма: белый, оранжевый, серый, черный
        COLORS = {
            'background': 'white',
            'primary': '#FF8C00',  # оранжевый
            'secondary': '#808080', # серый
            'text': 'black',
            'light_gray': '#F0F0F0',
            'border': '#CCCCCC',
            'button_text': 'black'
        }
        
        # Стили
        style = ttk.Style()
        style.configure('TFrame', background=COLORS['background'])
        style.configure('Header.TLabel', background=COLORS['background'], 
                       foreground=COLORS['primary'], font=('Arial', 16, 'bold'))
        style.configure('Normal.TLabel', background=COLORS['background'], 
                       foreground=COLORS['text'])
        
        # Стили для кнопок с черным текстом
        style.configure('Orange.TButton', background=COLORS['primary'], 
                       foreground=COLORS['button_text'], font=('Arial', 10, 'bold'))
        style.configure('Gray.TButton', background=COLORS['secondary'], 
                       foreground=COLORS['button_text'], font=('Arial', 10))
        style.configure('Blue.TButton', background='#3498db', 
                       foreground=COLORS['button_text'], font=('Arial', 9))
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20", style='TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        header_frame = ttk.Frame(main_frame, style='TFrame')
        header_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='ew')
        
        title_label = ttk.Label(header_frame, text="Сброс сетевых настроек", style='Header.TLabel')
        title_label.grid(row=0, column=0, sticky='w')
        
        version_label = ttk.Label(header_frame, text="v0.6", style='Normal.TLabel', font=('Arial', 10))
        version_label.grid(row=0, column=1, sticky='e', padx=(10, 0))
        
        # Информация о сетевом адаптере
        self.adapter_label = ttk.Label(main_frame, text="Сетевой адаптер: определяется...", 
                                      style='Normal.TLabel', font=('Arial', 10))
        self.adapter_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Выбор адаптера вручную
        ttk.Label(main_frame, text="Или выберите адаптер вручную:", 
                 style='Normal.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        adapter_frame = ttk.Frame(main_frame, style='TFrame')
        adapter_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.adapter_var = tk.StringVar()
        self.adapter_combo = ttk.Combobox(adapter_frame, textvariable=self.adapter_var, width=45, 
                                         font=('Arial', 9), background=COLORS['light_gray'])
        self.adapter_combo.grid(row=0, column=0, sticky='w')
        
        # Фрейм для кнопок справа
        buttons_frame = ttk.Frame(adapter_frame, style='TFrame')
        buttons_frame.grid(row=0, column=1, padx=(10, 0), sticky='e')
        
        # Кнопка обновления списка адаптеров
        refresh_btn = ttk.Button(buttons_frame, text="Обновить список", 
                               command=self.populate_adapters_list, style='Blue.TButton')
        refresh_btn.grid(row=0, column=0, padx=(0, 5))
        
        # Кнопка закрытия приложения
        close_btn = ttk.Button(buttons_frame, text="Закрыть приложение", 
                             command=self.root.destroy, style='Gray.TButton')
        close_btn.grid(row=0, column=1)
        
        # Кнопка запуска
        self.start_button = ttk.Button(main_frame, text="Запустить процесс", 
                                     command=self.start_process, style='Orange.TButton')
        self.start_button.grid(row=4, column=0, columnspan=2, pady=(20, 10), sticky='ew')
        
        # Прогресс-бар с плавной анимацией
        progress_frame = ttk.Frame(main_frame, style='TFrame')
        progress_frame.grid(row=5, column=0, columnspan=2, pady=(0, 20), sticky='ew')
        
        self.progress = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, length=650, mode='determinate')
        self.progress.grid(row=0, column=0, sticky='ew')
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе", 
                                    style='Normal.TLabel', font=('Arial', 10, "bold"))
        self.status_label.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Лог
        log_label = ttk.Label(main_frame, text="Лог выполнения:", 
                             style='Normal.TLabel', font=('Arial', 10, "bold"))
        log_label.grid(row=7, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Текстовое поле для лога
        log_frame = ttk.Frame(main_frame, style='TFrame')
        log_frame.grid(row=8, column=0, columnspan=2, sticky='ew', pady=(0, 10))
        
        self.log_text = tk.Text(log_frame, height=12, width=85, bg=COLORS['light_gray'], 
                               fg=COLORS['text'], font=('Consolas', 9), relief='solid', 
                               bd=1, highlightbackground=COLORS['border'])
        self.log_text.grid(row=0, column=0, sticky='ew')
        
        # Полоса прокрутки для лога
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
        # Фрейм для копирайта внизу
        copyright_frame = ttk.Frame(main_frame, style='TFrame')
        copyright_frame.grid(row=9, column=0, columnspan=2, pady=(10, 0), sticky='ew')
        
        # Копирайт с 2025 годом
        copyright_label = ttk.Label(copyright_frame, text="© 2025 ГБУЗ РБ Красноусольская ЦРБ", 
                                   style='Normal.TLabel', font=('Arial', 9))
        copyright_label.grid(row=0, column=0, sticky='w')
    
    def smooth_progress(self, target_value, duration=1000):
        """Плавное заполнение прогресс-бара"""
        current_value = self.progress['value']
        steps = 20
        step_delay = duration // steps
        step_value = (target_value - current_value) / steps
        
        def update_progress(step):
            if step < steps:
                new_value = current_value + (step + 1) * step_value
                self.progress['value'] = new_value
                self.root.after(step_delay, update_progress, step + 1)
        
        update_progress(0)
    
    def get_all_adapters(self):
        """Получает список всех сетевых адаптеров"""
        try:
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                  capture_output=True, text=True, encoding='cp866')
            
            adapters = []
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if line.strip() and not line.startswith('---') and not line.startswith('Состояние'):
                        parts = line.split()
                        if len(parts) >= 4:
                            # Берем название адаптера (все что после 3-го элемента)
                            adapter_name = ' '.join(parts[3:])
                            adapters.append(adapter_name)
            
            return adapters
        except Exception as e:
            self.log(f"Ошибка при получении списка адаптеров: {str(e)}")
            return []
    
    def populate_adapters_list(self):
        """Заполняет выпадающий список адаптерами"""
        adapters = self.get_all_adapters()
        self.adapter_combo['values'] = adapters
        if adapters:
            self.adapter_combo.current(0)
            self.log("Список адаптеров обновлен")
    
    def detect_network_adapter(self):
        """Автоматическое определение активного сетевого адаптера"""
        try:
            # Сначала попробуем получить список всех адаптеров
            self.populate_adapters_list()
            
            # Команда для получения информации о подключенных адаптерах
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                  capture_output=True, text=True, encoding='cp866')
            
            connected_adapters = []
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    # Ищем подключенные адаптеры (на русском или английском)
                    if ("Connected" in line or "Подключено" in line) and not line.startswith('Admin'):
                        parts = line.split()
                        if len(parts) >= 4:
                            adapter_name = ' '.join(parts[3:])
                            connected_adapters.append(adapter_name)
            
            if connected_adapters:
                # Берем первый подключенный адаптер
                self.adapter = connected_adapters[0]
                self.adapter_label.config(text=f"Обнаружен активный адаптер: {self.adapter}")
                self.adapter_var.set(self.adapter)
                self.log(f"Автоматически обнаружен сетевой адаптер: {self.adapter}")
            else:
                self.adapter_label.config(text="Активный адаптер не обнаружен. Выберите вручную.")
                self.log("Активный адаптер не обнаружен автоматически")
                
        except Exception as e:
            self.log(f"Ошибка при определении сетевого адаптера: {str(e)}")
    
    def set_automatic_ip(self):
        """Устанавливает автоматическое получение IP (только IP, не DNS) для адаптера Ethernet"""
        try:
            self.log("Настраиваем автоматическое получение IP для Ethernet...")
            
            # Команда для установки автоматического получения IP (только IP)
            cmd = ['netsh', 'interface', 'ip', 'set', 'address', 'name="Ethernet"', 'source=dhcp']
            
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='cp866')
            if result.returncode == 0:
                self.log("✓ Автоматическое получение IP настроено успешно")
                return True
            else:
                self.log(f"✗ Ошибка при настройке автоматического IP: {result.stderr}")
                return False
            
        except Exception as e:
            self.log(f"✗ Исключение при настройке автоматического IP: {str(e)}")
            return False
    
    def log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def run_command(self, command, description):
        """Выполнение команды и логирование результата"""
        self.log(description)
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='cp866')
            if result.returncode == 0:
                self.log("✓ Успешно выполнено")
                return True
            else:
                error_msg = result.stderr if result.stderr else "Неизвестная ошибка"
                self.log(f"✗ Ошибка: {error_msg}")
                return False
        except Exception as e:
            self.log(f"✗ Исключение: {str(e)}")
            return False
    
    def start_process(self):
        """Запуск процесса в отдельном потоке"""
        # Получаем выбранный адаптер
        selected_adapter = self.adapter_var.get()
        if not selected_adapter:
            messagebox.showerror("Ошибка", "Выберите сетевой адаптер!")
            return
        
        self.adapter = selected_adapter
        self.start_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()
    
    def process(self):
        """Основной процесс отключения/включения адаптера и очистки DNS"""
        try:
            self.log(f"Начинаем работу с адаптером: {self.adapter}")
            
            # Шаг 0: Настраиваем автоматическое получение IP для Ethernet (только IP)
            self.status_label.config(text="Настраиваем автоматическое получение IP...")
            self.smooth_progress(10, 300)
            
            self.set_automatic_ip()
            time.sleep(1)  # Ждем 1 секунду
            
            # Шаг 1: Отключаем сетевой адаптер
            self.status_label.config(text="Отключаем сетевой адаптер...")
            self.smooth_progress(25, 500)
            
            if not self.run_command(['netsh', 'interface', 'set', 'interface', 
                                   self.adapter, 'admin=disable'], 
                                  f"Отключаем адаптер {self.adapter}..."):
                self.status_label.config(text="Ошибка при отключении адаптера")
                self.start_button.config(state=tk.NORMAL)
                return
            
            time.sleep(3)  # Ждем 3 секунды
            
            # Шаг 2: Очищаем DNS кэш
            self.status_label.config(text="Очищаем DNS кэш...")
            self.smooth_progress(50, 500)
            
            if not self.run_command(['ipconfig', '/flushdns'], 
                                  "Очищаем DNS кэш..."):
                self.status_label.config(text="Ошибка при очистке DNS")
                self.log("Продолжаем процесс несмотря на ошибку DNS")
            
            time.sleep(2)  # Ждем 2 секунды
            
            # Шаг 3: Включаем сетевой адапter
            self.status_label.config(text="Включаем сетевой адаптер...")
            self.smooth_progress(75, 500)
            
            if not self.run_command(['netsh', 'interface', 'set', 'interface', 
                                   self.adapter, 'admin=enable'], 
                                  f"Включаем адаптер {self.adapter}..."):
                self.status_label.config(text="Ошибка при включении адаптера")
                self.start_button.config(state=tk.NORMAL)
                return
            
            time.sleep(2)  # Ждем 2 секунды
            
            # Завершение
            self.status_label.config(text="Процесс завершен успешно!")
            self.smooth_progress(100, 500)
            
            self.log("✓ Процесс завершен успешно!")
            
        except Exception as e:
            self.log(f"✗ Неожиданная ошибка: {str(e)}")
            self.status_label.config(text="Ошибка в процессе выполнения")
        
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    # Скрываем консольное окно (только для Windows)
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()