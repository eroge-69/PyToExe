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
        self.root.title("Управление сетевым адаптером и DNS")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Проверка прав администратора
        if not is_admin():
            messagebox.showerror("Ошибка", "Это приложение должно быть запущено с правами администратора!")
            sys.exit(1)
        
        self.create_widgets()
        self.detect_network_adapter()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление сетевым адаптером и DNS", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Информация о сетевом адаптере
        self.adapter_label = ttk.Label(main_frame, text="Сетевой адаптер: определяется...")
        self.adapter_label.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Кнопка запуска
        self.start_button = ttk.Button(main_frame, text="Запустить процесс", command=self.start_process)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Прогресс-бар
        self.progress = ttk.Progressbar(main_frame, orient=tk.HORIZONTAL, length=500, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, pady=(0, 20))
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Готов к работе")
        self.status_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Лог
        log_label = ttk.Label(main_frame, text="Лог выполнения:")
        log_label.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        # Текстовое поле для лога
        self.log_text = tk.Text(main_frame, height=10, width=70)
        self.log_text.grid(row=6, column=0, columnspan=2, pady=(0, 10))
        
        # Полоса прокрутки для лога
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=6, column=2, sticky=(tk.N, tk.S))
        self.log_text['yscrollcommand'] = scrollbar.set
        
    def detect_network_adapter(self):
        """Автоматическое определение активного сетевого адаптера"""
        try:
            # Команда для получения информации о сетевых адаптерах
            result = subprocess.run(['netsh', 'interface', 'show', 'interface'], 
                                  capture_output=True, text=True, encoding='cp866')
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Подключено" in line and "Ethernet" in line:
                        parts = line.split()
                        adapter_name = ' '.join(parts[3:])
                        self.adapter_label.config(text=f"Сетевой адаптер: {adapter_name}")
                        self.adapter = adapter_name
                        self.log(f"Обнаружен сетевой адаптер: {adapter_name}")
                        return
                
                # Если не нашли Ethernet, ищем другой подключенный адаптер
                for line in lines:
                    if "Подключено" in line:
                        parts = line.split()
                        adapter_name = ' '.join(parts[3:])
                        self.adapter_label.config(text=f"Сетевой адаптер: {adapter_name}")
                        self.adapter = adapter_name
                        self.log(f"Обнаружен сетевой адаптер: {adapter_name}")
                        return
                
                self.adapter_label.config(text="Сетевой адаптер: не обнаружен")
                self.log("Не удалось обнаружить активный сетевой адаптер")
            else:
                self.log("Ошибка при определении сетевого адаптера")
                
        except Exception as e:
            self.log(f"Ошибка: {str(e)}")
    
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
                self.log("Успешно выполнено")
                return True
            else:
                self.log(f"Ошибка: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"Исключение: {str(e)}")
            return False
    
    def start_process(self):
        """Запуск процесса в отдельном потоке"""
        self.start_button.config(state=tk.DISABLED)
        thread = threading.Thread(target=self.process)
        thread.daemon = True
        thread.start()
    
    def process(self):
        """Основной процесс отключения/включения адаптера и очистки DNS"""
        try:
            self.status_label.config(text="Отключаем сетевой адаптер...")
            self.progress['value'] = 25
            self.root.update_idletasks()
            
            # Отключаем сетевой адаптер
            if not self.run_command(['netsh', 'interface', 'set', 'interface', 
                                   f'"{self.adapter}"', 'admin=disable'], 
                                  "Отключаем сетевой адаптер..."):
                self.status_label.config(text="Ошибка при отключении адаптера")
                self.start_button.config(state=tk.NORMAL)
                return
            
            time.sleep(2)  # Ждем 2 секунды
            
            self.status_label.config(text="Очищаем DNS кэш...")
            self.progress['value'] = 50
            self.root.update_idletasks()
            
            # Очищаем DNS кэш
            if not self.run_command(['ipconfig', '/flushdns'], 
                                  "Очищаем DNS кэш..."):
                self.status_label.config(text="Ошибка при очистке DNS")
                # Пытаемся включить адаптер обратно
                self.run_command(['netsh', 'interface', 'set', 'interface', 
                                f'"{self.adapter}"', 'admin=enable'], 
                               "Пытаемся включить адаптер после ошибки...")
                self.start_button.config(state=tk.NORMAL)
                return
            
            time.sleep(2)  # Ждем 2 секунды
            
            self.status_label.config(text="Включаем сетевой адаптер...")
            self.progress['value'] = 75
            self.root.update_idletasks()
            
            # Включаем сетевой адаптер
            if not self.run_command(['netsh', 'interface', 'set', 'interface', 
                                   f'"{self.adapter}"', 'admin=enable'], 
                                  "Включаем сетевой адаптер..."):
                self.status_label.config(text="Ошибка при включении адаптера")
                self.start_button.config(state=tk.NORMAL)
                return
            
            time.sleep(1)  # Ждем 1 секунду
            
            self.status_label.config(text="Процесс завершен успешно!")
            self.progress['value'] = 100
            self.root.update_idletasks()
            
            self.log("Процесс завершен успешно!")
            
        except Exception as e:
            self.log(f"Неожиданная ошибка: {str(e)}")
            self.status_label.config(text="Ошибка в процессе выполнения")
        
        self.start_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkApp(root)
    root.mainloop()