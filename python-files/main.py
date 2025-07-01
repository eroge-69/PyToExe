import webbrowser
import sys
import os
import random
import time
from colorama import init, Fore, Style

init(autoreset=True)

CORRECT_PASSWORD = "Frostysky54"

COLORS = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE
]

BANNER = r"""
  ▄████████    ▄████████   ▄▄▄▄███▄▄▄▄   
  ███    ███   ███    ███ ▄██▀▀▀███▀▀▀██▄ 
  ███    █▀    ███    ███ ███   ███   ███ 
  ███          ███    ███ ███   ███   ███ 
▀███████████ ▀███████████ ███   ███   ███ 
         ███   ███    ███ ███   ███   ███ 
   ▄█    ███   ███    ███ ███   ███   ███ 
 ▄████████▀    ███    █▀   ▀█   ███   █▀  
"""

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_colored(text, color):
    print(f"{color}{text}{Style.RESET_ALL}")

def input_colored(prompt, color):
    print(f"{color}{prompt}{Style.RESET_ALL}", end='')
    user_input = input()
    print(Style.RESET_ALL, end='')
    return user_input

def open_links_in_same_window(file_path, color):
    try:
        with open(file_path, 'r') as file:
            urls = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print_colored("Error: urls.txt file not found.", color)
        return

    browser = webbrowser.get()
    if urls:
        browser.open(urls[0], new=1)
        for url in urls[1:]:
            browser.open(url, new=2)
        print_colored("All URLs have been opened.", color)
    else:
        print_colored("No URLs found in file.", color)

def main():
    color = random.choice(COLORS)
    while True:
        clear_terminal()
        print_colored(BANNER, color)
        print_colored(":)", color)
        entered_password = input_colored("Password: ", color)
        if entered_password != CORRECT_PASSWORD:
            print_colored("Wrong Password", color)
            exit()
        open_links_in_same_window("urls.txt", color)
        input_colored("", color)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting program. Goodbye!")
        sys.exit(0)
