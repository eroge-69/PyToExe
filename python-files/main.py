import time

while True:
    start = time.perf_counter()
    time.sleep(0.001)
    end = time.perf_counter()
    delta = (end - start) * 1000
    print(f"Sleep(1ms) took: {delta:.3f} ms")
