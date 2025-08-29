import os
import time
import subprocess
import shutil
import threading
import tkinter as tk
from tkinter import scrolledtext
from pathlib import Path
from datetime import datetime

class XMLManagerMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("XMLManager Monitor")
        self.root.geometry("800x600")
        
        # Переменные
        self.network_path = r"\\10.68.0.11\x_all\st"
        self.target_file = "start.txt"
        self.monitoring = False
        
        self.setup_ui()
        self.start_monitoring()
    
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Фрейм для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Кнопки управления
        self.start_btn = tk.Button(button_frame, text="Запуск мониторинга", 
                                 command=self.start_monitoring)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = tk.Button(button_frame, text="Остановить мониторинг", 
                                command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(button_frame, text="Очистить лог", 
                                 command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Область для вывода лога
        self.log_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, 
                                                width=90, height=25)
        self.log_area.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.log_area.config(state=tk.DISABLED)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                            relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def log_message(self, message):
        """Добавление сообщения в лог с временной меткой"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, formatted_message)
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        
        # Обновление статуса
        self.status_var.set(message)
    
    def clear_log(self):
        """Очистка лога"""
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.log_message("Лог очищен")
    
    def start_monitoring(self):
        """Запуск мониторинга в отдельном потоке"""
        if not self.monitoring:
            self.monitoring = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            
            self.log_message("Мониторинг запущен")
            self.log_message(f"Отслеживание папки: {self.network_path}")
            self.log_message(f"Целевой файл: {self.target_file}")
            
            # Запуск мониторинга в отдельном потоке
            self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
            self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        if self.monitoring:
            self.monitoring = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.log_message("Мониторинг остановлен")
    
    def check_file_exists(self, network_path, filename):
        """Проверяет существование файла в сетевой папке"""
        file_path = os.path.join(network_path, filename)
        return os.path.exists(file_path)
    
    def delete_file(self, network_path, filename):
        """Удаляет файл из сетевой папки"""
        try:
            file_path = os.path.join(network_path, filename)
            os.remove(file_path)
            self.log_message(f"Файл {filename} успешно удален")
            return True
        except Exception as e:
            self.log_message(f"Ошибка при удалении файла: {e}")
            return False
    
    def get_xml_manager_pid(self):
        """Находит PID процесса XMLManagerServer.exe с помощью wmic"""
        try:
            command = [
                'wmic', 'process', 'where', 
                'CommandLine like \"%XMLManagerServer.exe%\"', 
                'get', 'ProcessId,CommandLine'
            ]
            
            result = subprocess.run(command, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0 and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines[1:]:
                    if line.strip() and 'XMLManagerServer.exe' in line:
                        parts = line.split()
                        for part in parts:
                            if part.isdigit():
                                return int(part)
            
            self.log_message("Процесс XMLManagerServer.exe не найден")
            return None
            
        except Exception as e:
            self.log_message(f"Ошибка при поиске PID: {e}")
            return None
    
    def kill_process(self, pid):
        """Завершает процесс по PID"""
        try:
            if pid:
                result = subprocess.run(['taskkill', '/pid', str(pid), '/f'], 
                                      capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.log_message(f"Процесс с PID {pid} успешно завершен")
                else:
                    self.log_message(f"Не удалось завершить процесс: {result.stderr}")
            else:
                self.log_message("PID не указан, завершение процесса пропущено")
        except Exception as e:
            self.log_message(f"Ошибка при завершении процесса: {e}")
    
    def start_xml_manager(self):
        """Запускает XMLManagerServer.exe"""
        try:
            program_path = r"C:\XMLManagerServer\XMLManagerServer.exe"
            
            if os.path.exists(program_path):
                subprocess.Popen([program_path], shell=True)
                self.log_message("XMLManagerServer.exe успешно запущен")
                return True
            else:
                self.log_message(f"Файл {program_path} не найден")
                return False
                
        except Exception as e:
            self.log_message(f"Ошибка при запуске программы: {e}")
            return False
    
    def monitor_loop(self):
        """Основной цикл мониторинга"""
        while self.monitoring:
            try:
                # Проверяем доступность сетевой папки
                if not os.path.exists(self.network_path):
                    self.log_message(f"Сетевая папка {self.network_path} недоступна")
                    time.sleep(30)
                    continue
                
                # Проверяем наличие файла
                if self.check_file_exists(self.network_path, self.target_file):
                    self.log_message(f"Обнаружен файл {self.target_file}")
                    
                    # Удаляем файл
                    if self.delete_file(self.network_path, self.target_file):
                        # Находим и завершаем процесс
                        pid = self.get_xml_manager_pid()
                        self.kill_process(pid)
                        
                        # Ждем 5 секунд
                        self.log_message("Ожидание 5 секунд перед запуском...")
                        time.sleep(5)
                        
                        # Запускаем программу
                        self.start_xml_manager()
                    
                    self.log_message("Ожидание следующего файла...")
                
                # Пауза между проверками
                time.sleep(1)
                
            except Exception as e:
                self.log_message(f"Произошла ошибка в цикле мониторинга: {e}")
                time.sleep(10)
    
    def on_closing(self):
        """Обработчик закрытия окна"""
        self.stop_monitoring()
        self.root.destroy()

def main():
    """Основная функция для запуска в отдельном окне"""
    root = tk.Tk()
    app = XMLManagerMonitor(root)
    
    # Обработчик закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()

if __name__ == "__main__":
    main()
