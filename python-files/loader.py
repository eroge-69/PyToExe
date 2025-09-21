# fake_ogfn_loader.py
# Harmless simulation only — does not load drivers or touch system files.
import time
import sys

OGFN_ASCII = r"""
  ____   _____ ______  _   _ 
 / __ \ / ____|  ____|| \ | |
| |  | | |  __| |__   |  \| |
| |  | | | |_ |  __|  | . ` |
| |__| | |__| | |____ | |\  |
 \____/ \_____|______||_| \_|
"""

def slow_print(s, delay=0.03):
    for ch in s:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def progress_bar(total=30, delay=0.04, prefix=""):
    for i in range(total+1):
        pct = int(i/total*100)
        bar = "#" * i + "-" * (total-i)
        sys.stdout.write(f"\r{prefix}[{bar}] {pct}%")
        sys.stdout.flush()
        time.sleep(delay)
    print()

def main():
    print(OGFN_ASCII)
    print("made by @y293 and @jj on discord")
    print()
    key = input("Key: ").strip()
    if key == "1716094921":
        print("\nSuccess Time Left (1 WEEK)\n")
    else:
        print("\nInvalid Key — demo mode\n")
    # Driver message (simulation only)
    ans = input("driver not found load driver? y/n: ").strip().lower()
    if ans == 'y' or ans == 'yes':
        print("\nSimulating driver load (harmless)...")
        progress_bar(prefix="Loading driver: ")
        print("Driver simulated loaded (fake).")
    else:
        print("Skipping driver load (safe).")
    print()
    projects = {
        "1": "EON",
        "2": "RETRAC",
        "3": "CRYSTAL",
        "4": "ERA"
    }
    print("choose your project")
    for k, v in projects.items():
        print(f"{k}. {v}")
    choice = input("Enter number (1-4): ").strip()
    project = projects.get(choice)
    if not project:
        print("Invalid selection. Exiting.")
        input("Enter any key to exit...")
        return
    confirm = input(f'load "{project}"? y/n (MUST HAVE GAME OPEN): ').strip().lower()
    if confirm == 'y' or confirm == 'yes':
        print(f'\nloading "{project}" Cheat...')
        slow_print("Performing pre-checks...", 0.02)
        progress_bar(prefix=f"Loading {project}: ")
        print("\nLoaded — stay safe stay real")
    else:
        print("Load cancelled by user.")
    print()
    input("Enter any key to exit...")

if __name__ == "__main__":
    main()
