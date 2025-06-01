import threading
import queue
import random
import time
import string

# Shared queue between producer and consumers (shared memory model)
data_queue = queue.Queue()
stop_flag = threading.Event()

# Grid size for ASCII art
GRID_WIDTH = 80
GRID_HEIGHT = 20

# Lock to prevent console output from overlapping
print_lock = threading.Lock()

# PRODUCER THREAD #
def producer():
    while not stop_flag.is_set():
        num = random.randint(10, 50)  # Number of characters to generate
        data_queue.put(num)           # Push number into shared queue
        with print_lock:
            print(f"[Producer] Produced number: {num}")
        time.sleep(random.uniform(0.5, 2))  # Random sleep

# CONSUMER THREAD #
def consumer(consumer_id):
    while not stop_flag.is_set():
        try:
            num = data_queue.get(timeout=1)  # Wait for data
        except queue.Empty:
            continue

        # Create an empty grid
        grid = [[' ' for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

        # Fill grid with random characters at random positions
        for _ in range(num):
            x = random.randint(0, GRID_WIDTH - 1)
            y = random.randint(0, GRID_HEIGHT - 1)
            char = random.choice(string.ascii_letters + string.digits + string.punctuation)
            grid[y][x] = char

        # Print the "visual art"
        with print_lock:
            print(f"\n[Consumer {consumer_id}] Visual Art from number {num}:")
            for row in grid:
                print("".join(row))
            print("-" * GRID_WIDTH + "\n")

        time.sleep(0.5)

# STARTING THREADS #
producer_thread = threading.Thread(target=producer)
consumer_threads = [threading.Thread(target=consumer, args=(i,)) for i in range(2)]

producer_thread.start()
for t in consumer_threads:
    t.start()

# RUNNING FOR LIMITED TIME #
try:
    time.sleep(20)  # Run the simulation for 20 seconds
except KeyboardInterrupt:
    pass
finally:
    stop_flag.set()
    producer_thread.join()
    for t in consumer_threads:
        t.join()
    print("All threads finished.")
