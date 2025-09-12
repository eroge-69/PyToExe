# north_client.py
import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk, Listbox
import queue
from datetime import datetime
import os

class NorthMessengerClient:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("North Messenger")
        self.root.geometry("1000x700")
        self.root.configure(bg="#ffffff")
        
        self.gui_queue = queue.Queue()
        self.host = ""
        self.port = 5555
        self.nickname = ""
        self.client = None
        self.connected = False
        self.running = True
        
        # Списки для управления пользователями
        self.muted_users = set()
        self.blocked_users = set()
        
        # Список открытых серверов
        self.public_servers = [
            {"name": "North Main Hub", "ip": "192.168.50.148", "users": 1245},
            {"name": "Local Test Server", "ip": "localhost", "users": 42}
        ]
        
        self.setup_gui()
        self.check_gui_queue()
        
    def setup_gui(self):
        # Главный контейнер
        main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#ffffff", sashwidth=4)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Левая панель - список серверов
        left_panel = tk.Frame(main_container, bg="#2b2d42", width=300)
        main_container.add(left_panel)
        
        # Заголовок левой панели
        left_header = tk.Frame(left_panel, bg="#1a1b2e", height=70)
        left_header.pack(fill=tk.X)
        left_header.pack_propagate(False)
        
        left_title = tk.Label(left_header, text="North Messenger", 
                            font=("Segoe UI", 16, "bold"), bg="#1a1b2e", fg="#4cc9f0")
        left_title.pack(pady=20)
        
        # Статус подключения
        self.left_status = tk.Label(left_header, text="Не подключено", 
                                  font=("Segoe UI", 9), bg="#1a1b2e", fg="#8d99ae")
        self.left_status.pack(pady=(0, 10))
        
        # Список серверов
        servers_frame = tk.Frame(left_panel, bg="#2b2d42")
        servers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        servers_label = tk.Label(servers_frame, text="Доступные серверы", 
                               font=("Segoe UI", 12, "bold"), bg="#2b2d42", fg="#4cc9f0")
        servers_label.pack(pady=10)
        
        self.servers_listbox = Listbox(servers_frame, bg="#3d3f5c", fg="#edf2f4", 
                                     font=("Segoe UI", 10), relief=tk.FLAT, bd=0,
                                     selectbackground="#4cc9f0", selectforeground="#2b2d42",
                                     highlightthickness=0)
        self.servers_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Заполняем список серверов
        for server in self.public_servers:
            self.servers_listbox.insert(tk.END, f"{server['name']} 👥 {server['users']}")
        
        self.servers_listbox.bind("<Double-Button-1>", self.connect_to_selected_server)
        
        # Поле для ввода IP
        custom_ip_frame = tk.Frame(servers_frame, bg="#2b2d42")
        custom_ip_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.ip_entry = tk.Entry(custom_ip_frame, bg="#3d3f5c", fg="#edf2f4", 
                               font=("Segoe UI", 10), relief=tk.FLAT, insertbackground='white')
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.ip_entry.insert(0, "IP сервера")
        self.ip_entry.bind("<FocusIn>", lambda e: self.clear_ip_placeholder())
        self.ip_entry.bind("<FocusOut>", lambda e: self.restore_ip_placeholder())
        
        connect_btn = tk.Button(custom_ip_frame, text="➤", font=("Segoe UI", 10),
                              bg="#4cc9f0", fg="#2b2d42", relief=tk.FLAT,
                              command=self.connect_custom_server, width=3)
        connect_btn.pack(side=tk.RIGHT)
        
        # Правая панель - чат
        right_panel = tk.Frame(main_container, bg="#edf2f4")
        main_container.add(right_panel)
        
        # Заголовок чата
        chat_header = tk.Frame(right_panel, bg="#1a1b2e", height=70)
        chat_header.pack(fill=tk.X)
        chat_header.pack_propagate(False)
        
        self.chat_title = tk.Label(chat_header, text="North Messenger", 
                                 font=("Segoe UI", 14, "bold"), bg="#1a1b2e", fg="#4cc9f0")
        self.chat_title.pack(pady=20)
        
        # Область сообщений
        chat_frame = tk.Frame(right_panel, bg="#8d99ae")
        chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_area = scrolledtext.ScrolledText(chat_frame, height=20, 
                                                 font=("Segoe UI", 11),
                                                 bg="#edf2f4", fg="#2b2d42", 
                                                 wrap=tk.WORD, relief=tk.FLAT, bd=0,
                                                 padx=15, pady=15)
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.chat_area.config(state=tk.DISABLED)
        
        # Настройка тегов для форматирования
        self.chat_area.tag_configure("timestamp", foreground="#8d99ae", font=("Segoe UI", 9))
        self.chat_area.tag_configure("username", foreground="#4cc9f0", font=("Segoe UI", 11, "bold"))
        self.chat_area.tag_configure("message", foreground="#2b2d42", font=("Segoe UI", 11))
        self.chat_area.tag_configure("system", foreground="#ef233c", font=("Segoe UI", 10, "italic"))
        self.chat_area.tag_configure("my_message", foreground="#2b2d42", font=("Segoe UI", 11))
        self.chat_area.tag_configure("my_username", foreground="#7209b7", font=("Segoe UI", 11, "bold"))
        
        # Панель ввода
        input_frame = tk.Frame(right_panel, bg="#8d99ae", height=80)
        input_frame.pack(fill=tk.X)
        input_frame.pack_propagate(False)
        
        input_container = tk.Frame(input_frame, bg="#edf2f4", relief=tk.SOLID, bd=1)
        input_container.pack(fill=tk.BOTH, padx=10, pady=10)
        
        self.message_entry = tk.Entry(input_container, font=("Segoe UI", 12), 
                                    bg="#edf2f4", fg="#2b2d42", relief=tk.FLAT,
                                    insertbackground='#2b2d42')
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10, pady=10)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.config(state=tk.DISABLED)
        self.message_entry.insert(0, "Введите сообщение...")
        self.message_entry.bind("<FocusIn>", self.clear_message_placeholder)
        self.message_entry.bind("<FocusOut>", self.restore_message_placeholder)
        
        # Кнопка отправки
        self.send_button = tk.Button(input_container, text="➤", font=("Segoe UI", 14),
                                   bg="#4cc9f0", fg="#2b2d42", relief=tk.FLAT,
                                   command=self.send_message, width=3, height=1)
        self.send_button.pack(side=tk.RIGHT, padx=10, pady=10)
        self.send_button.config(state=tk.DISABLED)
        
        # Статус бар
        status_bar = tk.Frame(right_panel, bg="#8d99ae", height=30)
        status_bar.pack(fill=tk.X)
        status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(status_bar, text="Не подключено", 
                                   font=("Segoe UI", 9), bg="#8d99ae", fg="#2b2d42")
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        # Кнопки управления
        control_frame = tk.Frame(status_bar, bg="#8d99ae")
        control_frame.pack(side=tk.RIGHT, padx=10, pady=5)
        
        self.connect_button = tk.Button(control_frame, text="Подключиться", 
                                      font=("Segoe UI", 9), bg="#4cc9f0", fg="#2b2d42",
                                      relief=tk.FLAT, command=self.connect_custom_server)
        self.connect_button.pack(side=tk.LEFT, padx=2)
        
        self.disconnect_button = tk.Button(control_frame, text="Отключиться", 
                                         font=("Segoe UI", 9), bg="#ef233c", fg="#edf2f4",
                                         relief=tk.FLAT, command=self.disconnect)
        self.disconnect_button.pack(side=tk.LEFT, padx=2)
        self.disconnect_button.config(state=tk.DISABLED)
        
        # Настройка разделителя
        main_container.sash_place(0, 300, 0)
        
    def clear_ip_placeholder(self):
        if self.ip_entry.get() == "IP сервера":
            self.ip_entry.delete(0, tk.END)
            self.ip_entry.config(fg="#edf2f4")
            
    def restore_ip_placeholder(self):
        if not self.ip_entry.get():
            self.ip_entry.insert(0, "IP сервера")
            self.ip_entry.config(fg="#8d99ae")
            
    def clear_message_placeholder(self, event):
        if self.message_entry.get() == "Введите сообщение...":
            self.message_entry.delete(0, tk.END)
            self.message_entry.config(fg="#2b2d42")
            
    def restore_message_placeholder(self, event):
        if not self.message_entry.get() and not self.connected:
            self.message_entry.insert(0, "Введите сообщение...")
            self.message_entry.config(fg="#8d99ae")
    
    def connect_to_selected_server(self, event):
        selection = self.servers_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.public_servers):
                server = self.public_servers[index]
                self.host = server["ip"]
                self.connect_to_server()
    
    def connect_custom_server(self):
        if self.ip_entry.get() and self.ip_entry.get() != "IP сервера":
            self.host = self.ip_entry.get()
        else:
            self.host = simpledialog.askstring("Подключение", "Введите IP сервера:", parent=self.root)
        
        if self.host:
            self.connect_to_server()
    
    def add_to_gui_queue(self, action, data):
        self.gui_queue.put((action, data))
    
    def check_gui_queue(self):
        try:
            while not self.gui_queue.empty():
                action, data = self.gui_queue.get_nowait()
                if action == "display_message":
                    self._display_message(data)
                elif action == "update_status":
                    text, color = data
                    self.status_label.config(text=text, fg=color)
                    self.left_status.config(text=text, fg=color)
                elif action == "enable_input":
                    self.message_entry.config(state=tk.NORMAL)
                    self.send_button.config(state=tk.NORMAL)
                    self.message_entry.delete(0, tk.END)
                    self.message_entry.config(fg="#2b2d42")
                elif action == "disable_input":
                    self.message_entry.config(state=tk.DISABLED)
                    self.send_button.config(state=tk.DISABLED)
                    self.message_entry.delete(0, tk.END)
                    self.message_entry.insert(0, "Введите сообщение...")
                    self.message_entry.config(fg="#8d99ae")
                elif action == "disable_connect":
                    self.connect_button.config(state=tk.DISABLED)
                    self.disconnect_button.config(state=tk.NORMAL)
                    self.chat_title.config(text=f"Чат: {self.host}")
                elif action == "enable_connect":
                    self.connect_button.config(state=tk.NORMAL)
                    self.disconnect_button.config(state=tk.DISABLED)
                    self.chat_title.config(text="North Messenger")
        except queue.Empty:
            pass
        
        if self.running:
            self.root.after(100, self.check_gui_queue)
    
    def connect_to_server(self):
        if self.connected:
            return
            
        try:
            if not self.host:
                messagebox.showerror("Ошибка", "Введите IP адрес сервера")
                return
            
            print(f"NORTH: Подключаюсь к {self.host}:{self.port}")
            
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.settimeout(5)
            self.client.connect((self.host, self.port))
            self.client.settimeout(None)
            
            print("NORTH: Подключение установлено, запрашиваю ник")
            
            # Получаем ник
            self.get_nickname()
            
            # Запуск потока для получения сообщений
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            self.add_to_gui_queue("update_status", (f"Подключено к {self.host}", "#27ae60"))
            self.add_to_gui_queue("enable_input", None)
            self.add_to_gui_queue("disable_connect", None)
            self.connected = True
            
            self.add_to_gui_queue("display_message", "✅ Подключение к серверу North установлено!")
            
        except socket.timeout:
            messagebox.showerror("Ошибка", "Таймаут подключения к серверу")
        except ConnectionRefusedError:
            messagebox.showerror("Ошибка", "Сервер недоступен. Убедитесь, что сервер запущен.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу: {e}")
            print(f"NORTH: Ошибка подключения: {e}")
    
    def get_nickname(self):
        self.nickname = simpledialog.askstring("Никнейм", "Введите ваш никнейм:", parent=self.root)
        if not self.nickname:
            self.nickname = f"Гость_{os.getpid() % 1000}"
        
        # Отправка ника серверу
        try:
            nick_request = self.client.recv(1024).decode('utf-8')
            print(f"NORTH: Получен запрос ника: {nick_request}")
            if nick_request == "NICK":
                self.client.send(self.nickname.encode('utf-8'))
                print(f"NORTH: Отправлен ник: {self.nickname}")
        except Exception as e:
            print(f"NORTH: Ошибка при отправке ника: {e}")
            raise Exception("Ошибка при регистрации ника")
        
        self.root.title(f"North Messenger - {self.nickname}")
    
    def receive_messages(self):
        print("NORTH: Поток приема сообщений запущен")
        while self.connected and self.running:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message:
                    print(f"NORTH: Получено сообщение: {message}")
                    
                    # Проверяем, не от заблокированного пользователя
                    if ":" in message:
                        username = message.split(":")[0].strip()
                        if username in self.blocked_users:
                            continue
                    
                    self.add_to_gui_queue("display_message", message)
                else:
                    print("NORTH: Пустое сообщение, разрыв соединения")
                    raise Exception("Соединение разорвано")
            except ConnectionAbortedError:
                print("NORTH: Соединение разорвано")
                break
            except ConnectionResetError:
                print("NORTH: Соединение сброшено")
                break
            except OSError as e:
                print(f"NORTH: Ошибка сокета: {e}")
                break
            except Exception as e:
                print(f"NORTH: Неизвестная ошибка: {e}")
                break
        
        if self.connected:
            self.add_to_gui_queue("display_message", "❌ Соединение с сервером потеряно!")
            self.disconnect()
    
    def send_message(self, event=None):
        if not self.connected:
            return
            
        message = self.message_entry.get().strip()
        if message and message != "Введите сообщение...":
            full_message = f"{self.nickname}: {message}"
            try:
                print(f"NORTH: Отправляю сообщение: {full_message}")
                self.client.send(full_message.encode('utf-8'))
                self.message_entry.delete(0, tk.END)
            except Exception as e:
                print(f"NORTH: Ошибка отправки: {e}")
                self.add_to_gui_queue("display_message", "❌ Ошибка отправки сообщения!")
                self.disconnect()
    
    def _display_message(self, message):
        timestamp = datetime.now().strftime("%H:%M")
        
        self.chat_area.config(state=tk.NORMAL)
        
        if ":" in message:
            # Это сообщение от пользователя
            username, msg_text = message.split(":", 1)
            username = username.strip()
            msg_text = msg_text.strip()
            
            # Вставляем timestamp
            self.chat_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
            
            # Определяем, наше ли это сообщение
            if username == self.nickname:
                # Вставляем имя пользователя (своё)
                self.chat_area.insert(tk.END, f"{username}: ", "my_username")
                # Вставляем текст сообщения
                self.chat_area.insert(tk.END, f"{msg_text}\n", "my_message")
            else:
                # Вставляем имя пользователя (чужое)
                self.chat_area.insert(tk.END, f"{username}: ", "username")
                # Вставляем текст сообщения
                self.chat_area.insert(tk.END, f"{msg_text}\n", "message")
        else:
            # Это системное сообщение
            self.chat_area.insert(tk.END, f"[{timestamp}] {message}\n", "system")
        
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.see(tk.END)
    
    def disconnect(self):
        self.connected = False
        try:
            if self.client:
                self.client.close()
        except:
            pass
        
        self.add_to_gui_queue("update_status", ("Не подключено", "#8d99ae"))
        self.add_to_gui_queue("disable_input", None)
        self.add_to_gui_queue("enable_connect", None)
    
    def on_closing(self):
        self.running = False
        self.disconnect()
        self.root.quit()
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

if __name__ == "__main__":
    client = NorthMessengerClient()
    client.run()