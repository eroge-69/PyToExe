import zipfile
import os
import json
import re
import time
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from googletrans import Translator

class MinecraftModTranslator:
    def __init__(self, progress_callback=None, log_callback=None):
        self.translator = Translator()
        self.supported_files = ['.json', '.lang', '.mcmeta', '.txt', '.properties']
        self.skip_files = ['enchantments.json', 'achievements.json']
        self.technical_dirs = ['assets', 'data', 'textures', 'models', 'blockstates', 'shaders', 'font']
        self.translation_cache = {}
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.cancel_requested = False
        self.total_files = 0
        self.processed_files = 0

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)

    def update_progress(self, value=None, max_value=None):
        if self.progress_callback:
            self.progress_callback(value, max_value)

    def is_technical_text(self, text: str) -> bool:
        """Проверка, является ли текст техническим (не требует перевода)"""
        # Игровые идентификаторы (item.minecraft.stone)
        if re.match(r'^[a-z0-9_.]+$', text, re.IGNORECASE):
            return True
            
        # Пути к файлам (textures/block/stone.png)
        if re.search(r'[\\/]|\.(png|jpg|jpeg|gif|bmp|tga|json|mcmeta)$', text, re.IGNORECASE):
            return True
            
        # Цветовые коды (§4)
        if re.search(r'§[0-9a-fklmnor]', text, re.IGNORECASE):
            return True
            
        # JSON-специфичные ключи
        json_keys = ['parent', 'textures', 'model', 'elements', 'from', 'to', 
                    'rotation', 'shade', 'faces', 'uv', 'texture', 'cullface']
        if any(f'"{key}":' in text for key in json_keys):
            return True
            
        return False

    def translate_text(self, text: str) -> str:
        """Перевод текста с кэшированием результатов"""
        if self.cancel_requested:
            return text
            
        if not text or not text.strip():
            return text

        # Пропускаем технические строки
        if self.is_technical_text(text):
            return text

        if text in self.translation_cache:
            return self.translation_cache[text]

        try:
            time.sleep(0.05)
            translated = self.translator.translate(text, src='en', dest='ru').text
            self.translation_cache[text] = translated
            return translated
        except Exception as e:
            self.log(f"Ошибка перевода: {e}")
            return text

    def is_technical_path(self, file_path: str) -> bool:
        """Проверка, находится ли файл в технической директории"""
        file_path = file_path.replace("\\", "/").lower()
        for dir_name in self.technical_dirs:
            if f"/{dir_name}/" in file_path:
                return True
        return False

    def process_file(self, file_path: str):
        """Обработка файлов разных типов"""
        if self.cancel_requested:
            return False
            
        filename = os.path.basename(file_path)
        
        # Пропускаем технические файлы и директории
        if any(skip in filename for skip in self.skip_files) or self.is_technical_path(file_path):
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return False
        except Exception as e:
            self.log(f"Ошибка чтения {filename}: {str(e)}")
            return False

        modified = False
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.json':
            try:
                data = json.loads(content)
                if self.translate_json(data):
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    modified = True
            except json.JSONDecodeError:
                pass

        elif ext in ['.lang', '.properties']:
            lines = []
            for line in content.split('\n'):
                if self.cancel_requested:
                    return False
                    
                if '=' in line:
                    key, value = line.split('=', 1)
                    
                    # Пропускаем технические ключи
                    if self.is_technical_text(key) or self.is_technical_text(value):
                        lines.append(line)
                        continue
                        
                    if value.strip() and not value.startswith('#'):
                        new_value = self.translate_text(value)
                        if new_value != value:
                            line = f'{key}={new_value}'
                            modified = True
                    else:
                        lines.append(line)
                else:
                    lines.append(line)
            if modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))

        elif ext in ['.txt', '.mcmeta']:
            # Пропускаем технические .mcmeta файлы
            if ext == '.mcmeta' and ('pack.mcmeta' in filename or 'animation.mcmeta' in filename):
                return False
                
            new_content = self.translate_text(content)
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modified = True

        self.processed_files += 1
        self.update_progress(self.processed_files)
        return modified

    def translate_json(self, data: any) -> bool:
        """Рекурсивный перевод JSON структур с пропуском технических полей"""
        modified = False
        
        if isinstance(data, dict):
            for key in list(data.keys()):
                if self.cancel_requested:
                    return False
                    
                # Пропускаем технические ключи
                technical_keys = ['parent', 'textures', 'model', 'elements', 'from', 'to', 
                                'rotation', 'shade', 'faces', 'uv', 'texture', 'cullface',
                                'ambientocclusion', 'gui_light', 'display', 'thirdperson_righthand',
                                'firstperson_righthand', 'registryName', 'type', 'pipeline']
                if key in technical_keys:
                    continue
                    
                if isinstance(data[key], str):
                    # Пропускаем технические значения
                    if self.is_technical_text(data[key]):
                        continue
                        
                    new_value = self.translate_text(data[key])
                    if new_value != data[key]:
                        data[key] = new_value
                        modified = True
                else:
                    if self.translate_json(data[key]):
                        modified = True
                        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if self.cancel_requested:
                    return False
                    
                if isinstance(item, str):
                    # Пропускаем технические значения
                    if self.is_technical_text(item):
                        continue
                        
                    new_value = self.translate_text(item)
                    if new_value != item:
                        data[i] = new_value
                        modified = True
                else:
                    if self.translate_json(item):
                        modified = True
        return modified

    def count_translatable_files(self, directory):
        """Подсчет файлов для перевода"""
        count = 0
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if any(file.endswith(ext) for ext in self.supported_files):
                    if not any(skip in file for skip in self.skip_files) and not self.is_technical_path(file_path):
                        count += 1
        return count

    def process_jar(self, jar_path: str, output_path: str):
        """Основной метод обработки JAR-файла"""
        start_time = time.time()
        self.cancel_requested = False
        self.translation_cache = {}
        
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Распаковка JAR
                self.log("Распаковка архива...")
                with zipfile.ZipFile(jar_path, 'r') as zip_ref:
                    zip_ref.extractall(tmp_dir)
                
                # Подсчет файлов для перевода
                self.log("Поиск файлов для перевода...")
                self.total_files = self.count_translatable_files(tmp_dir)
                self.processed_files = 0
                
                # Проверка на наличие файлов для перевода
                if self.total_files == 0:
                    self.log("Не найдено файлов для перевода!")
                    self.log("Возможные причины:")
                    self.log("1. Мод уже переведен на русский")
                    self.log("2. В моде отсутствуют текстовые ресурсы")
                    self.log("3. Все файлы находятся в технических директориях")
                    self.update_progress(0, 100)  # Устанавливаем безопасные значения
                    return False
                
                self.update_progress(0, self.total_files)
                
                # Поиск и обработка файлов
                self.log(f"Найдено {self.total_files} файлов. Начинаю перевод...")
                for root, _, files in os.walk(tmp_dir):
                    for file in files:
                        if self.cancel_requested:
                            self.log("Прервано пользователем!")
                            return False
                            
                        file_path = os.path.join(root, file)
                        if any(file.endswith(ext) for ext in self.supported_files):
                            if self.process_file(file_path):
                                self.log(f"Переведен: {file}")
                
                # Упаковка обратно в JAR
                if not self.cancel_requested:
                    self.log("Создание нового архива...")
                    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        for root, _, files in os.walk(tmp_dir):
                            for file in files:
                                if self.cancel_requested:
                                    self.log("Прервано пользователем!")
                                    return False
                                    
                                abs_path = os.path.join(root, file)
                                rel_path = os.path.relpath(abs_path, tmp_dir)
                                zipf.write(abs_path, rel_path)
            
            # Статистика
            if not self.cancel_requested:
                elapsed = time.time() - start_time
                self.log(f"\nГотово! Переведено файлов: {self.processed_files}/{self.total_files}")
                self.log(f"Время выполнения: {elapsed:.1f} секунд")
                self.log(f"Результат сохранен в: {output_path}")
                return True
                
        except Exception as e:
            self.log(f"Критическая ошибка: {str(e)}")
            return False


class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Minecraft Mod Translator")
        self.geometry("700x500")
        self.resizable(True, True)
        self.configure(bg="#f0f0f0")
        
        # Инициализация переводчика
        self.translator = None
        self.thread = None
        
        # Создание элементов интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Стили
        style = ttk.Style()
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TLabel", background="#f0f0f0", font=("Arial", 10))
        style.configure("TButton", font=("Arial", 10))
        style.configure("TEntry", font=("Arial", 10))
        style.configure("Red.TButton", foreground="red")
        
        # Главный фрейм
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Поле ввода исходного файла
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Исходный файл (.jar):").pack(side=tk.LEFT)
        self.input_entry = ttk.Entry(input_frame, width=50)
        self.input_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(input_frame, text="Обзор", 
                  command=self.browse_input).pack(side=tk.RIGHT)
        
        # Поле вывода
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(output_frame, text="Куда сохранить:").pack(side=tk.LEFT)
        self.output_entry = ttk.Entry(output_frame, width=50)
        self.output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(output_frame, text="Обзор", 
                  command=self.browse_output).pack(side=tk.RIGHT)
        
        # Прогресс-бар
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient=tk.HORIZONTAL, mode='determinate')
        self.progress_bar.pack(fill=tk.X)
        
        self.progress_label = ttk.Label(progress_frame, text="Готов к работе")
        self.progress_label.pack(pady=5)
        
        # Лог
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(log_frame, text="Лог выполнения:").pack(anchor=tk.W)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.translate_btn = ttk.Button(button_frame, text="Начать перевод", 
                                      command=self.start_translation)
        self.translate_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = ttk.Button(button_frame, text="Отмена", 
                                   style="Red.TButton", command=self.cancel_translation,
                                   state=tk.DISABLED)
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="Очистить лог", 
                 command=self.clear_log).pack(side=tk.RIGHT, padx=5)
        
    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Выберите .jar файл мода",
            filetypes=(("JAR files", "*.jar"), ("All files", "*.*"))
        )
        if file_path:
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, file_path)
            
            # Автоматически генерируем имя для выходного файла
            dir_name = os.path.dirname(file_path)
            base_name = os.path.basename(file_path)
            name, ext = os.path.splitext(base_name)
            output_path = os.path.join(dir_name, f"{name}_RU{ext}")
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, output_path)
    
    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Куда сохранить переведенный мод",
            defaultextension=".jar",
            filetypes=(("JAR files", "*.jar"), ("All files", "*.*"))
        )
        if file_path:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, file_path)
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.update_idletasks()
    
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
    
    def update_progress(self, value=None, max_value=None):
        if max_value is not None:
            self.progress_bar["maximum"] = max_value
            
        if value is not None:
            self.progress_bar["value"] = value
            # Проверяем, чтобы избежать деления на ноль
            if max_value and max_value > 0:
                percent = (value / max_value) * 100
                self.progress_label.config(text=f"Выполнено: {percent:.1f}%")
            else:
                self.progress_label.config(text="Файлы не найдены")
        
        self.update_idletasks()
    
    def start_translation(self):
        input_path = self.input_entry.get()
        output_path = self.output_entry.get()
        
        if not input_path or not output_path:
            messagebox.showerror("Ошибка", "Укажите пути к файлам!")
            return
            
        if not os.path.exists(input_path):
            messagebox.showerror("Ошибка", "Исходный файл не найден!")
            return
            
        # Очистка лога
        self.clear_log()
        self.log_message("=== Начало процесса перевода ===")
        self.log_message("ВАЖНО: Не изменяйте технические данные (пути, идентификаторы)")
        self.log_message("Пропускаются файлы в папках: assets/, data/, textures/ и др.")
        
        # Блокировка интерфейса
        self.translate_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        
        # Создание переводчика
        self.translator = MinecraftModTranslator(
            progress_callback=self.update_progress,
            log_callback=self.log_message
        )
        
        # Запуск в отдельном потоке
        self.thread = threading.Thread(
            target=self.run_translation, 
            args=(input_path, output_path),
            daemon=True
        )
        self.thread.start()
    
    def run_translation(self, input_path, output_path):
        try:
            success = self.translator.process_jar(input_path, output_path)
            if success:
                self.log_message("\nПеревод успешно завершен!")
                self.log_message("Рекомендация: Проверьте мод в игре перед использованием")
                messagebox.showinfo("Готово", "Перевод мода успешно завершен!")
            elif self.translator.total_files == 0:
                messagebox.showinfo("Информация", "Файлов для перевода не найдено!\nМод может быть уже переведен или не содержит текстовых ресурсов.")
        except Exception as e:
            self.log_message(f"\nОшибка: {str(e)}")
        finally:
            # Разблокировка интерфейса
            self.after(0, self.enable_ui)
    
    def cancel_translation(self):
        if self.translator:
            self.translator.cancel_requested = True
            self.log_message("Запрос отмены...")
            self.cancel_btn.config(state=tk.DISABLED)
    
    def enable_ui(self):
        self.translate_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="Операция завершена")


if __name__ == "__main__":
    # Проверка зависимостей
    try:
        import googletrans
    except ImportError:
        print("Установите требуемые зависимости:")
        print("pip install googletrans==4.0.0-rc1")
        exit(1)
        
    app = TranslationApp()
    app.mainloop()