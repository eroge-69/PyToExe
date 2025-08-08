import socket
import struct
import datetime
import os
import select

# Settings
UDP_PORTS = [7785, 7786]  # Add or modify ports here
PACKET_SIZE = 250
FLOAT_SIZE = 4
EXPECTED_BYTES = PACKET_SIZE * FLOAT_SIZE  # 1000 bytes

# Create UDP sockets and bind
sockets = []
files = {}
print("Setting up sockets:")
for port in UDP_PORTS:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", port))
    sock.setblocking(0)
    sockets.append(sock)

    # File name: UDP_Data_YYYY-MM-DD_HH-MM-SS_PORT.csv
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"UDP_Data_{timestamp}_{port}.csv"

    file = open(filename, "a")
    file.write("timestamp," + ",".join([f"val{i}" for i in range(PACKET_SIZE)]) + "\n")
    files[port] = file

    print(f"  Listening on port {port}, saving to {filename}")

print("\nPress Ctrl+C to stop.\n")

try:
    while True:
        # Wait for readable sockets
        readable, _, _ = select.select(sockets, [], [], 1.0)

        for sock in readable:
            try:
                data, addr = sock.recvfrom(8192)
                port = sock.getsockname()[1]

                if len(data) != EXPECTED_BYTES:
                    print(f"[{port}] Unexpected packet size: {len(data)} bytes from {addr}, skipping...")
                    continue

                magnitudes = struct.unpack('<250f', data)
                host_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                line = f"{host_timestamp}," + ",".join(f"{v:.6f}" for v in magnitudes) + "\n"
                files[port].write(line)
                files[port].flush()

                print(f"[{port}] {host_timestamp} - From {addr}, preview: {magnitudes[:3]}")

            except struct.error as e:
                print(f"[{port}] Struct unpacking error:", e)

except KeyboardInterrupt:
    print("\nShutting down...")

finally:
    for file in files.values():
        file.close()
    for sock in sockets:
        sock.close()
    print("All files and sockets closed.")
