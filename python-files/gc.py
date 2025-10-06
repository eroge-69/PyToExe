import psutil
import ctypes
import time
from datetime import datetime

# Process name to monitor
TARGET_PROCESS_NAME = "RobloxPlayerBeta.exe"
CHECK_INTERVAL = 3  # Interval in seconds

# Windows function for clearing process working set
psapi = ctypes.WinDLL('psapi')
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

def log_with_timestamp(message):
    """Prints a message with current date and time"""
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    print(f"{timestamp} {message}")

def empty_working_set(pid):
    """Frees the process working set memory"""
    PROCESS_ALL_ACCESS = 0x1F0FFF  # Using full access rights
    handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not handle:
        log_with_timestamp(f"Failed to open process PID={pid}. Error code: {ctypes.get_last_error()}")
        return False
    try:
        result = psapi.EmptyWorkingSet(handle)
        if not result:
            log_with_timestamp(f"Failed to empty working set for PID={pid}. Error code: {ctypes.get_last_error()}")
        else:
            log_with_timestamp(f"Successfully emptied working set for PID={pid}.")
        return result
    finally:
        kernel32.CloseHandle(handle)

def find_processes_by_name(name):
    """Finds all processes with the specified name"""
    processes = []
    for proc in psutil.process_iter(attrs=["pid", "name"]):
        try:
            if proc.info['name'] == name:
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes

def main():
    log_with_timestamp(f"Starting process monitoring for: {TARGET_PROCESS_NAME}")
    while True:
        processes = find_processes_by_name(TARGET_PROCESS_NAME)
        if processes:
            for proc in processes:
                log_with_timestamp(f"Attempting to empty working set for PID={proc.info['pid']}")
                empty_working_set(proc.info['pid'])
        else:
            log_with_timestamp("No processes found.")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
