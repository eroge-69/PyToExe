
import random
import time
import os
from colorama import init, Fore

init(autoreset=True)

commands = [
    "ping 192.168.0.1",
    "access -granted",
    "decrypt --keyfile main.key",
    "bypass firewall",
    "upload payload.exe",
    "scan ports --range 20-65535",
    "spoof mac --interface eth0",
    "initiate trace",
    "extract credentials",
    "listen --port 1337"
]

errors = [
    "ERROR: Access denied",
    "WARNING: Unexpected response",
    "CRITICAL: Memory leak detected",
    "ALERT: Traceback incoming"
]

def loading_bar(task, duration=2):
    print(Fore.CYAN + f"{task} [", end="", flush=True)
    steps = 20
    for i in range(steps):
        print(Fore.CYAN + "█", end="", flush=True)
        time.sleep(duration / steps)
    print(Fore.CYAN + "] Done")

def main():
    os.system("title Hacker Terminal Simulator")

    # Initial fake loading
    loading_bar("Initializing environment", 1.5)
    loading_bar("Loading exploits", 2)
    loading_bar("Establishing secure tunnel", 2.5)
    print()

    try:
        while True:
            if random.randint(1, 15) == 1:
                print(Fore.RED + random.choice(errors))
            else:
                print(Fore.GREEN + random.choice(commands))
            time.sleep(random.uniform(0.1, 0.4))
    except KeyboardInterrupt:
        print(Fore.RESET + "\nSession terminated.")

if __name__ == "__main__":
    main()
