import multiprocessing
import time

def stress_test():
    while True:
        _ = sum(i*i for i in range(100000))

if __name__ == "__main__":
    processes = []
    for _ in range(multiprocessing.cpu_count()):
        p = multiprocessing.Process(target=stress_test)
        p.start()
        processes.append(p)

    time.sleep(300)  # Run for 5 minutes
    for p in processes:
        p.terminate()
