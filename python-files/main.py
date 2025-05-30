# main.py

import sys
from target_server import run_server
from attacker import start_attack

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py [server|attack]")
        sys.exit(1)

    if sys.argv[1] == 'server':
        run_server()
    elif sys.argv[1] == 'attack':
        start_attack()
    else:
        print("Invalid argument. Use 'server' or 'attack'.")
