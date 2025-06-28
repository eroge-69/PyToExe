import os
import subprocess
import sys
import time
from threading import Thread

# Install colorama if needed
try:
    import colorama
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    import colorama

from colorama import init, Fore, Style

init()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def generate_codes(service_name, total, code_length, color=None):
    """Generate codes for a service and write to a file."""
    import random  # Ensure random is imported here
    gentype = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    filename = f"{service_name}_Codes.txt"

    start_time = time.time()
    with open(filename, 'w') as out:
        for _ in range(total):
            code = ''.join(random.choice(gentype) for _ in range(code_length))
            out.write(code + "\n")
            # Removed speed control to generate as fast as possible

    print(f"{color if color else ''}Generated {total} codes for {service_name} in {time.time() - start_time:.2f} seconds.{Style.RESET_ALL if color else ''}")

while True:
    clear_screen()
    print("Made by Ahvoidful")
    print("Welcome In Starhub Generator")
    # Show menu options
    print(Fore.WHITE + "[1] -" + Style.RESET_ALL + Fore.MAGENTA + " PSN" + Style.RESET_ALL)
    print(Fore.WHITE + "[2] -" + Style.RESET_ALL + Fore.GREEN + " Playstore" + Style.RESET_ALL)
    print(Fore.WHITE + "[3] -" + Style.RESET_ALL + Fore.WHITE + " Roblox" + Style.RESET_ALL)
    print(Fore.WHITE + "[4] -" + Style.RESET_ALL + Fore.YELLOW + " Amazon" + Style.RESET_ALL)
    print(Fore.WHITE + "[5] -" + Style.RESET_ALL + Fore.RED + " Netflix" + Style.RESET_ALL)
    print(Fore.WHITE + "[6] -" + Style.BRIGHT + Fore.GREEN + " Xbox" + Style.RESET_ALL)
    print(Fore.WHITE + "[7] -" + Style.RESET_ALL + Fore.BLUE + " Itunes" + Style.RESET_ALL)
    print(Fore.WHITE + "[8] -" + Style.RESET_ALL + Fore.MAGENTA + " Nitro" + Style.RESET_ALL)
    print(Fore.WHITE + "[9] -" + Style.BRIGHT + Fore.BLACK + " Tiktok" + Style.RESET_ALL)
    print(Fore.WHITE + "[10] -" + Style.BRIGHT + Fore.CYAN + " Fortnite" + Style.RESET_ALL)
    print(Fore.WHITE + "[11] -" + Style.BRIGHT + Fore.RED + "Exit" + Style.RESET_ALL)

    choice = input("Please enter a number: ")

    if choice == '11':
        print("Exiting...")
        time.sleep(2)
        break

    services = {
        '1': ('PSN', 12),
        '2': ('PlayStore', 16),
        '3': ('Roblox', 18),
        '4': ('Amazon', 15),
        '5': ('Netflix', 15),
        '6': ('Xbox', 15),
        '7': ('iTunes', 16),
        '8': ('Nitro', 16),
        '9': ('Tiktok', 16),
        '10': ('Fortnite', 16)  # Added Fortnite
    }

    if choice not in services:
        print("Invalid choice.")
        time.sleep(2)
        continue

    service_name, code_length = services[choice]
    total_str = input(f"How many codes for {service_name}? ")
    try:
        total = int(total_str)
    except ValueError:
        print("Invalid number.")
        time.sleep(2)
        continue

    print(f"Generating {total} codes for {service_name}... (as fast as your system allows)")

    # Set color for Fortnite (light blue)
    color = None
    if service_name == 'Fortnite':
        color = Fore.CYAN

    # Run generation in a thread
    thread = Thread(target=generate_codes, args=(service_name, total, code_length, color))
    thread.start()
    thread.join()

    # After generation, ask to return or exit
    while True:
        print("\nWhat would you like to do next?")
        print("1. Return to main menu")
        print("2. Exit")
        next_action = input("Enter 1 or 2: ")
        if next_action == '1':
            break
        elif next_action == '2':
            print("Exiting...")
            time.sleep(2)
            exit()
        else:
            print("Invalid input. Please enter 1 or 2.")