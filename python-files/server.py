import socket
import threading

HOST = '0.0.0.0'
PORT = 5000

def handle_client(conn, addr):
    print(f"[+] New connection from {addr}")
    try:
        while True:
            data = conn.recv(272)
            if not data:
                break
            main_data = data[:271]
            char = data[271:272].decode('utf-8', errors='ignore')
            print(f"[{addr}] Received 271 bytes: {main_data[:20]}... and char: '{char}'")
    except Exception as e:
        print(f"[!] Error with {addr}: {e}")
    finally:
        print(f"[-] Connection closed from {addr}")
        conn.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(2)
    print(f"[+] Server listening on {HOST}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()
