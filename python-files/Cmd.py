import socket

HOST = '127.0.0.1'  # IP сервера — замени на внешний IP при подключении из другой сети
PORT = 4444

try:
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    response = client.recv(1024).decode("utf-8", errors="ignore")
    print(response)

    client.close()

except Exception as e:
    print("Ошибка подключения:", e)
