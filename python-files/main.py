import socket

LISTEN_IP = '113.212.108.184'
LISTEN_PORT = 9999  # Same port as PC sends to
import psutil
import socket
import time
import threading
import os
import shutil
import sqlite3
from datetime import datetime

# Your phone IP and port to send logs to
PHONE_IP = '192.168.1.100'   # Change to your phone's IP address
PHONE_PORT = 9999

# Apps to monitor (process names)
MONITOR_APPS = ['chrome.exe', 'firefox.exe', 'notepad.exe']

# Apps to block (process names)
BLOCK_APPS = ['notepad.exe']

# Chrome history file path (adjust if needed)
CHROME_HISTORY_PATH = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History')

# Time interval between checks (seconds)
CHECK_INTERVAL = 5

class Monitor:
    def __init__(self):
        self.sock = None
        self.connected = False
        self.last_processes = set()
        self.chrome_history_last_visit = None

    def connect(self):
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((PHONE_IP, PHONE_PORT))
                self.connected = True
                print("[*] Connected to phone")
            except Exception as e:
                print(f"[!] Connection failed: {e}. Retrying in 10 seconds...")
                time.sleep(10)

    def send_log(self, message):
        if self.connected:
            try:
                now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                full_msg = f"[{now}] {message}"
                self.sock.sendall(full_msg.encode('utf-8'))
            except Exception as e:
                print(f"[!] Sending failed: {e}")
                self.connected = False
                self.connect()

    def get_running_processes(self):
        procs = set()
        for proc in psutil.process_iter(['name']):
            try:
                procs.add(proc.info['name'].lower())
            except:
                pass
        return procs

    def block_apps(self, processes):
        for proc in psutil.process_iter(['name', 'pid']):
            try:
                pname = proc.info['name'].lower()
                if pname in BLOCK_APPS:
                    proc.kill()
                    self.send_log(f"Blocked and killed {pname} (PID: {proc.pid})")
            except:
                pass

    def check_chrome_history(self):
        try:
            # Copy chrome history file to temp to avoid lock issues
            tmp_history = 'History_tmp'
            shutil.copy2(CHROME_HISTORY_PATH, tmp_history)

            conn = sqlite3.connect(tmp_history)
            cursor = conn.cursor()
            cursor.execute("SELECT url, last_visit_time FROM urls ORDER BY last_visit_time DESC LIMIT 5;")
            rows = cursor.fetchall()
            conn.close()
            os.remove(tmp_history)

            new_visits = []
            for url, last_visit_time in rows:
                # Convert last_visit_time (webkit timestamp) to normal datetime
                visit_time = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time/10)
                if not self.chrome_history_last_visit or visit_time > self.chrome_history_last_visit:
                    new_visits.append((url, visit_time))
                else:
                    break

            if new_visits:
                # Update latest visit time
                self.chrome_history_last_visit = new_visits[0][1]

            for url, visit_time in reversed(new_visits):
                self.send_log(f"Visited {url} in Chrome browser")

        except Exception as e:
            # Ignore errors (e.g. chrome open locks DB)
            pass

    def monitor_loop(self):
        while True:
            procs = self.get_running_processes()

            # Detect newly opened monitored apps
            new_apps = procs - self.last_processes
            for app in new_apps:
                if app in MONITOR_APPS:
                    self.send_log(f"User opened {app}")

            # Block apps if found
            self.block_apps(procs)

            # Check Chrome browsing history
            if 'chrome.exe' in procs:
                self.check_chrome_history()

            self.last_processes = procs
            time.sleep(CHECK_INTERVAL)

def main():
    monitor = Monitor()
    monitor.connect()
    monitor.monitor_loop()

if __name__ == '__main__':
    main()
