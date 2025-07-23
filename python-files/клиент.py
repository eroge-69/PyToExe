import socket
import threading
import time  # Для задержки при переподключении

# Конфигурация клиента
HOST = '192.168.31.31'  # IP-адрес сервера # IP-адрес сервера (по умолчанию localhost)
PORT = 12345  # Порт сервера

connected = True  # Флаг для контроля подключения

def receive_messages(client_socket):
    """Получает сообщения от сервера и выводит их."""
    global connected
    try:
        while connected:  # Проверяем флаг подключения
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break  # Сервер закрыл соединение
                print(message)  # Выводим полученное сообщение
            except socket.error as e:
                print(f"Ошибка при получении сообщений: {e}")
                break  # Выходим из цикла при ошибке сокета
    except Exception as e:
        print(f"Непредвиденная ошибка при получении сообщений: {e}")
    finally:
        print("Поток приема сообщений завершен.")
        connected = False
        try:
            client_socket.close() # закрываем сокет тут
        except:
            pass


def send_messages(client_socket):
    """Отправляет сообщения на сервер."""
    global connected
    try:
        while connected:  # Проверяем флаг подключения
            message = input()
            try:
                client_socket.send(message.encode('utf-8'))
            except socket.error as e:
                print(f"Ошибка при отправке сообщений: {e}")
                break  # Выходим из цикла при ошибке сокета
    except Exception as e:
        print(f"Непредвиденная ошибка при отправке сообщений: {e}")
    finally:
        print("Поток отправки сообщений завершен.")
        connected = False
        try:
             client_socket.close() # закрываем сокет тут
        except:
            pass

def start_client():
    """Запускает клиент."""
    global connected
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"Подключено к серверу {HOST}:{PORT}")
        connected = True

        # Запускаем потоки для получения и отправки сообщений
        receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
        send_thread = threading.Thread(target=send_messages, args=(client_socket,))

        receive_thread.start()
        send_thread.start()

        receive_thread.join() # Ожидаем завершения потоков, чтобы корректно закрыть сокет
        send_thread.join()

    except socket.error as e:
        print(f"Ошибка подключения к серверу: {e}")
    except KeyboardInterrupt:
        print("\nКлиент остановлен.")
    finally:
        print("Клиент завершен.")
        connected = False
        try:
             client_socket.close()  # закрываем сокет тут
        except:
            pass


if __name__ == "__main__":
    start_client()
