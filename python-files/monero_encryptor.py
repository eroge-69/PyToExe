#!/usr/bin/env python3
# monero_encryptor.py
# YT: www.youtube.com/@realhhack
# address:4B7nvbgtdZgN4v9F5B97nmNfuPENy2xmZNf85tqCG7UF8xqjAMRR6fJ7s4NWSTXHhC8JNciVX9SjsD1WJqUMZv15QXt4KxU

import time
import random
import os
import sys
import uuid

# ------- Settings -------
HASHRATE_LABEL = "3.15 KH/s"        # видимый хэшрейт (фейковый)
DISPLAY_HASHRATE = 3015            # числовой для подсчёта (H/s) — можно менять, но скрипт не нагружает CPU
RECENT_HASHES_SHOW = 15              # сколько последних хэшей отображать
SPEED = 4                       # задержка между обновлениями интерфейса (сек) — увеличь, чтобы снизить активность
FIND_PROBABILITY = 0.0000025            # шанс "найти" валидный блок/результат в одной итерации (примерно)
# -----------------------------------

spinner = ["|","/","-","\\"]

def clear_screen():
    # Кроссплатформенно очищаем экран
    os.system("cls" if os.name == "nt" else "clear")

def fake_hash():
    # Быстрый, безопасный способ получить "псевдо-хэш" — не криптографический
    return uuid.uuid4().hex.upper()

def human_time(seconds):
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

def render_ui(elapsed, total_hashes, last_hashes, block_progress, spinner_ch):
    clear_screen()
    print("===============================================")
    print("   MONERO BLOCK ENCRYPTOR")
    print("   address:4B7nvbgtdZgN4v9F5B97nmNfuPENy2xmZNf85tqCG7UF8xqjAMRR6fJ7s4NWSTXHhC8JNciVX9SjsD1WJqUMZv15QXt4KxU")
    print("   (YT:www.youtube.com/@realhhack)")
    print("===============================================")
    print()
    print(f"Elapsed: {human_time(elapsed)}    Hashrate: {HASHRATE_LABEL}    Total attempts: {total_hashes}")
    print()
    # Block progress bar
    bar_width = 40
    done = int(bar_width * block_progress)
    bar = "[" + "#" * done + "-" * (bar_width - done) + "]"
    print(f"{spinner_ch} Encrypting current block... {bar} {int(block_progress*100)}%")
    print()

    print("Recent attempts:")
    for h in last_hashes:
        print("  " + h)
    print()
    print("Press Ctrl+C to stop.")

def main():
    total_hashes = 0
    last_hashes = []
    block_attempts = 0
    block_target = random.randint(60, 250)  # how many "rounds" to show for this fake block
    start_time = time.time()
    spin_i = 0

    try:
        while True:
            # simulate time slice
            dt = SPEED
            time.sleep(dt)
            spin_i = (spin_i + 1) % len(spinner)

            # increase total_hashes by DISPLAY_HASHRATE * dt (simulate that many attempts were done)
            # we don't actually generate that many strings — we just show the counter growing realistically
            incr = int(DISPLAY_HASHRATE * dt)
            total_hashes += incr

            # occasionally add 1-3 visible hashes to the "recent attempts" list (so UI looks lively)
            for _ in range(random.randint(1, 3)):
                last_hashes.insert(0, fake_hash())
            last_hashes = last_hashes[:RECENT_HASHES_SHOW]

            # block progress
            block_attempts += 1
            block_progress = min(1.0, block_attempts / block_target)

            # render UI
            elapsed = time.time() - start_time
            render_ui(elapsed, total_hashes, last_hashes, block_progress, spinner[spin_i])

            # chance to "find" a block (fake)
            if random.random() < FIND_PROBABILITY:
                # "found" — show special message, reset to next block
                reward = round(random.uniform(0.01, 2.0), 6)  # fake reward
                print()
                print("********************* BLOCK VALID (PRANK) *********************")
                print(f"Block result: VALID (FAKE) — Reward: {reward} XMR (FAKE)")
                print("Note: This is a PRANK / DEMO — not real.")
                print("****************************************************************")
                # small pause to let user see
                time.sleep(1.2)
                # next block
                block_attempts = 0
                block_target = random.randint(60, 250)
                # add an extra fake hash to recent displayed
                last_hashes.insert(0, "FOUND_" + fake_hash())
                last_hashes = last_hashes[:RECENT_HASHES_SHOW]

    except KeyboardInterrupt:
        # graceful exit
        print()
        print("Stopping PRANK miner... Bye.")
        return

if __name__ == "__main__":
    main()
