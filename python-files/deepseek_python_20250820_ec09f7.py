import socket

HOST = '0.0.0.0'  # Nasłuchuj na wszystkich interfejsach
PORT = 9999

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    print(f"Nasłuchiwanie na porcie {PORT}...")
    while True:
        conn, addr = s.accept()
        conn.close()  # Zamknij połączenie natychmiast