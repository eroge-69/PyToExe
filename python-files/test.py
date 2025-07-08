import socket
import time

variable = 0

try:
    # Создаем серверный сокет
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', 64500))
    server_sock.listen(10)
    print('Server is running on port 64500, press Ctrl+C to stop')

    while True:
        variable += 1
        print(f"Текущая переменная: {variable}")

        # Устанавливаем таймаут для accept, чтобы не блокировать цикл
        server_sock.settimeout(1.0)

        try:
            conn, addr = server_sock.accept()
            print('Connected:', addr)

            try:
                data = conn.recv(1024)
                if data:
                    print("Received:", data)

                    # Создаем КЛИЕНТСКИЙ сокет для пересылки данных
                    forward_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    try:
                        forward_sock.connect(('127.0.0.1', 8001))  # Подключаемся к целевому серверу
                        forward_sock.send(data)  # Пересылаем данные
                        print("Data forwarded to 127.0.0.1:64501")
                    except ConnectionRefusedError:
                        print("Target server (64501) is not available")
                    finally:
                        forward_sock.close()

                    # Отправляем ответ клиенту
                    conn.send(data.upper())
            finally:
                conn.close()

        except socket.timeout:
            continue  # Нет новых подключений - продолжаем цикл

        time.sleep(1)

except KeyboardInterrupt:
    print("Server stopped")
finally:
    server_sock.close()
