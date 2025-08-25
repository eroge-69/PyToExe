# client.py
import socket
import threading


class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.host = host
        self.port = port
        self.nickname = input("Введите ваш никнейм: ")
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        try:
            self.client.connect((self.host, self.port))
        except:
            print("Не удалось подключиться к серверу")
            return

        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.daemon = True
        self.receive_thread.start()

        self.write_messages()

    def receive_messages(self):
        while True:
            try:
                message = self.client.recv(1024).decode('utf-8')
                if message == "NICK":
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                print("Произошла ошибка!")
                self.client.close()
                break

    def write_messages(self):
        print("Для выхода введите 'выход'")
        while True:
            message = input()
            if message.lower() == 'выход':
                self.client.close()
                break
            message = f"{self.nickname}: {message}"
            self.client.send(message.encode('utf-8'))


if __name__ == "__main__":
    client = ChatClient()
    client.connect()