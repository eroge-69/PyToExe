import os
import json
import asyncio
import threading
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, colorchooser
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji
from telethon.errors import SessionPasswordNeededError
import logging

# Конфигурация
CONFIG_FILE = "tg_manager_config.json"
DEFAULT_CONFIG = {
    "api_id": 000000,
    "api_hash": "a0f4b835898asdfasfe851a7e3dc2f09dbad",
    "theme": {
        "bg": "#2c2f33",
        "fg": "white",
        "button_bg": "#7289da",
        "entry_bg": "#23272a",
        "listbox_bg": "#23272a",
        "listbox_fg": "white",
        "select_bg": "#7289da",
        "frame_bg": "#2c2f33",
        "label_bg": "#2c2f33",
        "labelframe_bg": "#2c2f33",
        "labelframe_fg": "white"
    }
}

class ConfigManager:
    @staticmethod
    def load_config():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    # Добавляем отсутствующие ключи темы
                    if "theme" not in config:
                        config["theme"] = DEFAULT_CONFIG["theme"]
                    else:
                        for key in DEFAULT_CONFIG["theme"]:
                            if key not in config["theme"]:
                                config["theme"][key] = DEFAULT_CONFIG["theme"][key]
                    return config
            except Exception as e:
                logging.error(f"Ошибка загрузки конфига: {e}")
                return DEFAULT_CONFIG
        return DEFAULT_CONFIG

    @staticmethod
    def save_config(config):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)

class TelegramManager:
    def __init__(self):
        self.clients = {}
        self.loop = asyncio.new_event_loop()
        self.config = ConfigManager.load_config()
        self.sessions_dir = "sessions"
        os.makedirs(self.sessions_dir, exist_ok=True)

    async def add_account(self, phone, ask_code_cb, ask_password_cb):
        session_name = os.path.join(self.sessions_dir, phone)
        client = TelegramClient(session_name, self.config["api_id"], self.config["api_hash"])
        
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.send_code_request(phone)
                code = await ask_code_cb()
                if not code:
                    return False
                
                try:
                    await client.sign_in(phone, code)
                except SessionPasswordNeededError:
                    password = await ask_password_cb()
                    if not password:
                        return False
                    await client.sign_in(password=password)
            
            self.clients[phone] = client
            logging.info(f"Аккаунт {phone} успешно добавлен")
            return True
            
        except Exception as e:
            logging.error(f"Ошибка добавления аккаунта {phone}: {str(e)}")
            await client.disconnect()
            return False

    async def join_channel_all(self, channel):
        results = {}
        for phone, client in self.clients.items():
            try:
                await client(JoinChannelRequest(channel))
                results[phone] = True
                logging.info(f"{phone}: успешно подписался на {channel}")
            except Exception as e:
                results[phone] = str(e)
                logging.error(f"{phone}: ошибка подписки - {str(e)}")
        return results

    async def react_to_specific_post(self, channel, post_id, emoji):
        results = {}
        for phone, client in self.clients.items():
            try:
                entity = await client.get_entity(channel)
                messages = await client.get_messages(entity, ids=post_id)
                if not messages:
                    results[phone] = "Пост не найден"
                    continue
                
                await client(SendReactionRequest(
                    peer=entity,
                    msg_id=post_id,
                    reaction=[ReactionEmoji(emoticon=emoji)]
                ))
                results[phone] = True
                logging.info(f"{phone}: успешно поставил реакцию '{emoji}' на пост {post_id}")
                
            except Exception as e:
                results[phone] = str(e)
                logging.error(f"{phone}: ошибка реакции - {str(e)}")
        return results

class ThemeEditor(tk.Toplevel):
    def __init__(self, parent, apply_callback):
        super().__init__(parent)
        self.title("Редактор темы")
        self.geometry("450x700")
        self.apply_callback = apply_callback
        self.config = ConfigManager.load_config()
        self.theme = self.config["theme"].copy()
        
        self.create_preview()
        self.create_controls()
        self.update_preview()
        
    def create_preview(self):
        preview_frame = ttk.Frame(self)
        preview_frame.pack(pady=10, padx=10, fill=tk.X)
        
        ttk.Label(preview_frame, text="Предпросмотр темы:").pack(anchor=tk.W)
        
        self.preview_label = ttk.Label(preview_frame, text="Пример текста")
        self.preview_label.pack(pady=5, anchor=tk.W)
        
        self.preview_btn = ttk.Button(preview_frame, text="Пример кнопки")
        self.preview_btn.pack(pady=5, fill=tk.X)
        
        self.preview_entry = ttk.Entry(preview_frame)
        self.preview_entry.pack(pady=5, fill=tk.X)
        self.preview_entry.insert(0, "Пример текста")
        
        self.preview_list = tk.Listbox(preview_frame, height=3)
        self.preview_list.pack(pady=5, fill=tk.X)
        for item in ["Элемент 1", "Элемент 2", "Элемент 3"]:
            self.preview_list.insert(tk.END, item)
        
        self.preview_labelframe = ttk.LabelFrame(preview_frame, text="Пример рамки")
        self.preview_labelframe.pack(pady=5, fill=tk.X)
        ttk.Label(self.preview_labelframe, text="Текст внутри рамки").pack()
    
    def create_controls(self):
        control_frame = ttk.Frame(self)
        control_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        colors = [
            ("Основной фон", "bg"),
            ("Цвет текста", "fg"),
            ("Фон кнопок", "button_bg"),
            ("Фон полей ввода", "entry_bg"),
            ("Фон списка", "listbox_bg"),
            ("Текст списка", "listbox_fg"),
            ("Выделение в списке", "select_bg"),
            ("Фон фреймов", "frame_bg"),
            ("Фон меток", "label_bg"),
            ("Фон LabelFrame", "labelframe_bg"),
            ("Текст LabelFrame", "labelframe_fg")
        ]
        
        for text, key in colors:
            frame = ttk.Frame(control_frame)
            frame.pack(fill=tk.X, pady=3)
            
            ttk.Label(frame, text=text, width=20).pack(side=tk.LEFT)
            
            color_btn = ttk.Button(
                frame,
                text="Изменить",
                command=lambda k=key: self.change_color(k),
                width=10
            )
            color_btn.pack(side=tk.LEFT, padx=5)
            
            canvas = tk.Canvas(frame, width=30, height=20, bd=0, highlightthickness=0)
            canvas.pack(side=tk.LEFT)
            canvas.create_rectangle(0, 0, 30, 20, fill=self.theme[key], outline="")
            setattr(self, f"{key}_indicator", canvas)
        
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(pady=15)
        
        ttk.Button(btn_frame, text="Применить", command=self.apply_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сбросить", command=self.reset_theme).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Отмена", command=self.destroy).pack(side=tk.LEFT, padx=5)
    
    def change_color(self, key):
        color = colorchooser.askcolor(title=f"Выберите цвет для {key}", initialcolor=self.theme[key])[1]
        if color:
            self.theme[key] = color
            getattr(self, f"{key}_indicator").delete("all")
            getattr(self, f"{key}_indicator").create_rectangle(0, 0, 30, 20, fill=color, outline="")
            self.update_preview()
    
    def update_preview(self):
        """Обновляет предпросмотр с новыми цветами"""
        try:
            # Основной фон окна
            self.configure(bg=self.theme["bg"])
            
            # Стиль для ttk виджетов
            style = ttk.Style()
            
            # Базовые настройки
            style.configure(".", 
                          background=self.theme["frame_bg"],
                          foreground=self.theme["fg"])
            
            # Элементы управления
            style.configure("TLabel",
                          background=self.theme["label_bg"],
                          foreground=self.theme["fg"])
            
            style.configure("TButton",
                          background=self.theme["button_bg"],
                          foreground=self.theme["fg"])
            
            style.configure("TEntry",
                          fieldbackground=self.theme["entry_bg"],
                          foreground=self.theme["fg"])
            
            style.configure("TFrame",
                          background=self.theme["frame_bg"])
            
            style.configure("TLabelframe",
                          background=self.theme["labelframe_bg"],
                          foreground=self.theme["labelframe_fg"])
            
            style.configure("TLabelframe.Label",
                          background=self.theme["labelframe_bg"],
                          foreground=self.theme["labelframe_fg"])
            
            # Обновляем стандартные tk виджеты
            self.preview_list.config(
                bg=self.theme["listbox_bg"],
                fg=self.theme["listbox_fg"],
                selectbackground=self.theme["select_bg"]
            )
            
            # Принудительное обновление виджетов предпросмотра
            self.preview_label.config(style="TLabel")
            self.preview_btn.config(style="TButton")
            self.preview_entry.config(style="TEntry")
            self.preview_labelframe.config(style="TLabelframe")
            
        except Exception as e:
            logging.error(f"Ошибка обновления предпросмотра: {e}")
    
    def apply_theme(self):
        self.config["theme"] = self.theme
        ConfigManager.save_config(self.config)
        self.apply_callback(self.theme)
        messagebox.showinfo("Успех", "Тема успешно применена!")
        self.destroy()
    
    def reset_theme(self):
        self.theme = DEFAULT_CONFIG["theme"].copy()
        for key in self.theme:
            if hasattr(self, f"{key}_indicator"):
                getattr(self, f"{key}_indicator").delete("all")
                getattr(self, f"{key}_indicator").create_rectangle(0, 0, 30, 20, fill=self.theme[key], outline="")
        self.update_preview()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Telegram Менеджер")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.config = ConfigManager.load_config()
        self.manager = TelegramManager()
        
        self.setup_menu()
        self.setup_ui()
        self.apply_theme(self.config["theme"])
        
        self.loop_thread = threading.Thread(
            target=self.start_loop,
            daemon=True
        )
        self.loop_thread.start()
    
    def setup_menu(self):
        menubar = tk.Menu(self)
        
        settings_menu = tk.Menu(menubar, tearoff=0)
        settings_menu.add_command(label="Редактор темы", command=self.open_theme_editor)
        settings_menu.add_separator()
        settings_menu.add_command(label="API Настройки", command=self.edit_api_settings)
        
        menubar.add_cascade(label="Настройки", menu=settings_menu)
        self.configure(menu=menubar)
    
    def setup_ui(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Account frame
        account_frame = ttk.LabelFrame(self.main_frame, text="Добавление аккаунта")
        account_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(account_frame, text="Номер телефона:").grid(row=0, column=0, padx=5, pady=5)
        self.phone_entry = ttk.Entry(account_frame)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.add_btn = ttk.Button(account_frame, text="Добавить", command=self.add_account)
        self.add_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Accounts list
        list_frame = ttk.LabelFrame(self.main_frame, text="Активные аккаунты")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.session_list = tk.Listbox(list_frame)
        self.session_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Channel operations
        channel_frame = ttk.LabelFrame(self.main_frame, text="Операции с каналами")
        channel_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(channel_frame, text="Канал:").grid(row=0, column=0, padx=5, pady=5)
        self.channel_entry = ttk.Entry(channel_frame)
        self.channel_entry.grid(row=0, column=1, padx=5, pady=5)
        
        self.join_btn = ttk.Button(channel_frame, text="Подписаться", command=self.join_channel)
        self.join_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Post reactions
        post_frame = ttk.LabelFrame(self.main_frame, text="Реакции на посты")
        post_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(post_frame, text="ID поста:").grid(row=0, column=0, padx=5, pady=5)
        self.post_id_entry = ttk.Entry(post_frame, width=10)
        self.post_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(post_frame, text="Реакция:").grid(row=0, column=2, padx=5, pady=5)
        self.reaction_entry = ttk.Entry(post_frame, width=10)
        self.reaction_entry.insert(0, "❤️")
        self.reaction_entry.grid(row=0, column=3, padx=5, pady=5)
        
        self.react_btn = ttk.Button(post_frame, text="Поставить реакцию", command=self.react_to_post)
        self.react_btn.grid(row=0, column=4, padx=5, pady=5)
    
    def apply_theme(self, theme):
        """Применяет тему ко всем элементам интерфейса"""
        try:
            self.config["theme"] = theme
            ConfigManager.save_config(self.config)
            
            # Основной фон окна
            self.configure(bg=theme["bg"])
            
            # Настройка стилей ttk
            self.style.configure(".", 
                               background=theme["frame_bg"],
                               foreground=theme["fg"])
            
            self.style.configure("TFrame",
                               background=theme["frame_bg"])
            
            self.style.configure("TLabel",
                               background=theme["label_bg"],
                               foreground=theme["fg"])
            
            self.style.configure("TButton",
                               background=theme["button_bg"],
                               foreground=theme["fg"])
            
            self.style.configure("TEntry",
                               fieldbackground=theme["entry_bg"],
                               foreground=theme["fg"])
            
            self.style.configure("TLabelframe",
                               background=theme["labelframe_bg"],
                               foreground=theme["labelframe_fg"])
            
            self.style.configure("TLabelframe.Label",
                               background=theme["labelframe_bg"],
                               foreground=theme["labelframe_fg"])
            
            # Обновляем стандартные tk виджеты
            self.session_list.config(
                bg=theme["listbox_bg"],
                fg=theme["listbox_fg"],
                selectbackground=theme["select_bg"]
            )
            
            # Принудительное обновление всех виджетов
            self.update_all_widgets()
            
        except Exception as e:
            logging.error(f"Ошибка применения темы: {e}")
            messagebox.showerror("Ошибка", f"Не удалось применить тему: {str(e)}")
    
    def update_all_widgets(self):
        """Рекурсивно обновляет все виджеты в интерфейсе"""
        for widget in self.winfo_children():
            self.update_widget_colors(widget)
    
    def update_widget_colors(self, widget):
        """Обновляет цвета конкретного виджета"""
        theme = self.config["theme"]
        
        try:
            if isinstance(widget, tk.Listbox):
                widget.config(
                    bg=theme["listbox_bg"],
                    fg=theme["listbox_fg"],
                    selectbackground=theme["select_bg"]
                )
            elif isinstance(widget, (tk.Frame, ttk.Frame)):
                widget.config(bg=theme["frame_bg"])
            elif isinstance(widget, (tk.Label, ttk.Label)):
                widget.config(bg=theme["label_bg"], fg=theme["fg"])
            elif isinstance(widget, (tk.Button, ttk.Button)):
                widget.config(bg=theme["button_bg"], fg=theme["fg"])
            elif isinstance(widget, (tk.Entry, ttk.Entry)):
                widget.config(
                    bg=theme["entry_bg"],
                    fg=theme["fg"],
                    insertbackground=theme["fg"]
                )
            
            # Рекурсивно обновляем дочерние виджеты
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self.update_widget_colors(child)
                    
        except Exception as e:
            logging.error(f"Ошибка обновления виджета: {e}")
    
    def open_theme_editor(self):
        ThemeEditor(self, self.apply_theme)
    
    def edit_api_settings(self):
        dialog = tk.Toplevel(self)
        dialog.title("API Настройки")
        
        ttk.Label(dialog, text="API ID:").grid(row=0, column=0, padx=5, pady=5)
        api_id_entry = ttk.Entry(dialog)
        api_id_entry.insert(0, str(self.config["api_id"]))
        api_id_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(dialog, text="API Hash:").grid(row=1, column=0, padx=5, pady=5)
        api_hash_entry = ttk.Entry(dialog)
        api_hash_entry.insert(0, self.config["api_hash"])
        api_hash_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def save():
            try:
                self.config["api_id"] = int(api_id_entry.get())
                self.config["api_hash"] = api_hash_entry.get()
                ConfigManager.save_config(self.config)
                self.manager.config = self.config
                dialog.destroy()
                messagebox.showinfo("Успех", "Настройки сохранены!")
            except ValueError:
                messagebox.showerror("Ошибка", "API ID должен быть числом")
        
        ttk.Button(dialog, text="Сохранить", command=save).grid(row=2, column=0, columnspan=2, pady=10)
    
    def start_loop(self):
        asyncio.set_event_loop(self.manager.loop)
        self.manager.loop.run_forever()
    
    def run_async(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.manager.loop)
    
    def on_close(self):
        """Корректное закрытие приложения"""
        try:
            # Остановка event loop
            self.manager.loop.call_soon_threadsafe(self.manager.loop.stop)
            # Ожидание завершения потока
            self.loop_thread.join(timeout=1)
            # Закрытие приложения
            self.destroy()
        except Exception as e:
            logging.error(f"Ошибка при закрытии: {e}")
            self.destroy()
    
    def add_account(self):
        phone = self.phone_entry.get().strip()
        if not phone:
            messagebox.showwarning("Ошибка", "Введите номер телефона")
            return

        self.add_btn.config(state=tk.DISABLED)
        
        async def ask_code():
            return simpledialog.askstring("Код подтверждения", "Введите код из Telegram:")
            
        async def ask_password():
            return simpledialog.askstring("Пароль", "Введите пароль от аккаунта:", show='*')
        
        future = self.run_async(self.manager.add_account(phone, ask_code, ask_password))
        future.add_done_callback(lambda f: self.after(0, self.add_account_done, f, phone))
    
    def add_account_done(self, future, phone):
        try:
            success = future.result()
            if success:
                self.session_list.insert(tk.END, phone)
                messagebox.showinfo("Успех", "Аккаунт успешно добавлен")
            else:
                messagebox.showerror("Ошибка", "Не удалось добавить аккаунт")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.add_btn.config(state=tk.NORMAL)
    
    def join_channel(self):
        channel = self.channel_entry.get().strip()
        if not channel:
            messagebox.showwarning("Ошибка", "Введите username или ссылку на канал")
            return
            
        self.join_btn.config(state=tk.DISABLED)
        
        future = self.run_async(self.manager.join_channel_all(channel))
        future.add_done_callback(lambda f: self.after(0, self.join_channel_done, f))
    
    def join_channel_done(self, future):
        try:
            results = future.result()
            success = [k for k, v in results.items() if v is True]
            errors = [f"{k}: {v}" for k, v in results.items() if v is not True]
            
            msg = []
            if success:
                msg.append(f"Успешно подписались: {len(success)}")
            if errors:
                msg.append(f"Ошибки ({len(errors)}):\n" + "\n".join(errors))
                
            messagebox.showinfo("Результат", "\n\n".join(msg))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.join_btn.config(state=tk.NORMAL)
    
    def react_to_post(self):
        channel = self.channel_entry.get().strip()
        post_id = self.post_id_entry.get().strip()
        emoji = self.reaction_entry.get().strip()
        
        if not channel or not post_id or not emoji:
            messagebox.showwarning("Ошибка", "Заполните все поля")
            return
            
        try:
            post_id = int(post_id)
        except ValueError:
            messagebox.showwarning("Ошибка", "ID поста должен быть числом")
            return
            
        self.react_btn.config(state=tk.DISABLED)
        
        future = self.run_async(self.manager.react_to_specific_post(channel, post_id, emoji))
        future.add_done_callback(lambda f: self.after(0, self.react_to_post_done, f))
    
    def react_to_post_done(self, future):
        try:
            results = future.result()
            success = [k for k, v in results.items() if v is True]
            errors = [f"{k}: {v}" for k, v in results.items() if v is not True]
            
            msg = []
            if success:
                msg.append(f"Успешно поставили реакцию: {len(success)}")
            if errors:
                msg.append(f"Ошибки ({len(errors)}):\n" + "\n".join(errors))
                
            messagebox.showinfo("Результат", "\n\n".join(msg))
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.react_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = App()
    app.mainloop()