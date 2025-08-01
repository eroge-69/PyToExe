import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import shutil
import threading

class OsuHitsoundConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер семпл-паков FL Studio -> osu!")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # Переменные
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.processing = False
        
        # Создание интерфейса
        self.create_widgets()
        
        # Настройка стилей
        self.setup_styles()
        
    def setup_styles(self):
        """Настройка стилей для виджетов"""
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Path.TButton", padding=5)
        style.configure("Action.TButton", padding=10)
        
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        
        # Заголовок
        title_label = ttk.Label(self.root, text="Конвертер семпл-паков FL Studio -> osu!", 
                               style="Title.TLabel")
        title_label.pack(pady=10)
        
        # Фрейм для путей
        path_frame = ttk.LabelFrame(self.root, text="Пути к папкам", padding=10)
        path_frame.pack(fill="x", padx=10, pady=5)
        
        # Исходная папка
        input_frame = ttk.Frame(path_frame)
        input_frame.pack(fill="x", pady=5)
        
        ttk.Label(input_frame, text="Исходная папка (FL Studio):").pack(anchor="w")
        
        input_path_frame = ttk.Frame(input_frame)
        input_path_frame.pack(fill="x", pady=2)
        
        ttk.Entry(input_path_frame, textvariable=self.input_path).pack(side="left", fill="x", expand=True)
        ttk.Button(input_path_frame, text="Обзор", command=self.browse_input).pack(side="right", padx=(5,0))
        
        # Папка вывода
        output_frame = ttk.Frame(path_frame)
        output_frame.pack(fill="x", pady=5)
        
        ttk.Label(output_frame, text="Папка вывода (osu!):").pack(anchor="w")
        
        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill="x", pady=2)
        
        ttk.Entry(output_path_frame, textvariable=self.output_path).pack(side="left", fill="x", expand=True)
        ttk.Button(output_path_frame, text="Обзор", command=self.browse_output).pack(side="right", padx=(5,0))
        
        # Фрейм для кнопок
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        # Кнопки действий
        self.convert_button = ttk.Button(button_frame, text="Конвертировать", 
                                        command=self.start_conversion, style="Action.TButton")
        self.convert_button.pack(side="left", padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Остановить", 
                                     command=self.stop_conversion, state="disabled")
        self.stop_button.pack(side="left", padx=(0, 10))
        
        ttk.Button(button_frame, text="О программе", command=self.show_about).pack(side="right")
        
        # Прогресс бар
        self.progress = ttk.Progressbar(self.root, mode="indeterminate")
        self.progress.pack(fill="x", padx=10, pady=5)
        
        # Лог
        log_frame = ttk.LabelFrame(self.root, text="Лог обработки", padding=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        
        # Статус
        self.status_var = tk.StringVar(value="Готов к работе")
        self.status_label = ttk.Label(self.root, textvariable=self.status_var, 
                                     relief="sunken", anchor="w")
        self.status_label.pack(fill="x", padx=10, pady=(0, 10))
        
    def browse_input(self):
        """Выбор исходной папки"""
        folder = filedialog.askdirectory(title="Выберите папку с семплами FL Studio")
        if folder:
            self.input_path.set(folder)
            
    def browse_output(self):
        """Выбор папки вывода"""
        folder = filedialog.askdirectory(title="Выберите папку для сохранения osu! семплов")
        if folder:
            self.output_path.set(folder)
            
    def log_message(self, message):
        """Добавление сообщения в лог"""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        self.root.update_idletasks()
        
    def update_status(self, message):
        """Обновление статуса"""
        self.status_var.set(message)
        self.root.update_idletasks()
        
    def start_conversion(self):
        """Запуск конвертации в отдельном потоке"""
        if not self.input_path.get():
            messagebox.showerror("Ошибка", "Укажите исходную папку!")
            return
            
        if not self.output_path.get():
            messagebox.showerror("Ошибка", "Укажите папку вывода!")
            return
            
        if not os.path.exists(self.input_path.get()):
            messagebox.showerror("Ошибка", "Исходная папка не существует!")
            return
            
        # Запуск в отдельном потоке
        self.processing = True
        self.convert_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.progress.start()
        
        # Запуск конвертации в потоке
        thread = threading.Thread(target=self.convert_samples)
        thread.daemon = True
        thread.start()
        
    def stop_conversion(self):
        """Остановка конвертации"""
        self.processing = False
        self.convert_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()
        self.update_status("Остановлено пользователем")
        self.log_message("Конвертация остановлена пользователем")
        
    def convert_samples(self):
        """Основная функция конвертации семплов"""
        try:
            input_folder = self.input_path.get()
            output_folder = self.output_path.get()
            
            # Создаем папку вывода
            os.makedirs(output_folder, exist_ok=True)
            
            # Очищаем лог
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.config(state="disabled")
            
            self.log_message(f"Начало конвертации...")
            self.log_message(f"Исходная папка: {input_folder}")
            self.log_message(f"Папка вывода: {output_folder}")
            self.log_message("-" * 50)
            
            # Маппинг имен
            sample_mapping = {
                'hitnormal': ['snare', 'sn', 'clap', 'cl', 'rim', 'rimshot', 'kick', 'bd'],
                'hitwhistle': ['whistle', 'whis', 'hihat', 'hh', 'hho', 'hhc', 'openhat'],
                'hitfinish': ['finish', 'fin', 'cymbal', 'cy', 'crash', 'cr', 'ride'],
                'hitclap': ['clap', 'cl', 'handclap', 'hc'],
                'slidertick': ['tick', 'slide', 'slider', 'stick'],
                'sliderwhistle': ['slidewhis', 'sliderwhis', 'slwhis'],
                'combobreak': ['combobreak', 'break', 'fail', 'error'],
            }
            
            # Расширения аудиофайлов
            audio_extensions = {'.wav', '.mp3', '.ogg', '.flac'}
            
            # Получаем список файлов
            files = [f for f in os.listdir(input_folder) 
                    if os.path.isfile(os.path.join(input_folder, f))]
            
            audio_files = [f for f in files 
                          if os.path.splitext(f)[1].lower() in audio_extensions]
            
            if not audio_files:
                self.log_message("В исходной папке не найдено аудиофайлов!")
                return
                
            self.log_message(f"Найдено аудиофайлов: {len(audio_files)}")
            
            processed_files = 0
            copied_files = 0
            
            for filename in audio_files:
                if not self.processing:  # Проверка на остановку
                    break
                    
                file_path = os.path.join(input_folder, filename)
                file_ext = os.path.splitext(filename)[1].lower()
                file_name_without_ext = os.path.splitext(filename)[0].lower()
                
                processed_files += 1
                self.update_status(f"Обработка файла {processed_files}/{len(audio_files)}: {filename}")
                
                # Ищем соответствия
                found_match = False
                for osu_name, fl_names in sample_mapping.items():
                    for fl_name in fl_names:
                        if (fl_name.lower() == file_name_without_ext or 
                            fl_name.lower() in file_name_without_ext or
                            file_name_without_ext.startswith(fl_name.lower()) or
                            file_name_without_ext.endswith(fl_name.lower())):
                            
                            # Создаем новое имя файла
                            new_filename = f"{osu_name}{file_ext}"
                            new_file_path = os.path.join(output_folder, new_filename)
                            
                            # Копируем файл с новым именем
                            try:
                                shutil.copy2(file_path, new_file_path)
                                self.log_message(f"✓ {filename} -> {new_filename}")
                                copied_files += 1
                                found_match = True
                                break
                    
                    if found_match:
                        break
                
                # Если не нашли соответствия, копируем как есть
                if not found_match and self.processing:
                    # Проверяем, может это уже правильное имя для osu!
                    if any(keyword in file_name_without_ext for keyword in 
                           ['hitnormal', 'hitwhistle', 'hitfinish', 'hitclap', 
                            'slidertick', 'sliderwhistle', 'combobreak']):
                        new_file_path = os.path.join(output_folder, filename)
                        shutil.copy2(file_path, new_file_path)
                        self.log_message(f"✓ {filename} (уже правильное имя)")
                        copied_files += 1
                    else:
                        # Для остальных файлов создаем базовое имя hitnormal
                        new_filename = f"hitnormal_{processed_files}{file_ext}"
                        new_file_path = os.path.join(output_folder, new_filename)
                        shutil.copy2(file_path, new_file_path)
                        self.log_message(f"~ {filename} -> {new_filename} (по умолчанию)")
                        copied_files += 1
                
                # Обновляем прогресс
                progress_percent = (processed_files / len(audio_files)) * 100
                self.root.after(0, lambda: None)  # Обновление GUI
            
            if self.processing:  # Только если не было остановлено
                self.log_message("-" * 50)
                self.log_message(f"Обработано файлов: {processed_files}")
                self.log_message(f"Скопировано файлов: {copied_files}")
                self.log_message(f"Готово! Семпл-пак для osu! находится в: {output_folder}")
                self.update_status(f"Готово! Обработано {copied_files} файлов")
                
        except Exception as e:
            self.log_message(f"Ошибка: {str(e)}")
            self.update_status("Ошибка при конвертации")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
            
        finally:
            # Завершение процесса
            self.processing = False
            self.root.after(0, self.finish_conversion)
            
    def finish_conversion(self):
        """Завершение конвертации"""
        self.convert_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.progress.stop()
        
    def show_about(self):
        """Показ информации о программе"""
        about_text = """
Конвертер семпл-паков FL Studio -> osu!
Версия: 1.0

Программа автоматически конвертирует семпл-паки 
из FL Studio в формат, совместимый с osu!.

Поддерживаемые форматы: WAV, MP3, OGG, FLAC

Автоматически распознаются следующие типы:
- hitnormal (snare, clap, rimshot и др.)
- hitwhistle (hihat, whistle и др.)
- hitfinish (crash, cymbal и др.)
- hitclap (clap и др.)
- slidertick (tick, slider и др.)
        """
        messagebox.showinfo("О программе", about_text)

def main():
    root = tk.Tk()
    app = OsuHitsoundConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()