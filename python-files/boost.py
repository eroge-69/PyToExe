import tkinter as tk
from tkinter import ttk, messagebox

class FPSBoostApp:
    def __init__(self, root):
        self.root = root
        self.root.title("GameBoost Pro v2.1")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a1a')
        
        # Стили
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Стиль для кнопок
        style.configure('Boost.TButton',
                       background='#00ff00',
                       foreground='black',
                       focuscolor='none',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.map('Boost.TButton',
                 background=[('active', '#00cc00'),
                           ('pressed', '#009900')])
        
        # Стиль для вкладок
        style.configure('Custom.TNotebook',
                       background='#2d2d2d',
                       foreground='white')
        style.configure('Custom.TNotebook.Tab',
                       background='#404040',
                       foreground='white',
                       padding=[20, 5])
        
        # Стиль для прогресс-бара
        style.configure('Custom.Horizontal.TProgressbar',
                       background='#00ff00',
                       troughcolor='#333333')
    
    def create_widgets(self):
        # Заголовок
        header_frame = tk.Frame(self.root, bg='#1a1a1a')
        header_frame.pack(pady=10)
        
        title_label = tk.Label(header_frame,
                              text="GAMEBOOST PRO",
                              font=('Arial', 20, 'bold'),
                              fg='#00ff00',
                              bg='#1a1a1a')
        title_label.pack()
        
        subtitle_label = tk.Label(header_frame,
                                 text="Оптимизация системы для игр",
                                 font=('Arial', 10),
                                 fg='#cccccc',
                                 bg='#1a1a1a')
        subtitle_label.pack()
        
        # Статус системы
        status_frame = tk.Frame(self.root, bg='#2d2d2d', relief='ridge', bd=1)
        status_frame.pack(fill='x', padx=20, pady=10)
        
        status_label = tk.Label(status_frame,
                               text="Статус системы: ОПТИМАЛЬНЫЙ",
                               font=('Arial', 11, 'bold'),
                               fg='#00ff00',
                               bg='#2d2d2d')
        status_label.pack(pady=5)
        
        # Прогресс-бар оптимизации
        progress_label = tk.Label(status_frame,
                                 text="Уровень оптимизации:",
                                 font=('Arial', 9),
                                 fg='#cccccc',
                                 bg='#2d2d2d')
        progress_label.pack(pady=(10, 5))
        
        self.progress = ttk.Progressbar(status_frame,
                                       style='Custom.Horizontal.TProgressbar',
                                       length=560,
                                       maximum=100,
                                       value=75)
        self.progress.pack(pady=5)
        
        # Вкладки
        notebook = ttk.Notebook(self.root, style='Custom.TNotebook')
        
        # Вкладка быстрой оптимизации
        quick_tab = tk.Frame(notebook, bg='#2d2d2d')
        notebook.add(quick_tab, text="Быстрая оптимизация")
        
        # Вкладка расширенных настроек
        advanced_tab = tk.Frame(notebook, bg='#2d2d2d')
        notebook.add(advanced_tab, text="Расширенные настройки")
        
        # Вкладка игровых профилей
        profiles_tab = tk.Frame(notebook, bg='#2d2d2d')
        notebook.add(profiles_tab, text="Игровые профили")
        
        notebook.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Содержимое вкладки быстрой оптимизации
        self.create_quick_tab(quick_tab)
        
        # Содержимое вкладки расширенных настроек
        self.create_advanced_tab(advanced_tab)
        
        # Содержимое вкладки игровых профилей
        self.create_profiles_tab(profiles_tab)
        
        # Панель действий
        self.create_action_panel()
    
    def create_quick_tab(self, parent):
        # Кнопки быстрой оптимизации
        buttons_frame = tk.Frame(parent, bg='#2d2d2d')
        buttons_frame.pack(pady=20)
        
        boost_btn = ttk.Button(buttons_frame,
                              text="🚀 БУСТ ПРОИЗВОДИТЕЛЬНОСТИ",
                              style='Boost.TButton',
                              command=self.do_nothing)
        boost_btn.grid(row=0, column=0, padx=10, pady=10, sticky='ew')
        
        clean_btn = ttk.Button(buttons_frame,
                              text="🧹 ОЧИСТКА ПАМЯТИ",
                              style='Boost.TButton',
                              command=self.do_nothing)
        clean_btn.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        
        network_btn = ttk.Button(buttons_frame,
                                text="📡 ОПТИМИЗАЦИЯ СЕТИ",
                                style='Boost.TButton',
                                command=self.do_nothing)
        network_btn.grid(row=1, column=0, padx=10, pady=10, sticky='ew')
        
        services_btn = ttk.Button(buttons_frame,
                                 text="⚙️ ОСТАНОВКА СЛУЖБ",
                                 style='Boost.TButton',
                                 command=self.do_nothing)
        services_btn.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        
        # Чекбоксы дополнительных опций
        options_frame = tk.Frame(parent, bg='#2d2d2d')
        options_frame.pack(pady=10)
        
        self.var1 = tk.BooleanVar(value=True)
        self.var2 = tk.BooleanVar(value=True)
        self.var3 = tk.BooleanVar(value=False)
        
        cb1 = tk.Checkbutton(options_frame,
                            text="Оптимизация процессов",
                            variable=self.var1,
                            bg='#2d2d2d',
                            fg='#cccccc',
                            selectcolor='#1a1a1a')
        cb1.pack(anchor='w')
        
        cb2 = tk.Checkbutton(options_frame,
                            text="Отключение визуальных эффектов",
                            variable=self.var2,
                            bg='#2d2d2d',
                            fg='#cccccc',
                            selectcolor='#1a1a1a')
        cb2.pack(anchor='w')
        
        cb3 = tk.Checkbutton(options_frame,
                            text="Приоритет игровых процессов",
                            variable=self.var3,
                            bg='#2d2d2d',
                            fg='#cccccc',
                            selectcolor='#1a1a1a')
        cb3.pack(anchor='w')
    
    def create_advanced_tab(self, parent):
        # Расширенные настройки
        settings_frame = tk.Frame(parent, bg='#2d2d2d')
        settings_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        settings = [
            "Настройка файла подкачки",
            "Оптимизация GPU",
            "Твики реестра",
            "Управление питанием",
            "Оптимизация DPC"
        ]
        
        for i, setting in enumerate(settings):
            frame = tk.Frame(settings_frame, bg='#404040')
            frame.pack(fill='x', pady=5)
            
            label = tk.Label(frame,
                           text=setting,
                           bg='#404040',
                           fg='white',
                           font=('Arial', 9))
            label.pack(side='left', padx=10, pady=5)
            
            btn = ttk.Button(frame,
                           text="Настроить",
                           style='Boost.TButton',
                           command=self.do_nothing)
            btn.pack(side='right', padx=10, pady=5)
    
    def create_profiles_tab(self, parent):
        # Игровые профили
        profiles_frame = tk.Frame(parent, bg='#2d2d2d')
        profiles_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        games = [
            "CS:GO / CS2",
            "Dota 2",
            "Valorant", 
            "Apex Legends",
            "Call of Duty: Warzone"
        ]
        
        for game in games:
            game_frame = tk.Frame(profiles_frame, bg='#404040')
            game_frame.pack(fill='x', pady=3)
            
            label = tk.Label(game_frame,
                           text=game,
                           bg='#404040',
                           fg='white',
                           font=('Arial', 9))
            label.pack(side='left', padx=10, pady=3)
            
            apply_btn = ttk.Button(game_frame,
                                 text="Применить профиль",
                                 style='Boost.TButton',
                                 command=self.do_nothing)
            apply_btn.pack(side='right', padx=5, pady=3)
    
    def create_action_panel(self):
        # Панель действий внизу
        action_frame = tk.Frame(self.root, bg='#1a1a1a')
        action_frame.pack(fill='x', pady=10)
        
        help_btn = ttk.Button(action_frame,
                             text="Справка",
                             command=self.do_nothing)
        help_btn.pack(side='left', padx=20)
        
        settings_btn = ttk.Button(action_frame,
                                text="Настройки",
                                command=self.do_nothing)
        settings_btn.pack(side='left', padx=10)
        
        # Центральная большая кнопка
        main_boost_btn = ttk.Button(action_frame,
                                   text="🚀 ЗАПУСТИТЬ ОПТИМИЗАЦИЮ",
                                   style='Boost.TButton',
                                   command=self.do_nothing)
        main_boost_btn.pack(side='left', padx=50)
        
        about_btn = ttk.Button(action_frame,
                              text="О программе",
                              command=self.do_nothing)
        about_btn.pack(side='right', padx=20)
        
        exit_btn = ttk.Button(action_frame,
                             text="Выход",
                             command=self.root.quit)
        exit_btn.pack(side='right', padx=10)
    
    def do_nothing(self):
        # Функция-заглушка для кнопок
        pass

if __name__ == "__main__":
    root = tk.Tk()
    app = FPSBoostApp(root)
    root.mainloop()