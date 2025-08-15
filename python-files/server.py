import socket
import struct
import time
import random

ADDRESS = "0.0.0.0"
PORT = 502

# Buat socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((ADDRESS, PORT))
sock.listen(5)

print(f"Modbus TCP server started at {ADDRESS}:{PORT}")

clients = []
channels = [0] * 8
last_update = 0

while True:
    # Terima koneksi baru
    try:
        sock.settimeout(0.2)
        conn, addr = sock.accept()
        clients.append(conn)
        # print(f"Client connected: {addr}")
    except socket.timeout:
        pass

    # Baca data dari client
    for conn in clients[:]:
        try:
            conn.settimeout(0.01)
            data = conn.recv(1024)
            if not data:
                clients.remove(conn)
                conn.close()
                continue

            # Ambil header Modbus
            transaction_id = data[0:2]
            protocol_id = data[2:4]
            unit_id = data[6:7]
            function_code = data[7:8]

            # Function code 3 = Read Holding Registers
            if function_code == b'\x03':
                byte_count = len(channels) * 2
                payload = struct.pack("B", byte_count)
                for val in channels:
                    payload += struct.pack(">H", val)

                pdu = function_code + payload
                mbap = transaction_id + protocol_id + struct.pack(">H", len(pdu) + 1) + unit_id
                conn.sendall(mbap + pdu)

        except socket.timeout:
            pass
        except Exception:
            clients.remove(conn)
            conn.close()

    # Update nilai setiap 1 detik
    if int(time.time()) != last_update:
        for i in range(8):
            channels[i] = random.randint(13107, 65535)

        print(time.strftime("%H:%M:%S") + " → " + ", ".join([f"Ch{i}={v}" for i, v in enumerate(channels)]))
        last_update = int(time.time())
