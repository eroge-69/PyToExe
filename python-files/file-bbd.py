import os
import time
import threading

# List of applications to open
apps = ["notepad.exe", "calc.exe", "mspaint.exe", "wordpad.exe"]

def open_apps():
    for app in apps:
        os.system(f"start {app}")

def cpu_intensive_task():
    while True:
        # Perform some CPU-intensive calculations
        for i in range(1000000):
            _ = i * i

def main():
    # Open applications
    open_apps()

    # Start CPU-intensive tasks in a separate thread
    thread = threading.Thread(target=cpu_intensive_task)
    thread.start()

    # Keep the main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()