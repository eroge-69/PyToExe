import socket

SERVER_ADDRESS = '192.168.1.6'
SERVER_PORT = 5000

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((SERVER_ADDRESS, SERVER_PORT))
    data = s.recv(1024)
    print('Received', repr(data))

input()
