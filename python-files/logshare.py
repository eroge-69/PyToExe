#!/usr/bin/env python3
import sys
import socket
import argparse
import threading

clients = []

def handle_client(conn, addr):
    global clients
    print(f"[SERVER] Client connected: {addr}")
    try:
        while True:
            data = conn.recv(1)  # Keep-alive read (not actually used)
            if not data:
                break
    except:
        pass
    finally:
        print(f"[SERVER] Client disconnected: {addr}")
        clients = [c for c in clients if c != conn]
        conn.close()

def run_server(port):
    global clients
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", port))
    sock.listen(5)
    print(f"[SERVER] Listening on 0.0.0.0:{port}")

    def accept_clients():
        while True:
            conn, addr = sock.accept()
            clients.append(conn)
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    threading.Thread(target=accept_clients, daemon=True).start()

    try:
        for line in sys.stdin:
            # Show on server's own stdout
            sys.stdout.write(line)
            sys.stdout.flush()

            # Send to all clients
            for conn in clients[:]:
                try:
                    conn.sendall(line.encode('utf-8'))
                except:
                    clients.remove(conn)
                    conn.close()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

def run_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(f"[CLIENT] Connected to {host}:{port}")
    try:
        while True:
            data = sock.recv(4096)
            if not data:
                break
            sys.stdout.write(data.decode('utf-8'))
            sys.stdout.flush()
    except KeyboardInterrupt:
        pass
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stream logs over TCP.")
    parser.add_argument("mode", choices=["server", "client"], help="Run as server or client")
    parser.add_argument("host_or_port", help="Port (server) or Host (client)")
    parser.add_argument("port", nargs="?", type=int, help="Port (client only)")
    args = parser.parse_args()

    if args.mode == "server":
        port = int(args.host_or_port)
        run_server(port)
    else:
        host = args.host_or_port
        port = args.port
        if not port:
            print("Error: Client mode requires host and port.")
            sys.exit(1)
        run_client(host, port)
