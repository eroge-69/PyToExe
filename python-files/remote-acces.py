import socket
import os

HOST = '0.0.0.0'  # Luistert op alle netwerkinterfaces
PORT = 65432
PASSWORD = 'password'  # Verander dit!

def handle_command(command):
    if command == 'shutdown':
        os.system('shutdown /s /t 1')  # Windows
    elif command == 'restart':
        os.system('shutdown /r /t 1')  # Windows
    else:
        print("Onbekende opdracht:", command)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Luistert op poort {PORT}...")

    while True:
        conn, addr = s.accept()
        with conn:
            print(f"Verbonden met {addr}")
            data = conn.recv(1024).decode()
            if not data:
                continue
            try:
                received_password, command = data.split(':')
                if received_password == PASSWORD:
                    handle_command(command.strip())
                    conn.sendall(b'Opdracht uitgevoerd.')
                else:
                    conn.sendall(b'Ongeldig wachtwoord.')
            except Exception as e:
                conn.sendall(f'Fout: {e}'.encode())
