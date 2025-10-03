import socket
import threading

IP = "192.168.0.32"
PORTS = [49081, 49082]  # multiple ports

def handle_client(conn, addr):
    print(f"[{addr}] connected; holding open")
    try:
        while True:
            # Optionally you can recv (but not required)
            data = conn.recv(1024)
            if not data:
                break
    except Exception as e:
        print("client handler error:", e)
    finally:
        conn.close()
        print(f"[{addr}] disconnected")

def listen_on_port(port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((IP, port))
    srv.listen(5)
    print(f"Listening on {IP}:{port}")
    while True:
        conn, addr = srv.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()

if __name__ == "__main__":
    threads = []
    for p in PORTS:
        t = threading.Thread(target=listen_on_port, args=(p,), daemon=True)
        t.start()
        threads.append(t)
    # keep main thread alive
    print("Servers running. Press Ctrl+C to exit.")
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("Shutting down.")