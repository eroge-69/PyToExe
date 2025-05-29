import socket
import os
import threading
import sys
import select

SERVER_IP = '127.0.0.1'
SERVER_PORT = 1312

console_lock = threading.Lock()

def receive_messages(sock):
    while True:
        try:
            ready = select.select([sock], [], [], 0.1)
            if ready[0]:
                data = sock.recv(4096)
                if not data:
                    break
                with console_lock:
                    print("\r" + data.decode(), end='')
                    print("\n" + username + ": ", end='', flush=True)
        except:
            break

def input_loop():
    while True:
        with console_lock:
            print(username + ": " , end='', flush=True)
        try:
            line = sys.stdin.readline()
        except:
            break
        if not line:
            continue
        cmd = line.strip()
        sock.sendall((cmd + "\n").encode())
        if cmd.lower() == "exit":
            break

def main():
    os.system("cls" if os.name == "nt" else "clear")
    global username, sock
    try:
        print("Connecting to the server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))
        sock.send(b"AphCrypt-1.0\n")
        print("Connected to the server successfully!\n")

        prompt = sock.recv(1024).decode()
        if prompt.strip().startswith("Username"):
            username = input("Enter username: ").strip()
            sock.sendall((username + "\n").encode())

        prompt = sock.recv(1024).decode()
        if prompt.strip().startswith("Password"):
            password = input("Enter password: ").strip()
            sock.sendall((password + "\n").encode())

        response = sock.recv(1024).decode()
        print(response)
        if "failed" in response.lower() or "disconnecting" in response.lower():
            print("Authentication failed. Exiting.")
            return

        threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
        input_loop()
    except ConnectionRefusedError:
        print("Could not connect to the server. Is it running?")
    except Exception as e:
        print("An error occurred:", e)
    finally:
        sock.close()
        print("\nGoodbye!")
        os.system("cls" if os.name == "nt" else "clear")

if __name__ == "__main__":
    main()