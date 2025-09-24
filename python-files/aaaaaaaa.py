import socket

UDP_IP = "26.87.220.120"  # например 78.29.92.92
UDP_PORT = 25536
MESSAGE = b"ping"

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(5)  # ждать ответ 5 секунд

try:
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024)
    print(f"Ответ от {addr}: {data}")
except socket.timeout:
    print("Ответ не получен — UDP блокируется или не проброшен")
