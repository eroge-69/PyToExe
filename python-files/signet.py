import os
import sys
import socket
import threading
import subprocess
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import struct

class SignNetSecure:
    def __init__(self):
        self.tor_process = None
        self.aes_key = b'12345678901234567890123456789012'  # 32 byte
        self.aes_iv = b'1234567890123456'  # 16 byte
        self.server_socket = None
        self.client_socket = None
        self.send_lock = threading.Lock()
        
    def on_process_exit(self):
        if self.tor_process and self.tor_process.poll() is None:
            self.tor_process.terminate()
            try:
                self.tor_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tor_process.kill()
        
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()

    def generate_own_id(self, port=9050):
        try:
            if not os.path.exists("tor"):
                print("'tor' folder not found!")
                return None

            self.tor_process = subprocess.Popen(
                ["tor\\tor.exe", "-f", "tor\\torrc"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for _ in range(20):
                if self.is_port_open("127.0.0.1", port):
                    break
                threading.Event().wait(1)

            hs_file = "tor\\hiddenservice\\hostname"
            for _ in range(10):
                if os.path.exists(hs_file):
                    with open(hs_file, 'r') as f:
                        return f.read().strip()
                threading.Event().wait(1)

            return None
        except Exception as ex:
            print(f"Hata: {ex}")
            return None

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('0.0.0.0', 1212))
            self.server_socket.listen(1)
            print("Server started. Waiting for connection...")

            self.client_socket, _ = self.server_socket.accept()
            print("Connection established!")

            receive_thread = threading.Thread(target=self.receive_loop, args=(self.client_socket,))
            receive_thread.daemon = True
            receive_thread.start()

            while True:
                msg = input()
                if msg.lower() == "exit":
                    break

                with self.send_lock:
                    encrypted = self.encrypt_aes(msg.encode('utf-8'))
                    self.client_socket.sendall(struct.pack('!I', len(encrypted)))
                    self.client_socket.sendall(encrypted)

        except Exception as ex:
            print(f"Server error: {ex}")
        finally:
            self.on_process_exit()

    def connect_to_onion(self, onion):
        try:
            if not onion.endswith(".onion"):
                onion += ".onion"

            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('127.0.0.1', 9050))

            # SOCKS5 bağlantısı
            self.client_socket.sendall(bytes([5, 1, 0]))
            response = self.client_socket.recv(2)

            connect_request = bytearray()
            connect_request.append(5)  # VER
            connect_request.append(1)  # CONNECT
            connect_request.append(0)  # RSV
            connect_request.append(3)  # ATYP (DOMAINNAME)
            connect_request.append(len(onion))
            connect_request.extend(onion.encode('ascii'))
            connect_request.extend([1212 >> 8, 1212 & 0xff])

            self.client_socket.sendall(connect_request)
            self.client_socket.recv(10)  # Yanıtı bekle

            print("The connection is established! You can start messaging.")

            receive_thread = threading.Thread(target=self.receive_loop, args=(self.client_socket,))
            receive_thread.daemon = True
            receive_thread.start()

            while True:
                msg = input()
                if msg.lower() == "exit":
                    break

                with self.send_lock:
                    encrypted = self.encrypt_aes(msg.encode('utf-8'))
                    self.client_socket.sendall(struct.pack('!I', len(encrypted)))
                    self.client_socket.sendall(encrypted)

        except Exception as ex:
            print(f"Client Error: {ex}")
        finally:
            self.on_process_exit()

    def receive_loop(self, sock):
        try:
            while True:
                length_bytes = sock.recv(4)
                if len(length_bytes) != 4:
                    break

                length = struct.unpack('!I', length_bytes)[0]
                data = bytearray()
                while len(data) < length:
                    chunk = sock.recv(length - len(data))
                    if not chunk:
                        raise Exception("Connection down")
                    data.extend(chunk)

                decrypted = self.decrypt_aes(bytes(data))
                print("Recieved:", decrypted.decode('utf-8'))

        except Exception as ex:
            print(f"Receiver error: {ex}")

    def encrypt_aes(self, plaintext):
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(self.aes_iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(plaintext) + padder.finalize()
        return encryptor.update(padded_data) + encryptor.finalize()

    def decrypt_aes(self, ciphertext):
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CBC(self.aes_iv),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        unpadder = padding.PKCS7(128).unpadder()
        padded_data = decryptor.update(ciphertext) + decryptor.finalize()
        return unpadder.update(padded_data) + unpadder.finalize()

    def is_port_open(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                s.connect((host, port))
                return True
        except:
            return False

if __name__ == "__main__":
    from cryptography.hazmat.primitives import padding
    
    app = SignNetSecure()
    
    print("1. Generate your own ID (onion address)")
    print("2. Connect to another ID")
    choice = input("Your choose (1 or 2): ")

    if choice == "1":
        onion = app.generate_own_id()
        if onion:
            print(f"ID'niz: {onion}")
            app.start_server()
    elif choice == "2":
        target = input("Bağlanılacak onion adresi: ").strip()
        app.connect_to_onion(target)
    else:
        print("Geçersiz seçim.")