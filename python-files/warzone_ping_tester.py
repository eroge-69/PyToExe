
import socket
import time

servers = {
    "EU - Frankfurt": "3.120.132.69",
    "EU - Ireland": "52.19.127.110",
    "Asia - Singapore": "13.250.126.185",
    "US - East (Virginia)": "3.225.59.253",
    "US - West (California)": "13.57.139.110",
    "Middle East - Bahrain": "157.175.1.1",
    "Middle East - Oman": "5.37.48.1"
}

ports = [3074, 443]

def test_tcp_ping(ip, port, timeout=2):
    try:
        start = time.time()
        sock = socket.create_connection((ip, port), timeout=timeout)
        sock.close()
        end = time.time()
        return round((end - start) * 1000)
    except:
        return None

print("Testing Warzone Server Connectivity...\n")
for name, ip in servers.items():
    print(f"== {name} ({ip}) ==")
    for port in ports:
        result = test_tcp_ping(ip, port)
        if result is not None:
            print(f"  Port {port}: ✅ {result} ms")
        else:
            print(f"  Port {port}: ❌ No response")
    print()
input("Press Enter to exit...")
