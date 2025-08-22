import socket
import threading

HOST = '127.0.0.1'
PORT = 12345

clients = []

def handle_client(client_socket, addr):
    try:
        nickname = client_socket.recv(1024).decode('utf-8')
        welcome_msg = f"{nickname} prisoedinilsa k chatu."
        broadcast(welcome_msg)
        while True:
            msg = client_socket.recv(1024)
            if not msg:
                break
            message = f"{nickname}: {msg.decode('utf-8')}"
            broadcast(message)
    except:
        pass
    finally:
        clients.remove(client_socket)
        client_socket.close()
        leave_msg = f"{nickname} pokinul chat."
        broadcast(leave_msg)

def broadcast(message):
    for client in clients:
        try:
            client.send(message.encode('utf-8'))
        except:
            pass

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"server zapuhen na {HOST}:{PORT}")
    while True:
        client_socket, addr = server.accept()
        clients.append(client_socket)
        threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True).start()