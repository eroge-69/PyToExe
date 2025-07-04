import socket
import threading

PORT = 12345
connections = []

# Użytkownik podaje swój nick na start
nickname = input("Podaj swoją nazwę użytkownika: ")

def handle_client(conn, addr):
    try:
        peer_nick = conn.recv(1024).decode()
        print(f"[SERWER] {peer_nick} dołączył z {addr[0]}")

        connections.append((conn, peer_nick))

        while True:
            msg = conn.recv(1024).decode()
            if not msg:
                break
            print(f"[{peer_nick}]: {msg}")
    except:
        pass
    finally:
        conn.close()
        print(f"[SERWER] {peer_nick} rozłączony.")

def server_thread():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", PORT))
    server.listen()

    print("[SERWER] Czekam na połączenia...")

    while True:
        conn, addr = server.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def client_thread(sock, peer_nick):
    try:
        while True:
            msg = sock.recv(1024).decode()
            if not msg:
                break
            print(f"[{peer_nick}]: {msg}")
    except:
        pass
    finally:
        sock.close()
        print(f"[SERWER] {peer_nick} rozłączony.")

# === Główna logika ===

mode = input("Stwórz czat czy dołącz? (create / join [IP]): ").strip()

# Odpalamy serwer w tle zawsze
threading.Thread(target=server_thread, daemon=True).start()

if mode.startswith("join"):
    ip = mode.split(" ")[1]

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, PORT))
        sock.send(nickname.encode())  # Wyślij swój nick
        connections.append((sock, f"{ip}"))

        threading.Thread(target=client_thread, args=(sock, ip), daemon=True).start()
    except:
        print("[BŁĄD] Nie udało się połączyć.")

print(">> Możesz pisać wiadomości. Wciśnij Ctrl+C, by zakończyć.")

try:
    while True:
        msg = input()
        for conn, nick in connections:
            try:
                conn.send(msg.encode())
            except:
                continue
except KeyboardInterrupt:
    print("\nZamykam...")
    for conn, _ in connections:
        conn.close()
