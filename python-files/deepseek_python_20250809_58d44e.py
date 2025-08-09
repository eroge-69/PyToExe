import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
import re

class CodeEditor:
    def __init__(self, root):
        self.root = root
        self.current_file = None
        self.file_type = None  # 'python' или 'html'
        self.dark_mode = False
        self.setup_ui()
        self.bind_shortcuts()
        
    def setup_ui(self):
        """Настройка интерфейса"""
        self.root.title("Редактор кода (Python/HTML)")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        self.setup_styles()
        self.setup_main_layout()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_text_area()
        self.setup_statusbar()
        self.setup_right_panel()
        
        # Начальное содержимое
        self.insert_initial_content()
        self.update_line_numbers()

    def setup_styles(self):
        """Настройка стилей"""
        style = ttk.Style()
        try:
            style.theme_use('clam')
        except:
            pass
        
        # Цвета для темной темы
        style.configure('Dark.TFrame', background='#2d2d2d')
        style.configure('Dark.TLabel', background='#2d2d2d', foreground='white')
        style.configure('Dark.TButton', background='#3c3c3c', foreground='white')
        
    def setup_main_layout(self):
        """Основная разметка окна"""
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        
        # Главный контейнер
        self.main_pane = ttk.Frame(self.root, padding=6)
        self.main_pane.grid(row=1, column=0, sticky="nsew")
        self.main_pane.rowconfigure(0, weight=1)
        self.main_pane.columnconfigure(1, weight=1)
    
    def setup_menu(self):
        """Создание меню приложения"""
        menubar = tk.Menu(self.root)
        
        # Меню Файл
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый Python", command=self.new_python_file, accelerator="Ctrl+Shift+N")
        file_menu.add_command(label="Новый HTML", command=self.new_html_file, accelerator="Ctrl+Shift+H")
        file_menu.add_command(label="Открыть...", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Сохранить", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Сохранить как...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.confirm_exit)
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню Правка
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Отменить", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Повторить", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Вырезать", command=self.cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Копировать", command=self.copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Вставить", command=self.paste, accelerator="Ctrl+V")
        edit_menu.add_separator()
        edit_menu.add_command(label="Выделить все", command=self.select_all, accelerator="Ctrl+A")
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        # Меню Вид
        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Темная тема", command=self.toggle_theme)
        menubar.add_cascade(label="Вид", menu=view_menu)
        
        # Меню Справка
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="О программе", command=self.show_about)
        menubar.add_cascade(label="Справка", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def setup_toolbar(self):
        """Панель инструментов"""
        self.toolbar = ttk.Frame(self.root, padding=(4, 2))
        self.toolbar.grid(row=0, column=0, sticky="ew")
        
        # Кнопки
        buttons = [
            ("Новый Python", self.new_python_file),
            ("Новый HTML", self.new_html_file),
            ("Открыть", self.open_file),
            ("Сохранить", self.save_file),
            ("Отменить", self.undo),
            ("Повторить", self.redo),
            ("Вырезать", self.cut),
            ("Копировать", self.copy),
            ("Вставить", self.paste),
        ]
        
        for i, (text, cmd) in enumerate(buttons):
            btn = ttk.Button(self.toolbar, text=text, command=cmd)
            btn.grid(row=0, column=i, padx=2)
    
    def setup_text_area(self):
        """Настройка текстовой области с нумерацией строк"""
        # Основной контейнер
        text_container = ttk.Frame(self.main_pane)
        text_container.grid(row=0, column=1, sticky="nsew")
        text_container.rowconfigure(0, weight=1)
        text_container.columnconfigure(1, weight=1)
        
        # Нумерация строк
        self.line_numbers = tk.Text(
            text_container,
            width=4,
            padx=4,
            pady=4,
            state='disabled',
            takefocus=0,
            wrap='none',
            font=('Consolas', 12),
            background='#f0f0f0',
            foreground='#666666'
        )
        self.line_numbers.grid(row=0, column=0, sticky="ns")
        
        # Текстовый редактор
        self.text_editor = tk.Text(
            text_container,
            wrap="none",
            undo=True,
            font=('Consolas', 12),
            tabs=4,
            insertbackground='black'
        )
        self.text_editor.grid(row=0, column=1, sticky="nsew")
        
        # Скроллбары
        y_scroll = ttk.Scrollbar(text_container, command=self.on_scroll)
        y_scroll.grid(row=0, column=2, sticky="ns")
        
        x_scroll = ttk.Scrollbar(text_container, orient="horizontal", command=self.text_editor.xview)
        x_scroll.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.text_editor.configure(
            yscrollcommand=self.update_scroll,
            xscrollcommand=x_scroll.set
        )
        
        # Привязка событий
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        self.text_editor.bind('<ButtonRelease>', self.on_text_change)
    
    def on_scroll(self, *args):
        """Обработка скролла"""
        self.text_editor.yview(*args)
        self.line_numbers.yview(*args)
    
    def update_scroll(self, *args):
        """Обновление скролла"""
        self.line_numbers.yview_moveto(args[0])
        self.scrollbar.set(*args)
    
    def on_text_change(self, event=None):
        """Обработка изменений текста"""
        self.update_line_numbers()
        self.highlight_syntax()
        self.update_cursor_pos()
    
    def setup_statusbar(self):
        """Статус бар"""
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.grid(row=2, column=0, sticky="ew")
        
        self.status_var = tk.StringVar()
        self.status_var.set("Готов")
        
        self.status_label = ttk.Label(
            self.status_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w",
            padding=(5, 2)
        )
        self.status_label.pack(side="left", fill="x", expand=True)
        
        # Позиция курсора
        self.cursor_pos = ttk.Label(
            self.status_frame,
            text="Строка: 1, Колонка: 1",
            relief="sunken",
            padding=(5, 2)
        )
        self.cursor_pos.pack(side="right")
    
    def setup_right_panel(self):
        """Правая панель с дополнительными функциями"""
        self.right_frame = ttk.Frame(self.main_pane, width=250)
        self.right_frame.grid(row=0, column=2, sticky="nse", padx=(6, 0))
        self.right_frame.grid_propagate(False)
        
        # Поиск
        ttk.Label(self.right_frame, text="Поиск").pack(anchor="w", padx=4, pady=(0, 5))
        
        self.search_entry = ttk.Entry(self.right_frame)
        self.search_entry.pack(fill="x", padx=4, pady=(0, 5))
        
        search_btn = ttk.Button(self.right_frame, text="Найти", command=self.search_text)
        search_btn.pack(pady=(0, 10))
        
        # Статистика
        ttk.Label(self.right_frame, text="Статистика").pack(anchor="w", padx=4)
        self.stats_label = ttk.Label(self.right_frame, text="Символов: 0\nСлов: 0\nСтрок: 0")
        self.stats_label.pack(anchor="w", padx=4, pady=5)
        
        # Кнопка обновления статистики
        update_btn = ttk.Button(self.right_frame, text="Обновить статистику", command=self.update_stats)
        update_btn.pack(pady=10)
    
    def bind_shortcuts(self):
        """Привязка горячих клавиш"""
        shortcuts = {
            '<Control-o>': self.open_file,
            '<Control-s>': self.save_file,
            '<Control-Shift-N>': self.new_python_file,
            '<Control-Shift-H>': self.new_html_file,
            '<Control-z>': self.undo,
            '<Control-y>': self.redo,
            '<Control-x>': self.cut,
            '<Control-c>': self.copy,
            '<Control-v>': self.paste,
            '<Control-a>': self.select_all,
            '<Control-f>': lambda e: self.search_entry.focus(),
            '<F5>': self.update_stats
        }
        
        for key, cmd in shortcuts.items():
            self.root.bind(key, cmd)
    
    # Основные функции редактора
    def new_python_file(self, event=None):
        """Создание нового Python файла"""
        self.current_file = None
        self.file_type = "python"
        self.text_editor.delete("1.0", "end")
        self.insert_initial_content()
        self.update_status("Создан новый Python файл")
    
    def new_html_file(self, event=None):
        """Создание нового HTML файла"""
        self.current_file = None
        self.file_type = "html"
        self.text_editor.delete("1.0", "end")
        self.insert_initial_content()
        self.update_status("Создан новый HTML файл")
    
    def open_file(self, event=None):
        """Открытие файла"""
        file_path = filedialog.askopenfilename(
            title="Открыть файл",
            filetypes=[
                ("Python файлы", "*.py"),
                ("HTML файлы", "*.html;*.htm"),
                ("Все файлы", "*.*")
            ]
        )
        
        if file_path:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                self.text_editor.delete("1.0", "end")
                self.text_editor.insert("1.0", content)
                self.current_file = file_path
                
                # Определяем тип файла по расширению
                if file_path.endswith(".py"):
                    self.file_type = "python"
                    self.update_status(f"Открыт Python файл: {os.path.basename(file_path)}")
                elif file_path.endswith((".html", ".htm")):
                    self.file_type = "html"
                    self.update_status(f"Открыт HTML файл: {os.path.basename(file_path)}")
                else:
                    self.file_type = None
                    self.update_status(f"Открыт файл: {os.path.basename(file_path)}")
                
                self.on_text_change()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось открыть файл:\n{str(e)}")
    
    def save_file(self, event=None):
        """Сохранение файла"""
        if self.current_file:
            try:
                with open(self.current_file, "w", encoding="utf-8") as f:
                    f.write(self.text_editor.get("1.0", "end-1c"))
                
                self.update_status(f"Сохранено: {os.path.basename(self.current_file)}")
                return True
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить файл:\n{str(e)}")
                return False
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        """Сохранение файла с выбором имени"""
        if self.file_type == "python":
            filetypes = [("Python файлы", "*.py"), ("Все файлы", "*.*")]
            defaultext = ".py"
        elif self.file_type == "html":
            filetypes = [("HTML файлы", "*.html"), ("Все файлы", "*.*")]
            defaultext = ".html"
        else:
            filetypes = [("Все файлы", "*.*")]
            defaultext = ""
        
        file_path = filedialog.asksaveasfilename(
            title="Сохранить как",
            defaultextension=defaultext,
            filetypes=filetypes
        )
        
        if file_path:
            self.current_file = file_path
            # Обновляем тип файла по расширению
            if file_path.endswith(".py"):
                self.file_type = "python"
            elif file_path.endswith((".html", ".htm")):
                self.file_type = "html"
            
            return self.save_file()
        return False
    
    def undo(self, event=None):
        """Отменить действие"""
        try:
            self.text_editor.edit_undo()
        except:
            pass
    
    def redo(self, event=None):
        """Повторить действие"""
        try:
            self.text_editor.edit_redo()
        except:
            pass
    
    def cut(self, event=None):
        """Вырезать текст"""
        self.text_editor.event_generate("<<Cut>>")
    
    def copy(self, event=None):
        """Копировать текст"""
        self.text_editor.event_generate("<<Copy>>")
    
    def paste(self, event=None):
        """Вставить текст"""
        self.text_editor.event_generate("<<Paste>>")
    
    def select_all(self, event=None):
        """Выделить весь текст"""
        self.text_editor.tag_add("sel", "1.0", "end")
        return "break"
    
    def toggle_theme(self):
        """Переключение темы"""
        self.dark_mode = not self.dark_mode
        
        if self.dark_mode:
            # Темная тема
            bg = "#1e1e1e"
            fg = "#d4d4d4"
            line_bg = "#252526"
            line_fg = "#858585"
            
            self.text_editor.config(
                bg=bg,
                fg=fg,
                insertbackground=fg,
                selectbackground="#264f78"
            )
            
            self.line_numbers.config(
                background=line_bg,
                foreground=line_fg
            )
            
            self.right_frame.config(style="Dark.TFrame")
            self.status_frame.config(style="Dark.TFrame")
            self.toolbar.config(style="Dark.TFrame")
            
            for label in [self.status_label, self.cursor_pos, self.stats_label]:
                label.config(style="Dark.TLabel")
        else:
            # Светлая тема
            bg = "#ffffff"
            fg = "#000000"
            line_bg = "#f0f0f0"
            line_fg = "#666666"
            
            self.text_editor.config(
                bg=bg,
                fg=fg,
                insertbackground=fg,
                selectbackground="#b5d5ff"
            )
            
            self.line_numbers.config(
                background=line_bg,
                foreground=line_fg
            )
            
            self.right_frame.config(style="TFrame")
            self.status_frame.config(style="TFrame")
            self.toolbar.config(style="TFrame")
            
            for label in [self.status_label, self.cursor_pos, self.stats_label]:
                label.config(style="TLabel")
        
        # Принудительно обновляем подсветку
        self.highlight_syntax()
    
    def update_line_numbers(self, event=None):
        """Обновление нумерации строк"""
        lines = self.text_editor.get('1.0', 'end-1c').split('\n')
        line_numbers_text = '\n'.join(str(i) for i in range(1, len(lines)+1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
        
        # Обновляем статистику
        self.update_stats()
    
    def highlight_syntax(self, event=None):
        """Подсветка синтаксиса для Python и HTML"""
        if not self.file_type:
            return
            
        # Удаляем все теги подсветки
        for tag in ["keyword", "string", "comment", "tag", "attribute"]:
            self.text_editor.tag_remove(tag, "1.0", "end")
        
        text = self.text_editor.get("1.0", "end-1c")
        
        if self.file_type == "python":
            self.highlight_python(text)
        elif self.file_type == "html":
            self.highlight_html(text)
    
    def highlight_python(self, text):
        """Подсветка Python кода"""
        # Ключевые слова Python
        keywords = [
            'False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await',
            'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
            'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is',
            'lambda', 'nonlocal', 'not', 'or', 'pass', 'raise', 'return',
            'try', 'while', 'with', 'yield'
        ]
        
        # Комментарии
        for match in re.finditer(r'#.*$', text, re.MULTILINE):
            start, end = match.span()
            self.text_editor.tag_add("comment", f"1.0+{start}c", f"1.0+{end}c")
        
        # Строки
        for match in re.finditer(r'(\'\'\'.*?\'\'\'|\"\"\".*?\"\"\"|\'.*?\'|\".*?\")', text, re.DOTALL):
            start, end = match.span()
            self.text_editor.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")
        
        # Ключевые слова
        for keyword in keywords:
            for match in re.finditer(r'\b' + keyword + r'\b', text):
                start, end = match.span()
                self.text_editor.tag_add("keyword", f"1.0+{start}c", f"1.0+{end}c")
        
        # Настройка цветов
        if self.dark_mode:
            self.text_editor.tag_config("keyword", foreground="#569cd6")
            self.text_editor.tag_config("string", foreground="#ce9178")
            self.text_editor.tag_config("comment", foreground="#6a9955")
        else:
            self.text_editor.tag_config("keyword", foreground="#0000ff")
            self.text_editor.tag_config("string", foreground="#a31515")
            self.text_editor.tag_config("comment", foreground="#008000")
    
    def highlight_html(self, text):
        """Подсветка HTML кода"""
        # Теги
        for match in re.finditer(r'<\/?\w+', text):
            start, end = match.span()
            self.text_editor.tag_add("tag", f"1.0+{start}c", f"1.0+{end}c")
        
        # Атрибуты
        for match in re.finditer(r'\b\w+=', text):
            start, end = match.span()
            self.text_editor.tag_add("attribute", f"1.0+{start}c", f"1.0+{end}c")
        
        # Строки в HTML
        for match in re.finditer(r'"[^"]*"', text):
            start, end = match.span()
            self.text_editor.tag_add("string", f"1.0+{start}c", f"1.0+{end}c")
        
        # Комментарии HTML
        for match in re.finditer(r'<!--.*?-->', text, re.DOTALL):
            start, end = match.span()
            self.text_editor.tag_add("comment", f"1.0+{start}c", f"1.0+{end}c")
        
        # Настройка цветов
        if self.dark_mode:
            self.text_editor.tag_config("tag", foreground="#569cd6")
            self.text_editor.tag_config("attribute", foreground="#9cdcfe")
            self.text_editor.tag_config("string", foreground="#ce9178")
            self.text_editor.tag_config("comment", foreground="#6a9955")
        else:
            self.text_editor.tag_config("tag", foreground="#0000ff")
            self.text_editor.tag_config("attribute", foreground="#ff00ff")
            self.text_editor.tag_config("string", foreground="#a31515")
            self.text_editor.tag_config("comment", foreground="#008000")
    
    def insert_initial_content(self):
        """Вставка начального контента в зависимости от типа файла"""
        if self.file_type == "python":
            self.text_editor.insert("1.0", 
                "# Начните писать Python код здесь\n"
                "def hello_world():\n"
                '    print("Hello, World!")\n\n'
                'if __name__ == "__main__":\n'
                "    hello_world()"
            )
        elif self.file_type == "html":
            self.text_editor.insert("1.0",
                '<!DOCTYPE html>\n'
                '<html lang="ru">\n'
                '<head>\n'
                '    <meta charset="UTF-8">\n'
                '    <title>Моя страница</title>\n'
                '</head>\n'
                '<body>\n'
                '    <h1>Привет, мир!</h1>\n'
                '</body>\n'
                '</html>'
            )
        else:
            self.text_editor.insert("1.0", 
                "Выберите тип файла (Python или HTML) в меню 'Файл' → 'Новый'\n"
                "или откройте существующий файл с расширением .py или .html"
            )
        
        self.highlight_syntax()
    
    def update_cursor_pos(self, event=None):
        """Обновление позиции курсора в статус баре"""
        cursor_pos = self.text_editor.index(tk.INSERT)
        line, column = cursor_pos.split(".")
        self.cursor_pos.config(text=f"Строка: {line}, Колонка: {column}")
    
    def search_text(self):
        """Поиск текста в редакторе"""
        search_str = self.search_entry.get()
        if not search_str:
            return
            
        # Удаляем предыдущие подсветки
        self.text_editor.tag_remove("found", "1.0", "end")
        
        start_pos = "1.0"
        matches = 0
        while True:
            start_pos = self.text_editor.search(search_str, start_pos, stopindex=tk.END)
            if not start_pos:
                break
                
            end_pos = f"{start_pos}+{len(search_str)}c"
            self.text_editor.tag_add("found", start_pos, end_pos)
            start_pos = end_pos
            matches += 1
        
        if matches > 0:
            self.text_editor.tag_config("found", 
                background="yellow", 
                foreground="black" if not self.dark_mode else "black"
            )
            self.update_status(f"Найдено совпадений: {matches}")
        else:
            self.update_status("Текст не найден")
    
    def update_stats(self):
        """Обновление статистики текста"""
        content = self.text_editor.get("1.0", "end-1c")
        chars = len(content)
        words = len(content.split())
        lines = content.count('\n') + 1
        
        self.stats_label.config(text=f"Символов: {chars}\nСлов: {words}\nСтрок: {lines}")
    
    def update_status(self, message):
        """Обновление статус бара"""
        self.status_var.set(message)
    
    def confirm_exit(self):
        """Подтверждение выхода из программы"""
        if messagebox.askokcancel("Выход", "Вы уверены, что хотите выйти?"):
            self.root.destroy()
    
    def show_about(self):
        """Окно 'О программе'"""
        about_text = (
            "Редактор кода (Python/HTML)\n"
            "Версия 1.0\n\n"
            "Возможности:\n"
            "- Подсветка синтаксиса Python и HTML\n"
            "- Нумерация строк\n"
            "- Темная/светлая тема\n"
            "- Поиск по тексту\n"
            "- Статистика документа\n\n"
            f"Дата: {datetime.now().strftime('%Y-%m-%d')}"
        )
        messagebox.showinfo("О программе", about_text)

if __name__ == "__main__":
    root = tk.Tk()
    editor = CodeEditor(root)
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", editor.confirm_exit)
    root.mainloop()