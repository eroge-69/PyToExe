import os
import sys
import time
import subprocess

def log(msg, log_path):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {msg}\n")

def wait_for_process_exit(process_name, log_path):
    while True:
        try:
            out = subprocess.check_output(['tasklist'], text=True)
            if process_name.lower() not in out.lower():
                log(f"[DONE] {process_name} завершився", log_path)
                break
            time.sleep(1)
        except Exception as e:
            log(f"[ERROR] Не вдалося перевірити процес: {e}", log_path)
            break

def delete_file(path, log_path, retries=5, delay=1):
    for _ in range(retries):
        if not os.path.exists(path):
            return
        try:
            os.remove(path)
            log(f"[OK] Видалено: {path}", log_path)
            return
        except Exception as e:
            time.sleep(delay)
    if os.path.exists(path):
        log(f"[FAIL] Не вдалося видалити: {path}", log_path)

def main():
    files = sys.argv[1:]
    if not files:
        return

    log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cleanup.log")
    process_name = "WorldOfTanks.exe"

    log(f"[WAIT] Очікування завершення {process_name}", log_path)
    wait_for_process_exit(process_name, log_path)

    for file_path in files:
        delete_file(file_path, log_path)

if __name__ == "__main__":
    main()