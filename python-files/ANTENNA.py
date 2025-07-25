import serial
import socket
import threading
import serial.tools.list_ports

# --- Конфигурация ---
BAUD_RATE = 9600
TEXT_FILE = 'output.txt'
TCP_HOST = '192.168.0.36'
TCP_PORT = 5000
DEVICE_NAME_KEYWORD = 'CH340'

# --- Глобальные ---
clients = []
clients_lock = threading.Lock()

# --- Автоопределение порта ---
def find_ch340_port():
    ports = list(serial.tools.list_ports.comports())
    ch340_ports = [p.device for p in ports if DEVICE_NAME_KEYWORD in p.description.upper()]
    
    if not ch340_ports:
        raise RuntimeError(f"[ERROR] Устройство '{DEVICE_NAME_KEYWORD}' не найдено.")
    if len(ch340_ports) > 1:
        print(f"[WARNING] Найдено несколько '{DEVICE_NAME_KEYWORD}', используется: {ch340_ports[0]}")

    return ch340_ports[0]

# --- Передача данных всем клиентам ---
def broadcast_to_clients(data):
    with clients_lock:
        for client in clients[:]:
            try:
                client.sendall((data + '\n').encode('utf-8'))
            except:
                print(f"[TCP] Отключение клиента: {client.getpeername()}")
                clients.remove(client)
                client.close()

# --- Чтение из COM-порта ---
def read_from_serial(com_port):
    with serial.Serial(com_port, BAUD_RATE, timeout=1) as ser, open(TEXT_FILE, 'a') as file:
        print(f"[SERIAL] Подключено к {com_port} @ {BAUD_RATE}")
        while True:
            if ser.in_waiting:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"[DATA] {line}")
                    file.write(line + '\n')
                    file.flush()
                    broadcast_to_clients(line)

# --- Обработка клиента (держим соединение открытым) ---
def handle_client(conn, addr):
    print(f"[TCP] Клиент подключен: {addr}")
    with clients_lock:
        clients.append(conn)
    try:
        while True:
            # Просто держим соединение открытым, т.к. передача push-режимом
            data = conn.recv(1)
            if not data:
                break
    except:
        pass
    finally:
        with clients_lock:
            if conn in clients:
                clients.remove(conn)
        conn.close()
        print(f"[TCP] Клиент отключен: {addr}")

# --- TCP-сервер ---
def tcp_server():
    print(f"[TCP] Сервер слушает на {TCP_HOST}:{TCP_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((TCP_HOST, TCP_PORT))
        server_socket.listen()
        while True:
            conn, addr = server_socket.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# --- Запуск ---
if __name__ == '__main__':
    try:
        com_port = find_ch340_port()
    except RuntimeError as e:
        print(e)
        exit(1)

    serial_thread = threading.Thread(target=read_from_serial, args=(com_port,), daemon=True)
    tcp_thread = threading.Thread(target=tcp_server, daemon=True)

    serial_thread.start()
    tcp_thread.start()

    print("[MAIN] Программа запущена. Нажмите Ctrl+C для выхода.")
    serial_thread.join()
    tcp_thread.join()
в