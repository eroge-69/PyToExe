import socket
import sys

def calibrate_gap(ip, port=9100, width=100, height=150, gap=3):
    commands = (
        f"SIZE {width} mm, {height} mm\r\n"
        f"GAP {gap} mm, 0 mm\r\n"
        "DIRECTION 1\r\n"
        "SET TEAR ON\r\n"
        "CLS\r\n"
        "AUTOSET\r\n"
    )
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, port))
        sock.sendall(commands.encode("ascii"))
        sock.close()
        print(f"[OK] Калибровка (GAP) отправлена на {ip}:{port}")
    except Exception as e:
        print(f"[ERR] Ошибка: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: tsc_calibrate_gap.py <IP> [PORT] [WIDTH] [HEIGHT] [GAP]")
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 9100
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 100
    height = int(sys.argv[4]) if len(sys.argv) > 4 else 150
    gap = int(sys.argv[5]) if len(sys.argv) > 5 else 3
    calibrate_gap(ip, port, width, height, gap)

