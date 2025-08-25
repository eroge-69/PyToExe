import socket
import threading
import json
import netifaces
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from base64 import b64encode, b64decode

class ChatServer:
    def __init__(self, port=5000):
        self.port = port
        self.clients = {}  # {username: (ip, port, socket, groups)}
        self.groups = {}   # {group_name: [usernames]}
        self.key = get_random_bytes(32)  # AES-256 key
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('', self.port))
        self.sock.listen(5)
        print(f"Server started on {self.get_lan_ip()}:{port}")
        print(f"Encryption Key (share securely): {b64encode(self.key).decode()}")
    
    def get_lan_ip(self):
        for iface in netifaces.interfaces():
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    if '192.168' in addr['addr'] or '10.0' in addr['addr']:
                        return addr['addr']
        return socket.gethostbyname(socket.gethostname())
    
    def broadcast(self, message, exclude=None):
        for user, (ip, port, sock, _) in self.clients.items():
            if user != exclude:
                try:
                    sock.send(json.dumps(message).encode())
                except:
                    del self.clients[user]
    
    def handle_client(self, client_socket, addr):
        try:
            # Handshake: send encryption key
            client_socket.send(b64encode(self.key))
            
            # Wait for registration
            data = client_socket.recv(1024).decode()
            reg = json.loads(data)
            username = reg['username']
            file_port = reg['file_port']
            
            # Register client
            self.clients[username] = (addr[0], file_port, client_socket, [])
            print(f"{username} connected from {addr[0]}")
            
            # Send current user list
            client_socket.send(json.dumps({
                'type': 'USERS',
                'users': list(self.clients.keys())
            }).encode())
            
            # Main loop
            while True:
                data = client_socket.recv(4096)
                if not  break
                
                # Decrypt and parse message
                nonce = data[:16]
                cipher = AES.new(self.key, AES.MODE_CTR, nonce=nonce)
                msg = json.loads(cipher.decrypt(data[16:]).decode())
                
                if msg['type'] == 'MSG':
                    self.broadcast({
                        'type': 'MSG',
                        'from': username,
                        'to': msg['to'],
                        'content': msg['content'],
                        'is_group': msg.get('is_group', False)
                    }, exclude=username)
                
                elif msg['type'] == 'CREATE_GROUP':
                    group_name = msg['group']
                    self.groups[group_name] = [username]
                    client_socket.send(json.dumps({
                        'type': 'GROUP_CREATED',
                        'group': group_name
                    }).encode())
                
                elif msg['type'] == 'JOIN_GROUP':
                    group_name = msg['group']
                    if group_name in self.groups:
                        self.groups[group_name].append(username)
                        self.broadcast({
                            'type': 'GROUP_UPDATE',
                            'group': group_name,
                            'users': self.groups[group_name]
                        })
        
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if username in self.clients:
                del self.clients[username]
                self.broadcast({'type': 'USER_LEFT', 'user': username})
            client_socket.close()

    def start(self):
        while True:
            client, addr = self.sock.accept()
            threading.Thread(target=self.handle_client, args=(client, addr), daemon=True).start()

if __name__ == "__main__":
    ChatServer().start()