import socket
import threading
import sys

def scan(ip, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, port))
        if result == 0:
            print(f"[+] Port {port} is OPEN")
        sock.close()
    except:
        pass

def main():
    print("== Simple Port Scanner ==")
    if len(sys.argv) < 3:
        print("Usage: port_scanner.exe <target_ip> <start_port>-<end_port>")
        print("Example: port_scanner.exe 192.168.1.1 20-100")
        sys.exit(1)

    target_ip = sys.argv[1]
    try:
        port_range = sys.argv[2].split('-')
        start_port = int(port_range[0])
        end_port = int(port_range[1])
    except:
        print("[!] Invalid port range format. Use <start>-<end>.")
        sys.exit(1)

    threads = []

    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan, args=(target_ip, port))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("[*] Scan complete.")

if __name__ == "__main__":
    main()

