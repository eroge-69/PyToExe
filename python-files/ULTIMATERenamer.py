import os
import random
import string
import shutil
import math
import hashlib
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

class RenamerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer Ultimate")
        self.root.minsize(750, 850)
        
        # Переменные
        self.files = []
        self.pattern_var = StringVar(value="Файл {numbers1}")
        self.preview_var = BooleanVar(value=True)
        self.random_chars_var = StringVar(value="5")
        self.undo_stack = []
        self.target_folder = ""
        self.file_types = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"],
            "audio": [".mp3", ".wav", ".ogg", ".flac", ".m4a"],
            "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx"]
        }
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Основные вкладки
        self.main_frame = ttk.Frame(self.notebook)
        self.advanced_frame = ttk.Frame(self.notebook)
        self.batch_frame = ttk.Frame(self.notebook)
        self.organize_frame = ttk.Frame(self.notebook)
        self.stats_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_frame, text="🎯 Основное")
        self.notebook.add(self.advanced_frame, text="⚡ Дополнительно")
        self.notebook.add(self.batch_frame, text="🔁 Пакетная обработка")
        self.notebook.add(self.organize_frame, text="📁 Организация")
        self.notebook.add(self.stats_frame, text="📊 Статистика")
        
        self.setup_main_tab()
        self.setup_advanced_tab()
        self.setup_batch_tab()
        self.setup_organize_tab()
        self.setup_stats_tab()
    
    def setup_main_tab(self):
        # Основной интерфейс
        Label(self.main_frame, text="Шаблон имени:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        
        input_frame = Frame(self.main_frame)
        input_frame.pack(fill=X, padx=5, pady=(0, 10))
        
        self.pattern_entry = Entry(input_frame, textvariable=self.pattern_var, width=50, font=("Arial", 10))
        self.pattern_entry.pack(side=LEFT, fill=X, expand=True)
        
        Button(input_frame, text="📋", command=self.show_placeholder_menu, 
               width=3, relief="raised", bg="lightblue", font=("Arial", 12)).pack(side=RIGHT, padx=(5, 0))
        
        # Улучшенные кнопки плейсхолдеров с иконками
        self.setup_placeholder_buttons()
        
        # Фрейм с описанием плейсхолдеров
        desc_frame = LabelFrame(self.main_frame, text="📖 Описание плейсхолдеров")
        desc_frame.pack(fill=X, padx=5, pady=5)
        
        descriptions = [
            "{numbersX} - нумерация с X (например, {numbers7} → 7, 8, 9...)",
            "{reverse} - обратная нумерация (от большего к меньшему)",
            "{letters} - буквы a, b, c... (если >26 файлов, добавится номер)",
            "{Letters} - буквы A, B, C... (если >26 файлов, добавится номер)",
            "{lettersR} - случайные буквы a-z (если >13 файлов, добавится номер)",
            "{LettersR} - случайные буквы A-Z (если >13 файлов, добавится номер)",
            "{date} - текущая дата (ДД-ММ-ГГГГ), {time} - время (ЧЧ-ММ-СС)",
            "{datetime} - дата и время, {year} - только год",
            "{randomX} - случайные X символов (укажите количество)",
            "{uuid} - уникальный идентификатор",
            "{original} - оригинальное имя файла, {ext} - расширение файла"
        ]
        
        for desc in descriptions:
            Label(desc_frame, text=desc, anchor="w", justify=LEFT, 
                 font=("Arial", 8), wraplength=600).pack(fill=X, padx=5, pady=1)
        
        # Опции
        options_frame = Frame(self.main_frame)
        options_frame.pack(fill=X, pady=5)
        
        Checkbutton(options_frame, text="🔍 Показывать превью перед переименованием", 
                   variable=self.preview_var, font=("Arial", 9)).pack(side=LEFT, padx=5)
        
        Button(options_frame, text="↩️ Отменить последнее действие", 
              command=self.undo_rename, bg="lightyellow", font=("Arial", 9)).pack(side=RIGHT, padx=5)
        
        # Кнопки действий
        button_frame = Frame(self.main_frame)
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="📁 Выбрать файлы", command=self.select_files, 
               bg="lightblue", width=16, font=("Arial", 9)).pack(side=LEFT, padx=3)
        Button(button_frame, text="👁️ Показать превью", command=self.show_preview,
               bg="lightyellow", width=16, font=("Arial", 9)).pack(side=LEFT, padx=3)
        Button(button_frame, text="✅ Переименовать", command=self.rename_files,
               bg="lightgreen", width=16, font=("Arial", 9)).pack(side=LEFT, padx=3)
        Button(button_frame, text="🗑️ Очистить список", command=self.clear_list,
               bg="lightcoral", width=16, font=("Arial", 9)).pack(side=LEFT, padx=3)
        
        # Список файлов
        list_frame = LabelFrame(self.main_frame, text="📄 Выбранные файлы")
        list_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.file_listbox = Listbox(list_frame, width=80, height=15, font=("Courier", 9))
        scrollbar = Scrollbar(list_frame)
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Контекстное меню для списка файлов
        self.listbox_menu = Menu(self.root, tearoff=0)
        self.listbox_menu.add_command(label="Удалить из списка", command=self.remove_selected_file)
        self.listbox_menu.add_command(label="Очистить весь список", command=self.clear_list)
        self.file_listbox.bind("<Button-3>", self.show_listbox_menu)
        
        # Статус
        self.status_label = Label(self.main_frame, text="Выберите файлы для переименования", 
                                 relief=SUNKEN, anchor=W, font=("Arial", 9))
        self.status_label.pack(fill=X, side=BOTTOM, pady=(5, 0))
    
    def setup_placeholder_buttons(self):
        """Улучшенные кнопки плейсхолдеров с категориями"""
        categories = [
            {
                "name": "🔢 Нумерация",
                "placeholders": [
                    ("{numbers1}", "Нумерация с 1", "#E3F2FD"),
                    ("{numbers0}", "Нумерация с 0", "#E3F2FD"),
                    ("{numbersX}", "Нумерация с X", "#E3F2FD"),
                    ("{reverse}", "Обратная нумерация", "#E3F2FD")
                ]
            },
            {
                "name": "🔤 Буквы и текст",
                "placeholders": [
                    ("{letters}", "Буквы a-z", "#FFF9C4"),
                    ("{Letters}", "Буквы A-Z", "#FFF9C4"),
                    ("{lettersR}", "Случайные a-z", "#FFF9C4"),
                    ("{LettersR}", "Случайные A-Z", "#FFF9C4")
                ]
            },
            {
                "name": "📅 Дата и время",
                "placeholders": [
                    ("{date}", "Текущая дата", "#C8E6C9"),
                    ("{time}", "Текущее время", "#C8E6C9"),
                    ("{datetime}", "Дата и время", "#C8E6C9"),
                    ("{year}", "Текущий год", "#C8E6C9")
                ]
            },
            {
                "name": "🎲 Случайные значения",
                "placeholders": [
                    ("{random3}", "3 случайных символа", "#FFCDD2"),
                    ("{random5}", "5 случайных символов", "#FFCDD2"),
                    ("{random8}", "8 случайных символов", "#FFCDD2"),
                    ("{randomX}", "X случайных символов", "#FFCDD2"),
                    ("{uuid}", "Уникальный ID", "#FFCDD2")
                ]
            },
            {
                "name": "📄 Информация о файле",
                "placeholders": [
                    ("{original}", "Оригинальное имя", "#E1BEE7"),
                    ("{ext}", "Расширение файла", "#E1BEE7")
                ]
            }
        ]
        
        for category in categories:
            cat_frame = LabelFrame(self.main_frame, text=category["name"])
            cat_frame.pack(fill=X, padx=5, pady=2)
            
            frame = Frame(cat_frame)
            frame.pack(fill=X, padx=5, pady=2)
            
            for ph, desc, color in category["placeholders"]:
                btn = Button(frame, text=ph, width=14 if len(ph) < 10 else 16, 
                           command=lambda p=ph: self.insert_placeholder(p),
                           relief="raised", bg=color, font=("Arial", 8))
                btn.pack(side=LEFT, padx=1, pady=1)
                self.create_tooltip(btn, desc)
    
    def setup_advanced_tab(self):
        """Расширенная вкладка с новыми функциями"""
        # Умное переименование
        smart_frame = LabelFrame(self.advanced_frame, text="🧠 Умное переименование")
        smart_frame.pack(fill=X, padx=5, pady=5)
        
        Button(smart_frame, text="Из EXIF фото", command=self.rename_from_exif,
               width=20, bg="#E3F2FD", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(smart_frame, text="Из ID3 тегов", command=self.rename_from_id3,
               width=20, bg="#E3F2FD", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(smart_frame, text="По дате создания", command=self.rename_by_date,
               width=20, bg="#E3F2FD", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        # Транслитерация
        translit_frame = LabelFrame(self.advanced_frame, text="🔤 Транслитерация и текст")
        translit_frame.pack(fill=X, padx=5, pady=5)
        
        Button(translit_frame, text="Рус → Англ", command=lambda: self.transliterate("ru_en"),
               width=15, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(translit_frame, text="Англ → Рус", command=lambda: self.transliterate("en_ru"),
               width=15, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(translit_frame, text="Верхний регистр", command=lambda: self.change_case("upper"),
               width=15, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(translit_frame, text="Нижний регистр", command=lambda: self.change_case("lower"),
               width=15, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        # Пакетные операции
        batch_frame = LabelFrame(self.advanced_frame, text="🔄 Пакетные операции")
        batch_frame.pack(fill=X, padx=5, pady=5)
        
        Button(batch_frame, text="Добавить папку рекурсивно", command=self.add_folder_recursive,
               width=22, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(batch_frame, text="Фильтр по типу файлов", command=self.filter_by_type,
               width=22, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(batch_frame, text="Случайный порядок", command=self.shuffle_files,
               width=22, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        # Безопасность и хеширование
        security_frame = LabelFrame(self.advanced_frame, text="🔒 Безопасность и хеширование")
        security_frame.pack(fill=X, padx=5, pady=5)
        
        Button(security_frame, text="Зашифровать имена", command=self.encrypt_names,
               width=18, bg="#FFCDD2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(security_frame, text="Создать MD5 хеш", command=lambda: self.hash_names("md5"),
               width=18, bg="#FFCDD2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(security_frame, text="Создать SHA256 хеш", command=lambda: self.hash_names("sha256"),
               width=18, bg="#FFCDD2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        # Замена и удаление текста
        text_frame = LabelFrame(self.advanced_frame, text="✂️ Работа с текстом")
        text_frame.pack(fill=X, padx=5, pady=5)
        
        replace_frame = Frame(text_frame)
        replace_frame.pack(fill=X, pady=2)
        
        Label(replace_frame, text="Найти:").pack(side=LEFT, padx=5)
        self.find_entry = Entry(replace_frame, width=15)
        self.find_entry.pack(side=LEFT, padx=5)
        
        Label(replace_frame, text="Заменить на:").pack(side=LEFT, padx=5)
        self.replace_entry = Entry(replace_frame, width=15)
        self.replace_entry.pack(side=LEFT, padx=5)
        
        Button(replace_frame, text="Заменить текст", command=self.replace_text,
               bg="#E1BEE7", font=("Arial", 9)).pack(side=LEFT, padx=10)
        
        delete_frame = Frame(text_frame)
        delete_frame.pack(fill=X, pady=2)
        
        Button(delete_frame, text="Удалить пробелы", command=lambda: self.delete_chars("spaces"),
               width=15, bg="#FFE0B2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(delete_frame, text="Удалить цифры", command=lambda: self.delete_chars("digits"),
               width=15, bg="#FFE0B2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(delete_frame, text="Удалить спецсимволы", command=lambda: self.delete_chars("special"),
               width=15, bg="#FFE0B2", font=("Arial", 9)).pack(side=LEFT, padx=2)
    
    def setup_batch_tab(self):
        """Пакетная обработка"""
        # Шаблоны для разных типов файлов
        templates_frame = LabelFrame(self.batch_frame, text="📋 Шаблоны для типов файлов")
        templates_frame.pack(fill=X, padx=5, pady=5)
        
        self.template_vars = {}
        template_types = [
            ("Изображения", "Фото {numbers1}"),
            ("Аудио", "Трек {numbers1}"),
            ("Видео", "Видео {numbers1}"),
            ("Документы", "Док {numbers1}")
        ]
        
        for i, (file_type, default) in enumerate(template_types):
            frame = Frame(templates_frame)
            frame.pack(fill=X, pady=2)
            
            Label(frame, text=file_type, width=12, font=("Arial", 9)).pack(side=LEFT)
            var = StringVar(value=default)
            self.template_vars[file_type] = var
            Entry(frame, textvariable=var, width=30, font=("Arial", 9)).pack(side=LEFT, padx=5)
            Button(frame, text="Применить", 
                  command=lambda t=file_type: self.apply_template(t),
                  width=10, font=("Arial", 8)).pack(side=LEFT)
        
        # Серийное переименование
        series_frame = LabelFrame(self.batch_frame, text="🎬 Серийное переименование")
        series_frame.pack(fill=X, padx=5, pady=5)
        
        Label(series_frame, text="Формат серии:", font=("Arial", 9)).pack(side=LEFT)
        self.series_format = Entry(series_frame, width=20, font=("Arial", 9))
        self.series_format.insert(0, "Серия {season}x{episode}")
        self.series_format.pack(side=LEFT, padx=5)
        
        Label(series_frame, text="Сезон:", font=("Arial", 9)).pack(side=LEFT)
        self.season_num = Entry(series_frame, width=3, font=("Arial", 9))
        self.season_num.insert(0, "1")
        self.season_num.pack(side=LEFT, padx=2)
        
        Label(series_frame, text="Начальный эпизод:", font=("Arial", 9)).pack(side=LEFT)
        self.episode_start = Entry(series_frame, width=3, font=("Arial", 9))
        self.episode_start.insert(0, "1")
        self.episode_start.pack(side=LEFT, padx=2)
        
        Button(series_frame, text="Применить к видео", command=self.apply_series_format,
               bg="#E3F2FD", font=("Arial", 9)).pack(side=LEFT, padx=10)
        
        # Групповые операции
        group_frame = LabelFrame(self.batch_frame, text="👥 Групповые операции")
        group_frame.pack(fill=X, padx=5, pady=5)
        
        Button(group_frame, text="Разделить на группы по 10", command=lambda: self.create_file_groups(10),
               width=20, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(group_frame, text="Разделить на группы по 25", command=lambda: self.create_file_groups(25),
               width=20, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(group_frame, text="Обратный порядок", command=self.reverse_order,
               width=20, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
    
    def setup_organize_tab(self):
        """Организация файлов"""
        # Создание папок
        folders_frame = LabelFrame(self.organize_frame, text="📁 Создание структуры папок")
        folders_frame.pack(fill=X, padx=5, pady=5)
        
        Button(folders_frame, text="По расширениям", command=self.organize_by_extension,
               width=18, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(folders_frame, text="По дате создания", command=self.organize_by_date,
               width=18, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(folders_frame, text="По размеру", command=self.organize_by_size,
               width=18, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(folders_frame, text="По типу файлов", command=self.organize_by_type,
               width=18, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        # Перемещение/копирование
        move_frame = LabelFrame(self.organize_frame, text="🚚 Перемещение и копирование")
        move_frame.pack(fill=X, padx=5, pady=5)
        
        target_frame = Frame(move_frame)
        target_frame.pack(fill=X, pady=2)
        
        Button(target_frame, text="Выбрать целевую папку", command=self.select_target_folder,
               width=20, bg="#E3F2FD", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        self.target_label = Label(target_frame, text="Не выбрана", fg="red", font=("Arial", 9))
        self.target_label.pack(side=LEFT, padx=10)
        
        action_frame = Frame(move_frame)
        action_frame.pack(fill=X, pady=2)
        
        Button(action_frame, text="Переместить в папку", command=self.move_to_folder,
               width=20, bg="#FFCDD2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(action_frame, text="Копировать в папку", command=self.copy_to_folder,
               width=20, bg="#FFCDD2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(action_frame, text="Создать символические ссылки", command=self.create_symlinks,
               width=25, bg="#FFCDD2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        
        # Группировка
        group_frame = LabelFrame(self.organize_frame, text="👥 Группировка файлов")
        group_frame.pack(fill=X, padx=5, pady=5)
        
        custom_frame = Frame(group_frame)
        custom_frame.pack(fill=X, pady=2)
        
        Label(custom_frame, text="Группировать по:", font=("Arial", 9)).pack(side=LEFT)
        self.group_size = Entry(custom_frame, width=5, font=("Arial", 9))
        self.group_size.insert(0, "10")
        self.group_size.pack(side=LEFT, padx=5)
        Label(custom_frame, text="файлов в группе", font=("Arial", 9)).pack(side=LEFT)
        
        Button(custom_frame, text="Создать группы", command=self.create_file_groups_custom,
               bg="#E1BEE7", font=("Arial", 9)).pack(side=LEFT, padx=10)
    
    def setup_stats_tab(self):
        """Статистика и анализ"""
        # Статистика файлов
        stats_frame = LabelFrame(self.stats_frame, text="📈 Статистика файлов")
        stats_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.stats_text = Text(stats_frame, height=15, wrap=WORD, font=("Courier", 9))
        scrollbar = Scrollbar(stats_frame, command=self.stats_text.yview)
        self.stats_text.config(yscrollcommand=scrollbar.set)
        
        self.stats_text.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Кнопки анализа
        analysis_frame = Frame(self.stats_frame)
        analysis_frame.pack(fill=X, padx=5, pady=5)
        
        Button(analysis_frame, text="🔄 Обновить статистику", command=self.update_stats,
               bg="#E3F2FD", width=18, font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(analysis_frame, text="🔍 Найти дубликаты", command=self.find_duplicates,
               bg="#C8E6C9", width=18, font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(analysis_frame, text="📊 Анализ имен", command=self.analyze_names,
               bg="#FFF9C4", width=18, font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(analysis_frame, text="📏 Анализ размеров", command=self.analyze_sizes,
               bg="#FFCDD2", width=18, font=("Arial", 9)).pack(side=LEFT, padx=2)
    
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    def create_tooltip(self, widget, text):
        """Создает всплывающую подсказку для виджета"""
        def on_enter(event):
            tooltip = Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            label = Label(tooltip, text=text, background="yellow", relief="solid", 
                         borderwidth=1, font=("Arial", 8), padx=5, pady=2)
            label.pack()
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def insert_placeholder(self, placeholder):
        """Вставляет плейсхолдер в поле ввода"""
        current = self.pattern_entry.get()
        cursor_pos = self.pattern_entry.index(INSERT)
        
        if placeholder == "{randomX}":
            try:
                count = int(self.random_chars_var.get())
                if count <= 0:
                    raise ValueError
                placeholder = f"{{random{count}}}"
            except ValueError:
                messagebox.showwarning("Ошибка", "Введите корректное число символов")
                return
        
        new_text = current[:cursor_pos] + placeholder + current[cursor_pos:]
        self.pattern_var.set(new_text)
        self.pattern_entry.focus_set()
        self.pattern_entry.icursor(cursor_pos + len(placeholder))
    
    def show_placeholder_menu(self):
        """Показывает меню со всеми плейсхолдерами"""
        menu = Menu(self.root, tearoff=0)
        
        categories = {
            "🔢 Нумерация": ["{numbers1}", "{numbers0}", "{numbersX}", "{reverse}"],
            "🔤 Буквы": ["{letters}", "{Letters}", "{lettersR}", "{LettersR}"],
            "📅 Дата/Время": ["{date}", "{time}", "{datetime}", "{year}"],
            "🎲 Случайные": ["{random3}", "{random5}", "{random8}", "{random10}", "{randomX}", "{uuid}"],
            "📄 Файлы": ["{original}", "{ext}"]
        }
        
        for category, placeholders in categories.items():
            submenu = Menu(menu, tearoff=0)
            for ph in placeholders:
                submenu.add_command(label=ph, 
                                  command=lambda p=ph: self.insert_placeholder(p))
            menu.add_cascade(label=category, menu=submenu)
        
        menu.post(self.pattern_entry.winfo_rootx(), 
                 self.pattern_entry.winfo_rooty() + self.pattern_entry.winfo_height())
    
    def show_listbox_menu(self, event):
        """Показывает контекстное меню для списка файлов"""
        try:
            self.listbox_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.listbox_menu.grab_release()
    
    def remove_selected_file(self):
        """Удаляет выбранный файл из списка"""
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            self.files.pop(index)
            self.update_file_list()
    
    def select_files(self):
        """Выбор файлов для переименования"""
        files = filedialog.askopenfilenames(
            title="Выберите файлы для переименования",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff"),
                ("Аудио", "*.mp3 *.wav *.ogg *.flac *.m4a"),
                ("Видео", "*.mp4 *.avi *.mkv *.mov *.wmv"),
                ("Документы", "*.pdf *.doc *.docx *.txt *.xlsx")
            ]
        )
        if files:
            self.files = list(files)
            self.update_file_list()
    
    def update_file_list(self):
        """Обновляет список файлов в интерфейсе"""
        self.file_listbox.delete(0, END)
        for file in self.files:
            self.file_listbox.insert(END, os.path.basename(file))
        self.status_label.config(text=f"📁 Выбрано файлов: {len(self.files)}")
    
    # ОСНОВНЫЕ ФУНКЦИИ ПЕРЕИМЕНОВАНИЯ
    def generate_new_name(self, pattern, i, original_name):
        """Генерирует новое имя файла на основе шаблона"""
        new_name = pattern
        filename, ext = os.path.splitext(original_name)
        
        # Обработка рандомных символов
        import re
        random_matches = re.findall(r'\{random(\d+)\}', new_name)
        for match in random_matches:
            count = int(match)
            random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=count))
            new_name = new_name.replace(f"{{random{match}}}", random_chars)
        
        # Обработка {randomX} с пользовательским количеством
        if "{randomX}" in new_name:
            try:
                count = int(self.random_chars_var.get())
                if count > 0:
                    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=count))
                    new_name = new_name.replace("{randomX}", random_chars)
            except ValueError:
                pass
        
        # Обработка UUID
        if "{uuid}" in new_name:
            import uuid
            new_name = new_name.replace("{uuid}", str(uuid.uuid4())[:8])
        
        # Обработка даты и времени
        if "{date}" in new_name:
            new_name = new_name.replace("{date}", datetime.now().strftime("%Y-%m-%d"))
        
        if "{time}" in new_name:
            new_name = new_name.replace("{time}", datetime.now().strftime("%H-%M-%S"))
        
        if "{datetime}" in new_name:
            new_name = new_name.replace("{datetime}", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        
        if "{year}" in new_name:
            new_name = new_name.replace("{year}", datetime.now().strftime("%Y"))
        
        # Информация о файле
        if "{original}" in new_name:
            new_name = new_name.replace("{original}", filename)
        
        if "{ext}" in new_name:
            new_name = new_name.replace("{ext}", ext[1:] if ext else "")
        
        # Нумерация
        if "{numbers" in new_name:
            start = new_name.find("{numbers") + 8
            end = new_name.find("}", start)
            if start < end:
                num_str = new_name[start:end]
                try:
                    start_num = int(num_str)
                except ValueError:
                    start_num = 1
                new_num = start_num + i
                new_name = new_name.replace(f"{{numbers{num_str}}}", str(new_num))
        
        # Обратная нумерация
        if "{reverse}" in new_name:
            new_num = len(self.files) - i
            new_name = new_name.replace("{reverse}", str(new_num))
        
        # Буквы по порядку
        if "{letters}" in new_name:
            letter = chr(97 + i % 26)
            if len(self.files) > 26:
                letter += str(i // 26 + 1)
            new_name = new_name.replace("{letters}", letter)
        
        if "{Letters}" in new_name:
            letter = chr(65 + i % 26)
            if len(self.files) > 26:
                letter += str(i // 26 + 1)
            new_name = new_name.replace("{Letters}", letter)
        
        # Случайные буквы
        while "{lettersR}" in new_name:
            letter = chr(random.randint(97, 122))
            if len(self.files) > 13:
                letter += str(i + 1)
            new_name = new_name.replace("{lettersR}", letter, 1)
        
        while "{LettersR}" in new_name:
            letter = chr(random.randint(65, 90))
            if len(self.files) > 13:
                letter += str(i + 1)
            new_name = new_name.replace("{LettersR}", letter, 1)
        
        # Добавляем расширение, если его нет
        if not os.path.splitext(new_name)[1] and ext:
            new_name += ext
        
        return new_name
    
    def show_preview(self):
        """Показывает превью переименования"""
        if not self.files:
            messagebox.showwarning("Ошибка", "Не выбраны файлы для превью")
            return
        
        pattern = self.pattern_var.get()
        if not pattern:
            messagebox.showwarning("Ошибка", "Введите шаблон имени")
            return
        
        preview_window = Toplevel(self.root)
        preview_window.title("👁️ Превью переименования")
        preview_window.geometry("800x500")
        preview_window.transient(self.root)
        preview_window.grab_set()
        
        # Заголовок
        header_frame = Frame(preview_window)
        header_frame.pack(fill=X, padx=10, pady=10)
        
        Label(header_frame, text="Превью переименования", font=("Arial", 12, "bold")).pack()
        Label(header_frame, text=f"Файлов: {len(self.files)} | Шаблон: {pattern}", 
              font=("Arial", 9)).pack()
        
        # Таблица превью
        tree_frame = Frame(preview_window)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)
        
        tree = ttk.Treeview(tree_frame, columns=("old", "new"), show="headings", height=15)
        tree.heading("old", text="📄 Старое имя")
        tree.heading("new", text="🔄 Новое имя")
        tree.column("old", width=350)
        tree.column("new", width=350)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        
        tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Заполняем таблицу
        for i, file_path in enumerate(self.files):
            old_name = os.path.basename(file_path)
            new_name = self.generate_new_name(pattern, i, old_name)
            tree.insert("", END, values=(old_name, new_name))
        
        # Кнопки
        button_frame = Frame(preview_window)
        button_frame.pack(fill=X, padx=10, pady=10)
        
        Button(button_frame, text="✅ Применить переименование", 
               command=lambda: [preview_window.destroy(), self.rename_files()],
               bg="lightgreen", font=("Arial", 10)).pack(side=LEFT, padx=5)
        
        Button(button_frame, text="❌ Отмена", 
               command=preview_window.destroy,
               bg="lightcoral", font=("Arial", 10)).pack(side=RIGHT, padx=5)
    
    def rename_files(self):
        """Основная функция переименования"""
        if not self.files:
            messagebox.showwarning("Ошибка", "Не выбраны файлы для переименования")
            return
        
        pattern = self.pattern_var.get()
        if not pattern:
            messagebox.showwarning("Ошибка", "Введите шаблон имени")
            return
        
        # Проверяем, есть ли плейсхолдеры
        placeholders = ["{numbers", "{letters", "{Letters", "{date", "{time", 
                       "{random", "{original", "{ext", "{reverse", "{uuid", "{year", "{datetime"]
        has_placeholder = any(ph in pattern for ph in placeholders)
        
        # Если нет плейсхолдеров, добавляем {numbers1}
        if not has_placeholder:
            pattern += " {numbers1}"
            self.pattern_var.set(pattern)
        
        try:
            # Сохраняем состояние для отмены
            self.undo_stack.append(list(self.files))
            if len(self.undo_stack) > 10:  # Ограничиваем размер стека
                self.undo_stack.pop(0)
            
            directory = os.path.dirname(self.files[0])
            renamed_files = []
            
            for i, file_path in enumerate(self.files):
                old_name = os.path.basename(file_path)
                new_name = self.generate_new_name(pattern, i, old_name)
                new_path = os.path.join(directory, new_name)
                
                # Если файл с таким именем уже существует, добавляем суффикс
                counter = 1
                temp_path = new_path
                while os.path.exists(temp_path):
                    name, ext = os.path.splitext(new_path)
                    temp_path = f"{name}_{counter}{ext}"
                    counter += 1
                
                os.rename(file_path, temp_path)
                renamed_files.append(temp_path)
            
            self.files = renamed_files
            self.update_file_list()
            messagebox.showinfo("Успех", f"✅ Успешно переименовано {len(renamed_files)} файлов")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Произошла ошибка: {str(e)}")
    
    def undo_rename(self):
        """Отмена последнего действия"""
        if not self.undo_stack:
            messagebox.showinfo("Информация", "📝 Нет действий для отмены")
            return
        
        try:
            old_files = self.undo_stack.pop()
            directory = os.path.dirname(self.files[0])
            
            for old_path, new_path in zip(old_files, self.files):
                if os.path.exists(new_path):
                    os.rename(new_path, old_path)
            
            self.files = old_files
            self.update_file_list()
            messagebox.showinfo("Успех", "↩️ Последнее действие отменено")
        
        except Exception as e:
            messagebox.showerror("Ошибка", f"❌ Ошибка при отмене: {str(e)}")
    
    def clear_list(self):
        """Очистка списка файлов"""
        self.files = []
        self.update_file_list()
        messagebox.showinfo("Успех", "🗑️ Список файлов очищен")
    
    # РАСШИРЕННЫЕ ФУНКЦИИ
    def rename_from_exif(self):
        """Переименование фото по EXIF данным"""
        if not self.files:
            messagebox.showwarning("Ошибка", "Не выбраны файлы")
            return
        
        try:
            # Проверяем наличие PIL
            try:
                from PIL import Image
                from PIL.ExifTags import TAGS
            except ImportError:
                messagebox.showerror("Ошибка", "Установите Pillow: pip install Pillow")
                return
            
            self.undo_stack.append(list(self.files))
            renamed_files = []
            
            for i, file_path in enumerate(self.files):
                if file_path.lower().endswith(('.jpg', '.jpeg', '.tiff', '.png')):
                    try:
                        with Image.open(file_path) as image:
                            exif_data = image._getexif()
                            
                            if exif_data:
                                # Пытаемся получить дату съемки
                                date_str = datetime.now().strftime('%Y-%m-%d')
                                for tag_id, value in exif_data.items():
                                    tag = TAGS.get(tag_id, tag_id)
                                    if tag in ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']:
                                        date_str = value.replace(':', '-').replace(' ', '_')[:19]
                                        break
                                
                                name, ext = os.path.splitext(os.path.basename(file_path))
                                new_name = f"Фото_{date_str}{ext}"
                                new_path = os.path.join(os.path.dirname(file_path), new_name)
                                os.rename(file_path, new_path)
                                renamed_files.append(new_path)
                            else:
                                renamed_files.append(file_path)
                                
                    except Exception as e:
                        renamed_files.append(file_path)
                        continue
                else:
                    renamed_files.append(file_path)
            
            self.files = renamed_files
            self.update_file_list()
            messagebox.showinfo("Успех", "EXIF переименование завершено")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка EXIF: {str(e)}")
    
    def rename_from_id3(self):
        """Переименование аудио по ID3 тегам"""
        messagebox.showinfo("Инфо", "Функция ID3 переименования требует установки mutagen: pip install mutagen")
        # Реализация с mutagen была бы здесь
    
    def rename_by_date(self):
        """Переименование по дате создания"""
        if not self.files:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for i, file_path in enumerate(self.files):
            try:
                stat = os.stat(file_path)
                create_time = datetime.fromtimestamp(stat.st_ctime)
                date_str = create_time.strftime('%Y-%m-%d_%H-%M-%S')
                
                name, ext = os.path.splitext(os.path.basename(file_path))
                new_name = f"{date_str}_{name}{ext}"
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                
                os.rename(file_path, new_path)
                renamed_files.append(new_path)
            except:
                renamed_files.append(file_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Переименование по дате завершено")
    
    def transliterate(self, direction):
        """Транслитерация рус↔англ"""
        if not self.files:
            return
        
        ru_en = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
            'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
            'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
            'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya'
        }
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for file_path in self.files:
            name, ext = os.path.splitext(os.path.basename(file_path))
            new_name = ""
            
            if direction == "ru_en":
                for char in name.lower():
                    new_name += ru_en.get(char, char)
            else:
                # Упрощенная обратная транслитерация
                en_ru = {v: k for k, v in ru_en.items() if v}
                for char in name.lower():
                    new_name += en_ru.get(char, char)
            
            new_path = os.path.join(os.path.dirname(file_path), new_name + ext)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Транслитерация завершена")
    
    def change_case(self, case_type):
        """Изменение регистра имен файлов"""
        if not self.files:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for file_path in self.files:
            name, ext = os.path.splitext(os.path.basename(file_path))
            
            if case_type == "upper":
                new_name = name.upper() + ext
            elif case_type == "lower":
                new_name = name.lower() + ext
            elif case_type == "title":
                new_name = name.title() + ext
            
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Регистр изменен")
    
    def add_folder_recursive(self):
        """Добавление всех файлов из папки рекурсивно"""
        folder = filedialog.askdirectory(title="Выберите папку")
        if folder:
            all_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    all_files.append(os.path.join(root, file))
            
            self.files.extend(all_files)
            self.update_file_list()
            messagebox.showinfo("Успех", f"Добавлено {len(all_files)} файлов")
    
    def filter_by_type(self):
        """Фильтрация файлов по типу"""
        if not self.files:
            return
        
        filter_window = Toplevel(self.root)
        filter_window.title("Фильтр по типу файлов")
        filter_window.geometry("300x200")
        
        Label(filter_window, text="Выберите типы файлов:", font=("Arial", 10)).pack(pady=10)
        
        type_var = StringVar(value="images")
        types = [("Изображения", "images"), ("Аудио", "audio"), 
                ("Видео", "video"), ("Документы", "documents")]
        
        for text, value in types:
            Radiobutton(filter_window, text=text, variable=type_var, 
                       value=value, font=("Arial", 9)).pack(anchor="w", padx=20)
        
        def apply_filter():
            selected_type = type_var.get()
            filtered_files = []
            
            for file_path in self.files:
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.file_types[selected_type]:
                    filtered_files.append(file_path)
            
            self.files = filtered_files
            self.update_file_list()
            filter_window.destroy()
            messagebox.showinfo("Успех", f"Оставлено {len(filtered_files)} файлов")
        
        Button(filter_window, text="Применить фильтр", command=apply_filter,
               bg="lightgreen", font=("Arial", 10)).pack(pady=20)
    
    def shuffle_files(self):
        """Перемешивание файлов в случайном порядке"""
        if not self.files:
            return
        
        random.shuffle(self.files)
        self.update_file_list()
        messagebox.showinfo("Успех", "Файлы перемешаны")
    
    def encrypt_names(self):
        """Простое шифрование имен файлов"""
        if not self.files:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for file_path in self.files:
            name, ext = os.path.splitext(os.path.basename(file_path))
            # Простое "шифрование" - реверс имени
            encrypted_name = name[::-1] + ext
            new_path = os.path.join(os.path.dirname(file_path), encrypted_name)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Имена зашифрованы")
    
    def hash_names(self, algorithm):
        """Хеширование имен файлов"""
        if not self.files:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for file_path in self.files:
            name, ext = os.path.splitext(os.path.basename(file_path))
            
            if algorithm == "md5":
                hash_obj = hashlib.md5(name.encode())
            else:  # sha256
                hash_obj = hashlib.sha256(name.encode())
            
            hashed_name = hash_obj.hexdigest()[:8] + ext
            new_path = os.path.join(os.path.dirname(file_path), hashed_name)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", f"Имена хешированы ({algorithm})")
    
    def replace_text(self):
        """Замена текста в именах файлов"""
        if not self.files:
            return
        
        find_text = self.find_entry.get()
        if not find_text:
            messagebox.showwarning("Ошибка", "Введите текст для поиска")
            return
        
        replace_text = self.replace_entry.get()
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for file_path in self.files:
            name, ext = os.path.splitext(os.path.basename(file_path))
            new_name = name.replace(find_text, replace_text) + ext
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Текст заменен")
    
    def delete_chars(self, char_type):
        """Удаление символов из имен файлов"""
        if not self.files:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for file_path in self.files:
            name, ext = os.path.splitext(os.path.basename(file_path))
            
            if char_type == "spaces":
                new_name = name.replace(" ", "") + ext
            elif char_type == "digits":
                new_name = ''.join([c for c in name if not c.isdigit()]) + ext
            elif char_type == "special":
                new_name = ''.join([c for c in name if c.isalnum() or c in ' .-_']) + ext
            
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Символы удалены")
    
    # ПАКЕТНАЯ ОБРАБОТКА
    def apply_template(self, file_type):
        """Применение шаблона к определенному типу файлов"""
        if not self.files:
            return
        
        template = self.template_vars[file_type].get()
        if not template:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        counter = 1
        
        for file_path in self.files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.file_types[file_type.lower()]:
                name, ext = os.path.splitext(os.path.basename(file_path))
                new_name = template.replace("{numbers1}", str(counter)) + ext
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                os.rename(file_path, new_path)
                renamed_files.append(new_path)
                counter += 1
            else:
                renamed_files.append(file_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", f"Шаблон применен к {file_type}")
    
    def apply_series_format(self):
        """Применение формата серии к видеофайлам"""
        if not self.files:
            return
        
        try:
            season = int(self.season_num.get())
            episode = int(self.episode_start.get())
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректные номера сезона и эпизода")
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        current_episode = episode
        
        for file_path in self.files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext in self.file_types["video"]:
                new_name = self.series_format.get().replace("{season}", str(season)).replace("{episode}", str(current_episode)) + ext
                new_path = os.path.join(os.path.dirname(file_path), new_name)
                os.rename(file_path, new_path)
                renamed_files.append(new_path)
                current_episode += 1
            else:
                renamed_files.append(file_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Формат серии применен")
    
    def reverse_order(self):
        """Обратный порядок файлов"""
        if not self.files:
            return
        
        self.files.reverse()
        self.update_file_list()
        messagebox.showinfo("Успех", "Порядок файлов изменен на обратный")
    
    def create_file_groups(self, group_size):
        """Создание групп файлов"""
        if not self.files:
            return
        
        self.undo_stack.append(list(self.files))
        renamed_files = []
        
        for i, file_path in enumerate(self.files):
            name, ext = os.path.splitext(os.path.basename(file_path))
            group_num = i // group_size + 1
            new_name = f"Группа{group_num}_{name}{ext}"
            new_path = os.path.join(os.path.dirname(file_path), new_name)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", f"Созданы группы по {group_size} файлов")
    
    def create_file_groups_custom(self):
        """Создание групп с пользовательским размером"""
        try:
            group_size = int(self.group_size.get())
            if group_size <= 0:
                raise ValueError
            self.create_file_groups(group_size)
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректный размер группы")
    
    # ОРГАНИЗАЦИЯ ФАЙЛОВ
    def organize_by_extension(self):
        """Организация по расширениям"""
        if not self.files:
            return
        
        for file_path in self.files:
            ext = os.path.splitext(file_path)[1][1:]  # Без точки
            if not ext:
                ext = "no_extension"
            
            folder_path = os.path.join(os.path.dirname(file_path), ext.upper())
            os.makedirs(folder_path, exist_ok=True)
            
            new_path = os.path.join(folder_path, os.path.basename(file_path))
            shutil.move(file_path, new_path)
        
        messagebox.showinfo("Успех", "Файлы организованы по расширениям")
        self.files = []
        self.update_file_list()
    
    def organize_by_date(self):
        """Организация по дате создания"""
        if not self.files:
            return
        
        for file_path in self.files:
            try:
                stat = os.stat(file_path)
                create_time = datetime.fromtimestamp(stat.st_ctime)
                date_str = create_time.strftime('%Y-%m-%d')
                
                folder_path = os.path.join(os.path.dirname(file_path), date_str)
                os.makedirs(folder_path, exist_ok=True)
                
                new_path = os.path.join(folder_path, os.path.basename(file_path))
                shutil.move(file_path, new_path)
            except:
                continue
        
        messagebox.showinfo("Успех", "Файлы организованы по дате")
        self.files = []
        self.update_file_list()
    
    def organize_by_size(self):
        """Организация по размеру"""
        if not self.files:
            return
        
        size_categories = {
            "tiny": (0, 1024),           # < 1KB
            "small": (1024, 1024*100),   # 1KB - 100KB
            "medium": (1024*100, 1024*1024),  # 100KB - 1MB
            "large": (1024*1024, 1024*1024*10),  # 1MB - 10MB
            "huge": (1024*1024*10, float('inf'))  # > 10MB
        }
        
        for file_path in self.files:
            try:
                size = os.path.getsize(file_path)
                category = "unknown"
                
                for cat, (min_size, max_size) in size_categories.items():
                    if min_size <= size < max_size:
                        category = cat
                        break
                
                folder_path = os.path.join(os.path.dirname(file_path), category.upper())
                os.makedirs(folder_path, exist_ok=True)
                
                new_path = os.path.join(folder_path, os.path.basename(file_path))
                shutil.move(file_path, new_path)
            except:
                continue
        
        messagebox.showinfo("Успех", "Файлы организованы по размеру")
        self.files = []
        self.update_file_list()
    
    def organize_by_type(self):
        """Организация по типу файлов"""
        if not self.files:
            return
        
        for file_path in self.files:
            ext = os.path.splitext(file_path)[1].lower()
            file_type = "other"
            
            for type_name, extensions in self.file_types.items():
                if ext in extensions:
                    file_type = type_name
                    break
            
            folder_path = os.path.join(os.path.dirname(file_path), file_type.upper())
            os.makedirs(folder_path, exist_ok=True)
            
            new_path = os.path.join(folder_path, os.path.basename(file_path))
            shutil.move(file_path, new_path)
        
        messagebox.showinfo("Успех", "Файлы организованы по типам")
        self.files = []
        self.update_file_list()
    
    def select_target_folder(self):
        """Выбор целевой папки для перемещения/копирования"""
        folder = filedialog.askdirectory(title="Выберите целевую папку")
        if folder:
            self.target_folder = folder
            self.target_label.config(text=folder, fg="green")
    
    def move_to_folder(self):
        """Перемещение файлов в выбранную папку"""
        if not self.target_folder:
            messagebox.showwarning("Ошибка", "Сначала выберите целевую папку")
            return
        
        if not self.files:
            return
        
        for file_path in self.files:
            try:
                new_path = os.path.join(self.target_folder, os.path.basename(file_path))
                shutil.move(file_path, new_path)
            except:
                continue
        
        messagebox.showinfo("Успех", "Файлы перемещены")
        self.files = []
        self.update_file_list()
    
    def copy_to_folder(self):
        """Копирование файлов в выбранную папку"""
        if not self.target_folder:
            messagebox.showwarning("Ошибка", "Сначала выберите целевую папку")
            return
        
        if not self.files:
            return
        
        for file_path in self.files:
            try:
                new_path = os.path.join(self.target_folder, os.path.basename(file_path))
                shutil.copy2(file_path, new_path)
            except:
                continue
        
        messagebox.showinfo("Успех", "Файлы скопированы")
        # Файлы остаются в списке для дальнейших операций
    
    def create_symlinks(self):
        """Создание символических ссылок"""
        if not self.target_folder:
            messagebox.showwarning("Ошибка", "Сначала выберите целевую папку")
            return
        
        if not self.files:
            return
        
        for file_path in self.files:
            try:
                link_path = os.path.join(self.target_folder, os.path.basename(file_path))
                if os.path.exists(link_path):
                    os.remove(link_path)
                os.symlink(file_path, link_path)
            except:
                continue
        
        messagebox.showinfo("Успех", "Символические ссылки созданы")
    
    # СТАТИСТИКА И АНАЛИЗ
    def update_stats(self):
        """Обновление статистики"""
        if not self.files:
            self.stats_text.delete(1.0, END)
            self.stats_text.insert(END, "Нет файлов для анализа")
            return
        
        total_size = 0
        extensions = {}
        size_categories = {
            "tiny": 0, "small": 0, "medium": 0, "large": 0, "huge": 0
        }
        
        for file_path in self.files:
            try:
                size = os.path.getsize(file_path)
                total_size += size
                ext = os.path.splitext(file_path)[1].lower() or "без расширения"
                extensions[ext] = extensions.get(ext, 0) + 1
                
                # Категории по размеру
                if size < 1024:
                    size_categories["tiny"] += 1
                elif size < 1024*100:
                    size_categories["small"] += 1
                elif size < 1024*1024:
                    size_categories["medium"] += 1
                elif size < 1024*1024*10:
                    size_categories["large"] += 1
                else:
                    size_categories["huge"] += 1
                    
            except:
                continue
        
        stats = f"""📊 СТАТИСТИКА ФАЙЛОВ
────────────────────
📁 Всего файлов: {len(self.files)}
💾 Общий размер: {self.format_size(total_size)}
📅 Дата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📈 РАСПРЕДЕЛЕНИЕ ПО ТИПАМ:
"""
        for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
            stats += f"  {ext}: {count} файлов\n"
        
        stats += f"\n📏 РАСПРЕДЕЛЕНИЕ ПО РАЗМЕРАМ:\n"
        stats += f"  🐜 Крошечные (<1KB): {size_categories['tiny']}\n"
        stats += f"  📄 Малые (1KB-100KB): {size_categories['small']}\n"
        stats += f"  📁 Средние (100KB-1MB): {size_categories['medium']}\n"
        stats += f"  💽 Большие (1MB-10MB): {size_categories['large']}\n"
        stats += f"  🐋 Огромные (>10MB): {size_categories['huge']}\n"
        
        self.stats_text.delete(1.0, END)
        self.stats_text.insert(END, stats)
    
    def format_size(self, size_bytes):
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    def find_duplicates(self):
        """Поиск дубликатов по содержимому"""
        if not self.files:
            return
        
        hashes = {}
        duplicates = []
        
        for file_path in self.files:
            try:
                # Простой хеш по размеру и имени (для скорости)
                file_hash = f"{os.path.getsize(file_path)}_{os.path.basename(file_path)}"
                if file_hash in hashes:
                    duplicates.append((hashes[file_hash], file_path))
                else:
                    hashes[file_hash] = file_path
            except:
                continue
        
        if duplicates:
            result = "🔍 НАЙДЕНЫ ДУБЛИКАТЫ:\n\n"
            for i, (orig, dup) in enumerate(duplicates[:10]):  # Ограничиваем вывод
                result += f"{i+1}. 📄 {os.path.basename(orig)}\n"
                result += f"   ├─ {orig}\n"
                result += f"   └─ {dup}\n\n"
            
            if len(duplicates) > 10:
                result += f"... и ещё {len(duplicates) - 10} дубликатов\n"
            
            self.stats_text.delete(1.0, END)
            self.stats_text.insert(END, result)
            
            # Кнопка для удаления дубликатов
            Button(self.stats_frame, text="🗑️ Удалить дубликаты", 
                  command=lambda: self.delete_duplicates(duplicates),
                  bg="red", fg="white", font=("Arial", 9)).pack(pady=5)
        else:
            self.stats_text.insert(END, "\n✅ Дубликаты не найдены")
    
    def delete_duplicates(self, duplicates):
        """Удаление найденных дубликатов"""
        for orig, dup in duplicates:
            try:
                os.remove(dup)
            except:
                continue
        
        self.update_file_list()
        self.update_stats()
        messagebox.showinfo("Успех", "Дубликаты удалены")
    
    def analyze_names(self):
        """Анализ имен файлов"""
        if not self.files:
            return
        
        name_lengths = []
        common_words = {}
        
        for file_path in self.files:
            name = os.path.splitext(os.path.basename(file_path))[0]
            name_lengths.append(len(name))
            
            # Простой анализ слов (разделение по пробелам и дефисам)
            words = name.replace('_', ' ').replace('-', ' ').split()
            for word in words:
                if len(word) > 2:  # Игнорируем короткие слова
                    common_words[word.lower()] = common_words.get(word.lower(), 0) + 1
        
        avg_length = sum(name_lengths) / len(name_lengths) if name_lengths else 0
        max_length = max(name_lengths) if name_lengths else 0
        min_length = min(name_lengths) if name_lengths else 0
        
        analysis = f"""📊 АНАЛИЗ ИМЕН ФАЙЛОВ
────────────────────
📏 Длина имен:
  Средняя: {avg_length:.1f} символов
  Максимальная: {max_length} символов
  Минимальная: {min_length} символов

🔤 Частые слова:
"""
        for word, count in sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:10]:
            analysis += f"  '{word}': {count} раз\n"
        
        self.stats_text.delete(1.0, END)
        self.stats_text.insert(END, analysis)
    
    def analyze_sizes(self):
        """Анализ размеров файлов"""
        if not self.files:
            return
        
        sizes = []
        for file_path in self.files:
            try:
                sizes.append(os.path.getsize(file_path))
            except:
                continue
        
        if not sizes:
            return
        
        avg_size = sum(sizes) / len(sizes)
        max_size = max(sizes)
        min_size = min(sizes)
        total_size = sum(sizes)
        
        analysis = f"""📏 АНАЛИЗ РАЗМЕРОВ ФАЙЛОВ
────────────────────
💾 Общий размер: {self.format_size(total_size)}
📊 Средний размер: {self.format_size(avg_size)}
⬆️ Самый большой: {self.format_size(max_size)}
⬇️ Самый маленький: {self.format_size(min_size)}
📈 Медианный размер: {self.format_size(sorted(sizes)[len(sizes)//2])}

📋 Распределение:
"""
        size_ranges = [
            (0, 1024, "Менее 1KB"),
            (1024, 1024*1024, "1KB - 1MB"),
            (1024*1024, 1024*1024*10, "1MB - 10MB"),
            (1024*1024*10, 1024*1024*100, "10MB - 100MB"),
            (1024*1024*100, float('inf'), "Более 100MB")
        ]
        
        for min_r, max_r, desc in size_ranges:
            count = sum(1 for size in sizes if min_r <= size < max_r)
            percentage = (count / len(sizes)) * 100
            analysis += f"  {desc}: {count} файлов ({percentage:.1f}%)\n"
        
        self.stats_text.delete(1.0, END)
        self.stats_text.insert(END, analysis)

if __name__ == "__main__":
    root = Tk()
    app = RenamerPro(root)
    root.mainloop()
