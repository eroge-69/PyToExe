#!/usr/bin/env python3
import socket
import threading
import signal
import sys
import time
import configparser
from contextlib import closing
try:
    import serial
except ImportError:
    print("Требуется pyserial: pip install pyserial")
    sys.exit(1)

_shutdown = threading.Event()


def load_config(filename="config.ini"):
    cfg = configparser.ConfigParser()
    if not cfg.read(filename, encoding="utf-8"):
        # если файла нет – создаём с шаблоном
        cfg["main"] = {
            "tcp_host": "0.0.0.0",
            "tcp_port": "5000",
        }
        cfg["serial"] = {
            "com": "COM3",
            "baud": "9600",
        }
        with open(filename, "w", encoding="utf-8") as f:
            cfg.write(f)
        print(f"[INFO] Создан шаблон {filename}, отредактируйте его и перезапустите.")
        sys.exit(0)
    return cfg


class TcpClients:
    def __init__(self):
        self._clients = set()
        self._lock = threading.Lock()

    def add(self, conn):
        with self._lock:
            self._clients.add(conn)

    def remove(self, conn):
        with self._lock:
            self._clients.discard(conn)

    def close_all(self):
        with self._lock:
            for c in list(self._clients):
                try:
                    c.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    c.close()
                except:
                    pass
            self._clients.clear()

    def broadcast(self, data):
        drops = []
        with self._lock:
            for c in self._clients:
                try:
                    c.sendall(data)
                except:
                    drops.append(c)
            for d in drops:
                try:
                    d.close()
                except:
                    pass
                self._clients.discard(d)


def handle_client(conn, addr, ser, clients):
    print(f"[TCP] Подключился {addr}")
    try:
        with conn:
            while not _shutdown.is_set():
                data = conn.recv(4096)
                if not data:
                    break
                ser.write(data)  # TCP → COM
    except Exception as e:
        print(f"[ERR] TCP->COM: {e}")
    finally:
        clients.remove(conn)
        print(f"[TCP] Отключился {addr}")


def com_reader(ser, clients):
    while not _shutdown.is_set():
        try:
            n = ser.in_waiting
            data = ser.read(n if n > 0 else 1)
            if data:
                clients.broadcast(data)  # COM → TCP
        except Exception as e:
            print(f"[ERR] COM->TCP: {e}")
            time.sleep(0.5)


def main():
    cfg = load_config("config.ini")

    tcp_host = cfg.get("main", "tcp_host", fallback="0.0.0.0")
    tcp_port = cfg.getint("main", "tcp_port", fallback=5000)

    com_port = cfg.get("serial", "com", fallback="COM3")
    baud = cfg.getint("serial", "baud", fallback=9600)

    def _sig(sig, frame):
        print("\n[SYS] Завершение...")
        _shutdown.set()
    signal.signal(signal.SIGINT, _sig)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, _sig)

    try:
        ser = serial.Serial(com_port, baud, timeout=0.05)
    except Exception as e:
        print(f"[FATAL] Не удалось открыть {com_port}: {e}")
        sys.exit(2)

    print(f"[OK] COM={com_port} @ {baud} | TCP={tcp_host}:{tcp_port}")

    clients = TcpClients()

    t_com = threading.Thread(target=com_reader, args=(ser, clients), daemon=True)
    t_com.start()

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((tcp_host, tcp_port))
        srv.listen(5)
        print("[OK] Ожидание TCP-клиентов...")

        while not _shutdown.is_set():
            try:
                srv.settimeout(0.5)
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            clients.add(conn)
            t = threading.Thread(target=handle_client, args=(conn, addr, ser, clients), daemon=True)
            t.start()

    clients.close_all()
    try:
        ser.close()
    except:
        pass
    print("[SYS] Выход.")


if __name__ == "__main__":
    main()
