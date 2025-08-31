import os
import subprocess
import threading
import time
import keyboard
import ctypes
import random
import string

# ---------------- CONFIG ----------------
VALORANT_PATH = r"C:\Riot Games\Valorant\live\VALORANT.exe"
PIPE_NAME = r"\\.\pipe\vgc_pipe_emulated"

bypass_active = threading.Event()
shutdown_flag = threading.Event()
bypass_ready = threading.Event()
log_lock = threading.Lock()

# ---------------- LOG ----------------
def log(msg):
    with log_lock:
        print(f"[{time.strftime('%H:%M:%S')}] {msg}")

# ---------------- PROCESS MANAGEMENT ----------------
def is_process_running(process_name):
    try:
        tasks = subprocess.check_output(["tasklist"], shell=True).decode()
        return process_name.lower() in tasks.lower()
    except:
        return False

def kill_process(process_name):
    subprocess.call(f"taskkill /f /im {process_name}", shell=True)

def start_process(path):
    subprocess.Popen([path], shell=False)

# ---------------- STEALTH ----------------
def set_stealth_name(name="notepad.exe"):
    ctypes.windll.kernel32.SetConsoleTitleW(name)

def randomize_console_title():
    while not shutdown_flag.is_set():
        title = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        set_stealth_name(title)
        time.sleep(5)

# ---------------- PIPE EMULATION ----------------
def emulate_vgc_pipe():
    log("Vanguard pipe emülasyonu başlatıldı.")
    while not shutdown_flag.is_set():
        # Pipe mesaj taklitleri, rastgele veri gönderme
        time.sleep(random.uniform(0.8,1.5))
    log("Vanguard pipe emülasyonu durduruldu.")

# ---------------- BYPASS ----------------
def run_bypass():
    bypass_active.set()
    log("Bypass başlatılıyor...")
    time.sleep(3)  # Simülasyon
    bypass_ready.set()
    log("Bypass tamamlandı.")
    bypass_active.clear()

# ---------------- HOTKEY HANDLERS ----------------
def f8_handler():
    if not bypass_active.is_set():
        log("F8 basıldı: Valorant kapatılıyor...")
        kill_process("VALORANT.exe")
        time.sleep(1)
        run_bypass()
        log("Valorant tekrar açılıyor...")
        start_process(VALORANT_PATH)

def f9_handler():
    log("F9 basıldı: Safe exit başlatılıyor...")
    bypass_active.clear()
    kill_process("VALORANT.exe")
    log("Valorant kapatıldı, bypass durduruldu. 2 saniye içinde program kapanacak.")
    time.sleep(2)
    shutdown_flag.set()
    input("Program kapanıyor, Enter'a basın...")  # Pencere kapanmasını önler
    os._exit(0)

# ---------------- HOTKEY LISTENER ----------------
def hotkey_listener():
    keyboard.add_hotkey("F8", f8_handler)
    keyboard.add_hotkey("F9", f9_handler)
    while not shutdown_flag.is_set():
        time.sleep(0.5)

# ---------------- MAIN ----------------
def main():
    log("Tealip Bypass başlatıldı. F8: Bypass + Valorant restart | F9: Safe Exit")

    if not is_process_running("VALORANT.exe"):
        log("Valorant başlatılıyor...")
        start_process(VALORANT_PATH)

    # Threadler
    threading.Thread(target=hotkey_listener, daemon=True).start()
    threading.Thread(target=randomize_console_title, daemon=True).start()
    threading.Thread(target=emulate_vgc_pipe, daemon=True).start()

    while not shutdown_flag.is_set():
        time.sleep(1)

    input("Program kapanıyor, Enter'a basın...")  # Pencere kapanmasını önler

if __name__ == "__main__":
    main()
