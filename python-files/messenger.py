import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Простой мессенджер")
        self.root.geometry("500x600")
        self.root.resizable(False, False)

        self.nickname = None
        self.sock = None
        self.is_server = False

        # Главный интерфейс
        self.setup_ui()

    def setup_ui(self):
        # Выбор режима
        self.mode_frame = tk.Frame(self.root)
        self.mode_frame.pack(pady=20)

        tk.Label(self.mode_frame, text="Выберите режим:", font=("Arial", 12)).pack()

        tk.Button(self.mode_frame, text="Запустить сервер", command=self.start_server_mode, width=20).pack(pady=5)
        tk.Button(self.mode_frame, text="Подключиться как клиент", command=self.start_client_mode, width=20).pack(pady=5)

        # Чат-интерфейс (скрыт до подключения)
        self.chat_frame = tk.Frame(self.root)

        self.chat_box = scrolledtext.ScrolledText(self.chat_frame, state='disabled', wrap=tk.WORD, height=20, font=("Arial", 10))
        self.chat_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.msg_entry = tk.Entry(self.chat_frame, font=("Arial", 12))
        self.msg_entry.pack(padx=10, fill=tk.X)
        self.msg_entry.bind("<Return>", lambda event: self.send_message())

        self.send_btn = tk.Button(self.chat_frame, text="Отправить", command=self.send_message)
        self.send_btn.pack(pady=5)

        self.quit_btn = tk.Button(self.chat_frame, text="Выйти", command=self.disconnect)
        self.quit_btn.pack(pady=5)

    def start_server_mode(self):
        self.is_server = True
        self.nickname = "Сервер"
        self.setup_server()
        self.switch_to_chat_ui()

    def start_client_mode(self):
        self.is_server = False
        server_ip = simpledialog.askstring("Подключение", "Введите IP сервера (например, 192.168.1.100):")
        if not server_ip:
            return

        self.nickname = simpledialog.askstring("Никнейм", "Введите ваш никнейм:")
        if not self.nickname:
            return

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((server_ip, 12345))
            self.switch_to_chat_ui()
            # Получаем приветствие от сервера
            threading.Thread(target=self.receive_messages, daemon=True).start()
            self.sock.send(self.nickname.encode('utf-8'))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться: {e}")
            return

    def setup_server(self):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.bind(('0.0.0.0', 12345))
        self.server_sock.listen()
        self.clients = []
        self.nicknames = []

        threading.Thread(target=self.accept_clients, daemon=True).start()
        self.add_message("✅ Сервер запущен и ожидает подключений...")

    def accept_clients(self):
        while True:
            try:
                client, address = self.server_sock.accept()
                threading.Thread(target=self.handle_client, args=(client,), daemon=True).start()
            except:
                break

    def handle_client(self, client):
        try:
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            self.clients.append(client)
            self.nicknames.append(nickname)
            self.add_message(f"✅ {nickname} подключился.")

            # Рассылка всем, кроме отправителя
            self.broadcast(f"📢 {nickname} присоединился к чату!".encode('utf-8'))

            while True:
                message = client.recv(1024)
                if not message:
                    break
                self.broadcast(message, sender=client)
        except:
            pass
        finally:
            if client in self.clients:
                index = self.clients.index(client)
                self.clients.remove(client)
                nickname = self.nicknames.pop(index)
                self.add_message(f"❌ {nickname} отключился.")
                self.broadcast(f"📢 {nickname} покинул чат.".encode('utf-8'))
                client.close()

    def broadcast(self, message, sender=None):
        msg = message.decode('utf-8') if isinstance(message, bytes) else message
        for client in self.clients:
            if client != sender:  # Не отправлять отправителю
                try:
                    client.send(message if isinstance(message, bytes) else message.encode('utf-8'))
                except:
                    continue

    def receive_messages(self):
        while True:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    self.add_message(message)
            except:
                self.add_message("⚠️ Соединение с сервером потеряно.")
                break

    def send_message(self):
        msg = self.msg_entry.get().strip()
        if not msg:
            return

        self.msg_entry.delete(0, tk.END)

        if self.is_server:
            # Сервер отправляет от своего имени
            full_msg = f"{self.nickname}: {msg}"
            self.add_message(full_msg)
            self.broadcast(full_msg)
        else:
            # Клиент отправляет через сокет
            full_msg = f"{self.nickname}: {msg}"
            self.add_message(full_msg)
            try:
                self.sock.send(full_msg.encode('utf-8'))
            except:
                self.add_message("❌ Не удалось отправить сообщение.")

    def add_message(self, message):
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, message + "\n")
        self.chat_box.config(state='disabled')
        self.chat_box.yview(tk.END)

    def switch_to_chat_ui(self):
        self.mode_frame.pack_forget()
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        self.add_message("💬 Чат запущен. Начинайте общение!")

    def disconnect(self):
        if self.is_server:
            for client in self.clients:
                client.close()
            self.server_sock.close()
        elif self.sock:
            self.sock.close()

        self.chat_frame.pack_forget()
        self.mode_frame.pack(pady=20)
        self.add_message = lambda msg: None  # Отключаем добавление сообщений

        messagebox.showinfo("Отключено", "Вы отключились от чата.")

# Запуск приложения
if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()