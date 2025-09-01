import os
import shutil
import zipfile
import threading
import time
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Обработчик архивов и PDF файлов")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Переменные для хранения путей
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.is_running = False
        self.processing_thread = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Конфигурация сетки
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Обработчик архивов и PDF файлов", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Выбор исходной папки
        ttk.Label(main_frame, text="Папка для отслеживания:").grid(row=1, column=0, sticky=tk.W, pady=5)
        source_entry = ttk.Entry(main_frame, textvariable=self.source_dir, width=50)
        source_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_source).grid(row=1, column=2, padx=5, pady=5)
        
        # Выбор целевой папки
        ttk.Label(main_frame, text="Папка для сохранения:").grid(row=2, column=0, sticky=tk.W, pady=5)
        target_entry = ttk.Entry(main_frame, textvariable=self.target_dir, width=50)
        target_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Обзор", command=self.browse_target).grid(row=2, column=2, padx=5, pady=5)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Запуск", command=self.start_processing)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(button_frame, text="Остановить", command=self.stop_processing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        
        # Лог действий
        ttk.Label(main_frame, text="Лог действий:").grid(row=4, column=0, sticky=tk.W, pady=(20, 5))
        
        self.log_area = scrolledtext.ScrolledText(main_frame, width=70, height=20)
        self.log_area.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Настройка весов для растягивания
        main_frame.rowconfigure(5, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
    def browse_source(self):
        directory = filedialog.askdirectory(title="Выберите папку для отслеживания")
        if directory:
            self.source_dir.set(directory)
            
    def browse_target(self):
        directory = filedialog.askdirectory(title="Выберите папку для сохранения")
        if directory:
            self.target_dir.set(directory)
            
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"
        self.log_area.insert(tk.END, formatted_message)
        self.log_area.see(tk.END)
        self.root.update_idletasks()
        
    def start_processing(self):
        if not self.source_dir.get() or not self.target_dir.get():
            messagebox.showerror("Ошибка", "Пожалуйста, укажите обе папки!")
            return
            
        if not os.path.exists(self.source_dir.get()):
            messagebox.showerror("Ошибка", "Исходная папка не существует!")
            return
            
        # Создаем целевую директорию если не существует
        os.makedirs(self.target_dir.get(), exist_ok=True)
        
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("Обработка запущена...")
        
        # Запускаем обработку в отдельном потоке
        self.processing_thread = threading.Thread(target=self.process_files, daemon=True)
        self.processing_thread.start()
        
        self.log_message("Запущена обработка файлов")
        
    def stop_processing(self):
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("Обработка остановлена")
        self.log_message("Обработка файлов остановлена")
        
    def process_files(self):
        # Словарь для отслеживания времени создания папок
        folder_creation_times = {}
        
        while self.is_running:
            try:
                # Проверяем все файлы в исходной директории
                for filename in os.listdir(self.source_dir.get()):
                    if not self.is_running:
                        break
                        
                    filepath = os.path.join(self.source_dir.get(), filename)
                    
                    # Обработка архивов
                    if filename.endswith(('.zip', '.rar', '.7z')):
                        try:
                            # Создаем уникальное имя для папки
                            archive_name = os.path.splitext(filename)[0]
                            new_folder_name = f"{archive_name}-W25"
                            dest_path = os.path.join(self.target_dir.get(), new_folder_name)
                            
                            # Создаем целевую папку
                            os.makedirs(dest_path, exist_ok=True)
                            
                            # Запоминаем время создания папки
                            folder_creation_times[dest_path] = datetime.now()
                            
                            # Перемещаем архив
                            shutil.move(filepath, dest_path)
                            
                            # Разархивируем
                            archive_path = os.path.join(dest_path, filename)
                            if filename.endswith('.zip'):
                                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                                    zip_ref.extractall(dest_path)
                            # Добавьте здесь обработку других форматов архивов при необходимости
                            
                            # Удаляем архив
                            os.remove(archive_path)
                            
                            # Извлекаем файлы из подпапок и удаляем пустые папки
                            for root, dirs, files in os.walk(dest_path):
                                for file in files:
                                    if root != dest_path:
                                        shutil.move(os.path.join(root, file), 
                                                  os.path.join(dest_path, file))
                            
                            # Удаляем пустые папки
                            for root, dirs, files in os.walk(dest_path, topdown=False):
                                for dir in dirs:
                                    dir_path = os.path.join(root, dir)
                                    if not os.listdir(dir_path):
                                        os.rmdir(dir_path)
                            
                            self.log_message(f"Обработан архив: {filename}")
                            
                        except Exception as e:
                            self.log_message(f"Ошибка при обработке архива {filename}: {str(e)}")
                    
                    # Обработка PDF файлов
                    elif filename.endswith('.pdf'):
                        try:
                            # Находим самую новую папку
                            if folder_creation_times:
                                latest_folder = max(folder_creation_times, key=folder_creation_times.get)
                                shutil.move(filepath, os.path.join(latest_folder, filename))
                                self.log_message(f"Перемещен PDF файл: {filename} в папку {os.path.basename(latest_folder)}")
                            else:
                                self.log_message(f"Нет созданных папок для перемещения PDF: {filename}")
                                
                        except Exception as e:
                            self.log_message(f"Ошибка при обработке PDF {filename}: {str(e)}")
                
                time.sleep(5)  # Проверка каждые 5 секунд
                
            except Exception as e:
                self.log_message(f"Ошибка в основном цикле: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.stop_processing(), root.destroy()))
    root.mainloop()