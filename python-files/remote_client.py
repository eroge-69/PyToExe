# remote_client.py
# LAN only, auto-connect to technician GUI.
# WARNING: No user confirmation! Use only on your own machines in trusted LAN.

import socket, struct, json, threading, os, platform

SERVER_HOST = "192.168.0.112:8765"  # <-- Замените на IP вашей техники в LAN

def send_msg(conn, obj):
    b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    conn.sendall(struct.pack(">I", len(b)) + b)

def recv_msg(conn):
    hdr = conn.recv(4)
    if not hdr:
        return None
    L = struct.unpack(">I", hdr)[0]
    data = b""
    while len(data) < L:
        chunk = conn.recv(L - len(data))
        if not chunk:
            raise ConnectionError("connection closed")
        data += chunk
    return json.loads(data.decode("utf-8"))

def list_dir(path):
    entries = []
    try:
        if not path:
            if os.name == "nt":
                for drive_letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                    d = f"{drive_letter}:" + os.sep
                    if os.path.exists(d):
                        entries.append({"name": d, "is_dir": True, "size": 0})
            else:
                entries.append({"name": "/", "is_dir": True, "size": 0})
        else:
            with os.scandir(path) as it:
                for e in it:
                    try:
                        is_dir = e.is_dir(follow_symlinks=False)
                        size = e.stat(follow_symlinks=False).st_size if not is_dir else 0
                        entries.append({"name": e.name, "is_dir": is_dir, "size": size})
                    except PermissionError:
                        continue
    except Exception as ex:
        return {"error": str(ex)}
    entries.sort(key=lambda x: (not x["is_dir"], x["name"].lower()))
    return {"entries": entries}

def handle_conn_loop(conn):
    try:
        while True:
            msg = recv_msg(conn)
            if msg is None:
                break
            t = msg.get("type")
            if t == "auth":
                # автоподключение: сразу отправляем OK
                send_msg(conn, {"type":"auth_resp", "status":"ok"})
            elif t == "list":
                path = msg.get("path", "")
                result = list_dir(path)
                if "error" in result:
                    send_msg(conn, {"type":"error","msg": result["error"], "path": path})
                else:
                    send_msg(conn, {"type":"list_resp","path": path, "entries": result["entries"]})
            elif t == "get":
                path = msg.get("path")
                if not path or not os.path.isfile(path):
                    send_msg(conn, {"type":"error","msg":"file_not_found"})
                    continue
                size = os.path.getsize(path)
                name = os.path.basename(path)
                send_msg(conn, {"type":"file","name": name, "size": size})
                with open(path, "rb") as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        conn.sendall(chunk)
    except Exception as e:
        try:
            conn.close()
        except: pass

def run_client():
    if ":" not in SERVER_HOST:
        print("SERVER_HOST must be host:port")
        return
    host, port = SERVER_HOST.split(":")
    port = int(port)
    while True:
        try:
            sock = socket.create_connection((host, port), timeout=30)
            # автоподключение: сразу auth
            send_msg(sock, {"type":"auth","code":"LAN_AUTO"})
            handle_conn_loop(sock)
        except Exception:
            # переподключение каждые 5 секунд
            import time
            time.sleep(5)

if __name__ == "__main__":
    run_client()
