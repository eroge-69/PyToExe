import os
import subprocess
import time
import ctypes
import tempfile

def get_process_list():
    output = os.popen('wmic process get ProcessId,ParentProcessId,CommandLine /format:list').read()
    processes = []
    current = {}
    for line in output.strip().splitlines():
        if not line.strip():
            if current:
                processes.append(current)
                current = {}
        else:
            key, _, value = line.partition('=')
            current[key.strip()] = value.strip()
    if current:
        processes.append(current)
    return processes

def get_temp_files():
    temp_dir = tempfile.gettempdir()
    file_list = []
    for root, dirs, files in os.walk(temp_dir):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                file_list.append((full_path, os.path.getsize(full_path)))
            except:
                pass
    return set(file_list)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        print("[ERROR] This script must be run as administrator.")
        return

    target = input("Enter full path to the file to execute: ").strip('"')

    if not os.path.isfile(target):
        print("[ERROR] File does not exist.")
        return

    print(f"[INFO] Starting: {target}")

    before_procs = get_process_list()
    before_files = get_temp_files()

    try:
        proc = subprocess.Popen(target, shell=False)
    except Exception as e:
        print(f"[ERROR] Could not execute file: {e}")
        return

    print(f"[INFO] Running with PID {proc.pid}")
    print("[INFO] Monitoring for 60 seconds...")

    for i in range(60):
        time.sleep(1)

        # Check for new processes
        procs = get_process_list()
        new_procs = [p for p in procs if p not in before_procs and p.get('ParentProcessId') == str(proc.pid)]
        for p in new_procs:
            cmd = p.get('CommandLine', '<unknown>')
            pid = p.get('ProcessId', '?')
            print(f"[NEW PROCESS] PID={pid} CMD={cmd}")

        # Check for new files in temp
        current_files = get_temp_files()
        dropped = current_files - before_files
        for f, size in dropped:
            print(f"[FILE DROP] {f} ({size} bytes)")

        # Update for next loop
        before_procs = procs
        before_files = current_files

    print("[INFO] Done monitoring.")

if __name__ == '__main__':
    main()
