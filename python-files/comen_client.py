
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw, ImageTk
import socket
import threading
import json
import datetime
import hashlib
import os
import base64
import io
import time

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class NetworkManager:
    """Менеджер сетевых соединений"""
    def __init__(self, app):
        self.app = app
        self.socket = None
        self.connected = False
        self.receive_thread = None

    def connect(self, host, port):
        """Подключение к серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))
            self.connected = True

            # Запуск потока приема сообщений
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()

            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False

    def disconnect(self):
        """Отключение от сервера"""
        self.connected = False
        if self.socket:
            self.socket.close()

    def send(self, data):
        """Отправка данных на сервер"""
        if self.connected and self.socket:
            try:
                message = json.dumps(data, ensure_ascii=False).encode('utf-8')
                self.socket.send(message)
                return True
            except Exception as e:
                print(f"Ошибка отправки: {e}")
                self.connected = False
                return False
        return False

    def receive_messages(self):
        """Прием сообщений от сервера"""
        while self.connected:
            try:
                data = self.socket.recv(8192)
                if not data:
                    break

                message = json.loads(data.decode('utf-8'))
                self.handle_message(message)

            except Exception as e:
                print(f"Ошибка приема: {e}")
                self.connected = False
                break

    def handle_message(self, message):
        """Обработка входящих сообщений"""
        msg_type = message.get('type')

        if msg_type == 'register_response':
            self.app.handle_register_response(message)

        elif msg_type == 'login_response':
            self.app.handle_login_response(message)

        elif msg_type == 'contacts_response':
            self.app.handle_contacts_response(message)

        elif msg_type == 'search_response':
            self.app.handle_search_response(message)

        elif msg_type == 'add_contact_response':
            self.app.handle_add_contact_response(message)

        elif msg_type == 'incoming_message':
            self.app.handle_incoming_message(message)

        elif msg_type == 'user_status':
            self.app.handle_user_status(message)

        elif msg_type == 'typing_indicator':
            self.app.handle_typing_indicator(message)

        elif msg_type == 'new_contact':
            self.app.handle_new_contact(message)

        elif msg_type == 'user_info_response':
            self.app.handle_user_info_response(message)

        elif msg_type == 'update_profile_response':
            self.app.handle_update_profile_response(message)

class AnimatedButton(ctk.CTkButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bind("<Enter>", lambda e: self.configure(cursor="hand2"))
        self.bind("<Leave>", lambda e: self.configure(cursor=""))

class ContactCard(ctk.CTkFrame):
    def __init__(self, parent, username, bio, avatar_data, is_online, on_click):
        super().__init__(parent, fg_color="#17212B", corner_radius=12)

        self.username = username

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="x", padx=15, pady=12)

        # Аватар с индикатором онлайн
        avatar_container = ctk.CTkFrame(main_frame, fg_color="transparent")
        avatar_container.pack(side="left", padx=(0, 15))

        avatar_frame = ctk.CTkFrame(avatar_container, width=50, height=50,
                                   corner_radius=25, fg_color="#5288C1")
        avatar_frame.pack()
        avatar_frame.pack_propagate(False)

        if avatar_data:
            try:
                img_data = base64.b64decode(avatar_data)
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((50, 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                avatar_label = ctk.CTkLabel(avatar_frame, image=photo, text="")
                avatar_label.image = photo
                avatar_label.place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(avatar_frame, text=username[0].upper(),
                           font=("Segoe UI", 22, "bold"), text_color="white").place(
                    relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(avatar_frame, text=username[0].upper(),
                       font=("Segoe UI", 22, "bold"), text_color="white").place(
                relx=0.5, rely=0.5, anchor="center")

        # Онлайн индикатор
        if is_online:
            online_dot = ctk.CTkFrame(avatar_container, width=14, height=14,
                                     corner_radius=7, fg_color="#4FBF67",
                                     border_width=2, border_color="#17212B")
            online_dot.place(x=36, y=36)

        info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(info_frame, text=username, font=("Segoe UI", 14, "bold"),
                    text_color="white", anchor="w").pack(anchor="w")

        status_text = "онлайн" if is_online else bio[:40] + "..." if len(bio) > 40 else bio
        status_color = "#4FBF67" if is_online else "#8B98A5"

        ctk.CTkLabel(info_frame, text=status_text, font=("Segoe UI", 11),
                    text_color=status_color, anchor="w").pack(anchor="w")

        chat_btn = AnimatedButton(main_frame, text="💬", width=40, height=40,
                                 corner_radius=20, fg_color="#2B5278",
                                 hover_color="#3A6A9E",
                                 command=lambda: on_click(username))
        chat_btn.pack(side="right")

class MessageBubble(ctk.CTkFrame):
    def __init__(self, parent, username, message, time_str, is_own=False, msg_type="text"):
        super().__init__(parent, fg_color="transparent")

        bubble_color = "#2B5278" if is_own else "#182533"
        text_color = "#FFFFFF"
        align = "e" if is_own else "w"

        bubble_container = ctk.CTkFrame(self, fg_color="transparent")
        bubble_container.pack(fill="x", padx=10, pady=5)

        message_frame = ctk.CTkFrame(bubble_container, fg_color=bubble_color, corner_radius=15)
        message_frame.pack(anchor=align, padx=5)

        if not is_own:
            ctk.CTkLabel(message_frame, text=username, font=("Segoe UI", 12, "bold"),
                        text_color="#6AB7FF", anchor="w").pack(anchor="w", padx=12, pady=(8, 0))

        if msg_type == "voice":
            voice_frame = ctk.CTkFrame(message_frame, fg_color="transparent")
            voice_frame.pack(anchor="w", padx=12, pady=8)

            AnimatedButton(voice_frame, text="▶", width=35, height=35,
                          corner_radius=17, fg_color="#4A90E2").pack(side="left", padx=(0, 10))

            ctk.CTkLabel(voice_frame, text="🎤 Голосовое сообщение",
                        font=("Segoe UI", 11), text_color=text_color).pack(side="left")
        else:
            ctk.CTkLabel(message_frame, text=message, font=("Segoe UI", 13),
                        text_color=text_color, anchor="w", wraplength=400,
                        justify="left").pack(anchor="w", padx=12, pady=(2, 4))

        ctk.CTkLabel(message_frame, text=time_str, font=("Segoe UI", 9),
                    text_color="#8B98A5", anchor="e").pack(anchor="e", padx=12, pady=(0, 6))

class ComenMessenger(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Comen Messenger - Online")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.center_window()

        self.network = NetworkManager(self)
        self.current_user = None
        self.current_chat = None
        self.user_data = None
        self.contacts_data = {}
        self.pending_responses = {}

        self.colors = {
            "bg_main": "#0E1621",
            "bg_secondary": "#17212B",
            "bg_chat": "#0E1621",
            "bg_input": "#182533",
            "accent": "#5288C1",
            "accent_hover": "#6BA3D7",
            "text": "#FFFFFF",
            "text_secondary": "#8B98A5",
            "online": "#4FBF67",
            "separator": "#2B3843"
        }

        self.configure(fg_color=self.colors["bg_main"])

        self.show_server_connect_screen()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def show_server_connect_screen(self):
        """Экран подключения к серверу"""
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_main"])
        main_frame.pack(fill="both", expand=True)

        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        logo_frame = ctk.CTkFrame(center_frame, fg_color=self.colors["accent"],
                                 corner_radius=40, width=120, height=120)
        logo_frame.pack(pady=(0, 25))
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame, text="C", font=("Segoe UI", 60, "bold"),
                    text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center_frame, text="Comen Messenger",
                    font=("Segoe UI", 46, "bold"),
                    text_color=self.colors["accent"]).pack(pady=(0, 10))

        ctk.CTkLabel(center_frame, text="Онлайн версия",
                    font=("Segoe UI", 15),
                    text_color=self.colors["text_secondary"]).pack(pady=(0, 40))

        form_frame = ctk.CTkFrame(center_frame, fg_color=self.colors["bg_secondary"],
                                 corner_radius=20, width=450, height=280)
        form_frame.pack(pady=20, padx=20)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="🌐 Адрес сервера",
                    font=("Segoe UI", 13, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w", padx=30, pady=(30, 5))

        self.server_entry = ctk.CTkEntry(form_frame,
                                        placeholder_text="IP:PORT (например 192.168.1.100:5555)",
                                        font=("Segoe UI", 14), height=50, corner_radius=12,
                                        border_width=0, fg_color=self.colors["bg_input"])
        self.server_entry.insert(0, "localhost:5555")
        self.server_entry.pack(fill="x", padx=30, pady=(0, 25))

        def connect():
            server_addr = self.server_entry.get().strip()
            if not server_addr:
                messagebox.showerror("Ошибка", "Введите адрес сервера!")
                return

            try:
                host, port = server_addr.split(':')
                port = int(port)

                if self.network.connect(host, port):
                    messagebox.showinfo("Успех", "Подключено к серверу!")
                    self.show_welcome_screen()
                else:
                    messagebox.showerror("Ошибка", "Не удалось подключиться к серверу")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Неверный адрес сервера\n{e}")

        AnimatedButton(form_frame, text="Подключиться к серверу",
                      width=390, height=55, corner_radius=12,
                      font=("Segoe UI", 15, "bold"),
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=connect).pack(padx=30, pady=(0, 25))

        ctk.CTkLabel(form_frame, text="💡 Для локального тестирования используйте localhost:5555",
                    font=("Segoe UI", 10), text_color=self.colors["text_secondary"],
                    wraplength=390).pack(padx=30)

    def show_welcome_screen(self):
        """Экран входа/регистрации"""
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_main"])
        main_frame.pack(fill="both", expand=True)

        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        logo_frame = ctk.CTkFrame(center_frame, fg_color=self.colors["accent"],
                                 corner_radius=40, width=120, height=120)
        logo_frame.pack(pady=(0, 25))
        logo_frame.pack_propagate(False)

        ctk.CTkLabel(logo_frame, text="C", font=("Segoe UI", 60, "bold"),
                    text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(center_frame, text="Comen Messenger",
                    font=("Segoe UI", 46, "bold"),
                    text_color=self.colors["accent"]).pack(pady=(0, 10))

        ctk.CTkLabel(center_frame, text="Быстрый и безопасный мессенджер",
                    font=("Segoe UI", 15),
                    text_color=self.colors["text_secondary"]).pack(pady=(0, 50))

        AnimatedButton(center_frame, text="Войти в аккаунт", width=320, height=55,
                      corner_radius=15, font=("Segoe UI", 15, "bold"),
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=self.show_login_screen).pack(pady=(0, 15))

        AnimatedButton(center_frame, text="Создать аккаунт", width=320, height=55,
                      corner_radius=15, font=("Segoe UI", 15),
                      fg_color=self.colors["bg_secondary"],
                      hover_color=self.colors["separator"],
                      command=self.show_register_screen).pack()

    def show_login_screen(self):
        """Экран входа"""
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_main"])
        main_frame.pack(fill="both", expand=True)

        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        AnimatedButton(main_frame, text="← Назад", width=100, height=35,
                      corner_radius=10, fg_color="transparent",
                      hover_color=self.colors["bg_secondary"],
                      command=self.show_welcome_screen).place(x=20, y=20)

        ctk.CTkLabel(center_frame, text="Вход в аккаунт",
                    font=("Segoe UI", 32, "bold"),
                    text_color=self.colors["text"]).pack(pady=(0, 30))

        form_frame = ctk.CTkFrame(center_frame, fg_color=self.colors["bg_secondary"],
                                 corner_radius=20, width=450, height=350)
        form_frame.pack(padx=20)
        form_frame.pack_propagate(False)

        ctk.CTkLabel(form_frame, text="👤 Имя пользователя",
                    font=("Segoe UI", 13, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w", padx=30, pady=(30, 5))

        username_entry = ctk.CTkEntry(form_frame, placeholder_text="Введите username",
                                      font=("Segoe UI", 14), height=50, corner_radius=12,
                                      border_width=0, fg_color=self.colors["bg_input"])
        username_entry.pack(fill="x", padx=30, pady=(0, 20))

        ctk.CTkLabel(form_frame, text="🔒 Пароль",
                    font=("Segoe UI", 13, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w", padx=30, pady=(0, 5))

        password_entry = ctk.CTkEntry(form_frame, placeholder_text="Введите пароль",
                                     font=("Segoe UI", 14), height=50, corner_radius=12,
                                     border_width=0, fg_color=self.colors["bg_input"], show="●")
        password_entry.pack(fill="x", padx=30, pady=(0, 30))

        def login():
            username = username_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            self.network.send({
                'type': 'login',
                'username': username,
                'password': password_hash
            })

            self.pending_responses['login'] = username

        AnimatedButton(form_frame, text="Войти", width=390, height=55,
                      corner_radius=12, font=("Segoe UI", 15, "bold"),
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=login).pack(padx=30, pady=(0, 30))

    def show_register_screen(self):
        """Экран регистрации"""
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ctk.CTkFrame(self, fg_color=self.colors["bg_main"])
        main_frame.pack(fill="both", expand=True)

        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        AnimatedButton(main_frame, text="← Назад", width=100, height=35,
                      corner_radius=10, fg_color="transparent",
                      hover_color=self.colors["bg_secondary"],
                      command=self.show_welcome_screen).place(x=20, y=20)

        ctk.CTkLabel(center_frame, text="Создание аккаунта",
                    font=("Segoe UI", 32, "bold"),
                    text_color=self.colors["text"]).pack(pady=(0, 20))

        form_frame = ctk.CTkFrame(center_frame, fg_color=self.colors["bg_secondary"],
                                 corner_radius=20, width=500, height=550)
        form_frame.pack(padx=20)
        form_frame.pack_propagate(False)

        avatar_frame = ctk.CTkFrame(form_frame, width=100, height=100,
                                   corner_radius=50, fg_color=self.colors["accent"])
        avatar_frame.pack(pady=(25, 10))
        avatar_frame.pack_propagate(False)

        self.avatar_label = ctk.CTkLabel(avatar_frame, text="📷",
                                        font=("Segoe UI", 40), text_color="white")
        self.avatar_label.place(relx=0.5, rely=0.5, anchor="center")

        self.selected_avatar = None

        def select_avatar():
            filename = filedialog.askopenfilename(
                title="Выберите аватар",
                filetypes=[("Изображения", "*.png *.jpg *.jpeg *.gif *.bmp")]
            )
            if filename:
                self.selected_avatar = filename
                try:
                    img = Image.open(filename)
                    img = img.resize((100, 100), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.avatar_label.configure(image=photo, text="")
                    self.avatar_label.image = photo
                except:
                    messagebox.showerror("Ошибка", "Не удалось загрузить изображение")

        AnimatedButton(form_frame, text="Выбрать аватар", width=200, height=35,
                      corner_radius=10, fg_color=self.colors["bg_input"],
                      hover_color=self.colors["separator"],
                      command=select_avatar).pack(pady=(0, 20))

        ctk.CTkLabel(form_frame, text="👤 Имя пользователя",
                    font=("Segoe UI", 12, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w", padx=30, pady=(0, 5))

        username_entry = ctk.CTkEntry(form_frame, placeholder_text="Придумайте username",
                                      font=("Segoe UI", 13), height=45, corner_radius=12,
                                      border_width=0, fg_color=self.colors["bg_input"])
        username_entry.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkLabel(form_frame, text="📧 Email",
                    font=("Segoe UI", 12, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w", padx=30, pady=(0, 5))

        email_entry = ctk.CTkEntry(form_frame, placeholder_text="your@email.com",
                                   font=("Segoe UI", 13), height=45, corner_radius=12,
                                   border_width=0, fg_color=self.colors["bg_input"])
        email_entry.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkLabel(form_frame, text="🔒 Пароль",
                    font=("Segoe UI", 12, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w", padx=30, pady=(0, 5))

        password_entry = ctk.CTkEntry(form_frame, placeholder_text="Придумайте пароль",
                                     font=("Segoe UI", 13), height=45, corner_radius=12,
                                     border_width=0, fg_color=self.colors["bg_input"], show="●")
        password_entry.pack(fill="x", padx=30, pady=(0, 25))

        def register():
            username = username_entry.get().strip()
            email = email_entry.get().strip()
            password = password_entry.get().strip()

            if not username or not email or not password:
                messagebox.showerror("Ошибка", "Заполните все поля!")
                return

            avatar_data = None
            if self.selected_avatar:
                with open(self.selected_avatar, 'rb') as f:
                    avatar_data = base64.b64encode(f.read()).decode()

            password_hash = hashlib.sha256(password.encode()).hexdigest()

            self.network.send({
                'type': 'register',
                'username': username,
                'email': email,
                'password': password_hash,
                'avatar': avatar_data
            })

        AnimatedButton(form_frame, text="Создать аккаунт", width=440, height=50,
                      corner_radius=12, font=("Segoe UI", 14, "bold"),
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=register).pack(padx=30, pady=(0, 30))

    # Обработчики ответов от сервера
    def handle_register_response(self, message):
        if message['success']:
            self.after(0, lambda: messagebox.showinfo("Успех", "Регистрация успешна!"))
            self.after(100, self.show_login_screen)
        else:
            self.after(0, lambda: messagebox.showerror("Ошибка", message['message']))

    def handle_login_response(self, message):
        if message['success']:
            username = self.pending_responses.get('login')
            self.current_user = username
            self.user_data = message['user_data']
            self.after(0, lambda: messagebox.showinfo("Успех", "Вход выполнен!"))
            self.after(100, self.show_main_app)

            # Запросить контакты
            self.network.send({
                'type': 'get_contacts',
                'username': self.current_user
            })
        else:
            self.after(0, lambda: messagebox.showerror("Ошибка", message['message']))

    def handle_contacts_response(self, message):
        self.contacts_data = {c['username']: c for c in message['contacts']}
        self.after(0, self.refresh_contacts_list)

    def handle_search_response(self, message):
        if hasattr(self, 'search_results_frame'):
            self.after(0, lambda: self.display_search_results(message['results']))

    def handle_add_contact_response(self, message):
        if message['success']:
            self.after(0, lambda: messagebox.showinfo("Успех", "Контакт добавлен!"))
            self.network.send({
                'type': 'get_contacts',
                'username': self.current_user
            })

    def handle_incoming_message(self, message):
        sender = message['sender']

        # Если чат открыт с этим пользователем
        if self.current_chat == sender:
            if message['msg_type'] == 'text':
                self.after(0, lambda: self.display_message(
                    sender, message['text'], message['timestamp'], False, 'text'
                ))
            elif message['msg_type'] == 'voice':
                self.after(0, lambda: self.display_message(
                    sender, "", message['timestamp'], False, 'voice'
                ))

    def handle_user_status(self, message):
        username = message['username']
        status = message['status']

        if username in self.contacts_data:
            self.contacts_data[username]['online'] = (status == 'online')
            self.after(0, self.refresh_contacts_list)

    def handle_typing_indicator(self, message):
        # Можно добавить индикацию печати
        pass

    def handle_new_contact(self, message):
        self.after(0, lambda: messagebox.showinfo("Новый контакт", message['message']))

    def handle_user_info_response(self, message):
        pass

    def handle_update_profile_response(self, message):
        if message['success']:
            self.after(0, lambda: messagebox.showinfo("Успех", "Профиль обновлен!"))

    def show_main_app(self):
        """Главный экран с контактами"""
        for widget in self.winfo_children():
            widget.destroy()

        main_container = ctk.CTkFrame(self, fg_color=self.colors["bg_main"])
        main_container.pack(fill="both", expand=True)

        # Левая панель
        left_panel = ctk.CTkFrame(main_container, width=320, fg_color=self.colors["bg_secondary"])
        left_panel.pack(side="left", fill="y")
        left_panel.pack_propagate(False)

        # Хедер
        left_header = ctk.CTkFrame(left_panel, height=70, fg_color=self.colors["bg_main"])
        left_header.pack(fill="x")
        left_header.pack_propagate(False)

        user_avatar_frame = ctk.CTkFrame(left_header, width=45, height=45,
                                        corner_radius=22, fg_color=self.colors["accent"])
        user_avatar_frame.pack(side="left", padx=(15, 10), pady=12)
        user_avatar_frame.pack_propagate(False)

        if self.user_data and self.user_data.get("avatar"):
            try:
                img_data = base64.b64decode(self.user_data["avatar"])
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((45, 45), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                avatar_img = ctk.CTkLabel(user_avatar_frame, image=photo, text="")
                avatar_img.image = photo
                avatar_img.place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(user_avatar_frame, text=self.current_user[0].upper(),
                           font=("Segoe UI", 20, "bold"), text_color="white").place(
                    relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(user_avatar_frame, text=self.current_user[0].upper(),
                       font=("Segoe UI", 20, "bold"), text_color="white").place(
                relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(left_header, text=self.current_user,
                    font=("Segoe UI", 14, "bold"),
                    text_color=self.colors["text"]).pack(side="left", pady=12)

        AnimatedButton(left_header, text="⚙", width=35, height=35,
                      corner_radius=17, fg_color="transparent",
                      hover_color=self.colors["separator"],
                      command=self.show_settings).pack(side="right", padx=(0, 10))

        AnimatedButton(left_header, text="+", width=35, height=35,
                      corner_radius=17, fg_color="transparent",
                      hover_color=self.colors["separator"],
                      command=self.show_add_contact).pack(side="right", padx=5)

        # Поиск
        search_frame = ctk.CTkFrame(left_panel, height=60, fg_color="transparent")
        search_frame.pack(fill="x", padx=15, pady=(10, 5))
        search_frame.pack_propagate(False)

        ctk.CTkEntry(search_frame, placeholder_text="🔍 Поиск контактов...",
                    font=("Segoe UI", 13), height=45, corner_radius=22,
                    border_width=0, fg_color=self.colors["bg_input"]).pack(fill="both", expand=True)

        # Список контактов
        self.contacts_frame = ctk.CTkScrollableFrame(left_panel, fg_color="transparent")
        self.contacts_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.refresh_contacts_list()

        # Правая панель
        self.right_panel = ctk.CTkFrame(main_container, fg_color=self.colors["bg_chat"])
        self.right_panel.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(self.right_panel, text="Выберите контакт для начала общения",
                    font=("Segoe UI", 18),
                    text_color=self.colors["text_secondary"]).place(relx=0.5, rely=0.5, anchor="center")

    def refresh_contacts_list(self):
        """Обновить список контактов"""
        for widget in self.contacts_frame.winfo_children():
            widget.destroy()

        if not self.contacts_data:
            ctk.CTkLabel(self.contacts_frame,
                        text="Нет контактов\nНажмите + чтобы добавить",
                        font=("Segoe UI", 12),
                        text_color=self.colors["text_secondary"]).pack(pady=50)
            return

        for username, data in self.contacts_data.items():
            card = ContactCard(
                self.contacts_frame,
                username,
                data.get('bio', ''),
                data.get('avatar'),
                data.get('online', False),
                self.open_chat
            )
            card.pack(fill="x", pady=5)

    def show_add_contact(self):
        """Диалог добавления контакта"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Добавить контакт")
        dialog.geometry("500x600")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.colors["bg_main"])

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 300
        dialog.geometry(f'500x600+{x}+{y}')

        ctk.CTkLabel(dialog, text="Поиск пользователей",
                    font=("Segoe UI", 24, "bold"),
                    text_color=self.colors["text"]).pack(pady=(20, 15))

        search_frame = ctk.CTkFrame(dialog, fg_color=self.colors["bg_secondary"],
                                   corner_radius=15, height=60)
        search_frame.pack(fill="x", padx=20, pady=(0, 15))
        search_frame.pack_propagate(False)

        search_entry = ctk.CTkEntry(search_frame, placeholder_text="Введите username или email",
                                   font=("Segoe UI", 14), height=40, corner_radius=10,
                                   border_width=0, fg_color=self.colors["bg_input"])
        search_entry.pack(side="left", fill="both", expand=True, padx=15, pady=10)

        self.search_results_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        self.search_results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        def search():
            query = search_entry.get().strip()
            if not query:
                return

            self.network.send({
                'type': 'search_users',
                'query': query
            })

        AnimatedButton(search_frame, text="🔍", width=50, height=40,
                      corner_radius=10, fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=search).pack(side="right", padx=(5, 15), pady=10)

        search_entry.bind("<Return>", lambda e: search())

    def display_search_results(self, results):
        """Отобразить результаты поиска"""
        for widget in self.search_results_frame.winfo_children():
            widget.destroy()

        for result in results:
            if result["username"] == self.current_user:
                continue

            result_frame = ctk.CTkFrame(self.search_results_frame,
                                      fg_color=self.colors["bg_secondary"],
                                      corner_radius=12)
            result_frame.pack(fill="x", pady=5)

            info_frame = ctk.CTkFrame(result_frame, fg_color="transparent")
            info_frame.pack(fill="x", padx=15, pady=15)

            ctk.CTkLabel(info_frame, text=result["username"],
                        font=("Segoe UI", 14, "bold"),
                        text_color=self.colors["text"]).pack(anchor="w")

            ctk.CTkLabel(info_frame, text=result["email"],
                        font=("Segoe UI", 11),
                        text_color=self.colors["text_secondary"]).pack(anchor="w")

            status_text = "🟢 онлайн" if result.get('online') else result["bio"]
            ctk.CTkLabel(info_frame, text=status_text,
                        font=("Segoe UI", 11),
                        text_color=self.colors["text_secondary"]).pack(anchor="w", pady=(5, 0))

            if result["username"] in self.contacts_data:
                ctk.CTkLabel(result_frame, text="✓ В контактах",
                            font=("Segoe UI", 11),
                            text_color=self.colors["online"]).pack(pady=(0, 10))
            else:
                def add_contact(username=result["username"]):
                    self.network.send({
                        'type': 'add_contact',
                        'username': self.current_user,
                        'contact': username
                    })

                AnimatedButton(result_frame, text="Добавить в контакты",
                              width=200, height=35, corner_radius=10,
                              fg_color=self.colors["accent"],
                              hover_color=self.colors["accent_hover"],
                              command=add_contact).pack(pady=(0, 10))

    def show_settings(self):
        """Настройки"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Настройки")
        dialog.geometry("500x400")
        dialog.resizable(False, False)
        dialog.configure(fg_color=self.colors["bg_main"])

        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 250
        y = (dialog.winfo_screenheight() // 2) - 200
        dialog.geometry(f'500x400+{x}+{y}')

        ctk.CTkLabel(dialog, text="⚙ Настройки",
                    font=("Segoe UI", 28, "bold"),
                    text_color=self.colors["text"]).pack(pady=(20, 20))

        info_frame = ctk.CTkFrame(dialog, fg_color=self.colors["bg_secondary"],
                                 corner_radius=12)
        info_frame.pack(fill="x", padx=20, pady=(0, 20))

        if self.user_data:
            ctk.CTkLabel(info_frame, text=f"Username: {self.current_user}",
                        font=("Segoe UI", 13),
                        text_color=self.colors["text"]).pack(anchor="w", padx=20, pady=(15, 5))

            ctk.CTkLabel(info_frame, text=f"Email: {self.user_data.get('email', '')}",
                        font=("Segoe UI", 13),
                        text_color=self.colors["text"]).pack(anchor="w", padx=20, pady=(0, 5))

            ctk.CTkLabel(info_frame, text=f"Статус: {self.user_data.get('bio', '')}",
                        font=("Segoe UI", 13),
                        text_color=self.colors["text"]).pack(anchor="w", padx=20, pady=(0, 15))

        AnimatedButton(dialog, text="Выйти из аккаунта",
                      width=460, height=50, corner_radius=12,
                      fg_color="#FF4444", hover_color="#CC0000",
                      command=lambda: [dialog.destroy(), self.network.disconnect(), self.show_server_connect_screen()]).pack(padx=20, pady=(0, 20))

    def open_chat(self, contact_username):
        """Открыть чат"""
        self.current_chat = contact_username

        for widget in self.right_panel.winfo_children():
            widget.destroy()

        # Хедер чата
        chat_header = ctk.CTkFrame(self.right_panel, height=70,
                                   fg_color=self.colors["bg_secondary"])
        chat_header.pack(fill="x")
        chat_header.pack_propagate(False)

        contact_data = self.contacts_data.get(contact_username, {})

        # Аватар
        avatar_frame = ctk.CTkFrame(chat_header, width=45, height=45,
                                   corner_radius=22, fg_color=self.colors["accent"])
        avatar_frame.pack(side="left", padx=(20, 12), pady=12)
        avatar_frame.pack_propagate(False)

        if contact_data.get("avatar"):
            try:
                img_data = base64.b64decode(contact_data["avatar"])
                img = Image.open(io.BytesIO(img_data))
                img = img.resize((45, 45), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                avatar_img = ctk.CTkLabel(avatar_frame, image=photo, text="")
                avatar_img.image = photo
                avatar_img.place(relx=0.5, rely=0.5, anchor="center")
            except:
                ctk.CTkLabel(avatar_frame, text=contact_username[0].upper(),
                           font=("Segoe UI", 20, "bold"), text_color="white").place(
                    relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(avatar_frame, text=contact_username[0].upper(),
                       font=("Segoe UI", 20, "bold"), text_color="white").place(
                relx=0.5, rely=0.5, anchor="center")

        # Имя
        info_frame = ctk.CTkFrame(chat_header, fg_color="transparent")
        info_frame.pack(side="left", pady=12)

        ctk.CTkLabel(info_frame, text=contact_username,
                    font=("Segoe UI", 16, "bold"),
                    text_color=self.colors["text"]).pack(anchor="w")

        status_text = "● онлайн" if contact_data.get('online') else "оффлайн"
        status_color = self.colors["online"] if contact_data.get('online') else self.colors["text_secondary"]

        ctk.CTkLabel(info_frame, text=status_text,
                    font=("Segoe UI", 11),
                    text_color=status_color).pack(anchor="w")

        # Область чата
        self.chat_scroll = ctk.CTkScrollableFrame(self.right_panel,
                                                  fg_color=self.colors["bg_chat"])
        self.chat_scroll.pack(fill="both", expand=True)

        self.display_system_message(f"Чат с {contact_username}")

        # Панель ввода
        input_container = ctk.CTkFrame(self.right_panel, height=90,
                                      fg_color=self.colors["bg_secondary"])
        input_container.pack(fill="x")
        input_container.pack_propagate(False)

        input_frame = ctk.CTkFrame(input_container, fg_color="transparent")
        input_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Поле ввода
        self.message_entry = ctk.CTkTextbox(input_frame, height=60, corner_radius=15,
                                           fg_color=self.colors["bg_input"],
                                           border_width=0, font=("Segoe UI", 13), wrap="word")
        self.message_entry.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Кнопка отправки
        AnimatedButton(input_frame, text="➤", width=60, height=60,
                      corner_radius=30, font=("Segoe UI", 24),
                      fg_color=self.colors["accent"],
                      hover_color=self.colors["accent_hover"],
                      command=self.send_message_to_contact).pack(side="right")

    def send_message_to_contact(self):
        """Отправить сообщение контакту"""
        message = self.message_entry.get("1.0", "end-1c").strip()

        if not message or not self.current_chat:
            return

        timestamp = datetime.datetime.now().strftime("%H:%M")

        # Отправить на сервер
        self.network.send({
            'type': 'text_message',
            'sender': self.current_user,
            'recipient': self.current_chat,
            'text': message,
            'timestamp': timestamp
        })

        # Отобразить свое сообщение
        self.display_message(self.current_user, message, timestamp, True, 'text')
        self.message_entry.delete("1.0", "end")

    def display_message(self, username, message, time_str, is_own=False, msg_type="text"):
        """Отобразить сообщение"""
        bubble = MessageBubble(self.chat_scroll, username, message, time_str, is_own, msg_type)
        self.after(100, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

    def display_system_message(self, message):
        """Системное сообщение"""
        system_frame = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        system_frame.pack(fill="x", pady=8)

        ctk.CTkLabel(system_frame, text=message, font=("Segoe UI", 11, "italic"),
                    text_color=self.colors["text_secondary"]).pack()

        self.after(100, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))

if __name__ == "__main__":
    app = ComenMessenger()
    app.mainloop()
