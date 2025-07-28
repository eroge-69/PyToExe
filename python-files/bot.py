import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import shutil
from datetime import datetime
import json
import webbrowser
import pysftp
from tempfile import NamedTemporaryFile

class BotDatabaseEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot Database Editor - Neon Style")
        self.root.geometry("1400x900")
        
        # Параметры SSH подключения
        self.ssh_host = "78.24.223.180"
        self.ssh_user = "root"
        self.ssh_password = "Linard11"  # Лучше использовать SSH-ключи
        self.remote_db_path = "/root/moderbot/bot_data.db"
        
        # Локальная временная копия БД
        self.local_db_path = "temp_bot_data.db"
        self.db_path = self.local_db_path  # Для совместимости с остальным кодом
        
        # Подключаемся к серверу и загружаем БД
        try:
            self.download_db()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить БД: {e}")
            self.root.destroy()
            return
        
        self.backup_dir = "db_backups"
        self.current_user_id = None
        
        # Создаем папку для бэкапов
        os.makedirs(self.backup_dir, exist_ok=True)
        
        self.setup_styles()
        self.create_widgets()
        self.load_users()
    
    def setup_styles(self):
        """Настройка светлого стиля интерфейса"""
        self.style = ttk.Style()
        
        # Основные цвета
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', foreground='#333333', font=('Helvetica', 10))
        self.style.configure('TButton', background='#e0e0e0', foreground='#333333', 
                       font=('Helvetica', 10), borderwidth=1)
        self.style.configure('TEntry', fieldbackground='#ffffff', foreground='#333333')
        self.style.configure('TLabelFrame', background='#f0f0f0', foreground='#333333')
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', background='#e0e0e0', foreground='#333333',
                        padding=[10, 5], font=('Helvetica', 10))
        
        # Стиль для Treeview
        self.style.configure('Treeview', background='#ffffff', foreground='#333333',
                        fieldbackground='#ffffff', rowheight=25)
        self.style.configure('Treeview.Heading', background='#e0e0e0', foreground='#333333',
                        font=('Helvetica', 10, 'bold'))
        self.style.map('Treeview', background=[('selected', '#4a98f7')], 
                    foreground=[('selected', '#ffffff')])
        
        # Стиль для кнопок
        self.style.map('TButton', background=[('active', '#d0d0d0')])
        
        # Настройка шрифтов
        self.bold_font = ('Helvetica', 10, 'bold')
        self.title_font = ('Helvetica', 12, 'bold')
        self.main_font = ('Helvetica', 10)
        
        # Цвета
        self.bg_color = '#f0f0f0'
        self.fg_color = '#333333'
        self.entry_bg = '#ffffff'
        self.button_bg = '#e0e0e0'
        self.button_active = '#d0d0d0'
    
    def download_db(self):
        """Загружает базу данных с сервера"""
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None  # Отключаем проверку хоста (небезопасно!)
            
            with pysftp.Connection(
                host=self.ssh_host,
                username=self.ssh_user,
                password=self.ssh_password,
                cnopts=cnopts
            ) as sftp:
                sftp.get(self.remote_db_path, self.local_db_path)
        except Exception as e:
            raise Exception(f"Не удалось загрузить БД с сервера: {e}")
    
    def upload_db(self):
        """Загружает базу данных на сервер"""
        try:
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None  # Отключаем проверку хоста (небезопасно!)
            
            with pysftp.Connection(
                host=self.ssh_host,
                username=self.ssh_user,
                password=self.ssh_password,
                cnopts=cnopts
            ) as sftp:
                sftp.put(self.local_db_path, self.remote_db_path)
        except Exception as e:
            raise Exception(f"Не удалось загрузить БД на сервер: {e}")
    
    def create_backup(self):
        """Создает резервную копию базы данных"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(self.backup_dir, f"backup_{timestamp}.db")
        
        # Копируем локальную БД в бэкап
        shutil.copy2(self.local_db_path, backup_path)
        
        return backup_path
    
    # Остальные методы остаются без изменений, так как они используют self.db_path,
    # который теперь указывает на self.local_db_path
    
    def create_widgets(self):
        # Основной контейнер
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для списка пользователей с неоновой подсветкой
        users_frame = ttk.LabelFrame(main_frame, text="Пользователи", padding=10)
        users_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Фрейм для информации о пользователе
        info_frame = ttk.LabelFrame(main_frame, text="Информация о пользователе", padding=10)
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Элементы для списка пользователей
        search_frame = ttk.Frame(users_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Поиск:", font=self.bold_font).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", self.on_search)
        
        # Treeview для пользователей с неоновым стилем
        tree_frame = ttk.Frame(users_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.users_tree = ttk.Treeview(tree_frame, columns=("id", "subscribed", "balance"), show="headings")
        self.users_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.users_tree.heading("subscribed", text="Подписка", anchor=tk.CENTER)
        self.users_tree.heading("balance", text="Баланс", anchor=tk.CENTER)
        
        self.users_tree.column("id", width=100, anchor=tk.CENTER)
        self.users_tree.column("subscribed", width=100, anchor=tk.CENTER)
        self.users_tree.column("balance", width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.users_tree.yview)
        self.users_tree.configure(yscrollcommand=scrollbar.set)
        
        self.users_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.users_tree.bind("<<TreeviewSelect>>", self.on_user_select)
        
        # Элементы для информации о пользователе
        self.user_info_frame = ttk.Frame(info_frame)
        self.user_info_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Основная информация
        ttk.Label(self.user_info_frame, text="ID:", font=self.bold_font).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.id_var = tk.StringVar()
        ttk.Label(self.user_info_frame, textvariable=self.id_var, font=self.main_font).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.user_info_frame, text="Подписка:", font=self.bold_font).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.subscribed_var = tk.IntVar()
        sub_check = ttk.Checkbutton(self.user_info_frame, variable=self.subscribed_var)
        sub_check.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.user_info_frame, text="Баланс:", font=self.bold_font).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.balance_var = tk.IntVar()
        balance_entry = ttk.Entry(self.user_info_frame, textvariable=self.balance_var, width=15, font=self.main_font)
        balance_entry.grid(row=2, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.user_info_frame, text="Дата регистрации:", font=self.bold_font).grid(row=3, column=0, sticky=tk.W, pady=5)
        self.start_date_var = tk.StringVar()
        ttk.Label(self.user_info_frame, textvariable=self.start_date_var, font=self.main_font).grid(row=3, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(self.user_info_frame, text="Последняя активность:", font=self.bold_font).grid(row=4, column=0, sticky=tk.W, pady=5)
        self.last_activity_var = tk.StringVar()
        ttk.Label(self.user_info_frame, textvariable=self.last_activity_var, font=self.main_font).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Кнопки для сохранения с неоновым эффектом
        button_frame = ttk.Frame(self.user_info_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=15)
        
        save_button = ttk.Button(button_frame, text="Сохранить изменения", command=self.save_user_info)
        save_button.pack(side=tk.LEFT, padx=5)
        
        refresh_button = ttk.Button(button_frame, text="Обновить данные", command=self.load_users)
        refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Вкладки для статистики
        self.notebook = ttk.Notebook(info_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка с игровой статистикой
        self.games_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.games_tab, text="Игровая статистика")
        
        # Вкладка с чеками
        self.checks_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.checks_tab, text="Чеки")
        
        # Вкладка с обучением ИИ
        self.ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.ai_tab, text="Обучение ИИ")
        
        # Создаем содержимое вкладок
        self.create_games_tab()
        self.create_checks_tab()
        self.create_ai_tab()
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, padx=5, pady=10)
        
        backup_button = ttk.Button(control_frame, text="Создать резервную копию", 
                                 command=self.create_backup_with_message)
        backup_button.pack(side=tk.LEFT, padx=5)
        
        export_button = ttk.Button(control_frame, text="Экспорт данных", 
                                 command=self.export_data)
        export_button.pack(side=tk.LEFT, padx=5)
        
        import_button = ttk.Button(control_frame, text="Импорт данных", 
                                 command=self.import_data)
        import_button.pack(side=tk.LEFT, padx=5)
        
        docs_button = ttk.Button(control_frame, text="Документация", 
                               command=self.open_docs)
        docs_button.pack(side=tk.RIGHT, padx=5)
    
    def open_docs(self):
        """Открывает документацию в браузере"""
        webbrowser.open("https://github.com/your-repo/docs")
    
    def create_games_tab(self):
        # Статистика по блэкджеку
        bj_frame = ttk.LabelFrame(self.games_tab, text="Блэкджек", padding=10)
        bj_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(bj_frame, text="Победы:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.bj_wins_var = tk.IntVar()
        ttk.Entry(bj_frame, textvariable=self.bj_wins_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(bj_frame, text="Поражения:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.bj_losses_var = tk.IntVar()
        ttk.Entry(bj_frame, textvariable=self.bj_losses_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(bj_frame, text="Ничьи:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.bj_draws_var = tk.IntVar()
        ttk.Entry(bj_frame, textvariable=self.bj_draws_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(bj_frame, text="Заработок:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.bj_earnings_var = tk.IntVar()
        ttk.Entry(bj_frame, textvariable=self.bj_earnings_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=3)
        
        # Статистика по крестикам-ноликам
        ttt_frame = ttk.LabelFrame(self.games_tab, text="Крестики-нолики", padding=10)
        ttt_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(ttt_frame, text="Победы:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.ttt_wins_var = tk.IntVar()
        ttk.Entry(ttt_frame, textvariable=self.ttt_wins_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(ttt_frame, text="Поражения:").grid(row=1, column=0, sticky=tk.W, pady=3)
        self.ttt_losses_var = tk.IntVar()
        ttk.Entry(ttt_frame, textvariable=self.ttt_losses_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(ttt_frame, text="Ничьи:").grid(row=2, column=0, sticky=tk.W, pady=3)
        self.ttt_draws_var = tk.IntVar()
        ttk.Entry(ttt_frame, textvariable=self.ttt_draws_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=3)
        
        ttk.Label(ttt_frame, text="Заработок:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.ttt_earnings_var = tk.IntVar()
        ttk.Entry(ttt_frame, textvariable=self.ttt_earnings_var, width=10).grid(row=3, column=1, sticky=tk.W, pady=3)
        
        # Кнопка сохранения игровой статистики
        save_games_button = ttk.Button(self.games_tab, text="Сохранить игровую статистику", 
                                     command=self.save_game_stats)
        save_games_button.pack(pady=10)
    
    def create_checks_tab(self):
        # Создаем Treeview для отображения чеков
        checks_tree_frame = ttk.Frame(self.checks_tab)
        checks_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.checks_tree = ttk.Treeview(checks_tree_frame, 
                                      columns=("id", "creator", "amount", "activations", "total", "created"), 
                                      show="headings")
        
        self.checks_tree.heading("id", text="ID чека", anchor=tk.CENTER)
        self.checks_tree.heading("creator", text="Создатель", anchor=tk.CENTER)
        self.checks_tree.heading("amount", text="Сумма", anchor=tk.CENTER)
        self.checks_tree.heading("activations", text="Активаций", anchor=tk.CENTER)
        self.checks_tree.heading("total", text="Всего", anchor=tk.CENTER)
        self.checks_tree.heading("created", text="Дата создания", anchor=tk.CENTER)
        
        self.checks_tree.column("id", width=150, anchor=tk.CENTER)
        self.checks_tree.column("creator", width=100, anchor=tk.CENTER)
        self.checks_tree.column("amount", width=80, anchor=tk.CENTER)
        self.checks_tree.column("activations", width=80, anchor=tk.CENTER)
        self.checks_tree.column("total", width=80, anchor=tk.CENTER)
        self.checks_tree.column("created", width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(checks_tree_frame, orient=tk.VERTICAL, command=self.checks_tree.yview)
        self.checks_tree.configure(yscrollcommand=scrollbar.set)
        
        self.checks_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления чеками
        checks_buttons_frame = ttk.Frame(self.checks_tab)
        checks_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        delete_check_button = ttk.Button(checks_buttons_frame, text="Удалить чек", 
                                       command=self.delete_check)
        delete_check_button.pack(side=tk.LEFT, padx=5)
        
        refresh_checks_button = ttk.Button(checks_buttons_frame, text="Обновить список", 
                                         command=self.load_checks)
        refresh_checks_button.pack(side=tk.LEFT, padx=5)
    
    def create_ai_tab(self):
        # Создаем Treeview для отображения вопросов-ответов
        ai_tree_frame = ttk.Frame(self.ai_tab)
        ai_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.ai_tree = ttk.Treeview(ai_tree_frame, 
                                  columns=("id", "question", "answer", "created"), 
                                  show="headings")
        
        self.ai_tree.heading("id", text="ID", anchor=tk.CENTER)
        self.ai_tree.heading("question", text="Вопрос", anchor=tk.CENTER)
        self.ai_tree.heading("answer", text="Ответ", anchor=tk.CENTER)
        self.ai_tree.heading("created", text="Дата создания", anchor=tk.CENTER)
        
        self.ai_tree.column("id", width=50, anchor=tk.CENTER)
        self.ai_tree.column("question", width=250)
        self.ai_tree.column("answer", width=250)
        self.ai_tree.column("created", width=120, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(ai_tree_frame, orient=tk.VERTICAL, command=self.ai_tree.yview)
        self.ai_tree.configure(yscrollcommand=scrollbar.set)
        
        self.ai_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления обучением ИИ
        ai_buttons_frame = ttk.Frame(self.ai_tab)
        ai_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        add_ai_button = ttk.Button(ai_buttons_frame, text="Добавить вопрос-ответ", 
                                 command=self.add_ai_training)
        add_ai_button.pack(side=tk.LEFT, padx=5)
        
        delete_ai_button = ttk.Button(ai_buttons_frame, text="Удалить выбранное", 
                                    command=self.delete_ai_training)
        delete_ai_button.pack(side=tk.LEFT, padx=5)
        
        refresh_ai_button = ttk.Button(ai_buttons_frame, text="Обновить список", 
                                     command=self.load_ai_training)
        refresh_ai_button.pack(side=tk.LEFT, padx=5)
    
    def load_users(self):
        """Загружает список пользователей из базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Очищаем текущий список
            for item in self.users_tree.get_children():
                self.users_tree.delete(item)
            
            # Загружаем пользователей
            cursor.execute("SELECT id, subscribed, balance FROM users ORDER BY id")
            for row in cursor.fetchall():
                user_id, subscribed, balance = row
                sub_text = "Да" if subscribed else "Нет"
                self.users_tree.insert("", tk.END, values=(user_id, sub_text, balance))
            
            conn.close()
            
            # Загружаем чеки и обучение ИИ
            self.load_checks()
            self.load_ai_training()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить пользователей: {e}")
    
    def on_search(self, event=None):
        """Фильтрация пользователей по поисковому запросу"""
        search_term = self.search_var.get().lower()
        
        for item in self.users_tree.get_children():
            values = self.users_tree.item(item, "values")
            if search_term in values[0].lower() or search_term in values[1].lower() or search_term in values[2].lower():
                self.users_tree.item(item, tags=("match",))
                self.users_tree.selection_set(item)
            else:
                self.users_tree.item(item, tags=("no_match",))
        
        # Подсветка найденных элементов
        self.users_tree.tag_configure("match", background='#00ffff', foreground='#000000')
        self.users_tree.tag_configure("no_match", background='#1a1a3a', foreground='#ffffff')
    
    def on_user_select(self, event):
        """Обработчик выбора пользователя"""
        selected_item = self.users_tree.selection()
        if not selected_item:
            return
            
        user_id = self.users_tree.item(selected_item[0], "values")[0]
        self.current_user_id = user_id
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Загружаем основную информацию о пользователе
            cursor.execute("SELECT id, subscribed, balance, start_date, last_activity FROM users WHERE id = ?", (user_id,))
            user_data = cursor.fetchone()
            
            if user_data:
                self.id_var.set(user_data[0])
                self.subscribed_var.set(user_data[1])
                self.balance_var.set(user_data[2])
                self.start_date_var.set(user_data[3])
                self.last_activity_var.set(user_data[4] if user_data[4] else "Неизвестно")
            
            # Загружаем игровую статистику
            cursor.execute("SELECT game_type, wins, losses, draws, earnings FROM game_stats WHERE user_id = ?", (user_id,))
            game_stats = cursor.fetchall()
            
            # Сбрасываем значения
            self.bj_wins_var.set(0)
            self.bj_losses_var.set(0)
            self.bj_draws_var.set(0)
            self.bj_earnings_var.set(0)
            
            self.ttt_wins_var.set(0)
            self.ttt_losses_var.set(0)
            self.ttt_draws_var.set(0)
            self.ttt_earnings_var.set(0)
            
            # Заполняем статистику
            for stat in game_stats:
                game_type, wins, losses, draws, earnings = stat
                if game_type == "blackjack":
                    self.bj_wins_var.set(wins)
                    self.bj_losses_var.set(losses)
                    self.bj_draws_var.set(draws)
                    self.bj_earnings_var.set(earnings)
                elif game_type == "tictactoe":
                    self.ttt_wins_var.set(wins)
                    self.ttt_losses_var.set(losses)
                    self.ttt_draws_var.set(draws)
                    self.ttt_earnings_var.set(earnings)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные пользователя: {e}")
    
    def save_user_info(self):
        if not self.current_user_id:
            messagebox.showwarning("Предупреждение", "Пользователь не выбран")
            return
            
        try:
            conn = sqlite3.connect(self.local_db_path)  # Используем локальную копию
            cursor = conn.cursor()
            
            self.create_backup()  # Создаем резервную копию
            
            cursor.execute(
                "UPDATE users SET subscribed = ?, balance = ? WHERE id = ?",
                (self.subscribed_var.get(), self.balance_var.get(), self.current_user_id))
            
            conn.commit()  # Явное подтверждение изменений
            conn.close()
            
            self.upload_db()  # Загружаем изменения на сервер  <--- ЭТО ОСНОВНОЕ ИСПРАВЛЕНИЕ
            
            self.load_users()  # Обновляем список пользователей
            messagebox.showinfo("Успех", "Данные пользователя сохранены")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def save_game_stats(self):
        if not self.current_user_id:
            messagebox.showwarning("Предупреждение", "Пользователь не выбран")
            return
            
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            self.create_backup()
            
            # Обновляем статистику по блэкджеку
            cursor.execute(
                """INSERT OR IGNORE INTO game_stats 
                (user_id, game_type, wins, losses, draws, earnings) 
                VALUES (?, ?, 0, 0, 0, 0)""",
                (self.current_user_id, "blackjack"))
                
            cursor.execute(
                """UPDATE game_stats SET 
                wins = ?, 
                losses = ?, 
                draws = ?, 
                earnings = ? 
                WHERE user_id = ? AND game_type = ?""",
                (
                    self.bj_wins_var.get(),
                    self.bj_losses_var.get(),
                    self.bj_draws_var.get(),
                    self.bj_earnings_var.get(),
                    self.current_user_id,
                    "blackjack"
                )
            )
            
            # То же самое для крестиков-ноликов
            cursor.execute(
                """INSERT OR IGNORE INTO game_stats 
                (user_id, game_type, wins, losses, draws, earnings) 
                VALUES (?, ?, 0, 0, 0, 0)""",
                (self.current_user_id, "tictactoe"))
                
            cursor.execute(
                """UPDATE game_stats SET 
                wins = ?, 
                losses = ?, 
                draws = ?, 
                earnings = ? 
                WHERE user_id = ? AND game_type = ?""",
                (
                    self.ttt_wins_var.get(),
                    self.ttt_losses_var.get(),
                    self.ttt_draws_var.get(),
                    self.ttt_earnings_var.get(),
                    self.current_user_id,
                    "tictactoe"
                )
            )
            
            conn.commit()
            conn.close()
            
            self.upload_db()  # Добавляем загрузку на сервер  <--- ВАЖНОЕ ДОБАВЛЕНИЕ
            messagebox.showinfo("Успех", "Игровая статистика сохранена")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить статистику: {e}")
    
    def load_checks(self):
        """Загружает список чеков из базы данных"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Очищаем текущий список
            for item in self.checks_tree.get_children():
                self.checks_tree.delete(item)
            
            # Загружаем чеки
            cursor.execute("""
                SELECT c.id, u.id, c.amount, c.activations_left, c.activations_left, c.created_at 
                FROM checks c
                LEFT JOIN users u ON c.creator_id = u.id
                ORDER BY c.created_at DESC
            """)
            
            for row in cursor.fetchall():
                check_id, creator_id, amount, activations, total, created = row
                self.checks_tree.insert("", tk.END, values=(check_id, creator_id, amount, activations, total, created))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить чеки: {e}")
    
    def delete_check(self):
        """Удаляет выбранный чек"""
        selected_item = self.checks_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Чек не выбран")
            return
            
        check_id = self.checks_tree.item(selected_item[0], "values")[0]
        
        if messagebox.askyesno("Подтверждение", f"Удалить чек {check_id}?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Создаем резервную копию перед изменением
                self.create_backup()
                
                # Удаляем чек и его активации
                cursor.execute("DELETE FROM checks WHERE id = ?", (check_id,))
                cursor.execute("DELETE FROM check_activations WHERE check_id = ?", (check_id,))
                
                conn.commit()
                conn.close()
                
                # Обновляем список
                self.load_checks()
                
                messagebox.showinfo("Успех", "Чек удален")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить чек: {e}")
    
    def load_ai_training(self):
        """Загружает список вопросов-ответов для обучения ИИ"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Очищаем текущий список
            for item in self.ai_tree.get_children():
                self.ai_tree.delete(item)
            
            # Загружаем обучение ИИ
            cursor.execute("SELECT id, question, answer, created_at FROM ai_training ORDER BY created_at DESC")
            
            for row in cursor.fetchall():
                item_id, question, answer, created = row
                self.ai_tree.insert("", tk.END, values=(item_id, question, answer, created))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить обучение ИИ: {e}")
    
    def add_ai_training(self):
        """Добавляет новый вопрос-ответ для обучения ИИ"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить вопрос-ответ")
        dialog.geometry("600x400")
        dialog.configure(bg=self.bg_color)
        
        ttk.Label(dialog, text="Вопрос:", font=self.bold_font).pack(padx=5, pady=5)
        question_entry = tk.Text(dialog, height=5, width=70, bg=self.entry_bg, fg=self.fg_color)
        question_entry.pack(padx=5, pady=5)
        
        ttk.Label(dialog, text="Ответ:", font=self.bold_font).pack(padx=5, pady=5)
        answer_entry = tk.Text(dialog, height=5, width=70, bg=self.entry_bg, fg=self.fg_color)
        answer_entry.pack(padx=5, pady=5)
        
        def save():
            question = question_entry.get("1.0", tk.END).strip()
            answer = answer_entry.get("1.0", tk.END).strip()
            
            if not question or not answer:
                messagebox.showwarning("Предупреждение", "Вопрос и ответ не могут быть пустыми")
                return
                
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Создаем резервную копию перед изменением
                self.create_backup()
                
                # Добавляем вопрос-ответ
                cursor.execute(
                    "INSERT INTO ai_training (question, answer, created_at) VALUES (?, ?, ?)",
                    (question.lower(), answer.lower(), datetime.now().isoformat())
                )
                
                conn.commit()
                conn.close()
                
                # Обновляем список
                self.load_ai_training()
                
                dialog.destroy()
                messagebox.showinfo("Успех", "Вопрос-ответ добавлен")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось добавить вопрос-ответ: {e}")
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Сохранить", command=save).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_ai_training(self):
        """Удаляет выбранный вопрос-ответ"""
        selected_item = self.ai_tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Элемент не выбран")
            return
            
        item_id = self.ai_tree.item(selected_item[0], "values")[0]
        
        if messagebox.askyesno("Подтверждение", "Удалить выбранный вопрос-ответ?"):
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                # Создаем резервную копию перед изменением
                self.create_backup()
                
                # Удаляем вопрос-ответ
                cursor.execute("DELETE FROM ai_training WHERE id = ?", (item_id,))
                
                conn.commit()
                conn.close()
                
                # Обновляем список
                self.load_ai_training()
                
                messagebox.showinfo("Успех", "Вопрос-ответ удален")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось удалить вопрос-ответ: {e}")
    
    def create_backup_with_message(self):
        """Создает резервную копию и показывает сообщение"""
        backup_path = self.create_backup()
        messagebox.showinfo("Резервная копия", f"Резервная копия создана:\n{backup_path}")
    
    def export_data(self):
        """Экспортирует данные в JSON файл"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Сохранить данные как"
        )
        
        if not file_path:
            return
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            data = {
                "users": [],
                "game_stats": [],
                "checks": [],
                "check_activations": [],
                "ai_training": [],
                "tiktok_mod": []
            }
            
            # Экспортируем пользователей
            cursor.execute("SELECT * FROM users")
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                data["users"].append(dict(zip(columns, row)))
            
            # Экспортируем игровую статистику
            cursor.execute("SELECT * FROM game_stats")
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                data["game_stats"].append(dict(zip(columns, row)))
            
            # Экспортируем чеки
            cursor.execute("SELECT * FROM checks")
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                data["checks"].append(dict(zip(columns, row)))
            
            # Экспортируем активации чеков
            cursor.execute("SELECT * FROM check_activations")
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                data["check_activations"].append(dict(zip(columns, row)))
            
            # Экспортируем обучение ИИ
            cursor.execute("SELECT * FROM ai_training")
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                data["ai_training"].append(dict(zip(columns, row)))
            
            # Экспортируем TikTok Mod
            cursor.execute("SELECT * FROM tiktok_mod")
            columns = [column[0] for column in cursor.description]
            for row in cursor.fetchall():
                data["tiktok_mod"].append(dict(zip(columns, row)))
            
            conn.close()
            
            # Сохраняем в файл
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Успех", f"Данные экспортированы в {file_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")
    
    def import_data(self):
        """Импортирует данные из JSON файла"""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Выберите файл для импорта"
        )
        
        if not file_path:
            return
            
        if not messagebox.askyesno("Подтверждение", "Это перезапишет текущие данные. Продолжить?"):
            return
            
        try:
            # Создаем резервную копию перед импортом
            backup_path = self.create_backup()
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Очищаем таблицы
            cursor.execute("DELETE FROM users")
            cursor.execute("DELETE FROM game_stats")
            cursor.execute("DELETE FROM checks")
            cursor.execute("DELETE FROM check_activations")
            cursor.execute("DELETE FROM ai_training")
            cursor.execute("DELETE FROM tiktok_mod")
            
            # Импортируем пользователей
            if "users" in data:
                for user in data["users"]:
                    columns = ", ".join(user.keys())
                    placeholders = ", ".join(["?"] * len(user))
                    cursor.execute(
                        f"INSERT INTO users ({columns}) VALUES ({placeholders})",
                        list(user.values())
                    )
            
            # Импортируем игровую статистику
            if "game_stats" in data:
                for stat in data["game_stats"]:
                    columns = ", ".join(stat.keys())
                    placeholders = ", ".join(["?"] * len(stat))
                    cursor.execute(
                        f"INSERT INTO game_stats ({columns}) VALUES ({placeholders})",
                        list(stat.values())
                    )
            
            # Импортируем чеки
            if "checks" in data:
                for check in data["checks"]:
                    columns = ", ".join(check.keys())
                    placeholders = ", ".join(["?"] * len(check))
                    cursor.execute(
                        f"INSERT INTO checks ({columns}) VALUES ({placeholders})",
                        list(check.values())
                    )
            
            # Импортируем активации чеков
            if "check_activations" in data:
                for activation in data["check_activations"]:
                    columns = ", ".join(activation.keys())
                    placeholders = ", ".join(["?"] * len(activation))
                    cursor.execute(
                        f"INSERT INTO check_activations ({columns}) VALUES ({placeholders})",
                        list(activation.values())
                    )
            
            # Импортируем обучение ИИ
            if "ai_training" in data:
                for training in data["ai_training"]:
                    columns = ", ".join(training.keys())
                    placeholders = ", ".join(["?"] * len(training))
                    cursor.execute(
                        f"INSERT INTO ai_training ({columns}) VALUES ({placeholders})",
                        list(training.values())
                    )
            
            # Импортируем TikTok Mod
            if "tiktok_mod" in data:
                for mod in data["tiktok_mod"]:
                    columns = ", ".join(mod.keys())
                    placeholders = ", ".join(["?"] * len(mod))
                    cursor.execute(
                        f"INSERT INTO tiktok_mod ({columns}) VALUES ({placeholders})",
                        list(mod.values())
                    )
            
            conn.commit()
            conn.close()
            
            # Обновляем интерфейс
            self.load_users()
            
            messagebox.showinfo("Успех", f"Данные импортированы из {file_path}\nРезервная копия сохранена в {backup_path}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Установка иконки (если есть)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    app = BotDatabaseEditor(root)
    root.mainloop()