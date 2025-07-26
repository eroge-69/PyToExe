import tkinter as tk
from tkinter import font as tkfont
from tkinter import colorchooser, messagebox, filedialog
import json
import os
from datetime import datetime, timedelta

class PokerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StrategyArt1.0 - Программа для покера")
        
        # Установка размеров окна
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = screen_width // 3
        window_height = int(screen_height * 0.85)
        root.geometry(f"{window_width}x{window_height}")
        
        # Базовый шрифт
        self.base_font = tkfont.Font(family="Arial", size=12)
        
        # Пароли
        self.EDIT_PASSWORD = "05111990"
        self.TIME_SETTING_PASSWORD = "0511199008092016"
        
        # Файл для хранения времени использования
        self.TIME_LIMIT_FILE = "time_limit.json"
        
        # Проверяем время использования
        self.time_limit_hours = 0  # 0 - неограниченно
        self.expiration_time = None
        self.load_time_limit()
        
        # Словарь для хранения данных всех разделов
        self.section_data = {
            "multipot_aggressor_flop": {"text": "", "tags": []},
            "multipot_aggressor_turn": {"text": "", "tags": []},
            "multipot_aggressor_river": {"text": "", "tags": []},
            "multipot_koller_flop": {"text": "", "tags": []},
            "multipot_koller_turn": {"text": "", "tags": []},
            "multipot_koller_river": {"text": "", "tags": []},
            "headsap_strategy1_flop": {"text": "", "tags": []},
            "headsap_strategy1_turn": {"text": "", "tags": []},
            "headsap_strategy1_river": {"text": "", "tags": []},
            "headsap_strategy2_flop": {"text": "", "tags": []},
            "headsap_strategy2_turn": {"text": "", "tags": []},
            "headsap_strategy2_river": {"text": "", "tags": []},
            "headsap_strategy3_flop": {"text": "", "tags": []},
            "headsap_strategy3_turn": {"text": "", "tags": []},
            "headsap_strategy3_river": {"text": "", "tags": []},
            "headsap_strategy4_flop": {"text": "", "tags": []},
            "headsap_strategy4_turn": {"text": "", "tags": []},
            "headsap_strategy4_river": {"text": "", "tags": []},
            "headsap_strategy5_flop": {"text": "", "tags": []},
            "headsap_strategy5_turn": {"text": "", "tags": []},
            "headsap_strategy5_river": {"text": "", "tags": []},
            "headsap_strategy6_flop": {"text": "", "tags": []},
            "headsap_strategy6_turn": {"text": "", "tags": []},
            "headsap_strategy6_river": {"text": "", "tags": []},
            "headsap_strategy7_flop": {"text": "", "tags": []},
            "headsap_strategy7_turn": {"text": "", "tags": []},
            "headsap_strategy7_river": {"text": "", "tags": []},
        }
        
        # Текущий активный раздел
        self.current_section = None
        
        # Загрузка сохранённых данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        self.setup_formatting_toolbar()
        self.setup_keyboard_shortcuts()
        
        # Текущая стратегия для хедсапа
        self.current_strategy = ""
        
        # Флаг режима редактирования
        self.edit_mode = False
        
        # Флаг режима настройки времени
        self.time_setting_mode = False
        
        # Проверяем, не истекло ли время
        self.check_time_limit()
    
    def load_time_limit(self):
        """Загружает настройки времени из файла"""
        if os.path.exists(self.TIME_LIMIT_FILE):
            try:
                with open(self.TIME_LIMIT_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.time_limit_hours = data.get("time_limit_hours", 0)
                    expiration_str = data.get("expiration_time")
                    if expiration_str:
                        self.expiration_time = datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
            except Exception as e:
                print(f"Ошибка загрузки времени: {str(e)}")
                self.time_limit_hours = 0
                self.expiration_time = None
    
    def save_time_limit(self):
        """Сохраняет настройки времени в файл"""
        try:
            data = {
                "time_limit_hours": self.time_limit_hours,
                "expiration_time": self.expiration_time.strftime("%Y-%m-%d %H:%M:%S") if self.expiration_time else None
            }
            with open(self.TIME_LIMIT_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения времени: {str(e)}")
    
    def check_time_limit(self):
        """Проверяет, не истекло ли время использования"""
        if self.time_limit_hours == 0:  # Неограниченный режим
            return
        
        if self.expiration_time and datetime.now() >= self.expiration_time:
            self.block_program()
    
    def block_program(self):
        """Блокирует программу (все кнопки кроме редактирования)"""
        # Отключаем все основные кнопки
        self.multipot_button.config(state="disabled")
        self.headsap_button.config(state="disabled")
        self.aggressor_button.config(state="disabled")
        self.koller_button.config(state="disabled")
        
        # Отключаем кнопки улиц
        for frame in [self.aggressor_street_frame, self.koller_street_frame, self.headsap_street_frame]:
            for child in frame.winfo_children():
                child.config(state="disabled")
        
        # Отключаем кнопки стратегий
        for frame in [self.strategy_col1, self.strategy_col2]:
            for child in frame.winfo_children():
                child.config(state="disabled")
        
        # Блокируем текстовое поле
        self.text_box.config(state="disabled")
        
        # Показываем сообщение
        messagebox.showwarning(
            "Время истекло", 
            "Срок использования программы истек. Обратитесь к разработчику."
        )
    
    def unblock_program(self):
        """Разблокирует программу"""
        # Включаем все основные кнопки
        self.multipot_button.config(state="normal")
        self.headsap_button.config(state="normal")
        self.aggressor_button.config(state="normal")
        self.koller_button.config(state="normal")
        
        # Включаем кнопки улиц
        for frame in [self.aggressor_street_frame, self.koller_street_frame, self.headsap_street_frame]:
            for child in frame.winfo_children():
                child.config(state="normal")
        
        # Включаем кнопки стратегий
        for frame in [self.strategy_col1, self.strategy_col2]:
            for child in frame.winfo_children():
                child.config(state="normal")
        
        # Разблокируем текстовое поле
        self.text_box.config(state="normal")
    
    def setup_keyboard_shortcuts(self):
        # Привязываем комбинации клавиш для корневого окна
        self.root.bind('<Control-v>', self.paste_from_clipboard)
        self.root.bind('<Control-V>', self.paste_from_clipboard)  # Для Caps Lock
        self.root.bind('<Command-v>', self.paste_from_clipboard)  # Для macOS
        
        # Переопределяем стандартное поведение текстового поля
        self.text_box.bind('<Control-v>', self.paste_from_clipboard)
        self.text_box.bind('<Control-V>', self.paste_from_clipboard)
        self.text_box.bind('<Command-v>', self.paste_from_clipboard)
    
    def paste_from_clipboard(self, event=None):
        try:
            # Получаем текст из буфера обмена
            text = self.root.clipboard_get()
            if text:
                # Удаляем выделенный текст, если есть
                try:
                    if self.text_box.tag_ranges("sel"):
                        self.text_box.delete("sel.first", "sel.last")
                except tk.TclError:
                    pass
                
                # Вставляем в текущую позицию курсора
                self.text_box.insert("insert", text)
            
            # Возвращаем "break" только если это событие от клавиатуры
            if event:
                return "break"
        except tk.TclError:
            pass  # В буфере обмена нет текста
        return None
    
    def paste_from_file(self):
        # Открываем диалог выбора файла
        file_path = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_box.insert('insert', content)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить файл: {str(e)}")
    
    def load_data(self):
        if os.path.exists("poker_data.json"):
            try:
                with open("poker_data.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Обновляем только существующие ключи
                    for key in self.section_data:
                        if key in data:
                            self.section_data[key] = data[key]
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
    
    def save_data(self):
        try:
            # Сохраняем текущий раздел перед сохранением
            if self.current_section:
                self.save_current_section()
            
            with open("poker_data.json", "w", encoding="utf-8") as f:
                json.dump(self.section_data, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Сохранение", "Данные успешно сохранены")
            
            # Закрываем режим редактирования после сохранения
            self.toggle_edit_mode(False)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {str(e)}")
    
    def save_current_section(self):
        if not self.current_section:
            return
        
        # Получаем весь текст
        text = self.text_box.get("1.0", "end-1c")
        tags = []
        
        # Собираем информацию о всех тегах
        for tag in self.text_box.tag_names():
            if tag not in ("sel", "cursor"):
                ranges = self.text_box.tag_ranges(tag)
                for i in range(0, len(ranges), 2):
                    start = ranges[i]
                    end = ranges[i+1]
                    start_index = self.text_box.index(start)
                    end_index = self.text_box.index(end)
                    
                    # Получаем конфигурацию тега
                    config = {}
                    tag_config = self.text_box.tag_config(tag)
                    if tag_config:
                        for key, value in tag_config.items():
                            if len(value) >= 2:
                                config[key] = value[-1]
                    
                    tags.append({
                        "name": tag,
                        "start": start_index,
                        "end": end_index,
                        "config": config
                    })
        
        self.section_data[self.current_section] = {
            "text": text,
            "tags": tags
        }
    
    def create_widgets(self):
        # Основной контейнер для всего интерфейса (кроме текстового поля)
        self.top_container = tk.Frame(self.root)
        self.top_container.pack(side="top", fill="x", expand=False)
        
        # Левый фрейм для кнопок стратегий
        self.left_frame = tk.Frame(self.top_container)
        self.left_frame.pack(side="left", fill="both", expand=True)
        
        # Правый фрейм для кнопок форматирования и кнопки "Ред."
        self.right_frame = tk.Frame(self.top_container)
        self.right_frame.pack(side="right", fill="y", expand=False)
        
        # Контейнер для текстового поля (нижняя часть)
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(side="bottom", fill="both", expand=True)
        
        # Фрейм для кнопки "Ред." и поля ввода пароля
        self.edit_frame = tk.Frame(self.right_frame)
        self.edit_frame.pack(side="top", anchor="ne", padx=5, pady=5)
        
        # Кнопка "Ред." в правом верхнем углу
        self.edit_btn = tk.Button(
            self.edit_frame,
            text="Ред.",
            width=4,
            height=1,
            command=self.request_password
        )
        self.edit_btn.pack(side="left")
        
        # Поле для ввода пароля (изначально скрыто)
        self.password_entry = tk.Entry(
            self.edit_frame,
            width=10,
            show="*"
        )
        
        # Фрейм для основных кнопок (Мультипот/Хедсап) в левой части
        self.main_button_frame = tk.Frame(self.left_frame)
        self.main_button_frame.pack(side="top", pady=5)
        
        # Кнопки Мультипот и Хедсап
        self.multipot_button = tk.Button(
            self.main_button_frame,
            text="Мультипот",
            width=15,
            height=2,
            command=self.show_multipot_actions
        )
        self.multipot_button.pack(side="left", padx=5)
        
        self.headsap_button = tk.Button(
            self.main_button_frame,
            text="Хедсап",
            width=15,
            height=2,
            command=self.show_headsap_strategies
        )
        self.headsap_button.pack(side="left", padx=5)
        
        # Фрейм для кнопок Агрессор/Коллер
        self.action_frame = tk.Frame(self.left_frame)
        self.action_frame.pack_forget()
        
        self.aggressor_button = tk.Button(
            self.action_frame,
            text="Агрессор",
            width=15,
            height=2,
            command=self.show_aggressor_streets
        )
        self.aggressor_button.pack(side="left", padx=5)
        
        self.koller_button = tk.Button(
            self.action_frame,
            text="Коллер",
            width=15,
            height=2,
            command=self.show_koller_streets
        )
        self.koller_button.pack(side="left", padx=5)
        
        # Фрейм для кнопок Флоп/Тёрн/Ривер
        self.street_frame_container = tk.Frame(self.left_frame)
        self.street_frame_container.pack_forget()
        
        # Фреймы для улиц (Агрессор и Коллер)
        self.aggressor_street_frame = tk.Frame(self.street_frame_container)
        self.aggressor_street_frame.pack_forget()
        
        self.flop_button_agr = tk.Button(
            self.aggressor_street_frame,
            text="Флоп",
            width=10,
            height=2,
            command=lambda: self.show_section("multipot_aggressor_flop")
        )
        self.flop_button_agr.pack(side="left", padx=5)
        
        self.turn_button_agr = tk.Button(
            self.aggressor_street_frame,
            text="Тёрн",
            width=10,
            height=2,
            command=lambda: self.show_section("multipot_aggressor_turn")
        )
        self.turn_button_agr.pack(side="left", padx=5)
        
        self.river_button_agr = tk.Button(
            self.aggressor_street_frame,
            text="Ривер",
            width=10,
            height=2,
            command=lambda: self.show_section("multipot_aggressor_river")
        )
        self.river_button_agr.pack(side="left", padx=5)
        
        self.koller_street_frame = tk.Frame(self.street_frame_container)
        self.koller_street_frame.pack_forget()
        
        self.flop_button_kol = tk.Button(
            self.koller_street_frame,
            text="Флоп",
            width=10,
            height=2,
            command=lambda: self.show_section("multipot_koller_flop")
        )
        self.flop_button_kol.pack(side="left", padx=5)
        
        self.turn_button_kol = tk.Button(
            self.koller_street_frame,
            text="Тёрн",
            width=10,
            height=2,
            command=lambda: self.show_section("multipot_koller_turn")
        )
        self.turn_button_kol.pack(side="left", padx=5)
        
        self.river_button_kol = tk.Button(
            self.koller_street_frame,
            text="Ривер",
            width=10,
            height=2,
            command=lambda: self.show_section("multipot_koller_river")
        )
        self.river_button_kol.pack(side="left", padx=5)
        
        # Фрейм для кнопок стратегий в Хедсапе
        self.headsap_strategy_frame = tk.Frame(self.left_frame)
        self.headsap_strategy_frame.pack_forget()

        strategy_data = [
            ("ХА.СРП.\n3пл баррель", "headsap_strategy1"),
            ("ХА.СРП.\nКак Коллер", "headsap_strategy2"),
            ("ХА.ПФРа.\nКонбет, чек-рейз", "headsap_strategy3"),
            ("ХА.Чек флопа\nи ОПП чек", "headsap_strategy4"),
            ("ХА.Чек флопа\nи ОПП ставит", "headsap_strategy5"),
            ("Как играть\nпротив donk-bet", "headsap_strategy6"),
            ("Проб-бет (без позиции)\nот коллера на тёрне", "headsap_strategy7")
        ]

        # Рассчитываем увеличенную ширину (на 20% больше)
        base_width = 25
        increased_width = int(base_width * 1.2)

        # Создаем два фрейма для столбиков
        self.strategy_col1 = tk.Frame(self.headsap_strategy_frame)
        self.strategy_col1.pack(side="left", fill="both", expand=True, padx=5)

        self.strategy_col2 = tk.Frame(self.headsap_strategy_frame)
        self.strategy_col2.pack(side="left", fill="both", expand=True, padx=5)

        # Создаем кнопки для первого столбца (4 кнопки)
        for text, strategy_id in strategy_data[:4]:
            btn = tk.Button(
                self.strategy_col1,
                text=text,
                width=increased_width,
                height=2,
                command=lambda t=text, s=strategy_id: self.show_headsap_street_buttons(t, s)
            )
            btn.pack(pady=2)

        # Создаем кнопки для второго столбца (3 кнопки)
        for text, strategy_id in strategy_data[4:]:
            btn = tk.Button(
                self.strategy_col2,
                text=text,
                width=increased_width,
                height=2,
                command=lambda t=text, s=strategy_id: self.show_headsap_street_buttons(t, s)
            )
            btn.pack(pady=2)
        
        # Фрейм для кнопок улиц в Хедсапе
        self.headsap_street_frame = tk.Frame(self.left_frame)
        self.headsap_street_frame.pack_forget()
        
        # Текстовое поле с полосой прокрутки
        self.text_frame = tk.Frame(self.root)
        self.text_frame.pack(side="bottom", fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side="right", fill="y")
        
        self.text_box = tk.Text(
            self.text_frame,
            bg="white",
            font=self.base_font,
            wrap="word",
            yscrollcommand=self.scrollbar.set,
            undo=True
        )
        self.text_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.config(command=self.text_box.yview)
        
        # Настройка тегов для форматирования
        self.setup_text_tags()
    
    def setup_text_tags(self):
        # Стандартные теги форматирования
        self.text_box.tag_configure("bold", font=(self.base_font.actual("family"), self.base_font.actual("size"), "bold"))
        self.text_box.tag_configure("italic", font=(self.base_font.actual("family"), self.base_font.actual("size"), "italic"))
        self.text_box.tag_configure("underline", underline=True)
        self.text_box.tag_configure("overstrike", overstrike=True)
        
        # Базовый тег для размера шрифта
        self.text_box.tag_configure("font_size", font=self.base_font)
        
        # Базовый тег для цвета текста
        self.text_box.tag_configure("color", foreground="black")
    
    def setup_formatting_toolbar(self):
        # Размещаем панель инструментов в правом фрейме
        self.toolbar = tk.Frame(self.right_frame)
        self.toolbar.pack(side="top", fill="y", padx=5, pady=5)
        
        # Кнопки форматирования (изначально скрыты)
        self.bold_btn = tk.Button(self.toolbar, text="Ж", command=lambda: self.toggle_format("bold"))
        self.italic_btn = tk.Button(self.toolbar, text="К", command=lambda: self.toggle_format("italic"))
        self.underline_btn = tk.Button(self.toolbar, text="П", command=lambda: self.toggle_format("underline"))
        self.strike_btn = tk.Button(self.toolbar, text="З", command=lambda: self.toggle_format("overstrike"))
        self.color_btn = tk.Button(self.toolbar, text="Цвет", command=self.change_text_color)
        
        # Выбор размера шрифта (только для выделенного текста)
        self.font_size = tk.IntVar(value=self.base_font.actual("size"))
        self.size_menu = tk.OptionMenu(
            self.toolbar, 
            self.font_size, 
            *range(8, 25), 
            command=self.change_selected_font_size
        )
        
        # Кнопка сохранения
        self.save_btn = tk.Button(self.toolbar, text="Сохранить все", command=self.save_data)
        
        # Кнопка для вставки символа
        self.symbol_btn = tk.Button(self.toolbar, text="Символ", command=self.insert_symbol)
        
        # Кнопка для вставки из файла
        self.paste_file_btn = tk.Button(
            self.toolbar, 
            text="Вставить из файла", 
            command=self.paste_from_file
        )
        
        # Кнопка для вставки из буфера обмена
        self.paste_btn = tk.Button(self.toolbar, text="Вставить", command=self.paste_from_clipboard)
        
        # Кнопка выхода из режима редактирования
        self.exit_edit_btn = tk.Button(
            self.toolbar,
            text="Выход",
            command=lambda: self.toggle_edit_mode(False)
        )
        
        # Изначально скрываем все кнопки форматирования
        self.toggle_edit_mode(False)
    
    def request_password(self):
        """Запрашивает пароль для входа в режим редактирования или настройки времени"""
        if not self.edit_mode and not self.time_setting_mode:
            # Показываем поле для ввода пароля
            self.password_entry.pack(side="left", padx=5)
            self.password_entry.focus_set()
            
            # Кнопка подтверждения пароля
            self.confirm_btn = tk.Button(
                self.edit_frame,
                text="OK",
                width=2,
                command=self.check_password
            )
            self.confirm_btn.pack(side="left")
            
            # Привязываем Enter к проверке пароля
            self.password_entry.bind("<Return>", lambda e: self.check_password())
        else:
            if self.edit_mode:
                self.toggle_edit_mode(False)
            elif self.time_setting_mode:
                self.toggle_time_setting_mode(False)
    
    def check_password(self):
        """Проверяет введенный пароль"""
        entered_password = self.password_entry.get()
        
        if entered_password == self.EDIT_PASSWORD:
            self.toggle_edit_mode(True)
        elif entered_password == self.TIME_SETTING_PASSWORD:
            self.toggle_time_setting_mode(True)
        else:
            messagebox.showerror("Ошибка", "Неверный пароль")
        
        # Очищаем поле ввода и скрываем его
        self.password_entry.delete(0, tk.END)
        self.password_entry.pack_forget()
        self.confirm_btn.pack_forget()
    
    def toggle_edit_mode(self, state=None):
        """Переключает режим редактирования"""
        if state is None:
            self.edit_mode = not self.edit_mode
        else:
            self.edit_mode = state
        
        if self.edit_mode:
            # Выходим из режима настройки времени, если он был активен
            if self.time_setting_mode:
                self.toggle_time_setting_mode(False)
            
            # Показываем все кнопки форматирования
            self.bold_btn.pack(side="top", pady=2)
            self.italic_btn.pack(side="top", pady=2)
            self.underline_btn.pack(side="top", pady=2)
            self.strike_btn.pack(side="top", pady=2)
            self.color_btn.pack(side="top", pady=2)
            self.size_menu.pack(side="top", pady=2)
            self.save_btn.pack(side="top", pady=5)
            self.symbol_btn.pack(side="top", pady=2)
            self.paste_file_btn.pack(side="top", pady=2)
            self.paste_btn.pack(side="top", pady=2)
            self.exit_edit_btn.pack(side="top", pady=5)
            
            # Меняем текст кнопки "Ред." на "Обычн."
            self.edit_btn.config(text="Обычн.")
        else:
            # Скрываем все кнопки форматирования
            self.bold_btn.pack_forget()
            self.italic_btn.pack_forget()
            self.underline_btn.pack_forget()
            self.strike_btn.pack_forget()
            self.color_btn.pack_forget()
            self.size_menu.pack_forget()
            self.save_btn.pack_forget()
            self.symbol_btn.pack_forget()
            self.paste_file_btn.pack_forget()
            self.paste_btn.pack_forget()
            self.exit_edit_btn.pack_forget()
            
            # Меняем текст кнопки "Обычн." на "Ред."
            self.edit_btn.config(text="Ред.")
    
    def toggle_time_setting_mode(self, state=None):
        """Переключает режим настройки времени"""
        if state is None:
            self.time_setting_mode = not self.time_setting_mode
        else:
            self.time_setting_mode = state
        
        if self.time_setting_mode:
            # Выходим из режима редактирования, если он был активен
            if self.edit_mode:
                self.toggle_edit_mode(False)
            
            # Создаем окно для настройки времени
            self.time_setting_window = tk.Toplevel(self.root)
            self.time_setting_window.title("Настройка времени использования")
            self.time_setting_window.geometry("400x300")
            self.time_setting_window.resizable(False, False)
            
            # Информация о текущем времени
            time_info = "Неограниченный режим" if self.time_limit_hours == 0 else \
                      f"Осталось: {self.get_remaining_time()}"
            
            self.time_info_label = tk.Label(
                self.time_setting_window,
                text=time_info,
                font=("Arial", 12)
            )
            self.time_info_label.pack(pady=10)
            
            # Поле для ввода часов
            self.hours_label = tk.Label(
                self.time_setting_window,
                text="Введите количество часов (0 - неограниченно):",
                font=("Arial", 10)
            )
            self.hours_label.pack(pady=5)
            
            self.hours_entry = tk.Entry(
                self.time_setting_window,
                font=("Arial", 12),
                width=10
            )
            self.hours_entry.pack(pady=5)
            self.hours_entry.insert(0, str(self.time_limit_hours))
            
            # Кнопка сохранить
            self.save_time_btn = tk.Button(
                self.time_setting_window,
                text="Сохранить",
                width=15,
                height=2,
                command=self.save_time_settings
            )
            self.save_time_btn.pack(pady=10)
            
            # Кнопка выхода
            self.exit_time_btn = tk.Button(
                self.time_setting_window,
                text="Выход",
                width=15,
                height=2,
                command=lambda: self.toggle_time_setting_mode(False)
            )
            self.exit_time_btn.pack(pady=5)
            
            # Меняем текст кнопки "Ред." на "Обычн."
            self.edit_btn.config(text="Обычн.")
        else:
            # Закрываем окно настройки времени, если оно было открыто
            if hasattr(self, 'time_setting_window') and self.time_setting_window.winfo_exists():
                self.time_setting_window.destroy()
            
            # Меняем текст кнопки "Обычн." на "Ред."
            self.edit_btn.config(text="Ред.")
    
    def get_remaining_time(self):
        """Возвращает строку с оставшимся временем"""
        if self.time_limit_hours == 0:
            return "Неограниченный режим"
        
        if not self.expiration_time:
            return "Время не установлено"
        
        remaining = self.expiration_time - datetime.now()
        if remaining.total_seconds() <= 0:
            return "Время истекло"
        
        hours = int(remaining.total_seconds() // 3600)
        minutes = int((remaining.total_seconds() % 3600) // 60)
        return f"{hours} ч. {minutes} мин."
    
    def save_time_settings(self):
        """Сохраняет настройки времени"""
        try:
            hours = int(self.hours_entry.get())
            if hours < 0 or hours > 999:
                raise ValueError("Количество часов должно быть от 0 до 999")
            
            self.time_limit_hours = hours
            
            if hours > 0:
                self.expiration_time = datetime.now() + timedelta(hours=hours)
            else:
                self.expiration_time = None
            
            self.save_time_limit()
            self.check_time_limit()
            
            # Обновляем информацию в окне
            time_info = "Неограниченный режим" if self.time_limit_hours == 0 else \
                      f"Осталось: {self.get_remaining_time()}"
            self.time_info_label.config(text=time_info)
            
            messagebox.showinfo("Сохранено", "Настройки времени успешно сохранены")
            
            # Разблокируем программу, если она была заблокирована
            self.unblock_program()
        except ValueError as e:
            messagebox.showerror("Ошибка", str(e))
    
    def toggle_format(self, tag_name):
        try:
            # Проверяем, есть ли уже такой тег на выделенном тексте
            current_tags = self.text_box.tag_names("sel.first")
            if tag_name in current_tags:
                self.text_box.tag_remove(tag_name, "sel.first", "sel.last")
            else:
                self.text_box.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass  # Нет выделенного текста
    
    def change_text_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            try:
                # Создаем уникальный тег для этого цвета
                tag_name = f"color_{color}"
                if tag_name not in self.text_box.tag_names():
                    self.text_box.tag_configure(tag_name, foreground=color)
                self.text_box.tag_add(tag_name, "sel.first", "sel.last")
            except tk.TclError:
                pass  # Нет выделенного текста
    
    def change_selected_font_size(self, size):
        try:
            # Создаем уникальный тег для этого размера
            tag_name = f"size_{size}"
            if tag_name not in self.text_box.tag_names():
                self.text_box.tag_configure(tag_name, font=(self.base_font.actual("family"), size))
            self.text_box.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass  # Нет выделенного текста
    
    def insert_symbol(self):
        symbol_window = tk.Toplevel(self.root)
        symbol_window.title("Выберите символ")
        
        symbols = ["♠", "♥", "♦", "♣", "→", "←", "↑", "↓", "✓", "✗"]
        
        for i, symbol in enumerate(symbols):
            btn = tk.Button(
                symbol_window, 
                text=symbol, 
                font=("Arial", 14),
                command=lambda s=symbol: self.insert_selected_symbol(s, symbol_window)
            )
            btn.grid(row=i//5, column=i%5, padx=5, pady=5)
    
    def insert_selected_symbol(self, symbol, window):
        self.text_box.insert("insert", symbol)
        window.destroy()
    
    def show_section(self, section_name):
        # Сохраняем текущий раздел перед переключением
        if self.current_section:
            self.save_current_section()
        
        # Устанавливаем новый текущий раздел
        self.current_section = section_name
        
        # Очищаем текстовое поле
        self.text_box.config(state="normal")
        self.text_box.delete("1.0", "end")
        
        # Удаляем все пользовательские теги (кроме базовых)
        for tag in self.text_box.tag_names():
            if tag not in ("sel", "cursor", "bold", "italic", "underline", "overstrike", "font_size", "color"):
                self.text_box.tag_delete(tag)
        
        # Загружаем текст
        section = self.section_data[section_name]
        self.text_box.insert("end", section["text"])
        
        # Восстанавливаем форматирование
        for tag_info in section.get("tags", []):
            tag_name = tag_info["name"]
            
            # Если тег еще не существует, создаем его
            if tag_name not in self.text_box.tag_names():
                config = tag_info.get("config", {})
                if config:
                    # Восстанавливаем конфигурацию тега
                    self.text_box.tag_configure(tag_name, **config)
            
            # Применяем тег к тексту
            self.text_box.tag_add(tag_name, tag_info["start"], tag_info["end"])
        
        self.text_box.config(state="normal")
    
    def show_multipot_actions(self):
        self.action_frame.pack(side="top", pady=5)
        self.street_frame_container.pack(side="top", pady=5)
        self.headsap_strategy_frame.pack_forget()
        self.headsap_street_frame.pack_forget()
    
    def show_headsap_strategies(self):
        self.headsap_strategy_frame.pack(side="top", pady=5)
        self.action_frame.pack_forget()
        self.street_frame_container.pack_forget()
    
    def show_aggressor_streets(self):
        self.aggressor_street_frame.pack(side="top", pady=5)
        self.koller_street_frame.pack_forget()
    
    def show_koller_streets(self):
        self.koller_street_frame.pack(side="top", pady=5)
        self.aggressor_street_frame.pack_forget()
    
    def show_headsap_street_buttons(self, strategy_text, strategy_id):
        self.current_strategy = strategy_text
        self.headsap_street_frame.pack(side="top", pady=5)
        
        # Очищаем предыдущие кнопки
        for widget in self.headsap_street_frame.winfo_children():
            widget.destroy()
        
        # Создаем кнопки для улиц
        streets = [
            ("Флоп", f"{strategy_id}_flop"),
            ("Тёрн", f"{strategy_id}_turn"),
            ("Ривер", f"{strategy_id}_river")
        ]
        
        for street, section_id in streets:
            btn = tk.Button(
                self.headsap_street_frame,
                text=street,
                width=10,
                height=2,
                command=lambda s=section_id: self.show_section(s)
            )
            btn.pack(side="left", padx=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = PokerApp(root)
    root.mainloop()