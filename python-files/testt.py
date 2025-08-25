# server_increment.py

import socket

HOST = '0.0.0.0'  # Tüm ağ arayüzlerinden dinle
PORT = 12345      # Port numarası

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"Sunucu {PORT} portunda dinleniyor...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Bağlantı: {addr}")
                data = conn.recv(1024)
                try:
                    number = int(data.decode())
                    result = number + 1
                    conn.sendall(str(result).encode())
                except ValueError:
                    conn.sendall(b"Hata: Gecerli bir sayi gonderin.")

if __name__ == "__main__":
    start_server()
