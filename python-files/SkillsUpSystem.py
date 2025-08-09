import socket

host = "192.168.1.6"
port = 4444

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

try:
    while True:
        message = input()
        if message.lower() in ["exit", "quit"]:
            break
        client.send((message + "\n").encode())
except:
    pass
finally:
    client.close()
