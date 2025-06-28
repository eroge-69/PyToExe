import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
import json
import os
from datetime import datetime

class VortexBrowser:
    def __init__(self, root):
        self.root = root
        self.search_engines = {
            "Google": "https://www.google.com/search?q={}",
            "DuckDuckGo": "https://duckduckgo.com/?q={}",
            "Bing": "https://www.bing.com/search?q={}",
            "Yandex": "https://yandex.ru/search/?text={}",
            "YouTube": "https://www.youtube.com/results?search_query={}",
            "GitHub": "https://github.com/search?q={}"
        }
        self.current_engine = "Google"
        self.config_dir = "VortexBrowserData"
        self.history_file = os.path.join(self.config_dir, "history.json")
        self.settings_file = os.path.join(self.config_dir, "settings.json")
        
        self.create_config_dir()
        self.load_settings()
        
        self.setup_window()
        self.create_menu()
        self.create_toolbar()
        self.create_main_interface()
        self.create_history_panel()
        self.create_statusbar()
        
        self.load_history()

    def create_config_dir(self):
        """Создает директорию для хранения данных приложения"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def setup_window(self):
        """Настройка основного окна"""
        self.root.title("Vortex Browser")
        self.root.geometry(self.settings.get("window_size", "1000x800"))
        self.root.minsize(800, 600)
        
        # Попытка установить иконку
        try:
            self.root.iconbitmap(default=os.path.join(self.config_dir, 'icon.ico'))
        except:
            pass
        
        # Стиль для элементов
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('TEntry', font=('Arial', 12), padding=5)
        style.configure('TFrame', background='#f5f5f5')
        style.configure('TLabel', background='#f5f5f5')
        style.configure('History.TFrame', background='#ffffff')
        style.configure('Status.TLabel', background='#e0e0e0', font=('Arial', 9))

    def create_menu(self):
        """Создает главное меню"""
        menubar = tk.Menu(self.root)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новое окно", command=self.new_window)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Настройки", command=self.show_settings)
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_toolbar(self):
        """Создает панель инструментов"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(fill='x', padx=5, pady=5)
        
        # Кнопки навигации
        nav_buttons = [
            ("Домой", self.go_home, "🏠"),
            ("Назад", self.go_back, "⬅"),
            ("Вперед", self.go_forward, "➡"),
            ("Обновить", self.refresh_search, "🔄")
        ]
        
        for text, command, emoji in nav_buttons:
            btn = ttk.Button(
                toolbar,
                text=f"{emoji} {text}",
                command=command
            )
            btn.pack(side='left', padx=2)
        
        # Разделитель
        ttk.Separator(toolbar, orient='vertical').pack(side='left', padx=5, fill='y')
        
        # Кнопка очистки истории
        clear_history_btn = ttk.Button(
            toolbar,
            text="🧹 Очистить историю",
            command=self.clear_history
        )
        clear_history_btn.pack(side='right', padx=2)

    def create_main_interface(self):
        """Создание основного интерфейса"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(expand=True, fill='both', padx=20, pady=10)

        # Заголовок
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(
            title_frame,
            text="Vortex Browser",
            font=("Arial", 24, "bold"),
            foreground="#333333"
        )
        title_label.pack(side='left')
        
        version_label = ttk.Label(
            title_frame,
            text="v1.0",
            font=("Arial", 10),
            foreground="#666666"
        )
        version_label.pack(side='right')

        # Фрейм для поиска
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill='x', pady=10)

        # Поле ввода с подсказкой
        self.search_entry = ttk.Entry(
            search_frame,
            width=50,
            font=("Arial", 12)
        )
        self.search_entry.pack(side='left', expand=True, fill='x', padx=(0, 10))
        self.set_placeholder()
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.set_placeholder)
        self.search_entry.focus()
        
        # Привязываем обработчик нажатия Enter
        self.search_entry.bind('<Return>', lambda event: self.perform_search())

        # Кнопка поиска
        search_btn = ttk.Button(
            search_frame,
            text="🔍 Поиск",
            command=self.perform_search
        )
        search_btn.pack(side='left')

        # Фрейм для выбора поисковика
        engine_frame = ttk.Frame(main_frame)
        engine_frame.pack(fill='x', pady=10)

        ttk.Label(
            engine_frame,
            text="Поисковик:",
            font=("Arial", 10)
        ).pack(side='left')

        # Выбор поисковой системы
        self.engine_var = tk.StringVar(value=self.current_engine)
        engine_menu = ttk.OptionMenu(
            engine_frame,
            self.engine_var,
            self.current_engine,
            *self.search_engines.keys()
        )
        engine_menu.pack(side='left', padx=10)

        # Кнопка очистки
        clear_btn = ttk.Button(
            engine_frame,
            text="Очистить",
            command=self.clear_search
        )
        clear_btn.pack(side='left')

    def create_history_panel(self):
        """Создает панель истории"""
        history_frame = ttk.Frame(self.root, style='History.TFrame')
        history_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))
        
        # Заголовок и кнопки управления историей
        header_frame = ttk.Frame(history_frame)
        header_frame.pack(fill='x')
        
        ttk.Label(
            header_frame,
            text="История поиска:",
            font=("Arial", 10)
        ).pack(side='left')
        
        ttk.Button(
            header_frame,
            text="Экспорт истории",
            command=self.export_history
        ).pack(side='right', padx=5)
        
        ttk.Button(
            header_frame,
            text="Импорт истории",
            command=self.import_history
        ).pack(side='right', padx=5)
        
        # Список истории
        self.history_listbox = tk.Listbox(
            history_frame,
            height=12,
            font=("Arial", 10),
            selectbackground="#e0e0e0",
            bg="white"
        )
        self.history_listbox.pack(fill='both', expand=True, pady=(5, 0))
        
        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(self.history_listbox)
        scrollbar.pack(side='right', fill='y')
        self.history_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.history_listbox.yview)
        
        # Контекстное меню для истории
        self.history_menu = tk.Menu(self.root, tearoff=0)
        self.history_menu.add_command(label="Повторить поиск", command=self.repeat_selected_search)
        self.history_menu.add_command(label="Удалить запись", command=self.delete_history_item)
        self.history_menu.add_separator()
        self.history_menu.add_command(label="Очистить историю", command=self.clear_history)
        
        self.history_listbox.bind("<Double-Button-1>", self.repeat_search)
        self.history_listbox.bind("<Button-3>", self.show_history_menu)

    def create_statusbar(self):
        """Создает статусбар"""
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        
        statusbar = ttk.Frame(self.root, style='Status.TFrame')
        statusbar.pack(fill='x', padx=0, pady=0)
        
        ttk.Label(
            statusbar,
            textvariable=self.status_var,
            style='Status.TLabel'
        ).pack(side='left', padx=10)
        
        ttk.Label(
            statusbar,
            text=f"Поисковик: {self.current_engine}",
            style='Status.TLabel'
        ).pack(side='right', padx=10)

    def perform_search(self):
        """Выполняет поиск"""
        query = self.search_entry.get().strip()
        if query and query != "Введите поисковый запрос...":
            engine = self.engine_var.get()
            self.current_engine = engine
            url = self.search_engines[engine].format(query)
            self.open_url(url)
            
            # Добавляем запрос в историю
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            history_item = f"{timestamp} | {engine}: {query}"
            
            if self.history_listbox.size() == 0 or self.history_listbox.get(0) != history_item:
                self.history_listbox.insert(0, history_item)
                self.save_history()
                
            self.status_var.set(f"Выполнен поиск: '{query}' в {engine}")
        else:
            self.status_var.set("Введите поисковый запрос!")
            self.search_entry.focus()

    def open_url(self, url):
        """Открывает URL в браузере по умолчанию"""
        webbrowser.open(url)

    def clear_search(self):
        """Очищает поле поиска"""
        self.search_entry.delete(0, tk.END)
        self.set_placeholder()
        self.status_var.set("Готов к поиску")

    def clear_placeholder(self, event=None):
        """Удаляет подсказку при фокусе"""
        if self.search_entry.get() == "Введите поисковый запрос...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(foreground="black")

    def set_placeholder(self, event=None):
        """Устанавливает подсказку при потере фокуса"""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Введите поисковый запрос...")
            self.search_entry.config(foreground="gray")

    def go_home(self):
        """Домашняя страница"""
        self.clear_search()
        self.engine_var.set("Google")
        self.status_var.set("Готов к поиску")

    def go_back(self):
        """Навигация назад"""
        self.status_var.set("Функция 'Назад' в разработке")

    def go_forward(self):
        """Навигация вперед"""
        self.status_var.set("Функция 'Вперед' в разработке")

    def refresh_search(self):
        """Обновляет текущий поиск"""
        if self.search_entry.get() and self.search_entry.get() != "Введите поисковый запрос...":
            self.perform_search()

    def repeat_search(self, event):
        """Повторяет поиск из истории"""
        self.repeat_selected_search()

    def repeat_selected_search(self):
        """Повторяет выбранный поиск из истории"""
        selection = self.history_listbox.curselection()
        if selection:
            selected_item = self.history_listbox.get(selection[0])
            # Извлекаем поисковик и запрос из строки истории
            parts = selected_item.split(" | ")[1].split(": ", 1)
            if len(parts) == 2:
                engine, query = parts
                if engine in self.search_engines:
                    self.engine_var.set(engine)
                    self.search_entry.delete(0, tk.END)
                    self.search_entry.insert(0, query)
                    self.search_entry.config(foreground="black")
                    self.perform_search()

    def show_history_menu(self, event):
        """Показывает контекстное меню для истории"""
        try:
            self.history_listbox.selection_clear(0, tk.END)
            self.history_listbox.selection_set(self.history_listbox.nearest(event.y))
            self.history_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.history_menu.grab_release()

    def delete_history_item(self):
        """Удаляет выбранный элемент истории"""
        selection = self.history_listbox.curselection()
        if selection:
            self.history_listbox.delete(selection[0])
            self.save_history()

    def clear_history(self):
        """Очищает историю поиска"""
        if messagebox.askyesno(
            "Очистка истории",
            "Вы уверены, что хотите полностью очистить историю поиска?",
            parent=self.root
        ):
            self.history_listbox.delete(0, tk.END)
            self.save_history()

    def export_history(self):
        """Экспортирует историю в файл"""
        file_path = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Экспорт истории"
        )
        if file_path:
            history = [self.history_listbox.get(i) for i in range(self.history_listbox.size())]
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, ensure_ascii=False, indent=2)
                self.status_var.set(f"История экспортирована в {file_path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось экспортировать историю: {e}")

    def import_history(self):
        """Импортирует историю из файла"""
        file_path = tk.filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Импорт истории"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                
                if isinstance(history, list):
                    self.history_listbox.delete(0, tk.END)
                    for item in history:
                        self.history_listbox.insert(tk.END, item)
                    self.save_history()
                    self.status_var.set(f"Успешно импортировано {len(history)} записей")
                else:
                    messagebox.showerror("Ошибка", "Неправильный формат файла истории")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось импортировать историю: {e}")

    def show_settings(self):
        """Показывает окно настроек"""
        settings_win = tk.Toplevel(self.root)
        settings_win.title("Настройки")
        settings_win.geometry("400x300")
        
        ttk.Label(
            settings_win,
            text="Настройки Vortex Browser",
            font=("Arial", 14)
        ).pack(pady=10)
        
        # Выбор поисковика по умолчанию
        ttk.Label(
            settings_win,
            text="Поисковик по умолчанию:",
            font=("Arial", 10)
        ).pack(anchor='w', padx=20, pady=(10, 0))
        
        default_engine = ttk.Combobox(
            settings_win,
            values=list(self.search_engines.keys()),
            font=("Arial", 10)
        )
        default_engine.set(self.settings.get("default_engine", "Google"))
        default_engine.pack(fill='x', padx=20, pady=5)
        
        # Кнопки сохранения/отмены
        btn_frame = ttk.Frame(settings_win)
        btn_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Button(
            btn_frame,
            text="Сохранить",
            command=lambda: self.save_settings({
                "default_engine": default_engine.get(),
                "window_size": self.settings.get("window_size", "1000x800")
            }, settings_win)
        ).pack(side='right', padx=5)
        
        ttk.Button(
            btn_frame,
            text="Отмена",
            command=settings_win.destroy
        ).pack(side='right', padx=5)

    def show_about(self):
        """Показывает окно 'О программе'"""
        about_win = tk.Toplevel(self.root)
        about_win.title("О программе Vortex Browser")
        about_win.geometry("400x300")
        
        ttk.Label(
            about_win,
            text="Vortex Browser",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        ttk.Label(
            about_win,
            text="Версия 1.0",
            font=("Arial", 12)
        ).pack()
        
        ttk.Label(
            about_win,
            text="\nПростой и удобный браузер с возможностью\n"
                 "поиска в различных поисковых системах\n",
            font=("Arial", 10)
        ).pack()
        
        ttk.Label(
            about_win,
            text="© 2023 Vortex Browser Team",
            font=("Arial", 9)
        ).pack(side='bottom', pady=10)

    def new_window(self):
        """Открывает новое окно браузера"""
        new_root = tk.Toplevel(self.root)
        app = VortexBrowser(new_root)

    def load_settings(self):
        """Загружает настройки из файла"""
        self.settings = {
            "default_engine": "Google",
            "window_size": "1000x800"
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings.update(json.load(f))
                self.current_engine = self.settings["default_engine"]
            except Exception as e:
                print(f"Ошибка загрузки настроек: {e}")

    def save_settings(self, settings, window):
        """Сохраняет настройки в файл"""
        self.settings.update(settings)
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            
            self.current_engine = settings["default_engine"]
            self.engine_var.set(self.current_engine)
            window.destroy()
            self.status_var.set("Настройки сохранены")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")

    def load_history(self):
        """Загружает историю из файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    for item in reversed(history):
                        self.history_listbox.insert(0, item)
            except Exception as e:
                print(f"Ошибка загрузки истории: {e}")

    def save_history(self):
        """Сохраняет историю в файл"""
        history = [self.history_listbox.get(i) for i in range(self.history_listbox.size())]
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ошибка сохранения истории: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VortexBrowser(root)
    root.mainloop()