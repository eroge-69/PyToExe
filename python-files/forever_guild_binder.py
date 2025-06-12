import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import mysql.connector
from mysql.connector import Error
import hashlib
import json
import threading
import time
import pyautogui
import keyboard
from datetime import datetime
import os
from PIL import Image, ImageTk
import requests
from io import BytesIO

class ForeverGuildBinder:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Forever Guild - Binder")
        self.root.geometry("900x700")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, False)
        
        # Цвета темы Forever Guild
        self.colors = {
            'bg': '#1a1a1a',
            'card_bg': '#2d2d2d',
            'accent': '#ff6b35',  # Оранжевый
            'accent_hover': '#ff8c42',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'success': '#4caf50',
            'error': '#f44336',
            'border': '#404040'
        }
        
        # Переменные
        self.current_user = None
        self.is_admin = False
        self.db_connection = None
        self.binder_active = False
        self.binder_thread = None
        self.selected_profile = None
        
        # Настройки базы данных
        self.db_config = {
            'host': '77.246.159.43',
            'database': 'Forever',
            'user': 'Forever',
            'password': 'lM6jB0eG9x'
        }
        
        self.setup_database()
        self.create_login_interface()
        
    def setup_database(self):
        """Настройка базы данных и создание таблиц"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Создание таблицы пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(64) NOT NULL,
                    is_admin BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Создание таблицы профилей биндов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bind_profiles (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    profile_name VARCHAR(100) NOT NULL,
                    bind_text TEXT NOT NULL,
                    cooldown_seconds INT DEFAULT 5,
                    hotkey VARCHAR(20) DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Создание таблицы логов
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT,
                    action VARCHAR(100) NOT NULL,
                    details TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            
            # Добавление администратора по умолчанию
            admin_password = self.hash_password("094404")
            cursor.execute("""
                INSERT IGNORE INTO users (username, password_hash, is_admin) 
                VALUES (%s, %s, %s)
            """, ("SlaudGG", admin_password, True))
            
            connection.commit()
            cursor.close()
            connection.close()
            
        except Error as e:
            messagebox.showerror("Database Error", f"Ошибка подключения к базе данных: {e}")
    
    def hash_password(self, password):
        """Хеширование пароля"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_login_interface(self):
        """Создание интерфейса входа"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Главный контейнер
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(expand=True, fill='both')
        
        # Логотип и заголовок
        logo_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        logo_frame.pack(pady=50)
        
        # Заголовок
        title_label = tk.Label(
            logo_frame, 
            text="FOREVER GUILD", 
            font=("Arial", 28, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['bg']
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            logo_frame,
            text="Professional Binder System",
            font=("Arial", 12),
            fg=self.colors['text_secondary'],
            bg=self.colors['bg']
        )
        subtitle_label.pack(pady=5)
        
        # Форма входа
        login_frame = tk.Frame(main_frame, bg=self.colors['card_bg'], relief='raised', bd=2)
        login_frame.pack(pady=30, padx=100, fill='x')
        
        # Заголовок формы
        form_title = tk.Label(
            login_frame,
            text="Авторизация",
            font=("Arial", 16, "bold"),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        )
        form_title.pack(pady=20)
        
        # Поле логина
        tk.Label(
            login_frame,
            text="Логин:",
            font=("Arial", 11),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        ).pack(pady=(10, 5))
        
        self.username_entry = tk.Entry(
            login_frame,
            font=("Arial", 12),
            width=25,
            bg='#404040',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            bd=5
        )
        self.username_entry.pack(pady=5, ipady=8)
        
        # Поле пароля
        tk.Label(
            login_frame,
            text="Пароль:",
            font=("Arial", 11),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        ).pack(pady=(10, 5))
        
        self.password_entry = tk.Entry(
            login_frame,
            font=("Arial", 12),
            width=25,
            bg='#404040',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            bd=5,
            show='*'
        )
        self.password_entry.pack(pady=5, ipady=8)
        
        # Кнопка входа
        login_btn = tk.Button(
            login_frame,
            text="ВОЙТИ",
            font=("Arial", 12, "bold"),
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            width=20,
            pady=10,
            command=self.login,
            cursor='hand2'
        )
        login_btn.pack(pady=20)
        
        # Статус
        self.status_label = tk.Label(
            login_frame,
            text="",
            font=("Arial", 10),
            bg=self.colors['card_bg']
        )
        self.status_label.pack(pady=5)
        
        # Привязка Enter к кнопке входа
        self.root.bind('<Return>', lambda e: self.login())
        
        # Фокус на поле логина
        self.username_entry.focus()
    
    def login(self):
        """Обработка входа"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.show_status("Заполните все поля", "error")
            return
        
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute("""
                SELECT id, username, is_admin, is_active 
                FROM users 
                WHERE username = %s AND password_hash = %s
            """, (username, password_hash))
            
            user = cursor.fetchone()
            
            if user and user[3]:  # Проверка активности
                self.current_user = {
                    'id': user[0],
                    'username': user[1],
                    'is_admin': user[2]
                }
                self.is_admin = user[2]
                
                # Обновление времени последнего входа
                cursor.execute("""
                    UPDATE users SET last_login = NOW() WHERE id = %s
                """, (user[0],))
                
                # Лог входа
                cursor.execute("""
                    INSERT INTO activity_logs (user_id, action, details) 
                    VALUES (%s, %s, %s)
                """, (user[0], "login", f"Successful login from {username}"))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                self.create_main_interface()
                
            else:
                self.show_status("Неверный логин или пароль", "error")
                
        except Error as e:
            self.show_status(f"Ошибка подключения: {e}", "error")
    
    def show_status(self, message, status_type="info"):
        """Отображение статуса"""
        colors = {
            "info": self.colors['text'],
            "error": self.colors['error'],
            "success": self.colors['success']
        }
        
        self.status_label.config(text=message, fg=colors.get(status_type, self.colors['text']))
        
        # Автоскрытие через 3 секунды
        self.root.after(3000, lambda: self.status_label.config(text=""))
    
    def create_main_interface(self):
        """Создание основного интерфейса"""
        # Очистка окна
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.geometry("1200x800")
        
        # Верхняя панель
        header_frame = tk.Frame(self.root, bg=self.colors['card_bg'], height=60)
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        header_frame.pack_propagate(False)
        
        # Логотип и приветствие
        tk.Label(
            header_frame,
            text=f"Forever Guild Binder | Добро пожаловать, {self.current_user['username']}",
            font=("Arial", 14, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack(side='left', padx=20, pady=15)
        
        # Кнопка выхода
        logout_btn = tk.Button(
            header_frame,
            text="Выйти",
            font=("Arial", 10),
            bg=self.colors['error'],
            fg='white',
            relief='flat',
            command=self.logout,
            cursor='hand2'
        )
        logout_btn.pack(side='right', padx=20, pady=15)
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Левая панель - Биндер
        left_panel = tk.Frame(main_container, bg=self.colors['card_bg'], width=600)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        self.create_binder_panel(left_panel)
        
        # Правая панель - Профили и админка
        right_panel = tk.Frame(main_container, bg=self.colors['card_bg'], width=400)
        right_panel.pack(side='right', fill='both', padx=(5, 0))
        
        self.create_right_panel(right_panel)
    
    def create_binder_panel(self, parent):
        """Создание панели биндера"""
        # Заголовок
        title_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        title_frame.pack(fill='x', padx=20, pady=20)
        
        tk.Label(
            title_frame,
            text="🔥 БИНДЕР",
            font=("Arial", 18, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack()
        
        # Текст для отправки
        text_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        text_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Label(
            text_frame,
            text="Текст сообщения:",
            font=("Arial", 11, "bold"),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        ).pack(anchor='w')
        
        self.message_text = tk.Text(
            text_frame,
            font=("Arial", 11),
            height=8,
            bg='#404040',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            bd=5,
            wrap='word'
        )
        self.message_text.pack(fill='x', pady=5)
        
        # Настройки
        settings_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        settings_frame.pack(fill='x', padx=20, pady=10)
        
        # Кулдаун
        cooldown_frame = tk.Frame(settings_frame, bg=self.colors['card_bg'])
        cooldown_frame.pack(fill='x', pady=5)
        
        tk.Label(
            cooldown_frame,
            text="Кулдаун (сек):",
            font=("Arial", 11),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        ).pack(side='left')
        
        self.cooldown_var = tk.StringVar(value="5")
        cooldown_entry = tk.Entry(
            cooldown_frame,
            textvariable=self.cooldown_var,
            font=("Arial", 11),
            width=10,
            bg='#404040',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            bd=3
        )
        cooldown_entry.pack(side='right')
        
        # Горячая клавиша
        hotkey_frame = tk.Frame(settings_frame, bg=self.colors['card_bg'])
        hotkey_frame.pack(fill='x', pady=5)
        
        tk.Label(
            hotkey_frame,
            text="Горячая клавиша:",
            font=("Arial", 11),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        ).pack(side='left')
        
        self.hotkey_var = tk.StringVar(value="F1")
        hotkey_entry = tk.Entry(
            hotkey_frame,
            textvariable=self.hotkey_var,
            font=("Arial", 11),
            width=10,
            bg='#404040',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief='flat',
            bd=3
        )
        hotkey_entry.pack(side='right')
        
        # Кнопки управления
        control_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        control_frame.pack(fill='x', padx=20, pady=20)
        
        self.start_btn = tk.Button(
            control_frame,
            text="🚀 ЗАПУСТИТЬ",
            font=("Arial", 12, "bold"),
            bg=self.colors['success'],
            fg='white',
            relief='flat',
            width=15,
            pady=10,
            command=self.start_binder,
            cursor='hand2'
        )
        self.start_btn.pack(side='left', padx=(0, 10))
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ ОСТАНОВИТЬ",
            font=("Arial", 12, "bold"),
            bg=self.colors['error'],
            fg='white',
            relief='flat',
            width=15,
            pady=10,
            command=self.stop_binder,
            cursor='hand2',
            state='disabled'
        )
        self.stop_btn.pack(side='left', padx=10)
        
        # Статус биндера
        self.binder_status = tk.Label(
            parent,
            text="Статус: Остановлен",
            font=("Arial", 11),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        self.binder_status.pack(pady=10)
        
        # Последнее сообщение
        self.last_message_time = tk.Label(
            parent,
            text="",
            font=("Arial", 10),
            fg=self.colors['text_secondary'],
            bg=self.colors['card_bg']
        )
        self.last_message_time.pack()
    
    def create_right_panel(self, parent):
        """Создание правой панели"""
        notebook = ttk.Notebook(parent)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Стили для notebook
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['card_bg'])
        style.configure('TNotebook.Tab', padding=[20, 10])
        
        # Вкладка профилей
        profiles_frame = tk.Frame(notebook, bg=self.colors['card_bg'])
        notebook.add(profiles_frame, text='Профили')
        self.create_profiles_tab(profiles_frame)
        
        # Админ-панель (только для админов)
        if self.is_admin:
            admin_frame = tk.Frame(notebook, bg=self.colors['card_bg'])
            notebook.add(admin_frame, text='Админ-панель')
            self.create_admin_tab(admin_frame)
    
    def create_profiles_tab(self, parent):
        """Создание вкладки профилей"""
        # Заголовок
        tk.Label(
            parent,
            text="Профили биндов",
            font=("Arial", 14, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack(pady=10)
        
        # Список профилей
        profiles_list_frame = tk.Frame(parent, bg=self.colors['card_bg'])
        profiles_list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Скроллбар для списка
        scrollbar = tk.Scrollbar(profiles_list_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.profiles_listbox = tk.Listbox(
            profiles_list_frame,
            font=("Arial", 10),
            bg='#404040',
            fg=self.colors['text'],
            selectbackground=self.colors['accent'],
            relief='flat',
            bd=0,
            yscrollcommand=scrollbar.set
        )
        self.profiles_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.profiles_listbox.yview)
        
        # Кнопки управления профилями
        profile_buttons = tk.Frame(parent, bg=self.colors['card_bg'])
        profile_buttons.pack(fill='x', padx=10, pady=10)
        
        tk.Button(
            profile_buttons,
            text="Загрузить",
            font=("Arial", 9),
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            command=self.load_profile,
            cursor='hand2'
        ).pack(side='left', padx=2)
        
        tk.Button(
            profile_buttons,
            text="Сохранить",
            font=("Arial", 9),
            bg=self.colors['success'],
            fg='white',
            relief='flat',
            command=self.save_profile,
            cursor='hand2'
        ).pack(side='left', padx=2)
        
        tk.Button(
            profile_buttons,
            text="Удалить",
            font=("Arial", 9),
            bg=self.colors['error'],
            fg='white',
            relief='flat',
            command=self.delete_profile,
            cursor='hand2'
        ).pack(side='left', padx=2)
        
        self.load_profiles()
    
    def create_admin_tab(self, parent):
        """Создание админ-панели"""
        # Заголовок
        tk.Label(
            parent,
            text="⚙️ Админ-панель",
            font=("Arial", 14, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack(pady=10)
        
        # Управление пользователями
        users_frame = tk.LabelFrame(
            parent,
            text="Пользователи",
            font=("Arial", 11, "bold"),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        )
        users_frame.pack(fill='x', padx=10, pady=5)
        
        # Список пользователей
        self.users_listbox = tk.Listbox(
            users_frame,
            font=("Arial", 9),
            height=8,
            bg='#404040',
            fg=self.colors['text'],
            selectbackground=self.colors['accent'],
            relief='flat'
        )
        self.users_listbox.pack(fill='x', padx=5, pady=5)
        
        # Кнопки управления пользователями
        user_buttons = tk.Frame(users_frame, bg=self.colors['card_bg'])
        user_buttons.pack(fill='x', padx=5, pady=5)
        
        tk.Button(
            user_buttons,
            text="Добавить",
            font=("Arial", 8),
            bg=self.colors['success'],
            fg='white',
            relief='flat',
            command=self.add_user_dialog,
            cursor='hand2'
        ).pack(side='left', padx=2)
        
        tk.Button(
            user_buttons,
            text="Изменить",
            font=("Arial", 8),
            bg=self.colors['accent'],
            fg='white',
            relief='flat',
            command=self.edit_user_dialog,
            cursor='hand2'
        ).pack(side='left', padx=2)
        
        tk.Button(
            user_buttons,
            text="Удалить",
            font=("Arial", 8),
            bg=self.colors['error'],
            fg='white',
            relief='flat',
            command=self.delete_user,
            cursor='hand2'
        ).pack(side='left', padx=2)
        
        # Логи активности
        logs_frame = tk.LabelFrame(
            parent,
            text="Логи активности",
            font=("Arial", 11, "bold"),
            fg=self.colors['text'],
            bg=self.colors['card_bg']
        )
        logs_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.logs_text = tk.Text(
            logs_frame,
            font=("Courier", 8),
            height=10,
            bg='#404040',
            fg=self.colors['text'],
            relief='flat',
            state='disabled'
        )
        self.logs_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.load_users()
        self.load_logs()
    
    def start_binder(self):
        """Запуск биндера"""
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Предупреждение", "Введите текст сообщения!")
            return
        
        try:
            cooldown = int(self.cooldown_var.get())
            if cooldown < 1:
                raise ValueError("Кулдаун должен быть больше 0")
        except ValueError as e:
            messagebox.showerror("Ошибка", f"Неверное значение кулдауна: {e}")
            return
        
        self.binder_active = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.binder_status.config(text="Статус: Активен", fg=self.colors['success'])
        
        # Запуск биндера в отдельном потоке
        self.binder_thread = threading.Thread(target=self.binder_worker, daemon=True)
        self.binder_thread.start()
        
        # Регистрация горячей клавиши
        hotkey = self.hotkey_var.get()
        if hotkey:
            try:
                keyboard.add_hotkey(hotkey, self.send_message)
            except:
                pass
        
        # Лог активности
        self.log_activity("binder_start", f"Started binder with cooldown {cooldown}s")
    
    def stop_binder(self):
        """Остановка биндера"""
        self.binder_active = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.binder_status.config(text="Статус: Остановлен", fg=self.colors['text_secondary'])
        
        # Удаление горячих клавиш
        try:
            keyboard.unhook_all()
        except:
            pass
        
        self.log_activity("binder_stop", "Stopped binder")
    
    def binder_worker(self):
        """Рабочий поток биндера"""
        while self.binder_active:
            time.sleep(0.1)  # Небольшая задержка для экономии ресурсов
    
    def send_message(self):
        """Отправка сообщения"""
        if not self.binder_active:
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            return
        
        try:
            cooldown = int(self.cooldown_var.get())
            
            # Проверка кулдауна
            current_time = time.time()
            if hasattr(self, 'last_send_time'):
                if current_time - self.last_send_time < cooldown:
                    remaining = cooldown - (current_time - self.last_send_time)
                    self.root.after(0, lambda: self.last_message_time.config(
                        text=f"Кулдаун: {remaining:.1f}с", 
                        fg=self.colors['error']
                    ))
                    return
            
            # Отправка сообщения
            pyautogui.typewrite(message)
            pyautogui.press('enter')
            
            self.last_send_time = current_time
            
            # Обновление UI
            self.root.after(0, lambda: self.last_message_time.config(
                text=f"Отправлено: {datetime.now().strftime('%H:%M:%S')}", 
                fg=self.colors['success']
            ))
            
            # Лог отправки
            self.log_activity("message_sent", f"Message sent: {message[:50]}...")
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка отправки: {e}"))
    
    def load_profiles(self):
        """Загрузка профилей пользователя"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, profile_name, bind_text, cooldown_seconds, hotkey 
                FROM bind_profiles 
                WHERE user_id = %s
                ORDER BY profile_name
            """, (self.current_user['id'],))
            
            profiles = cursor.fetchall()
            
            self.profiles_listbox.delete(0, tk.END)
            self.profiles_data = {}
            
            for profile in profiles:
                profile_id, name, text, cooldown, hotkey = profile
                self.profiles_listbox.insert(tk.END, name)
                self.profiles_data[name] = {
                    'id': profile_id,
                    'text': text,
                    'cooldown': cooldown,
                    'hotkey': hotkey
                }
            
            cursor.close()
            connection.close()
            
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки профилей: {e}")
    
    def save_profile(self):
        """Сохранение профиля"""
        profile_name = tk.simpledialog.askstring("Сохранение профиля", "Название профиля:")
        if not profile_name:
            return
        
        message = self.message_text.get("1.0", tk.END).strip()
        if not message:
            messagebox.showwarning("Предупреждение", "Введите текст сообщения!")
            return
        
        try:
            cooldown = int(self.cooldown_var.get())
            hotkey = self.hotkey_var.get()
            
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Проверка существования профиля
            cursor.execute("""
                SELECT id FROM bind_profiles 
                WHERE user_id = %s AND profile_name = %s
            """, (self.current_user['id'], profile_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Обновление существующего профиля
                cursor.execute("""
                    UPDATE bind_profiles 
                    SET bind_text = %s, cooldown_seconds = %s, hotkey = %s 
                    WHERE id = %s
                """, (message, cooldown, hotkey, existing[0]))
                messagebox.showinfo("Успех", f"Профиль '{profile_name}' обновлен!")
            else:
                # Создание нового профиля
                cursor.execute("""
                    INSERT INTO bind_profiles (user_id, profile_name, bind_text, cooldown_seconds, hotkey) 
                    VALUES (%s, %s, %s, %s, %s)
                """, (self.current_user['id'], profile_name, message, cooldown, hotkey))
                messagebox.showinfo("Успех", f"Профиль '{profile_name}' сохранен!")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            self.load_profiles()
            self.log_activity("profile_save", f"Saved profile: {profile_name}")
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное значение кулдауна!")
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка сохранения профиля: {e}")
    
    def load_profile(self):
        """Загрузка выбранного профиля"""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль для загрузки!")
            return
        
        profile_name = self.profiles_listbox.get(selection[0])
        profile_data = self.profiles_data.get(profile_name)
        
        if profile_data:
            # Загрузка данных в интерфейс
            self.message_text.delete("1.0", tk.END)
            self.message_text.insert("1.0", profile_data['text'])
            self.cooldown_var.set(str(profile_data['cooldown']))
            self.hotkey_var.set(profile_data['hotkey'])
            
            self.selected_profile = profile_name
            messagebox.showinfo("Успех", f"Профиль '{profile_name}' загружен!")
            self.log_activity("profile_load", f"Loaded profile: {profile_name}")
    
    def delete_profile(self):
        """Удаление профиля"""
        selection = self.profiles_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите профиль для удаления!")
            return
        
        profile_name = self.profiles_listbox.get(selection[0])
        
        if messagebox.askyesno("Подтверждение", f"Удалить профиль '{profile_name}'?"):
            try:
                connection = mysql.connector.connect(**self.db_config)
                cursor = connection.cursor()
                
                profile_id = self.profiles_data[profile_name]['id']
                cursor.execute("DELETE FROM bind_profiles WHERE id = %s", (profile_id,))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                self.load_profiles()
                messagebox.showinfo("Успех", f"Профиль '{profile_name}' удален!")
                self.log_activity("profile_delete", f"Deleted profile: {profile_name}")
                
            except Error as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления профиля: {e}")
    
    def load_users(self):
        """Загрузка списка пользователей"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT id, username, is_admin, is_active, last_login, created_at 
                FROM users 
                ORDER BY username
            """)
            
            users = cursor.fetchall()
            
            self.users_listbox.delete(0, tk.END)
            self.users_data = {}
            
            for user in users:
                user_id, username, is_admin, is_active, last_login, created_at = user
                status = "✓" if is_active else "✗"
                admin_mark = "👑" if is_admin else ""
                display_name = f"{status} {username} {admin_mark}"
                
                self.users_listbox.insert(tk.END, display_name)
                self.users_data[display_name] = {
                    'id': user_id,
                    'username': username,
                    'is_admin': is_admin,
                    'is_active': is_active,
                    'last_login': last_login,
                    'created_at': created_at
                }
            
            cursor.close()
            connection.close()
            
        except Error as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки пользователей: {e}")
    
    def add_user_dialog(self):
        """Диалог добавления пользователя"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить пользователя")
        dialog.geometry("400x300")
        dialog.configure(bg=self.colors['card_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрирование окна
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Заголовок
        tk.Label(
            dialog,
            text="Добавить нового пользователя",
            font=("Arial", 14, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack(pady=20)
        
        # Поля ввода
        fields_frame = tk.Frame(dialog, bg=self.colors['card_bg'])
        fields_frame.pack(pady=20, padx=40, fill='x')
        
        # Логин
        tk.Label(fields_frame, text="Логин:", fg=self.colors['text'], bg=self.colors['card_bg']).pack(anchor='w')
        username_entry = tk.Entry(fields_frame, font=("Arial", 11), bg='#404040', fg=self.colors['text'])
        username_entry.pack(fill='x', pady=(0, 10))
        
        # Пароль
        tk.Label(fields_frame, text="Пароль:", fg=self.colors['text'], bg=self.colors['card_bg']).pack(anchor='w')
        password_entry = tk.Entry(fields_frame, font=("Arial", 11), bg='#404040', fg=self.colors['text'], show='*')
        password_entry.pack(fill='x', pady=(0, 10))
        
        # Админ чекбокс
        admin_var = tk.BooleanVar()
        tk.Checkbutton(
            fields_frame,
            text="Права администратора",
            variable=admin_var,
            fg=self.colors['text'],
            bg=self.colors['card_bg'],
            selectcolor='#404040'
        ).pack(anchor='w', pady=10)
        
        # Кнопки
        buttons_frame = tk.Frame(dialog, bg=self.colors['card_bg'])
        buttons_frame.pack(pady=20)
        
        def save_user():
            username = username_entry.get().strip()
            password = password_entry.get()
            
            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return
            
            try:
                connection = mysql.connector.connect(**self.db_config)
                cursor = connection.cursor()
                
                password_hash = self.hash_password(password)
                cursor.execute("""
                    INSERT INTO users (username, password_hash, is_admin) 
                    VALUES (%s, %s, %s)
                """, (username, password_hash, admin_var.get()))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                self.load_users()
                self.log_activity("user_add", f"Added user: {username}")
                messagebox.showinfo("Успех", f"Пользователь '{username}' добавлен!")
                dialog.destroy()
                
            except mysql.connector.IntegrityError:
                messagebox.showerror("Ошибка", "Пользователь с таким логином уже существует!")
            except Error as e:
                messagebox.showerror("Ошибка", f"Ошибка добавления пользователя: {e}")
        
        tk.Button(
            buttons_frame,
            text="Сохранить",
            font=("Arial", 11),
            bg=self.colors['success'],
            fg='white',
            relief='flat',
            command=save_user,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Arial", 11),
            bg=self.colors['error'],
            fg='white',
            relief='flat',
            command=dialog.destroy,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        username_entry.focus()
    
    def edit_user_dialog(self):
        """Диалог редактирования пользователя"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для редактирования!")
            return
        
        selected_display = self.users_listbox.get(selection[0])
        user_data = self.users_data[selected_display]
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Редактировать пользователя")
        dialog.geometry("400x350")
        dialog.configure(bg=self.colors['card_bg'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Центрирование окна
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Заголовок
        tk.Label(
            dialog,
            text=f"Редактировать: {user_data['username']}",
            font=("Arial", 14, "bold"),
            fg=self.colors['accent'],
            bg=self.colors['card_bg']
        ).pack(pady=20)
        
        # Поля ввода
        fields_frame = tk.Frame(dialog, bg=self.colors['card_bg'])
        fields_frame.pack(pady=20, padx=40, fill='x')
        
        # Новый пароль
        tk.Label(fields_frame, text="Новый пароль (оставьте пустым, чтобы не менять):", 
                fg=self.colors['text'], bg=self.colors['card_bg']).pack(anchor='w')
        password_entry = tk.Entry(fields_frame, font=("Arial", 11), bg='#404040', fg=self.colors['text'], show='*')
        password_entry.pack(fill='x', pady=(0, 10))
        
        # Админ чекбокс
        admin_var = tk.BooleanVar(value=user_data['is_admin'])
        tk.Checkbutton(
            fields_frame,
            text="Права администратора",
            variable=admin_var,
            fg=self.colors['text'],
            bg=self.colors['card_bg'],
            selectcolor='#404040'
        ).pack(anchor='w', pady=10)
        
        # Активность чекбокс
        active_var = tk.BooleanVar(value=user_data['is_active'])
        tk.Checkbutton(
            fields_frame,
            text="Активный пользователь",
            variable=active_var,
            fg=self.colors['text'],
            bg=self.colors['card_bg'],
            selectcolor='#404040'
        ).pack(anchor='w', pady=5)
        
        # Кнопки
        buttons_frame = tk.Frame(dialog, bg=self.colors['card_bg'])
        buttons_frame.pack(pady=20)
        
        def update_user():
            new_password = password_entry.get()
            
            try:
                connection = mysql.connector.connect(**self.db_config)
                cursor = connection.cursor()
                
                if new_password:
                    password_hash = self.hash_password(new_password)
                    cursor.execute("""
                        UPDATE users 
                        SET password_hash = %s, is_admin = %s, is_active = %s 
                        WHERE id = %s
                    """, (password_hash, admin_var.get(), active_var.get(), user_data['id']))
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET is_admin = %s, is_active = %s 
                        WHERE id = %s
                    """, (admin_var.get(), active_var.get(), user_data['id']))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                self.load_users()
                self.log_activity("user_edit", f"Edited user: {user_data['username']}")
                messagebox.showinfo("Успех", f"Пользователь '{user_data['username']}' обновлен!")
                dialog.destroy()
                
            except Error as e:
                messagebox.showerror("Ошибка", f"Ошибка обновления пользователя: {e}")
        
        tk.Button(
            buttons_frame,
            text="Сохранить",
            font=("Arial", 11),
            bg=self.colors['success'],
            fg='white',
            relief='flat',
            command=update_user,
            cursor='hand2'
        ).pack(side='left', padx=10)
        
        tk.Button(
            buttons_frame,
            text="Отмена",
            font=("Arial", 11),
            bg=self.colors['error'],
            fg='white',
            relief='flat',
            command=dialog.destroy,
            cursor='hand2'
        ).pack(side='left', padx=10)
    
    def delete_user(self):
        """Удаление пользователя"""
        selection = self.users_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите пользователя для удаления!")
            return
        
        selected_display = self.users_listbox.get(selection[0])
        user_data = self.users_data[selected_display]
        
        if user_data['id'] == self.current_user['id']:
            messagebox.showerror("Ошибка", "Нельзя удалить самого себя!")
            return
        
        if messagebox.askyesno("Подтверждение", f"Удалить пользователя '{user_data['username']}'?\nВсе его профили также будут удалены!"):
            try:
                connection = mysql.connector.connect(**self.db_config)
                cursor = connection.cursor()
                
                # Удаление профилей пользователя
                cursor.execute("DELETE FROM bind_profiles WHERE user_id = %s", (user_data['id'],))
                
                # Удаление пользователя
                cursor.execute("DELETE FROM users WHERE id = %s", (user_data['id'],))
                
                connection.commit()
                cursor.close()
                connection.close()
                
                self.load_users()
                self.log_activity("user_delete", f"Deleted user: {user_data['username']}")
                messagebox.showinfo("Успех", f"Пользователь '{user_data['username']}' удален!")
                
            except Error as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления пользователя: {e}")
    
    def load_logs(self):
        """Загрузка логов активности"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            cursor.execute("""
                SELECT u.username, al.action, al.details, al.timestamp 
                FROM activity_logs al
                JOIN users u ON al.user_id = u.id
                ORDER BY al.timestamp DESC 
                LIMIT 100
            """)
            
            logs = cursor.fetchall()
            
            self.logs_text.config(state='normal')
            self.logs_text.delete("1.0", tk.END)
            
            for log in logs:
                username, action, details, timestamp = log
                log_line = f"[{timestamp}] {username}: {action}"
                if details:
                    log_line += f" - {details}"
                log_line += "\n"
                self.logs_text.insert(tk.END, log_line)
            
            self.logs_text.config(state='disabled')
            self.logs_text.see(tk.END)
            
            cursor.close()
            connection.close()
            
        except Error as e:
            self.logs_text.config(state='normal')
            self.logs_text.insert(tk.END, f"Ошибка загрузки логов: {e}\n")
            self.logs_text.config(state='disabled')
    
    def log_activity(self, action, details=None):
        """Запись в лог активности"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            cursor.execute("""
                INSERT INTO activity_logs (user_id, action, details) 
                VALUES (%s, %s, %s)
            """, (self.current_user['id'], action, details))
            
            connection.commit()
            cursor.close()
            connection.close()
            
            # Обновление логов в админ-панели
            if self.is_admin and hasattr(self, 'logs_text'):
                self.root.after(100, self.load_logs)
                
        except Error:
            pass  # Игнорируем ошибки логирования
    
    def logout(self):
        """Выход из системы"""
        if self.binder_active:
            self.stop_binder()
        
        self.log_activity("logout", "User logged out")
        self.current_user = None
        self.is_admin = False
        
        self.create_login_interface()
    
    def run(self):
        """Запуск приложения"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Обработка закрытия приложения"""
        if self.binder_active:
            self.stop_binder()
        
        if self.current_user:
            self.log_activity("app_close", "Application closed")
        
        self.root.destroy()

# Дополнительные импорты для создания exe
import tkinter.simpledialog

if __name__ == "__main__":
    try:
        app = ForeverGuildBinder()
        app.run()
    except Exception as e:
        messagebox.showerror("Критическая ошибка", f"Произошла критическая ошибка: {e}")