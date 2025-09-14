#!/usr/bin/env python3
"""
Image Collector - инструмент для сбора изображений в единую папку
"""#!/usr/bin/env python3
"""
Графический интерфейс для копирования изображений в одну папку.
"""

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Set
from dataclasses import dataclass
import logging

# Конфигурация логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class Config:
    """Конфигурационные параметры скрипта."""
    SOURCE_DIR: Path
    DESTINATION_DIR: Path
    IMAGE_EXTENSIONS: Set[str] = frozenset({
        '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif',
        '.heic', '.raw', '.cr2', '.nef', '.arw'
    })


class ImageCopier:
    """Класс для управления процессом копирования изображений."""
    
    def __init__(self, config: Config):
        self.config = config
        self.copied_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
    def _should_process_file(self, file_path: Path) -> bool:
        """Проверяет, является ли файл изображением подходящего формата."""
        return (
            file_path.is_file() and 
            file_path.suffix.lower() in self.config.IMAGE_EXTENSIONS
        )
    
    def _handle_existing_file(self, destination: Path, original_name: str) -> Path:
        """Обрабатывает конфликт имен файлов."""
        if not destination.exists():
            return destination
            
        stem, suffix = destination.stem, destination.suffix
        counter = 1
        
        while True:
            new_name = f"{stem}_copy_{counter:03d}{suffix}"
            new_path = destination.with_name(new_name)
            
            if not new_path.exists():
                logger.warning(f"Файл {original_name} существует, создается {new_name}")
                return new_path
            counter += 1
    
    def copy_images(self, progress_callback=None) -> dict:
        """Копирует изображения и возвращает статистику."""
        if not self.config.SOURCE_DIR.exists():
            raise FileNotFoundError(f"Исходная директория не найдена: {self.config.SOURCE_DIR}")
        
        # Создаем целевую папку
        self.config.DESTINATION_DIR.mkdir(parents=True, exist_ok=True)
        
        # Собираем все файлы для подсчета общего количества
        all_files = []
        for root, dirs, files in os.walk(self.config.SOURCE_DIR):
            current_dir = Path(root)
            for file_name in files:
                file_path = current_dir / file_name
                all_files.append(file_path)
        
        total_files = len(all_files)
        processed = 0
        
        if total_files == 0:
            return {'copied': 0, 'skipped': 0, 'errors': 0}
        
        # Обрабатываем файлы
        for file_path in all_files:
            if self._should_process_file(file_path):
                try:
                    # Создаем путь назначения - просто имя файла в целевой папке
                    destination_path = self.config.DESTINATION_DIR / file_path.name
                    
                    # Обрабатываем конфликты имен
                    destination_path = self._handle_existing_file(destination_path, file_path.name)
                    
                    # Копируем файл
                    shutil.copy2(file_path, destination_path)
                    self.copied_count += 1
                    logger.info(f"Скопирован: {file_path.name}")
                    
                except OSError as e:
                    self.error_count += 1
                    logger.error(f"Ошибка копирования {file_path}: {e}")
                except Exception as e:
                    self.error_count += 1
                    logger.exception(f"Неожиданная ошибка при обработке {file_path}")
            else:
                self.skipped_count += 1
            
            processed += 1
            if progress_callback and total_files > 0:
                progress = (processed / total_files) * 100
                progress_callback(progress)
        
        return {
            'copied': self.copied_count,
            'skipped': self.skipped_count,
            'errors': self.error_count
        }


class ImageCopyApp:
    """Графическое приложение для копирования изображений."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Копировщик изображений")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        self.setup_ui()
        self.source_path = Path()
        self.dest_base_path = Path()  # Базовая папка назначения
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Source folder selection
        ttk.Label(main_frame, text="Исходная папка:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.source_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.source_var, state='readonly').grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Выбрать...", command=self.select_source).grid(
            row=0, column=2, padx=5, pady=5)
        
        # Destination folder selection
        ttk.Label(main_frame, text="Папка назначения:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.dest_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.dest_var, state='readonly').grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Button(main_frame, text="Выбрать...", command=self.select_destination).grid(
            row=1, column=2, padx=5, pady=5)
        
        # Info label
        ttk.Label(main_frame, text="Все изображения будут скопированы в одну папку", 
                 font=('Arial', 9), foreground='gray').grid(
                 row=2, column=0, columnspan=3, pady=5)
        
        # Progress bar
        ttk.Label(main_frame, text="Прогресс:").grid(row=3, column=0, sticky=tk.W, pady=10)
        self.progress = ttk.Progressbar(main_frame, mode='determinate')
        self.progress.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), padx=5, pady=10)
        
        # Status label
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(main_frame, textvariable=self.status_var).grid(
            row=4, column=0, columnspan=3, pady=10)
        
        # Results label
        self.results_var = tk.StringVar()
        ttk.Label(main_frame, textvariable=self.results_var).grid(
            row=5, column=0, columnspan=3, pady=5)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        ttk.Button(button_frame, text="Начать копирование", 
                  command=self.start_copying).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Очистить", 
                  command=self.clear_fields).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Выход", 
                  command=self.root.quit).pack(side=tk.LEFT, padx=10)
    
    def select_source(self):
        """Выбор исходной папки."""
        folder = filedialog.askdirectory(title="Выберите исходную папку")
        if folder:
            self.source_path = Path(folder)
            self.source_var.set(str(self.source_path))
    
    def select_destination(self):
        """Выбор базовой папки назначения."""
        folder = filedialog.askdirectory(title="Выберите папку назначения")
        if folder:
            self.dest_base_path = Path(folder)
            self.dest_var.set(str(self.dest_base_path))
    
    def update_progress(self, value):
        """Обновляет прогресс бар."""
        self.progress['value'] = value
        self.status_var.set(f"Выполняется... {value:.1f}%")
        self.root.update_idletasks()
    
    def start_copying(self):
        """Запускает процесс копирования."""
        if not self.source_path or not self.dest_base_path:
            messagebox.showerror("Ошибка", "Выберите исходную папку и папку назначения!")
            return
        
        if self.source_path == self.dest_base_path:
            messagebox.showerror("Ошибка", "Исходная папка и папка назначения не могут быть одинаковыми!")
            return
        
        try:
            # Создаем папку с именем исходной папки внутри папки назначения
            folder_name = self.source_path.name
            destination_dir = self.dest_base_path / folder_name
            
            config = Config(SOURCE_DIR=self.source_path, DESTINATION_DIR=destination_dir)
            copier = ImageCopier(config)
            
            # Блокируем кнопки во время работы
            self.set_buttons_state('disabled')
            
            # Запускаем копирование
            results = copier.copy_images(progress_callback=self.update_progress)
            
            # Показываем результаты
            self.show_results(results, destination_dir)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.set_buttons_state('normal')
    
    def set_buttons_state(self, state):
        """Изменяет состояние кнопок."""
        for widget in self.root.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.state(['!disabled' if state == 'normal' else 'disabled'])
    
    def show_results(self, results, destination_dir):
        """Показывает результаты работы."""
        self.results_var.set(
            f"Готово! Создана папка: {destination_dir.name}\n"
            f"Скопировано: {results['copied']}, "
            f"Пропущено: {results['skipped']}, "
            f"Ошибок: {results['errors']}"
        )
        self.status_var.set("Завершено")
        
        if results['copied'] > 0:
            messagebox.showinfo("Успех", 
                               f"Копирование завершено успешно!\n"
                               f"Все изображения находятся в папке:\n{destination_dir}")
        else:
            messagebox.showwarning("Предупреждение", "Не найдено изображений для копирования!")
    
    def clear_fields(self):
        """Очищает все поля."""
        self.source_var.set("")
        self.dest_var.set("")
        self.status_var.set("Готов к работе")
        self.results_var.set("")
        self.progress['value'] = 0
        self.source_path = Path()
        self.dest_base_path = Path()


def main():
    """Запуск графического приложения."""
    root = tk.Tk()
    app = ImageCopyApp(root)
    
    # Центрирование окна
    root.eval('tk::PlaceWindow . center')
    
    root.mainloop()


if __name__ == "__main__":
    main()

import os
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import Set, List, Dict, Optional, Callable
import logging
import threading

#region Logger Configuration
class AppLogger:
    """Настройка системы логирования приложения"""
    
    def __init__(self):
        self.logger = logging.getLogger('ImageCollector')
        self._setup_logger()
    
    def _setup_logger(self):
        """Конфигурация логгера"""
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            
            # Консольный вывод
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)

logger = AppLogger()
#endregion

#region Model
class CopyConfiguration:
    """Конфигурация параметров копирования"""
    
    __slots__ = ('source_directory', 'destination_base', 'image_extensions')
    
    def __init__(self, source_dir: Path, dest_base: Path):
        self.source_directory = source_dir
        self.destination_base = dest_base
        self.image_extensions = {
            '.jpg', '.jpeg', '.png', '.webp', '.gif', 
            '.bmp', '.tiff', '.tif', '.heic', '.raw', 
            '.cr2', '.nef', '.arw', '.svg'
        }
    
    def validate_paths(self) -> bool:
        """Проверка корректности путей"""
        return (self.source_directory.exists() and 
                self.source_directory.is_dir() and
                self.destination_base.exists() and
                self.destination_base.is_dir() and
                self.source_directory != self.destination_base)

class CopyResult:
    """Результаты операции копирования"""
    
    __slots__ = ('copied_files', 'skipped_files', 'error_count', 'target_directory')
    
    def __init__(self):
        self.copied_files = 0
        self.skipped_files = 0
        self.error_count = 0
        self.target_directory = None
    
    def __str__(self) -> str:
        return (f"Скопировано: {self.copied_files}, "
                f"Пропущено: {self.skipped_files}, "
                f"Ошибок: {self.error_count}")

class ImageOperations:
    """Операции с изображениями"""
    
    def __init__(self, config: CopyConfiguration):
        self.config = config
        self.result = CopyResult()
    
    def _is_image_file(self, file_path: Path) -> bool:
        """Проверяет, является ли файл изображением"""
        return (file_path.is_file() and 
                file_path.suffix.lower() in self.config.image_extensions)
    
    def _generate_unique_filename(self, target_path: Path, original_name: str) -> Path:
        """Генерирует уникальное имя файла при конфликте"""
        if not target_path.exists():
            return target_path
        
        stem = target_path.stem
        suffix = target_path.suffix
        counter = 1
        
        while True:
            new_filename = f"{stem}_копия_{counter:03d}{suffix}"
            new_path = target_path.with_name(new_filename)
            
            if not new_path.exists():
                logger.info(f"Файл '{original_name}' переименован в '{new_filename}'")
                return new_path
            counter += 1
    
    def _collect_image_files(self) -> List[Path]:
        """Собирает все файлы изображений из исходной директории"""
        image_files = []
        
        for current_dir, _, files in os.walk(self.config.source_directory):
            for filename in files:
                file_path = Path(current_dir) / filename
                if self._is_image_file(file_path):
                    image_files.append(file_path)
        
        return image_files
    
    def execute_copy_operation(self, progress_callback: Optional[Callable] = None) -> CopyResult:
        """Выполняет операцию копирования изображений"""
        if not self.config.validate_paths():
            raise ValueError("Некорректные пути директорий")
        
        # Создаем целевую директорию с именем исходной папки
        target_dir_name = self.config.source_directory.name
        target_directory = self.config.destination_base / target_dir_name
        target_directory.mkdir(exist_ok=True)
        
        self.result.target_directory = target_directory
        
        # Получаем все изображения
        image_files = self._collect_image_files()
        total_files = len(image_files)
        
        if total_files == 0:
            logger.warning("Изображения не найдены в указанной директории")
            return self.result
        
        # Копируем файлы
        for index, source_file in enumerate(image_files, 1):
            try:
                target_file = target_directory / source_file.name
                target_file = self._generate_unique_filename(target_file, source_file.name)
                
                shutil.copy2(source_file, target_file)
                self.result.copied_files += 1
                
                logger.info(f"Успешно скопирован: {source_file.name}")
                
            except OSError as error:
                self.result.error_count += 1
                logger.error(f"Ошибка копирования {source_file.name}: {error}")
            except Exception as error:
                self.result.error_count += 1
                logger.error(f"Неожиданная ошибка при обработке {source_file.name}: {error}")
            
            # Вызываем callback прогресса
            if progress_callback:
                progress = (index / total_files) * 100
                progress_callback(progress)
        
        self.result.skipped_files = total_files - self.result.copied_files - self.result.error_count
        return self.result
#endregion

#region View
class MainWindow:
    """Главное окно приложения"""
    
    def __init__(self, root: tk.Tk, controller: 'AppController'):
        self.root = root
        self.controller = controller
        self._setup_window()
        self._create_widgets()
    
    def _setup_window(self):
        """Настройка основного окна"""
        self.root.title("Сборщик изображений")
        self.root.geometry("650x450")
        self.root.resizable(False, False)
        self.root.configure(bg='#f0f0f0')
        
        # Центрирование окна
        self._center_window()
    
    def _center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def _create_widgets(self):
        """Создает элементы интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20", style='Main.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        header_label = ttk.Label(
            main_frame, 
            text="Сборщик изображений", 
            font=('Segoe UI', 16, 'bold'),
            foreground='#2c3e50'
        )
        header_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Выбор исходной директории
        ttk.Label(main_frame, text="Исходная папка:", font=('Segoe UI', 10)).grid(
            row=1, column=0, sticky=tk.W, pady=8)
        
        self.source_var = tk.StringVar()
        source_entry = ttk.Entry(main_frame, textvariable=self.source_var, 
                               font=('Segoe UI', 9), state='readonly', width=40)
        source_entry.grid(row=1, column=1, padx=8, pady=8, sticky=tk.EW)
        
        ttk.Button(main_frame, text="Обзор...", 
                  command=self.controller.select_source_directory).grid(
                  row=1, column=2, padx=8, pady=8)
        
        # Выбор директории назначения
        ttk.Label(main_frame, text="Папка назначения:", font=('Segoe UI', 10)).grid(
            row=2, column=0, sticky=tk.W, pady=8)
        
        self.dest_var = tk.StringVar()
        dest_entry = ttk.Entry(main_frame, textvariable=self.dest_var, 
                             font=('Segoe UI', 9), state='readonly', width=40)
        dest_entry.grid(row=2, column=1, padx=8, pady=8, sticky=tk.EW)
        
        ttk.Button(main_frame, text="Обзор...", 
                  command=self.controller.select_destination_directory).grid(
                  row=2, column=2, padx=8, pady=8)
        
        # Информационная панель
        info_frame = ttk.Frame(main_frame, style='Info.TFrame')
        info_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=15)
        
        info_label = ttk.Label(
            info_frame, 
            text="• Все изображения будут собраны в одну папку\n"
                 "• Папка создается автоматически с именем исходной директории\n"
                 "• Конфликтующие имена файлов будут переименованы",
            font=('Segoe UI', 9),
            foreground='#7f8c8d',
            justify=tk.LEFT
        )
        info_label.pack(padx=10, pady=10)
        
        # Прогресс-бар
        ttk.Label(main_frame, text="Выполнение:", font=('Segoe UI', 10)).grid(
            row=4, column=0, sticky=tk.W, pady=12)
        
        self.progress = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress.grid(row=4, column=1, columnspan=2, padx=8, pady=12, sticky=tk.EW)
        
        # Статус
        self.status_var = tk.StringVar(value="Ожидание выбора директорий")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                               font=('Segoe UI', 9), foreground='#34495e')
        status_label.grid(row=5, column=0, columnspan=3, pady=8)
        
        # Результаты
        self.result_var = tk.StringVar()
        result_label = ttk.Label(main_frame, textvariable=self.result_var, 
                               font=('Segoe UI', 9), foreground='#27ae60')
        result_label.grid(row=6, column=0, columnspan=3, pady=8)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(
            button_frame, 
            text="Запустить сбор", 
            command=self.controller.start_copy_process,
            style='Accent.TButton'
        )
        self.start_button.pack(side=tk.LEFT, padx=12)
        
        ttk.Button(button_frame, text="Сброс", 
                  command=self.controller.reset_fields).pack(side=tk.LEFT, padx=12)
        
        ttk.Button(button_frame, text="Выход", 
                  command=self.controller.exit_application).pack(side=tk.LEFT, padx=12)
        
        # Настройка стилей
        self._configure_styles()
        
        # Настройка весов колонок
        main_frame.columnconfigure(1, weight=1)
    
    def _configure_styles(self):
        """Настройка стилей элементов"""
        style = ttk.Style()
        style.configure('Main.TFrame', background='#ffffff')
        style.configure('Info.TFrame', background='#ecf0f1')
        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'))
    
    def update_progress(self, value: float):
        """Обновление прогресс-бара"""
        self.progress['value'] = value
        self.status_var.set(f"Выполнение: {value:.1f}%")
    
    def update_results(self, result: CopyResult):
        """Обновление результатов операции"""
        if result.copied_files > 0:
            self.result_var.set(
                f"Готово! Создана папка: {result.target_directory.name}\n"
                f"Успешно скопировано: {result.copied_files} файлов"
            )
        else:
            self.result_var.set("Изображения не найдены")
    
    def set_controls_state(self, enabled: bool):
        """Установка состояния элементов управления"""
        state = 'normal' if enabled else 'disabled'
        self.start_button.config(state=state)
    
    def show_error(self, message: str):
        """Отображение сообщения об ошибке"""
        messagebox.showerror("Ошибка", message)
    
    def show_success(self, message: str):
        """Отображение сообщения об успехе"""
        messagebox.showinfo("Успех", message)
    
    def show_warning(self, message: str):
        """Отображение предупреждения"""
        messagebox.showwarning("Внимание", message)
#endregion

#region Controller
class AppController:
    """Контроллер приложения"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.view = MainWindow(self.root, self)
        self.copy_thread = None
        self.is_processing = False
        
        self.source_directory = None
        self.destination_directory = None
    
    def select_source_directory(self):
        """Выбор исходной директории"""
        directory = filedialog.askdirectory(title="Укажите исходную папку с изображениями")
        if directory:
            self.source_directory = Path(directory)
            self.view.source_var.set(str(self.source_directory))
    
    def select_destination_directory(self):
        """Выбор директории назначения"""
        directory = filedialog.askdirectory(title="Укажите папку для сохранения результатов")
        if directory:
            self.destination_directory = Path(directory)
            self.view.dest_var.set(str(self.destination_directory))
    
    def _validate_inputs(self) -> bool:
        """Проверка корректности введенных данных"""
        if not self.source_directory or not self.destination_directory:
            self.view.show_error("Необходимо выбрать обе директории")
            return False
        
        if self.source_directory == self.destination_directory:
            self.view.show_error("Исходная и целевая директории не должны совпадать")
            return False
        
        if not self.source_directory.exists():
            self.view.show_error("Исходная директория не существует")
            return False
        
        if not self.destination_directory.exists():
            self.view.show_error("Целевая директория не существует")
            return False
        
        return True
    
    def _copy_operation_thread(self):
        """Поток выполнения операции копирования"""
        try:
            config = CopyConfiguration(self.source_directory, self.destination_directory)
            operations = ImageOperations(config)
            
            result = operations.execute_copy_operation(self.view.update_progress)
            
            # Обновляем UI в основном потоке
            self.root.after(0, lambda: self._on_copy_complete(result))
            
        except Exception as error:
            self.root.after(0, lambda: self.view.show_error(f"Ошибка выполнения: {error}"))
            self.root.after(0, self._on_operation_finished)
    
    def _on_copy_complete(self, result: CopyResult):
        """Обработка завершения операции копирования"""
        self.view.update_results(result)
        
        if result.copied_files > 0:
            self.view.show_success(
                f"Операция завершена успешно!\n"
                f"Скопировано файлов: {result.copied_files}\n"
                f"Папка с результатами: {result.target_directory}"
            )
        else:
            self.view.show_warning("Изображения не найдены в указанной директории")
        
        self._on_operation_finished()
    
    def _on_operation_finished(self):
        """Завершение операции"""
        self.is_processing = False
        self.view.set_controls_state(True)
        self.view.status_var.set("Операция завершена")
    
    def start_copy_process(self):
        """Запуск процесса копирования"""
        if self.is_processing:
            return
        
        if not self._validate_inputs():
            return
        
        self.is_processing = True
        self.view.set_controls_state(False)
        self.view.status_var.set("Выполняется сбор изображений...")
        self.view.result_var.set("")
        self.view.progress['value'] = 0
        
        # Запускаем в отдельном потоке
        self.copy_thread = threading.Thread(target=self._copy_operation_thread, daemon=True)
        self.copy_thread.start()
    
    def reset_fields(self):
        """Сброс полей ввода"""
        self.source_directory = None
        self.destination_directory = None
        self.view.source_var.set("")
        self.view.dest_var.set("")
        self.view.status_var.set("Ожидание выбора директорий")
        self.view.result_var.set("")
        self.view.progress['value'] = 0