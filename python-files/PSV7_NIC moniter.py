import os
import time
from datetime import datetime
import csv
import configparser

CONFIG_FILE = "config.ini"
LOG_FILE = "network_monitor.csv"
MAX_LOG_SIZE = 1 * 1024 * 1024  # 1MB
INTERVAL_SEC = 10

def load_targets(config_path):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config.items("Targets")  # [(ip, name), ...]

def rotate_log_file():
    if os.path.isfile(LOG_FILE) and os.path.getsize(LOG_FILE) >= MAX_LOG_SIZE:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"network_monitor_{timestamp}.csv"
        os.rename(LOG_FILE, new_name)
        print(f">>> Log rotated: {new_name}")

def write_header():
    with open(LOG_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Device", "IP Address", "Status"])

def log_event(ip, name, is_alive):
    rotate_log_file()
    if not os.path.isfile(LOG_FILE):
        write_header()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "Ping successful" if is_alive else "Ping failed"
        writer.writerow([timestamp, name, ip, status])

# 시작
targets = load_targets(CONFIG_FILE)
if not os.path.isfile(LOG_FILE):
    write_header()

while True:
    for ip, name in targets:
        response = os.system(f"ping -n 1 {ip} >nul")
        is_alive = (response == 0)
        log_event(ip, name, is_alive)
    time.sleep(INTERVAL_SEC)