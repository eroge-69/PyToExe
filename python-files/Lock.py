import psutil
import time
import os

target_app = "chrome.exe"
limit_seconds = 1  # 30 minutes

start_time = time.time()
while True:
    # Check if app is running
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == target_app:
            current_time = time.time()
            if current_time - start_time > limit_seconds:
                os.system(f"taskkill /F /PID {proc.info['pid']}")
                print(f"{target_app} has been closed.")
                break
    time.sleep(5)
