import socket
import threading

clients = []

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            # Diffuse le message à tous les clients sauf l'envoyeur
            for c in clients:
                if c != client_socket:
                    c.send(message)
        except:
            break
    clients.remove(client_socket)
    client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 12345))  # écoute sur le port 12345
    server.listen()
    print("Serveur lancé, en attente de connexions...")

    while True:
        client_socket, addr = server.accept()
        print(f"Connexion de {addr}")
        clients.append(client_socket)
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()

if __name__ == "__main__":
    main()
