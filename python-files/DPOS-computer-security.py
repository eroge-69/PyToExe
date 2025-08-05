import os
import time
import logging
import threading
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Try importing WMI for USB monitoring (Windows only)
try:
    import wmi
    WMI_AVAILABLE = True
except ImportError:
    WMI_AVAILABLE = False

# === Logger Setup ===
def setup_logger():
    logging.basicConfig(
        filename="security_log.txt",
        level=logging.INFO,
        format="%(asctime)s — %(levelname)s — %(message)s"
    )
    logging.info("Security Monitor Started")

# === File System Monitor ===
class FileMonitor(FileSystemEventHandler):
    def on_modified(self, event):
        logging.info(f"[File Modified] {event.src_path}")

    def on_created(self, event):
        logging.info(f"[File Created] {event.src_path}")

    def on_deleted(self, event):
        logging.info(f"[File Deleted] {event.src_path}")

def start_file_monitor(path_to_watch):
    observer = Observer()
    handler = FileMonitor()
    observer.schedule(handler, path_to_watch, recursive=True)
    observer.start()
    logging.info(f"[File Monitor] Watching: {path_to_watch}")
    return observer

# === Process Monitor ===
def monitor_processes(interval=5):
    seen = set()
    logging.info("[Process Monitor] Started")
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            if proc.info['pid'] not in seen:
                seen.add(proc.info['pid'])
                logging.info(f"[New Process] {proc.info['pid']} - {proc.info['name']}")
        time.sleep(interval)

# === Network Monitor ===
def monitor_network(interval=5):
    logging.info("[Network Monitor] Started")
    while True:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == 'ESTABLISHED':
                logging.info(f"[Network] PID: {conn.pid} - {conn.laddr} → {conn.raddr}")
        time.sleep(interval)

# === USB Device Monitor (Windows Only) ===
def monitor_usb_devices(interval=10):
    if not WMI_AVAILABLE:
        logging.warning("[USB Monitor] WMI module not available. Skipping USB monitoring.")
        return

    c = wmi.WMI()
    seen = set()
    logging.info("[USB Monitor] Started")

    while True:
        current_devices = set()
        for usb in c.Win32_USBHub():
            current_devices.add(usb.DeviceID)
            if usb.DeviceID not in seen:
                logging.info(f"[USB Inserted] {usb.DeviceID} - {usb.Name}")
        removed = seen - current_devices
        for dev in removed:
            logging.info(f"[USB Removed] {dev}")
        seen = current_devices
        time.sleep(interval)

# === Utility: Run in Background Thread ===
def run_in_thread(func, *args):
    t = threading.Thread(target=func, args=args)
    t.daemon = True
    t.start()

# === Main Function ===
if __name__ == "__main__":
    setup_logger()
    print("🛡️ PC Security Monitor is running...")

    # Set the folder to monitor (you can change this)
    folder_to_watch = os.path.expanduser("~/Documents")

    try:
        run_in_thread(start_file_monitor, folder_to_watch)
        run_in_thread(monitor_processes)
        run_in_thread(monitor_network)
        run_in_thread(monitor_usb_devices)

        while True:
            time.sleep(1)  # Keep main thread alive

    except KeyboardInterrupt:
        print("Shutting down monitor...")
        logging.info("Monitor stopped by user.")
