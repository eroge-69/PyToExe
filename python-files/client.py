import socket

HOST = input("Введите ip адрес сервера: ") #'127.0.0.1'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        cmd = input("Введите команду ('exit' для выхода): ")
        if cmd.lower() == 'exit':
            break
        s.sendall(cmd.encode())
        data = s.recv(1024)
        print('Ответ сервера:', data.decode())
