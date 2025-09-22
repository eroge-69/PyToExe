import os
import time
import shutil
import threading
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

class BackupApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SilkSong Save Backup")
        self.root.geometry("500x300")
        
        # Переменные для отслеживания
        self.is_monitoring = False
        self.monitor_thread = None
        
        # Пути к папкам
        self.folder_path = r'C:\Users\MashPC\AppData\LocalLow\Team Cherry\Hollow Knight Silksong'
        self.backup_base_folder = r'C:\Users\MashPC\AppData\LocalLow\Team Cherry\Hollow Knight SilksongSave'
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Проверяем существование папок
        self.check_folders()
    
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Hollow Knight SilkSong Save Backup", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)
        
        # Информация о путях
        path_info = ttk.LabelFrame(main_frame, text="Пути", padding="5")
        path_info.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        source_label = ttk.Label(path_info, text=f"Исходная папка: {self.folder_path}")
        source_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        backup_label = ttk.Label(path_info, text=f"Папка для бэкапов: {self.backup_base_folder}")
        backup_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Начать отслеживание", 
                                      command=self.start_monitoring)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Остановить", 
                                     command=self.stop_monitoring, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10))
        status_label.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Лог событий
        log_frame = ttk.LabelFrame(main_frame, text="Лог событий", padding="5")
        log_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Создаем текстовое поле для лога с прокруткой
        self.log_text = tk.Text(log_frame, height=8, width=60)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Настройка веса строк и столбцов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
    
    def check_folders(self):
        """Проверяет существование папок"""
        if not os.path.exists(self.folder_path):
            self.log_message(f"ОШИБКА: Исходная папка не найдена: {self.folder_path}")
            self.start_button.config(state=tk.DISABLED)
        
        if not os.path.exists(self.backup_base_folder):
            try:
                os.makedirs(self.backup_base_folder)
                self.log_message(f"Создана папка для бэкапов: {self.backup_base_folder}")
            except Exception as e:
                self.log_message(f"ОШИБКА: Не удалось создать папку для бэкапов: {e}")
                self.start_button.config(state=tk.DISABLED)
    
    def log_message(self, message):
        """Добавляет сообщение в лог"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)  # Автопрокрутка к последнему сообщению
        print(log_entry.strip())
    
    def get_files_snapshot(self, path):
        """Создает снимок файлов в папке с их временем изменения"""
        try:
            return {f: os.path.getmtime(os.path.join(path, f)) for f in os.listdir(path)}
        except Exception as e:
            self.log_message(f"Ошибка при создании снимка: {e}")
            return {}
    
    def monitoring_loop(self):
        """Основной цикл отслеживания"""
        scan_interval = 5
        previous_snapshot = self.get_files_snapshot(self.folder_path)
        backup_folder = None
        
        while self.is_monitoring:
            time.sleep(scan_interval)
            
            if not self.is_monitoring:
                break
                
            current_snapshot = self.get_files_snapshot(self.folder_path)
            changes_detected = False
            
            # Проверяем изменения
            for f in current_snapshot:
                if f not in previous_snapshot:
                    # Новый файл
                    if backup_folder is None:
                        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        backup_folder = os.path.join(self.backup_base_folder, f'backup_{timestamp}')
                        os.makedirs(backup_folder, exist_ok=True)
                    
                    src = os.path.join(self.folder_path, f)
                    dst = os.path.join(backup_folder, f)
                    shutil.copy2(src, dst)
                    self.log_message(f'Добавлен файл: {f}')
                    changes_detected = True
                    
                elif current_snapshot[f] != previous_snapshot[f]:
                    # Файл изменён
                    if backup_folder is None:
                        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
                        backup_folder = os.path.join(self.backup_base_folder, f'backup_{timestamp}')
                        os.makedirs(backup_folder, exist_ok=True)
                    
                    src = os.path.join(self.folder_path, f)
                    dst = os.path.join(backup_folder, f)
                    shutil.copy2(src, dst)
                    self.log_message(f'Файл изменён: {f}')
                    changes_detected = True
            
            # Проверяем удаленные файлы
            for f in previous_snapshot:
                if f not in current_snapshot:
                    self.log_message(f'Файл удалён: {f}')
                    changes_detected = True
            
            # Создаем полную копию при изменениях
            if changes_detected and backup_folder:
                full_backup_path = os.path.join(self.backup_base_folder, f'full_backup_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}')
                try:
                    shutil.copytree(self.folder_path, full_backup_path)
                    self.log_message(f'Создана полная копия: {os.path.basename(full_backup_path)}')
                except Exception as e:
                    self.log_message(f'Ошибка при создании полной копии: {e}')
            
            previous_snapshot = current_snapshot
        
        self.log_message("Отслеживание остановлено")
    
    def start_monitoring(self):
        """Запускает отслеживание"""
        if not os.path.exists(self.folder_path):
            messagebox.showerror("Ошибка", "Исходная папка не найдена!")
            return
        
        self.is_monitoring = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Отслеживание запущено")
        
        self.log_message("Запуск отслеживания...")
        
        # Запускаем отслеживание в отдельном потоке
        self.monitor_thread = threading.Thread(target=self.monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Останавливает отслеживание"""
        self.is_monitoring = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Отслеживание остановлено")
        self.log_message("Остановка отслеживания...")

def main():
    root = tk.Tk()
    app = BackupApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
