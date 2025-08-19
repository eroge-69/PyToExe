import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import webbrowser
from time import strftime
import os

class Windows9Simulator:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows 9 Simulator")
        self.root.geometry("800x600")
        self.root.configure(bg='#0078D7')
        
        # Переменные
        self.start_menu_visible = False
        self.open_apps = {}  # Словарь для хранения открытых приложений
        self.cursor_position = (0, 0)
        
        # Рабочий стол (фон с квадратиками)
        self.desktop = tk.Frame(self.root, bg='#0078D7', cursor="arrow")
        self.desktop.pack(expand=True, fill='both')
        
        # Создаем 4 больших квадратика на рабочем столе
        self.create_desktop_icons()
        
        # Панель задач
        self.taskbar = tk.Frame(self.root, bg='#1a1a1a', height=40)
        self.taskbar.pack(side='bottom', fill='x')
        
        # Кнопка "Пуск"
        self.start_button = tk.Button(
            self.taskbar, 
            text="Пуск", 
            bg='#333333', 
            fg='white',
            command=self.toggle_start_menu
        )
        self.start_button.pack(side='left', padx=5)
        
        # Фрейм для кнопок приложений на панели задач
        self.taskbar_apps = tk.Frame(self.taskbar, bg='#1a1a1a')
        self.taskbar_apps.pack(side='left', fill='both', expand=True)
        
        # Часы
        self.clock = tk.Label(self.taskbar, text="00:00", bg='#1a1a1a', fg='white')
        self.clock.pack(side='right', padx=10)
        self.update_clock()
        
        # Меню "Пуск"
        self.start_menu = tk.Frame(self.root, bg='#1a1a1a', width=200, height=300)
        self.build_start_menu()
        self.start_menu.place_forget()
        
        # Курсор
        self.cursor = tk.Label(self.root, text="", bg="black", fg="white", font=('Arial', 12))
        self.cursor.place(x=0, y=0)
        self.root.bind('<Motion>', self.move_cursor)
        self.root.bind('<Button-1>', self.cursor_click)
        
    def move_cursor(self, event):
        self.cursor_position = (event.x, event.y)
        self.cursor.place(x=event.x, y=event.y)
        
    def cursor_click(self, event):
        # Мигание курсора при клике
        self.cursor.config(bg='white')
        self.root.after(100, lambda: self.cursor.config(bg='black'))
    
    def create_desktop_icons(self):
        # Создаем 4 больших квадратика в центре рабочего стола
        colors = ['#ff0000', '#00ff00', '#0000ff', '#ffff00']
        icon_size = 150  # Увеличили размер квадратиков
        labels = ["Мои документы", "Корзина", "Мой компьютер", "Сеть"]
        
        # Центральный контейнер для квадратиков
        center_frame = tk.Frame(self.desktop, bg='#0078D7')
        center_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        for i in range(4):
            row = i // 2
            col = i % 2
            icon_frame = tk.Frame(center_frame, bg='#0078D7')
            icon_frame.grid(row=row, column=col, padx=15, pady=15)
            
            icon = tk.Frame(
                icon_frame,
                bg=colors[i],
                width=icon_size,
                height=icon_size,
                highlightthickness=2,
                highlightbackground="white"
            )
            icon.pack()
            
            label = tk.Label(
                icon_frame,
                text=labels[i],
                bg='#0078D7',
                fg='white'
            )
            label.pack()
            
            # Привязываем двойной клик для открытия проводника
            icon.bind("<Double-Button-1>", lambda e, app=labels[i]: self.open_explorer() if app == "Мой компьютер" else None)
    
    def update_clock(self):
        current_time = strftime('%H:%M')
        self.clock.config(text=current_time)
        self.root.after(60000, self.update_clock)
    
    def toggle_start_menu(self):
        if self.start_menu_visible:
            self.start_menu.place_forget()
        else:
            self.start_menu.place(x=10, rely=1.0, y=-40, anchor='sw')
            self.start_menu.lift()
        self.start_menu_visible = not self.start_menu_visible
    
    def build_start_menu(self):
        apps = [
            ("Калькулятор", self.open_calculator),
            ("Терминал", self.open_terminal),
            ("Браузер", self.open_browser),
            ("Блокнот", self.open_notepad),
            ("Проводник", self.open_explorer),
            ("Завершение работы", self.shutdown)
        ]
        
        for name, cmd in apps:
            btn = tk.Button(
                self.start_menu,
                text=name,
                bg='#1a1a1a',
                fg='white',
                anchor='w',
                command=cmd
            )
            btn.pack(fill='x', pady=2)
    
    def add_app_to_taskbar(self, app_name, window):
        # Создаем кнопку на панели задач
        btn = tk.Button(
            self.taskbar_apps,
            text=app_name,
            bg='#1a1a1a',
            fg='white',
            relief='flat',
            command=lambda: self.focus_app(window)
        )
        btn.pack(side='left', padx=2)
        
        # Сохраняем ссылку на кнопку
        self.open_apps[window] = btn
        
        # Привязываем закрытие окна к удалению кнопки
        window.protocol("WM_DELETE_WINDOW", lambda: self.close_app(window))
    
    def focus_app(self, window):
        window.deiconify()
        window.lift()
        window.focus_force()
    
    def close_app(self, window):
        # Удаляем кнопку из панели задач
        if window in self.open_apps:
            self.open_apps[window].destroy()
            del self.open_apps[window]
        window.destroy()
    
    def open_notepad(self):
        self.toggle_start_menu()
        notepad = tk.Toplevel(self.root)
        notepad.title("Блокнот - Безымянный")
        notepad.geometry("400x500")
        
        self.current_file = None
        
        text_area = scrolledtext.ScrolledText(
            notepad,
            wrap=tk.WORD,
            width=40,
            height=20,
            font=('Arial', 12)
        )
        text_area.pack(expand=True, fill='both', padx=5, pady=5)
        
        # Меню
        menubar = tk.Menu(notepad)
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Новый", command=lambda: self.new_file(notepad, text_area))
        file_menu.add_command(label="Открыть", command=lambda: self.open_file(notepad, text_area))
        file_menu.add_command(label="Сохранить", command=lambda: self.save_file(notepad, text_area))
        file_menu.add_command(label="Сохранить как...", command=lambda: self.save_file_as(notepad, text_area))
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=lambda: self.close_app(notepad))
        menubar.add_cascade(label="Файл", menu=file_menu)
        
        # Меню "Правка"
        edit_menu = tk.Menu(menubar, tearoff=0)
        edit_menu.add_command(label="Вырезать", command=lambda: text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Копировать", command=lambda: text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Вставить", command=lambda: text_area.event_generate("<<Paste>>"))
        menubar.add_cascade(label="Правка", menu=edit_menu)
        
        notepad.config(menu=menubar)
        
        # Добавляем на панель задач
        self.add_app_to_taskbar("Блокнот", notepad)
    
    def new_file(self, window, text_area):
        text_area.delete(1.0, tk.END)
        window.title("Блокнот - Безымянный")
        self.current_file = None
    
    def open_file(self, window, text_area):
        filepath = filedialog.askopenfilename(
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "r", encoding="utf-8") as input_file:
            text = input_file.read()
            text_area.delete(1.0, tk.END)
            text_area.insert(tk.END, text)
        window.title(f"Блокнот - {os.path.basename(filepath)}")
        self.current_file = filepath
    
    def save_file(self, window, text_area):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as output_file:
                text = text_area.get(1.0, tk.END)
                output_file.write(text)
        else:
            self.save_file_as(window, text_area)
    
    def save_file_as(self, window, text_area):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, "w", encoding="utf-8") as output_file:
            text = text_area.get(1.0, tk.END)
            output_file.write(text)
        window.title(f"Блокнот - {os.path.basename(filepath)}")
        self.current_file = filepath
    
    def open_calculator(self):
        self.toggle_start_menu()
        calc = tk.Toplevel(self.root)
        calc.title("Калькулятор")
        calc.geometry("250x350")
        
        entry = tk.Entry(calc, font=('Arial', 18), justify='right')
        entry.pack(fill='x', padx=10, pady=10)
        
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        frame = tk.Frame(calc)
        frame.pack()
        
        for i, btn in enumerate(buttons):
            b = tk.Button(
                frame, 
                text=btn, 
                width=3, 
                height=1,
                command=lambda x=btn: self.on_calc_click(x, entry)
            )
            b.grid(row=i//4, column=i%4, padx=2, pady=2)
        
        # Добавляем на панель задач
        self.add_app_to_taskbar("Калькулятор", calc)
    
    def on_calc_click(self, key, entry):
        if key == '=':
            try:
                result = eval(entry.get())
                entry.delete(0, tk.END)
                entry.insert(tk.END, str(result))
            except:
                entry.delete(0, tk.END)
                entry.insert(tk.END, "Error")
        else:
            entry.insert(tk.END, key)
    
    def open_terminal(self):
        self.toggle_start_menu()
        terminal = tk.Toplevel(self.root)
        terminal.title("Терминал")
        terminal.geometry("400x300")
        
        text = scrolledtext.ScrolledText(terminal, bg='black', fg='white', font=('Courier', 12))
        text.pack(expand=True, fill='both')
        
        text.insert(tk.END, "Добро пожаловать в эмулятор терминала\n\n")
        text.insert(tk.END, "user@simulator:~$ ")
        
        entry = tk.Entry(terminal, bg='black', fg='white', insertbackground='white')
        entry.pack(fill='x', padx=5, pady=5)
        entry.focus()
        
        def execute_command(event=None):
            cmd = entry.get()
            text.insert(tk.END, cmd + "\n")
            
            if cmd == "help":
                text.insert(tk.END, "Доступные команды: help, clear, exit\n")
            elif cmd == "clear":
                text.delete(1.0, tk.END)
            elif cmd == "exit":
                self.close_app(terminal)
                return
            else:
                text.insert(tk.END, f"Команда '{cmd}' не найдена. Введите 'help' для списка команд.\n")
            
            text.insert(tk.END, "user@simulator:~$ ")
            entry.delete(0, tk.END)
            text.see(tk.END)
        
        entry.bind("<Return>", execute_command)
        
        # Добавляем на панель задач
        self.add_app_to_taskbar("Терминал", terminal)
    
    def open_browser(self):
        self.toggle_start_menu()
        browser = tk.Toplevel(self.root)
        browser.title("Браузер")
        browser.geometry("400x300")
        
        frame = tk.Frame(browser)
        frame.pack(fill='x')
        
        url_entry = tk.Entry(frame)
        url_entry.pack(side='left', fill='x', expand=True)
        url_entry.insert(0, "https://google.com")
        
        go_btn = tk.Button(frame, text="Перейти", command=lambda: webbrowser.open(url_entry.get()))
        go_btn.pack(side='right')
        
        content = tk.Label(browser, text="Браузер откроет сайт в вашем основном браузере")
        content.pack(expand=True)
        
        # Добавляем на панель задач
        self.add_app_to_taskbar("Браузер", browser)
    
    def open_explorer(self):
        self.toggle_start_menu()
        explorer = tk.Toplevel(self.root)
        explorer.title("Проводник")
        explorer.geometry("500x400")
        
        # Панель инструментов
        toolbar = tk.Frame(explorer, bg='#e1e1e1')
        toolbar.pack(fill='x')
        
        back_btn = tk.Button(toolbar, text="Назад")
        back_btn.pack(side='left', padx=2)
        
        forward_btn = tk.Button(toolbar, text="Вперёд")
        forward_btn.pack(side='left', padx=2)
        
        up_btn = tk.Button(toolbar, text="Вверх", command=lambda: self.navigate_up(explorer, tree, path_var))
        up_btn.pack(side='left', padx=2)
        
        # Адресная строка
        path_frame = tk.Frame(explorer)
        path_frame.pack(fill='x', padx=5, pady=5)
        
        path_var = tk.StringVar(value=os.getcwd())
        path_entry = tk.Entry(path_frame, textvariable=path_var)
        path_entry.pack(side='left', fill='x', expand=True)
        
        go_btn = tk.Button(path_frame, text="Перейти", 
                          command=lambda: self.navigate_to(path_var.get(), explorer, tree, path_var))
        go_btn.pack(side='right')
        
        # Дерево файлов
        tree_frame = tk.Frame(explorer)
        tree_frame.pack(fill='both', expand=True)
        
        tree = ttk.Treeview(tree_frame)
        tree["columns"] = ("size", "type", "modified")
        tree.column("#0", width=300, minwidth=200)
        tree.column("size", width=80, minwidth=80)
        tree.column("type", width=100, minwidth=100)
        tree.column("modified", width=120, minwidth=120)
        
        tree.heading("#0", text="Имя", anchor='w')
        tree.heading("size", text="Размер", anchor='w')
        tree.heading("type", text="Тип", anchor='w')
        tree.heading("modified", text="Изменён", anchor='w')
        
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scroll.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(fill='both', expand=True)
        
        # Заполняем дерево
        self.populate_tree(tree, os.getcwd())
        
        # Обработчики событий
        tree.bind("<Double-1>", lambda e: self.on_tree_double_click(e, tree, path_var))
        path_entry.bind("<Return>", lambda e: self.navigate_to(path_var.get(), explorer, tree, path_var))
        
        # Добавляем на панель задач
        self.add_app_to_taskbar("Проводник", explorer)
    
    def populate_tree(self, tree, path):
        tree.delete(*tree.get_children())
        try:
            for item in os.listdir(path):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    tree.insert("", 'end', text=item, values=("Папка", "", ""))
                else:
                    size = os.path.getsize(full_path)
                    tree.insert("", 'end', text=item, values=(f"{size} байт", "Файл", ""))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать содержимое папки: {e}")
    
    def on_tree_double_click(self, event, tree, path_var):
        item = tree.selection()[0]
        name = tree.item(item, "text")
        current_path = path_var.get()
        new_path = os.path.join(current_path, name)
        
        if os.path.isdir(new_path):
            path_var.set(new_path)
            self.populate_tree(tree, new_path)
        else:
            try:
                os.startfile(new_path)
            except:
                messagebox.showinfo("Информация", f"Не удалось открыть файл: {name}")
    
    def navigate_to(self, path, window, tree, path_var):
        if os.path.exists(path):
            path_var.set(path)
            self.populate_tree(tree, path)
        else:
            messagebox.showerror("Ошибка", "Указанный путь не существует")
    
    def navigate_up(self, window, tree, path_var):
        current_path = path_var.get()
        parent_path = os.path.dirname(current_path)
        if os.path.exists(parent_path):
            path_var.set(parent_path)
            self.populate_tree(tree, parent_path)
    
    def shutdown(self):
        if messagebox.askyesno("Завершение работы", "Вы действительно хотите завершить работу Windows 9 Simulator?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = Windows9Simulator(root)
    root.mainloop()