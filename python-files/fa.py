import os, time
from colorama import init, Fore, Style

init(autoreset=True)

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def fade_text(text, colors):
    lines = text.strip('\n').splitlines()
    for i, line in enumerate(lines):
        color = colors[min(i, len(colors)-1)]
        print(color + line)
        time.sleep(0.04)

ascii_hellify = """
██╗  ██╗███████╗██╗     ██╗     ██╗███████╗██╗   ██╗██╗   ██╗
██║  ██║██╔════╝██║     ██║     ██║██╔════╝╚██╗ ██╔╝╚██╗ ██╔╝
███████║█████╗  ██║     ██║     ██║█████╗   ╚████╔╝  ╚████╔╝ 
██╔══██║██╔══╝  ██║     ██║     ██║██╔══╝    ╚██╔╝    ╚██╔╝  
██║  ██║███████╗███████╗███████╗██║███████╗   ██║      ██║   
╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
"""

fade_colors = [
    Fore.MAGENTA + Style.BRIGHT,
    Fore.MAGENTA,
    Fore.LIGHTMAGENTA_EX,
    Fore.LIGHTBLACK_EX,
    Fore.BLACK
]

clear()
fade_text(ascii_hellify, fade_colors)
print(Fore.MAGENTA + Style.BRIGHT + "                  HELLIFY BOOSTER\n")
time.sleep(0.3)

print(Fore.GREEN + "[1] 1 Month Boost")
print(Fore.GREEN + "[2] 2 Month Boost")
print(Fore.GREEN + "[3] 3 Month Boost\n")
time.sleep(0.2)

print(Style.BRIGHT + Fore.WHITE + "Choose an option " + Fore.LIGHTGREEN_EX + "→ ", end="")
choice = input()

print("\n" + Fore.LIGHTBLACK_EX + "Connecting to API...")
time.sleep(1)
print(Fore.LIGHTBLACK_EX + "Getting tokens...")
time.sleep(2)
time.sleep(2)
print(Fore.LIGHTBLACK_EX + "Checking tokens...")

time.sleep(5)
clear()
fade_text(ascii_hellify, fade_colors)
print(Fore.MAGENTA + Style.BRIGHT + "                  HELLIFY BOOSTER\n")
print(Fore.RED + Style.BRIGHT + "           TOKENS ARE EMPTY PLEASE TRY AGAIN LATER ❌\n")
time.sleep(0.1)
print(Fore.RED + Style.BRIGHT + "           TOKENS ARE EMPTY PLEASE TRY AGAIN LATER ❌\n")
time.sleep(0.1)
print(Fore.RED + Style.BRIGHT + "           TOKENS ARE EMPTY PLEASE TRY AGAIN LATER ❌\n")
time.sleep(0.1)
print(Fore.RED + Style.BRIGHT + "           TOKENS ARE EMPTY PLEASE TRY AGAIN LATER ❌\n")
time.sleep(0.1)
print(Fore.RED + Style.BRIGHT + "           TOKENS ARE EMPTY PLEASE TRY AGAIN LATER ❌\n")
time.sleep(0.1)

# Kapanışta beklet
input(Fore.LIGHTBLACK_EX + Style.BRIGHT + "\nPress ENTER to exit...")
