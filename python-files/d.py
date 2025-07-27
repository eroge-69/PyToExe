import subprocess
import threading
import time
import sys

def open_prompts(max_prompts=10000000, delay=0.1):
    global stop_flag
    count = 0
    while not stop_flag and count < max_prompts:
        subprocess.Popen("cmd.exe")
        time.sleep(delay)
        count += 1
    print(f"Stopped after {count} prompts.")

def stop_after_seconds(seconds):
    global stop_flag
    time.sleep(seconds)
    stop_flag = True
    print("Triggering stop...")

# Run the opener and stopper in separate threads
if __name__ == "__main__":
    threading.Thread(target=stop_after_seconds, args=(5,)).start()
    open_prompts(max_prompts=10000000, delay=0.