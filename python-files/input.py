import socket
 
client = socket.socket()            # создаем сокет клиента
hostname = socket.gethostname()     # получаем хост локальной машины
port = 26262                    # устанавливаем порт сервера
client.connect((hostname, port))    # подключаемся к серверу
 
print("receiving data from server")
while True:
    data = client.recv(1024)    # получаем данные от сервера
    print(bytes.decode(data))
    if not data: break
 
client.close()