import psutil
import time
import random
import threading
import pyfiglet
import os
import re
import atexit
import signal
import msvcrt
import sys

BTC_TO_USD = 67000
RAM_FILE = "ram_usage.txt"
LOCK_FILE = "miner.lock"

# List of country codes where BTC mining is forbidden (example)
FORBIDDEN_COUNTRIES = {"CN", "MA", "DZ", "BD", "EG", "IQ", "NE", "QA", "JO", "KW", "OM", "PK", "SA", "TN"}

try:
    import win32event
    import win32api
    import winerror
except ImportError:
    print("pywin32 is required. Install with: pip install pywin32")
    sys.exit(1)

mutex = win32event.CreateMutex(None, False, "BARKOD_BTC_SINGLE_INSTANCE")
last_error = win32api.GetLastError()

if last_error == winerror.ERROR_ALREADY_EXISTS:
    print("Another instance is already running.")
    sys.exit(1)

def rgb_gradient(start_rgb, end_rgb, steps):
    gradient = []
    for i in range(steps):
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * i / (steps - 1))
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * i / (steps - 1))
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * i / (steps - 1))
        gradient.append((r, g, b))
    return gradient

def ansi_color(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"

def print_gradient_banner(text):
    ascii_banner = pyfiglet.figlet_format(text)
    lines = ascii_banner.splitlines()
    max_len = max(len(line) for line in lines)
    start_rgb = (0, 102, 255)
    end_rgb = (204, 153, 255)
    gradient = rgb_gradient(start_rgb, end_rgb, max_len)
    for line in lines:
        output = ""
        for i, char in enumerate(line.ljust(max_len)):
            r, g, b = gradient[i]
            output += ansi_color(r, g, b) + char
        output += "\033[0m"
        print(output)

def get_max_ram_gb():
    total_ram = psutil.virtual_memory().total // (1024 ** 3)
    return total_ram // 2 if total_ram > 1 else 1

def read_used_ram():
    if not os.path.exists(RAM_FILE):
        return 0
    try:
        with open(RAM_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0

def write_used_ram(used):
    with open(RAM_FILE, "w") as f:
        f.write(str(used))

def iban_checksum(iban):
    # Move first 4 chars to end, convert letters to numbers, mod 97 == 1
    iban = iban.replace(' ', '').upper()
    if not re.match(r'^[A-Z0-9]+$', iban):
        return False
    rearranged = iban[4:] + iban[:4]
    digits = ''
    for ch in rearranged:
        if ch.isdigit():
            digits += ch
        else:
            digits += str(ord(ch) - 55)
    try:
        return int(digits) % 97 == 1
    except Exception:
        return False

def get_country_from_iban(iban):
    iban = iban.replace(' ', '').upper()
    return iban[:2]

class FakeMiner:
    def __init__(self):
        self.btc_income = 0.0
        self.running = False
        self.thread = None
        self.ram_gb = 0
        self.btc_per_second = 0.0

    def mine(self):
        while self.running:
            self.btc_income += self.btc_per_second
            usd_income = self.btc_income * BTC_TO_USD
            print(f"\rIncome: {self.btc_income:.8f} BTC | ${usd_income:,.2f} USD", end='')
            time.sleep(1)

    def start(self, ram_gb):
        if not self.running:
            print("\033[92mMining started! (This is FAKE, for fun only!)\033[0m")
            self.running = True
            self.ram_gb = ram_gb
            # 10GB = 0.000018 BTC/24H
            self.btc_per_second = (ram_gb / 10) * (0.000018 / 86400)
            used_ram = read_used_ram()
            write_used_ram(used_ram + ram_gb)
            self.thread = threading.Thread(target=self.mine)
            self.thread.start()

    def stop(self):
        if self.running:
            self.running = False
            self.thread.join()
            print()
            used_ram = read_used_ram()
            write_used_ram(max(0, used_ram - self.ram_gb))

def exit_and_reset(miner=None):
    if miner is not None:
        miner.stop()
    write_used_ram(0)
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    print("\nRAM usage file reset. Miner lock removed. Program closed.")
    exit()

def safe_input(prompt, miner=None):
    value = input(prompt)
    if value.strip() == "":
        exit_and_reset(miner)
    return value

def cleanup():
    write_used_ram(0)
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
    print("\nRAM usage file reset. Miner lock removed. Program closed.")

def signal_handler(sig, frame):
    cleanup()
    exit(0)

# Register cleanup for normal exit and signals
atexit.register(cleanup)
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

class SingleOpenFile:
    _is_open = False  # Class-level variable

    def __init__(self, filename, mode='r'):
        self.filename = filename
        self.mode = mode
        self.file = None

    def open(self):
        if SingleOpenFile._is_open:
            raise Exception("Another file is already open!")
        self.file = open(self.filename, self.mode)
        SingleOpenFile._is_open = True
        return self.file

    def close(self):
        if self.file:
            self.file.close()
            self.file = None
            SingleOpenFile._is_open = False

# Usage example:
# f1 = SingleOpenFile('test1.txt', 'r')
# file_obj1 = f1.open()
# f2 = SingleOpenFile('test2.txt', 'r')
# file_obj2 = f2.open()  # Raises Exception
# f1.close()
# file_obj2 = f2.open()  # Now allowed

def remove_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def check_single_instance():
    if os.path.exists(LOCK_FILE):
        print("Another instance is already running.")
        exit(1)
    with open(LOCK_FILE, 'w') as f:
        f.write('locked')
    atexit.register(remove_lock)

def acquire_lock():
    try:
        lock_handle = open(LOCK_FILE, 'w')
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
        return lock_handle
    except OSError:
        print("Another instance is already running.")
        exit(1)

def release_lock(lock_handle):
    try:
        msvcrt.locking(lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
        lock_handle.close()
        os.remove(LOCK_FILE)
    except Exception:
        pass

try:
    check_single_instance()
    print_gradient_banner("BARKOD-BTC")
    miner = FakeMiner()
    lock_handle = acquire_lock()
    input("Type 'start' to begin mining. Press Enter at any prompt to quit.\n>")
finally:
    if 'lock_handle' in locals():
        release_lock(lock_handle)
    win32api.CloseHandle(mutex)