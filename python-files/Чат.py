import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox
from datetime import datetime
import json
from tkinter import font as tkfont

class ModernChatClient:
    def __init__(self):
        # Настройка основного окна
        self.root = tk.Tk()
        self.root.title("Modern Chat Client")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        self.root.configure(bg="#36393F")
        
        self.client_socket = None
        self.is_connected = False
        self.username = "Гость"
        
        # Современная цветовая схема
        self.colors = {
            'primary': "#5865F2",      # Blue
            'secondary': "#2F3136",    # Dark gray
            'accent': "#43B581",       # Green
            'danger': "#ED4245",       # Red
            'warning': "#FAA61A",      # Orange
            'success': "#43B581",      # Green
            'background': "#36393F",   # Main background
            'surface': "#2F3136",      # Card background
            'text_primary': "#FFFFFF",
            'text_secondary': "#B9BBBE",
            'text_muted': "#72767D",
            'input_bg': "#40444B",
            'button_hover': "#4752C4"
        }
        
        # Настройка шрифтов
        self.title_font = tkfont.Font(family="Segoe UI", size=14, weight="bold")
        self.normal_font = tkfont.Font(family="Segoe UI", size=11)
        self.small_font = tkfont.Font(family="Segoe UI", size=10)
        
        self.setup_gui()
        
    def create_rounded_frame(self, parent, **kwargs):
        """Создает фрейм"""
        frame = tk.Frame(parent, **kwargs)
        return frame
    
    def create_modern_button(self, parent, text, command, **kwargs):
        """Создает современную кнопку"""
        bg_color = kwargs.pop('bg', self.colors['primary'])
        fg_color = kwargs.pop('fg', self.colors['text_primary'])
        hover_color = kwargs.pop('hover_color', self.colors['button_hover'])
        
        btn = tk.Button(parent, text=text, command=command,
                       bg=bg_color, fg=fg_color,
                       font=self.normal_font, relief="flat",
                       bd=0, padx=15, pady=8, **kwargs)
        
        # Эффект при наведении
        def on_enter(e):
            btn.configure(bg=hover_color)
        
        def on_leave(e):
            btn.configure(bg=bg_color)
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def create_modern_entry(self, parent, **kwargs):
        """Создает современное поле ввода"""
        return tk.Entry(parent, bg=self.colors['input_bg'], fg=self.colors['text_primary'],
                       font=self.normal_font, relief="flat", bd=0,
                       insertbackground=self.colors['text_primary'], **kwargs)
    
    def setup_gui(self):
        # Главный контейнер
        main_frame = self.create_rounded_frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Верхняя панель - настройки подключения
        self.setup_connection_panel(main_frame)
        
        # Основная область чата
        self.setup_chat_area(main_frame)
        
        # Панель ввода сообщения
        self.setup_input_panel(main_frame)
        
        # Статус бар
        self.setup_status_bar(main_frame)
    
    def setup_connection_panel(self, parent):
        conn_frame = self.create_rounded_frame(parent, bg=self.colors['surface'])
        conn_frame.pack(fill="x", pady=(0, 10))
        
        # Заголовок
        header = tk.Label(conn_frame, text="Подключение к серверу", 
                         bg=self.colors['surface'], fg=self.colors['text_primary'],
                         font=self.title_font)
        header.pack(pady=(15, 10))
        
        # Поля ввода
        input_frame = self.create_rounded_frame(conn_frame, bg=self.colors['surface'])
        input_frame.pack(fill="x", padx=20, pady=(0, 15))
        
        # Имя пользователя
        username_frame = self.create_rounded_frame(input_frame, bg=self.colors['surface'])
        username_frame.pack(side="left", padx=(0, 15))
        
        tk.Label(username_frame, text="Имя пользователя:", 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(anchor="w")
        
        self.username_var = tk.StringVar(value="Гость")
        username_entry = self.create_modern_entry(username_frame, textvariable=self.username_var,
                                                 width=15)
        username_entry.pack(pady=(5, 0))
        
        # IP сервера
        ip_frame = self.create_rounded_frame(input_frame, bg=self.colors['surface'])
        ip_frame.pack(side="left", padx=(0, 15))
        
        tk.Label(ip_frame, text="IP сервера:", 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(anchor="w")
        
        self.ip_var = tk.StringVar(value="127.0.0.1")
        ip_entry = self.create_modern_entry(ip_frame, textvariable=self.ip_var, width=15)
        ip_entry.pack(pady=(5, 0))
        
        # Порт
        port_frame = self.create_rounded_frame(input_frame, bg=self.colors['surface'])
        port_frame.pack(side="left", padx=(0, 15))
        
        tk.Label(port_frame, text="Порт:", 
                bg=self.colors['surface'], fg=self.colors['text_secondary']).pack(anchor="w")
        
        self.port_var = tk.StringVar(value="5555")
        port_entry = self.create_modern_entry(port_frame, textvariable=self.port_var, width=8)
        port_entry.pack(pady=(5, 0))
        
        # Кнопки подключения
        button_frame = self.create_rounded_frame(input_frame, bg=self.colors['surface'])
        button_frame.pack(side="right")
        
        self.connect_btn = self.create_modern_button(button_frame, "Подключиться", 
                                                    self.connect_server,
                                                    bg=self.colors['primary'])
        self.connect_btn.pack(side="left", padx=(0, 10))
        
        self.disconnect_btn = self.create_modern_button(button_frame, "Отключиться", 
                                                       self.disconnect_server,
                                                       bg=self.colors['danger'],
                                                       state="disabled")
        self.disconnect_btn.pack(side="left")
    
    def setup_chat_area(self, parent):
        chat_container = self.create_rounded_frame(parent, bg=self.colors['surface'])
        chat_container.pack(fill="both", expand=True, pady=(0, 10))
        
        # Заголовок чата
        chat_header = self.create_rounded_frame(chat_container, bg=self.colors['surface'])
        chat_header.pack(fill="x")
        
        tk.Label(chat_header, text="Общий чат", 
                bg=self.colors['surface'], fg=self.colors['text_primary'],
                font=self.title_font).pack(side="left", padx=20, pady=10)
        
        # Кнопка очистки чата
        clear_btn = self.create_modern_button(chat_header, "Очистить", 
                                             self.clear_chat,
                                             bg=self.colors['surface'],
                                             fg=self.colors['text_secondary'])
        clear_btn.pack(side="right", padx=20, pady=10)
        
        # Область сообщений
        text_frame = self.create_rounded_frame(chat_container, bg="#2B2D31")
        text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.chat_text = scrolledtext.ScrolledText(text_frame, 
                                                 bg="#2B2D31",
                                                 fg="#FFFFFF",
                                                 font=("Segoe UI", 11),
                                                 wrap="word",
                                                 relief="flat",
                                                 bd=0,
                                                 padx=10,
                                                 pady=10)
        self.chat_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.chat_text.config(state="disabled")
        
        # Настраиваем теги для цветов
        self.chat_text.tag_config("system", foreground="#FAA61A")      # Orange
        self.chat_text.tag_config("my_message", foreground="#5865F2")  # Blue
        self.chat_text.tag_config("other_message", foreground="#43B581")  # Green
        self.chat_text.tag_config("error", foreground="#ED4245")       # Red
        self.chat_text.tag_config("info", foreground="#00AFF4")        # Light blue
        self.chat_text.tag_config("timestamp", foreground="#72767D")   # Gray
    
    def setup_input_panel(self, parent):
        input_frame = self.create_rounded_frame(parent, bg=self.colors['surface'])
        input_frame.pack(fill="x", pady=(0, 10))
        
        input_container = self.create_rounded_frame(input_frame, bg=self.colors['surface'])
        input_container.pack(fill="both", padx=15, pady=15)
        
        # Поле ввода сообщения
        self.message_var = tk.StringVar()
        msg_entry = self.create_modern_entry(input_container, 
                                            textvariable=self.message_var,
                                            width=50)
        msg_entry.pack(side="left", fill="x", expand=True, padx=(15, 15))
        msg_entry.bind("<Return>", lambda e: self.send_message())
        
        # Кнопка отправки
        self.send_btn = self.create_modern_button(input_container, "Отправить", 
                                                 self.send_message,
                                                 bg=self.colors['primary'],
                                                 state="disabled")
        self.send_btn.pack(side="right")
    
    def setup_status_bar(self, parent):
        status_frame = self.create_rounded_frame(parent, bg=self.colors['surface'], height=40)
        status_frame.pack(fill="x")
        status_frame.pack_propagate(False)
        
        status_container = self.create_rounded_frame(status_frame, bg=self.colors['surface'])
        status_container.pack(fill="both", padx=15)
        
        self.status_var = tk.StringVar(value="Не подключено")
        status_label = tk.Label(status_container, 
                               textvariable=self.status_var,
                               bg=self.colors['surface'],
                               fg=self.colors['danger'],
                               font=("Segoe UI", 10, "bold"))
        status_label.pack(side="left")
        
        # Счетчик онлайн пользователей
        self.users_online_var = tk.StringVar(value="Онлайн: 0")
        users_label = tk.Label(status_container, 
                              textvariable=self.users_online_var,
                              bg=self.colors['surface'],
                              fg=self.colors['text_secondary'])
        users_label.pack(side="right")
    
    def clear_chat(self):
        self.chat_text.config(state="normal")
        self.chat_text.delete(1.0, "end")
        self.chat_text.config(state="disabled")
        self.add_system_message("Чат очищен")
    
    def add_message(self, message, message_type="info"):
        self.chat_text.config(state="normal")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Вставляем timestamp с отдельным тегом
        self.chat_text.insert("end", f"[{timestamp}] ", "timestamp")
        self.chat_text.insert("end", f"{message}\n", message_type)
        
        self.chat_text.config(state="disabled")
        self.chat_text.see("end")
    
    def add_system_message(self, message):
        self.add_message(f"{message}", "system")
    
    def add_chat_message(self, username, message, is_my_message=False):
        tag = "my_message" if is_my_message else "other_message"
        self.add_message(f"{username}: {message}", tag)
    
    def connect_server(self):
        server_ip = self.ip_var.get().strip()
        try:
            port = int(self.port_var.get().strip())
        except ValueError:
            messagebox.showerror("Ошибка", "Порт должен быть числом!")
            return
        
        if not server_ip:
            messagebox.showerror("Ошибка", "Введите IP сервера!")
            return
        
        self.username = self.username_var.get().strip() or "Гость"
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.settimeout(5)
            
            self.add_system_message(f"Подключаемся к {server_ip}:{port}...")
            
            self.client_socket.connect((server_ip, port))
            self.is_connected = True
            
            # Отправляем информацию о пользователе
            login_data = {
                'type': 'login',
                'username': self.username
            }
            self.client_socket.send(json.dumps(login_data).encode('utf-8'))
            
            self.connect_btn.config(state="disabled")
            self.disconnect_btn.config(state="normal")
            self.send_btn.config(state="normal")
            self.status_var.set("Подключено")
            
            self.add_system_message("Подключение установлено!")
            
            # Запускаем поток приема сообщений
            self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
            self.receive_thread.start()
            
        except socket.timeout:
            self.add_system_message("Таймаут подключения")
            messagebox.showerror("Ошибка", "Таймаут подключения к серверу")
        except ConnectionRefusedError:
            self.add_system_message("Подключение отклонено")
            messagebox.showerror("Ошибка", "Сервер недоступен или порт закрыт")
        except Exception as e:
            self.add_system_message(f"Ошибка подключения: {e}")
            messagebox.showerror("Ошибка", f"Не удалось подключиться:\n{e}")
    
    def disconnect_server(self):
        self.is_connected = False
        try:
            if self.client_socket:
                self.client_socket.close()
            self.connect_btn.config(state="normal")
            self.disconnect_btn.config(state="disabled")
            self.send_btn.config(state="disabled")
            self.status_var.set("Не подключено")
            self.add_system_message("Отключено от сервера")
        except Exception as e:
            self.add_system_message(f"Ошибка отключения: {e}")
    
    def send_message(self):
        if not self.is_connected or not self.client_socket:
            messagebox.showerror("Ошибка", "Не подключено к серверу!")
            return
        
        message = self.message_var.get().strip()
        if not message:
            messagebox.showwarning("Предупреждение", "Введите сообщение!")
            return
        
        try:
            # Формируем JSON сообщение
            message_data = {
                'type': 'message',
                'username': self.username,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            self.client_socket.send(json.dumps(message_data).encode('utf-8'))
            self.add_chat_message("Вы", message, is_my_message=True)
            self.message_var.set("")
            
        except Exception as e:
            self.add_system_message(f"Ошибка отправки: {e}")
            self.disconnect_server()
    
    def receive_messages(self):
        while self.is_connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    self.add_system_message("Сервер отключился")
                    self.disconnect_server()
                    break
                
                try:
                    message_data = json.loads(data.decode('utf-8'))
                    
                    if message_data['type'] == 'message':
                        self.add_chat_message(message_data['username'], message_data['message'])
                    elif message_data['type'] == 'system':
                        self.add_system_message(message_data['message'])
                    elif message_data['type'] == 'users_online':
                        self.users_online_var.set(f"Онлайн: {message_data['count']}")
                        
                except json.JSONDecodeError:
                    # Простой текст (для обратной совместимости)
                    message = data.decode('utf-8').strip()
                    self.add_system_message(f"Сервер: {message}")
                
            except socket.timeout:
                continue
            except Exception as e:
                if self.is_connected:
                    self.add_system_message(f"Ошибка получения данных: {e}")
                    self.disconnect_server()
                break
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.add_system_message("Чат-клиент запущен. Подключитесь к серверу.")
        self.root.mainloop()
    
    def on_closing(self):
        if self.is_connected:
            self.disconnect_server()
        self.root.destroy()

if __name__ == "__main__":
    chat_client = ModernChatClient()
    chat_client.run()