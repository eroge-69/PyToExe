import os
import random
import string
import shutil
import math
import hashlib
from tkinter import *
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import subprocess
import json
from PIL import Image, ExifTags
import mutagen
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import cv2
import numpy as np

class RenamerProUltimate:
    def __init__(self, root):
        self.root = root
        self.root.title("Renamer Delux")
        self.root.minsize(900, 800)
        
        # Переменные
        self.files = []
        self.pattern_var = StringVar(value="Файл {numbers1}")
        self.preview_var = BooleanVar(value=True)
        self.random_chars_var = StringVar(value="5")
        self.undo_stack = []
        self.target_folder = ""
        self.current_desc_page = 0
        
        self.file_types = {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
            "audio": [".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac"],
            "video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm"],
            "documents": [".pdf", ".doc", ".docx", ".txt", ".xlsx", ".pptx"]
        }
        
        # Цвета для доминирующих цветов
        self.color_names = {
            'red': 'красный', 'green': 'зеленый', 'blue': 'синий', 
            'yellow': 'желтый', 'purple': 'фиолетовый', 'orange': 'оранжевый',
            'pink': 'розовый', 'brown': 'коричневый', 'gray': 'серый',
            'black': 'черный', 'white': 'белый'
        }
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Основные вкладки
        self.main_frame = ttk.Frame(self.notebook)
        self.advanced_frame = ttk.Frame(self.notebook)
        self.media_frame = ttk.Frame(self.notebook)
        self.internet_frame = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_frame, text="🎯 Основное")
        self.notebook.add(self.advanced_frame, text="⚡ Дополнительно")
        self.notebook.add(self.media_frame, text="📷 Медиа")
        self.notebook.add(self.internet_frame, text="🌐 Интернет")
        
        self.setup_main_tab()
        self.setup_advanced_tab()
        self.setup_media_tab()
        self.setup_internet_tab()
    
    def setup_main_tab(self):
        # Основной фрейм с двумя колонками
        main_container = PanedWindow(self.main_frame, orient=HORIZONTAL)
        main_container.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Левая панель - управление
        left_frame = Frame(main_container)
        main_container.add(left_frame)
        
        # Правая панель - список файлов
        right_frame = Frame(main_container)
        main_container.add(right_frame)
        
        # Левая панель - элементы управления
        Label(left_frame, text="Шаблон имени:", font=("Arial", 10, "bold")).pack(pady=(10, 0))
        
        input_frame = Frame(left_frame)
        input_frame.pack(fill=X, padx=5, pady=(0, 10))
        
        self.pattern_entry = Entry(input_frame, textvariable=self.pattern_var, width=40, font=("Arial", 10))
        self.pattern_entry.pack(side=LEFT, fill=X, expand=True)
        
        Button(input_frame, text="📋", command=self.show_placeholder_menu, 
               width=3, relief="raised", bg="lightblue", font=("Arial", 12)).pack(side=RIGHT, padx=(5, 0))
        
        # Основные кнопки плейсхолдеров
        self.setup_main_placeholder_buttons(left_frame)
        
        # Описание плейсхолдеров с навигацией
        self.setup_placeholder_descriptions(left_frame)
        
        # Опции и кнопки
        self.setup_control_buttons(left_frame)
        
        # Правая панель - список файлов
        self.setup_file_list(right_frame)
    
    def setup_main_placeholder_buttons(self, parent):
        """Основные кнопки плейсхолдеров"""
        main_placeholders_frame = LabelFrame(parent, text="🚀 Основные плейсхолдеры")
        main_placeholders_frame.pack(fill=X, padx=5, pady=5)
        
        # Первый ряд - нумерация
        row1 = Frame(main_placeholders_frame)
        row1.pack(fill=X, pady=2)
        
        num_placeholders = [
            ("{numbers1}", "1, 2, 3...", "#E3F2FD"),
            ("{numbers01}", "01, 02...", "#E3F2FD"),
            ("{numbers001}", "001, 002...", "#E3F2FD"),
            ("{reverse}", "Обратная нумерация", "#E3F2FD"),
            ("{reverseX}", "reverseX", "#E3F2FD")
        ]
        
        for ph, desc, color in num_placeholders:
            btn = Button(row1, text=ph, width=12, 
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg=color, font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
        
        # Второй ряд - буквы
        row2 = Frame(main_placeholders_frame)
        row2.pack(fill=X, pady=2)
        
        letter_placeholders = [
            ("{letters}", "a, b, c...", "#FFF9C4"),
            ("{Letters}", "A, B, C...", "#FFF9C4"),
            ("{lettersR}", "Случайные буквы", "#FFF9C4"),
            ("{LettersR}", "Случайные заглавные", "#FFF9C4"),
            ("{cyrillic}", "а, б, в...", "#FFF9C4")
        ]
        
        for ph, desc, color in letter_placeholders:
            btn = Button(row2, text=ph, width=12,
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg=color, font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
        
        # Третий ряд - дата и время
        row3 = Frame(main_placeholders_frame)
        row3.pack(fill=X, pady=2)
        
        date_placeholders = [
            ("{date}", "2023-10-01", "#C8E6C9"),
            ("{time}", "14-30-45", "#C8E6C9"),
            ("{datetime}", "2023-10-01_14-30", "#C8E6C9"),
            ("{year}", "2023", "#C8E6C9"),
            ("{timestamp}", "Unix время", "#C8E6C9")
        ]
        
        for ph, desc, color in date_placeholders:
            btn = Button(row3, text=ph, width=12,
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg=color, font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
    
    def setup_placeholder_descriptions(self, parent):
        """Описание плейсхолдеров с навигацией"""
        desc_frame = LabelFrame(parent, text="📖 Описание плейсхолдеров")
        desc_frame.pack(fill=X, padx=5, pady=5)
        
        # Навигация
        nav_frame = Frame(desc_frame)
        nav_frame.pack(fill=X, padx=5, pady=2)
        
        Button(nav_frame, text="◀", command=self.prev_desc_page,
               width=3, font=("Arial", 8)).pack(side=LEFT)
        
        self.desc_label = Label(nav_frame, text="Страница 1/4", font=("Arial", 8))
        self.desc_label.pack(side=LEFT, padx=10)
        
        Button(nav_frame, text="▶", command=self.next_desc_page,
               width=3, font=("Arial", 8)).pack(side=LEFT)
        
        # Текст описания
        self.desc_text = Text(desc_frame, height=6, wrap=WORD, font=("Arial", 8))
        desc_scrollbar = Scrollbar(desc_frame, command=self.desc_text.yview)
        self.desc_text.config(yscrollcommand=desc_scrollbar.set)
        
        self.desc_text.pack(side=LEFT, fill=BOTH, expand=True, padx=(5, 0))
        desc_scrollbar.pack(side=RIGHT, fill=Y, padx=(0, 5))
        
        self.update_descriptions()
    
    def setup_control_buttons(self, parent):
        """Кнопки управления"""
        # Опции
        options_frame = Frame(parent)
        options_frame.pack(fill=X, pady=5)
        
        Checkbutton(options_frame, text="🔍 Показывать превью перед переименованием", 
                   variable=self.preview_var, font=("Arial", 9)).pack(side=LEFT, padx=5)
        
        Button(options_frame, text="↩️ Отменить действие", 
              command=self.undo_rename, bg="lightyellow", font=("Arial", 9)).pack(side=RIGHT, padx=5)
        
        # Основные кнопки действий
        button_frame = Frame(parent)
        button_frame.pack(fill=X, pady=10)
        
        Button(button_frame, text="📁 Выбрать файлы", command=self.select_files, 
               bg="lightblue", width=15, font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(button_frame, text="👁️ Показать превью", command=self.show_preview,
               bg="lightyellow", width=15, font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(button_frame, text="✅ Переименовать", command=self.rename_files,
               bg="lightgreen", width=15, font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(button_frame, text="🗑️ Очистить список", command=self.clear_list,
               bg="lightcoral", width=15, font=("Arial", 9)).pack(side=LEFT, padx=2)
    
    def setup_file_list(self, parent):
        """Список файлов с детальной информацией"""
        list_frame = LabelFrame(parent, text="📄 Выбранные файлы")
        list_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        # Создаем Treeview для отображения файлов с информацией
        columns = ("name", "size", "type", "modified")
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        # Настраиваем колонки
        self.file_tree.heading("name", text="Имя файла")
        self.file_tree.heading("size", text="Размер")
        self.file_tree.heading("type", text="Тип")
        self.file_tree.heading("modified", text="Изменен")
        
        self.file_tree.column("name", width=250)
        self.file_tree.column("size", width=80)
        self.file_tree.column("type", width=80)
        self.file_tree.column("modified", width=120)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        self.file_tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.pack(side=RIGHT, fill=Y)
        
        # Контекстное меню
        self.tree_menu = Menu(self.root, tearoff=0)
        self.tree_menu.add_command(label="Удалить из списка", command=self.remove_selected_file)
        self.tree_menu.add_command(label="Показать информацию", command=self.show_file_info)
        self.file_tree.bind("<Button-3>", self.show_tree_menu)
        
        # Статус
        self.status_label = Label(parent, text="Выберите файлы для переименования", 
                                 relief=SUNKEN, anchor=W, font=("Arial", 9))
        self.status_label.pack(fill=X, side=BOTTOM, pady=(5, 0))
    
    def setup_advanced_tab(self):
        """Дополнительные функции и плейсхолдеры"""
        # Панель быстрого доступа к плейсхолдерам
        quick_access_frame = LabelFrame(self.advanced_frame, text="⚡ Быстрый доступ к плейсхолдерам")
        quick_access_frame.pack(fill=X, padx=5, pady=5)
        
        # Разделяем на категории
        categories = [
            {
                "name": "📊 Информация о файле",
                "placeholders": [
                    ("{size}", "Размер (байты)", "#E1BEE7"),
                    ("{size_kb}", "Размер (KB)", "#E1BEE7"),
                    ("{size_mb}", "Размер (MB)", "#E1BEE7"),
                    ("{created}", "Дата создания", "#E1BEE7"),
                    ("{modified}", "Дата изменения", "#E1BEE7"),
                    ("{accessed}", "Дата доступа", "#E1BEE7")
                ]
            },
            {
                "name": "🔤 Текст и преобразования",
                "placeholders": [
                    ("{camelCase}", "camelCase", "#FFE0B2"),
                    ("{PascalCase}", "PascalCase", "#FFE0B2"),
                    ("{snake_case}", "snake_case", "#FFE0B2"),
                    ("{kebab-case}", "kebab-case", "#FFE0B2"),
                    ("{slug}", "URL-слаг", "#FFE0B2"),
                    ("{reverse}", "Реверс имени", "#FFE0B2"),
                    ("{shuffle}", "Перемешать буквы", "#FFE0B2")
                ]
            },
            {
                "name": "🎲 Случайные значения",
                "placeholders": [
                    ("{random3}", "3 символа", "#FFCDD2"),
                    ("{random5}", "5 символов", "#FFCDD2"),
                    ("{random8}", "8 символов", "#FFCDD2"),
                    ("{randomX}", "X символов", "#FFCDD2"),
                    ("{uuid}", "UUID", "#FFCDD2")
                ]
            }
        ]
        
        for category in categories:
            cat_frame = LabelFrame(quick_access_frame, text=category["name"])
            cat_frame.pack(fill=X, padx=5, pady=2)
            
            frame = Frame(cat_frame)
            frame.pack(fill=X, padx=5, pady=2)
            
            for ph, desc, color in category["placeholders"]:
                btn = Button(frame, text=ph, width=14,
                           command=lambda p=ph: self.insert_placeholder(p),
                           relief="raised", bg=color, font=("Arial", 8))
                btn.pack(side=LEFT, padx=1, pady=1)
                self.create_tooltip(btn, desc)
        
        # Дополнительные функции
        functions_frame = LabelFrame(self.advanced_frame, text="🛠️ Дополнительные функции")
        functions_frame.pack(fill=X, padx=5, pady=5)
        
        Button(functions_frame, text="Транслитерация Рус→Англ", command=lambda: self.transliterate("ru_en"),
               width=20, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(functions_frame, text="Изменить регистр", command=self.change_case_dialog,
               width=15, bg="#FFF9C4", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(functions_frame, text="Добавить папку рекурсивно", command=self.add_folder_recursive,
               width=20, bg="#C8E6C9", font=("Arial", 9)).pack(side=LEFT, padx=2)
    
    def setup_media_tab(self):
        """Медиа-функции для изображений, аудио и видео"""
        # Изображения
        image_frame = LabelFrame(self.media_frame, text="🖼️ Для изображений")
        image_frame.pack(fill=X, padx=5, pady=5)
        
        image_placeholders = [
            ("{dominant_color}", "Доминирующий цвет"),
            ("{camera_model}", "Модель камеры"),
            ("{focal_length}", "Фокусное расстояние"),
            ("{iso}", "ISO"),
            ("{shutter_speed}", "Выдержка"),
            ("{aperture}", "Диафрагма"),
            ("{dimensions}", "Размеры изображения"),
            ("{contains_people}", "Содержит людей"),
            ("{contains_landscape}", "Содержит пейзаж")
        ]
        
        image_buttons_frame = Frame(image_frame)
        image_buttons_frame.pack(fill=X, padx=5, pady=2)
        
        for i, (ph, desc) in enumerate(image_placeholders):
            btn = Button(image_buttons_frame, text=ph, width=16,
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg="#E3F2FD", font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
        
        # Аудио
        audio_frame = LabelFrame(self.media_frame, text="🎵 Для аудио")
        audio_frame.pack(fill=X, padx=5, pady=5)
        
        audio_placeholders = [
            ("{artist}", "Исполнитель"),
            ("{title}", "Название трека"),
            ("{album}", "Альбом"),
            ("{track_number}", "Номер трека"),
            ("{genre}", "Жанр"),
            ("{year}", "Год"),
            ("{duration}", "Длительность"),
            ("{bitrate}", "Битрейт"),
            ("{bpm}", "BPM"),
            ("{key}", "Тональность")
        ]
        
        audio_buttons_frame = Frame(audio_frame)
        audio_buttons_frame.pack(fill=X, padx=5, pady=2)
        
        for i, (ph, desc) in enumerate(audio_placeholders):
            btn = Button(audio_buttons_frame, text=ph, width=12,
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg="#FFF9C4", font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
        
        # Видео
        video_frame = LabelFrame(self.media_frame, text="🎥 Для видео")
        video_frame.pack(fill=X, padx=5, pady=5)
        
        video_placeholders = [
            ("{codec}", "Кодек"),
            ("{resolution}", "Разрешение"),
            ("{duration}", "Длительность"),
            ("{frame_rate}", "Частота кадров"),
            ("{bitrate}", "Битрейт"),
            ("{fps}", "FPS")
        ]
        
        video_buttons_frame = Frame(video_frame)
        video_buttons_frame.pack(fill=X, padx=5, pady=2)
        
        for i, (ph, desc) in enumerate(video_placeholders):
            btn = Button(video_buttons_frame, text=ph, width=12,
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg="#C8E6C9", font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
    
    def setup_internet_tab(self):
        """Интернет-функции и умная организация"""
        # Умная организация
        smart_frame = LabelFrame(self.internet_frame, text="🧠 Умная организация")
        smart_frame.pack(fill=X, padx=5, pady=5)
        
        smart_placeholders = [
            ("{file_category}", "Категория файла"),
            ("{content_type}", "Тип контента"),
            ("{quality}", "Качество"),
            ("{file_type}", "Тип файла")
        ]
        
        smart_buttons_frame = Frame(smart_frame)
        smart_buttons_frame.pack(fill=X, padx=5, pady=2)
        
        for ph, desc in smart_placeholders:
            btn = Button(smart_buttons_frame, text=ph, width=15,
                       command=lambda p=ph: self.insert_placeholder(p),
                       relief="raised", bg="#E1BEE7", font=("Arial", 8))
            btn.pack(side=LEFT, padx=1, pady=1)
            self.create_tooltip(btn, desc)
        
        # Интернет-функции
        internet_frame = LabelFrame(self.internet_frame, text="🌐 Интернет-функции")
        internet_frame.pack(fill=X, padx=5, pady=5)
        
        internet_buttons_frame = Frame(internet_frame)
        internet_buttons_frame.pack(fill=X, padx=5, pady=2)
        
        Button(internet_buttons_frame, text="Получить погоду", command=self.get_weather,
               width=15, bg="#FFE0B2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(internet_buttons_frame, text="Определить местоположение", command=self.get_location,
               width=20, bg="#FFE0B2", font=("Arial", 9)).pack(side=LEFT, padx=2)
        Button(internet_buttons_frame, text="Перевести имена", command=self.translate_names,
               width=15, bg="#FFE0B2", font=("Arial", 9)).pack(side=LEFT, padx=2)
    
    # ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ
    def create_tooltip(self, widget, text):
        """Создает всплывающую подсказку"""
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
    
    def prev_desc_page(self):
        """Предыдущая страница описаний"""
        if self.current_desc_page > 0:
            self.current_desc_page -= 1
            self.update_descriptions()
    
    def next_desc_page(self):
        """Следующая страница описаний"""
        if self.current_desc_page < 3:  # 4 страницы (0-3)
            self.current_desc_page += 1
            self.update_descriptions()
    
    def update_descriptions(self):
        """Обновляет описание плейсхолдеров"""
        descriptions = [
            """🔢 НУМЕРАЦИЯ:
{numbers1} - 1, 2, 3...
{numbers01} - 01, 02, 03...
{numbers001} - 001, 002, 003...
{reverse} - Обратная нумерация
{reverseX} - Обратная от X (reverse-3 → -3, -4...)
{hex} - Шестнадцатеричная
{roman} - Римские цифры""",
            
            """📅 ДАТА И ВРЕМЯ:
{date} - 2023-10-01
{time} - 14-30-45
{datetime} - 2023-10-01_14-30
{year} - 2023
{timestamp} - Unix время
{weekday} - Понедельник
{month_name} - Январь""",
            
            """🔤 ТЕКСТ И ПРЕОБРАЗОВАНИЯ:
{letters} - a, b, c...
{Letters} - A, B, C...
{camelCase} - fileName
{PascalCase} - FileName
{snake_case} - file_name
{kebab-case} - file-name
{reverse} - emanelif (реверс)
{shuffle} - ifleeman (перемешать)""",
            
            """📊 ИНФОРМАЦИЯ О ФАЙЛЕ:
{size} - Размер в байтах
{size_kb} - Размер в KB
{size_mb} - Размер в MB
{created} - Дата создания
{modified} - Дата изменения
{accessed} - Дата доступа
{file_category} - Категория файла"""
        ]
        
        self.desc_text.delete(1.0, END)
        self.desc_text.insert(END, descriptions[self.current_desc_page])
        self.desc_label.config(text=f"Страница {self.current_desc_page + 1}/4")
    
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
            "🔢 Нумерация": ["{numbers1}", "{numbers01}", "{numbers001}", "{reverse}", "{reverseX}"],
            "📅 Дата/Время": ["{date}", "{time}", "{datetime}", "{year}", "{timestamp}"],
            "🔤 Буквы": ["{letters}", "{Letters}", "{lettersR}", "{LettersR}", "{cyrillic}"],
            "📊 Инфо о файле": ["{size}", "{size_kb}", "{size_mb}", "{created}", "{modified}"],
            "🎲 Случайные": ["{random3}", "{random5}", "{random8}", "{randomX}", "{uuid}"],
            "🖼️ Изображения": ["{dominant_color}", "{camera_model}", "{dimensions}"],
            "🎵 Аудио": ["{artist}", "{title}", "{duration}", "{bitrate}"],
            "🎥 Видео": ["{codec}", "{resolution}", "{fps}", "{duration}"]
        }
        
        for category, placeholders in categories.items():
            submenu = Menu(menu, tearoff=0)
            for ph in placeholders:
                submenu.add_command(label=ph, 
                                  command=lambda p=ph: self.insert_placeholder(p))
            menu.add_cascade(label=category, menu=submenu)
        
        menu.post(self.pattern_entry.winfo_rootx(), 
                 self.pattern_entry.winfo_rooty() + self.pattern_entry.winfo_height())
    
    # ОСНОВНЫЕ ФУНКЦИИ ПЕРЕИМЕНОВАНИЯ
    def generate_new_name(self, pattern, i, original_name, file_path):
        """Генерирует новое имя файла на основе шаблона"""
        new_name = pattern
        filename, ext = os.path.splitext(original_name)
        
        # Базовые плейсхолдеры
        new_name = self.process_basic_placeholders(new_name, i, filename, ext)
        
        # Информация о файле
        new_name = self.process_file_info_placeholders(new_name, file_path)
        
        # Медиа-плейсхолдеры
        new_name = self.process_media_placeholders(new_name, file_path, ext)
        
        # Умная организация
        new_name = self.process_smart_placeholders(new_name, file_path, ext)
        
        # Текст и преобразования
        new_name = self.process_text_placeholders(new_name, filename)
        
        # Добавляем расширение, если его нет
        if not os.path.splitext(new_name)[1] and ext:
            new_name += ext
        
        return new_name
    
    def process_basic_placeholders(self, new_name, i, filename, ext):
        """Обрабатывает базовые плейсхолдеры"""
        # Нумерация с ведущими нулями
        if "{numbers01}" in new_name:
            new_name = new_name.replace("{numbers01}", str(i+1).zfill(2))
        
        if "{numbers001}" in new_name:
            new_name = new_name.replace("{numbers001}", str(i+1).zfill(3))
        
        # Обратная нумерация от X
        if "{reverseX}" in new_name:
            try:
                start_num = int(new_name.split("{reverseX}")[0].split()[-1])
                new_num = start_num - i
                new_name = new_name.replace("{reverseX}", str(new_num))
            except:
                new_num = len(self.files) - i
                new_name = new_name.replace("{reverseX}", str(new_num))
        
        # Кириллица
        if "{cyrillic}" in new_name:
            cyrillic = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
            if i < len(cyrillic):
                new_name = new_name.replace("{cyrillic}", cyrillic[i])
        
        # Unix timestamp
        if "{timestamp}" in new_name:
            new_name = new_name.replace("{timestamp}", str(int(datetime.now().timestamp())))
        
        return new_name
    
    def process_file_info_placeholders(self, new_name, file_path):
        """Обрабатывает плейсхолдеры информации о файле"""
        try:
            stat = os.stat(file_path)
            
            # Размер файла
            if "{size}" in new_name:
                new_name = new_name.replace("{size}", str(stat.st_size))
            
            if "{size_kb}" in new_name:
                new_name = new_name.replace("{size_kb}", f"{stat.st_size/1024:.1f}")
            
            if "{size_mb}" in new_name:
                new_name = new_name.replace("{size_mb}", f"{stat.st_size/(1024*1024):.1f}")
            
            # Даты
            if "{created}" in new_name:
                new_name = new_name.replace("{created}", datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d"))
            
            if "{modified}" in new_name:
                new_name = new_name.replace("{modified}", datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d"))
            
            if "{accessed}" in new_name:
                new_name = new_name.replace("{accessed}", datetime.fromtimestamp(stat.st_atime).strftime("%Y-%m-%d"))
                
        except:
            pass
        
        return new_name
    
    def process_media_placeholders(self, new_name, file_path, ext):
        """Обрабатывает медиа-плейсхолдеры"""
        file_path_lower = file_path.lower()
        
        # Для изображений
        if ext.lower() in self.file_types["images"]:
            new_name = self.process_image_placeholders(new_name, file_path)
        
        # Для аудио
        elif ext.lower() in self.file_types["audio"]:
            new_name = self.process_audio_placeholders(new_name, file_path)
        
        # Для видео
        elif ext.lower() in self.file_types["video"]:
            new_name = self.process_video_placeholders(new_name, file_path)
        
        return new_name
    
    def process_image_placeholders(self, new_name, file_path):
        """Обрабатывает плейсхолдеры для изображений"""
        try:
            with Image.open(file_path) as img:
                # Размеры изображения
                if "{dimensions}" in new_name:
                    new_name = new_name.replace("{dimensions}", f"{img.width}x{img.height}")
                
                # EXIF данные
                try:
                    exif_data = img._getexif()
                    if exif_data:
                        for tag_id, value in exif_data.items():
                            tag = ExifTags.TAGS.get(tag_id, tag_id)
                            
                            if tag == 'Model' and "{camera_model}" in new_name:
                                new_name = new_name.replace("{camera_model}", str(value))
                            
                            elif tag == 'FocalLength' and "{focal_length}" in new_name:
                                new_name = new_name.replace("{focal_length}", str(value))
                            
                            elif tag == 'ISOSpeedRatings' and "{iso}" in new_name:
                                new_name = new_name.replace("{iso}", str(value))
                            
                            elif tag == 'ExposureTime' and "{shutter_speed}" in new_name:
                                new_name = new_name.replace("{shutter_speed}", str(value))
                            
                            elif tag == 'FNumber' and "{aperture}" in new_name:
                                new_name = new_name.replace("{aperture}", str(value))
                except:
                    pass
                
                # Доминирующий цвет (упрощенная версия)
                if "{dominant_color}" in new_name:
                    try:
                        # Уменьшаем изображение для скорости
                        img_small = img.resize((100, 100))
                        colors = img_small.getcolors(maxcolors=10000)
                        if colors:
                            most_common = max(colors, key=lambda x: x[0])
                            dominant_rgb = most_common[1]
                            # Простое определение цвета
                            color_name = self.get_color_name(dominant_rgb)
                            new_name = new_name.replace("{dominant_color}", color_name)
                    except:
                        new_name = new_name.replace("{dominant_color}", "разноцветный")
                        
        except Exception as e:
            print(f"Ошибка обработки изображения: {e}")
        
        return new_name
    
    def get_color_name(self, rgb):
        """Определяет название цвета по RGB"""
        if isinstance(rgb, tuple) and len(rgb) >= 3:
            r, g, b = rgb[0], rgb[1], rgb[2]
            
            # Простая логика определения цвета
            if r > 200 and g < 100 and b < 100:
                return "красный"
            elif r < 100 and g > 200 and b < 100:
                return "зеленый"
            elif r < 100 and g < 100 and b > 200:
                return "синий"
            elif r > 200 and g > 200 and b < 100:
                return "желтый"
            elif r > 200 and g < 100 and b > 200:
                return "фиолетовый"
            elif r > 200 and g > 100 and b < 100:
                return "оранжевый"
        
        return "разноцветный"
    
    def process_audio_placeholders(self, new_name, file_path):
        """Обрабатывает плейсхолдеры для аудио"""
        try:
            audio = MP3(file_path)
            
            # Базовые теги
            if "{artist}" in new_name and 'TPE1' in audio:
                new_name = new_name.replace("{artist}", str(audio['TPE1']))
            
            if "{title}" in new_name and 'TIT2' in audio:
                new_name = new_name.replace("{title}", str(audio['TIT2']))
            
            if "{album}" in new_name and 'TALB' in audio:
                new_name = new_name.replace("{album}", str(audio['TALB']))
            
            if "{track_number}" in new_name and 'TRCK' in audio:
                new_name = new_name.replace("{track_number}", str(audio['TRCK']))
            
            if "{genre}" in new_name and 'TCON' in audio:
                new_name = new_name.replace("{genre}", str(audio['TCON']))
            
            if "{year}" in new_name and 'TDRC' in audio:
                new_name = new_name.replace("{year}", str(audio['TDRC']))
            
            # Техническая информация
            if "{duration}" in new_name:
                duration = audio.info.length
                mins = int(duration // 60)
                secs = int(duration % 60)
                new_name = new_name.replace("{duration}", f"{mins:02d}:{secs:02d}")
            
            if "{bitrate}" in new_name:
                new_name = new_name.replace("{bitrate}", f"{audio.info.bitrate//1000}kbps")
                
        except Exception as e:
            print(f"Ошибка обработки аудио: {e}")
        
        return new_name
    
    def process_video_placeholders(self, new_name, file_path):
        """Обрабатывает плейсхолдеры для видео"""
        try:
            # Используем OpenCV для получения информации о видео
            cap = cv2.VideoCapture(file_path)
            
            if "{resolution}" in new_name:
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                new_name = new_name.replace("{resolution}", f"{width}x{height}")
            
            if "{fps}" in new_name or "{frame_rate}" in new_name:
                fps = cap.get(cv2.CAP_PROP_FPS)
                new_name = new_name.replace("{fps}", f"{fps:.1f}")
                new_name = new_name.replace("{frame_rate}", f"{fps:.1f}")
            
            if "{duration}" in new_name:
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps > 0:
                    duration = frame_count / fps
                    mins = int(duration // 60)
                    secs = int(duration % 60)
                    new_name = new_name.replace("{duration}", f"{mins:02d}:{secs:02d}")
            
            cap.release()
            
        except Exception as e:
            print(f"Ошибка обработки видео: {e}")
        
        return new_name
    
    def process_smart_placeholders(self, new_name, file_path, ext):
        """Обрабатывает плейсхолдеры умной организации"""
        # Категория файла
        if "{file_category}" in new_name:
            for category, extensions in self.file_types.items():
                if ext.lower() in extensions:
                    new_name = new_name.replace("{file_category}", category)
                    break
            else:
                new_name = new_name.replace("{file_category}", "other")
        
        # Тип файла
        if "{file_type}" in new_name:
            new_name = new_name.replace("{file_type}", ext[1:].upper() if ext else "NOEXT")
        
        # Качество (упрощенная логика)
        if "{quality}" in new_name:
            try:
                size = os.path.getsize(file_path)
                if size < 1024 * 1024:  # < 1MB
                    quality = "low"
                elif size < 10 * 1024 * 1024:  # < 10MB
                    quality = "medium"
                else:
                    quality = "high"
                new_name = new_name.replace("{quality}", quality)
            except:
                new_name = new_name.replace("{quality}", "unknown")
        
        return new_name
    
    def process_text_placeholders(self, new_name, filename):
        """Обрабатывает текстовые плейсхолдеры"""
        # Реверс имени
        if "{reverse}" in new_name:
            new_name = new_name.replace("{reverse}", filename[::-1])
        
        # Перемешивание букв
        if "{shuffle}" in new_name:
            chars = list(filename)
            random.shuffle(chars)
            new_name = new_name.replace("{shuffle}", ''.join(chars))
        
        # CamelCase
        if "{camelCase}" in new_name:
            words = filename.replace('_', ' ').replace('-', ' ').split()
            camel_case = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
            new_name = new_name.replace("{camelCase}", camel_case)
        
        # PascalCase
        if "{PascalCase}" in new_name:
            words = filename.replace('_', ' ').replace('-', ' ').split()
            pascal_case = ''.join(word.capitalize() for word in words)
            new_name = new_name.replace("{PascalCase}", pascal_case)
        
        # snake_case
        if "{snake_case}" in new_name:
            snake_case = filename.replace(' ', '_').replace('-', '_').lower()
            new_name = new_name.replace("{snake_case}", snake_case)
        
        # kebab-case
        if "{kebab-case}" in new_name:
            kebab_case = filename.replace(' ', '-').replace('_', '-').lower()
            new_name = new_name.replace("{kebab-case}", kebab_case)
        
        # URL-слаг
        if "{slug}" in new_name:
            slug = ''.join(c for c in filename.lower() if c.isalnum() or c in ' -')
            slug = slug.replace(' ', '-')
            new_name = new_name.replace("{slug}", slug)
        
        return new_name

    # ОСТАЛЬНЫЕ МЕТОДЫ (select_files, update_file_list, show_preview, rename_files, etc.)
    # ... они остаются аналогичными предыдущей версии, но адаптированными под новую структуру

    def select_files(self):
        """Выбор файлов для переименования"""
        files = filedialog.askopenfilenames(
            title="Выберите файлы для переименования",
            filetypes=[
                ("Все файлы", "*.*"),
                ("Изображения", "*.jpg *.jpeg *.png *.gif *.bmp *.tiff *.webp"),
                ("Аудио", "*.mp3 *.wav *.ogg *.flac *.m4a *.aac"),
                ("Видео", "*.mp4 *.avi *.mkv *.mov *.wmv *.flv *.webm"),
                ("Документы", "*.pdf *.doc *.docx *.txt *.xlsx *.pptx")
            ]
        )
        if files:
            self.files = list(files)
            self.update_file_list()
    
    def update_file_list(self):
        """Обновляет список файлов в интерфейсе"""
        # Очищаем дерево
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Добавляем файлы
        for file_path in self.files:
            try:
                name = os.path.basename(file_path)
                size = os.path.getsize(file_path)
                file_type = os.path.splitext(name)[1].upper() or "ФАЙЛ"
                modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M")
                
                # Форматируем размер
                if size < 1024:
                    size_str = f"{size} B"
                elif size < 1024 * 1024:
                    size_str = f"{size/1024:.1f} KB"
                else:
                    size_str = f"{size/(1024*1024):.1f} MB"
                
                self.file_tree.insert("", END, values=(name, size_str, file_type, modified))
                
            except Exception as e:
                print(f"Ошибка добавления файла {file_path}: {e}")
        
        self.status_label.config(text=f"📁 Выбрано файлов: {len(self.files)}")
    
    def show_tree_menu(self, event):
        """Показывает контекстное меню для дерева файлов"""
        try:
            self.tree_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tree_menu.grab_release()
    
    def remove_selected_file(self):
        """Удаляет выбранный файл из списка"""
        selection = self.file_tree.selection()
        if selection:
            index = self.file_tree.index(selection[0])
            self.files.pop(index)
            self.update_file_list()
    
    def show_file_info(self):
        """Показывает детальную информацию о файле"""
        selection = self.file_tree.selection()
        if selection:
            index = self.file_tree.index(selection[0])
            file_path = self.files[index]
            
            info_window = Toplevel(self.root)
            info_window.title("Информация о файле")
            info_window.geometry("400x300")
            
            try:
                stat = os.stat(file_path)
                info_text = f"""📄 ИНФОРМАЦИЯ О ФАЙЛЕ

📁 Имя: {os.path.basename(file_path)}
📊 Размер: {self.format_size(stat.st_size)}
📅 Создан: {datetime.fromtimestamp(stat.st_ctime)}
✏️ Изменен: {datetime.fromtimestamp(stat.st_mtime)}
🔍 Доступ: {datetime.fromtimestamp(stat.st_atime)}
📝 Расширение: {os.path.splitext(file_path)[1]}

📊 ДОПОЛНИТЕЛЬНО:"""
                
                # Медиа-информация
                ext = os.path.splitext(file_path)[1].lower()
                if ext in self.file_types["images"]:
                    try:
                        with Image.open(file_path) as img:
                            info_text += f"\n🖼️ Размер: {img.width} x {img.height}"
                    except:
                        pass
                
                elif ext in self.file_types["audio"]:
                    try:
                        audio = MP3(file_path)
                        info_text += f"\n🎵 Длительность: {audio.info.length:.1f} сек"
                        info_text += f"\n🎵 Битрейт: {audio.info.bitrate} bps"
                    except:
                        pass
                
                text_widget = Text(info_window, wrap=WORD, font=("Arial", 9))
                text_widget.insert(END, info_text)
                text_widget.config(state=DISABLED)
                text_widget.pack(fill=BOTH, expand=True, padx=10, pady=10)
                
            except Exception as e:
                Label(info_window, text=f"Ошибка: {e}").pack(padx=10, pady=10)
    
    def format_size(self, size_bytes):
        """Форматирование размера файла"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
    
    # ОСТАЛЬНЫЕ МЕТОДЫ (show_preview, rename_files, undo_rename, clear_list, etc.)
    # ... они остаются аналогичными предыдущей версии

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
            new_name = self.generate_new_name(pattern, i, old_name, file_path)
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
                       "{random", "{original", "{ext", "{reverse", "{uuid", "{year", 
                       "{datetime", "{size", "{created", "{modified}"]
        has_placeholder = any(ph in pattern for ph in placeholders)
        
        # Если нет плейсхолдеров, добавляем {numbers1}
        if not has_placeholder:
            pattern += " {numbers1}"
            self.pattern_var.set(pattern)
        
        if self.preview_var.get():
            result = messagebox.askyesno("Подтверждение", 
                                       "Показать превью перед переименованием?")
            if result:
                self.show_preview()
                return
        
        try:
            # Сохраняем состояние для отмены
            self.undo_stack.append(list(self.files))
            if len(self.undo_stack) > 10:
                self.undo_stack.pop(0)
            
            directory = os.path.dirname(self.files[0])
            renamed_files = []
            
            for i, file_path in enumerate(self.files):
                old_name = os.path.basename(file_path)
                new_name = self.generate_new_name(pattern, i, old_name, file_path)
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
    
    # ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ
    def change_case_dialog(self):
        """Диалог изменения регистра"""
        dialog = Toplevel(self.root)
        dialog.title("Изменение регистра")
        dialog.geometry("300x150")
        
        Label(dialog, text="Выберите регистр:", font=("Arial", 10)).pack(pady=10)
        
        case_var = StringVar(value="upper")
        
        Radiobutton(dialog, text="ВЕРХНИЙ РЕГИСТР", variable=case_var, 
                   value="upper", font=("Arial", 9)).pack(anchor="w", padx=20)
        Radiobutton(dialog, text="нижний регистр", variable=case_var,
                   value="lower", font=("Arial", 9)).pack(anchor="w", padx=20)
        Radiobutton(dialog, text="Заглавные Буквы", variable=case_var,
                   value="title", font=("Arial", 9)).pack(anchor="w", padx=20)
        
        def apply_case():
            self.change_case(case_var.get())
            dialog.destroy()
        
        Button(dialog, text="Применить", command=apply_case,
               bg="lightgreen", font=("Arial", 10)).pack(pady=10)
    
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
                en_ru = {v: k for k, v in ru_en.items() if v}
                for char in name.lower():
                    new_name += en_ru.get(char, char)
            
            new_path = os.path.join(os.path.dirname(file_path), new_name + ext)
            os.rename(file_path, new_path)
            renamed_files.append(new_path)
        
        self.files = renamed_files
        self.update_file_list()
        messagebox.showinfo("Успех", "Транслитерация завершена")
    
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
    
    # ИНТЕРНЕТ-ФУНКЦИИ
    def get_weather(self):
        """Получение погоды (заглушка)"""
        messagebox.showinfo("Погода", "Функция получения погоды требует API ключ и интернет-соединение")
    
    def get_location(self):
        """Определение местоположения (заглушка)"""
        messagebox.showinfo("Местоположение", "Функция определения местоположения требует GPS данные или IP геолокацию")
    
    def translate_names(self):
        """Перевод имен файлов (заглушка)"""
        messagebox.showinfo("Перевод", "Функция перевода требует API ключ переводчика и интернет-соединение")

if __name__ == "__main__":
    root = Tk()
    app = RenamerProUltimate(root)
    root.mainloop()
