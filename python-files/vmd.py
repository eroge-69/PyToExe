import socket

HOST = '0.0.0.0'
PORT = 1557

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Listening on port {PORT} as vmd.exe...")
    while True:
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            conn.sendall(b'Hello from vmd.exe!\n')