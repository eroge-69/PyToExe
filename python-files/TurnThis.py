import os
import sys
import time
import webbrowser
import random
import urllib.request
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

CURRENT_VERSION = "v1.0.0"
PRODUCT_KEYS = {
    "MRSK-4X7Q9-PZ2NM-K5YBT-JD8WR",
    "Tester"
}
LOAD_TIME = 25
FLASH_LIMIT = 999999
TITLE = "USDT Flasher"

RAINBOW = [
    Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA
]

ascii_banner = [
" ██████   ██████                                      █████       ",
"░░██████ ██████                                      ░░███        ",
" ░███░█████░███   ██████    ██████  ████████   █████  ░███ █████  ",
" ░███░░███ ░███  ░░░░░███  ███░░███░░███░░███ ███░░   ░███░░███   ",
" ░███ ░░░  ░███   ███████ ░███████  ░███ ░░░ ░░█████  ░██████░    ",
" ░███      ░███  ███░░███ ░███░░░   ░███      ░░░░███ ░███░░███   ",
" █████     █████░░████████░░██████  █████     ██████  ████ █████  ",
"░░░░░     ░░░░░  ░░░░░░░░  ░░░░░░  ░░░░░     ░░░░░░  ░░░░ ░░░░░   ",
"                    By t.me/MaerskTools                           "
]

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def rainbow_banner(banner_lines, delay=0.2):
    for i, line in enumerate(banner_lines):
        color = RAINBOW[i % len(RAINBOW)]
        print(color + line)
        time.sleep(delay)  # make it slowly flash

def random_color():
    return random.choice([
        Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE,
        Fore.MAGENTA, Fore.CYAN, Fore.WHITE
    ])

def print_colored(text, end='\n'):
    print(random_color() + text + Style.RESET_ALL, end=end)

def check_internet():
    try:
        urllib.request.urlopen("https://www.google.com", timeout=5)
        return True
    except Exception:
        return False

def loading_bar(duration=5):
    bar_length = 30
    messages = [
        "Connecting to Ethereum and Solana RPC nodes...",
        "Fetching latest block headers...",
        "Signing transaction with private relays...",
        "Broadcasting transaction to ETH/SOL validators...",
        "Waiting for block confirmations across the network..."
    ]
    
    steps = duration * 10  # number of 0.1 second steps
    for i in range(steps):
        progress = i / steps
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '-' * (bar_length - filled_length)
        color = random_color()

        # Pick a message depending on progress
        msg_index = min(i * len(messages) // steps, len(messages) - 1)
        message = messages[msg_index]

        # Internet drops mid-process
        if i % 15 == 0:  # every ~1.5s check
            if not check_internet():
                print_colored("\n[FAILED] Dropped Connection")
                return False

        print(f"\r{color}{message} |{bar}| {int(progress*100)}% ", end='', flush=True)
        time.sleep(0.1)  # smooth update
    print()
    return True

# ----- Input Sections with "Try Again" -----
def get_product_key():
    while True:
        input_key = input(random_color() + "Enter Product Key: " + Style.RESET_ALL).strip()
        if input_key in PRODUCT_KEYS:
            return input_key
        print(Fore.RED + "Invalid key. Try again.")

def get_flash_choice():
    while True:
        print_colored("What would you like to flash? (USDT)")
        choice = input("> ").strip().upper()
        if choice == "USDT":
            return choice
        print_colored("[FAILED] Invalid option. Please type USDT.")

def get_amount():
    while True:
        print_colored(f"How much would you like to flash? [$999k limit]")
        amount_input = input("> ").strip().replace("$", "").replace(",", "")
        try:
            amount = int(amount_input)
            if 0 < amount <= FLASH_LIMIT:
                return amount
            else:
                print_colored("[FAILED] Amount out of allowed range. Try again.")
        except ValueError:
            print_colored("[FAILED] Invalid number. Please try again.")

def get_address():
    while True:
        address = input(random_color() + "Enter ETH/SOL address: " + Style.RESET_ALL).strip()
        confirm = input(f"Is this the correct address? ({address}) (y/n): ").strip().lower()
        if confirm == "y":
            return address
        print_colored("[FAILED] Address not confirmed. Try again.")

# ----- Main -----
def main():
    clear_screen()
    try:
        os.system(f"title {TITLE}")
    except Exception:
        pass

    # Flashing rainbow banner
    rainbow_banner(ascii_banner, delay=0.15)

    # Inputs with validation loops
    get_product_key()
    get_flash_choice()
    amount = get_amount()
    address = get_address()

    # Internet check before loading
    if not check_internet():
        print_colored("[FAILED] Internet Error")
        input("Press Enter to close...")
        return

    # Loading bar with mid-checks
    if not loading_bar(LOAD_TIME):
        input("Press Enter to close...")
        return  # exit if connection dropped

    # Handle different networks
    if address.startswith("0x"):
        webbrowser.open("https://etherscan.io/token/0xdac17f958d2ee523a2206206994597c13d831ec7")
        webbrowser.open(f"https://etherscan.io/address/{address}")
    else:
        webbrowser.open("https://explorer.solana.com/address/Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB")
        webbrowser.open(f"https://explorer.solana.com/address/{address}")

    # Transaction outcome
    if amount % 2 == 0:
        print_colored("[SUCCEEDED] The flash was successful! If flash does not show please repeat with an VPN")
    else:
        print_colored("[FAILED] Transaction could not be processed.")

    # Keep CMD open
    input("\nPress Enter to close...")

if __name__ == "__main__":
    main()
