import time
import random
import os

GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

total_btc = 0.0
block_count = 0

while True:
    block_count += 1
    hash_fake = ''.join(random.choice("0123456789abcdef") for _ in range(64))
    earned = round(random.uniform(0.00000001, 0.0005), 8)
    total_btc += earned

    print(f"{GREEN}[Block #{block_count}] Mining...{RESET}")
    print(f"Hash: {hash_fake}")
    print(f"{YELLOW}+{earned} BTC{RESET} (Total: {total_btc:.8f} BTC)\n")
    
    time.sleep(0.3)