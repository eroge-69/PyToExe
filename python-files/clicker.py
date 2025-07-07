import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import time
import pyautogui
import keyboard
import json
import os
import winsound
from PIL import Image, ImageTk
import math
from pynput import mouse, keyboard as kb_listener


class AdvancedAutoClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("AutoClicker")
        self.root.geometry("650x700")
        self.root.minsize(650, 700)
        self.root.configure(bg='#1e1e1e')

        # Сделаем окно адаптивным
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Загрузка иконки
        try:
            self.root.iconbitmap("autoclicker.ico")
        except:
            pass

        # Стили
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.configure_styles()

        # Переменные
        self.clicking = False
        self.recording = False
        self.macro_playing = False  # Новый флаг для воспроизведения макроса
        self.macro_actions = []
        self.current_tab = "clicker"
        self.mode = "infinite"
        self.mouse_listener = None
        self.keyboard_listener = None
        self.selected_macro = None

        # Макросы
        self.macros = {}
        self.load_macros()

        # Создание интерфейса
        self.create_widgets()

        # Глобальные горячие клавиши
        keyboard.add_hotkey('f5', self.start_operation)
        keyboard.add_hotkey('f6', self.stop_operation)
        keyboard.add_hotkey('f7', self.get_current_position)
        # Горячие клавиши для макросов
        keyboard.add_hotkey('f8', self.start_recording)
        keyboard.add_hotkey('f9', self.stop_recording)
        keyboard.add_hotkey('f10', self.toggle_macro_playback)  # Изменено на переключатель

        # Обработка закрытия
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Запуск потока для одновременного управления мышью и клавиатурой
        self.action_thread = None
        self.macro_thread = None  # Поток для воспроизведения макроса

    def configure_styles(self):
        # Настройка стилей
        self.style.configure('.', background='#1e1e1e', foreground='white', font=('Segoe UI', 9))
        self.style.configure('TFrame', background='#1e1e1e')
        self.style.configure('TLabel', background='#1e1e1e', foreground='white')
        self.style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        self.style.configure('TNotebook.Tab', background='#333', foreground='white',
                             padding=[15, 5], font=('Segoe UI', 10, 'bold'))
        self.style.map('TNotebook.Tab', background=[('selected', '#555')])
        self.style.configure('TButton', background='#333', foreground='white',
                             font=('Segoe UI', 9), borderwidth=1, padding=5)
        self.style.map('TButton', background=[('active', '#444'), ('disabled', '#222')])
        self.style.configure('TCheckbutton', background='#1e1e1e', foreground='white')
        self.style.configure('TRadiobutton', background='#1e1e1e', foreground='white')
        self.style.configure('TEntry', fieldbackground='#252525', foreground='white', insertbackground='white')
        self.style.configure('TCombobox', fieldbackground='#252525', foreground='white')
        self.style.configure('TLabelframe', background='#1e1e1e', foreground='#e1e1e1', font=('Segoe UI', 10, 'bold'))
        self.style.configure('TLabelframe.Label', background='#1e1e1e', foreground='#e1e1e1')
        self.style.configure('Start.TButton', background='#2a5c2a')
        self.style.configure('Stop.TButton', background='#5c2a2a')
        self.style.configure('Record.TButton', background='#5c2a2a')
        self.style.configure('Macro.TButton', background='#2a2a5c')

    def create_widgets(self):
        # Основной контейнер с адаптивностью
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        main_container.grid_rowconfigure(0, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Заголовок
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        title_label = ttk.Label(header_frame, text="AUTOCLICKER",
                                font=('Segoe UI', 14, 'bold'), foreground='#4a9cff')
        title_label.pack(side=tk.LEFT)

        # Создание вкладок
        self.notebook = ttk.Notebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Вкладка Кликера
        self.clicker_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.clicker_frame, text="Авто-кликер")
        self.create_clicker_tab()

        # Вкладка Макросов
        self.macros_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.macros_frame, text="Макросы")
        self.create_macros_tab()

        # Статус бар
        self.status_var = tk.StringVar(value="Готов")
        self.status_bar = ttk.Label(main_container, textvariable=self.status_var,
                                    relief=tk.SUNKEN, anchor=tk.W,
                                    background='#252525', foreground='#aaaaaa')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))

        # Горячие клавиши
        hotkeys_frame = ttk.Frame(main_container)
        hotkeys_frame.pack(fill=tk.X, pady=(5, 0))

        hotkeys_label = ttk.Label(hotkeys_frame,
                                  text="Горячие клавиши: F5 - Старт, F6 - Стоп, F7 - Координаты, F8 - Запись, F9 - Стоп записи, F10 - Воспроизвести/Стоп",
                                  font=('Segoe UI', 8), foreground='#888888')
        hotkeys_label.pack(side=tk.LEFT)

        # Привязка событий
        self.notebook.bind("<<NotebookTabChanged>>", self.tab_changed)

    def create_clicker_tab(self):
        # Основной фрейм с адаптивностью
        main_frame = ttk.Frame(self.clicker_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Контейнер для настроек
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Верхняя панель - Режим работы
        mode_frame = ttk.LabelFrame(settings_frame, text="Режим работы")
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        self.operation_mode = tk.StringVar(value="both")
        ttk.Radiobutton(mode_frame, text="Только мышь", variable=self.operation_mode,
                        value="mouse").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="Только клавиатура", variable=self.operation_mode,
                        value="keyboard").pack(side=tk.LEFT, padx=10, pady=5)
        ttk.Radiobutton(mode_frame, text="Мышь и клавиатура", variable=self.operation_mode,
                        value="both").pack(side=tk.LEFT, padx=10, pady=5)

        # Средняя панель - Настройки
        middle_frame = ttk.Frame(settings_frame)
        middle_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель - Настройки мыши
        mouse_frame = ttk.LabelFrame(middle_frame, text="Настройки мыши")
        mouse_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Тип клика
        click_type_frame = ttk.Frame(mouse_frame)
        click_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(click_type_frame, text="Тип клика:").pack(side=tk.LEFT)
        self.click_type = tk.StringVar(value="left")
        ttk.Radiobutton(click_type_frame, text="Левый", variable=self.click_type, value="left").pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Radiobutton(click_type_frame, text="Правый", variable=self.click_type, value="right").pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Radiobutton(click_type_frame, text="Двойной", variable=self.click_type, value="double").pack(side=tk.LEFT,
                                                                                                         padx=5)

        # Позиция клика
        position_frame = ttk.Frame(mouse_frame)
        position_frame.pack(fill=tk.X, pady=5)
        ttk.Label(position_frame, text="Позиция:").pack(side=tk.LEFT)
        self.position_var = tk.StringVar(value="current")
        ttk.Radiobutton(position_frame, text="Текущая", variable=self.position_var, value="current").pack(side=tk.LEFT,
                                                                                                          padx=5)
        ttk.Radiobutton(position_frame, text="Заданная", variable=self.position_var, value="fixed").pack(side=tk.LEFT,
                                                                                                         padx=5)

        # Координаты
        coords_frame = ttk.Frame(mouse_frame)
        coords_frame.pack(fill=tk.X, pady=5)
        ttk.Label(coords_frame, text="X:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar(value="0")
        ttk.Entry(coords_frame, textvariable=self.x_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Label(coords_frame, text="Y:").pack(side=tk.LEFT)
        self.y_var = tk.StringVar(value="0")
        ttk.Entry(coords_frame, textvariable=self.y_var, width=8).pack(side=tk.LEFT, padx=5)
        ttk.Button(coords_frame, text="Получить (F7)", command=self.get_current_position).pack(side=tk.RIGHT)

        # Интервал для мыши
        interval_frame = ttk.Frame(mouse_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(interval_frame, text="Интервал кликов (сек):").pack(side=tk.LEFT)
        self.mouse_interval_var = tk.StringVar(value="1.0")
        ttk.Entry(interval_frame, textvariable=self.mouse_interval_var, width=8).pack(side=tk.LEFT, padx=5)

        # Правая панель - Настройки клавиатуры
        keyboard_frame = ttk.LabelFrame(middle_frame, text="Настройки клавиатуры")
        keyboard_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # Клавиша
        key_frame = ttk.Frame(keyboard_frame)
        key_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_frame, text="Клавиша:").pack(side=tk.LEFT)
        self.key_var = tk.StringVar(value="a")
        key_entry = ttk.Entry(key_frame, textvariable=self.key_var, width=15)
        key_entry.pack(side=tk.LEFT, padx=5)

        # Тип нажатия
        press_type_frame = ttk.Frame(keyboard_frame)
        press_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(press_type_frame, text="Тип нажатия:").pack(side=tk.LEFT)
        self.press_type_var = tk.StringVar(value="press")
        ttk.Radiobutton(press_type_frame, text="Нажать", variable=self.press_type_var, value="press").pack(side=tk.LEFT,
                                                                                                           padx=5)
        ttk.Radiobutton(press_type_frame, text="Зажать", variable=self.press_type_var, value="down").pack(side=tk.LEFT,
                                                                                                          padx=5)
        ttk.Radiobutton(press_type_frame, text="Отпустить", variable=self.press_type_var, value="up").pack(side=tk.LEFT,
                                                                                                           padx=5)

        # Интервал для клавиатуры
        key_interval_frame = ttk.Frame(keyboard_frame)
        key_interval_frame.pack(fill=tk.X, pady=5)
        ttk.Label(key_interval_frame, text="Интервал нажатий (сек):").pack(side=tk.LEFT)
        self.key_interval_var = tk.StringVar(value="1.0")
        ttk.Entry(key_interval_frame, textvariable=self.key_interval_var, width=8).pack(side=tk.LEFT, padx=5)

        # Нижняя панель - Общие настройки
        common_frame = ttk.LabelFrame(settings_frame, text="Общие настройки")
        common_frame.pack(fill=tk.X, pady=10)

        # Режим работы
        mode_frame = ttk.Frame(common_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mode_frame, text="Режим:").pack(side=tk.LEFT)
        self.mode_var = tk.StringVar(value="infinite")
        ttk.Radiobutton(mode_frame, text="Бесконечно", variable=self.mode_var, value="infinite").pack(side=tk.LEFT,
                                                                                                      padx=5)
        ttk.Radiobutton(mode_frame, text="По времени", variable=self.mode_var, value="time").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="По действиям", variable=self.mode_var, value="actions").pack(side=tk.LEFT,
                                                                                                       padx=5)

        # Параметры режима
        params_frame = ttk.Frame(common_frame)
        params_frame.pack(fill=tk.X, pady=5)
        ttk.Label(params_frame, text="Длительность (сек):").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="10")
        self.duration_entry = ttk.Entry(params_frame, textvariable=self.duration_var, width=8, state='disabled')
        self.duration_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(params_frame, text="Количество действий:").pack(side=tk.LEFT, padx=(20, 0))
        self.actions_var = tk.StringVar(value="10")
        self.actions_entry = ttk.Entry(params_frame, textvariable=self.actions_var, width=8, state='disabled')
        self.actions_entry.pack(side=tk.LEFT, padx=5)

        # Обработчики изменения режима
        self.mode_var.trace_add('write', self.update_mode_fields)

        # Кнопки управления
        btn_frame = ttk.Frame(settings_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="▶ Старт (F5)", style='Start.TButton', command=self.start_actions)
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=(0, 5))

        self.stop_btn = ttk.Button(btn_frame, text="⏹ Стоп (F6)", style='Stop.TButton',
                                   state=tk.DISABLED, command=self.stop_operation)
        self.stop_btn.pack(side=tk.RIGHT, expand=True, padx=(5, 0))

        # Визуальный индикатор
        self.canvas = tk.Canvas(btn_frame, width=40, height=40, bg='#1e1e1e', highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, padx=10)
        self.indicator = self.canvas.create_oval(10, 10, 30, 30, fill='red')

        # Информация
        ttk.Label(settings_frame, text="Переместите курсор в нужную позицию перед запуском",
                  foreground="#666666", font=('Segoe UI', 8), anchor=tk.CENTER).pack(pady=(10, 0))

    def create_macros_tab(self):
        # Основной фрейм с адаптивностью
        main_frame = ttk.Frame(self.macros_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Контейнер для настроек
        settings_frame = ttk.Frame(main_frame)
        settings_frame.pack(fill=tk.BOTH, expand=True)

        # Левая панель - Управление макросами
        control_frame = ttk.LabelFrame(settings_frame, text="Управление макросами")
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10), pady=5)

        # Настройки воспроизведения макроса
        playback_frame = ttk.LabelFrame(control_frame, text="Настройки воспроизведения")
        playback_frame.pack(fill=tk.X, pady=(0, 10))

        # Режим работы макроса
        mode_frame = ttk.Frame(playback_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mode_frame, text="Режим:").pack(side=tk.LEFT)
        self.macro_mode = tk.StringVar(value="once")
        ttk.Radiobutton(mode_frame, text="1 раз", variable=self.macro_mode, value="once").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="По времени", variable=self.macro_mode, value="time").pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Radiobutton(mode_frame, text="По циклам", variable=self.macro_mode, value="cycles").pack(side=tk.LEFT,
                                                                                                     padx=5)
        ttk.Radiobutton(mode_frame, text="Бесконечно", variable=self.macro_mode, value="infinite").pack(side=tk.LEFT,
                                                                                                        padx=5)

        # Параметры режима
        params_frame = ttk.Frame(playback_frame)
        params_frame.pack(fill=tk.X, pady=5)
        ttk.Label(params_frame, text="Длительность (сек):").pack(side=tk.LEFT)
        self.macro_duration_var = tk.StringVar(value="10")
        self.macro_duration_entry = ttk.Entry(params_frame, textvariable=self.macro_duration_var, width=8,
                                              state='disabled')
        self.macro_duration_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(params_frame, text="Циклы:").pack(side=tk.LEFT, padx=(20, 0))
        self.macro_cycles_var = tk.StringVar(value="5")
        self.macro_cycles_entry = ttk.Entry(params_frame, textvariable=self.macro_cycles_var, width=8, state='disabled')
        self.macro_cycles_entry.pack(side=tk.LEFT, padx=5)

        # Обработчики изменения режима
        self.macro_mode.trace_add('write', self.update_macro_mode)

        # Кнопки управления
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        self.record_btn = ttk.Button(btn_frame, text="● Начать запись (F8)", style='Record.TButton',
                                     command=self.start_recording)
        self.record_btn.pack(fill=tk.X, pady=2)

        self.stop_record_btn = ttk.Button(btn_frame, text="■ Остановить запись (F9)", style='Record.TButton',
                                          command=self.stop_recording, state=tk.DISABLED)
        self.stop_record_btn.pack(fill=tk.X, pady=2)

        self.play_btn = ttk.Button(btn_frame, text="▶ Воспроизвести (F10)", style='Macro.TButton',
                                   command=self.play_macro)
        self.play_btn.pack(fill=tk.X, pady=2)

        # НОВАЯ КНОПКА: Закончить воспроизведение
        self.stop_play_btn = ttk.Button(btn_frame, text="■ Закончить воспроизведение (F10)",
                                        style='Record.TButton', command=self.stop_macro_playback,
                                        state=tk.DISABLED)
        self.stop_play_btn.pack(fill=tk.X, pady=2)

        # Список макросов
        macro_frame = ttk.LabelFrame(control_frame, text="Сохраненные макросы")
        macro_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.macro_listbox = tk.Listbox(macro_frame, bg='#252525', fg='white',
                                        selectbackground='#4a9cff', selectforeground='white',
                                        borderwidth=0, highlightthickness=0)
        self.macro_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.macro_listbox.bind('<<ListboxSelect>>', self.on_macro_select)

        # Загрузить сохраненные макросы
        self.update_macro_list()

        # Кнопки управления макросами
        macro_btn_frame = ttk.Frame(macro_frame)
        macro_btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(macro_btn_frame, text="Сохранить", command=self.save_macro).pack(side=tk.LEFT, fill=tk.X,
                                                                                    expand=True, padx=(0, 2))
        ttk.Button(macro_btn_frame, text="Удалить", command=self.delete_macro).pack(side=tk.RIGHT, fill=tk.X,
                                                                                    expand=True, padx=(2, 0))

        # Правая панель - Лог макросов
        log_frame = ttk.LabelFrame(settings_frame, text="Запись макроса")
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)

        self.log_text = tk.Text(log_frame, bg='#252525', fg='white',
                                insertbackground='white', borderwidth=0,
                                font=('Consolas', 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.log_text.config(state=tk.DISABLED)

        scrollbar = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

        # Информация
        ttk.Label(settings_frame, text="Записывайте клики и нажатия клавиш для создания макросов",
                  foreground="#666666", font=('Segoe UI', 8), anchor=tk.CENTER).pack(side=tk.BOTTOM, fill=tk.X,
                                                                                     pady=(10, 0))

    # Новый метод: переключение воспроизведения/остановки макроса
    def toggle_macro_playback(self):
        if self.macro_playing:
            self.stop_macro_playback()
        else:
            self.play_macro()

    # Новый метод: остановка воспроизведения макроса
    def stop_macro_playback(self):
        if self.macro_playing:
            self.macro_playing = False
            self.status_var.set("Воспроизведение макроса остановлено")
            self.play_btn.config(state=tk.NORMAL)
            self.stop_play_btn.config(state=tk.DISABLED)
            self.play_sound('stop')

    def update_macro_mode(self, *args):
        mode = self.macro_mode.get()
        if mode == "time":
            self.macro_duration_entry.config(state='normal')
            self.macro_cycles_entry.config(state='disabled')
        elif mode == "cycles":
            self.macro_duration_entry.config(state='disabled')
            self.macro_cycles_entry.config(state='normal')
        else:
            self.macro_duration_entry.config(state='disabled')
            self.macro_cycles_entry.config(state='disabled')

    def update_mode_fields(self, *args):
        mode = self.mode_var.get()
        if mode == "time":
            self.duration_entry.config(state='normal')
            self.actions_entry.config(state='disabled')
        elif mode == "actions":
            self.duration_entry.config(state='disabled')
            self.actions_entry.config(state='normal')
        else:
            self.duration_entry.config(state='disabled')
            self.actions_entry.config(state='disabled')

    def get_current_position(self):
        x, y = pyautogui.position()
        self.x_var.set(str(x))
        self.y_var.set(str(y))
        self.status_var.set(f"Получены координаты: X={x}, Y={y}")
        self.play_sound('info')

    def tab_changed(self, event):
        self.current_tab = self.notebook.tab(self.notebook.select(), "text").lower()
        self.status_var.set(f"Активная вкладка: {self.current_tab}")

    def start_operation(self):
        if self.current_tab == "авто-кликер":
            self.start_actions()
        elif self.current_tab == "макросы":
            self.play_macro()

    def start_actions(self):
        # Проверка режима работы
        operation_mode = self.operation_mode.get()
        if operation_mode not in ["mouse", "keyboard", "both"]:
            messagebox.showerror("Ошибка", "Выберите режим работы")
            return

        # Проверка настроек мыши
        if operation_mode in ["mouse", "both"] and self.position_var.get() == "fixed":
            try:
                x = int(self.x_var.get())
                y = int(self.y_var.get())
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректные координаты")
                return

        # Проверка интервалов
        try:
            mouse_interval = float(self.mouse_interval_var.get()) if operation_mode in ["mouse", "both"] else 0
            key_interval = float(self.key_interval_var.get()) if operation_mode in ["keyboard", "both"] else 0

            if (operation_mode in ["mouse", "both"] and mouse_interval <= 0) or \
                    (operation_mode in ["keyboard", "both"] and key_interval <= 0):
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные интервалы (числа > 0)")
            return

        # Проверка режима
        mode = self.mode_var.get()
        duration = 0
        actions = 0

        if mode == "time":
            try:
                duration = float(self.duration_var.get())
                if duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректную длительность (число > 0)")
                return

        if mode == "actions":
            try:
                actions = int(self.actions_var.get())
                if actions <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Ошибка", "Введите корректное количество действий (целое число > 0)")
                return

        # Запускаем действия
        self.clicking = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_var.set("Выполнение действий...")
        self.canvas.itemconfig(self.indicator, fill='green')

        # Запускаем поток для одновременного управления мышью и клавиатурой
        self.action_thread = threading.Thread(
            target=self.execute_actions,
            args=(operation_mode, mouse_interval, key_interval, mode, duration, actions),
            daemon=True
        )
        self.action_thread.start()
        self.play_sound('start')

    def execute_actions(self, operation_mode, mouse_interval, key_interval, mode, duration, actions):
        start_time = time.time()
        action_count = 0

        # Инициализация таймеров
        last_mouse_time = time.time() if operation_mode in ["mouse", "both"] else 0
        last_key_time = time.time() if operation_mode in ["keyboard", "both"] else 0

        while self.clicking:
            current_time = time.time()

            # Проверка условий остановки
            if mode == "time" and (current_time - start_time) > duration:
                break

            if mode == "actions" and action_count >= actions:
                break

            # Выполнение действия мыши
            if operation_mode in ["mouse", "both"] and current_time - last_mouse_time >= mouse_interval:
                try:
                    if self.position_var.get() == "fixed":
                        x = int(self.x_var.get())
                        y = int(self.y_var.get())
                        pyautogui.moveTo(x, y)

                    click_type = self.click_type.get()
                    if click_type == "double":
                        pyautogui.doubleClick()
                    else:
                        pyautogui.click(button=click_type)

                    action_count += 1
                    self.status_var.set(f"Действий: {action_count} | Режим: {mode}")

                except Exception as e:
                    print(f"Ошибка мыши: {e}")

                last_mouse_time = current_time

            # Выполнение действия клавиатуры
            if operation_mode in ["keyboard", "both"] and current_time - last_key_time >= key_interval:
                key = self.key_var.get().strip()
                if key:
                    try:
                        press_type = self.press_type_var.get()
                        if press_type == "press":
                            keyboard.press_and_release(key)
                        elif press_type == "down":
                            keyboard.press(key)
                        elif press_type == "up":
                            keyboard.release(key)

                        action_count += 1
                        self.status_var.set(f"Действий: {action_count} | Режим: {mode}")

                    except Exception as e:
                        print(f"Ошибка клавиатуры: {e}")

                last_key_time = current_time

            # Небольшая задержка для снижения нагрузки на CPU
            time.sleep(0.01)

        self.stop_operation()

    def on_mouse_click(self, x, y, button, pressed):
        if not self.recording:
            return

        button_name = ""
        if button == mouse.Button.left:
            button_name = "left"
        elif button == mouse.Button.right:
            button_name = "right"
        elif button == mouse.Button.middle:
            button_name = "middle"

        action_type = "down" if pressed else "up"

        action = {
            'type': 'mouse',
            'action': action_type,
            'button': button_name,
            'x': x,
            'y': y,
            'time': time.time()
        }

        self.macro_actions.append(action)

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"Мышь: {button_name} {action_type} в ({x}, {y})\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_key_press(self, key):
        if not self.recording:
            return

        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).split('.')[-1]

        action = {
            'type': 'keyboard',
            'action': 'down',
            'key': key_name,
            'time': time.time()
        }

        self.macro_actions.append(action)

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"Клавиша: {key_name} down\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_key_release(self, key):
        if not self.recording:
            return

        try:
            key_name = key.char
        except AttributeError:
            key_name = str(key).split('.')[-1]

        # Не записываем отпускание обычных клавиш, чтобы не загромождать
        if len(key_name) > 1:  # Специальные клавиши (ctrl, shift и т.д.)
            action = {
                'type': 'keyboard',
                'action': 'up',
                'key': key_name,
                'time': time.time()
            }

            self.macro_actions.append(action)

            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"Клавиша: {key_name} up\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

    def start_recording(self):
        self.recording = True
        self.macro_actions = []
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.insert(tk.END, "Начата запись макроса...\n")
        self.log_text.config(state=tk.DISABLED)
        self.status_var.set("Запись макроса начата...")
        self.record_btn.config(state=tk.DISABLED)
        self.stop_record_btn.config(state=tk.NORMAL)

        # Запускаем слушатели событий
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.keyboard_listener = kb_listener.Listener(on_press=self.on_key_press, on_release=self.on_key_release)

        self.mouse_listener.start()
        self.keyboard_listener.start()

        self.play_sound('record')

    def stop_recording(self):
        self.recording = False

        if self.mouse_listener:
            self.mouse_listener.stop()
        if self.keyboard_listener:
            self.keyboard_listener.stop()

        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, "Запись макроса остановлена\n")
        self.log_text.config(state=tk.DISABLED)
        self.status_var.set(f"Запись завершена. Действий: {len(self.macro_actions)}")
        self.record_btn.config(state=tk.NORMAL)
        self.stop_record_btn.config(state=tk.DISABLED)
        self.play_sound('stop')

    def on_macro_select(self, event):
        selection = self.macro_listbox.curselection()
        if selection:
            macro_name = self.macro_listbox.get(selection[0]).split(' (')[0]
            self.selected_macro = macro_name
            self.status_var.set(f"Выбран макрос: {macro_name}")

    def play_macro(self):
        actions = []
        macro_name = ""

        # Определяем, какой макрос воспроизводить
        if self.selected_macro and self.selected_macro in self.macros:
            actions = self.macros[self.selected_macro]
            macro_name = self.selected_macro
        elif self.macro_actions:
            actions = self.macro_actions
            macro_name = "Последний записанный"
        else:
            messagebox.showinfo("Информация", "Нет макроса для воспроизведения")
            return

        if not actions:
            messagebox.showinfo("Информация", "Макрос пуст")
            return

        # Получаем настройки воспроизведения
        mode = self.macro_mode.get()
        duration = float(self.macro_duration_var.get()) if mode == "time" else 0
        cycles = int(self.macro_cycles_var.get()) if mode == "cycles" else 1

        self.clicking = True
        self.macro_playing = True  # Устанавливаем флаг воспроизведения
        self.status_var.set(f"Воспроизведение макроса: {macro_name}...")
        self.play_btn.config(state=tk.DISABLED)
        self.stop_play_btn.config(state=tk.NORMAL)  # Активируем кнопку остановки

        # Запускаем поток воспроизведения
        self.macro_thread = threading.Thread(
            target=self.play_macro_loop,
            args=(actions, mode, duration, cycles),
            daemon=True
        )
        self.macro_thread.start()
        self.play_sound('start')

    def play_macro_loop(self, actions, mode, duration, cycles):
        start_time = time.time()
        cycle_count = 0

        while self.clicking and self.macro_playing:  # Проверяем оба флага
            if mode == "once":
                # Воспроизводим один раз
                self.play_recorded_actions(actions)
                break
            elif mode == "time":
                # Проверяем время
                if time.time() - start_time > duration:
                    break
                self.play_recorded_actions(actions)
            elif mode == "cycles":
                # Проверяем количество циклов
                if cycle_count >= cycles:
                    break
                self.play_recorded_actions(actions)
                cycle_count += 1
            else:  # Бесконечный режим
                self.play_recorded_actions(actions)

        self.stop_macro_playback()  # Используем новую функцию остановки
        self.play_btn.config(state=tk.NORMAL)

    def play_recorded_actions(self, actions):
        if not actions:
            return

        # Первое действие - время начала
        start_time = actions[0]['time']

        for i, action in enumerate(actions):
            if not self.clicking or not self.macro_playing:  # Проверяем флаги
                break

            # Рассчитываем задержку
            if i > 0:
                delay = action['time'] - actions[i - 1]['time']
                if delay > 0:
                    time.sleep(delay)

            # Воспроизводим действие
            try:
                if action['type'] == 'mouse':
                    pyautogui.moveTo(action['x'], action['y'])

                    if action['action'] == 'down':
                        if action['button'] == 'left':
                            pyautogui.mouseDown(button='left')
                        elif action['button'] == 'right':
                            pyautogui.mouseDown(button='right')
                        elif action['button'] == 'middle':
                            pyautogui.mouseDown(button='middle')
                    elif action['action'] == 'up':
                        if action['button'] == 'left':
                            pyautogui.mouseUp(button='left')
                        elif action['button'] == 'right':
                            pyautogui.mouseUp(button='right')
                        elif action['button'] == 'middle':
                            pyautogui.mouseUp(button='middle')

                elif action['type'] == 'keyboard':
                    if action['action'] == 'down':
                        keyboard.press(action['key'])
                    elif action['action'] == 'up':
                        keyboard.release(action['key'])

            except Exception as e:
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, f"Ошибка воспроизведения: {str(e)}\n")
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)

    def save_macro(self):
        if not self.macro_actions:
            messagebox.showinfo("Информация", "Нет действий для сохранения")
            return

        macro_name = simpledialog.askstring("Сохранение макроса", "Введите имя макроса:")
        if macro_name:
            self.macros[macro_name] = self.macro_actions.copy()
            self.save_macros()
            self.update_macro_list()
            self.selected_macro = macro_name
            self.status_var.set(f"Макрос '{macro_name}' сохранен")
            self.play_sound('save')

    def delete_macro(self):
        if not self.selected_macro:
            messagebox.showinfo("Информация", "Выберите макрос для удаления")
            return

        if messagebox.askyesno("Подтверждение", f"Удалить макрос '{self.selected_macro}'?"):
            if self.selected_macro in self.macros:
                del self.macros[self.selected_macro]
                self.save_macros()
                self.update_macro_list()
                self.selected_macro = None
                self.status_var.set(f"Макрос удален")
                self.play_sound('delete')

    def update_macro_list(self):
        self.macro_listbox.delete(0, tk.END)
        for name in self.macros:
            action_count = len(self.macros[name])
            self.macro_listbox.insert(tk.END, f"{name} ({action_count} действий)")

    def load_macros(self):
        try:
            if os.path.exists("macros.json"):
                with open("macros.json", "r") as f:
                    self.macros = json.load(f)
        except:
            pass

    def save_macros(self):
        try:
            with open("macros.json", "w") as f:
                json.dump(self.macros, f)
        except:
            pass

    def stop_operation(self):
        self.clicking = False
        self.recording = False
        self.macro_playing = False  # Останавливаем воспроизведение макроса
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.play_btn.config(state=tk.NORMAL)
        self.stop_play_btn.config(state=tk.DISABLED)  # Деактивируем кнопку остановки
        self.status_var.set("Операция остановлена")
        self.canvas.itemconfig(self.indicator, fill='red')
        self.play_sound('stop')

    def play_sound(self, sound_type):
        try:
            if sound_type == 'start':
                winsound.Beep(800, 200)
            elif sound_type == 'stop':
                winsound.Beep(400, 200)
            elif sound_type == 'record':
                winsound.Beep(600, 300)
            elif sound_type == 'save':
                winsound.Beep(1200, 100)
                winsound.Beep(1000, 100)
            elif sound_type == 'delete':
                winsound.Beep(300, 300)
            elif sound_type == 'info':
                winsound.Beep(500, 100)
        except:
            pass

    def on_close(self):
        if self.clicking or self.recording or self.macro_playing:
            if messagebox.askyesno("Подтверждение", "Операция все еще выполняется! Вы уверены, что хотите выйти?"):
                self.clicking = False
                self.recording = False
                self.macro_playing = False
                time.sleep(0.5)
                self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = AdvancedAutoClicker(root)
    root.mainloop()