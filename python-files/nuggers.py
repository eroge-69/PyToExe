import os
import time
import random
import string
import ctypes
import sys

# --- Ayarlar ---
BASE_DIR = "C:\\Users\\13ege"  # Kök dizin
LOG_FILE = os.path.join(BASE_DIR, "nugges_log.txt")
STARTUP_NAME = "NuggesStartup"  # Başlangıç dosyası adı

# --- Fonksiyonlar ---
def generate_random_name(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def log(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{time.ctime()} - {message}\n")

def rename_targets(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=False):
        for filename in filenames:
            if "clownfish" in filename.lower():
                old_path = os.path.join(dirpath, filename)
                new_name = generate_random_name() + os.path.splitext(filename)[1]
                new_path = os.path.join(dirpath, new_name)
                try:
                    os.rename(old_path, new_path)
                    log(f"Renamed file: {old_path} -> {new_path}")
                except Exception as e:
                    log(f"Failed to rename file: {old_path} - {e}")

        for dirname in dirnames:
            if "clownfish" in dirname.lower():
                old_path = os.path.join(dirpath, dirname)
                new_path = os.path.join(dirpath, generate_random_name())
                try:
                    os.rename(old_path, new_path)
                    log(f"Renamed folder: {old_path} -> {new_path}")
                except Exception as e:
                    log(f"Failed to rename folder: {old_path} - {e}")

def add_to_startup():
    startup_path = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    exe_path = os.path.abspath(sys.argv[0])
    bat_path = os.path.join(startup_path, f"{STARTUP_NAME}.bat")

    if not os.path.exists(bat_path):
        with open(bat_path, "w") as bat_file:
            bat_file.write(f'@echo off\nstart "" "{exe_path}"\n')
        log("Added to startup.")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# --- Ana Program ---
def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

    add_to_startup()
    log("Script started.")
    while True:
        rename_targets(BASE_DIR)
        time.sleep(120)  # Her 2 dakikada bir çalışır

if __name__ == "__main__":
    main()
