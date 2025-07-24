import os
import time
import subprocess

FLAG_PATH = r"C:\hum-s01\hum_core\pm2\reload.flag"

time.sleep(10)
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Reloader woke up...")

while True:
    if os.path.exists(FLAG_PATH):
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Flag detected. Reloading PM2...")
        subprocess.run(["pm2", "reload", "all"], shell=True)
        os.remove(FLAG_PATH)
    time.sleep(10)