import time
import random
import os
import signal
import sys
import psutil  # pip install psutil

def find_roblox_pid():
    # Search for a process called "RobloxPlayerBeta.exe"
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == "RobloxPlayerBeta.exe":
            return proc.info['pid']
    return None

def main():
    print("Target: RobloxPlayerBeta.exe")
    time.sleep(1)  # <-- 1 second wait before searching
    print("Searching for Roblox Instance...")
    time.sleep(1)

    pid = find_roblox_pid()
    if pid:
        print("Found Roblox Instance")
        print(f"PID: {pid}")
        print("Injecting...")
        time.sleep(1)
        print("Injected!")
        print("\nPress Ctrl+C or close this window to exit.")
        try:
            while True:
                time.sleep(1)  # keep window open
        except KeyboardInterrupt:
            print("\nExiting...")
    else:
        print("Roblox not found, exiting")
        time.sleep(2)
        sys.exit()

def cleanup():
    # Attempt to terminate Roblox if running
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == "RobloxPlayerBeta.exe":
            try:
                os.kill(proc.info['pid'], signal.SIGTERM)
                print(f"Closed Roblox PID {proc.info['pid']}")
            except Exception:
                pass

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()
