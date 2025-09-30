import socket
import os
import tqdm

def send_file(host, port, file_path):
    file_size = os.path.getsize(file_path)
    filename = os.path.basename(file_path)

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Подключаемся к {host}:{port}...")
        client_socket.connect((host, port))
        print("Подключение установлено!")

        file_info = f"{filename}|{file_size}"
        client_socket.send(file_info.encode())

        client_socket.recv(1024)

        progress = tqdm.tqdm(range(file_size), f"Отправка {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        with open(file_path, "rb") as file:
            while True:
                bytes_read = file.read(4096)
                if not bytes_read:
                    break
                client_socket.sendall(bytes_read)
                progress.update(len(bytes_read))

        print("Файл успешно отправлен!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client_socket.close()

def receive_file(port, save_directory="received_files"):
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)

    print(f"Сервер запущен на порту {port}. Ожидание подключения...")

    client_socket, address = server_socket.accept()
    print(f"Подключение от {address}")

    try:
        file_info = client_socket.recv(1024).decode()
        filename, file_size = file_info.split("|")
        file_size = int(file_size)

        client_socket.send(b"OK")

        file_path = os.path.join(save_directory, filename)
        progress = tqdm.tqdm(range(file_size), f"Получение {filename}", unit="B", unit_scale=True, unit_divisor=1024)

        with open(file_path, "wb") as file:
            bytes_received = 0
            while bytes_received < file_size:
                bytes_read = client_socket.recv(4096)
                if not bytes_read:
                    break
                file.write(bytes_read)
                bytes_received += len(bytes_read)
                progress.update(len(bytes_read))

        print(f"Файл {filename} успешно получен и сохранен!")

    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client_socket.close()
        server_socket.close()

if __name__ == "__main__":
    a=input("Получить файл(d)/Отправить файл(u)\n")
    if a=='d' or a=='в':
        PORT = 5001
        receive_file(PORT)
        print(True)
    elif a=='u' or a=='г':
        HOST = input('Введите ip получателя\n')
        PORT = 5001
        FILE_PATH = input('Введите полный путь файла\n')
        send_file(HOST, PORT, FILE_PATH)
        print(True)