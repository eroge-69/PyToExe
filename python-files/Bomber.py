import time

memory_hog = bytearray(512 * 1024 * 1024 * 1024)  # Allocate 512GB
while True:
    time.sleep(10)  # Keep memory allocated
