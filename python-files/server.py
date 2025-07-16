import socket
import threading
from tkinter import *

class ServerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Сервер")

        # Инициализация сокета
        self.server_socket = None
        self.clients = []

        # Создание элементов интерфейса
        self.create_widgets()

    def create_widgets(self):
        self.status_label = Label(self.root, text="Ожидание подключения...")
        self.status_label.pack(pady=10)

        self.start_btn = Button(self.root, text="Запустить", command=self.start_server)
        self.start_btn.pack(pady=5)

        self.stop_btn = Button(self.root, text="Остановить", command=self.stop_server, state=DISABLED)
        self.stop_btn.pack(pady=5)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(1)

        self.status_label.config(text="Сервер запущен")
        self.start_btn.config(state=DISABLED)
        self.stop_btn.config(state=NORMAL)

        threading.Thread(target=self.accept_connections).start()

    def stop_server(self):
        if self.server_socket:
            self.server_socket.close()
            self.status_label.config(text="Сервер остановлен")
            self.start_btn.config(state=NORMAL)
            self.stop_btn.config(state=DISABLED)

    def accept_connections(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                self.clients.append(client_socket)
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
            except OSError:
                break

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    self.broadcast(data, client_socket)
                else:
                    break
            except:
                break
        self.clients.remove(client_socket)
        client_socket.close()

    def broadcast(self, message, sender_socket):
        for client in self.clients:
            if client != sender_socket:
                try:
                    client.send(message)
                except:
                    client.close()
                    self.clients.remove(client)

if __name__ == "__main__":
    root = Tk()
    app = ServerApp(root)
    root.mainloop()