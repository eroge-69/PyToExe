import socket
import threading
import sys

# === Цветове ===
RED = "\033[91m"
BLACK_BG = "\033[40m"
RESET = "\033[0m"

HOST = input("Въведи IP на сървъра: ")
PORT = 12345

def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode('utf-8')
            print(f"{RED}{BLACK_BG}{message}{RESET}")
        except:
            print("Връзката е прекъсната.")
            sock.close()
            break

def send_messages(sock):
    while True:
        try:
            message = input()
            sock.send(message.encode('utf-8'))
        except:
            break

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((HOST, PORT))
    except:
        print("Не може да се свърже със сървъра.")
        sys.exit()

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    send_messages(sock)

if __name__ == "__main__":
    start_client()
