import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext, font
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import Channel, User
from telethon.tl.functions.channels import JoinChannelRequest, CreateChannelRequest
import asyncio
import threading
import os
import logging
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import aiohttp

logging.basicConfig(level=logging.INFO)

# Выводим логотип в консоль при запуске
print(r"""
███╗   ███╗ ██████╗ ███╗   ██╗████████╗
████╗ ████║██╔════╝ ████╗  ██║╚══██╔══╝
██╔████╔██║██║  ███╗██╔██╗ ██║   ██║   
██║╚██╔╝██║██║   ██║██║╚██╗██║   ██║   
██║ ╚═╝ ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
""")
print("Сделано Ч.Х.Г \"MGNT\"")

THEMES = {
    'dark': {
        'bg': '#0d1117',
        'secondary_bg': '#161b22',
        'text': '#c9d1d9',
        'button_bg': '#238636',
        'input_bg': '#161b22',
        'message_bg': '#21262d',
        'self_message_bg': '#1f6feb',
        'border': '#30363d',
        'error': '#ff7b72',
        'task_bg': '#2d333b',
        'header_bg': '#0a0d12',
        'highlight': '#58a6ff',
        'console_info': '#58a6ff',
        'console_warning': '#d29922',
        'console_error': '#ff7b72',
        'console_success': '#3fb950',
        'console_command': '#a371f7'
    },
    'light': {
        'bg': '#ffffff',
        'secondary_bg': '#f3f6f9',
        'text': '#000000',
        'button_bg': '#0084ff',
        'input_bg': '#ffffff',
        'message_bg': '#e9ecef',
        'self_message_bg': '#0084ff',
        'border': '#ccd0d5',
        'error': '#ff0000',
        'task_bg': '#e3e6e9',
        'header_bg': '#e0e7ff',
        'highlight': '#1a73e8',
        'console_info': '#1a73e8',
        'console_warning': '#f9ab00',
        'console_error': '#d93025',
        'console_success': '#0f9d58',
        'console_command': '#673ab7'
    }
}

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.withdraw()
        self.splash = tk.Toplevel(root)
        self.splash.overrideredirect(True)
        self.splash.geometry("500x300")
        self.splash.configure(bg="#0a0d12")
        
        # Центрируем на экране
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 500) // 2
        y = (screen_height - 300) // 2
        self.splash.geometry(f"500x300+{x}+{y}")
        
        # Создаем логотип
        self.create_logo()
        
        # Автозакрытие через 2 секунды
        self.root.after(2000, self.destroy_splash)
    
    def create_logo(self):
        logo_frame = tk.Frame(self.splash, bg="#0a0d12")
        logo_frame.pack(expand=True, fill=tk.BOTH)
        
        # Большой логотип MGNT
        logo_font = font.Font(family="Arial", size=48, weight="bold")
        logo_label = tk.Label(
            logo_frame, 
            text="MGNT", 
            fg="#58a6ff", 
            bg="#0a0d12", 
            font=logo_font
        )
        logo_label.pack(pady=(40, 0))
        
        # Подпись
        signature_font = font.Font(family="Arial", size=14)
        signature_label = tk.Label(
            logo_frame, 
            text="Сделано Ч.Х.Г \"MGNT\"", 
            fg="#c9d1d9", 
            bg="#0a0d12", 
            font=signature_font
        )
        signature_label.pack(pady=(20, 0))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(
            logo_frame, 
            orient=tk.HORIZONTAL, 
            length=300, 
            mode='determinate'
        )
        self.progress.pack(pady=30)
        self.update_progress()
    
    def update_progress(self):
        for i in range(101):
            self.progress['value'] = i
            self.splash.update()
            time.sleep(0.02)
    
    def destroy_splash(self):
        self.splash.destroy()
        self.root.deiconify()

class AuthDialog(tk.Toplevel):
    def __init__(self, parent, title, prompt, theme):
        super().__init__(parent)
        self.theme = theme
        self.title(title)
        self.geometry("320x150")
        self.configure(bg=THEMES[self.theme]['bg'])
        self.resizable(False, False)
        
        self.label = tk.Label(
            self, text=prompt,
            bg=THEMES[self.theme]['bg'],
            fg=THEMES[self.theme]['text'],
            font=('Segoe UI', 11)
        )
        self.label.pack(pady=12)
        
        self.entry = tk.Entry(
            self, 
            bg=THEMES[self.theme]['input_bg'],
            fg=THEMES[self.theme]['text'],
            insertbackground=THEMES[self.theme]['text'],
            relief='flat', 
            font=('Segoe UI', 11)
        )
        self.entry.pack(pady=5, fill=tk.X, padx=20)
        self.entry.bind("<Return>", lambda e: self.ok())
        
        btn_frame = tk.Frame(self, bg=THEMES[self.theme]['bg'])
        btn_frame.pack(pady=10)
        
        self.ok_btn = tk.Button(
            btn_frame, 
            text="OK", 
            command=self.ok,
            bg=THEMES[self.theme]['button_bg'],
            fg='white', 
            relief='flat',
            font=('Segoe UI', 10, 'bold'),
            width=8
        )
        self.ok_btn.pack(side=tk.LEFT, padx=6)
        
        self.cancel_btn = tk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.cancel,
            bg=THEMES[self.theme]['secondary_bg'],
            fg=THEMES[self.theme]['text'], 
            relief='flat',
            font=('Segoe UI', 10),
            width=8
        )
        self.cancel_btn.pack(side=tk.RIGHT, padx=6)
        
        self.result = None
        self.grab_set()
        self.focus_force()
    
    def ok(self):
        self.result = self.entry.get()
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()

class CreateChatsDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.title("Создание чатов")
        self.geometry("400x450")
        self.configure(bg=THEMES[self.theme]['bg'])
        self.resizable(False, False)
        
        fields = [
            ("ID аккаунта:", 'account_id'),
            ("Количество чатов (до 999):", 'chat_count'),
            ("Названия (через запятую):", 'titles'),
            ("Описание:", 'description'),
            ("Тайм-аут (секунды):", 'timeout'),
            ("Групп перед паузой:", 'pause_after'),
            ("Длительность паузы (сек):", 'pause_duration')
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(
                self, 
                text=label, 
                background=THEMES[self.theme]['bg'], 
                foreground=THEMES[self.theme]['text']
            ).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            if key == 'description':
                entry = scrolledtext.ScrolledText(self, height=3, width=30)
            else:
                entry = ttk.Entry(self, width=30)
            
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[key] = entry
        
        self.create_btn = ttk.Button(
            self, 
            text="Создать", 
            command=self.validate,
            style='Accent.TButton'
        )
        self.create_btn.grid(row=7, column=0, columnspan=2, pady=15)
        self.result = None
    
    def validate(self):
        try:
            data = {
                'account_id': int(self.entries['account_id'].get()),
                'chat_count': int(self.entries['chat_count'].get()),
                'titles': [x.strip() for x in self.entries['titles'].get().split(',')],
                'description': self.entries['description'].get("1.0", tk.END).strip(),
                'timeout': int(self.entries['timeout'].get()),
                'pause_after': int(self.entries['pause_after'].get()),
                'pause_duration': int(self.entries['pause_duration'].get()),
                'type': 'create_chats',
                'status': 'Активна'
            }
            
            if data['chat_count'] < 1 or data['chat_count'] > 999:
                raise ValueError("Количество чатов должно быть от 1 до 999")
            if len(data['titles']) == 0:
                raise ValueError("Укажите хотя бы одно название")
            if data['timeout'] < 0 or data['pause_duration'] < 0:
                raise ValueError("Время должно быть положительным числом")
            if data['pause_after'] < 0:
                raise ValueError("Количество групп перед паузой не может быть отрицательным")
            
            self.result = data
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

class SubscribeDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.title("Накрутка подписчиков")
        self.geometry("400x300")
        self.configure(bg=THEMES[self.theme]['bg'])
        self.resizable(False, False)
        
        fields = [
            ("Аккаунты (через запятую):", 'accounts'),
            ("Ссылка на канал:", 'channel'),
            ("Мин. интервал (мин):", 'min_interval'),
            ("Макс. интервал (мин):", 'max_interval')
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(
                self, 
                text=label, 
                background=THEMES[self.theme]['bg'], 
                foreground=THEMES[self.theme]['text']
            ).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            entry = ttk.Entry(self, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[key] = entry
        
        self.create_btn = ttk.Button(
            self, 
            text="Создать", 
            command=self.accept,
            style='Accent.TButton'
        )
        self.create_btn.grid(row=4, column=0, columnspan=2, pady=15)
    
    def accept(self):
        try:
            accounts = [int(x.strip()) for x in self.entries['accounts'].get().split(',')]
            channel = self.entries['channel'].get()
            min_interval = int(self.entries['min_interval'].get())
            max_interval = int(self.entries['max_interval'].get())
            
            if min_interval < 1 or max_interval > 60 or min_interval > max_interval:
                raise ValueError("Некорректный интервал (1-60 мин)")
            
            self.result = {
                'type': 'subscribe',
                'accounts': accounts,
                'channel': channel,
                'min_interval': min_interval,
                'max_interval': max_interval,
                'status': 'Активна'
            }
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проверьте данные: {str(e)}")

class CodeRequestDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.title("Получить код")
        self.geometry("300x150")
        self.configure(bg=THEMES[self.theme]['bg'])
        
        ttk.Label(
            self, 
            text="ID аккаунта:",
            background=THEMES[self.theme]['bg'], 
            foreground=THEMES[self.theme]['text']
        ).pack(pady=10)
        
        self.entry = ttk.Entry(self, width=20)
        self.entry.pack()
        
        btn_frame = tk.Frame(self, bg=THEMES[self.theme]['bg'])
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Запросить", 
            command=self.ok,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.cancel
        ).pack(side=tk.RIGHT, padx=5)
        
        self.result = None
    
    def ok(self):
        self.result = self.entry.get()
        self.destroy()
    
    def cancel(self):
        self.result = None
        self.destroy()

class AddProxyDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.title("Добавить Proxy")
        self.geometry("400x300")
        self.configure(bg=THEMES[self.theme]['bg'])
        
        fields = [
            ("Название:", 'name'),
            ("Тип (socks5/http):", 'type'),
            ("Хост:", 'host'),
            ("Порт:", 'port'),
            ("Логин (опционально):", 'username'),
            ("Пароль (опционально):", 'password')
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(
                self, 
                text=label, 
                background=THEMES[self.theme]['bg'], 
                foreground=THEMES[self.theme]['text']
            ).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            entry = ttk.Entry(self, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            self.entries[key] = entry
        
        btn_frame = tk.Frame(self, bg=THEMES[self.theme]['bg'])
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        ttk.Button(
            btn_frame, 
            text="Сохранить", 
            command=self.save,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        self.result = None

    def save(self):
        try:
            data = {
                'name': self.entries['name'].get(),
                'type': self.entries['type'].get().lower(),
                'host': self.entries['host'].get(),
                'port': int(self.entries['port'].get()),
                'username': self.entries['username'].get() or "",
                'password': self.entries['password'].get() or "",
                'status': 'Не проверен'
            }
            
            if not data['name']:
                raise ValueError("Введите название прокси")
            if data['type'] not in ['socks5', 'http']:
                raise ValueError("Тип прокси должен быть socks5 или http")
            if not data['host']:
                raise ValueError("Введите хост")
            if data['port'] < 1 or data['port'] > 65535:
                raise ValueError("Некорректный порт")
            
            self.result = data
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

class ProxyManagerDialog(tk.Toplevel):
    def __init__(self, parent, manager, theme):
        super().__init__(parent)
        self.manager = manager
        self.theme = theme
        self.title("Управление Proxy")
        self.geometry("800x500")
        self.configure(bg=THEMES[self.theme]['bg'])
        
        # Заголовок
        header = tk.Frame(self, bg=THEMES[self.theme]['header_bg'])
        header.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header, 
            text="Управление прокси-серверами",
            bg=THEMES[self.theme]['header_bg'],
            fg=THEMES[self.theme]['text'],
            font=('Segoe UI', 14, 'bold')
        ).pack(pady=10)
        
        # Список прокси
        self.tree = ttk.Treeview(self, columns=("Name", "Type", "Host", "Port", "Status"), show="headings")
        self.tree.heading("Name", text="Название")
        self.tree.heading("Type", text="Тип")
        self.tree.heading("Host", text="Хост")
        self.tree.heading("Port", text="Порт")
        self.tree.heading("Status", text="Статус")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления
        btn_frame = tk.Frame(self, bg=THEMES[self.theme]['bg'])
        btn_frame.pack(pady=10)
        
        buttons = [
            ("Добавить", self.add_proxy),
            ("Проверить", self.check_proxy),
            ("Активировать", self.activate_proxy),
            ("Деактивировать", self.deactivate_proxy),
            ("Удалить", self.delete_proxy)
        ]
        
        for text, cmd in buttons:
            ttk.Button(
                btn_frame, 
                text=text, 
                command=cmd,
                style='TButton' if text != "Добавить" else 'Accent.TButton'
            ).pack(side=tk.LEFT, padx=5)
        
        self.load_proxies()
    
    def load_proxies(self):
        self.tree.delete(*self.tree.get_children())
        try:
            if not os.path.exists('proxies.xlsx'):
                df = pd.DataFrame(columns=['Name','Type','Host','Port','Username','Password','Status'])
                df.to_excel('proxies.xlsx', index=False)
                return
                
            df = pd.read_excel('proxies.xlsx')
            df = df.fillna("")
            
            for _, row in df.iterrows():
                self.tree.insert("", 'end', values=(
                    row['Name'],
                    row['Type'],
                    row['Host'],
                    row['Port'],
                    row['Status'] if 'Status' in df.columns else "Неизвестно"
                ))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка загрузки прокси: {str(e)}")
    
    def add_proxy(self):
        dialog = AddProxyDialog(self, self.theme)
        self.wait_window(dialog)
        if dialog.result:
            try:
                if os.path.exists('proxies.xlsx'):
                    df = pd.read_excel('proxies.xlsx')
                    df = df.fillna("")
                else:
                    df = pd.DataFrame(columns=['Name', 'Type', 'Host', 'Port', 'Username', 'Password', 'Status'])
                
                new_df = pd.DataFrame([dialog.result])
                df = pd.concat([df, new_df], ignore_index=True)
                df.to_excel('proxies.xlsx', index=False)
                self.load_proxies()
                self.manager.print_console(f"[+] Прокси '{dialog.result['name']}' добавлен", 'info')
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка сохранения: {str(e)}")
    
    def get_selected_proxy(self):
        selected = self.tree.selection()
        if not selected:
            return None
        item = self.tree.item(selected[0])
        return {
            'name': item['values'][0],
            'type': item['values'][1],
            'host': item['values'][2],
            'port': item['values'][3],
            'username': "",
            'password': "",
            'status': item['values'][4] if len(item['values']) > 4 else ""
        }
    
    def check_proxy(self):
        proxy = self.get_selected_proxy()
        if proxy:
            self.manager.run_async_task(self.manager.check_proxy_connection(proxy))
    
    def activate_proxy(self):
        proxy = self.get_selected_proxy()
        if proxy:
            self.manager.activate_proxy(proxy)
    
    def deactivate_proxy(self):
        self.manager.deactivate_proxy()
    
    def delete_proxy(self):
        proxy = self.get_selected_proxy()
        if proxy and messagebox.askyesno("Подтверждение", f"Удалить прокси '{proxy['name']}'?"):
            try:
                if not os.path.exists('proxies.xlsx'):
                    return
                    
                df = pd.read_excel('proxies.xlsx')
                df = df.fillna("")
                df = df[df['Name'] != proxy['name']]
                df.to_excel('proxies.xlsx', index=False)
                self.load_proxies()
                self.manager.print_console(f"[✓] Прокси '{proxy['name']}' удален", 'success')
                
                if self.manager.current_proxy and self.manager.current_proxy['name'] == proxy['name']:
                    self.manager.deactivate_proxy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка удаления: {str(e)}")

class EditAccountDialog(tk.Toplevel):
    def __init__(self, parent, theme, current_data):
        super().__init__(parent)
        self.theme = theme
        self.title("Редактирование аккаунта")
        self.geometry("400x250")
        self.configure(bg=THEMES[self.theme]['bg'])
        
        fields = [
            ("ID:", 'id'),
            ("Телефон:", 'phone'),
            ("API ID:", 'api_id'),
            ("API HASH:", 'api_hash')
        ]
        
        self.entries = {}
        for i, (label, key) in enumerate(fields):
            ttk.Label(
                self, 
                text=label, 
                background=THEMES[self.theme]['bg'], 
                foreground=THEMES[self.theme]['text']
            ).grid(row=i, column=0, padx=10, pady=5, sticky='w')
            
            entry = ttk.Entry(self, width=25)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entry.insert(0, current_data[key])
            
            self.entries[key] = entry
        
        btn_frame = tk.Frame(self, bg=THEMES[self.theme]['bg'])
        btn_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        ttk.Button(
            btn_frame, 
            text="Сохранить", 
            command=self.save,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        self.result = None

    def save(self):
        self.result = {
            'id': self.entries['id'].get(),
            'phone': self.entries['phone'].get(),
            'api_id': self.entries['api_id'].get(),
            'api_hash': self.entries['api_hash'].get()
        }
        self.destroy()

class AccountWindow(tk.Toplevel):
    def __init__(self, parent, manager, phone, client, theme):
        super().__init__(parent)
        self.manager = manager
        self.phone = phone
        self.current_client = client
        self.current_theme = theme
        self.current_chat_id = None
        self.auto_refresh = True
        self.refresh_interval = manager.refresh_interval
        
        self.title(f"Аккаунт: {phone}")
        self.geometry("1000x700")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Заголовок окна
        self.header_frame = tk.Frame(self, bg=THEMES[self.current_theme]['header_bg'], height=50)
        self.header_frame.pack(fill=tk.X)
        
        tk.Label(
            self.header_frame, 
            text=f"Аккаунт: {phone}",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 12, 'bold')
        ).pack(side=tk.LEFT, padx=15)
        
        # Кнопка обновления
        refresh_btn = tk.Button(
            self.header_frame, 
            text="⟳ Обновить",
            command=lambda: self.run_async_task(self.load_chats()),
            bg=THEMES[self.current_theme]['button_bg'],
            fg='white',
            relief='flat',
            font=('Segoe UI', 10)
        )
        refresh_btn.pack(side=tk.RIGHT, padx=15)
        
        self.create_widgets()
        self.apply_theme()
        self.start_auto_refresh()
        
        # Загружаем чаты сразу после открытия окна
        self.run_async_task(self.load_chats())
    
    def run_async_task(self, coroutine):
        asyncio.run_coroutine_threadsafe(coroutine, self.manager.loop)
    
    def create_widgets(self):
        # Основной контейнер
        main_container = tk.Frame(self, bg=THEMES[self.current_theme]['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Фрейм для списка чатов
        left_frame = tk.Frame(main_container, bg=THEMES[self.current_theme]['secondary_bg'], width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # Заголовок списка чатов
        chat_header = tk.Frame(left_frame, bg=THEMES[self.current_theme]['header_bg'])
        chat_header.pack(fill=tk.X)
        
        tk.Label(
            chat_header, 
            text="Ваши чаты",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=5)
        
        # Список чатов с полосой прокрутки
        chat_container = tk.Frame(left_frame, bg=THEMES[self.current_theme]['secondary_bg'])
        chat_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.chat_list = ttk.Treeview(
            chat_container, 
            columns=("Name", "Type"), 
            show="headings",
            height=20,
            selectmode='browse'
        )
        self.chat_list.heading("Name", text="Название")
        self.chat_list.heading("Type", text="Тип")
        self.chat_list.column("Name", width=180)
        self.chat_list.column("Type", width=50)
        self.chat_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_list.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_list.configure(yscrollcommand=scrollbar.set)
        
        # Фрейм для сообщений
        right_frame = tk.Frame(main_container, bg=THEMES[self.current_theme]['bg'])
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Область сообщений
        message_frame = tk.Frame(right_frame, bg=THEMES[self.current_theme]['secondary_bg'])
        message_frame.pack(fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Заголовок чата
        self.chat_header = tk.Frame(message_frame, bg=THEMES[self.current_theme]['header_bg'], height=40)
        self.chat_header.pack(fill=tk.X)
        
        self.chat_title = tk.Label(
            self.chat_header, 
            text="Выберите чат",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 10, 'bold')
        )
        self.chat_title.pack(pady=10)
        
        # Область сообщений
        self.message_box = scrolledtext.ScrolledText(
            message_frame, 
            wrap=tk.WORD, 
            bg=THEMES[self.current_theme]['secondary_bg'], 
            fg=THEMES[self.current_theme]['text'],
            insertbackground=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 11),
            state=tk.DISABLED
        )
        self.message_box.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Настройка тегов для сообщений
        self.message_box.tag_config('self_msg', 
            foreground='white', 
            background=THEMES[self.current_theme]['self_message_bg'],
            lmargin1=20, lmargin2=20, rmargin=20, spacing3=5
        )
        self.message_box.tag_config('other_msg', 
            foreground=THEMES[self.current_theme]['text'], 
            background=THEMES[self.current_theme]['message_bg'],
            lmargin1=20, lmargin2=20, rmargin=20, spacing3=5
        )
        self.message_box.tag_config('timestamp', 
            foreground='#8b949e', 
            font=('Segoe UI', 9)
        )
        self.message_box.tag_config('sender', 
            foreground=THEMES[self.current_theme]['highlight'], 
            font=('Segoe UI', 10, 'bold')
        )
        
        # Ввод сообщения
        input_frame = tk.Frame(
            message_frame, 
            bg=THEMES[self.current_theme]['secondary_bg'],
            height=50, 
            padx=10, 
            pady=10
        )
        input_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.message_input = tk.Entry(
            input_frame, 
            bg=THEMES[self.current_theme]['input_bg'], 
            fg=THEMES[self.current_theme]['text'],
            insertbackground=THEMES[self.current_theme]['text'],
            relief='flat', 
            font=('Segoe UI', 12)
        )
        self.message_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.send_btn = tk.Button(
            input_frame, 
            text="Отправить", 
            command=self.send_message,
            bg=THEMES[self.current_theme]['button_bg'], 
            fg='white', 
            relief='flat', 
            font=('Segoe UI', 11, 'bold')
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        self.chat_list.bind("<<TreeviewSelect>>", self.on_chat_selected)
    
    def apply_theme(self):
        theme = THEMES[self.current_theme]
        self.configure(bg=theme['bg'])
        
        # Настройка стилей Treeview
        style = ttk.Style()
        style.theme_use('clam')
        
        # Общий стиль для Treeview
        style.configure("Treeview", 
            background=theme['secondary_bg'], 
            fieldbackground=theme['secondary_bg'],
            foreground=theme['text'], 
            borderwidth=0,
            font=('Segoe UI', 10)
        )
        style.map('Treeview', 
            background=[('selected', theme['button_bg'])],
            foreground=[('selected', 'white')]
        )
        
        # Стиль заголовков Treeview
        style.configure("Treeview.Heading", 
            background=theme['bg'], 
            foreground=theme['text'],
            font=('Segoe UI', 10, 'bold'), 
            relief='flat'
        )
        
        # Обновляем другие виджеты
        self.message_box.configure(
            bg=theme['secondary_bg'], 
            fg=theme['text'],
            insertbackground=theme['text']
        )
        self.message_input.configure(
            bg=theme['input_bg'], 
            fg=theme['text'],
            insertbackground=theme['text']
        )
        self.send_btn.configure(bg=theme['button_bg'])
    
    def start_auto_refresh(self):
        def auto_refresh():
            while self.auto_refresh:
                if self.current_chat_id:
                    self.run_async_task(self.load_chat_messages())
                time.sleep(self.refresh_interval)
        threading.Thread(target=auto_refresh, daemon=True).start()
    
    async def load_chats(self):
        try:
            self.chat_list.delete(*self.chat_list.get_children())
            async for dialog in self.current_client.iter_dialogs(limit=100):
                entity = dialog.entity
                chat_type = "Канал" if isinstance(entity, Channel) else "Бот" if isinstance(entity, User) and entity.bot else "Чат"
                self.chat_list.insert("", 'end', values=(dialog.name, chat_type), iid=str(dialog.id))
            self.manager.print_console(f"[✓] Чаты для {self.phone} обновлены", 'success')
        except Exception as e:
            self.manager.print_console(f"[!] Ошибка загрузки чатов: {str(e)}", 'error')
    
    def on_chat_selected(self, event):
        selected = self.chat_list.selection()
        if selected:
            self.current_chat_id = int(selected[0])
            chat_name = self.chat_list.item(selected[0])['values'][0]
            self.chat_title.config(text=chat_name)
            self.run_async_task(self.load_chat_messages())
    
    async def load_chat_messages(self):
        try:
            if not self.current_chat_id or not self.current_client:
                return
            
            self.message_box.config(state=tk.NORMAL)
            self.message_box.delete(1.0, tk.END)
            
            async for message in self.current_client.iter_messages(self.current_chat_id, limit=50, reverse=True):
                if message.text:
                    sender = await message.get_sender()
                    sender_name = sender.first_name if sender else "Неизвестно"
                    timestamp = message.date.strftime("%H:%M")
                    
                    # Форматируем сообщение
                    self.message_box.insert(tk.END, f"{sender_name}: ", 'sender')
                    self.message_box.insert(tk.END, f"{message.text}\n", 'self_msg' if message.out else 'other_msg')
                    self.message_box.insert(tk.END, f"{timestamp}\n\n", 'timestamp')
            
            self.message_box.config(state=tk.DISABLED)
            self.message_box.see(tk.END)
        except Exception as e:
            self.manager.print_console(f"[!] Ошибка загрузки сообщений: {str(e)}", 'error')
    
    def send_message(self):
        if not self.current_client or not self.current_chat_id:
            messagebox.showwarning("Ошибка", "Выберите чат!", parent=self)
            return
        text = self.message_input.get()
        if not text:
            return
        self.run_async_task(self.send_message_async(text))
    
    async def send_message_async(self, text):
        try:
            await self.current_client.send_message(self.current_chat_id, text)
            self.message_input.delete(0, tk.END)
            await self.load_chat_messages()
            self.manager.print_console(f"[✓] Сообщение отправлено: {self.phone}", 'success')
        except Exception as e:
            self.manager.print_console(f"[!] Ошибка отправки: {str(e)}", 'error')
    
    def on_closing(self):
        self.auto_refresh = False
        self.run_async_task(self.logout_async())
        self.manager.account_windows.remove(self)
        self.destroy()
    
    async def logout_async(self):
        try:
            if self.current_client and self.current_client.is_connected():
                await self.current_client.disconnect()
                self.manager.print_console(f"[!] Выход из аккаунта: {self.phone}", 'warning')
        except Exception as e:
            self.manager.print_console(f"[!] Ошибка выхода: {str(e)}", 'error')

class WarmUpDialog(tk.Toplevel):
    def __init__(self, parent, theme):
        super().__init__(parent)
        self.theme = theme
        self.title("Авто прогрев аккаунтов")
        self.geometry("350x150")
        self.configure(bg=THEMES[self.theme]['bg'])
        
        # Минимальный интервал
        ttk.Label(
            self, 
            text="Минимальный интервал (сек):",
            background=THEMES[self.theme]['bg'], 
            foreground=THEMES[self.theme]['text']
        ).grid(row=0, column=0, padx=10, pady=5, sticky='w')
        
        self.min_entry = ttk.Entry(self, width=15)
        self.min_entry.grid(row=0, column=1, padx=10, pady=5)
        self.min_entry.insert(0, "5")
        
        # Максимальный интервал
        ttk.Label(
            self, 
            text="Максимальный интервал (сек):",
            background=THEMES[self.theme]['bg'], 
            foreground=THEMES[self.theme]['text']
        ).grid(row=1, column=0, padx=10, pady=5, sticky='w')
        
        self.max_entry = ttk.Entry(self, width=15)
        self.max_entry.grid(row=1, column=1, padx=10, pady=5)
        self.max_entry.insert(0, "10")
        
        # Кнопки
        btn_frame = tk.Frame(self, bg=THEMES[self.theme]['bg'])
        btn_frame.grid(row=2, column=0, columnspan=2, pady=15)
        
        ttk.Button(
            btn_frame, 
            text="Начать", 
            command=self.accept,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Отмена", 
            command=self.destroy
        ).pack(side=tk.RIGHT, padx=10)
    
    def accept(self):
        try:
            min_interval = int(self.min_entry.get())
            max_interval = int(self.max_entry.get())
            
            if min_interval < 1 or max_interval < min_interval:
                raise ValueError("Некорректные интервалы")
                
            self.result = (min_interval, max_interval)
            self.destroy()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Проверьте данные: {str(e)}")

class TelegramAccountManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Manager Pro")
        self.root.geometry("1280x720")
        
        # Показываем заставку
        SplashScreen(self.root)
        
        # Основные настройки
        self.current_theme = 'dark'
        self.running = True
        self.auto_refresh = True
        self.active_tasks = []
        self.showing_tasks = False
        self.refresh_interval = 5
        self.code_request_client = None
        self.loop = asyncio.new_event_loop()
        self._start_async_loop()
        self.setup_styles()
        self.session_dir = 'sessions'
        self.db_file = 'database.xlsx'
        self.current_proxy = None
        self.account_windows = []
        self.command_history = []
        self.history_index = -1
        self.warming_up = False
        
        # Инициализация хранилища
        self.init_storage()
        
        self.create_widgets()
        self.update_accounts_list()
        self.create_tasks_interface()
        self.create_console()
        self.apply_theme()
        
        # Устанавливаем иконку приложения
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

    def init_storage(self):
        if not os.path.exists(self.session_dir):
            os.makedirs(self.session_dir)
        if not os.path.exists(self.db_file):
            pd.DataFrame(columns=['ID','Phone','API_ID','API_HASH']).to_excel(self.db_file, index=False)
        else:
            df = pd.read_excel(self.db_file)
            if 'ID' not in df.columns:
                df['ID'] = range(1, len(df)+1)
                df.to_excel(self.db_file, index=False)
        
        # Инициализация базы прокси
        if not os.path.exists('proxies.xlsx'):
            df = pd.DataFrame(columns=[
                'Name', 'Type', 'Host', 'Port', 
                'Username', 'Password', 'Status'
            ])
            df.to_excel('proxies.xlsx', index=False)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Создаем кастомные стили
        self.style.configure('Accent.TButton', 
                            background=THEMES[self.current_theme]['button_bg'],
                            foreground='white',
                            font=('Segoe UI', 10, 'bold'),
                            borderwidth=0)
        
        self.style.map('Accent.TButton', 
                      background=[('active', THEMES[self.current_theme]['button_bg']),
                                   ('disabled', THEMES[self.current_theme]['secondary_bg'])])
        
        self.style.configure('TButton', 
                            background=THEMES[self.current_theme]['secondary_bg'],
                            foreground=THEMES[self.current_theme]['text'],
                            font=('Segoe UI', 10),
                            borderwidth=0)
        
        self.style.configure('Treeview.Heading', 
                            background=THEMES[self.current_theme]['header_bg'],
                            foreground=THEMES[self.current_theme]['text'],
                            font=('Segoe UI', 10, 'bold'), 
                            relief='flat')
        
        self.style.configure('Treeview', 
                            background=THEMES[self.current_theme]['secondary_bg'],
                            fieldbackground=THEMES[self.current_theme]['secondary_bg'],
                            foreground=THEMES[self.current_theme]['text'],
                            borderwidth=0,
                            font=('Segoe UI', 10))
        
        self.style.map('Treeview', 
                      background=[('selected', THEMES[self.current_theme]['button_bg'])],
                      foreground=[('selected', 'white')])

    def apply_theme(self):
        theme = THEMES[self.current_theme]
        self.root.configure(bg=theme['bg'])
        
        # Обновляем стили
        self.style.configure('Accent.TButton', background=theme['button_bg'])
        self.style.configure('TButton', background=theme['secondary_bg'], foreground=theme['text'])
        self.style.configure('Treeview.Heading', background=theme['header_bg'], foreground=theme['text'])
        self.style.configure('Treeview', background=theme['secondary_bg'], fieldbackground=theme['secondary_bg'], foreground=theme['text'])
        
        # Обновляем все виджеты
        for widget in self.root.winfo_children():
            self.update_widget_theme(widget)
        
        # Обновляем тему во всех открытых окнах аккаунтов
        for window in self.account_windows:
            window.current_theme = self.current_theme
            window.apply_theme()

    def update_widget_theme(self, widget):
        theme = THEMES[self.current_theme]
        if isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            widget.configure(bg=theme['secondary_bg'], fg=theme['text'])
        elif isinstance(widget, tk.Entry):
            widget.configure(bg=theme['input_bg'], fg=theme['text'], insertbackground=theme['text'])
        elif isinstance(widget, (tk.Frame, ttk.Frame)):
            widget.configure(bg=theme['bg'])

    def _start_async_loop(self):
        self.thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self.thread.start()

    def _run_async_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def create_widgets(self):
        # Основной контейнер
        main_container = tk.Frame(self.root, bg=THEMES[self.current_theme]['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Левая панель с аккаунтами
        left_panel = tk.Frame(main_container, bg=THEMES[self.current_theme]['bg'], width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Заголовок аккаунтов
        accounts_header = tk.Frame(left_panel, bg=THEMES[self.current_theme]['header_bg'])
        accounts_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            accounts_header, 
            text="Управление аккаунтами",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 12, 'bold')
        ).pack(pady=8)
        
        # Кнопки управления
        btn_frame = tk.Frame(left_panel, bg=THEMES[self.current_theme]['bg'])
        btn_frame.pack(fill=tk.X, pady=5)
        
        buttons = [
            ("➕ Добавить аккаунт", self.add_account),
            ("🔑 Войти в аккаунт", self.init_login),
            ("📈 Накрутка подписчиков", self.show_subscribe_dialog),
            ("💬 Создать чаты", self.show_create_chats_dialog),
            ("🔐 Получить код", self.get_login_code),
            ("🌐 Proxy", self.show_proxy_manager),
            ("⚙️ Настройки", self.show_settings),
            ("🚪 Выход", self.logout)
        ]
        
        for text, cmd in buttons:
            btn = tk.Button(
                btn_frame, 
                text=text, 
                command=cmd,
                bg=THEMES[self.current_theme]['secondary_bg'],
                fg=THEMES[self.current_theme]['text'], 
                relief='flat', 
                font=('Segoe UI', 11),
                anchor='w',
                padx=10
            )
            btn.pack(fill=tk.X, pady=3)
        
        # Список аккаунтов
        list_frame = tk.Frame(left_panel, bg=THEMES[self.current_theme]['bg'])
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Заголовок списка
        list_header = tk.Frame(list_frame, bg=THEMES[self.current_theme]['header_bg'])
        list_header.pack(fill=tk.X)
        
        tk.Label(
            list_header, 
            text="Список аккаунтов",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 10, 'bold')
        ).pack(pady=3)
        
        # Дерево аккаунтов
        tree_container = tk.Frame(list_frame, bg=THEMES[self.current_theme]['bg'])
        tree_container.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(
            tree_container, 
            columns=("ID", "Phone", "API ID", "HASH ID"), 
            show="headings",
            height=15
        )
        
        # Настройка столбцов
        columns = [
            ("ID", "ID", 50),
            ("Phone", "Телефон", 120),
            ("API ID", "API ID", 80),
            ("HASH ID", "HASH ID", 120)
        ]
        
        for col_id, col_text, width in columns:
            self.tree.heading(col_id, text=col_text)
            self.tree.column(col_id, width=width, anchor=tk.CENTER)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки редактирования
        edit_frame = tk.Frame(left_panel, bg=THEMES[self.current_theme]['bg'])
        edit_frame.pack(fill=tk.X, pady=5)
        
        self.edit_btn = tk.Button(
            edit_frame, 
            text="✎ Редактировать", 
            command=self.edit_account,
            bg=THEMES[self.current_theme]['button_bg'],
            fg='white', 
            relief='flat', 
            font=('Segoe UI', 10)
        )
        self.edit_btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)
        
        self.delete_btn = tk.Button(
            edit_frame, 
            text="🗑 Удалить", 
            command=self.delete_account,
            bg=THEMES[self.current_theme]['error'],
            fg='white', 
            relief='flat', 
            font=('Segoe UI', 10)
        )
        self.delete_btn.pack(side=tk.RIGHT, padx=2, fill=tk.X, expand=True)
        
        # Правая панель с задачами
        right_panel = tk.Frame(main_container, bg=THEMES[self.current_theme]['bg'])
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Заголовок задач
        tasks_header = tk.Frame(right_panel, bg=THEMES[self.current_theme]['header_bg'])
        tasks_header.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(
            tasks_header, 
            text="Активные задачи",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 12, 'bold')
        ).pack(pady=8)
        
        # Список задач
        self.tasks_list = ttk.Treeview(
            right_panel, 
            columns=("Type", "Target", "Details", "Status"), 
            show="headings",
            height=15
        )
        
        # Настройка столбцов задач
        task_columns = [
            ("Type", "Тип", 100),
            ("Target", "Цель", 150),
            ("Details", "Детали", 300),
            ("Status", "Статус", 100)
        ]
        
        for col_id, col_text, width in task_columns:
            self.tasks_list.heading(col_id, text=col_text)
            self.tasks_list.column(col_id, width=width, anchor=tk.W)
        
        self.tasks_list.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Полоса прокрутки для задач
        task_scrollbar = ttk.Scrollbar(right_panel, orient="vertical", command=self.tasks_list.yview)
        task_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tasks_list.configure(yscrollcommand=task_scrollbar.set)
        
        # Кнопка отмены задачи
        cancel_frame = tk.Frame(right_panel, bg=THEMES[self.current_theme]['bg'])
        cancel_frame.pack(fill=tk.X, pady=5)
        
        self.cancel_task_btn = ttk.Button(
            cancel_frame, 
            text="❌ Отменить задачу", 
            command=self.cancel_task,
            style='Accent.TButton'
        )
        self.cancel_task_btn.pack(fill=tk.X, pady=3)

    def show_proxy_manager(self):
        ProxyManagerDialog(self.root, self, self.current_theme)

    async def check_proxy_connection(self, proxy):
        try:
            self.print_console(f"[?] Проверка прокси {proxy['name']}...", 'info')
            
            # Создаем временный клиент для проверки
            proxy_dict = self.create_proxy_dict(proxy)
            
            # Обработка аутентификации
            auth = None
            if proxy.get('username') and proxy.get('password'):
                auth = aiohttp.BasicAuth(proxy['username'], proxy['password'])
            
            proxy_url = ""
            if proxy['type'] == 'http':
                proxy_url = f"http://{proxy['host']}:{proxy['port']}"
            elif proxy['type'] == 'socks5':
                proxy_url = f"socks5://{proxy['host']}:{proxy['port']}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://api.ipify.org",
                    proxy=proxy_url,
                    proxy_auth=auth
                ) as response:
                    if response.status == 200:
                        ip = await response.text()
                        self.print_console(f"[✓] Прокси работает! Ваш IP: {ip}", 'success')
                        self.update_proxy_status(proxy['name'], f"Работает (IP: {ip})")
                    else:
                        self.print_console(f"[!] Ошибка проверки: HTTP статус {response.status}", 'error')
                        self.update_proxy_status(proxy['name'], f"Ошибка: HTTP {response.status}")
        except Exception as e:
            self.print_console(f"[!] Ошибка проверки прокси: {str(e)}", 'error')
            self.update_proxy_status(proxy['name'], f"Ошибка: {str(e)}")

    def create_proxy_dict(self, proxy):
        if not proxy:
            return None
            
        proxy_dict = {
            'proxy_type': proxy['type'],
            'addr': proxy['host'],
            'port': proxy['port'],
            'rdns': True
        }
        
        # Проверка наличия логина/пароля
        if proxy.get('username') and proxy.get('password'):
            proxy_dict['username'] = proxy['username']
            proxy_dict['password'] = proxy['password']
        
        return proxy_dict

    def update_proxy_status(self, name, status):
        try:
            # Проверяем существование файла
            if not os.path.exists('proxies.xlsx'):
                return
                
            df = pd.read_excel('proxies.xlsx')
            df = df.fillna("")  # Заменяем NaN на пустые строки
            
            # Добавляем колонку Status если отсутствует
            if 'Status' not in df.columns:
                df['Status'] = ""
            
            # Обновляем статус
            df.loc[df['Name'] == name, 'Status'] = status
            
            # Сохраняем обратно
            df.to_excel('proxies.xlsx', index=False)
        except Exception as e:
            self.print_console(f"[!] Ошибка обновления статуса прокси: {str(e)}", 'error')

    def activate_proxy(self, proxy):
        self.current_proxy = proxy
        self.print_console(f"[✓] Прокси активирован: {proxy['name']}", 'success')
        self.update_proxy_status(proxy['name'], "Активен")

    def deactivate_proxy(self):
        if self.current_proxy:
            name = self.current_proxy['name']
            self.current_proxy = None
            self.print_console(f"[✓] Прокси деактивирован: {name}", 'success')
            self.update_proxy_status(name, "Не активен")
        else:
            self.print_console("[!] Нет активного прокси для деактивации", 'warning')

    def show_create_chats_dialog(self):
        dialog = CreateChatsDialog(self.root, self.current_theme)
        self.root.wait_window(dialog)
        if dialog.result:
            task = dialog.result
            task['task_id'] = len(self.active_tasks) + 1
            self.active_tasks.append(task)
            self.update_tasks_list()
            self.run_async_task(self.execute_create_chats_task(task))

    async def execute_create_chats_task(self, task):
        try:
            client = await self.get_client_for_account(task['account_id'])
            if not client:
                self.print_console(f"[!] Аккаунт {task['account_id']} не найден или не авторизован", 'error')
                task['status'] = 'Ошибка'
                self.update_tasks_list()
                return

            created = 0
            counter_before_pause = 0
            for i in range(task['chat_count']):
                if task['status'] != 'Активна':
                    break
                
                title = random.choice(task['titles'])
                try:
                    await client(CreateChannelRequest(
                        title=title,
                        about=task['description'],
                        megagroup=True
                    ))
                    created += 1
                    counter_before_pause += 1
                    self.print_console(f"[✓] Создан чат: {title}", 'success')
                    
                    if task['pause_after'] > 0 and counter_before_pause >= task['pause_after']:
                        self.print_console(f"⏸ Массовая пауза {task['pause_duration']} сек...", 'info')
                        await asyncio.sleep(task['pause_duration'])
                        counter_before_pause = 0
                    
                    await asyncio.sleep(task['timeout'])
                    
                except Exception as e:
                    self.print_console(f"[!] Ошибка создания чата: {str(e)}", 'error')
                    await asyncio.sleep(10)

            task['status'] = f"Завершена ({created}/{task['chat_count']})"
            self.active_tasks = [t for t in self.active_tasks if t['status'] == 'Активна']
            self.update_tasks_list()
        except Exception as e:
            self.print_console(f"[!] Ошибка задачи: {str(e)}", 'error')
            task['status'] = 'Ошибка'
            self.active_tasks = [t for t in self.active_tasks if t['status'] == 'Активна']
            self.update_tasks_list()

    def show_subscribe_dialog(self):
        dialog = SubscribeDialog(self.root, self.current_theme)
        self.root.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            task = dialog.result
            task['task_id'] = len(self.active_tasks) + 1
            self.active_tasks.append(task)
            self.update_tasks_list()
            self.run_async_task(self.execute_sub_task(task))

    def get_login_code(self):
        dialog = CodeRequestDialog(self.root, self.current_theme)
        self.root.wait_window(dialog)
        if dialog.result:
            try:
                account_id = int(dialog.result)
                self.run_async_task(self.request_code(account_id))
            except:
                self.print_console("Ошибка: Некорректный ID", 'error')

    async def request_code(self, account_id):
        try:
            df = pd.read_excel(self.db_file)
            account = df[df['ID'] == account_id].iloc[0]
            
            # Добавляем поддержку прокси
            proxy = self.create_proxy_dict(self.current_proxy)
            
            self.code_request_client = TelegramClient(
                os.path.join(self.session_dir, f"{account['Phone']}.session"),
                int(account['API_ID']),
                account['API_HASH'],
                loop=self.loop,
                proxy=proxy
            )
            await self.code_request_client.connect()
            await self.code_request_client.send_code_request(account['Phone'])
            self.print_console(f"[+] Код отправлен на {account['Phone']}", 'success')
            code = await self.get_input("Ввод кода", "Введите код из Telegram:")
            if code:
                await self.code_request_client.sign_in(account['Phone'], code)
                self.print_console("[✓] Успешная авторизация", 'success')
        except Exception as e:
            self.print_console(f"[!] Ошибка: {str(e)}", 'error')

    async def get_input(self, title, prompt):
        future = asyncio.Future()
        self.root.after(0, lambda: self.show_auth_dialog(future, title, prompt))
        return await future

    def show_auth_dialog(self, future, title, prompt):
        dialog = AuthDialog(self.root, title, prompt, self.current_theme)
        self.root.wait_window(dialog)
        self.loop.call_soon_threadsafe(future.set_result, dialog.result)

    def create_tasks_interface(self):
        # Уже реализовано в create_widgets
        pass

    def create_console(self):
        # Консоль внизу окна
        console_frame = tk.Frame(self.root, bg=THEMES[self.current_theme]['bg'])
        console_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Заголовок консоли
        console_header = tk.Frame(console_frame, bg=THEMES[self.current_theme]['header_bg'], height=30)
        console_header.pack(fill=tk.X)
        
        tk.Label(
            console_header, 
            text="Консоль приложения",
            bg=THEMES[self.current_theme]['header_bg'],
            fg=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 10, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        # Кнопка очистки
        clear_btn = tk.Button(
            console_header, 
            text="Очистить", 
            command=self.clear_console,
            bg=THEMES[self.current_theme]['secondary_bg'],
            fg=THEMES[self.current_theme]['text'], 
            relief='flat', 
            font=('Segoe UI', 9)
        )
        clear_btn.pack(side=tk.RIGHT, padx=10)
        
        # Область вывода консоли
        self.console_output = scrolledtext.ScrolledText(
            console_frame, 
            wrap=tk.WORD,
            bg=THEMES[self.current_theme]['secondary_bg'], 
            fg=THEMES[self.current_theme]['text'],
            insertbackground=THEMES[self.current_theme]['text'],
            font=('Segoe UI', 10),
            height=8
        )
        self.console_output.pack(fill=tk.BOTH, expand=True, padx=1, pady=(0, 1))
        self.console_output.config(state=tk.DISABLED)
        
        # Настройка тегов для цветного вывода
        self.console_output.tag_config('info', foreground=THEMES[self.current_theme]['console_info'])
        self.console_output.tag_config('warning', foreground=THEMES[self.current_theme]['console_warning'])
        self.console_output.tag_config('error', foreground=THEMES[self.current_theme]['console_error'])
        self.console_output.tag_config('success', foreground=THEMES[self.current_theme]['console_success'])
        self.console_output.tag_config('command', foreground=THEMES[self.current_theme]['console_command'])
        
        # Поле ввода команд
        self.console_input = tk.Entry(
            console_frame, 
            bg=THEMES[self.current_theme]['input_bg'], 
            fg=THEMES[self.current_theme]['text'],
            insertbackground=THEMES[self.current_theme]['text'],
            relief='flat', 
            font=('Segoe UI', 12)
        )
        self.console_input.pack(fill=tk.X, side=tk.BOTTOM)
        self.console_input.bind("<Return>", self.handle_console_command)
        self.console_input.insert(0, "Введите команду...")
        self.console_input.bind("<FocusIn>", lambda e: self.console_input.delete(0, tk.END))
        
        # Привязка стрелок для истории команд
        self.console_input.bind("<Up>", self.show_prev_command)
        self.console_input.bind("<Down>", self.show_next_command)

    def show_prev_command(self, event):
        if self.command_history:
            if self.history_index == -1:
                self.history_index = len(self.command_history) - 1
            else:
                self.history_index = max(0, self.history_index - 1)
            
            self.console_input.delete(0, tk.END)
            self.console_input.insert(0, self.command_history[self.history_index])
        return "break"

    def show_next_command(self, event):
        if self.command_history:
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.console_input.delete(0, tk.END)
                self.console_input.insert(0, self.command_history[self.history_index])
            else:
                self.history_index = len(self.command_history)
                self.console_input.delete(0, tk.END)
        return "break"

    def clear_console(self):
        self.console_output.config(state=tk.NORMAL)
        self.console_output.delete(1.0, tk.END)
        self.console_output.config(state=tk.DISABLED)

    def handle_console_command(self, event):
        command = self.console_input.get()
        self.console_input.delete(0, tk.END)
        
        # Сохраняем команду в историю
        if command and command != "Введите команду...":
            self.command_history.append(command)
            self.history_index = len(self.command_history)
        
        self.execute_command(command)

    def execute_command(self, command):
        if command.lower() in ["clear", "очистить"]:
            self.clear_console()
            self.print_console("Консоль очищена", 'info')
        elif command.lower() in ["proxy", "прокси"]:
            if self.current_proxy:
                self.print_console(f"[🌐] Активный прокси: {self.current_proxy['name']} ({self.current_proxy['type']}://{self.current_proxy['host']}:{self.current_proxy['port']})", 'info')
            else:
                self.print_console("[🌐] Прокси не активен", 'warning')
        elif command.lower() in ["help", "помощь"]:
            self.show_help()
        elif command.lower().startswith("theme"):
            parts = command.split()
            if len(parts) > 1:
                new_theme = parts[1].lower()
                if new_theme in ['dark', 'light']:
                    self.change_theme(new_theme)
                    self.print_console(f"[✓] Тема изменена на {'светлую' if new_theme == 'light' else 'темную'}", 'success')
                else:
                    self.print_console("Доступные темы: dark, light", 'error')
            else:
                current = 'светлая' if self.current_theme == 'light' else 'темная'
                self.print_console(f"Текущая тема: {current}. Используйте: theme [dark/light]", 'info')
        elif command.lower() in ["accounts", "аккаунты"]:
            self.print_console("[!] Список аккаунтов:", 'info')
            df = pd.read_excel(self.db_file)
            for _, row in df.iterrows():
                self.print_console(f"    ID: {row['ID']}, Телефон: {row['Phone']}", 'info')
        elif command.lower() in ["tasklist", "задачи"]:
            self.print_console("[!] Активные задачи:", 'info')
            for task in self.active_tasks:
                self.print_console(f"    ID: {task['task_id']}, Тип: {task['type']}, Статус: {task['status']}", 'info')
        elif command.lower().startswith("check"):
            parts = command.split()
            if len(parts) > 1:
                try:
                    account_id = int(parts[1])
                    self.run_async_task(self.check_account_ban(account_id))
                except ValueError:
                    self.print_console("Ошибка: Некорректный ID аккаунта", 'error')
            else:
                self.print_console("Используйте: check [id]", 'error')
        elif command.lower().startswith("cancel"):
            parts = command.split()
            if len(parts) > 1:
                try:
                    task_id = int(parts[1])
                    self.cancel_task_by_id(task_id)
                except ValueError:
                    self.print_console("Ошибка: Некорректный ID задачи", 'error')
            else:
                self.print_console("Используйте: cancel [id_задачи]", 'error')
        elif command.lower() in ["exit", "выход"]:
            self.logout()
        elif command.lower() in ["open all", "openall"]:
            self.show_warm_up_dialog()
        else:
            self.print_console(f"[!] Неизвестная команда: {command}", 'error')
            self.print_console("Введите 'help' для списка команд", 'info')

    def show_warm_up_dialog(self):
        dialog = WarmUpDialog(self.root, self.current_theme)
        self.root.wait_window(dialog)
        if hasattr(dialog, 'result') and dialog.result:
            min_interval, max_interval = dialog.result
            self.run_async_task(self.warm_up_accounts(min_interval, max_interval))

    async def warm_up_accounts(self, min_interval, max_interval):
        try:
            if self.warming_up:
                self.print_console("[!] Прогрев уже выполняется", 'warning')
                return
                
            self.warming_up = True
            self.print_console(f"[🔥] Начинаем прогрев аккаунтов: интервал {min_interval}-{max_interval} сек", 'info')
            
            # Получаем список всех аккаунтов
            df = pd.read_excel(self.db_file)
            accounts = df.to_dict('records')
            
            for account in accounts:
                if not self.warming_up:
                    break
                    
                try:
                    self.print_console(f"[↻] Прогрев аккаунта ID: {account['ID']} ({account['Phone']})", 'info')
                    
                    # Создаем клиента
                    proxy = self.create_proxy_dict(self.current_proxy)
                    client = TelegramClient(
                        os.path.join(self.session_dir, f"{account['Phone']}.session"),
                        int(account['API_ID']),
                        account['API_HASH'],
                        loop=self.loop,
                        proxy=proxy
                    )
                    
                    # Подключаемся
                    await client.connect()
                    
                    # Проверяем авторизацию
                    if not await client.is_user_authorized():
                        self.print_console(f"[!] Аккаунт {account['Phone']} не авторизован", 'warning')
                        continue
                    
                    # Получаем информацию о себе
                    me = await client.get_me()
                    self.print_console(f"[✓] Успешный вход: @{me.username or me.first_name}", 'success')
                    
                    # Генерируем случайный интервал
                    delay = random.randint(min_interval, max_interval)
                    self.print_console(f"⏳ Ожидание {delay} сек...", 'info')
                    await asyncio.sleep(delay)
                    
                    # Отключаемся
                    await client.disconnect()
                    
                except Exception as e:
                    self.print_console(f"[!] Ошибка прогрева аккаунта {account['ID']}: {str(e)}", 'error')
            
            self.print_console("[✓] Прогрев всех аккаунтов завершен", 'success')
            self.warming_up = False
        except Exception as e:
            self.print_console(f"[!] Ошибка прогрева: {str(e)}", 'error')
            self.warming_up = False

    def show_help(self):
        help_text = """
[Список команд]
help - Показать список команд
proxy - Показать статус прокси
theme [dark/light] - Изменить тему оформления
accounts - Показать список аккаунтов
tasklist - Показать активные задачи
check [id] - Проверить статус аккаунта (бан)
cancel [task_id] - Отменить задачу
open all - Прогреть все аккаунты
clear - Очистить консоль
exit - Выйти из приложения
"""
        self.print_console(help_text, 'info')

    async def check_account_ban(self, account_id):
        try:
            client = await self.get_client_for_account(account_id)
            if not client:
                self.print_console(f"[!] Аккаунт {account_id} не найден или не авторизован", 'error')
                return
            
            try:
                # Пробуем получить информацию о себе
                me = await client.get_me()
                self.print_console(f"[✓] Аккаунт {account_id} активен: @{me.username or me.first_name}", 'success')
            except Exception as e:
                if "A wait of" in str(e) or "FloodWaitError" in str(e):
                    self.print_console(f"[!] Аккаунт {account_id} временно заблокирован", 'warning')
                elif "deactivated" in str(e).lower():
                    self.print_console(f"[!] Аккаунт {account_id} забанен", 'error')
                else:
                    self.print_console(f"[!] Ошибка проверки аккаунта {account_id}: {str(e)}", 'error')
        except Exception as e:
            self.print_console(f"[!] Ошибка проверки аккаунта: {str(e)}", 'error')

    def cancel_task_by_id(self, task_id):
        for task in self.active_tasks:
            if task['task_id'] == task_id:
                task['status'] = 'Отменена'
                self.print_console(f"[✓] Задача ID {task_id} отменена", 'success')
                self.update_tasks_list()
                return
        self.print_console(f"[!] Задача с ID {task_id} не найдена", 'error')

    def add_account(self):
        phone = simpledialog.askstring("Добавить аккаунт", "Введите номер телефона:", parent=self.root)
        api_id = simpledialog.askstring("Добавить аккаунт", "Введите API ID:", parent=self.root)
        hash_id = simpledialog.askstring("Добавить аккаунт", "Введите HASH ID:", parent=self.root)
        if all([phone, api_id, hash_id]):
            try:
                df = pd.read_excel(self.db_file)
                new_id = df['ID'].max() + 1 if not df.empty else 1
                new_row = {'ID': new_id, 'Phone': phone, 'API_ID': api_id, 'API_HASH': hash_id}
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                df.to_excel(self.db_file, index=False)
                self.update_accounts_list()
                self.print_console(f"[+] Аккаунт {phone} добавлен с ID {new_id}", 'success')
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка записи: {str(e)}", parent=self.root)
        else:
            messagebox.showerror("Ошибка", "Все поля обязательны для заполнения", parent=self.root)

    def edit_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите аккаунт для редактирования", parent=self.root)
            return
        values = self.tree.item(selected[0])['values']
        current_data = {'id': values[0], 'phone': values[1], 'api_id': values[2], 'api_hash': values[3]}
        dialog = EditAccountDialog(self.root, self.current_theme, current_data)
        self.root.wait_window(dialog)
        if hasattr(dialog, 'result'):
            try:
                df = pd.read_excel(self.db_file)
                index = df[df['ID'] == int(dialog.result['id'])].index[0]
                df.at[index, 'Phone'] = dialog.result['phone']
                df.at[index, 'API_ID'] = dialog.result['api_id']
                df.at[index, 'API_HASH'] = dialog.result['api_hash']
                df.to_excel(self.db_file, index=False)
                self.update_accounts_list()
                self.print_console(f"[✓] Аккаунт ID {dialog.result['id']} обновлен", 'success')
            except Exception as e:
                self.print_console(f"[!] Ошибка обновления: {str(e)}", 'error')

    def delete_account(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите аккаунт для удаления", parent=self.root)
            return
        values = self.tree.item(selected[0])['values']
        if messagebox.askyesno("Подтверждение", f"Удалить аккаунт ID {values[0]} ({values[1]})?", parent=self.root):
            try:
                df = pd.read_excel(self.db_file)
                df = df[df['ID'] != values[0]]
                df.to_excel(self.db_file, index=False)
                session_file = os.path.join(self.session_dir, f"{values[1]}.session")
                if os.path.exists(session_file):
                    os.remove(session_file)
                self.update_accounts_list()
                self.print_console(f"[✓] Аккаунт ID {values[0]} удален", 'success')
            except Exception as e:
                self.print_console(f"[!] Ошибка удаления: {str(e)}", 'error')

    def update_accounts_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            df = pd.read_excel(self.db_file)
            for _, row in df.iterrows():
                self.tree.insert("", 'end', values=(row['ID'], row['Phone'], row['API_ID'], row['API_HASH']))
        except Exception as e:
            self.print_console(f"[!] Ошибка чтения базы данных: {str(e)}", 'error')

    def init_login(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Ошибка", "Выберите аккаунт", parent=self.root)
            return
        values = self.tree.item(selected[0])['values']
        if len(values) != 4:
            messagebox.showerror("Ошибка", "Некорректные данные аккаунта", parent=self.root)
            return
        account_id, phone, api_id, api_hash = values
        self.run_async_task(self.auth_flow(phone, api_id, api_hash))

    def run_async_task(self, coroutine):
        asyncio.run_coroutine_threadsafe(coroutine, self.loop)

    async def auth_flow(self, phone, api_id, api_hash):
        try:
            session_path = os.path.join(self.session_dir, f"{phone}.session")
            
            # Добавляем поддержку прокси
            proxy = self.create_proxy_dict(self.current_proxy)
            
            client = TelegramClient(
                session_path,
                int(api_id),
                api_hash,
                loop=self.loop,
                proxy=proxy
            )
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = await self.get_input("Подтверждение входа", "Введите код из Telegram:")
                if not code:
                    return
                try:
                    await client.sign_in(phone, code)
                except Exception as e:
                    if "password" in str(e):
                        password = await self.get_input("Двухэтапная аутентификация", "Введите пароль:")
                        await client.sign_in(password=password)
            if await client.is_user_authorized():
                self.print_console(f"[+] Успешная авторизация: {phone}", 'success')
                # Создаем новое окно для аккаунта
                account_window = AccountWindow(self.root, self, phone, client, self.current_theme)
                self.account_windows.append(account_window)
            else:
                self.print_console("[!] Ошибка авторизации", 'error')
        except Exception as e:
            self.print_console(f"[!] Критическая ошибка: {str(e)}", 'error')

    def print_console(self, text, tag=None):
        timestamp = datetime.now().strftime("[%H:%M:%S]")
        self.console_output.config(state=tk.NORMAL)
        
        # Добавляем временную метку
        self.console_output.insert(tk.END, f"{timestamp} ", 'info' if tag else None)
        
        # Добавляем текст с указанным тегом
        if tag:
            self.console_output.insert(tk.END, f"{text}\n", tag)
        else:
            self.console_output.insert(tk.END, f"{text}\n")
        
        self.console_output.see(tk.END)
        self.console_output.config(state=tk.DISABLED)

    def show_settings(self):
        settings_dialog = tk.Toplevel(self.root)
        settings_dialog.title("Настройки")
        settings_dialog.geometry("300x250")
        settings_dialog.configure(bg=THEMES[self.current_theme]['bg'])
        settings_dialog.resizable(False, False)
        
        # Центрируем окно
        settings_dialog.update_idletasks()
        width = settings_dialog.winfo_width()
        height = settings_dialog.winfo_height()
        x = (settings_dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (settings_dialog.winfo_screenheight() // 2) - (height // 2)
        settings_dialog.geometry(f'+{x}+{y}')
        
        # Выбор темы
        theme_frame = tk.Frame(settings_dialog, bg=THEMES[self.current_theme]['bg'])
        theme_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            theme_frame, 
            text="Выберите тему:",
            background=THEMES[self.current_theme]['bg'], 
            foreground=THEMES[self.current_theme]['text']
        ).pack(anchor='w')
        
        theme_var = tk.StringVar(value=self.current_theme)
        
        dark_theme = ttk.Radiobutton(
            theme_frame, 
            text="Темная", 
            variable=theme_var, 
            value='dark',
            command=lambda: self.change_theme('dark')
        )
        dark_theme.pack(anchor='w', pady=5)
        
        light_theme = ttk.Radiobutton(
            theme_frame, 
            text="Светлая", 
            variable=theme_var, 
            value='light',
            command=lambda: self.change_theme('light')
        )
        light_theme.pack(anchor='w', pady=5)
        
        # Интервал обновления
        interval_frame = tk.Frame(settings_dialog, bg=THEMES[self.current_theme]['bg'])
        interval_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(
            interval_frame, 
            text="Интервал обновления (сек):",
            background=THEMES[self.current_theme]['bg'], 
            foreground=THEMES[self.current_theme]['text']
        ).pack(anchor='w')
        
        interval_var = tk.IntVar(value=self.refresh_interval)
        interval_entry = ttk.Entry(interval_frame, textvariable=interval_var, width=10)
        interval_entry.pack(anchor='w', pady=5)
        
        # Кнопки
        btn_frame = tk.Frame(settings_dialog, bg=THEMES[self.current_theme]['bg'])
        btn_frame.pack(pady=10)
        
        ttk.Button(
            btn_frame, 
            text="Сохранить", 
            command=lambda: self.change_refresh_interval(interval_var.get()),
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(
            btn_frame, 
            text="Отмена", 
            command=settings_dialog.destroy
        ).pack(side=tk.RIGHT, padx=10)

    def change_refresh_interval(self, interval):
        try:
            self.refresh_interval = int(interval)
            self.print_console(f"Интервал обновления изменен на {interval} сек", 'success')
        except ValueError:
            self.print_console("Ошибка: Введите число", 'error')

    def change_theme(self, theme):
        self.current_theme = theme
        self.apply_theme()

    def logout(self):
        if not messagebox.askyesno("Подтверждение", "Вы уверены, что хотите выйти?", parent=self.root):
            return
        
        # Закрываем все окна аккаунтов
        for window in self.account_windows:
            window.on_closing()
        
        self.account_windows = []
        self.print_console("[!] Выход выполнен", 'warning')

    async def execute_sub_task(self, task):
        try:
            for account_id in task['accounts']:
                if task['status'] != 'Активна':
                    break
                client = await self.get_client_for_account(account_id)
                if not client:
                    continue
                try:
                    entity = await client.get_entity(task['channel'])
                    await client(JoinChannelRequest(channel=entity))
                    self.print_console(f"[✓] Аккаунт {account_id} подписался на {task['channel']}", 'success')
                    delay = random.randint(task['min_interval'] * 60, task['max_interval'] * 60)
                    await asyncio.sleep(delay)
                except Exception as e:
                    self.print_console(f"[!] Ошибка подписки {account_id}: {str(e)}", 'error')
            task['status'] = 'Завершена'
            self.active_tasks = [t for t in self.active_tasks if t['status'] == 'Активна']
            self.update_tasks_list()
        except Exception as e:
            self.print_console(f"[!] Ошибка задачи: {str(e)}", 'error')
            task['status'] = 'Ошибка'
            self.active_tasks = [t for t in self.active_tasks if t['status'] == 'Активна']
            self.update_tasks_list()

    async def get_client_for_account(self, account_id):
        try:
            df = pd.read_excel(self.db_file)
            account = df[df['ID'] == account_id].iloc[0]
            session_path = os.path.join(self.session_dir, f"{account['Phone']}.session")
            
            # Добавляем поддержку прокси
            proxy = self.create_proxy_dict(self.current_proxy)
            
            client = TelegramClient(
                session_path,
                int(account['API_ID']),
                account['API_HASH'],
                loop=self.loop,
                proxy=proxy
            )
            await client.connect()
            if not await client.is_user_authorized():
                return None
            return client
        except Exception as e:
            return None

    def update_tasks_list(self):
        self.tasks_list.delete(*self.tasks_list.get_children())
        for task in self.active_tasks:
            if task['type'] == 'subscribe':
                details = f"Аккаунтов: {len(task['accounts'])} | Интервал: {task['min_interval']}-{task['max_interval']}мин"
                target = task['channel']
            elif task['type'] == 'create_chats':
                details = (f"Чатов: {task['chat_count']} | Тайм-аут: {task['timeout']}с | "
                          f"Пауза: каждые {task['pause_after']} чатов на {task['pause_duration']}с")
                target = f"Аккаунт {task['account_id']}"
            self.tasks_list.insert("", 'end', values=(task['type'], target, details, task['status']))

    def cancel_task(self):
        selected = self.tasks_list.selection()
        if not selected:
            return
        item = self.tasks_list.item(selected[0])
        target = item['values'][1]
        for task in self.active_tasks:
            if (task.get('channel') == target) or (task.get('account_id') and f"Аккаунт {task['account_id']}" == target):
                task['status'] = 'Отменена'
        self.active_tasks = [t for t in self.active_tasks if t['status'] == 'Активна']
        self.update_tasks_list()

    def on_closing(self):
        self.running = False
        self.warming_up = False
        self.loop.call_soon_threadsafe(self.loop.stop)
        if self.thread.is_alive():
            self.thread.join()
        
        # Закрываем все окна аккаунтов
        for window in self.account_windows:
            window.on_closing()
        
        self.root.destroy()

if __name__ == "__main__":
    if not os.path.exists('sessions'):
        os.makedirs('sessions')
    root = tk.Tk()
    app = TelegramAccountManager(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
