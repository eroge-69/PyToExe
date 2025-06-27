
import psutil
import time

def kill_process(process_name):
    for proc in psutil.process_iter(['name']):
        if proc.info['name'] == process_name:
            try:
                proc.kill()
                print(f"Terminated {process_name}")
            except Exception as e:
                print(f"Could not terminate {process_name}: {e}")

if __name__ == "__main__":
    while True:
        kill_process("paintthetownred.exe")
        time.sleep(5)
