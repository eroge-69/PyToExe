import socket
import threading  # Добавляем импорт для threading

# Хост и порт сервера
HOST = 'd11.aurorix.net'  # Заменить на IP или домен сервера
PORT = 25292

# Функция для обработки получения сообщений
def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message, end='')  # Печатаем сообщение от сервера
        except:
            print("Ошибка при получении сообщения.")
            break

# Функция для отправки сообщений
def send_message(client_socket):
    while True:
        message = input()  # Вводим сообщение
        client_socket.send(message.encode())  # Отправляем сообщение на сервер

# Основная функция клиента
def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))  # Подключение к серверу

    # Запрос ника
    nickname = input("Введите ваш ник: ")
    client_socket.send(nickname.encode())  # Отправляем ник серверу

    # Запускаем два потока: один для получения сообщений, другой для отправки
    print("Подключение установлено. Вы можете начать чат!")
    threading.Thread(target=receive_messages, args=(client_socket,)).start()
    send_message(client_socket)

if __name__ == "__main__":
    start_client()
