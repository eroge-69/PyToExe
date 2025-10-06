
import os
import psutil
import shutil
import time
from pathlib import Path
import ctypes
import sys

APP_NAME = "TLauncherBooster"

def boost_process(process_name):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] and process_name.lower() in proc.info['name'].lower():
            try:
                proc.nice(psutil.HIGH_PRIORITY_CLASS)
            except Exception:
                pass

def clean_cache():
    mc_folder = Path.home() / ".minecraft"
    temp_dirs = ["logs", "cache", "versions"]
    for d in temp_dirs:
        path = mc_folder / d
        if path.exists() and path.is_dir():
            try:
                shutil.rmtree(path)
            except Exception:
                pass

def main():
    ctypes.windll.kernel32.SetConsoleTitleW(APP_NAME)
    while True:
        boost_process("TLauncher.exe")
        boost_process("javaw.exe")
        clean_cache()
        time.sleep(60)  # Run every minute

if __name__ == "__main__":
    main()
