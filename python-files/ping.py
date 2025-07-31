import subprocess
from datetime import datetime
import platform
import time

# === Configuration ===
TARGET = "192.168.23.1"  # Replace with your IP or hostname
LOG_FILE = "ping_log.txt"
PING_COUNT = 4           # Number of pings to send in one run

# === Helper Function ===
def log_ping_result(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

# === Determine OS and Command ===
is_windows = platform.system().lower() == "windows"
ping_option = "-n" if is_windows else "-c"

# === Build and Run Ping Command ===
print(f"Pinging {TARGET} {PING_COUNT} times...")
cmd = ["ping", ping_option, str(PING_COUNT), TARGET]

try:
    result = subprocess.run(cmd, capture_output=True, text=True, shell=is_windows, timeout=10)
    if result.returncode == 0:
        print("Ping successful.")
        log_ping_result("Ping successful.\n" + result.stdout.strip())
    else:
        print("Ping failed.")
        log_ping_result("Ping failed.\n" + result.stdout.strip())

except subprocess.TimeoutExpired:
    error_msg = "Ping command timed out."
    print(error_msg)
    log_ping_result(error_msg)

except Exception as e:
    error_msg = f"Error: {str(e)}"
    print(error_msg)
    log_ping_result(error_msg)
